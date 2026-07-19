#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LHH: Language-Heuristic Hybrid 引擎 (语言-启发式混合逃逸与搜索)
来源: le_degn_system.py Section 5 (lines 768-1012)
"""

import math
import random
import heapq
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable

import numpy as np

from le_degn_system.environment.road_network import RoadNetworkEnv


@dataclass
class HeuristicCandidate:
    name: str
    description: str
    func: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    escape_path: List[int] = field(default_factory=list)
    cost: float = float('inf')


class StateVerbalizer:
    @staticmethod
    def verbalize(env, current_node, blocked_edges, k_hop=3):
        subgraph_nodes = {current_node}
        frontier = {current_node}
        for _ in range(k_hop):
            new_frontier = set()
            for n in frontier:
                for _, nb in env.G.out_edges(n):
                    new_frontier.add(nb)
                for nb, _ in env.G.in_edges(n):
                    new_frontier.add(nb)
            subgraph_nodes |= new_frontier
            frontier = new_frontier
        lines = [f"# 当前车辆位于节点 {current_node}",
                 f"# 局部子图: {k_hop}-hop, {len(subgraph_nodes)} 节点"]
        for _, nb, d in env.G.out_edges(current_node, data=True):
            w = d.get('width', 5.0)
            wt = d.get('weight', 10)
            st = "拥堵" if (current_node, nb) in blocked_edges else "可通行"
            lines.append(f"  弧 {current_node}->{nb} [宽{w:.1f}m 成本{wt:.0f}] {st}")
        return '\n'.join(lines)


class HeuristicTemplateLibrary:
    @staticmethod
    def greedy_widest_road(env, start, blocked, max_depth=15, **kw):
        path, visited, cur = [start], {start}, start
        for _ in range(max_depth):
            best_next, best_w = None, -1
            for _, nb, d in env.G.out_edges(cur, data=True):
                if (cur, nb) in blocked or nb in visited:
                    continue
                w = d.get('width', 1.0)
                if w > best_w:
                    best_w, best_next = w, nb
            if best_next is None:
                break
            path.append(best_next); visited.add(best_next); cur = best_next
            if cur not in {n for e in blocked for n in e}:
                break
        return path

    @staticmethod
    def min_penalty_escape(env, start, blocked, max_depth=15, **kw):
        left_pen = env.params.get('left_turn_penalty', 1.5)
        uturn_pen = env.params.get('u_turn_penalty', 7.0)
        path, visited, cur, prev_angle = [start], {start}, start, None
        for _ in range(max_depth):
            best_next, best_cost, best_angle = None, float('inf'), None
            for _, nb, d in env.G.out_edges(cur, data=True):
                if (cur, nb) in blocked or nb in visited:
                    continue
                angle = d.get('angle', 0)
                base = d.get('weight', 10)
                pen = 1.0
                if prev_angle is not None:
                    diff = abs((angle - prev_angle) % 360)
                    if diff > 180: diff = 360 - diff
                    if 150 <= diff <= 210: pen = uturn_pen
                    elif 60 <= diff <= 120: pen = left_pen
                cost = base * pen
                if cost < best_cost:
                    best_cost, best_next, best_angle = cost, nb, angle
            if best_next is None:
                break
            path.append(best_next); visited.add(best_next)
            prev_angle = best_angle; cur = best_next
            if cur not in {n for e in blocked for n in e}:
                break
        return path

    @staticmethod
    def max_connectivity_escape(env, start, blocked, max_depth=15, **kw):
        path, visited, cur = [start], {start}, start
        for _ in range(max_depth):
            best_next, best_deg = None, -1
            for _, nb, d in env.G.out_edges(cur, data=True):
                if (cur, nb) in blocked or nb in visited:
                    continue
                deg = env.G.out_degree(nb)
                if deg > best_deg:
                    best_deg, best_next = deg, nb
            if best_next is None:
                break
            path.append(best_next); visited.add(best_next); cur = best_next
            if cur not in {n for e in blocked for n in e}:
                break
        return path

    @staticmethod
    def adaptive_astar_escape(env, start, blocked, max_depth=50,
                              width_weight=2.0, **kw):
        counter = 0
        open_set = [(0, counter, start, [start])]
        g_score = {start: 0}
        safe = set(env.G.nodes()) - {n for e in blocked for n in e}
        if not safe: safe = set(env.G.nodes())
        target = None
        for _, nb in env.G.out_edges(start):
            if (start, nb) not in blocked and nb in safe:
                for _, nb2 in env.G.out_edges(nb):
                    if (nb, nb2) not in blocked:
                        target = nb2; break
            if target: break
        if target is None:
            sl = list(safe)
            target = random.choice(sl) if sl else start

        def h(n):
            if n not in env.pos or target not in env.pos: return 0
            return math.hypot(env.pos[n][0]-env.pos[target][0],
                              env.pos[n][1]-env.pos[target][1])
        while open_set:
            f, _, cur, path = heapq.heappop(open_set)
            if cur == target or len(path) > max_depth:
                return path
            for _, nb, d in env.G.out_edges(cur, data=True):
                if (cur, nb) in blocked: continue
                wt = d.get('weight', 10)
                w = d.get('width', 3.0)
                cost = wt * (1.0 / max(w/10.0, 0.3)) / width_weight
                tent_g = g_score[cur] + cost
                if nb not in g_score or tent_g < g_score[nb]:
                    g_score[nb] = tent_g
                    counter += 1
                    heapq.heappush(open_set, (tent_g+h(nb), counter, nb, path+[nb]))
        return [start]

    @staticmethod
    def multi_hop_greedy_escape(env, start, blocked, max_depth=20,
                                lookahead=3, **kw):
        path, visited, cur = [start], {start}, start
        for _ in range(max_depth):
            best_next, best_score = None, -float('inf')
            for _, nb, d in env.G.out_edges(cur, data=True):
                if (cur, nb) in blocked or nb in visited: continue
                score = d.get('width', 3.0)*2.0 - d.get('weight', 10)*0.1
                for _, nb2, d2 in env.G.out_edges(nb, data=True):
                    if (nb, nb2) not in blocked and nb2 not in visited:
                        score += d2.get('width', 3.0)*0.5
                if score > best_score:
                    best_score, best_next = score, nb
            if best_next is None: break
            path.append(best_next); visited.add(best_next); cur = best_next
            if cur not in {n for e in blocked for n in e}: break
        return path


class GSESLoop:
    def __init__(self, env):
        self.env = env
        self.library = HeuristicTemplateLibrary()
        self.templates = [
            ('greedy_widest_road', self.library.greedy_widest_road),
            ('min_penalty_escape', self.library.min_penalty_escape),
            ('max_connectivity_escape', self.library.max_connectivity_escape),
            ('adaptive_astar_escape', self.library.adaptive_astar_escape),
            ('multi_hop_greedy_escape', self.library.multi_hop_greedy_escape),
        ]
        self.performance_history: Dict[str, List[float]] = defaultdict(list)

    def run(self, current_node, blocked_edges, verbose=True):
        candidates = []
        for name, func in self.templates:
            cand = HeuristicCandidate(name=name, description=f"Template: {name}", func=func)
            candidates.append(cand)
        for cand in candidates:
            try:
                path = cand.func(self.env, current_node, blocked_edges)
                cost = self._evaluate_path(path, blocked_edges)
                cand.escape_path, cand.cost = path, cost
                cand.score = 1.0 / max(cost, 1e-6) * len(path)
            except Exception:
                cand.escape_path, cand.cost, cand.score = [current_node], float('inf'), 0.0
        candidates.sort(key=lambda c: c.cost)
        best = candidates[0]
        for c in candidates:
            self.performance_history[c.name].append(c.cost)
        if verbose:
            print(f"[GSES] 评估 {len(candidates)} 个候选启发式:")
            for c in candidates:
                avg = np.mean(self.performance_history[c.name]) if self.performance_history[c.name] else 0
                tag = " <- 最佳" if c is best else ""
                print(f"  {c.name}: cost={c.cost:.1f} len={len(c.escape_path)} avg={avg:.1f}{tag}")
        return best

    def _evaluate_path(self, path, blocked):
        if len(path) < 2: return 1e6
        cost = 0
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            if (u, v) in blocked: cost += 1e4
            elif self.env.G.has_edge(u, v):
                d = next(iter(self.env.G[u][v].values()))
                cost += d.get('weight', 10)
            else: cost += 500
        return cost

    def reflect(self):
        weights = {}
        for name, costs in self.performance_history.items():
            weights[name] = 1.0/max(np.mean(costs[-5:]), 1e-3) if costs else 1.0
        total = sum(weights.values())
        if total < 1e-12: return {k: 1.0/len(weights) for k in weights}
        return {k: v/total for k, v in weights.items()}


class LHHEngine:
    def __init__(self, env):
        self.env = env
        self.verbalizer = StateVerbalizer()
        self.gses = GSESLoop(env)
        self.escape_count = 0

    def escape(self, current_node, blocked_edges, verbose=True):
        self.escape_count += 1
        if verbose:
            prompt = self.verbalizer.verbalize(self.env, current_node, blocked_edges)
            print(f"\n[LHH] -- 逃逸 #{self.escape_count} --")
            for line in prompt.split('\n')[:5]:
                print(f"  {line}")
        best = self.gses.run(current_node, blocked_edges, verbose)
        if verbose:
            print(f"[LHH] 选定: {best.name} | 路径: {best.escape_path}")
            prefs = self.gses.reflect()
            top = sorted(prefs.items(), key=lambda x: -x[1])[:3]
            print(f"[LHH] 反思偏好: {[f'{k}={v:.2f}' for k, v in top]}")
        return best.escape_path
