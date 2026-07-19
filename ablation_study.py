#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN Ablation Study Script
用于组件消融研究，评估各组件的贡献
"""

import os
import sys
import json
import random
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from le_degn_system import (
    RoadNetworkEnv, LineGraphBuilder, ERFM, SADGWN, 
    TrafficDataGenerator, LHHEngine, LEDEGNSystem, BaselineDHAN,
    PerformanceTracker, calculate_aocc
)

def run_erfm_only(env, lg, env_params):
    """只使用ERFM的简化版本"""
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    
    from le_degn_system import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)
    
    system = LEDEGNSystem(env, erfm, None, None, lg)
    
    tracker = PerformanceTracker(30.0)
    
    emb = erfm.encode(lg.node_features, lg.penalty_matrix)
    N = emb.size(0)
    available = list(range(N))
    max_tour = min(len(available), 80)
    if len(available) > max_tour:
        available = random.sample(available, max_tour)
    
    unvisited = list(available)
    start = random.choice(unvisited)
    tour = [unvisited.pop(unvisited.index(start))]
    
    while unvisited:
        cur = tour[-1]
        vis_t = torch.tensor(tour, dtype=torch.long)
        unv_t = torch.tensor(unvisited, dtype=torch.long)
        probs = erfm.decode_step(emb, cur, vis_t, unv_t, 0.3)
        chosen_local = int(torch.argmax(probs).item())
        chosen = unvisited[chosen_local]
        tour.append(chosen)
        unvisited.remove(chosen)
    
    trans_cost = system._tour_transition_cost(tour)
    total_cost = system.service_cost + trans_cost
    tracker.update(total_cost)
    
    return {
        'final_cost': total_cost,
        'init_transition': trans_cost,
        'final_transition': trans_cost,
        'trajectory': tracker.trajectory,
        'escape_count': 0,
        'service_cost': system.service_cost
    }

def run_erfm_with_lhh(env, lg, env_params):
    """使用ERFM + LHH"""
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    
    from le_degn_system import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)
    
    lhh = LHHEngine(env)
    system = LEDEGNSystem(env, erfm, None, lhh, lg)
    
    env.closed_edges.clear()
    events = system._default_events(lg.num_line_nodes())
    
    tour = system.plan_global_route(temperature=0.5)
    node_path = system.tour_to_node_path(tour)
    tracker = PerformanceTracker(30.0)
    trans_cost = system._tour_transition_cost(tour)
    total_cost = system.service_cost + trans_cost
    tracker.update(total_cost)
    
    for event in events:
        edges_to_block = event.get('edges', [])
        for e in edges_to_block:
            env.closed_edges.add(tuple(e))
        
        progress = 0
        affected, affected_node = False, None
        for lid in tour[progress:]:
            if lid not in lg.lid2edge: continue
            u, v, _, _ = lg.lid2edge[lid]
            if (u, v) in env.closed_edges:
                affected, affected_node = True, u
                break
        
        if affected and affected_node is not None:
            escape_path = lhh.escape(affected_node, env.closed_edges, verbose=False)
            blocked_lids = set()
            for lid in range(lg.num_line_nodes()):
                u, v, _, _ = lg.lid2edge[lid]
                if (u, v) in env.closed_edges:
                    blocked_lids.add(lid)
            new_tour = system.plan_global_route(tracker, temperature=0.8, blocked_lids=blocked_lids)
            new_total = system._tour_total_cost(new_tour)
            tracker.update(new_total)
            tour = new_tour
            progress = 0
        
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
        'init_transition': trans_cost,
        'final_transition': post_trans,
        'aocc': aocc,
        'trajectory': tracker.trajectory,
        'escape_count': lhh.escape_count,
        'service_cost': system.service_cost
    }

def run_full_system(env, lg, env_params):
    """完整LE-DEGN系统"""
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    
    from le_degn_system import ERFMTrainer
    trainer = ERFMTrainer(erfm, lg, env, lr=5e-4)
    trainer.train(episodes=100)
    
    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=20, batch_size=8)
    
    lhh = LHHEngine(env)
    system = LEDEGNSystem(env, erfm, stgcn, lhh, lg)
    
    result = system.execute_dynamic(time_budget=30.0, verbose=False)
    
    return result

def main():
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    results = {}
    
    print("="*60)
    print("LE-DEGN Ablation Study")
    print("="*60)
    
    # Test configurations
    configs = [
        ('Full LE-DEGN', 'full'),
        ('ERFM-only', 'erfm_only'),
        ('ERFM+LHH', 'erfm_lhh'),
    ]
    
    for name, config_type in configs:
        print(f"\n[Testing] {name}")
        
        env = RoadNetworkEnv(node_count=60)
        lg = LineGraphBuilder(env)
        lg.build()
        
        if config_type == 'full':
            result = run_full_system(env, lg, None)
        elif config_type == 'erfm_only':
            result = run_erfm_only(env, lg, None)
        elif config_type == 'erfm_lhh':
            result = run_erfm_with_lhh(env, lg, None)
        
        results[config_type] = {
            'name': name,
            'final_cost': result.get('final_cost', 0),
            'init_transition': result.get('init_transition', 0),
            'final_transition': result.get('final_transition', 0),
            'aocc': result.get('aocc', 0),
            'escape_count': result.get('escape_count', 0),
            'service_cost': result.get('service_cost', 0)
        }
        
        print(f"  Final Cost: {result.get('final_cost', 0):.1f}")
        print(f"  AOCC: {result.get('aocc', 0):.4f}")
        print(f"  Escape Count: {result.get('escape_count', 0)}")
    
    # Save results
    with open('ablation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("Ablation Study Results")
    print("="*60)
    print(f"{'Configuration':<20} {'Final Cost':<15} {'AOCC':<10} {'Escapes':<10}")
    print("-"*60)
    for config_type, data in results.items():
        print(f"{data['name']:<20} {data['final_cost']:<15.1f} {data['aocc']:<10.4f} {data['escape_count']:<10}")
    
    print("\nResults saved to: ablation_results.json")

if __name__ == '__main__':
    main()
