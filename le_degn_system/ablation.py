#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN Ablation Study Script (重构版 - 包内导入)
=======================================
消融研究核心原则:
  1. 所有配置从相同的贪心NN基线出发，init_transition 完全一致
  2. 所有配置共享同一个路网拓扑，service_cost 完全一致
  3. 四个配置: Full / ERFM+LHH / ERFM+SA-DGWN / ERFM-only
  4. 每个配置差异仅为被移除的组件，其他条件完全相同

组件贡献度定义:
  - ERFM贡献 = (ERFM+LHH - Full) 中 ERFM 部分（间接贡献）
  - SA-DGWN贡献 = 主动预测减少逃逸次数的效果
  - LHH贡献 = 被动逃逸处理的有效性
"""

import os
import sys
import json
import copy
import random

import numpy as np
import torch

from le_degn_system.pipeline.system import LEDEGNSystem
from le_degn_system.pipeline.baseline import BaselineDHAN
from le_degn_system.visualization.viz import Visualizer

from le_degn_system.environment.road_network import RoadNetworkEnv
from le_degn_system.environment.line_graph import LineGraphBuilder
from le_degn_system.models.erfm import ERFM, ERFMTrainer
from le_degn_system.models.sadgwn import SADGWN, TrafficDataGenerator
from le_degn_system.models.lhh import LHHEngine
from le_degn_system.core.metrics import PerformanceTracker, calculate_aocc

# ═══════════════════════════════════════════════════════════════
# 共享工具：贪心NN初始路径
# ═══════════════════════════════════════════════════════════════

def compute_greedy_nn_tour(lg, seed=None):
    """
    所有消融配置共用的贪心NN初始路径生成器。
    保证每个配置从完全相同的基线出发。

    返回: (tour_list, transition_cost)
    """
    if seed is not None:
        random.seed(seed)
    TC = lg.transition_cost
    N = lg.num_line_nodes()
    if N == 0:
        return [], 0.0

    available = list(range(N))
    max_nn = min(len(available), 120)
    if len(available) > max_nn:
        available = random.sample(available, max_nn)

    best_tour, best_trans = None, float('inf')
    starts = random.sample(available, min(5, len(available)))
    for start in starts:
        unvisited = set(available)
        cur = start
        unvisited.remove(cur)
        tour = [cur]
        while unvisited:
            nearest, min_c = None, float('inf')
            for nb in unvisited:
                c = TC[cur, nb].item()
                if c < min_c:
                    min_c, nearest = c, nb
            if nearest is None:
                break
            tour.append(nearest)
            unvisited.remove(nearest)
            cur = nearest
        trans = sum(TC[tour[i], tour[i + 1]].item() for i in range(len(tour) - 1))
        if len(tour) > 1:
            trans += TC[tour[-1], tour[0]].item()
        if trans < best_trans:
            best_trans, best_tour = trans, list(tour)

    return best_tour if best_tour else [], best_trans


# ═══════════════════════════════════════════════════════════════
# 消融配置实现
# ═══════════════════════════════════════════════════════════════

def run_erfm_only(env, lg, nn_tour, nn_trans):
    """
    ERFM-only: 仅有边中心编码器，无任何动态组件。
    从贪心NN出发 -> 2-opt局部优化 -> 无逃逸能力。
    """
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    system = LEDEGNSystem(env, erfm, None, None, lg)
    tracker = PerformanceTracker(30.0)

    # 从贪心NN出发
    tour = list(nn_tour)
    trans_cost = nn_trans
    total_cost = system.service_cost + trans_cost
    tracker.update(total_cost)

    # 仅做2-opt优化（无逃逸，无重规划）
    optimized = system._local_2opt(tour, max_iter=300)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans
    tracker.update(final_total)

    TC = lg.transition_cost
    N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower
    U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {
        'final_cost': final_total,
        'init_transition': nn_trans,
        'final_transition': post_trans,
        'aocc': aocc,
        'trajectory': tracker.trajectory,
        'escape_count': 0,
        'replan_count': 0,
        'service_cost': system.service_cost
    }


def run_erfm_with_sadgwn(env, lg, nn_tour, nn_trans):
    """
    ERFM + SA-DGWN（无LHH）: 有拥堵预测但无语言驱动的逃逸能力。
    拥堵时靠 ERFM 重规划（plan_global_route）规避。
    """
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=20, batch_size=8)

    # 无LHH -> 拥堵时仅做 ERFM 重规划
    system = LEDEGNSystem(env, erfm, stgcn, None, lg)
    tracker = PerformanceTracker(30.0)

    env.closed_edges.clear()
    events = system._default_events(lg.num_line_nodes())

    tour = list(nn_tour)
    cur_trans = nn_trans
    total_cost = system.service_cost + cur_trans
    tracker.update(total_cost)

    replan_count = 0
    for event in events:
        edges_to_block = event.get('edges', [])
        for e in edges_to_block:
            env.closed_edges.add(tuple(e))

        # SA-DGWN 预测拥堵风险
        c_dyn = system.predict_congestion()
        high_risk = (c_dyn > 0.5).sum().item()

        # 检查当前路径是否受堵
        affected = False
        for lid in tour:
            if lid not in lg.lid2edge:
                continue
            u, v, _, _ = lg.lid2edge[lid]
            if (u, v) in env.closed_edges:
                affected = True
                break

        if affected:
            replan_count += 1
            blocked_lids = set()
            for lid in range(lg.num_line_nodes()):
                u, v, _, _ = lg.lid2edge[lid]
                if (u, v) in env.closed_edges:
                    blocked_lids.add(lid)
            new_tour = system.plan_global_route(tracker, temperature=0.8,
                                                 blocked_lids=blocked_lids)
            if new_tour:
                tour = new_tour
                cur_trans = system._tour_transition_cost(tour)
                new_total = system.service_cost + cur_trans
                tracker.update(new_total)

        if random.random() < 0.3 and env.closed_edges:
            env.reopen_random_edges(1)

    # 2-opt优化
    optimized = system._local_2opt(tour, max_iter=200)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans
    tracker.update(final_total)

    TC = lg.transition_cost
    N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower
    U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {
        'final_cost': final_total,
        'init_transition': nn_trans,
        'final_transition': post_trans,
        'aocc': aocc,
        'trajectory': tracker.trajectory,
        'escape_count': 0,
        'replan_count': replan_count,
        'service_cost': system.service_cost
    }


def run_erfm_with_lhh(env, lg, nn_tour, nn_trans):
    """
    ERFM + LHH（无SA-DGWN）: 有语言驱动的逃逸但无主动拥堵预测。
    每次逃逸后触发 LHH 启发式选路 + ERFM 重规划。
    """
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    lhh = LHHEngine(env)
    system = LEDEGNSystem(env, erfm, None, lhh, lg)
    tracker = PerformanceTracker(30.0)

    env.closed_edges.clear()
    events = system._default_events(lg.num_line_nodes())

    tour = list(nn_tour)
    cur_trans = nn_trans
    total_cost = system.service_cost + cur_trans
    tracker.update(total_cost)

    for event in events:
        edges_to_block = event.get('edges', [])
        for e in edges_to_block:
            env.closed_edges.add(tuple(e))

        # 检查路径是否受堵
        affected, affected_node = False, None
        for lid in tour:
            if lid not in lg.lid2edge:
                continue
            u, v, _, _ = lg.lid2edge[lid]
            if (u, v) in env.closed_edges:
                affected, affected_node = True, u
                break

        if affected and affected_node is not None:
            # LHH 逃逸
            escape_path = lhh.escape(affected_node, env.closed_edges, verbose=False)
            blocked_lids = set()
            for lid in range(lg.num_line_nodes()):
                u, v, _, _ = lg.lid2edge[lid]
                if (u, v) in env.closed_edges:
                    blocked_lids.add(lid)
            new_tour = system.plan_global_route(tracker, temperature=0.8,
                                                 blocked_lids=blocked_lids)
            if new_tour:
                tour = new_tour
                cur_trans = system._tour_transition_cost(tour)
                new_total = system.service_cost + cur_trans
                tracker.update(new_total)

        if random.random() < 0.3 and env.closed_edges:
            env.reopen_random_edges(1)

    optimized = system._local_2opt(tour, max_iter=200)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans
    tracker.update(final_total)

    TC = lg.transition_cost
    N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower
    U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {
        'final_cost': final_total,
        'init_transition': nn_trans,
        'final_transition': post_trans,
        'aocc': aocc,
        'trajectory': tracker.trajectory,
        'escape_count': lhh.escape_count,
        'replan_count': lhh.escape_count,
        'service_cost': system.service_cost
    }


def run_full_system(env, lg, nn_tour, nn_trans):
    """
    完整 LE-DEGN: ERFM + SA-DGWN + LHH。
    唯一调用 execute_dynamic 的配置。
    """
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=20, batch_size=8)

    lhh = LHHEngine(env)
    system = LEDEGNSystem(env, erfm, stgcn, lhh, lg)

    result = system.execute_dynamic(time_budget=30.0, verbose=False,
                                      initial_tour=nn_tour)

    return result


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def main():
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    results = {}

    print("=" * 60)
    print("LE-DEGN Ablation Study (重构版)")
    print("=" * 60)
    print("原则: 所有配置从相同贪心NN基线出发, 共享同一路网")

    # Step 1: 生成共享路网
    base_env = RoadNetworkEnv(node_count=60)
    base_lg = LineGraphBuilder(base_env)
    base_lg.build()

    # Step 2: 计算共享的贪心NN初始路径（所有配置共用）
    nn_tour, nn_trans = compute_greedy_nn_tour(base_lg, seed=42)
    print(f"\n[基线] 贪心NN初始转移代价: {nn_trans:.1f}  "
          f"路径长度: {len(nn_tour)} 边")

    # Step 3: 四个消融配置
    configs = [
        ('Full LE-DEGN',       'full',            run_full_system),
        ('ERFM + LHH',          'erfm_lhh',        run_erfm_with_lhh),
        ('ERFM + SA-DGWN',      'erfm_sadgwn',     run_erfm_with_sadgwn),
        ('ERFM only (baseline)','erfm_only',       run_erfm_only),
    ]

    for name, cfg_id, runner in configs:
        print(f"\n[Testing] {name}")
        env = copy.deepcopy(base_env)
        lg = LineGraphBuilder(env)
        lg.build()

        result = runner(env, lg, nn_tour, nn_trans)

        results[cfg_id] = {
            'name': name,
            'final_cost': result.get('final_cost', 0),
            'init_transition': result.get('init_transition', 0),
            'final_transition': result.get('final_transition', 0),
            'aocc': result.get('aocc', 0),
            'escape_count': result.get('escape_count', 0),
            'replan_count': result.get('replan_count', 0),
            'service_cost': result.get('service_cost', 0)
        }

        print(f"  Init Transition: {result.get('init_transition', 0):.1f}")
        print(f"  Final Transition: {result.get('final_transition', 0):.1f}")
        print(f"  Final Cost: {result.get('final_cost', 0):.1f}")
        print(f"  AOCC: {result.get('aocc', 0):.4f}")
        print(f"  Escape Count: {result.get('escape_count', 0)}")

    # Step 4: 一致性格检查
    print("\n" + "=" * 60)
    print("一致性验证")
    print("=" * 60)
    sc_vals = [d['service_cost'] for d in results.values()]
    it_vals = [d['init_transition'] for d in results.values()]
    sc_ok = max(sc_vals) - min(sc_vals) < 0.01
    it_ok = max(it_vals) - min(it_vals) < 0.01
    print(f"  Service Cost 一致: {'PASS' if sc_ok else 'FAIL'} "
          f"(范围: {min(sc_vals):.1f} - {max(sc_vals):.1f})")
    print(f"  Init Transition 一致: {'PASS' if it_ok else 'FAIL'} "
          f"(范围: {min(it_vals):.1f} - {max(it_vals):.1f})")

    # Step 5: 组件贡献分析
    print("\n组件贡献分析 (基于 Total Cost):")
    full_cost = results['full']['final_cost']
    lhh_cost = results['erfm_lhh']['final_cost']
    sadgwn_cost = results['erfm_sadgwn']['final_cost']
    erfm_cost = results['erfm_only']['final_cost']
    total_gain = erfm_cost - full_cost
    if total_gain > 0:
        lhh_gain = sadgwn_cost - lhh_cost  # LHH在SA-DGWN基础上的增益
        sadgwn_gain = lhh_cost - full_cost  # SA-DGWN在LHH基础上的增益
        erfm_gain = erfm_cost - max(lhh_cost, sadgwn_cost)  # 基础贡献
        print(f"  ERFM基础贡献:      {erfm_gain:.1f} ({erfm_gain/total_gain*100:.1f}%)")
        print(f"  LHH贡献:           {lhh_gain:.1f} ({lhh_gain/total_gain*100:.1f}%)")
        print(f"  SA-DGWN贡献:       {sadgwn_gain:.1f} ({sadgwn_gain/total_gain*100:.1f}%)")
        print(f"  总改善:            {total_gain:.1f}")

    # Step 6: 保存结果
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'ablation_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("Ablation Study Results")
    print("=" * 60)
    header = (f"{'Configuration':<22} {'Final Cost':<12} {'AOCC':<10} "
              f"{'Escapes':<8} {'Replans':<8}")
    print(header)
    print("-" * 68)
    for cfg_id in ['full', 'erfm_lhh', 'erfm_sadgwn', 'erfm_only']:
        d = results[cfg_id]
        print(f"{d['name']:<22} {d['final_cost']:<12.1f} "
              f"{d['aocc']:<10.4f} {d['escape_count']:<8} {d['replan_count']:<8}")

    print(f"\nResults saved to: {out_path}")


if __name__ == '__main__':
    main()
