#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RealRoadNetworkEnv: 真实OSM路网环境
====================================
实现与 RoadNetworkEnv 完全兼容的接口，
使 LEDEGNSystem 无需修改即可在真实路网上运行。

将 RealRoadNetworkLoader 的输出适配为 LEDEGNSystem 可直接使用的格式。
"""

import math
import random
from typing import Dict, Tuple, List

import numpy as np
import networkx as nx

from real_data_loader import RealRoadNetworkLoader


class RealRoadNetworkEnv:
    """
    真实 OSM 路网环境 —— RoadNetworkEnv 的直接替代品

    使用方式:
        loader = RealRoadNetworkLoader(city="Shanghai, China", radius=3000)
        env = RealRoadNetworkEnv(loader)
        lg = LineGraphBuilder(env)
        lg.build()
        # 之后所有对 env 的使用与 RoadNetworkEnv 完全一致
    """

    def __init__(self, loader: RealRoadNetworkLoader):
        """
        Args:
            loader: 已加载完毕的 RealRoadNetworkLoader 实例
        """
        self.G: nx.MultiDiGraph = loader.G
        self.pos: Dict[int, Tuple[float, float]] = loader.pos
        self.edge_widths: Dict[Tuple[int, int], float] = loader.edge_widths
        self.closed_edges: set = set()

        # LHH 逃逸参数（与 RoadNetworkEnv 默认值一致）
        self.params = {
            'left_turn_penalty': 1.5,
            'u_turn_penalty': 7.0,
            'avg_degree': 2.7,
            't_junction_ratio': 0.65,
            'cross_junction_ratio': 0.18,
            'dead_end_ratio': 0.07,
            'segment_length_mean': 80,
            'segment_length_std': 20,
            'min_turning_radius': 5.0,
        }

        self.node_count = self.G.number_of_nodes()
        self.size_x = 1
        self.size_y = 1

        # 预计算最短路径
        self._precompute_shortest_paths()

        n_edges = self.G.number_of_edges()
        print(f"[RealRoadNetworkEnv] 就绪: {self.node_count} 节点, "
              f"{n_edges} 边  强连通={'是' if nx.is_strongly_connected(self.G) else '否'}")

    def _precompute_shortest_paths(self) -> None:
        """预计算全源最短路径（与 RoadNetworkEnv 逻辑完全一致）"""
        simple_G = nx.DiGraph()
        for u, v, d in self.G.edges(data=True):
            w = d.get('weight', 10)
            if simple_G.has_edge(u, v):
                if w < simple_G[u][v]['weight']:
                    simple_G[u][v]['weight'] = w
            else:
                simple_G.add_edge(u, v, weight=w)

        try:
            self.sp_dist = dict(
                nx.all_pairs_dijkstra_path_length(simple_G, weight='weight'))
        except Exception:
            self.sp_dist = {}
        print(f"[RealRoadNetworkEnv] 最短路径矩阵: {len(self.sp_dist)} 源节点")

    def shortest_path_cost(self, u: int, v: int) -> float:
        """查询两点间最短路径代价"""
        if u == v:
            return 0.0
        if u in self.sp_dist and v in self.sp_dist[u]:
            return self.sp_dist[u][v]
        if u in self.pos and v in self.pos:
            return math.hypot(
                self.pos[u][0] - self.pos[v][0],
                self.pos[u][1] - self.pos[v][1]) * 3.0
        return 500.0

    # ── 拥堵事件管理 ──

    def close_edge(self, u: int, v: int) -> None:
        """封堵单条边"""
        self.closed_edges.add((u, v))

    def open_edge(self, u: int, v: int) -> None:
        """开放单条边"""
        self.closed_edges.discard((u, v))

    def close_random_edges(self, n: int) -> List[Tuple[int, int]]:
        """随机封堵 n 条边"""
        avail = [(u, v) for u, v, *_ in self.G.edges(keys=False)
                 if (u, v) not in self.closed_edges]
        if not avail:
            return []
        chosen = random.sample(avail, min(n, len(avail)))
        for e in chosen:
            self.closed_edges.add(e)
        return chosen

    def reopen_random_edges(self, n: int) -> List[Tuple[int, int]]:
        """随机重新开放 n 条边"""
        if not self.closed_edges:
            return []
        chosen = random.sample(
            list(self.closed_edges), min(n, len(self.closed_edges)))
        for e in chosen:
            self.closed_edges.discard(e)
        return chosen

    # ── 基于真实拥堵概率的智能事件生成 ──

    def _default_events_real(self, num_events: int = 3) -> List[dict]:
        """
        基于 OSM road type 的真实拥堵概率生成事件。
        高 congestion_prob 的边（如施工路段、商业步行街）更可能被选中。
        """
        edges = [(u, v, self.G[u][v][0].get('congestion_prob', 0.3))
                 for u, v, *_ in self.G.edges(keys=False)
                 if (u, v) not in self.closed_edges]
        if not edges:
            return []

        probs = np.array([e[2] for e in edges])
        probs = probs / probs.sum()

        events = []
        for i in range(num_events):
            num_block = random.randint(2, max(3, len(edges) // 10))
            try:
                chosen_idx = np.random.choice(
                    len(edges), size=min(num_block, len(edges)),
                    replace=False, p=probs)
            except ValueError:
                chosen_idx = np.random.choice(
                    len(edges), size=min(num_block, len(edges)),
                    replace=False)
            chosen = [(edges[idx][0], edges[idx][1]) for idx in chosen_idx]
            events.append({
                'type': f'real_congestion_wave_{i + 1}',
                'edges': [list(e) for e in chosen]
            })
        return events
