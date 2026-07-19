# -*- coding: utf-8 -*-
"""
Section 2: 线图变换器
从 le_degn_system.py 提取

包含:
  - LineGraphBuilder: 将原始路网的路段（边）转换为线图节点，
    构建线图拓扑用于 GNN 编码，并预计算转移代价矩阵
"""

from typing import Dict, Tuple, Optional

import networkx as nx
import torch

from le_degn_system.environment.road_network import RoadNetworkEnv


class LineGraphBuilder:
    """线图变换器：将原始路网的多重有向图转换为线图。

    线图中每个节点对应原始路网的一条有向边，
    线图边表示路段间的可转移连通关系（共享中间节点）。

    核心功能:
      - 线图拓扑构建
      - 边特征提取 (EDGE_FEAT_DIM=13)
      - 转弯惩罚矩阵
      - 邻接矩阵
      - 转移代价矩阵 (transition_cost)
    """

    EDGE_FEAT_DIM = 13

    def __init__(self, env: RoadNetworkEnv):
        self.env = env
        self.edge2lid: Dict[Tuple[int, int, int], int] = {}
        self.lid2edge: Dict[int, Tuple[int, int, int, dict]] = {}
        self.line_graph: Optional[nx.DiGraph] = None
        self.node_features: Optional[torch.Tensor] = None
        self.penalty_matrix: Optional[torch.Tensor] = None
        self.adj: Optional[torch.Tensor] = None
        # ★ 转移代价矩阵
        self.transition_cost: Optional[torch.Tensor] = None

    def build(self) -> nx.DiGraph:
        G = self.env.G
        lid = 0
        for u, v, k, d in G.edges(data=True, keys=True):
            self.edge2lid[(u, v, k)] = lid
            self.lid2edge[lid] = (u, v, k, d)
            lid += 1
        N = lid
        self.line_graph = nx.DiGraph()
        self.line_graph.add_nodes_from(range(N))
        for i in range(N):
            _, vi, _, di = self.lid2edge[i]
            for j in range(N):
                if i == j:
                    continue
                uj, _, _, dj = self.lid2edge[j]
                if vi == uj:
                    tp = self._turn_penalty(di.get('angle', 0),
                                            dj.get('angle', 0))
                    self.line_graph.add_edge(i, j, turn_penalty=tp,
                                            shared_node=vi)
        self._extract_features()
        self._build_penalty_matrix()
        self._build_adj()
        self._build_transition_costs()   # ★ 新增
        print(f"[线图] 线图节点={N}  线图边={self.line_graph.number_of_edges()}")
        return self.line_graph

    @staticmethod
    def _turn_penalty(a_in, a_out):
        d = abs((a_out - a_in) % 360)
        if d > 180:
            d = 360 - d
        if d < 30:
            return 1.0
        if 60 <= d <= 120:
            return 1.5
        if 150 <= d <= 210:
            return 7.0
        return 1.0

    def _extract_features(self):
        feats = []
        for i in range(len(self.lid2edge)):
            u, v, k, d = self.lid2edge[i]
            pu, pv = self.env.pos[u], self.env.pos[v]
            tw = d.get('time_window', {'E': 0, 'L': 1440})
            feats.append([
                d.get('weight', 10) / 200.0,
                d.get('width', 5) / 25.0,
                d.get('angle', 0) / 360.0,
                float(d.get('type', 0)),
                pu[0] / 60.0, pu[1] / 60.0,
                pv[0] / 60.0, pv[1] / 60.0,
                self.env.G.in_degree(u) / 10.0,
                self.env.G.out_degree(v) / 10.0,
                d.get('turn_penalty', 1.0) / 7.0,
                tw.get('E', 0) / 1440.0,
                tw.get('L', 1440) / 1440.0,
            ])
        self.node_features = torch.tensor(feats, dtype=torch.float32)

    def _build_penalty_matrix(self):
        N = len(self.lid2edge)
        M = torch.zeros(N, N)
        for i, j, d in self.line_graph.edges(data=True):
            p = d.get('turn_penalty', 1.0)
            if p >= 7.0:
                M[i, j] = -8.0
            elif p >= 1.5:
                M[i, j] = -1.5
        self.penalty_matrix = M

    def _build_adj(self):
        N = len(self.lid2edge)
        A = torch.zeros(N, N)
        for i, j in self.line_graph.edges():
            A[i, j] = 1.0
        self.adj = A

    def _build_transition_costs(self):
        """★ 核心修复：构建线图节点间的真实转移代价矩阵

        transition_cost[i][j] = 从边i的终点到边j的起点的最短路径代价
                               + 转弯惩罚

        这才是排列顺序影响的、需要优化的成本部分。
        """
        N = len(self.lid2edge)
        TC = torch.full((N, N), 500.0)  # 默认大值

        for i in range(N):
            _, vi, _, di = self.lid2edge[i]  # 边i: ?->vi
            for j in range(N):
                if i == j:
                    TC[i, j] = 0.0
                    continue
                uj, _, _, dj = self.lid2edge[j]  # 边j: uj->?

                # 从边i的终点(vi)到边j的起点(uj)的最短路径代价
                sp_cost = self.env.shortest_path_cost(vi, uj)

                # 转弯惩罚（仅当直接相连时有意义）
                turn_pen = 0.0
                if vi == uj:  # 直接衔接
                    tp = self._turn_penalty(
                        di.get('angle', 0), dj.get('angle', 0))
                    turn_pen = (tp - 1.0) * 15.0  # 放大转弯惩罚

                TC[i, j] = sp_cost + turn_pen

        self.transition_cost = TC
        avg_tc = TC[TC < 490].mean().item() if (TC < 490).any() else 0
        print(f"[线图] 转移代价矩阵: {N}x{N}, 平均转移代价={avg_tc:.1f}")

    def num_line_nodes(self):
        return len(self.lid2edge)
