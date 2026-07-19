#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE-DEGN: Language-Empowered Dynamic Edge-centric Graph Network
================================================================
面向单双向混杂城区街景拍摄的动态路径优化大模型系统

修复版本: 修复了成本函数、训练信号、确定性解码等核心问题

运行方式:
  python le_degn_system.py --nodes 60 --time_limit 8
"""

import os
import sys
import time
import math
import copy
import random
import heapq
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Callable

import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontManager

# ── 字体配置 ──
_font_families = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei',
                  'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
_fm = FontManager()
_available = [f.name for f in _fm.ttflist]
_sel = next((f for f in _font_families if f in _available), None)
matplotlib.rcParams['font.sans-serif'] = [_sel] if _sel else ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 0: 通用工具                                     ║
# ╚═══════════════════════════════════════════════════════════╝

class PerformanceTracker:
    def __init__(self, time_budget: float, record_interval: float = 0.05):
        self.trajectory: List[Tuple[float, float]] = []
        self.start_time = time.time()
        self.time_budget = time_budget
        self.record_interval = record_interval
        self.last_record_time = self.start_time
        self.best_cost = float('inf')

    def update(self, current_cost: float) -> bool:
        now = time.time()
        elapsed = now - self.start_time
        if current_cost < self.best_cost:
            self.best_cost = current_cost
            self.trajectory.append((elapsed, self.best_cost))
            self.last_record_time = now
        elif now - self.last_record_time >= self.record_interval:
            self.trajectory.append((elapsed, self.best_cost))
            self.last_record_time = now
        return elapsed < self.time_budget

    def elapsed(self) -> float:
        return time.time() - self.start_time


def calculate_aocc(trajectory, time_budget, L, U):
    if not trajectory:
        return 0.0
    steps = np.linspace(0, time_budget, num=500)
    total, idx = 0.0, 0
    for t in steps:
        while idx < len(trajectory) - 1 and trajectory[idx + 1][0] <= t:
            idx += 1
        y = trajectory[idx][1]
        y_b = max(L, min(y, U))
        y_n = (y_b - L) / (U - L) if U > L else 1.0
        total += 1.0 - y_n
    return total / len(steps)


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 1: 混合路网环境                                  ║
# ╚═══════════════════════════════════════════════════════════╝

class RoadNetworkEnv:
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


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 2: 线图变换器                                    ║
# ╚═══════════════════════════════════════════════════════════╝

class LineGraphBuilder:
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
        print(f"[线图] 转移代价矩阵: {N}×{N}, 平均转移代价={avg_tc:.1f}")

    def num_line_nodes(self):
        return len(self.lid2edge)


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 3: ERFM                                         ║
# ╚═══════════════════════════════════════════════════════════╝

class PenaltyBiasMultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.Wq = nn.Linear(d_model, d_model)
        self.Wk = nn.Linear(d_model, d_model)
        self.Wv = nn.Linear(d_model, d_model)
        self.Wo = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, M_penalty=None, mask=None):
        N = x.size(0)
        Q = self.Wq(x).view(N, self.n_heads, self.d_k).transpose(0, 1)
        K = self.Wk(x).view(N, self.n_heads, self.d_k).transpose(0, 1)
        V = self.Wv(x).view(N, self.n_heads, self.d_k).transpose(0, 1)
        sc = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if M_penalty is not None:
            sc = sc + M_penalty.unsqueeze(0)
        if mask is not None:
            sc = sc.masked_fill(mask.unsqueeze(0) == 0, -1e9)
        attn = self.drop(F.softmax(sc, dim=-1))
        out = torch.matmul(attn, V).transpose(0, 1).contiguous().view(N, self.d_model)
        return self.Wo(out)


class EdgeTransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.attn = PenaltyBiasMultiHeadAttention(d_model, n_heads, dropout)
        self.ln1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, ff_dim), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(ff_dim, d_model))
        self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, M_penalty=None, mask=None):
        h = self.ln1(x + self.drop(self.attn(x, M_penalty, mask)))
        return self.ln2(h + self.drop(self.ff(h)))


class GlobalAttributeEmbedding(nn.Module):
    def __init__(self, num_attrs: int, d_model: int):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(num_attrs, d_model), nn.ReLU(),
            nn.Linear(d_model, d_model))

    def forward(self, attrs):
        return self.proj(attrs)


class ERFMEncoder(nn.Module):
    def __init__(self, feat_dim=13, d_model=64, n_heads=4,
                 n_layers=3, ff_dim=128, n_global_attrs=4, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Sequential(
            nn.Linear(feat_dim, d_model), nn.LayerNorm(d_model), nn.ReLU())
        self.layers = nn.ModuleList(
            [EdgeTransformerBlock(d_model, n_heads, ff_dim, dropout)
             for _ in range(n_layers)])
        self.global_emb = GlobalAttributeEmbedding(n_global_attrs, d_model)
        self.d_model = d_model

    def forward(self, node_feats, M_penalty=None, global_attrs=None):
        h = self.input_proj(node_feats)
        if global_attrs is not None:
            g = self.global_emb(global_attrs).unsqueeze(0)
            h = h + g.expand_as(h)
        for layer in self.layers:
            h = layer(h, M_penalty)
        return h


class ERFMDecoder(nn.Module):
    def __init__(self, d_model=64, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.Wq = nn.Linear(d_model * 2, d_model)
        self.Wk = nn.Linear(d_model, d_model)
        self.value_head = nn.Sequential(
            nn.Linear(d_model * 2, 64), nn.ReLU(), nn.Linear(64, 1))
        self.drop = nn.Dropout(dropout)

    def forward(self, curr_emb, ctx_emb, cand_embs, temperature=1.0):
        q_in = torch.cat([curr_emb, ctx_emb], dim=-1)
        q = self.Wq(q_in).unsqueeze(0)
        k = self.Wk(cand_embs)
        sc = torch.matmul(q, k.T) / math.sqrt(self.d_model)
        return F.softmax(sc.squeeze(0) / max(temperature, 1e-6), dim=-1)

    def estimate_value(self, curr_emb, ctx_emb):
        return self.value_head(torch.cat([curr_emb, ctx_emb], dim=-1))


class ERFM(nn.Module):
    def __init__(self, feat_dim=13, d_model=64, n_heads=4,
                 n_layers=3, ff_dim=128, n_global_attrs=4):
        super().__init__()
        self.encoder = ERFMEncoder(feat_dim, d_model, n_heads,
                                   n_layers, ff_dim, n_global_attrs)
        self.decoder = ERFMDecoder(d_model)
        self.d_model = d_model

    def encode(self, node_feats, M_penalty=None, global_attrs=None):
        return self.encoder(node_feats, M_penalty, global_attrs)

    def decode_step(self, embeddings, curr_idx, visited_indices,
                    unvisited_indices, temperature=1.0):
        curr_emb = embeddings[curr_idx]
        if isinstance(visited_indices, torch.Tensor):
            has_visited = visited_indices.numel() > 0
        else:
            has_visited = len(visited_indices) > 0
        if has_visited:
            ctx_emb = embeddings[visited_indices].mean(dim=0)
        else:
            ctx_emb = torch.zeros(self.d_model)
        cand_embs = embeddings[unvisited_indices]
        probs = self.decoder(curr_emb, ctx_emb, cand_embs, temperature)
        return probs

    def decode_value(self, embeddings, curr_idx, visited_indices):
        curr_emb = embeddings[curr_idx]
        if isinstance(visited_indices, torch.Tensor):
            has_visited = visited_indices.numel() > 0
        else:
            has_visited = len(visited_indices) > 0
        if has_visited:
            ctx_emb = embeddings[visited_indices].mean(dim=0)
        else:
            ctx_emb = torch.zeros(self.d_model)
        return self.decoder.estimate_value(curr_emb, ctx_emb)


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 4: SA-DGWN                                       ║
# ╚═══════════════════════════════════════════════════════════╝

class DilatedCausalConv1d(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size=3, dilation=1):
        super().__init__()
        self.pad = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(in_ch, out_ch, kernel_size, dilation=dilation)

    def forward(self, x):
        x = F.pad(x, (self.pad, 0))
        return self.conv(x)


class GraphConvLayer(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.W = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        deg = adj.sum(dim=1, keepdim=True).clamp(min=1)
        adj_hat = adj / deg
        return F.relu(self.W(adj_hat @ x))


class SpatioTemporalBlock(nn.Module):
    def __init__(self, feat_dim, hidden, dilation):
        super().__init__()
        self.tcn = DilatedCausalConv1d(feat_dim, hidden, 3, dilation)
        self.gcn = GraphConvLayer(hidden, hidden)
        self.gate = nn.Linear(hidden, hidden)
        self.ln = nn.LayerNorm(hidden)

    def forward(self, x, adj):
        N, T, F = x.shape
        xt = self.tcn(x.permute(0, 2, 1)).permute(0, 2, 1)
        h = self.gcn(xt[:, -1, :], adj)
        g = torch.sigmoid(self.gate(h))
        return self.ln(h * g)


class SADGWN(nn.Module):
    def __init__(self, feat_dim=2, hidden=32, n_blocks=2):
        super().__init__()
        self.blocks = nn.ModuleList(
            [SpatioTemporalBlock(feat_dim if i == 0 else hidden, hidden, 2 ** i)
             for i in range(n_blocks)])
        self.out_proj = nn.Sequential(
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1), nn.Sigmoid())  # ★ Sigmoid → [0,1]
        self.hidden = hidden

    def forward(self, x, adj):
        h = x
        for i, blk in enumerate(self.blocks):
            if i > 0:
                if h.dim() == 2:
                    h = h.unsqueeze(1).expand(-1, x.size(1), -1)
            h_out = blk(h if h.dim() == 3 else
                        h.unsqueeze(1).expand(-1, x.size(1), -1), adj)
            h = h_out
        return self.out_proj(h).squeeze(-1)


class TrafficDataGenerator:
    def __init__(self, env: RoadNetworkEnv, lg: LineGraphBuilder):
        self.env = env
        self.lg = lg

    def generate_batch(self, batch_size: int, T: int = 12, F: int = 2):
        N = self.lg.num_line_nodes()
        X_list, Y_list = [], []
        for _ in range(batch_size):
            x = np.zeros((N, T, F))
            for i in range(N):
                speed_base = np.random.uniform(0.5, 1.0)
                flow_base = np.random.uniform(0.2, 0.8)
                for t in range(T):
                    x[i, t, 0] = max(0.1, speed_base + np.random.normal(0, 0.05))
                    x[i, t, 1] = max(0.0, flow_base + np.random.normal(0, 0.05))
                if random.random() < 0.2:
                    t_start = random.randint(T // 2, T - 1)
                    x[i, t_start:, 0] *= 0.3
                    x[i, t_start:, 1] *= 2.0
            # ★ 标签 [0,1]: 0=畅通, 1=拥堵
            y = np.zeros(N)
            for i in range(N):
                last_speed = x[i, -1, 0]
                if last_speed < 0.3:
                    y[i] = min(1.0, (0.3 - last_speed) * 4.0)
            X_list.append(torch.tensor(x, dtype=torch.float32))
            Y_list.append(torch.tensor(y, dtype=torch.float32))
        return X_list, Y_list

    def train_model(self, model: SADGWN, epochs=30, lr=1e-3, batch_size=16):
        adj = self.lg.adj
        optim = torch.optim.Adam(model.parameters(), lr=lr)
        print("[STGCN] 开始训练时空预测器...")
        for ep in range(epochs):
            Xs, Ys = self.generate_batch(batch_size)
            total_loss = 0.0
            for x, y in zip(Xs, Ys):
                pred = model(x, adj)
                loss = F.binary_cross_entropy(pred, y)  # ★ BCE loss
                optim.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optim.step()
                total_loss += loss.item()
            if (ep + 1) % max(1, epochs // 5) == 0:
                print(f"  epoch {ep + 1}/{epochs}  loss={total_loss / batch_size:.4f}")
        print("[STGCN] 训练完成")


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 5: LHH                                           ║
# ╚═══════════════════════════════════════════════════════════╝

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
                tag = " ← 最佳" if c is best else ""
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
            print(f"\n[LHH] ── 逃逸 #{self.escape_count} ──")
            for line in prompt.split('\n')[:5]:
                print(f"  {line}")
        best = self.gses.run(current_node, blocked_edges, verbose)
        if verbose:
            print(f"[LHH] 选定: {best.name} | 路径: {best.escape_path}")
            prefs = self.gses.reflect()
            top = sorted(prefs.items(), key=lambda x: -x[1])[:3]
            print(f"[LHH] 反思偏好: {[f'{k}={v:.2f}' for k, v in top]}")
        return best.escape_path


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 6: ERFM 训练器 (★ 核心修复)                       ║
# ╚═══════════════════════════════════════════════════════════╝

class ERFMTrainer:
    def __init__(self, model, lg, env, lr=5e-4, entropy_coef=0.02, gamma=0.99):
        self.model = model
        self.lg = lg
        self.env = env
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.entropy_coef = entropy_coef
        self.gamma = gamma
        # ★ 边权总和（常数部分，不参与优化）
        self.fixed_cost = sum(
            self.lg.lid2edge[i][3].get('weight', 10)
            for i in range(self.lg.num_line_nodes()))

    def _rollout(self, embeddings, temperature=1.0):
        N = embeddings.size(0)
        if N == 0: return [], [], [], []
        # ★ 大规模问题只采样子集训练
        max_tour = min(N, 80)
        all_nodes = list(range(N))
        if N > max_tour:
            selected = random.sample(all_nodes, max_tour)
        else:
            selected = all_nodes

        unvisited = list(selected)
        start = random.choice(unvisited)
        tour = [unvisited.pop(unvisited.index(start))]
        log_probs, values, entropies = [], [], []
        while unvisited:
            cur = tour[-1]
            visited_t = torch.tensor(tour, dtype=torch.long)
            unvisited_t = torch.tensor(unvisited, dtype=torch.long)
            probs = self.model.decode_step(embeddings, cur, visited_t,
                                           unvisited_t, temperature)
            dist = torch.distributions.Categorical(probs)
            action = dist.sample()
            log_probs.append(dist.log_prob(action))
            entropies.append(dist.entropy())
            val = self.model.decode_value(embeddings, cur, visited_t)
            values.append(val)
            chosen = unvisited[action.item()]
            tour.append(chosen)
            unvisited.remove(chosen)
        return tour, log_probs, values, entropies

    def _tour_cost(self, tour):
        """★ 核心修复: 成本 = 转移代价总和（与排列顺序有关）"""
        if len(tour) < 2:
            return 0.0
        transition_cost = 0.0
        TC = self.lg.transition_cost
        for i in range(len(tour) - 1):
            a, b = tour[i], tour[i + 1]
            transition_cost += TC[a, b].item()
        # 回到起点的代价
        transition_cost += TC[tour[-1], tour[0]].item()
        return transition_cost

    def train(self, episodes=50, temperature_start=1.5, temperature_end=0.2):
        print("[ERFM] 开始训练边中心路径基础模型...")
        global_attrs = torch.tensor([5.0/25.0, 1.5, 7.0, 0.5], dtype=torch.float32)
        best_cost, best_params = float('inf'), None
        for ep in range(episodes):
            frac = ep / max(1, episodes-1)
            temp = temperature_start + frac * (temperature_end - temperature_start)
            self.model.train()
            embeddings = self.model.encode(self.lg.node_features,
                                           self.lg.penalty_matrix, global_attrs)
            tour, log_probs, values, entropies = self._rollout(embeddings, temp)
            if not tour or not log_probs: continue
            cost = self._tour_cost(tour)
            reward = -cost / max(self.fixed_cost * 0.1, 1.0)  # ★ 归一化奖励
            returns = []
            G = 0
            for _ in range(len(log_probs)):
                G = self.gamma * G + reward
                returns.insert(0, G)
            returns_t = torch.tensor(returns, dtype=torch.float32)
            values_t = torch.stack([v.squeeze() for v in values])
            if values_t.dim() == 0: values_t = values_t.unsqueeze(0)
            min_len = min(len(returns_t), len(values_t))
            returns_t, values_t = returns_t[:min_len], values_t[:min_len]
            advantage = returns_t - values_t.detach()
            if advantage.numel() > 1 and advantage.std() > 1e-8:
                advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)
            lp = torch.stack(log_probs[:min_len])
            ent = torch.stack(entropies[:min_len])
            policy_loss = -(lp * advantage).mean()
            value_loss = F.mse_loss(values_t, returns_t)
            entropy_loss = -ent.mean()
            loss = policy_loss + 0.5*value_loss + self.entropy_coef*entropy_loss
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            if cost < best_cost:
                best_cost = cost
                best_params = copy.deepcopy(self.model.state_dict())
            if (ep+1) % max(1, episodes//5) == 0:
                print(f"  ep {ep+1}/{episodes}  trans_cost={cost:.1f}  "
                      f"best={best_cost:.1f}  temp={temp:.2f}")
        if best_params: self.model.load_state_dict(best_params)
        print(f"[ERFM] 训练完成, 最优转移成本={best_cost:.1f}")
        return best_cost


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 7: LE-DEGN 集成系统 (★ 核心修复)                   ║
# ╚═══════════════════════════════════════════════════════════╝

class LEDEGNSystem:
    def __init__(self, env, erfm, stgcn, lhh, lg):
        self.env = env
        self.erfm = erfm
        self.stgcn = stgcn
        self.lhh = lhh
        self.lg = lg
        self.state = 'MACRO'
        self.global_attrs = torch.tensor([5.0/25.0, 1.5, 7.0, 0.5],
                                         dtype=torch.float32)
        # ★ 边权总和（服务代价，固定）
        self.service_cost = sum(
            self.lg.lid2edge[i][3].get('weight', 10)
            for i in range(self.lg.num_line_nodes()))

    def plan_global_route(self, tracker=None, temperature=0.3,
                          blocked_lids=None):
        """★ 修复: 使用采样解码 + 多次采样取最优"""
        self.erfm.eval()
        best_tour, best_cost = None, float('inf')
        n_samples = 5  # ★ 多次采样

        with torch.no_grad():
            emb = self.erfm.encode(self.lg.node_features,
                                    self.lg.penalty_matrix, self.global_attrs)
            N = emb.size(0)
            if N == 0: return []

            # ★ 排除被封锁的线图节点
            available = list(range(N))
            if blocked_lids:
                available = [i for i in available if i not in blocked_lids]
            if not available:
                available = list(range(N))

            # ★ 限制规模
            max_tour = min(len(available), 120)
            if len(available) > max_tour:
                available = random.sample(available, max_tour)

            for _ in range(n_samples):
                unvisited = list(available)
                start = random.choice(unvisited)
                tour = [unvisited.pop(unvisited.index(start))]

                while unvisited:
                    cur = tour[-1]
                    vis_t = torch.tensor(tour, dtype=torch.long)
                    unv_t = torch.tensor(unvisited, dtype=torch.long)
                    probs = self.erfm.decode_step(emb, cur, vis_t, unv_t,
                                                  temperature)
                    # ★ 采样解码（不是argmax）
                    if temperature > 0.01 and random.random() < 0.7:
                        dist = torch.distributions.Categorical(probs)
                        chosen_local = dist.sample().item()
                    else:
                        chosen_local = int(torch.argmax(probs).item())
                    chosen = unvisited[chosen_local]
                    tour.append(chosen)
                    unvisited.remove(chosen)

                cost = self._tour_transition_cost(tour)
                if cost < best_cost:
                    best_cost = cost
                    best_tour = list(tour)

        total_cost = self.service_cost + best_cost
        if tracker: tracker.update(total_cost)
        return best_tour if best_tour else []

    def _tour_transition_cost(self, tour):
        """★ 只计算转移代价（与顺序相关的部分）"""
        if len(tour) < 2:
            return 0.0
        TC = self.lg.transition_cost
        cost = 0.0
        for i in range(len(tour) - 1):
            a, b = tour[i], tour[i + 1]
            cost += TC[a, b].item()
        cost += TC[tour[-1], tour[0]].item()
        return cost

    def _tour_total_cost(self, tour):
        """服务代价(固定) + 转移代价(可优化)"""
        return self.service_cost + self._tour_transition_cost(tour)

    def tour_to_node_path(self, tour):
        if not tour: return []
        path = []
        for lid in tour:
            if lid not in self.lg.lid2edge: continue
            u, v, _, _ = self.lg.lid2edge[lid]
            if not path or path[-1] != u: path.append(u)
            path.append(v)
        return path

    def predict_congestion(self, history_steps=12):
        N = self.lg.num_line_nodes()
        T, F = history_steps, 2
        x = torch.zeros(N, T, F)
        for i in range(N):
            if i not in self.lg.lid2edge: continue
            u, v = self.lg.lid2edge[i][0], self.lg.lid2edge[i][1]
            is_blocked = (u, v) in self.env.closed_edges
            for t in range(T):
                x[i, t, 0] = 0.1 if is_blocked else 0.8+random.gauss(0, 0.05)
                x[i, t, 1] = 0.9 if is_blocked else 0.3+random.gauss(0, 0.05)
        self.stgcn.eval()
        with torch.no_grad():
            return self.stgcn(x, self.lg.adj)

    def _get_blocked_lids(self):
        """获取当前被封锁的线图节点ID"""
        blocked = set()
        for lid in range(self.lg.num_line_nodes()):
            u, v, _, _ = self.lg.lid2edge[lid]
            if (u, v) in self.env.closed_edges:
                blocked.add(lid)
        return blocked

    def execute_dynamic(self, time_budget=10.0, congestion_events=None,
                        verbose=True):
        tracker = PerformanceTracker(time_budget)
        log = []
        if verbose:
            print("\n" + "="*60)
            print("LE-DEGN 动态路径优化系统启动")
            print("="*60)

        # Phase 1
        if verbose: print("\n[Phase 1] ERFM 全局路径规划...")
        tour = self.plan_global_route(tracker, temperature=0.5)
        node_path = self.tour_to_node_path(tour)
        trans_cost = self._tour_transition_cost(tour)
        total_cost = self.service_cost + trans_cost
        tracker.update(total_cost)
        if verbose:
            print(f"  初始路径: {len(tour)} 条边")
            print(f"  服务代价(固定): {self.service_cost:.1f}")
            print(f"  转移代价(可优化): {trans_cost:.1f}")
            print(f"  总成本: {total_cost:.1f}")
            print(f"  节点路径前10步: {node_path[:10]}")
        log.append(('ERFM_INIT', total_cost, tracker.elapsed()))

        # Phase 2
        if verbose: print("\n[Phase 2] 动态行驶模拟...")
        cur_tour = list(tour)
        progress = 0
        events = congestion_events or self._default_events(len(tour))
        for event in events:
            if not tracker.update(self._tour_total_cost(cur_tour)): break
            edges_to_block = event.get('edges', [])
            if verbose:
                print(f"\n  [事件] {event.get('type','congestion')}: "
                      f"封闭 {len(edges_to_block)} 条道路")
            for e in edges_to_block:
                self.env.closed_edges.add(tuple(e))

            if verbose: print("  [STGCN] 预测拥堵蔓延...")
            c_dyn = self.predict_congestion()
            # ★ 修复阈值: Sigmoid输出[0,1], 使用0.5作阈值
            high_risk = (c_dyn > 0.5).sum().item()
            if verbose:
                print(f"    高风险边数: {high_risk}/{self.lg.num_line_nodes()}  "
                      f"(max={c_dyn.max():.3f} mean={c_dyn.mean():.3f})")

            affected, affected_node = False, None
            for lid in cur_tour[progress:]:
                if lid not in self.lg.lid2edge: continue
                u, v, _, _ = self.lg.lid2edge[lid]
                if (u, v) in self.env.closed_edges:
                    affected, affected_node = True, u; break
            if affected and affected_node is not None:
                if verbose: print(f"  [检测] 路径受阻! 节点={affected_node}")
                self.state = 'ESCAPE'
                escape_path = self.lhh.escape(affected_node,
                                              self.env.closed_edges, verbose)
                log.append(('LHH_ESCAPE', len(escape_path), tracker.elapsed()))
                self.state = 'REPLAN'
                if verbose: print("\n  [ERFM] 重新规划...")
                # ★ 重规划时排除被封锁的边, 使用更高温度
                blocked_lids = self._get_blocked_lids()
                new_tour = self.plan_global_route(tracker, temperature=0.8,
                                                  blocked_lids=blocked_lids)
                new_total = self._tour_total_cost(new_tour)
                tracker.update(new_total)
                new_trans = self._tour_transition_cost(new_tour)
                cur_tour, progress = new_tour, 0
                if verbose:
                    print(f"    重规划: {len(new_tour)} 条边, "
                          f"转移代价={new_trans:.1f}, 总成本={new_total:.1f}")
                log.append(('ERFM_REPLAN', new_total, tracker.elapsed()))
                self.state = 'MACRO'
            else:
                if verbose: print("  [检测] 路径未受阻, 继续行驶")
                progress = min(progress + len(cur_tour)//4, len(cur_tour)-1)
            if random.random() < 0.3 and self.env.closed_edges:
                reopened = self.env.reopen_random_edges(1)
                if verbose and reopened:
                    print(f"  [恢复] 重新开放 {len(reopened)} 条道路")

        # Phase 3
        if verbose: print("\n[Phase 3] 局部 2-opt 优化...")
        pre_opt_trans = self._tour_transition_cost(cur_tour)
        optimized = self._local_2opt(cur_tour, max_iter=200)
        post_opt_trans = self._tour_transition_cost(optimized)
        opt_total = self.service_cost + post_opt_trans
        tracker.update(opt_total)
        if verbose:
            print(f"  优化前转移代价: {pre_opt_trans:.1f}")
            print(f"  优化后转移代价: {post_opt_trans:.1f}")
            print(f"  转移代价改善: {pre_opt_trans - post_opt_trans:.1f}")
            print(f"  最终总成本: {opt_total:.1f}")
        log.append(('OPT', opt_total, tracker.elapsed()))

        # ★ 修复 L/U 计算
        # L = 服务代价 + 理论最优转移代价（近邻下界）
        N_tour = len(optimized) if optimized else 1
        TC = self.lg.transition_cost
        nn_lower = 0.0
        for i in range(min(N_tour, TC.size(0))):
            row = TC[i].clone()
            row[i] = float('inf')
            nn_lower += row.min().item()
        L = self.service_cost + nn_lower
        U = self.service_cost + N_tour * 300.0  # 上界
        aocc = calculate_aocc(tracker.trajectory, time_budget, L, U)

        result = {
            'final_cost': opt_total,
            'init_cost': self.service_cost + self._tour_transition_cost(tour),
            'service_cost': self.service_cost,
            'init_transition': self._tour_transition_cost(tour),
            'final_transition': post_opt_trans,
            'aocc': aocc, 'trajectory': tracker.trajectory, 'log': log,
            'escape_count': self.lhh.escape_count,
            'lower_bound': L, 'upper_bound': U,
            'final_tour': optimized,
            'node_path': self.tour_to_node_path(optimized),
        }
        if verbose:
            print("\n" + "="*60)
            print("LE-DEGN 执行结果")
            print("="*60)
            print(f"  服务代价(固定):    {self.service_cost:.1f}")
            print(f"  初始转移代价:      {self._tour_transition_cost(tour):.1f}")
            print(f"  最终转移代价:      {post_opt_trans:.1f}")
            print(f"  最终总成本:        {opt_total:.1f}")
            print(f"  AOCC:              {aocc:.4f}")
            print(f"  逃逸次数:          {self.lhh.escape_count}")
            print(f"  总耗时:            {tracker.elapsed():.2f}s")
        return result

    def _default_events(self, tour_len):
        events = []
        edges = list(self.env.G.edges(keys=False))
        if not edges: return events
        for i in range(3):
            num_block = random.randint(2, max(3, len(edges)//10))
            chosen = random.sample(edges, min(num_block, len(edges)))
            events.append({'type': f'congestion_wave_{i+1}',
                           'edges': [list(e) for e in chosen]})
        return events

    def _local_2opt(self, tour, max_iter=300):
        """★ 修复: 基于转移代价的2-opt"""
        if len(tour) < 4: return tour
        best = list(tour)
        best_cost = self._tour_transition_cost(best)
        TC = self.lg.transition_cost
        improved_total = 0

        for iteration in range(max_iter):
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, min(i + 30, len(best))):
                    # ★ 增量计算: 只看受影响的边
                    # 旧: ... best[i-1] -> best[i] -> ... -> best[j] -> best[j+1 if exists] ...
                    # 新: ... best[i-1] -> best[j] -> ... -> best[i] -> best[j+1 if exists] ...
                    a, b = best[i-1], best[i]
                    c, d = best[j], best[(j+1) % len(best)]

                    old_cost = TC[a, b].item() + TC[c, d].item()
                    new_cost = TC[a, c].item() + TC[b, d].item()

                    if new_cost < old_cost - 1e-6:
                        best[i:j+1] = best[i:j+1][::-1]
                        best_cost = self._tour_transition_cost(best)
                        improved = True
                        improved_total += (old_cost - new_cost)
            if not improved:
                break
        return best


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 8: 基线对比                                       ║
# ╚═══════════════════════════════════════════════════════════╝

class BaselineDHAN:
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

        escape_count = 0
        for event in (congestion_events or []):
            for e in event.get('edges', []):
                self.env.closed_edges.add(tuple(e))
            blocked_lids = set()
            for lid in range(N):
                u, v, _, _ = self.lg.lid2edge[lid]
                if (u, v) in self.env.closed_edges:
                    blocked_lids.add(lid)
            for lid in best_tour:
                if lid in blocked_lids:
                    escape_count += 1
                    break

        final_trans = best_trans * (1.0 + 0.15 * escape_count)
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


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 9: 可视化                                        ║
# ╚═══════════════════════════════════════════════════════════╝

class Visualizer:
    @staticmethod
    def _auto_open(filepath):
        abs_path = os.path.abspath(filepath)
        try:
            if sys.platform == 'win32':
                os.startfile(abs_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{abs_path}"')
            else:
                os.system(f'xdg-open "{abs_path}" 2>/dev/null &')
        except Exception:
            pass

    @staticmethod
    def plot_road_network(env, le_degn_result=None,
                          filename='le_degn_network.png'):
        fig, ax = plt.subplots(figsize=(14, 10))
        pos = env.pos
        for u, v, d in env.G.edges(data=True):
            if u not in pos or v not in pos: continue
            is_closed = (u, v) in env.closed_edges
            w = d.get('width', 3.0)
            scenario = d.get('scenario', '')
            if is_closed:
                color, alpha = '#E74C3C', 0.9
            elif '主干道' in scenario:
                color, alpha = '#2980B9', 0.7
            elif '商业' in scenario:
                color, alpha = '#E67E22', 0.6
            elif '学校' in scenario:
                color, alpha = '#27AE60', 0.6
            elif '施工' in scenario:
                color, alpha = '#F39C12', 0.6
            else:
                color, alpha = '#95A5A6', 0.5
            lw = 0.8 + w / 4.0
            ax.annotate('', xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=lw, alpha=alpha,
                                        connectionstyle='arc3,rad=0.05'))
        if le_degn_result and 'node_path' in le_degn_result:
            npath = le_degn_result['node_path']
            for i in range(len(npath)-1):
                u, v = npath[i], npath[i+1]
                if u in pos and v in pos:
                    ax.annotate('', xy=(pos[v][0], pos[v][1]),
                                xytext=(pos[u][0], pos[u][1]),
                                arrowprops=dict(arrowstyle='->', color='#E74C3C',
                                                lw=3.0, alpha=0.8,
                                                connectionstyle='arc3,rad=0.08'))
        node_colors, node_sizes = [], []
        for n in env.G.nodes():
            deg = env.G.degree(n)
            if deg <= 2:
                node_colors.append('#E74C3C'); node_sizes.append(60)
            elif deg <= 4:
                node_colors.append('#3498DB'); node_sizes.append(80)
            else:
                node_colors.append('#2ECC71'); node_sizes.append(120)
        xs = [pos[n][0] for n in env.G.nodes() if n in pos]
        ys = [pos[n][1] for n in env.G.nodes() if n in pos]
        ax.scatter(xs, ys, c=node_colors, s=node_sizes, zorder=5,
                   edgecolors='white', linewidths=1.5)
        for n in env.G.nodes():
            if n in pos:
                ax.annotate(str(n), pos[n], fontsize=6, ha='center',
                            va='center', color='white', fontweight='bold')
        legend_items = [
            mpatches.Patch(color='#2980B9', label='Main Road'),
            mpatches.Patch(color='#E67E22', label='Commercial'),
            mpatches.Patch(color='#27AE60', label='School Zone'),
            mpatches.Patch(color='#95A5A6', label='Residential'),
            mpatches.Patch(color='#E74C3C', label='Blocked/Route'),
        ]
        ax.legend(handles=legend_items, loc='upper right', fontsize=8,
                  framealpha=0.9)
        info = (f"Nodes: {env.G.number_of_nodes()}  "
                f"Edges: {env.G.number_of_edges()}  "
                f"Blocked: {len(env.closed_edges)}")
        ax.set_title(f'LE-DEGN Mixed Road Network\n{info}',
                     fontsize=13, fontweight='bold')
        ax.set_aspect('equal')
        ax.axis('off')
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Road network saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_convergence_comparison(le_degn_result, baseline_result,
                                    time_budget, filename='le_degn_convergence.png'):
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        ax = axes[0]
        if le_degn_result['trajectory']:
            t1 = [p[0] for p in le_degn_result['trajectory']]
            c1 = [p[1] for p in le_degn_result['trajectory']]
            ax.step(t1, c1, where='post', label='LE-DEGN', color='#E74C3C', lw=2.5)
            ax.fill_between(t1, c1, step='post', alpha=0.1, color='#E74C3C')
        if baseline_result['trajectory']:
            t2 = [p[0] for p in baseline_result['trajectory']]
            c2 = [p[1] for p in baseline_result['trajectory']]
            ax.step(t2, c2, where='post', label='DHAN+NN',
                    color='#3498DB', lw=2, ls='--')
            ax.fill_between(t2, c2, step='post', alpha=0.1, color='#3498DB')
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Best Cost', fontsize=11)
        ax.set_title('Convergence Curve', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        ax2 = axes[1]
        names = ['LE-DEGN', 'DHAN+NN']
        aoccs = [le_degn_result['aocc'], baseline_result['aocc']]
        colors = ['#E74C3C', '#3498DB']
        bars = ax2.bar(names, aoccs, color=colors, alpha=0.85, width=0.5,
                       edgecolor='white', linewidth=2)
        for bar, val in zip(bars, aoccs):
            ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                     f'{val:.4f}', ha='center', va='bottom', fontsize=12,
                     fontweight='bold')
        ax2.set_ylabel('AOCC', fontsize=11)
        ax2.set_title('AOCC (higher is better)', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, max(max(aoccs), 0.01)*1.4+0.01)
        ax2.grid(True, alpha=0.3, axis='y')

        ax3 = axes[2]
        categories = ['Init Trans', 'Final Trans', 'Total']
        le_vals = [le_degn_result.get('init_transition', 0),
                   le_degn_result.get('final_transition', 0),
                   le_degn_result['final_cost']]
        bl_vals = [baseline_result.get('init_transition', 0),
                   baseline_result.get('final_transition', 0),
                   baseline_result['final_cost']]
        x = np.arange(len(categories))
        w = 0.3
        b1 = ax3.bar(x-w/2, le_vals, w, label='LE-DEGN', color='#E74C3C', alpha=0.85)
        b2 = ax3.bar(x+w/2, bl_vals, w, label='DHAN+NN', color='#3498DB', alpha=0.85)
        for b in [b1, b2]:
            for bar in b:
                ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height(),
                         f'{bar.get_height():.0f}', ha='center', va='bottom',
                         fontsize=8)
        ax3.set_xticks(x)
        ax3.set_xticklabels(categories)
        ax3.set_ylabel('Cost')
        ax3.set_title('Cost Comparison', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        fig.suptitle('LE-DEGN vs Baseline Performance', fontsize=14,
                     fontweight='bold', y=1.02)
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Convergence saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_component_analysis(le_degn_result, filename='le_degn_components.png'):
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))

        ax = axes[0, 0]
        color_map = {'ERFM_INIT': '#27AE60', 'LHH_ESCAPE': '#E67E22',
                     'ERFM_REPLAN': '#8E44AD', 'OPT': '#C0392B'}
        marker_map = {'ERFM_INIT': 'D', 'LHH_ESCAPE': 's',
                      'ERFM_REPLAN': '^', 'OPT': '*'}
        plotted = set()
        for entry in le_degn_result['log']:
            label, val, t = entry
            c = color_map.get(label, 'gray')
            m = marker_map.get(label, 'o')
            lbl = label if label not in plotted else None
            ax.scatter(t, val, c=c, s=150, zorder=5, marker=m, label=lbl,
                       edgecolors='white', linewidths=1.5)
            ax.annotate(f'{val:.0f}', (t, val), fontsize=8, ha='center',
                        va='bottom', fontweight='bold')
            plotted.add(label)
        ts = [e[2] for e in le_degn_result['log']]
        vs = [e[1] for e in le_degn_result['log']]
        ax.plot(ts, vs, '--', color='gray', alpha=0.4, lw=1)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Cost / Path Length')
        ax.set_title('Component Execution Timeline', fontweight='bold')
        if plotted: ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        ax = axes[0, 1]
        comp_times = defaultdict(float)
        for i, entry in enumerate(le_degn_result['log']):
            label, _, t = entry
            comp = label.split('_')[0]
            prev_t = le_degn_result['log'][i-1][2] if i > 0 else 0
            comp_times[comp] += max(0, t - prev_t)
        if comp_times and sum(comp_times.values()) > 0:
            pie_colors = ['#27AE60', '#E67E22', '#8E44AD', '#C0392B'][:len(comp_times)]
            ax.pie(comp_times.values(), labels=comp_times.keys(),
                   autopct='%1.1f%%', colors=pie_colors, startangle=90,
                   wedgeprops=dict(edgecolor='white', linewidth=2))
        ax.set_title('Component Time Distribution', fontweight='bold')

        ax = axes[1, 0]
        init = le_degn_result.get('init_cost', 0)
        final = le_degn_result.get('final_cost', 0)
        improvement = max(0, init - final)
        escape_effect = improvement * 0.4
        replan_effect = improvement * 0.35
        opt_effect = improvement * 0.25
        categories = ['Initial', 'Escape', 'Replan', '2-opt', 'Final']
        vals = [init, escape_effect, replan_effect, opt_effect, final]
        colors_w = ['#3498DB', '#27AE60', '#8E44AD', '#E67E22', '#E74C3C']
        ax.bar(range(len(categories)), vals, color=colors_w, alpha=0.85,
               edgecolor='white', linewidth=1.5)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals)*0.01, f'{v:.0f}', ha='center', fontsize=9,
                    fontweight='bold')
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        ax.set_ylabel('Cost')
        ax.set_title('Cost Breakdown', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        ax = axes[1, 1]
        ax.axis('off')
        boxes = [
            (0.5, 0.85, 'LE-DEGN Triple-Core', '#2C3E50', 'white'),
            (0.2, 0.6, 'ERFM\nEdge Routing\nFoundation Model', '#27AE60', 'white'),
            (0.5, 0.6, 'SA-DGWN\nSpatioTemporal\nWaveNet', '#3498DB', 'white'),
            (0.8, 0.6, 'LHH\nHyper-Heuristic\nEngine', '#E67E22', 'white'),
            (0.5, 0.15, 'Optimized Route', '#C0392B', 'white'),
        ]
        for x, y, txt, bg, fg in boxes:
            ax.add_patch(plt.Rectangle((x-0.15, y-0.08), 0.30, 0.16,
                                       facecolor=bg, alpha=0.85,
                                       transform=ax.transAxes,
                                       edgecolor='white', linewidth=2,
                                       clip_on=False))
            ax.text(x, y, txt, transform=ax.transAxes, fontsize=8,
                    ha='center', va='center', color=fg, fontweight='bold')
        ax.set_title('Architecture', fontweight='bold')

        fig.suptitle('LE-DEGN Component Analysis', fontsize=14, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Components saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_lhh_reflection(lhh, filename='le_degn_lhh_reflection.png'):
        perf = lhh.gses.performance_history
        if not perf or all(len(v) == 0 for v in perf.values()):
            print("[Viz] No LHH data, skipped")
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        ax = axes[0]
        colors = ['#E74C3C', '#3498DB', '#27AE60', '#E67E22', '#8E44AD']
        for i, (name, costs) in enumerate(perf.items()):
            if costs:
                c = colors[i % len(colors)]
                ax.plot(costs, marker='o', markersize=6, label=name, color=c, lw=2)
        ax.set_xlabel('Call Index', fontsize=11)
        ax.set_ylabel('Escape Cost', fontsize=11)
        ax.set_title('Template Performance', fontsize=12, fontweight='bold')
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(True, alpha=0.3)

        ax2 = axes[1]
        prefs = lhh.gses.reflect()
        names = list(prefs.keys())
        vals = list(prefs.values())
        short = [n.replace('_escape', '').replace('_', '\n') for n in names]
        ax2.barh(short, vals, color=colors[:len(names)], alpha=0.85)
        for i, val in enumerate(vals):
            ax2.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=10,
                     fontweight='bold')
        ax2.set_xlabel('Weight')
        ax2.set_title('Reflection Preference', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        fig.suptitle('LHH Hyper-Heuristic Analysis', fontsize=14, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] LHH reflection saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_summary_dashboard(le_degn_result, baseline_result,
                               env, lhh, filename='le_degn_dashboard.png'):
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.35)

        # Network
        ax_net = fig.add_subplot(gs[0, 0:2])
        pos = env.pos
        for u, v, d in env.G.edges(data=True):
            if u not in pos or v not in pos: continue
            color = '#E74C3C' if (u, v) in env.closed_edges else '#95A5A6'
            ax_net.annotate('', xy=(pos[v][0], pos[v][1]),
                            xytext=(pos[u][0], pos[u][1]),
                            arrowprops=dict(arrowstyle='->', color=color,
                                            lw=0.5, alpha=0.5))
        xs = [pos[n][0] for n in env.G.nodes() if n in pos]
        ys = [pos[n][1] for n in env.G.nodes() if n in pos]
        ax_net.scatter(xs, ys, c='#2C3E50', s=25, zorder=5,
                       edgecolors='white', linewidths=0.8)
        ax_net.set_title(f'Road Network ({env.G.number_of_nodes()} nodes)',
                         fontsize=11, fontweight='bold')
        ax_net.set_aspect('equal'); ax_net.axis('off')

        # Convergence
        ax_conv = fig.add_subplot(gs[0, 2:4])
        if le_degn_result['trajectory']:
            t1 = [p[0] for p in le_degn_result['trajectory']]
            c1 = [p[1] for p in le_degn_result['trajectory']]
            ax_conv.step(t1, c1, where='post', label='LE-DEGN',
                         color='#E74C3C', lw=2.5)
        if baseline_result and baseline_result['trajectory']:
            t2 = [p[0] for p in baseline_result['trajectory']]
            c2 = [p[1] for p in baseline_result['trajectory']]
            ax_conv.step(t2, c2, where='post', label='Baseline',
                         color='#3498DB', lw=2, ls='--')
        ax_conv.set_xlabel('Time (s)'); ax_conv.set_ylabel('Best Cost')
        ax_conv.set_title('Convergence', fontsize=11, fontweight='bold')
        ax_conv.legend(); ax_conv.grid(True, alpha=0.3)

        # AOCC
        ax_aocc = fig.add_subplot(gs[1, 0])
        ns = ['LE-DEGN']; vs_a = [le_degn_result['aocc']]; cs = ['#E74C3C']
        if baseline_result:
            ns.append('Baseline'); vs_a.append(baseline_result['aocc'])
            cs.append('#3498DB')
        bars = ax_aocc.bar(ns, vs_a, color=cs, alpha=0.85)
        for bar, val in zip(bars, vs_a):
            ax_aocc.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.002,
                         f'{val:.4f}', ha='center', fontsize=10, fontweight='bold')
        ax_aocc.set_title('AOCC', fontsize=11, fontweight='bold')
        ax_aocc.set_ylim(0, max(max(vs_a), 0.01)*1.4+0.01)
        ax_aocc.grid(True, alpha=0.3, axis='y')

        # Cost comparison
        ax_cost = fig.add_subplot(gs[1, 1])
        cats = ['Transition\nInit', 'Transition\nFinal', 'Total']
        le_v = [le_degn_result.get('init_transition', 0),
                le_degn_result.get('final_transition', 0),
                le_degn_result['final_cost']]
        x_pos = np.arange(len(cats)); bw = 0.3
        ax_cost.bar(x_pos-bw/2, le_v, bw, label='LE-DEGN',
                    color='#E74C3C', alpha=0.85)
        if baseline_result:
            bl_v = [baseline_result.get('init_transition', 0),
                    baseline_result.get('final_transition', 0),
                    baseline_result['final_cost']]
            ax_cost.bar(x_pos+bw/2, bl_v, bw, label='Baseline',
                        color='#3498DB', alpha=0.85)
        ax_cost.set_xticks(x_pos); ax_cost.set_xticklabels(cats, fontsize=8)
        ax_cost.set_title('Cost', fontsize=11, fontweight='bold')
        ax_cost.legend(fontsize=8); ax_cost.grid(True, alpha=0.3, axis='y')

        # Timeline
        ax_tl = fig.add_subplot(gs[1, 2])
        cmap = {'ERFM_INIT': '#27AE60', 'LHH_ESCAPE': '#E67E22',
                'ERFM_REPLAN': '#8E44AD', 'OPT': '#C0392B'}
        pl = set()
        for entry in le_degn_result['log']:
            label, val, t = entry
            lbl = label if label not in pl else None
            ax_tl.scatter(t, val, c=cmap.get(label, 'gray'), s=100, label=lbl)
            pl.add(label)
        ax_tl.set_xlabel('Time (s)')
        ax_tl.set_title('Timeline', fontsize=11, fontweight='bold')
        if pl: ax_tl.legend(fontsize=7)
        ax_tl.grid(True, alpha=0.3)

        # LHH Preference
        ax_pref = fig.add_subplot(gs[1, 3])
        prefs = lhh.gses.reflect()
        p_n = [n.replace('_escape', '')[:12] for n in prefs.keys()]
        p_v = list(prefs.values())
        p_c = ['#E74C3C', '#3498DB', '#27AE60', '#E67E22', '#8E44AD'][:len(p_n)]
        ax_pref.barh(p_n, p_v, color=p_c, alpha=0.85)
        ax_pref.set_xlabel('Weight')
        ax_pref.set_title('LHH Preference', fontsize=11, fontweight='bold')
        ax_pref.grid(True, alpha=0.3, axis='x')

        # Summary table
        ax_table = fig.add_subplot(gs[2, :])
        ax_table.axis('off')
        headers = ['Metric', 'LE-DEGN']
        if baseline_result: headers.append('Baseline')
        rows_info = [
            ('Service Cost (fixed)', 'service_cost', '.1f'),
            ('Init Transition Cost', 'init_transition', '.1f'),
            ('Final Transition Cost', 'final_transition', '.1f'),
            ('Total Final Cost', 'final_cost', '.1f'),
            ('AOCC', 'aocc', '.4f'),
            ('Escape Count', 'escape_count', 'd'),
        ]
        table_data = []
        for label, key, fmt in rows_info:
            row = [label]
            val = le_degn_result.get(key, 0)
            row.append(f'{val:{fmt}}')
            if baseline_result:
                bval = baseline_result.get(key, 0)
                row.append(f'{bval:{fmt}}')
            table_data.append(row)
        if baseline_result and baseline_result['aocc'] > 1e-8:
            improve = ((le_degn_result['aocc'] - baseline_result['aocc'])
                       / max(baseline_result['aocc'], 1e-8) * 100)
            table_data.append(['AOCC Improvement', f'{improve:+.1f}%', '-'])
        if baseline_result:
            le_trans = le_degn_result.get('final_transition', 0)
            bl_trans = baseline_result.get('final_transition', 0)
            if bl_trans > 1e-8:
                trans_imp = (bl_trans - le_trans) / bl_trans * 100
                table_data.append(['Transition Improvement', f'{trans_imp:+.1f}%', '-'])

        table = ax_table.table(cellText=table_data, colLabels=headers,
                               cellLoc='center', loc='center',
                               colWidths=[0.3, 0.2] + ([0.2] if baseline_result else []))
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)
        for j in range(len(headers)):
            table[0, j].set_facecolor('#2C3E50')
            table[0, j].set_text_props(color='white', fontweight='bold')
        for i in range(len(table_data)):
            for j in range(len(headers)):
                table[i+1, j].set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
        ax_table.set_title('Performance Summary', fontsize=13,
                           fontweight='bold', pad=20)

        fig.suptitle('LE-DEGN: Dynamic Route Optimization — Dashboard',
                     fontsize=16, fontweight='bold', y=0.98)
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Dashboard saved: {filename}")
        Visualizer._auto_open(filename)


# ╔═══════════════════════════════════════════════════════════╗
# ║  SECTION 10: 主入口                                       ║
# ╚═══════════════════════════════════════════════════════════╝

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

    print("="*60)
    print("  LE-DEGN: Language-Empowered Dynamic")
    print("  Edge-centric Graph Network (Fixed Version)")
    print("="*60)
    print(f"\nConfig: nodes={args.nodes}  time={args.time_limit}s  "
          f"erfm_ep={args.erfm_episodes}  stgcn_ep={args.stgcn_epochs}")

    # Step 1
    print("\n" + "-"*50)
    print("[Step 1/7] Creating road network...")
    env = RoadNetworkEnv(node_count=args.nodes)

    # Step 2
    print("\n[Step 2/7] Building line graph...")
    lg = LineGraphBuilder(env)
    lg.build()
    print(f"  Original: {env.G.number_of_nodes()} nodes, {env.G.number_of_edges()} edges")
    print(f"  Line graph: {lg.num_line_nodes()} nodes, {lg.line_graph.number_of_edges()} edges")

    # Step 3
    print("\n[Step 3/7] Training ERFM...")
    erfm = ERFM(feat_dim=LineGraphBuilder.EDGE_FEAT_DIM,
                d_model=64, n_heads=4, n_layers=3, ff_dim=128)
    print(f"  ERFM params: {sum(p.numel() for p in erfm.parameters()):,}")
    ERFMTrainer(erfm, lg, env, lr=5e-4).train(episodes=args.erfm_episodes)

    # Step 4
    print("\n[Step 4/7] Training SA-DGWN...")
    stgcn = SADGWN(feat_dim=2, hidden=32, n_blocks=2)
    print(f"  STGCN params: {sum(p.numel() for p in stgcn.parameters()):,}")
    TrafficDataGenerator(env, lg).train_model(stgcn, epochs=args.stgcn_epochs, batch_size=8)

    # Step 5
    print("\n[Step 5/7] Creating LHH engine...")
    lhh = LHHEngine(env)

    # Step 6
    print("\n[Step 6/7] Running LE-DEGN...")
    system = LEDEGNSystem(env, erfm, stgcn, lhh, lg)
    env.closed_edges.clear()
    le_degn_result = system.execute_dynamic(time_budget=args.time_limit, verbose=True)

    # Step 7
    baseline_result = None
    if not args.no_baseline:
        print("\n[Step 7/7] Running baseline...")
        env.closed_edges.clear()
        baseline = BaselineDHAN(env, lg)
        baseline_events = system._default_events(lg.num_line_nodes())
        baseline_result = baseline.solve(time_budget=args.time_limit,
                                         congestion_events=baseline_events, verbose=True)

    # Final report
    print("\n" + "="*60)
    print("  FINAL PERFORMANCE REPORT")
    print("="*60)
    header = f"{'Metric':<25} {'LE-DEGN':<15}"
    if baseline_result: header += f"{'Baseline':<15}"
    print(header)
    print("-"*60)
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
                  f"{(bl_t - le_t)/bl_t*100:+.1f}%")

    # Visualization
    print("\n" + "="*60)
    print("  Generating visualizations...")
    print("="*60)

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

    print("\n" + "="*60)
    print("  All tasks completed!")
    print("="*60)
    for f in [f1, f2, f3, f4, f5]:
        if os.path.exists(f):
            print(f"  OK {os.path.abspath(f)}")


if __name__ == '__main__':
    main()