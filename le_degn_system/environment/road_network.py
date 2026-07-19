# -*- coding: utf-8 -*-
"""
Section 1: 混合路网环境
从 le_degn_system.py 提取

包含:
  - RoadNetworkEnv: 混合路网环境，生成带方向规则的老城区路网拓扑
"""

import math
import random
import numpy as np
import networkx as nx
from typing import Dict, Tuple


class RoadNetworkEnv:
    """混合路网环境：生成模拟老城区混合路网的有向多重图。

    支持道路类型（商业街、学校周边、主干道、居民区、施工路段）、
    通行方向规则、强连通性保证、最短路径预计算。
    """

    def __init__(self, node_count: int = 50, old_town_params: dict = None):
        self.G = nx.MultiDiGraph()
        self.size_x = max(3, math.ceil(math.sqrt(node_count)))
        self.size_y = max(3, math.ceil(node_count / self.size_x))
        self.node_count = node_count
        self.params = old_town_params or {
            'avg_degree': 2.7, 't_junction_ratio': 0.65,
            'cross_junction_ratio': 0.18, 'dead_end_ratio': 0.07,
            'segment_length_mean': 80, 'segment_length_std': 20,
            'min_turning_radius': 5.0, 'left_turn_penalty': 1.5,
            'u_turn_penalty': 7.0,
        }
        self.pos: Dict[int, Tuple[float, float]] = {}
        self.closed_edges: set = set()
        self.edge_widths: Dict[Tuple[int, int], float] = {}
        self._build_network()
        self._apply_direction_rules()
        self._ensure_strong_connectivity()
        # ★ 预计算全源最短路径
        self._precompute_shortest_paths()

    def _build_network(self):
        nid, nmap = 0, {}
        step = 50.0 / max(self.size_x, self.size_y)
        for i in range(self.size_y):
            for j in range(self.size_x):
                if nid >= self.node_count:
                    break
                x = j * step + np.random.normal(0, step * 0.25)
                y = -i * step + np.random.normal(0, step * 0.25)
                nmap[(i, j)] = nid
                self.pos[nid] = (x, y)
                self.G.add_node(nid)
                nid += 1
            if nid >= self.node_count:
                break
        self.node_count = len(nmap)
        target_edges = int(self.node_count * self.params['avg_degree'] / 2)
        ec = 0
        cj = self.size_x // 2
        for i in range(self.size_y - 1):
            if (i, cj) in nmap and (i + 1, cj) in nmap:
                u, v = nmap[(i, cj)], nmap[(i + 1, cj)]
                w = np.random.uniform(15, 25)
                if not self.G.has_edge(u, v):
                    base_length = 80
                    speed_factor = 1.2  # 主干道速度因子
                    length = base_length / speed_factor
                    self.G.add_edge(u, v, weight=length, width=w, angle=180,
                                   type=0, scenario='主干道',
                                   time_window={'E': 0, 'L': 1440}, color='#45B7D1',
                                   speed_factor=1.2, congestion_prob=0.2)
                    self.edge_widths[(u, v)] = w
                    ec += 1
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        for i in range(self.size_y):
            for j in range(self.size_x):
                if (i, j) not in nmap:
                    continue
                curr = nmap[(i, j)]
                jtype = self._sample_junction()
                max_e = 1 if jtype == 'dead' else (3 if jtype == 't' else 4)
                cur_deg = self.G.degree(curr)
                rem = max(0, max_e - cur_deg)
                random.shuffle(dirs)
                for di, dj in dirs[:rem]:
                    ni, nj = i + di, j + dj
                    if (ni, nj) not in nmap:
                        continue
                    nxt = nmap[(ni, nj)]
                    if self.G.has_edge(curr, nxt):
                        continue
                    base_length = max(30, np.random.normal(
                        self.params['segment_length_mean'],
                        self.params['segment_length_std']))
                    w = self._rand_width()
                    angle = self._calc_angle(di, dj)
                    rt = self._rand_road_type(j, cj)
                    speed_factor = rt.get('speed_factor', 1.0)
                    length = base_length / speed_factor
                    self.G.add_edge(curr, nxt, weight=length, width=w,
                                   angle=angle, **rt)
                    self.edge_widths[(curr, nxt)] = w
                    ec += 1
                    if ec >= target_edges:
                        return

    def _sample_junction(self):
        r = random.random()
        if r < self.params['dead_end_ratio']:
            return 'dead'
        if r < self.params['dead_end_ratio'] + self.params['t_junction_ratio']:
            return 't'
        return 'cross'

    def _rand_width(self):
        ws = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0]
        ps = [0.20, 0.25, 0.20, 0.15, 0.10, 0.05, 0.03, 0.02]
        return float(np.random.choice(ws, p=ps))

    def _calc_angle(self, di, dj):
        base = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}.get(
            (di, dj), 0)
        return (base + np.random.normal(0, 15)) % 360

    def _rand_road_type(self, j, cj):
        scenarios = [
            {
                'type': 0,
                'scenario': '商业步行街',
                'time_window': {'E': 0, 'L': 1440},
                'color': '#FF6B6B',
                'speed_factor': 0.5,  # 限速，通行时间延长
                'congestion_prob': 0.4  # 人流量大，容易拥堵
            },
            {
                'type': 1,
                'scenario': '学校周边',
                'time_window': {'E': 540, 'L': 1020},
                'color': '#4ECDC4',
                'speed_factor': 0.6,  # 上下学时段限速
                'congestion_prob': 0.5  # 上下学高峰容易拥堵
            },
            {
                'type': 0,
                'scenario': '主干道',
                'time_window': {'E': 0, 'L': 1440},
                'color': '#45B7D1',
                'speed_factor': 1.2,  # 宽阔高速，通行时间缩短
                'congestion_prob': 0.2  # 车道多，不易拥堵
            },
            {
                'type': 0,
                'scenario': '居民区',
                'time_window': {'E': 0, 'L': 1440},
                'color': '#96CEB4',
                'speed_factor': 0.7,  # 限速通行
                'congestion_prob': 0.3  # 相对畅通
            },
            {
                'type': 1,
                'scenario': '施工路段',
                'time_window': {'E': 0, 'L': 1440},
                'color': '#FFEAA7',
                'speed_factor': 0.3,  # 施工占用道路，通行时间大幅延长
                'congestion_prob': 0.8  # 经常拥堵
            },
        ]
        if abs(j - cj) <= 1:
            p = [0.1, 0.1, 0.5, 0.2, 0.1]
        else:
            p = [0.1, 0.1, 0.1, 0.6, 0.1]
        s = np.random.choice(scenarios, p=p)
        return dict(s)

    def _apply_direction_rules(self):
        to_rm = []
        for u, v, data in self.G.edges(data=True):
            w = data.get('width', 5.0)
            if w < 4.5 and self.G.has_edge(v, u):
                to_rm.append((v, u))
            elif 3.0 <= w < 4.5:
                data['weight'] *= 1.5
        for u, v in to_rm:
            if self.G.has_edge(u, v):
                self.G.remove_edge(u, v)

    def _ensure_strong_connectivity(self):
        added = 0
        for n in list(self.G.nodes()):
            if self.G.degree(n) == 0:
                candidates = [m for m in self.G.nodes()
                              if m != n and self.G.degree(m) > 0]
                if not candidates:
                    candidates = [m for m in self.G.nodes() if m != n]
                if not candidates:
                    continue
                near = min(candidates,
                           key=lambda m: math.hypot(
                               self.pos[n][0] - self.pos[m][0],
                               self.pos[n][1] - self.pos[m][1]))
                for a, b in [(n, near), (near, n)]:
                    self.G.add_edge(a, b, weight=80, width=5.0, angle=0,
                                   type=0, scenario='连通补边',
                                   time_window={'E': 0, 'L': 1440},
                                   color='#45B7D1')
                    added += 1
        for _ in range(30):
            sinks = [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
            if not sinks:
                break
            for s in sinks:
                near = min((m for m in self.G.nodes() if m != s),
                           key=lambda m: math.hypot(
                               self.pos[s][0] - self.pos[m][0],
                               self.pos[s][1] - self.pos[m][1]))
                self.G.add_edge(s, near, weight=80, width=5.0, angle=0,
                               type=0, scenario='连通补边',
                               time_window={'E': 0, 'L': 1440}, color='#45B7D1')
                added += 1
        for _ in range(200):
            if nx.is_strongly_connected(self.G):
                break
            sccs = sorted(nx.strongly_connected_components(self.G),
                          key=len, reverse=True)
            if len(sccs) < 2:
                break
            s1, s2 = sccs[0], sccs[1]
            best = min(((u, v) for u in s1 for v in s2),
                       key=lambda p: math.hypot(
                           self.pos[p[0]][0] - self.pos[p[1]][0],
                           self.pos[p[0]][1] - self.pos[p[1]][1]))
            for a, b in [best, (best[1], best[0])]:
                if not self.G.has_edge(a, b):
                    self.G.add_edge(a, b, weight=80, width=5.0, angle=0,
                                   type=0, scenario='连通补边',
                                   time_window={'E': 0, 'L': 1440},
                                   color='#45B7D1')
                    added += 1
        print(f"[路网] 节点={self.G.number_of_nodes()}  "
              f"边={self.G.number_of_edges()}  补边={added}  "
              f"强连通={'是' if nx.is_strongly_connected(self.G) else '否'}")

    def _precompute_shortest_paths(self):
        """★ 预计算全源最短路径（用于转移代价计算）"""
        # 构建简单有向图用于最短路径
        simple_G = nx.DiGraph()
        for u, v, d in self.G.edges(data=True):
            w = d.get('weight', 10)
            if simple_G.has_edge(u, v):
                if w < simple_G[u][v]['weight']:
                    simple_G[u][v]['weight'] = w
            else:
                simple_G.add_edge(u, v, weight=w)
        try:
            self.sp_dist = dict(nx.all_pairs_dijkstra_path_length(
                simple_G, weight='weight'))
        except Exception:
            self.sp_dist = {}
        print(f"[路网] 最短路径矩阵: {len(self.sp_dist)} 源节点")

    def shortest_path_cost(self, u, v):
        """查询两点间最短路径代价"""
        if u == v:
            return 0.0
        if u in self.sp_dist and v in self.sp_dist[u]:
            return self.sp_dist[u][v]
        # 回退：欧氏距离 × 惩罚系数
        if u in self.pos and v in self.pos:
            return math.hypot(self.pos[u][0] - self.pos[v][0],
                              self.pos[u][1] - self.pos[v][1]) * 3.0
        return 500.0

    def close_edge(self, u, v):
        self.closed_edges.add((u, v))

    def open_edge(self, u, v):
        self.closed_edges.discard((u, v))

    def close_random_edges(self, n):
        avail = [(u, v) for u, v, *_ in self.G.edges(keys=False)
                 if (u, v) not in self.closed_edges]
        chosen = random.sample(avail, min(n, len(avail)))
        for e in chosen:
            self.closed_edges.add(e)
        return chosen

    def reopen_random_edges(self, n):
        if not self.closed_edges:
            return []
        chosen = random.sample(list(self.closed_edges),
                               min(n, len(self.closed_edges)))
        for e in chosen:
            self.closed_edges.discard(e)
        return chosen
