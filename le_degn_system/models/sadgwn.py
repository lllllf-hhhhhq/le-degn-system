#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SA-DGWN: Self-Attention Dynamic Graph WaveNet (时空图卷积交通预测器)
来源: le_degn_system.py Section 4 (lines 653-766)
"""

import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from le_degn_system.environment.road_network import RoadNetworkEnv
from le_degn_system.environment.line_graph import LineGraphBuilder


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
    """时空图卷积拥堵预测器。

    两种模式:
      - 标准模式: out_proj → Sigmoid, 输出拥堵概率 [0,1]
      - 回归模式: reg_head → Linear, 输出速度预测, 外部转拥堵概率
    """
    def __init__(self, feat_dim=2, hidden=32, n_blocks=2):
        super().__init__()
        self.blocks = nn.ModuleList(
            [SpatioTemporalBlock(feat_dim if i == 0 else hidden, hidden, 2 ** i)
             for i in range(n_blocks)])
        self.out_proj = nn.Sequential(
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1), nn.Sigmoid())  # 标准: Sigmoid -> [0,1]
        self.reg_head = nn.Linear(hidden, 1)       # 回归: 速度预测
        self.hidden = hidden
        self._use_regression = False
        self._sumo_speeds = None                   # (N, T) SUMO 速度数据
        self._adj = None

    def enable_regression_mode(self):
        """切换为回归模式 (速度预测 + 外部转拥堵)。"""
        self._use_regression = True

    def set_sumo_data(self, speeds: 'torch.Tensor', adj: 'torch.Tensor'):
        """注入 SUMO 速度数据和邻接矩阵。"""
        self._sumo_speeds = speeds
        self._adj = adj.clone()

    def forward(self, x, adj):
        h = x
        for i, blk in enumerate(self.blocks):
            if i > 0:
                if h.dim() == 2:
                    h = h.unsqueeze(1).expand(-1, x.size(1), -1)
            h_out = blk(h if h.dim() == 3 else
                        h.unsqueeze(1).expand(-1, x.size(1), -1), adj)
            h = h_out
        if self._use_regression:
            return self.reg_head(h).squeeze(-1)  # (N,) 速度预测
        return self.out_proj(h).squeeze(-1)      # (N,) 拥堵概率

    def predict_congestion_from_sumo(self, history_steps=12, scale=3.5):
        """使用 SUMO 数据预测拥堵: 预测速度 → 比较实际速度 → 拥堵概率。

        返回: (N,) tensor, 拥堵概率 [0,1]
        """
        if self._sumo_speeds is None or self._adj is None:
            return torch.zeros(self._sumo_speeds.size(0) if self._sumo_speeds is not None else 1)
        N, T_full = self._sumo_speeds.shape
        if T_full < history_steps + 1:
            return torch.zeros(N)

        # 取最近 history_steps 步作为输入
        import random
        t_start = random.randint(0, T_full - history_steps - 1)
        x = self._sumo_speeds[:, t_start:t_start+history_steps].unsqueeze(-1)  # (N, W, 1)
        # 拼接流量特征（用速度近似）
        flow = self._sumo_speeds[:, t_start:t_start+history_steps].unsqueeze(-1) * 0.5
        x = torch.cat([x, flow], dim=-1)  # (N, W, 2)

        # 预测下一步速度
        with torch.no_grad():
            pred_speed = self.forward(x, self._adj)  # (N,)
            true_speed = self._sumo_speeds[:, t_start+history_steps]  # (N,)

        # 速度下降 → 拥堵概率
        speed_drop = (true_speed - pred_speed) / true_speed.clamp(min=0.01)
        congestion = torch.sigmoid(speed_drop * scale)
        return congestion

    @classmethod
    def from_sumo_checkpoint(cls, checkpoint_path: str, sumo_npy_path: str,
                             feat_dim=2, hidden=32, n_blocks=2):
        """从 SUMO 训练权重创建并加载模型 (回归模式)。

        参数:
            checkpoint_path: sadgwn_sumo_trained.pt 路径
            sumo_npy_path:   traffic_tensor.npy 路径
        返回: SADGWN 实例, 已加载权重并处于回归模式
        """
        import numpy as np
        model = cls(feat_dim=feat_dim, hidden=hidden, n_blocks=n_blocks)
        model.enable_regression_mode()

        # 加载 SUMO 速度数据
        arr = np.load(sumo_npy_path)  # (N, T, 2)
        speeds = torch.from_numpy(arr[:, :, 0]).float()  # (N, T)
        model._sumo_speeds = speeds

        # 加载权重
        state_dict = torch.load(checkpoint_path, map_location='cpu')
        # 兼容不同格式的 state_dict
        model.load_state_dict(state_dict, strict=False)
        model.eval()

        return model


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
            # 标签 [0,1]: 0=畅通, 1=拥堵
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
                loss = F.binary_cross_entropy(pred, y)  # BCE loss
                optim.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optim.step()
                total_loss += loss.item()
            if (ep + 1) % max(1, epochs // 5) == 0:
                print(f"  epoch {ep + 1}/{epochs}  loss={total_loss / batch_size:.4f}")
        print("[STGCN] 训练完成")
