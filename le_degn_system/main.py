#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN 主入口 (Section 10)
从 le_degn_system.py 提取

运行方式:
  python -m le_degn_system.main --nodes 60 --time_limit 8
"""

import os
import random
import argparse

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


def main():
    parser = argparse.ArgumentParser(
        description='LE-DEGN: Dynamic Route Optimization')
    parser.add_argument('--nodes', type=int, default=60)
    parser.add_argument('--time_limit', type=float, default=30.0)
    parser.add_argument('--erfm_episodes', type=int, default=100)
    parser.add_argument('--stgcn_epochs', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--no_baseline', action='store_true')
    parser.add_argument('--output_dir', type=str, default='.')
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("  LE-DEGN: Language-Empowered Dynamic")
    print("  Edge-centric Graph Network (Fixed Version)")
    print("=" * 60)
    print(f"\nConfig: nodes={args.nodes}  time={args.time_limit}s  "
          f"erfm_ep={args.erfm_episodes}  stgcn_ep={args.stgcn_epochs}")

    # Step 1: 创建路网
    print("\n" + "-" * 50)
    print("[Step 1/7] Creating road network...")
    env = RoadNetworkEnv(node_count=args.nodes)

    # Step 2: 构建线图
    print("\n[Step 2/7] Building line graph...")
    lg = LineGraphBuilder(env)
    lg.build()
    print(f"  Original: {env.G.number_of_nodes()} nodes, "
          f"{env.G.number_of_edges()} edges")
    print(f"  Line graph: {lg.num_line_nodes()} nodes, "
          f"{lg.line_graph.number_of_edges()} edges")

    # Step 3: 训练 ERFM
    print("\n[Step 3/7] Training ERFM...")
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    print(f"  ERFM params: {sum(p.numel() for p in erfm.parameters()):,}")
    ERFMTrainer(erfm, lg, env, lr=5e-4).train(episodes=args.erfm_episodes)

    # Step 4: 训练 SA-DGWN
    print("\n[Step 4/7] Training SA-DGWN...")
    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    print(f"  STGCN params: {sum(p.numel() for p in stgcn.parameters()):,}")
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=args.stgcn_epochs,
                                               batch_size=8)

    # Step 5: 创建 LHH 引擎
    print("\n[Step 5/7] Creating LHH engine...")
    lhh = LHHEngine(env)

    # Step 6: 运行 LE-DEGN
    print("\n[Step 6/7] Running LE-DEGN...")
    system = LEDEGNSystem(env, erfm, stgcn, lhh, lg)
    env.closed_edges.clear()
    le_degn_result = system.execute_dynamic(time_budget=args.time_limit,
                                            verbose=True)

    # Step 7: 运行基线
    baseline_result = None
    if not args.no_baseline:
        print("\n[Step 7/7] Running baseline...")
        env.closed_edges.clear()
        baseline = BaselineDHAN(env, lg)
        baseline_events = system._default_events(lg.num_line_nodes())
        baseline_result = baseline.solve(time_budget=args.time_limit,
                                         congestion_events=baseline_events,
                                         verbose=True)

    # 最终报告
    print("\n" + "=" * 60)
    print("  FINAL PERFORMANCE REPORT")
    print("=" * 60)
    header = f"{'Metric':<25} {'LE-DEGN':<15}"
    if baseline_result:
        header += f"{'Baseline':<15}"
    print(header)
    print("-" * 60)
    rows = [('Service Cost (fixed)', 'service_cost', '.1f'),
            ('Init Transition', 'init_transition', '.1f'),
            ('Final Transition', 'final_transition', '.1f'),
            ('Total Final Cost', 'final_cost', '.1f'),
            ('AOCC', 'aocc', '.4f'),
            ('Escape Count', 'escape_count', 'd')]
    for label, key, fmt in rows:
        le_val = le_degn_result.get(key, 0)
        line = f"{label:<25} {le_val:<15{fmt}}"
        if baseline_result and key in baseline_result:
            line += f"{baseline_result[key]:<15{fmt}}"
        print(line)
    if baseline_result:
        le_t = le_degn_result.get('final_transition', 0)
        bl_t = baseline_result.get('final_transition', 0)
        if bl_t > 1e-8:
            print(f"\nLE-DEGN transition improvement: "
                  f"{(bl_t - le_t) / bl_t * 100:+.1f}%")

    # 可视化
    print("\n" + "=" * 60)
    print("  Generating visualizations...")
    print("=" * 60)

    f1 = os.path.join(out_dir, 'le_degn_network.png')
    f2 = os.path.join(out_dir, 'le_degn_convergence.png')
    f3 = os.path.join(out_dir, 'le_degn_components.png')
    f4 = os.path.join(out_dir, 'le_degn_lhh_reflection.png')
    f5 = os.path.join(out_dir, 'le_degn_dashboard.png')

    Visualizer.plot_road_network(env, le_degn_result, f1)
    if baseline_result:
        Visualizer.plot_convergence_comparison(le_degn_result, baseline_result,
                                               args.time_limit, f2)
    Visualizer.plot_component_analysis(le_degn_result, f3)
    Visualizer.plot_lhh_reflection(lhh, f4)
    if baseline_result:
        Visualizer.plot_summary_dashboard(le_degn_result, baseline_result,
                                          env, lhh, f5)

    print("\n" + "=" * 60)
    print("  All tasks completed!")
    print("=" * 60)
    for f in [f1, f2, f3, f4, f5]:
        if os.path.exists(f):
            print(f"  OK {os.path.abspath(f)}")


if __name__ == '__main__':
    main()
