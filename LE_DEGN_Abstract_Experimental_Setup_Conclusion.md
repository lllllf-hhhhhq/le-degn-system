# LE-DEGN: Abstract, Experimental Setup, and Conclusion

---

## Abstract

Street-view vehicle routing in mixed unidirectional/bidirectional urban road networks poses a significant combinatorial challenge due to dynamic congestion, heterogeneous road types, and complex kinematic constraints. This paper proposes the Language-Empowered Dynamic Edge-centric Graph Network (LE-DEGN), a novel three-module architecture that addresses the Mixed Chinese Postman Problem (MCPP) through learned edge representations, spatio-temporal congestion prediction, and adaptive heuristic selection. The system first transforms the primal road graph into a line graph, enabling an Edge-centric Route Foundation Model (ERFM) based on penalty-biased multi-head self-attention to encode 13-dimensional edge features into optimized routing policies. A Spatio-Temporal Attention-based Dynamic Graph Wave Network (SA-DGWN) proactively predicts congestion propagation using dilated causal convolutions and graph convolutions, while a Language-driven Heuristic Hub (LHH) adaptively selects escape strategies through a Generate-Score-Execute-Self-reflect (GSES) loop. Extensive experiments on synthetic urban networks ranging from 40 to 100 nodes demonstrate that LE-DEGN achieves an average cost reduction of 12.1% over a strong Greedy Nearest-Neighbor baseline with DHAN-style congestion handling, with peak improvements reaching 16.3% at 80-node networks. Ablation studies confirm the synergistic contribution of all three modules, and scalability analysis verifies near-linear execution time scaling, establishing LE-DEGN as an effective and practical solution for dynamic urban routing.

---

## 摘要

混合单向/双向城市路网的街景车路径优化因动态拥堵、异构道路类型和复杂运动学约束而构成重大组合挑战。本文提出语言赋能的动态边中心图网络（LE-DEGN），一种通过学习的边表示、时空拥堵预测和自适应启发式选择来解决混合中国邮路问题（MCPP）的新型三模块架构。该系统首先将原始路图转换为线图，使基于惩罚偏置多头自注意力的边中心路由基础模型（ERFM）能够将13维边特征编码为优化的路由策略。时空注意力动态图波网络（SA-DGWN）利用扩张因果卷积和图卷积主动预测拥堵传播，而语言驱动启发式中心（LHH）通过生成-评分-执行-自反思（GSES）循环自适应选择逃逸策略。在40至100个节点的合成城市网络上的大量实验表明，LE-DEGN相比具有DHAN风格拥堵处理的强贪婪最近邻基线实现了平均12.1%的成本降低，在80节点网络中峰值改进达到16.3%。消融研究证实了所有三个模块的协同贡献，可扩展性分析验证了近乎线性的执行时间缩放，确立了LE-DEGN作为动态城市路由的有效实用解决方案。

---

## 4. Experimental Setup

### 4.1 Hardware and Software Environment

All experiments were conducted on a single workstation equipped with an Intel Core i7 processor and 16 GB of system memory. The software stack comprises Python 3.8, PyTorch 1.12.0, NetworkX 2.8, and NumPy 1.21.0. All neural network computations utilize CPU execution to ensure reproducibility and accessibility. The operating system is Windows 10, and all random seeds are explicitly fixed for deterministic behavior.

### 4.2 Dataset Generation

Since no publicly available benchmark dataset captures the full complexity of mixed unidirectional/bidirectional urban networks with dynamic congestion, we generate synthetic road networks using the `RoadNetworkEnv` class. Networks are constructed with 40, 60, 80, and 100 nodes, corresponding to increasing levels of urban complexity from small neighborhoods to metropolitan districts. Each network is generated with the following topological parameters: average degree 2.7, T-junction ratio 0.65, cross-junction ratio 0.18, dead-end ratio 0.07, segment length mean 80 m with standard deviation 20 m, minimum turning radius 5.0 m, left-turn penalty 1.5, and U-turn penalty 7.0. Five road types are embedded: Main Road, Commercial Pedestrian, School Zone, Residential, and Construction, each with distinct speed factors, congestion probabilities, and time windows. The spatial-dependent scenario sampling distribution assigns higher probability to Main Roads near the central corridor. All generated networks undergo strong connectivity patching via a three-phase procedure (zero-degree resolution, sink resolution, and SCC bridging) and are verified via Tarjan's algorithm.

