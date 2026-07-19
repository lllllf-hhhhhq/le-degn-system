#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERFM: Edge-central Route Foundation Model
来源: le_degn_system.py Section 3 (lines 512-651) + Section 6 (lines 1014-1121)
"""

import math
import copy
import random

import torch
import torch.nn as nn
import torch.nn.functional as F

from le_degn_system.environment.road_network import RoadNetworkEnv
from le_degn_system.environment.line_graph import LineGraphBuilder


# ═══════════════════════════════════════════════════════════════
# Section 3: ERFM (Edge-central Route Foundation Model)
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# Section 6: ERFM 训练器
# ═══════════════════════════════════════════════════════════════

class ERFMTrainer:
    def __init__(self, model, lg, env, lr=5e-4, entropy_coef=0.02, gamma=0.99):
        self.model = model
        self.lg = lg
        self.env = env
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.entropy_coef = entropy_coef
        self.gamma = gamma
        # 边权总和（常数部分，不参与优化）
        self.fixed_cost = sum(
            self.lg.lid2edge[i][3].get('weight', 10)
            for i in range(self.lg.num_line_nodes()))

    def _rollout(self, embeddings, temperature=1.0):
        N = embeddings.size(0)
        if N == 0: return [], [], [], []
        # 大规模问题只采样子集训练
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
        """成本 = 转移代价总和（与排列顺序有关）"""
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
            reward = -cost / max(self.fixed_cost * 0.1, 1.0)  # 归一化奖励
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

    def _adaptive_train(self, episodes=100, temp_start=1.5, temp_end=0.2,
                         patience=10, warmup=20):
        """
        自适应温度训练: 基于 cost 改善率动态调整温度。
        - 若连续 patience 个 episode 无改善, 升高温度增加探索
        - 若持续改善, 降低温度加速收敛
        """
        print("[ERFM] 自适应温度训练 (Adaptive Temperature)...")
        global_attrs = torch.tensor([5.0/25.0, 1.5, 7.0, 0.5], dtype=torch.float32)
        best_cost, best_params = float('inf'), None
        temp = temp_start
        no_improve = 0

        for ep in range(episodes):
            if ep < warmup:
                # warmup 阶段: 线性退火
                temp = temp_start + (ep/warmup) * (0.5 - temp_start)
            else:
                # 自适应阶段
                if no_improve >= patience:
                    temp = min(1.5, temp * 1.3)  # 升高温度探索
                    no_improve = 0
                else:
                    temp = max(0.1, temp * 0.95)  # 缓慢降温

            self.model.train()
            embeddings = self.model.encode(self.lg.node_features,
                                           self.lg.penalty_matrix, global_attrs)
            tour, log_probs, values, entropies = self._rollout(embeddings, temp)
            if not tour or not log_probs: continue
            cost = self._tour_cost(tour)
            prev_best = best_cost
            if cost < best_cost:
                best_cost = cost
                best_params = copy.deepcopy(self.model.state_dict())
                no_improve = 0
            else:
                no_improve += 1

            # REINFORCE 更新（与 train() 一致）
            reward = -cost / max(self.fixed_cost * 0.1, 1.0)
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
            loss = policy_loss + 0.5 * value_loss + self.entropy_coef * entropy_loss
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            if (ep + 1) % max(1, episodes // 5) == 0:
                print(f"  ep {ep+1}/{episodes}  trans_cost={cost:.1f}  "
                      f"best={best_cost:.1f}  temp={temp:.2f}  "
                      f"no_impr={no_improve}")

        if best_params: self.model.load_state_dict(best_params)
        print(f"[ERFM] 自适应训练完成, 最优转移成本={best_cost:.1f}")
        return best_cost
