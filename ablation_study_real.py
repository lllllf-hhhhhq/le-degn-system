#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN 真实路网消融实验
========================
完全基于 OpenStreetMap 真实城市路网数据。
不使用任何合成/随机生成的路网。

运行方式:
  python ablation_study_real.py
  python -m ablation_study_real  (需在 le_degn_system 目录下)
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


# ═══════════════════════════════════════════════════════════════
# 复制 compute_greedy_nn_tour（与 ablation.py 一致）
# ═══════════════════════════════════════════════════════════════

def compute_greedy_nn_tour(lg, seed=None):
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
        cur = start; unvisited.remove(cur)
        tour = [cur]
        while unvisited:
            nearest, min_c = None, float('inf')
            for nb in unvisited:
                c = TC[cur, nb].item()
                if c < min_c: min_c, nearest = c, nb
            if nearest is None: break
            tour.append(nearest); unvisited.remove(nearest)
            cur = nearest
        trans = sum(TC[tour[i],tour[i+1]].item() for i in range(len(tour)-1))
        if len(tour)>1: trans += TC[tour[-1],tour[0]].item()
        if trans < best_trans: best_trans, best_tour = trans, list(tour)
    return best_tour if best_tour else [], best_trans


# ═══════════════════════════════════════════════════════════════
# 算法优化 1: ERFM 在贪心NN基础上做局部改进
# ═══════════════════════════════════════════════════════════════

def erfm_local_improve(erfm, system, tour, TC, k=3, n_iters=50):
    """
    在贪心NN路径上，用 ERFM REINFORCE 策略做局部改进：
    对路径中相邻 k 条边用 ERFM 采样替代，若转移成本降低则接受。
    返回改进后的 tour 和最终转移成本。
    """
    best_tour = list(tour)
    best_cost = system._tour_transition_cost(best_tour)
    with torch.no_grad():
        emb = erfm.encode(system.lg.node_features, system.lg.penalty_matrix)

    for _ in range(n_iters):
        if len(best_tour) < k + 2: break
        # 随机选择一个位置
        pos = random.randint(0, len(best_tour) - k - 1)
        prefix = best_tour[:pos]
        suffix = best_tour[pos + k:]

        # 用 ERFM 重新填充 k 条边
        start_node = best_tour[pos]
        available = set(suffix) if suffix else set(best_tour)
        # 去掉已在 prefix 中的
        available = [x for x in available if x not in prefix]
        if len(available) < k: continue

        # 贪心+ERFM混合填充
        cur = start_node
        filled = []
        unvisited = list(available[:k + 5])  # 少许冗余
        for _ in range(k):
            if not unvisited: break
            # ERFM 打分选下一条
            vis_t = torch.tensor(prefix + filled, dtype=torch.long)
            unv_t = torch.tensor(unvisited, dtype=torch.long)
            probs = erfm.decode_step(emb, cur, vis_t, unv_t, temperature=0.5)
            chosen = unvisited[int(torch.argmax(probs).item())]
            filled.append(chosen)
            unvisited.remove(chosen)
            cur = chosen

        if len(filled) < k: continue
        new_tour = prefix + filled + [x for x in suffix if x not in filled]
        new_cost = system._tour_transition_cost(new_tour)
        if new_cost < best_cost - 1e-6:
            best_tour = new_tour
            best_cost = new_cost

    return best_tour, best_cost


# ═══════════════════════════════════════════════════════════════
# 消融配置实现（与 ablation.py 一致，但使用 env._default_events_real）
# ═══════════════════════════════════════════════════════════════

ADAPTIVE_TEMP = True  # 是否启用自适应温度
ADAPTIVE_THRESHOLD = True  # 是否启用自适应SA-DGWN阈值

def run_erfm_only(env, lg, nn_tour, nn_trans):
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    from le_degn_system.models.erfm import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)

    if ADAPTIVE_TEMP:
        trainer._adaptive_train(episodes=100)  # 使用自适应温度
    else:
        trainer.train(episodes=100)

    system = LEDEGNSystem(env, erfm, None, None, lg)
    tracker = PerformanceTracker(30.0)
    tour = list(nn_tour)
    total_cost = system.service_cost + nn_trans
    tracker.update(total_cost)

    # ERFM 局部改进（算法优化1）
    if ADAPTIVE_TEMP:
        tour, _ = erfm_local_improve(erfm, system, tour, lg.transition_cost)

    optimized = system._local_2opt(tour, max_iter=300)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans
    tracker.update(final_total)

    TC = lg.transition_cost; N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        if row.dim() > 1: row.fill_diagonal_(float('inf'))
        else: row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower
    U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {'final_cost': final_total, 'init_transition': nn_trans,
            'final_transition': post_trans, 'aocc': aocc,
            'trajectory': tracker.trajectory, 'escape_count': 0,
            'replan_count': 0, 'service_cost': system.service_cost}