### 4.3 Hyperparameter Configuration

The hyperparameters for each LE-DEGN module are summarized in Table 1.

**Table 1: Hyperparameter Configuration**

| Module | Parameter | Value | Description |
|:---|:---|:---|:---|
| ERFM Encoder | `feat_dim` | 13 | Edge feature dimension |
| | `d_model` | 64 | Transformer model dimension |
| | `n_heads` | 4 | Number of attention heads |
| | `n_layers` | 3 | Number of transformer blocks |
| | `ff_dim` | 128 | Feed-forward network dimension |
| | `dropout` | 0.1 | Dropout rate |
| ERFM Decoder | `temperature_start` | 1.5 | Initial sampling temperature |
| | `temperature_end` | 0.2 | Final sampling temperature |
| ERFM Training | `episodes` | 50 | REINFORCE training episodes |
| | `lr` | 5e-4 | Adam learning rate |
| | `entropy_coef` | 0.02 | Entropy regularization coefficient |
| | `gamma` | 0.99 | Discount factor for returns |
| | `grad_clip` | 1.0 | Gradient clipping norm |
| SA-DGWN | `feat_dim` | 2 | Input features (speed, flow) |
| | `hidden` | 32 | Hidden layer dimension |
| | `n_blocks` | 2 | Number of spatio-temporal blocks |
| | `epochs` | 30 | Training epochs |
| | `lr` | 1e-3 | Adam learning rate |
| | `batch_size` | 16 | Training batch size |
| | `T` | 12 | Historical timesteps |
| LHH | `max_depth` | 15-50 | Heuristic search depth |
| | `k_hop` | 3 | Subgraph neighborhood radius |
| | `window_size` | 5 | Reflection rolling window |
| 2-opt | `max_iter` | 300 | Maximum iterations |
| | `search_window` | 30 | Local search neighborhood |
| System | `time_budget` | 10.0 s | Execution time limit |
| | `n_samples` | 5 | ERFM rollout samples |
| | `max_tour` | 80-120 | Maximum tour size |

### 4.4 Evaluation Metrics

Four primary metrics are employed to evaluate system performance:

1. **Total Cost**: The sum of service cost (fixed edge traversal cost) and transition cost (order-dependent inter-edge traversal cost), measuring overall routing efficiency.

2. **AOCC (Area Over the Convergence Curve)**: An anytime performance metric computed over 500 time-discretized intervals. The cost trajectory is normalized against a lower bound (service cost plus nearest-neighbor heuristic) and an upper bound (service cost plus 300 times tour length). AOCC near 1.0 indicates rapid convergence; near 0.0 indicates stagnation.

3. **Escape Count**: The number of congestion-triggered escape operations, reflecting the system's ability to avoid dynamic obstacles.

4. **Execution Time**: Wall-clock time from system initialization to final optimization completion.

### 4.5 Baseline Configuration

The baseline method, referred to as DHAN+NN (Dynamic Heuristic Attention Network with Nearest-Neighbor), implements a Greedy Nearest-Neighbor heuristic augmented with DHAN-style congestion handling. Specifically:

- Route construction samples 5 distinct starting edges and greedily appends the nearest unvisited edge based on the transition cost matrix.
- Congestion response applies a fixed 15% penalty to the transition cost upon detecting any blocked edge in the current tour.
- No predictive congestion modeling, no adaptive re-planning, and no local optimization are performed.

This baseline represents a strong conventional approach that lacks LE-DEGN's three core innovations: learned edge representations, spatio-temporal prediction, and adaptive heuristic selection.

### 4.6 Experimental Protocol

Each experimental configuration is executed with 10 independent random seeds to ensure statistical reliability. For each run, the following protocol is observed:

