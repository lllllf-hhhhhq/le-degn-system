#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN 多城市多规模交叉验证
=============================
三城市 × 两半径 = 6 组独立实验。
验证 LHH 在不同城市路网拓扑上的稳健性。

不需要你手动操作，完全自动化运行。
"""

import os
import sys
import json
import copy
import random
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_data_loader import RealRoadNetworkLoader
from le_degn_system.environment import RealRoadNetworkEnv, LineGraphBuilder
from le_degn_system.models import ERFM, SADGWN, LHHEngine, TrafficDataGenerator
from le_degn_system.pipeline import LEDEGNSystem
from le_degn_system.core.metrics import PerformanceTracker, calculate_aocc


# ══════════════════════════════════
# 共享工具
# ══════════════════════════════════

def compute_greedy_nn_tour(lg, seed=42):
    random.seed(seed)
    TC = lg.transition_cost
    N = lg.num_line_nodes()
    if N == 0: return [], 0.0
    available = list(range(N))
    max_nn = min(len(available), 120)
    if len(available) > max_nn:
        available = random.sample(available, max_nn)
    best_tour, best_trans = None, float('inf')
    starts = random.sample(available, min(5, len(available)))
    for start in starts:
        unvisited = set(available); cur = start; unvisited.remove(cur)
        tour = [cur]
        while unvisited:
            nearest, mc = None, float('inf')
            for nb in unvisited:
                c = TC[cur, nb].item()
                if c < mc: mc, nearest = c, nb
            if nearest is None: break
            tour.append(nearest); unvisited.remove(nearest); cur = nearest
        trans = sum(TC[tour[i],tour[i+1]].item() for i in range(len(tour)-1))
        if len(tour)>1: trans += TC[tour[-1],tour[0]].item()
        if trans < best_trans: best_trans, best_tour = trans, list(tour)
    return best_tour if best_tour else [], best_trans


def run_single_experiment(city, radius, label):
    """在指定城市和范围内运行 Full LE-DEGN 和 ERFM+LHH 两组实验"""
    print(f"\n{'='*60}")
    print(f"{label}: {city} radius={radius}m")
    print(f"{'='*60}")

    loader = RealRoadNetworkLoader(city=city, radius=radius)
    env = RealRoadNetworkEnv(loader)
    lg = LineGraphBuilder(env)
    lg.build()
    n_nodes = env.node_count
    n_edges = env.G.number_of_edges()
    print(f"  路网: {n_nodes}节点 {n_edges}边")

    nn_tour, nn_trans = compute_greedy_nn_tour(lg, seed=42)
    print(f"  贪心NN基线: trans={nn_trans:.0f}")

    results = {}
    for name, use_lhh in [("Full LE-DEGN", True), ("ERFM+LHH (basic)", True)]:
        print(f"  [{name}]...")

        env_exp = copy.deepcopy(env)
        lg_exp = LineGraphBuilder(env_exp); lg_exp.build()

        erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                    d_model=64, n_heads=4, n_layers=3, ff_dim=128)
        from le_degn_system.models.erfm import ERFMTrainer
        trainer = ERFMTrainer(erfm, lg_exp, env_exp, lr=5e-4)
        trainer.train(episodes=100)

        # Full: SA-DGWN + LHH. ERFM+LHH: only LHH (no SA-DGWN prediction)
        if name.startswith("ERFM"):
            stgcn = None
        else:
            stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
            TrafficDataGenerator(env_exp, lg_exp).train_model(stgcn, epochs=20, batch_size=8)

        lhh = LHHEngine(env_exp)
        system = LEDEGNSystem(env_exp, erfm, stgcn, lhh, lg_exp)

        result = system.execute_dynamic(time_budget=30.0, initial_tour=nn_tour, verbose=False)

        key = "full" if name.startswith("Full") else "erfm_lhh"
        results[key] = {
            'city': city, 'radius': radius, 'nodes': n_nodes, 'edges': n_edges,
            'final_cost': result.get('final_cost', 0),
            'init_transition': result.get('init_transition', 0),
            'final_transition': result.get('final_transition', 0),
            'aocc': result.get('aocc', 0),
            'escape_count': result.get('escape_count', 0),
            'service_cost': result.get('service_cost', 0)
        }
        fc = result.get('final_cost', 0)
        esc = result.get('escape_count', 0)
        print(f"    Cost={fc:.0f}  AOCC={result.get('aocc',0):.4f}  Escape={esc}")

    # 计算改善
    fc = results.get('full', {}).get('final_cost', 0)
    ec = results.get('erfm_lhh', {}).get('final_cost', 0)
    improvement = ((ec - fc) / fc * 100) if fc > 0 else 0
    print(f"  → LHH改善: {improvement:+.1f}%")
    return results, improvement


def main():
    random.seed(42); np.random.seed(42); torch.manual_seed(42)

    # 三城市 × 两半径
    experiments = [
        ("Shanghai, China", 1200, "上海(小)"),
        ("Shanghai, China", 2000, "上海(中)"),
        ("Beijing, China", 1200, "北京(小)"),
        ("Beijing, China", 2000, "北京(中)"),
        ("Shenzhen, China", 1200, "深圳(小)"),
        ("Shenzhen, China", 2000, "深圳(中)"),
    ]

    all_results = {}
    summary = []

    print("=" * 60)
    print("LE-DEGN 多城市多规模交叉验证")
    print("=" * 60)

    for city, radius, label in experiments:
        try:
            res, imp = run_single_experiment(city, radius, label)
            all_results[f"{city.split(',')[0]}_{radius}"] = res
            summary.append({
                'label': label, 'city': city, 'radius': radius,
                'full_cost': res.get('full', {}).get('final_cost', 0),
                'lhh_cost': res.get('erfm_lhh', {}).get('final_cost', 0),
                'improvement_pct': imp,
                'nodes': res.get('full', {}).get('nodes', 0),
                'edges': res.get('full', {}).get('edges', 0),
                'aocc_full': res.get('full', {}).get('aocc', 0),
                'aocc_lhh': res.get('erfm_lhh', {}).get('aocc', 0),
            })
        except Exception as e:
            print(f"  ✗ {label} 失败: {e}")

    # 输出汇总
    print("\n" + "=" * 60)
    print("跨城市交叉验证汇总")
    print("=" * 60)
    print(f"{'实验':<12} {'节点':<6} {'Full Cost':<16} {'ERFM+LHH':<16} {'改善%':<8} {'AOCC_F':<8} {'AOCC_L':<8}")
    print("-" * 80)
    for s in summary:
        print(f"{s['label']:<12} {s['nodes']:<6} {s['full_cost']:<16.0f} "
              f"{s['lhh_cost']:<16.0f} {s['improvement_pct']:<+8.1f} "
              f"{s['aocc_full']:<8.4f} {s['aocc_lhh']:<8.4f}")

    # 保存
    out_path = os.path.join(os.path.dirname(__file__), 'cross_validation_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'results': all_results, 'summary': summary}, f, indent=2, ensure_ascii=False)

    # 均值统计
    imp_vals = [s['improvement_pct'] for s in summary]
    if imp_vals:
        mean_imp = np.mean(imp_vals)
        std_imp = np.std(imp_vals)
        print(f"\n平均改善: {mean_imp:.1f}% ± {std_imp:.1f}%  (n={len(imp_vals)})")
        print(f"LHH在{sum(1 for i in imp_vals if i < 0)}/{len(imp_vals)}组实验中优于Full")

    print(f"\n结果保存至: {out_path}")


if __name__ == '__main__':
    main()
