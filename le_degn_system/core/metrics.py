# -*- coding: utf-8 -*-
"""
Section 0: 通用工具
从 le_degn_system.py 提取

包含:
  - PerformanceTracker: 性能追踪器，记录求解过程中的 cost 轨迹
  - calculate_aocc: 计算 AOCC (Area Over the Convergence Curve) 指标
"""

import time
import numpy as np
from typing import List, Tuple


class PerformanceTracker:
    """性能追踪器：记录求解过程中最优 cost 随时间的变化轨迹。

    用于计算 AOCC (Area Over the Convergence Curve) 指标，
    该指标衡量算法在给定时间预算内收敛到高质量解的能力。
    """

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
    """计算 AOCC (Area Over the Convergence Curve)。

    将收敛曲线归一化到 [0, 1] 区间后，计算曲线下方的面积。
    AOCC 越大，表示算法越早收敛到高质量解。

    参数:
        trajectory: List[Tuple[float, float]]，每次记录的 (elapsed_time, best_cost)
        time_budget: float，总时间预算
        L: float，理论下界
        U: float，理论上界

    返回:
        float，AOCC 值，范围 [0, 1]
    """
    if not trajectory:
        return 0.0
    # ★ 修复: 若数据点超出边界, 自动扩展U以保证有效归一化
    max_observed = max(y for _, y in trajectory)
    U_effective = max(U, max_observed * 1.05)  # 扩展5%余量
    steps = np.linspace(0, time_budget, num=500)
    total, idx = 0.0, 0
    for t in steps:
        while idx < len(trajectory) - 1 and trajectory[idx + 1][0] <= t:
            idx += 1
        y = trajectory[idx][1]
        y_b = max(L, min(y, U_effective))
        y_n = (y_b - L) / (U_effective - L) if U_effective > L else 1.0
        total += 1.0 - y_n
    return total / len(steps)


def calculate_adaptive_bounds(service_cost, transition_cost_matrix, tour_len):
    """
    ★ 新增: 根据真实路网规模自适应计算 L/U 边界。

    对于大路网（几百节点），service_cost 占主导，
    简单的 N*300 上界会导致 AOCC=0。此函数自动适配。

    Args:
        service_cost: 固定服务代价
        transition_cost_matrix: 转移代价方阵 (N×N)
        tour_len: 当前路径长度

    Returns:
        (L, U) 自适应边界
    """
    N = transition_cost_matrix.size(0)
    # 下界: 每步取最短可能转移代价
    nn_lower = 0.0
    for i in range(min(tour_len, N)):
        row = transition_cost_matrix[i].clone()
        if row.dim() > 1:
            row.fill_diagonal_(float('inf'))
        else:
            row[i] = float('inf')
        nn_lower += row.min().item()
    L = service_cost + nn_lower

    # 上界: 基于实际转移代价统计量，而非固定 300
    max_edge_cost = float(transition_cost_matrix.max())
    avg_edge_cost = float(transition_cost_matrix[transition_cost_matrix > 0].mean())
    # U = service_cost + tour_len * max(max_edge, avg_edge*3)
    # 这样大路网的上界自动适配真实代价量级
    U = service_cost + tour_len * max(max_edge_cost, avg_edge_cost * 3.0)

    return L, U