1. **Network Generation**: A new road network is instantiated with the specified node count and fixed random seed.
2. **Line Graph Construction**: The primal graph is transformed into a line graph with 13-dimensional edge features, penalty matrix, adjacency matrix, and transition cost matrix.
3. **ERFM Training**: The edge-centric transformer is trained for 50 episodes using REINFORCE with temperature annealing from 1.5 to 0.2.
4. **SA-DGWN Training**: The spatio-temporal predictor is trained for 30 epochs on synthetic traffic data with binary cross-entropy loss.
5. **Dynamic Execution**: Three predefined congestion events inject random edge blockages (2-3 edges per event). The system executes the three-phase pipeline: global planning, dynamic re-planning with LHH escape, and 2-opt local refinement.
6. **Metric Recording**: Total cost, AOCC, escape count, and execution time are recorded for both LE-DEGN and the baseline under identical congestion events.

Reported values represent the mean across all 10 independent runs.

---

## 4. 实验设置

### 4.1 硬件与软件环境

所有实验均在配备Intel Core i7处理器和16 GB系统内存的单工作站上进行。软件栈包括Python 3.8、PyTorch 1.12.0、NetworkX 2.8和NumPy 1.21.0。所有神经网络计算均使用CPU执行以确保可复现性和可及性。操作系统为Windows 10，所有随机种子均显式固定以确保确定性行为。

### 4.2 数据集生成

由于现有公开基准数据集无法完整捕捉混合单向/双向城市网络中动态拥堵的全部复杂性，我们使用`RoadNetworkEnv`类生成合成道路网络。网络分别构建为40、60、80和100个节点，对应从小型社区到都市区的递增城市复杂度。每个网络使用以下拓扑参数生成：平均度2.7、T型路口比例0.65、十字路口比例0.18、断头路比例0.07、路段长度均值80米（标准差20米）、最小转弯半径5.0米、左转惩罚1.5、掉头惩罚7.0。嵌入五种道路类型：主干道、商业步行街、学校周边、居民区和施工路段，每种具有不同的速度因子、拥堵概率和时间窗口。空间相关的场景采样分布为中心走廊附近的主干道分配更高概率。所有生成的网络均通过三阶段程序（零度节点修复、汇节点修复和强连通分量桥接）进行强连通性修补，并通过Tarjan算法验证。

### 4.3 超参数配置

各LE-DEGN模块的超参数汇总于表1。

**表1：超参数配置**

| 模块 | 参数 | 取值 | 说明 |
|:---|:---|:---|:---|
| ERFM编码器 | `feat_dim` | 13 | 边特征维度 |
| | `d_model` | 64 | Transformer模型维度 |
| | `n_heads` | 4 | 注意力头数 |
| | `n_layers` | 3 | Transformer块数 |
| | `ff_dim` | 128 | 前馈网络维度 |
| | `dropout` | 0.1 | Dropout比率 |
| ERFM解码器 | `temperature_start` | 1.5 | 初始采样温度 |
| | `temperature_end` | 0.2 | 最终采样温度 |
| ERFM训练 | `episodes` | 50 | REINFORCE训练轮数 |
| | `lr` | 5e-4 | Adam学习率 |
| | `entropy_coef` | 0.02 | 熵正则化系数 |
| | `gamma` | 0.99 | 回报折扣因子 |
| | `grad_clip` | 1.0 | 梯度裁剪范数 |
| SA-DGWN | `feat_dim` | 2 | 输入特征（速度、流量） |
| | `hidden` | 32 | 隐藏层维度 |
| | `n_blocks` | 2 | 时空块数 |
| | `epochs` | 30 | 训练轮数 |
| | `lr` | 1e-3 | Adam学习率 |
| | `batch_size` | 16 | 训练批次大小 |
| | `T` | 12 | 历史时间步 |
| LHH | `max_depth` | 15-50 | 启发式搜索深度 |
| | `k_hop` | 3 | 子图邻域半径 |
| | `window_size` | 5 | 反思滚动窗口 |
| 2-opt | `max_iter` | 300 | 最大迭代次数 |
| | `search_window` | 30 | 局部搜索邻域 |
| 系统 | `time_budget` | 10.0秒 | 执行时间限制 |
| | `n_samples` | 5 | ERFM采样次数 |
| | `max_tour` | 80-120 | 最大路径规模 |

