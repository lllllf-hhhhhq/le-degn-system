# -*- coding: utf-8 -*-
"""
Section 8: 基线对比
从 le_degn_system.py 提取

包含:
  - BaselineDHAN: 基于贪心最近邻的 DHAN 基线算法，
    使用转移代价矩阵进行路径规划，支持拥堵逃逸重规划
"""

import random

from le_degn_system.core.metrics import PerformanceTracker, calculate_aocc
from le_degn_system.environment.road_network import RoadNetworkEnv
from le_degn_system.environment.line_graph import LineGraphBuilder


class BaselineDHAN:
    """DHAN + 贪心最近邻基线算法。

    使用多起点贪心最近邻策略，基于转移代价矩阵 (transition_cost)
    生成边遍历顺序，并支持拥堵事件下的逃逸重规划。

    用于与 LE-DEGN 的深度强化学习/注意力机制方法进行对比。
    """

    def __init__(self, env, lg):
        self.env = env
        self.lg = lg
        self.service_cost = sum(
            self.lg.lid2edge[i][3].get('weight', 10)
            for i in range(self.lg.num_line_nodes()))

    def solve(self, time_budget=10.0, congestion_events=None, verbose=True):
        tracker = PerformanceTracker(time_budget)
        N = self.lg.num_line_nodes()
        if N == 0:
            return {'final_cost': float('inf'), 'init_cost': float('inf'),
                    'aocc': 0.0, 'trajectory': [], 'escape_count': 0,
                    'lower_bound': 0, 'upper_bound': 1}
        if verbose:
            print("\n" + "="*60)
            print("基线 DHAN + 贪心最近邻 启动")
            print("="*60)

        # ★ 基线: 最近邻贪心（基于转移代价矩阵）
        TC = self.lg.transition_cost
        max_tour = min(N, 120)
        available = list(range(N))
        if N > max_tour:
            available = random.sample(available, max_tour)

        # 尝试多个起点
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
                if nearest is None: break
                tour.append(nearest)
                unvisited.remove(nearest)
                cur = nearest
            trans = sum(TC[tour[i], tour[i+1]].item() for i in range(len(tour)-1))
            trans += TC[tour[-1], tour[0]].item()
            if trans < best_trans:
                best_trans, best_tour = trans, list(tour)

        init_total = self.service_cost + best_trans
        tracker.update(init_total)
        if verbose:
            print(f"  最近邻路径: {len(best_tour)} 条边")
            print(f"  转移代价: {best_trans:.1f}")
            print(f"  总成本: {init_total:.1f}")

        # ★ 修复: Baseline 真实验逃逸处理——在排除封锁边后重新运行贪心NN
        escape_count = 0
        cur_tour = list(best_tour)
        cur_trans = best_trans
        for event in (congestion_events or []):
            for e in event.get('edges', []):
                self.env.closed_edges.add(tuple(e))
            # 找出当前路径中被封锁的边
            blocked_lids = set()
            for lid in range(N):
                u, v, _, _ = self.lg.lid2edge[lid]
                if (u, v) in self.env.closed_edges:
                    blocked_lids.add(lid)
            affected = [lid for lid in cur_tour if lid in blocked_lids]
            if not affected:
                continue
            escape_count += len(affected)
            # 在排除封锁边后重新运行贪心最近邻
            available = [lid for lid in range(N)
                         if lid not in blocked_lids]
            if len(available) < 2:
                continue
            # 多起点贪心NN重规划
            re_best_tour, re_best_trans = None, float('inf')
            re_starts = random.sample(available, min(5, len(available)))
            for start in re_starts:
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
                trans = sum(TC[tour[i], tour[i + 1]].item()
                            for i in range(len(tour) - 1))
                if len(tour) > 1:
                    trans += TC[tour[-1], tour[0]].item()
                if trans < re_best_trans:
                    re_best_trans, re_best_tour = trans, list(tour)
            if re_best_tour is not None:
                cur_tour = re_best_tour
                cur_trans = re_best_trans
                new_total = self.service_cost + cur_trans
                tracker.update(new_total)

        final_trans = cur_trans
        final_total = self.service_cost + final_trans
        tracker.update(final_total)

        # 计算下界和上界
        nn_lower = 0.0
        for i in range(min(len(best_tour), TC.size(0))):
            row = TC[i].clone()
            row[i] = float('inf')
            nn_lower += row.min().item()
        L = self.service_cost + nn_lower
        U = self.service_cost + len(best_tour) * 300.0
        aocc = calculate_aocc(tracker.trajectory, time_budget, L, U)

        result = {'final_cost': final_total, 'init_cost': init_total,
                  'service_cost': self.service_cost,
                  'init_transition': best_trans, 'final_transition': final_trans,
                  'aocc': aocc, 'trajectory': tracker.trajectory,
                  'escape_count': escape_count, 'lower_bound': L, 'upper_bound': U}
        if verbose:
            print(f"\n基线结果: 总成本={final_total:.1f}  "
                  f"转移={final_trans:.1f}  AOCC={aocc:.4f}  逃逸={escape_count}")
        return result
