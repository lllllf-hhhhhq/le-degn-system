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