### 4.4 评估指标

采用四个主要指标评估系统性能：

1. **总成本（Total Cost）**：服务成本（固定边遍历成本）与转移成本（顺序相关的边间遍历成本）之和，衡量整体路由效率。

2. **AOCC（收敛曲线上方面积）**：在500个时间离散区间上计算的随时性能指标。成本轨迹相对于下界（服务成本加最近邻启发式）和上界（服务成本加300倍路径长度）进行归一化。AOCC接近1.0表示快速收敛；接近0.0表示停滞。

3. **逃逸次数（Escape Count）**：拥堵触发的逃逸操作次数，反映系统规避动态障碍的能力。

4. **执行时间（Execution Time）**：从系统初始化到最终优化完成的挂钟时间。

### 4.5 基线配置

基线方法称为DHAN+NN（动态启发式注意力网络与最近邻），实现了贪婪最近邻启发式与DHAN风格拥堵处理的组合。具体而言：

- 路径构造采样5个不同的起始边，并基于转移代价矩阵贪婪地追加最近的未访问边。
- 拥堵响应在检测到当前路径中的任何被封锁边时，对转移成本施加固定的15%惩罚。
- 不执行预测性拥堵建模、自适应重新规划或局部优化。

该基线代表一种强大的传统方法，但缺乏LE-DEGN的三个核心创新：学习的边表示、时空预测和自适应启发式选择。

### 4.6 实验协议

每个实验配置使用10个独立随机种子执行以确保统计可靠性。每次运行遵循以下协议：

1. **网络生成**：使用指定的节点计数和固定随机种子实例化新的道路网络。
2. **线图构建**：将原始图转换为线图，包含13维边特征、惩罚矩阵、邻接矩阵和转移代价矩阵。
3. **ERFM训练**：使用REINFORCE算法训练边中心Transformer 50轮，温度从1.5退火至0.2。
4. **SA-DGWN训练**：使用二元交叉熵损失在合成交通数据上训练时空预测器30轮。
5. **动态执行**：三个预定义拥堵事件注入随机边封锁（每个事件2-3条边）。系统执行三阶段管线：全局规划、带LHH逃逸的动态重新规划和2-opt局部优化。
6. **指标记录**：在相同拥堵事件下记录LE-DEGN和基线的总成本、AOCC、逃逸次数和执行时间。

报告值为10次独立运行的平均值。

---

## 5. Conclusion

### 5.1 Summary of Contributions

This paper presents the Language-Empowered Dynamic Edge-centric Graph Network (LE-DEGN), a novel architecture for dynamic street-view vehicle routing in mixed unidirectional/bidirectional urban networks. The key contributions are threefold:

First, we introduce an Edge-centric Route Foundation Model (ERFM) that transforms the primal road graph into a line graph and employs penalty-biased multi-head self-attention to encode 13-dimensional edge features. This edge-centric perspective fundamentally reformulates the Mixed Chinese Postman Problem as a node sequencing task on edges, enabling the transformer architecture to directly model inter-edge transition costs.

Second, we propose a Spatio-Temporal Attention-based Dynamic Graph Wave Network (SA-DGWN) that proactively predicts congestion propagation through dilated causal convolutions and graph convolutions. By forecasting high-risk road segments before they affect the planned route, SA-DGWN enables proactive re-planning rather than reactive escape.

Third, we design a Language-driven Heuristic Hub (LHH) that adaptively selects among five complementary heuristic strategies through a Generate-Score-Execute-Self-reflect (GSES) loop. The reflection mechanism continuously updates heuristic preferences based on a rolling performance window, enabling rapid adaptation to prevailing network conditions.

### 5.2 Key Findings

Extensive experiments on synthetic urban networks with 40 to 100 nodes demonstrate that LE-DEGN achieves consistent and statistically significant performance improvements over a strong Greedy Nearest-Neighbor baseline with DHAN-style congestion handling. The system realizes an average total cost reduction of 12.1% across all tested scales, with peak improvements of 16.3% at 80-node networks. AOCC metrics confirm faster convergence to high-quality solutions, with the performance gap widening from 22.9% at 40 nodes to 33.9% at 100 nodes.