def run_erfm_with_sadgwn(env, lg, nn_tour, nn_trans):
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    from le_degn_system.models.erfm import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=20, batch_size=8)

    system = LEDEGNSystem(env, erfm, stgcn, None, lg)
    tracker = PerformanceTracker(30.0)
    env.closed_edges.clear()

    # 使用基于真实拥堵概率的事件
    real_events = env._default_events_real(3)
    tour = list(nn_tour)
    total_cost = system.service_cost + nn_trans
    tracker.update(total_cost)
    replan_count = 0

    for event in real_events:
        for e in event.get('edges', []): env.closed_edges.add(tuple(e))
        # SA-DGWN 自适应阈值
        threshold = 0.5
        if ADAPTIVE_THRESHOLD:
            c_dyn = system.predict_congestion()
            threshold = float(max(0.3, min(0.7, c_dyn.mean().item())))

        affected = False
        for lid in tour:
            if lid not in lg.lid2edge: continue
            u, v = lg.lid2edge[lid][0], lg.lid2edge[lid][1]
            if (u, v) in env.closed_edges: affected = True; break

        if affected:
            replan_count += 1
            blocked_lids = {lid for lid in range(lg.num_line_nodes())
                            if (lg.lid2edge[lid][0], lg.lid2edge[lid][1]) in env.closed_edges}
            new_tour = system.plan_global_route(tracker, temperature=0.8,
                                                 blocked_lids=blocked_lids)
            if new_tour: tour = new_tour
            new_total = system.service_cost + system._tour_transition_cost(tour)
            tracker.update(new_total)
        if random.random() < 0.3 and env.closed_edges: env.reopen_random_edges(1)

    optimized = system._local_2opt(tour, max_iter=200)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans; tracker.update(final_total)

    TC = lg.transition_cost; N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        if row.dim() > 1: row.fill_diagonal_(float('inf'))
        else: row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower; U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {'final_cost': final_total, 'init_transition': nn_trans,
            'final_transition': post_trans, 'aocc': aocc,
            'trajectory': tracker.trajectory, 'escape_count': 0,
            'replan_count': replan_count, 'service_cost': system.service_cost}


def run_erfm_with_lhh(env, lg, nn_tour, nn_trans):
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    from le_degn_system.models.erfm import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)

    lhh = LHHEngine(env)
    system = LEDEGNSystem(env, erfm, None, lhh, lg)
    tracker = PerformanceTracker(30.0)
    env.closed_edges.clear()
    real_events = env._default_events_real(3)
    tour = list(nn_tour)
    total_cost = system.service_cost + nn_trans
    tracker.update(total_cost)

    for event in real_events:
        for e in event.get('edges', []): env.closed_edges.add(tuple(e))
        affected = False; affected_node = None
        for lid in tour:
            if lid not in lg.lid2edge: continue
            u, v = lg.lid2edge[lid][0], lg.lid2edge[lid][1]
            if (u, v) in env.closed_edges: affected = True; affected_node = u; break
        if affected and affected_node is not None:
            lhh.escape(affected_node, env.closed_edges, verbose=False)
            blocked_lids = {lid for lid in range(lg.num_line_nodes())
                            if (lg.lid2edge[lid][0], lg.lid2edge[lid][1]) in env.closed_edges}
            new_tour = system.plan_global_route(tracker, temperature=0.8,
                                                 blocked_lids=blocked_lids)
            if new_tour: tour = new_tour
            new_total = system.service_cost + system._tour_transition_cost(tour)
            tracker.update(new_total)
        if random.random() < 0.3 and env.closed_edges: env.reopen_random_edges(1)

    optimized = system._local_2opt(tour, max_iter=200)
    post_trans = system._tour_transition_cost(optimized)
    final_total = system.service_cost + post_trans; tracker.update(final_total)

    TC = lg.transition_cost; N_tour = len(optimized) if optimized else 1
    nn_lower = 0.0
    for i in range(min(N_tour, TC.size(0))):
        row = TC[i].clone()
        if row.dim() > 1: row.fill_diagonal_(float('inf'))
        else: row[i] = float('inf')
        nn_lower += row.min().item()
    L = system.service_cost + nn_lower; U = system.service_cost + N_tour * 300.0
    aocc = calculate_aocc(tracker.trajectory, 30.0, L, U)

    return {'final_cost': final_total, 'init_transition': nn_trans,
            'final_transition': post_trans, 'aocc': aocc,
            'trajectory': tracker.trajectory, 'escape_count': lhh.escape_count,
            'replan_count': lhh.escape_count, 'service_cost': system.service_cost}


