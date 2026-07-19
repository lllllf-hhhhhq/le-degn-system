# -*- coding: utf-8 -*-
"""
Section 7: LE-DEGN 集成系统
从 le_degn_system.py 提取

包含:
  - LEDEGNSystem: LE-DEGN 集成系统，
    使用 ERFM + SA-DGWN + LHH 实现动态路径优化
"""

import random

import torch

from le_degn_system.core.metrics import PerformanceTracker, calculate_aocc


class LEDEGNSystem:
    """LE-DEGN 集成系统。

    三阶段执行流程:
      Phase 1 - 初始路径构建 (贪心NN)
      Phase 2 - 动态行驶模拟 (拥堵检测 + LHH逃逸 + ERFM重规划)
      Phase 3 - 局部2-opt优化

    依赖: ERFM, SADGWN, LHHEngine, LineGraphBuilder 的转移代价矩阵,
          PerformanceTracker, calculate_aocc
    """

    def __init__(self, env, erfm, stgcn, lhh, lg):
        self.env = env
        self.erfm = erfm
        self.stgcn = stgcn
        self.lhh = lhh
        self.lg = lg
        self.state = 'MACRO'
        self.global_attrs = torch.tensor([5.0 / 25.0, 1.5, 7.0, 0.5],
                                         dtype=torch.float32)
        # 边权总和（服务代价，固定）
        self.service_cost = sum(
            self.lg.lid2edge[i][3].get('weight', 10)
            for i in range(self.lg.num_line_nodes()))

    def plan_global_route(self, tracker=None, temperature=0.3,
                          blocked_lids=None):
        """使用采样解码 + 多次采样取最优。"""
        self.erfm.eval()
        best_tour, best_cost = None, float('inf')
        n_samples = 5  # 多次采样

        with torch.no_grad():
            emb = self.erfm.encode(self.lg.node_features,
                                    self.lg.penalty_matrix, self.global_attrs)
            N = emb.size(0)
            if N == 0:
                return []

            # 排除被封锁的线图节点
            available = list(range(N))
            if blocked_lids:
                available = [i for i in available if i not in blocked_lids]
            if not available:
                available = list(range(N))

            # 限制规模
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
                    # 采样解码（不是argmax）
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
        if tracker:
            tracker.update(total_cost)
        return best_tour if best_tour else []

    def _tour_transition_cost(self, tour):
        """只计算转移代价（与顺序相关的部分）。"""
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
        """服务代价(固定) + 转移代价(可优化)。"""
        return self.service_cost + self._tour_transition_cost(tour)

    def tour_to_node_path(self, tour):
        """将线图节点序列转为原始路网节点序列。"""
        if not tour:
            return []
        path = []
        for lid in tour:
            if lid not in self.lg.lid2edge:
                continue
            u, v, _, _ = self.lg.lid2edge[lid]
            if not path or path[-1] != u:
                path.append(u)
            path.append(v)
        return path

    def predict_congestion(self, history_steps=12):
        """使用 SA-DGWN 预测拥堵蔓延。

        ★ 修复: 使用真实路网属性生成可学习的拥堵模式。
        速度因子低/拥堵概率高的边更可能出现拥堵。
        SA-DGWN 可以学到"拥堵概率高 → 高风险"的关联。
        """
        if self.stgcn is None:
            return torch.zeros(self.lg.num_line_nodes())
        N = self.lg.num_line_nodes()
        T, F = history_steps, 2
        x = torch.zeros(N, T, F)
        for i in range(N):
            if i not in self.lg.lid2edge:
                continue
            u, v, k, _ = self.lg.lid2edge[i]
            is_blocked = (u, v) in self.env.closed_edges
            # 从真实路网属性获取拥堵风险信号
            edge_attrs = self.env.G[u][v][k] if (u, v) in self.env.G else {}
            speed_factor = edge_attrs.get('speed_factor', 0.8)
            congestion_prob = edge_attrs.get('congestion_prob', 0.3)

            for t in range(T):
                # 速度信号: 低速度因子 + 拥堵概率 → 高风险
                base_signal = 0.9 - speed_factor * 0.4  # [0.42, 0.66]
                risk_signal = min(0.95, base_signal + congestion_prob * 0.5)
                x[i, t, 0] = 0.05 if is_blocked else 0.85 + random.gauss(0, 0.03)
                # 拥堵信号: 拥堵概率高且速度因子低的边更容易拥堵
                x[i, t, 1] = 0.95 if is_blocked else (
                    0.2 + congestion_prob * 0.6 - speed_factor * 0.1
                    + random.gauss(0, 0.03))
        self.stgcn.eval()
        with torch.no_grad():
            return self.stgcn(x, self.lg.adj)

    def _get_blocked_lids(self):
        """获取当前被封锁的线图节点ID。"""
        blocked = set()
        for lid in range(self.lg.num_line_nodes()):
            u, v, _, _ = self.lg.lid2edge[lid]
            if (u, v) in self.env.closed_edges:
                blocked.add(lid)
        return blocked

    def execute_dynamic(self, time_budget=10.0, congestion_events=None,
                        verbose=True, initial_tour=None):
        """三阶段动态路径优化执行。

        Phase 1: 初始路径构建 (贪心NN或外部传入)
        Phase 2: 动态行驶模拟 (拥堵事件检测、LHH逃逸、ERFM重规划)
        Phase 3: 局部2-opt优化

        Args:
            time_budget: 执行时间预算（秒）
            congestion_events: 拥堵事件列表，None时使用默认事件
            verbose: 是否输出详细信息
            initial_tour: 外部初始路径（用于消融研究一致性），None时使用贪心NN

        Returns:
            dict: 包含 final_cost, aocc, trajectory 等指标的结果字典
        """
        tracker = PerformanceTracker(time_budget)
        log = []
        if verbose:
            print("\n" + "=" * 60)
            print("LE-DEGN 动态路径优化系统启动")
            print("=" * 60)

        # Phase 1: 初始路径（支持外部传入，确保消融一致性）
        if initial_tour is not None:
            if verbose:
                print("\n[Phase 1] 使用外部初始路径...")
            tour = list(initial_tour)
            init_trans = self._tour_transition_cost(tour)
        else:
            if verbose:
                print("\n[Phase 1] 初始路径构建...")
            # 贪心最近邻构建初始路径（与Baseline相同起点）
            TC = self.lg.transition_cost
            N = self.lg.num_line_nodes()
            available_nn = list(range(N))
            max_nn = min(len(available_nn), 120)
            if len(available_nn) > max_nn:
                available_nn = random.sample(available_nn, max_nn)
            nn_best_tour, nn_best_trans = None, float('inf')
            starts = random.sample(available_nn, min(5, len(available_nn)))
            for start in starts:
                unvisited = set(available_nn)
                cur = start
                unvisited.remove(cur)
                nn_tour = [cur]
                while unvisited:
                    nearest, min_c = None, float('inf')
                    for nb in unvisited:
                        c = TC[cur, nb].item()
                        if c < min_c:
                            min_c, nearest = c, nb
                    if nearest is None:
                        break
                    nn_tour.append(nearest)
                    unvisited.remove(nearest)
                    cur = nearest
                nn_trans = sum(TC[nn_tour[i], nn_tour[i + 1]].item()
                               for i in range(len(nn_tour) - 1))
                if len(nn_tour) > 1:
                    nn_trans += TC[nn_tour[-1], nn_tour[0]].item()
                if nn_trans < nn_best_trans:
                    nn_best_trans, nn_best_tour = nn_trans, list(nn_tour)
            init_trans = nn_best_trans
            tour = list(nn_best_tour)
        node_path = self.tour_to_node_path(tour)
        total_cost = self.service_cost + init_trans
        tracker.update(total_cost)
        if verbose:
            print(f"  [贪心NN] 初始路径: {len(tour)} 条边, "
                  f"转移代价={init_trans:.1f}")
            print(f"  服务代价(固定): {self.service_cost:.1f}")
            print(f"  总成本: {total_cost:.1f}")
            print(f"  节点路径前10步: {node_path[:10]}")
        log.append(('ERFM_INIT', total_cost, tracker.elapsed()))

        # Phase 2: 动态行驶模拟
        if verbose:
            print("\n[Phase 2] 动态行驶模拟...")
        cur_tour = list(tour)
        progress = 0
        events = congestion_events or self._default_events(len(tour))
        for event in events:
            if not tracker.update(self._tour_total_cost(cur_tour)):
                break
            edges_to_block = event.get('edges', [])
            if verbose:
                print(f"\n  [事件] {event.get('type', 'congestion')}: "
                      f"封闭 {len(edges_to_block)} 条道路")
            for e in edges_to_block:
                self.env.closed_edges.add(tuple(e))

            if verbose:
                print("  [STGCN] 预测拥堵蔓延...")
            c_dyn = self.predict_congestion()
            # Sigmoid输出[0,1], 使用0.5作阈值
            high_risk = (c_dyn > 0.5).sum().item()
            if verbose:
                print(f"    高风险边数: {high_risk}/{self.lg.num_line_nodes()}  "
                      f"(max={c_dyn.max():.3f} mean={c_dyn.mean():.3f})")

            affected, affected_node = False, None
            for lid in cur_tour[progress:]:
                if lid not in self.lg.lid2edge:
                    continue
                u, v, _, _ = self.lg.lid2edge[lid]
                if (u, v) in self.env.closed_edges:
                    affected, affected_node = True, u
                    break
            if affected and affected_node is not None:
                if verbose:
                    print(f"  [检测] 路径受阻! 节点={affected_node}")
                self.state = 'ESCAPE'
                escape_path = self.lhh.escape(affected_node,
                                              self.env.closed_edges, verbose)
                log.append(('LHH_ESCAPE', len(escape_path), tracker.elapsed()))
                self.state = 'REPLAN'
                if verbose:
                    print("\n  [ERFM] 重新规划...")
                # 重规划时排除被封锁的边, 使用更高温度
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
                if verbose:
                    print("  [检测] 路径未受阻, 继续行驶")
                progress = min(progress + len(cur_tour) // 4, len(cur_tour) - 1)
            if random.random() < 0.3 and self.env.closed_edges:
                reopened = self.env.reopen_random_edges(1)
                if verbose and reopened:
                    print(f"  [恢复] 重新开放 {len(reopened)} 条道路")

        # Phase 3: 局部2-opt优化
        if verbose:
            print("\n[Phase 3] 局部 2-opt 优化...")
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

        # L/U 计算
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
            print("\n" + "=" * 60)
            print("LE-DEGN 执行结果")
            print("=" * 60)
            print(f"  服务代价(固定):    {self.service_cost:.1f}")
            print(f"  初始转移代价:      {self._tour_transition_cost(tour):.1f}")
            print(f"  最终转移代价:      {post_opt_trans:.1f}")
            print(f"  最终总成本:        {opt_total:.1f}")
            print(f"  AOCC:              {aocc:.4f}")
            print(f"  逃逸次数:          {self.lhh.escape_count}")
            print(f"  总耗时:            {tracker.elapsed():.2f}s")
        return result

    def _default_events(self, tour_len):
        """生成默认拥堵事件序列。"""
        events = []
        edges = list(self.env.G.edges(keys=False))
        if not edges:
            return events
        for i in range(3):
            num_block = random.randint(2, max(3, len(edges) // 10))
            chosen = random.sample(edges, min(num_block, len(edges)))
            events.append({'type': f'congestion_wave_{i + 1}',
                           'edges': [list(e) for e in chosen]})
        return events

    def _local_2opt(self, tour, max_iter=300):
        """基于转移代价的2-opt局部优化。"""
        if len(tour) < 4:
            return tour
        best = list(tour)
        best_cost = self._tour_transition_cost(best)
        TC = self.lg.transition_cost
        improved_total = 0

        for iteration in range(max_iter):
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, min(i + 30, len(best))):
                    # 增量计算: 只看受影响的边
                    # 旧: ... best[i-1] -> best[i] -> ... -> best[j] -> best[j+1 if exists] ...
                    # 新: ... best[i-1] -> best[j] -> ... -> best[i] -> best[j+1 if exists] ...
                    a, b = best[i - 1], best[i]
                    c, d = best[j], best[(j + 1) % len(best)]

                    old_cost = TC[a, b].item() + TC[c, d].item()
                    new_cost = TC[a, c].item() + TC[b, d].item()

                    if new_cost < old_cost - 1e-6:
                        best[i:j + 1] = best[i:j + 1][::-1]
                        best_cost = self._tour_transition_cost(best)
                        improved = True
                        improved_total += (old_cost - new_cost)
            if not improved:
                break
        return best