Ablation studies reveal the synergistic nature of the three modules: ERFM alone is insufficient for dynamic environments (AOCC = 0.0000), while the full system achieves AOCC = 0.5387. LHH contributes a 52.2% cost reduction through intelligent escape handling, and SA-DGWN provides an additional 18.3% improvement through proactive congestion prediction. Execution times remain practical (0.82-2.49 seconds) with near-linear scaling, confirming LE-DEGN's suitability for real-time urban routing applications.

### 5.3 Limitations and Future Work

Several limitations of the current work suggest directions for future research. First, the experiments are conducted on synthetically generated road networks; validation on real-world urban datasets such as OpenStreetMap would strengthen the practical applicability claims. Second, the SA-DGWN module is trained on synthetic traffic patterns; integration with real historical traffic data would improve prediction accuracy. Third, the current system handles a single vehicle; extending LE-DEGN to multi-vehicle collaborative routing scenarios represents a promising direction. Fourth, the language component in LHH currently operates as structured state verbalization rather than natural language; deeper integration with large language models for heuristic generation could unlock more sophisticated adaptive behaviors. Finally, the ERFM training uses REINFORCE, which exhibits high variance; exploring actor-critic methods with more stable advantage estimation or transformer-based reinforcement learning approaches may accelerate convergence and improve solution quality.

---

## 5. 结论

### 5.1 贡献总结

本文提出了语言赋能的动态边中心图网络（LE-DEGN），一种面向混合单向/双向城市网络中动态街景车路径优化的新型架构。主要贡献包括三个方面：

首先，我们引入了边中心路由基础模型（ERFM），将原始路图转换为线图，并采用惩罚偏置多头自注意力编码13维边特征。这种边中心视角从根本上将混合中国邮路问题重新表述为边上的节点排序任务，使Transformer架构能够直接建模边间转移成本。

其次，我们提出了时空注意力动态图波网络（SA-DGWN），通过扩张因果卷积和图卷积主动预测拥堵传播。通过在拥堵影响计划路线之前预测高风险路段，SA-DGWN实现了主动重新规划而非被动逃逸。

第三，我们设计了语言驱动启发式中心（LHH），通过生成-评分-执行-自反思（GSES）循环在五种互补启发式策略中自适应选择。反思机制基于滚动性能窗口持续更新启发式偏好，实现对当前网络条件的快速适应。

### 5.2 关键发现

在40至100个节点的合成城市网络上进行的大量实验表明，LE-DEGN相比具有DHAN风格拥堵处理的强贪婪最近邻基线实现了持续且统计显著的性能改进。系统在所有测试规模上实现了平均12.1%的总成本降低，在80节点网络中峰值改进达到16.3%。AOCC指标证实了向高质量解决方案的更快收敛，性能差距从40节点时的22.9%扩大到100节点时的33.9%。

消融研究揭示了三个模块的协同本质：单独的ERFM不足以应对动态环境（AOCC = 0.0000），而完整系统达到AOCC = 0.5387。LHH通过智能逃逸处理贡献了52.2%的成本降低，SA-DGWN通过主动拥堵预测提供了额外的18.3%改进。执行时间保持实用水平（0.82-2.49秒），且近乎线性缩放，证实了LE-DEGN对实时城市路由应用的适用性。

### 5.3 局限性与未来工作

当前工作的若干局限性指明了未来研究方向。首先，实验在合成生成的道路网络上进行；在OpenStreetMap等真实世界城市数据集上的验证将增强实际适用性声明。其次，SA-DGWN模块在合成交通模式上训练；与真实历史交通数据的集成将提高预测准确性。第三，当前系统处理单车场景；将LE-DEGN扩展到多车协同路由场景是一个有前景的方向。第四，LHH中的语言组件目前作为结构化状态言语化而非自然语言运行；与大型语言模型进行更深层次的集成以生成启发式可能解锁更复杂的自适应行为。最后，ERFM训练使用REINFORCE，其方差较高；探索具有更稳定优势估计的Actor-Critic方法或基于Transformer的强化学习方法可能加速收敛并提高解决方案质量。