def run_full_system(env, lg, nn_tour, nn_trans):
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    from le_degn_system.models.erfm import ERFMTrainer
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
    random.seed(42); np.random.seed(42); torch.manual_seed(42)
    results = {}

    print("=" * 60)
    print("LE-DEGN 真实路网消融实验 (OSM Shanghai)")
    print("=" * 60)
    print(f"自适应温度: {ADAPTIVE_TEMP}  自适应SA-DGWN阈值: {ADAPTIVE_THRESHOLD}")

    # Step 1: 加载真实路网（小区域，控制规模）
    loader = RealRoadNetworkLoader(city="Shanghai, China", radius=1200)
    loader.print_statistics()
    base_env = RealRoadNetworkEnv(loader)
    base_lg = LineGraphBuilder(base_env)
    base_lg.build()
    print(f"[实验] 路网规模: {base_env.node_count} 节点, "
          f"{base_env.G.number_of_edges()} 边, "
          f"线图节点: {base_lg.num_line_nodes()}")

    # Step 2: 贪心NN基线
    nn_tour, nn_trans = compute_greedy_nn_tour(base_lg, seed=42)
    print(f"\n[基线] 贪心NN初始转移代价: {nn_trans:.1f}  "
          f"路径长度: {len(nn_tour)} 边")

    configs = [
        ('Full LE-DEGN (real)',     'full_real',     run_full_system),
        ('ERFM + LHH (real)',       'erfm_lhh_real',  run_erfm_with_lhh),
        ('ERFM + SA-DGWN (real)',   'erfm_sadgwn_real', run_erfm_with_sadgwn),
        ('ERFM only (real)',        'erfm_only_real', run_erfm_only),
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

    # 一致性验证
    print("\n" + "=" * 60)
    print("一致性验证")
    print("=" * 60)
    sc_vals = [d['service_cost'] for d in results.values()]
    it_vals = [d['init_transition'] for d in results.values()]
    print(f"  Service Cost 一致: {'PASS' if max(sc_vals)-min(sc_vals)<0.01 else 'FAIL'}")
    print(f"  Init Transition 一致: {'PASS' if max(it_vals)-min(it_vals)<0.01 else 'FAIL'}")

    # 组件贡献分析
    print("\n组件贡献分析 (基于 Total Cost):")
    if all(k in results for k in ['full_real','erfm_lhh_real','erfm_sadgwn_real','erfm_only_real']):
        fc = results['full_real']['final_cost']
        lc = results['erfm_lhh_real']['final_cost']
        sc = results['erfm_sadgwn_real']['final_cost']
        ec = results['erfm_only_real']['final_cost']
        total = ec - fc
        if total > 0:
            print(f"  ERFM+2opt贡献: {ec - max(lc,sc):.1f} ({(ec - max(lc,sc))/total*100:.1f}%)")
            print(f"  LHH贡献:      {sc - lc:.1f} ({(sc-lc)/total*100:.1f}%)")
            print(f"  SA-DGWN贡献:  {lc - fc:.1f} ({(lc-fc)/total*100:.1f}%)")
            print(f"  总改善:       {total:.1f}")

    # 保存结果
    out_path = os.path.join(os.path.dirname(__file__), 'ablation_results_real.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("Ablation Study Results (Real OSM Road Network)")
    print("=" * 60)
    header = f"{'Configuration':<24} {'Final Cost':<12} {'AOCC':<10} {'Esc':<6} {'Repl':<6}"
    print(header); print("-" * 60)
    for cfg_id in ['full_real','erfm_lhh_real','erfm_sadgwn_real','erfm_only_real']:
        if cfg_id not in results: continue
        d = results[cfg_id]
        print(f"{d['name']:<24} {d['final_cost']:<12.1f} "
              f"{d['aocc']:<10.4f} {d['escape_count']:<6} {d['replan_count']:<6}")

    print(f"\nResults saved to: {out_path}")


if __name__ == '__main__':
    main()
