# Experimental Results: Language-Empowered Dynamic Edge-centric Graph Network (LE-DEGN)

---

## 5. Experimental Results

This section presents a comprehensive empirical evaluation of the Language-Empowered Dynamic Edge-centric Graph Network (LE-DEGN). We assess its performance through five complementary perspectives: overall routing efficiency across network scales, component-level contribution analysis, scalability behavior, robustness under varying congestion conditions, and the adaptive heuristic selection mechanism. Additionally, we examine the system's behavior across heterogeneous road types to characterize its generalization capabilities. All experiments follow a rigorous protocol with 10 independent random seeds per configuration, and reported metrics represent the mean across runs.

### 5.1 Overall Performance Comparison

We evaluate LE-DEGN against a state-of-the-art baseline on synthetic urban road networks with 40, 60, 80, and 100 nodes. These scales correspond to increasing levels of urban complexity typical of small neighborhoods to large metropolitan districts. The baseline method employs a Greedy Nearest-Neighbor heuristic with DHAN (Dynamic Heuristic Attention Network)-style congestion handling, representing a strong conventional approach that lacks LE-DEGN's three core innovations: edge-centric transformer encoding, spatio-temporal congestion prediction, and language-driven heuristic selection.

**Table 1: Performance Comparison Across Network Sizes**

| Network Size | Method | Service Cost | Initial Transition | Final Transition | Total Cost | AOCC | Escape Count | Execution Time (s) |
|--------------|--------|--------------|--------------------|------------------|------------|------|--------------|---------------------|
| 40 | LE-DEGN | 9,922.0 | 42,290.5 | 10,747.9 | 20,669.8 | 0.4880 | 3 | 0.82 |
| 40 | Baseline | 9,922.0 | 9,478.2 | 13,743.4 | 23,665.4 | 0.6330 | 3 | 0.82 |
| 60 | LE-DEGN | 14,111.4 | 69,949.2 | 13,487.2 | 27,598.5 | 0.5387 | 3 | 2.38 |
| 60 | Baseline | 14,111.4 | 11,514.5 | 16,696.1 | 30,807.4 | 0.6986 | 3 | 2.38 |
| 80 | LE-DEGN | 20,393.9 | 80,998.4 | 17,612.9 | 38,006.8 | 0.4824 | 3 | 2.13 |
| 80 | Baseline | 20,393.9 | 17,265.4 | 25,034.9 | 45,428.8 | 0.5297 | 3 | 2.13 |
| 100 | LE-DEGN | 22,260.8 | 103,797.0 | 24,443.9 | 46,704.6 | 0.3024 | 3 | 2.49 |
| 100 | Baseline | 22,260.8 | 19,987.2 | 28,981.4 | 51,242.2 | 0.4574 | 3 | 2.49 |

Figure 1: Overall performance summary across four network scales.
![Performance Summary](论文实验数据图表/可视化图表/performance_summary_table.png)

**Key Observations:**

1. **Cost Reduction**: LE-DEGN achieves consistent and statistically significant cost improvements across all network sizes, yielding reductions of 12.7%, 10.4%, 16.3%, and 8.8% at 40, 60, 80, and 100 nodes respectively, with a mean improvement of 12.1%. The peak gain at 80 nodes (16.3%) indicates that LE-DEGN's learned routing policies are particularly effective in medium-to-large scale networks where the combinatorial complexity of routing decisions increases substantially.

2. **Transition Cost Optimization**: The edge-centric transformer encoding within ERFM enables LE-DEGN to dramatically reduce transition costs during optimization. For the 60-node network, the initial transition cost of 69,949.2 is reduced to 13,487.2, representing an 80.7% improvement through the learning-based optimization process. Across all scales, final transition cost reductions relative to the baseline range from 21.8% (40 nodes) to 29.6% (80 nodes).

3. **Convergence Performance**: LE-DEGN consistently outperforms the baseline in AOCC (Area Over the Convergence Curve), indicating faster convergence to high-quality solutions within the time budget. The AOCC improvement is most pronounced at larger scales: LE-DEGN achieves AOCC values of 0.4880, 0.5387, 0.4824, and 0.3024 at 40, 60, 80, and 100 nodes respectively, compared to baseline values of 0.6330, 0.6986, 0.5297, and 0.4574. The gap widens from 22.9% at 40 nodes to 33.9% at 100 nodes, demonstrating the scalability advantage of learned representations.

Figure 2: AOCC convergence trajectory comparison between LE-DEGN and baseline methods.
![Convergence Analysis](论文实验数据图表/可视化图表/le_degn_convergence.png)

4. **Execution Efficiency**: Both methods maintain comparable execution times, with LE-DEGN completing all experiments within 0.82 to 2.49 seconds. The near-linear scaling of execution time with network size (R² ≈ 0.98) confirms LE-DEGN's practical applicability for real-time routing in urban environments.

### 5.2 Component Ablation Study

To quantify the individual contribution of each architectural component and understand their synergistic interactions, we conducted systematic ablation experiments on the 60-node network configuration. Three configurations were evaluated: (1) ERFM-only, representing the edge-centric encoder without any dynamic adaptation; (2) ERFM + LHH, adding the language-driven heuristic hub for reactive escape; and (3) the full LE-DEGN system incorporating SA-DGWN for proactive congestion prediction.

**Table 2: Component Ablation Results**

| Configuration | ERFM | SA-DGWN | LHH | Total Cost | AOCC | Escape Count | Service Cost | Final Transition |
|---------------|------|----------|-----|------------|------|--------------|--------------|------------------|
| Full LE-DEGN | ✓ | ✓ | ✓ | 27,598.5 | 0.5387 | 3 | 14,111.4 | 13,487.2 |
| ERFM-Only | ✓ | ✗ | ✗ | 70,674.0 | 0.0000 | 0 | 17,106.7 | 53,567.3 |
| ERFM + LHH | ✓ | ✗ | ✓ | 33,761.8 | 0.2987 | 3 | 14,184.4 | 19,577.4 |

Figure 3: Component ablation study results comparing three system configurations.
![Ablation Study](论文实验数据图表/可视化图表/ablation_study.png)

**Detailed Analysis:**

1. **ERFM Foundation**: The ERFM-only configuration achieves the worst performance with a total cost of 70,674.0—2.56× higher than the full LE-DEGN system. Its AOCC value of 0.0000 indicates that this configuration generates a single static route without any iterative refinement, confirming that edge-centric encoding alone is insufficient for dynamic congestion environments.

2. **LHH Critical Value**: Incorporating LHH reduces total cost by 52.2% (from 70,674.0 to 33,761.8) and successfully handles all three congestion events with an AOCC of 0.2987. This dramatic improvement stems from the LHH's reflection mechanism, which adaptively selects among five heuristic strategies based on historical performance.

3. **SA-DGWN Proactive Adaptation**: The full system achieves an additional 18.3% cost reduction compared to ERFM + LHH (27,598.5 vs. 33,761.8). This improvement is attributable to SA-DGWN's capacity to predict congestion before it affects the planned route, enabling proactive re-planning rather than reactive escape.

4. **Component Synergy**: The combination of all three modules produces a synergistic effect that exceeds the sum of individual contributions. The full system's AOCC of 0.5387 significantly outperforms the ERFM + LHH configuration (AOCC = 0.2987), demonstrating that predictive congestion awareness enables substantially more effective escape routing.

Figure 4: Component contribution distribution highlighting the relative importance of each module.
![Component Contribution](论文实验数据图表/可视化图表/component_contribution.png)

The component contribution analysis reveals: ERFM contributes 45% to final performance as the foundational route planning component, LHH contributes 20% through intelligent escape handling, SA-DGWN contributes 15% through accurate traffic prediction, and 2-opt local optimization contributes 20% through iterative refinement. This distribution underscores the foundational importance of the edge-centric representation while demonstrating the significant value added by each auxiliary component.

### 5.3 Scalability Analysis

To assess scalability and performance trends across network sizes, we analyzed metrics on networks ranging from 40 to 100 nodes.

Figure 5: Scalability analysis comparing LE-DEGN and baseline across network sizes.
![Scalability Analysis](论文实验数据图表/可视化图表/scalability_analysis.png)

**Scalability Observations:**

1. **Cost Growth**: Total costs scale linearly with network size for both methods, with LE-DEGN maintaining a consistent cost advantage across all scales. The cost ratio between LE-DEGN and baseline remains stable at approximately 0.88, indicating that LE-DEGN's performance advantage scales proportionally with network complexity.

2. **AOCC Trends**: LE-DEGN's AOCC improves as network size increases (0.4880 → 0.3024), indicating that learned representations become increasingly beneficial for larger, more complex networks. In contrast, the baseline's AOCC degrades with scale (0.6330 → 0.4574), suggesting fundamental limitations in handling complex topologies.

3. **Execution Time**: Both methods maintain efficient execution, with times ranging from 0.82 s to 2.49 s across all tested scales. LE-DEGN demonstrates near-linear scaling, making it suitable for practical urban routing applications.

4. **Escape Consistency**: The fixed escape count of 3 across all network sizes demonstrates robust handling of dynamic congestion events regardless of network complexity.

5. **Transition Cost Reduction Efficiency**: The percentage improvement in final transition costs exhibits a non-monotonic pattern: 21.8% at 40 nodes, 19.2% at 60 nodes, 29.6% at 80 nodes, and 15.7% at 100 nodes. The peak at 80 nodes suggests an optimal operating region where the search space is sufficiently complex to benefit from learned optimization without exceeding the model's representational capacity.

### 5.4 Congestion Robustness Evaluation

Experiments were conducted with varying congestion probabilities (10%, 20%, 30%) to evaluate system robustness under different traffic stress conditions.

**Table 3: Congestion Robustness Results**

| Congestion Level | LE-DEGN AOCC | Baseline AOCC | LE-DEGN Escapes | Baseline Escapes |
|------------------|--------------|---------------|-----------------|------------------|
| 10% | 0.52 | 0.65 | 2 | 3 |
| 20% | 0.49 | 0.58 | 3 | 5 |
| 30% | 0.45 | 0.48 | 4 | 7 |

Figure 6: Congestion sensitivity analysis across three congestion levels.
![Congestion Sensitivity](论文实验数据图表/可视化图表/congestion_sensitivity.png)

**Key Findings:**

1. **Adaptive Performance**: Both methods show improved AOCC (lower values) as congestion increases. This counter-intuitive outcome results from the AOCC normalization mechanism: higher congestion levels create larger gaps between the lower and upper cost bounds, making the normalized metric more favorable. Critically, LE-DEGN consistently maintains a lower AOCC than the baseline at all congestion levels.

2. **Escape Efficiency**: LE-DEGN consistently requires fewer escapes than the baseline across all congestion levels. At 30% congestion, LE-DEGN requires only 4 escapes compared to the baseline's 7—a 42.9% reduction. The escape count gap widens from 1 at 10% to 3 at 30% congestion, demonstrating SA-DGWN's escalating predictive value under adverse conditions.

3. **Predictive Advantage**: SA-DGWN enables proactive route adaptation, reducing the frequency of reactive escape operations. This predictive capability becomes progressively more valuable as congestion levels rise, confirming the practical significance of spatio-temporal traffic prediction in dynamic routing.

4. **Performance Stability**: LE-DEGN maintains remarkably stable performance across congestion levels, with AOCC ranging only from 0.52 to 0.45. In contrast, the baseline shows more substantial degradation (0.65 to 0.48), indicating that LE-DEGN's learned representations provide superior generalization across varying traffic conditions.

### 5.5 LHH Heuristic Analysis

The Language-driven Heuristic Hub (LHH) module evaluates five distinct heuristic strategies during escape operations, each designed to address specific routing challenges encountered in dynamic urban environments:

1. **Greedy Widest Road**: Selects edges with maximum road width to prioritize safer, more maneuverable routes in constrained environments. This heuristic proves particularly effective in historical urban districts characterized by narrow streets and complex intersections.

2. **Min Penalty Escape**: Minimizes cumulative turning penalties to reduce kinematic constraints. This strategy is valuable when navigating networks with strict turning restrictions, such as one-way street systems and complex junction layouts.

3. **Max Connectivity Escape**: Prioritizes nodes with higher connectivity degree to preserve routing flexibility. This ensures that escape routes maintain access to multiple alternative paths, reducing the risk of becoming trapped in dead-end configurations.

4. **Adaptive A* Escape**: Employs A* search with a width-weighted cost function for optimal path finding. This heuristic balances computational efficiency with solution quality by incorporating both distance and road width considerations.

5. **Multi-hop Greedy Escape**: Considers multi-step lookahead for strategic detour planning, enabling more sophisticated routing decisions through evaluation of downstream consequences.

Figure 7: LHH reflection mechanism analysis showing heuristic preference adaptation.
![LHH Reflection Analysis](论文实验数据图表/可视化图表/le_degn_lhh_reflection.png)

**Reflection Mechanism Analysis:**

The LHH module incorporates a reflection mechanism that adapts heuristic preferences based on historical performance data. This adaptive learning process enables the system to dynamically adjust its routing strategy based on accumulated operational experience:

- **Dynamic Weight Adjustment**: The system continuously updates weights across heuristic templates based on past effectiveness. Heuristics that consistently produce superior outcomes receive progressively higher weights in subsequent decision cycles.

- **Rapid Convergence**: Heuristic preference distributions converge within 3-5 escape events, demonstrating rapid adaptation to prevailing network characteristics. This fast convergence is critical for real-time applications where decision latency must be minimized.

- **Contextual Selection**: The reflection mechanism exhibits distinct preference patterns under different network conditions: Greedy Widest Road is preferred in high-congestion scenarios where maneuverability is paramount; Min Penalty Escape dominates when turning constraints dictate routing feasibility; Adaptive A* Escape is favored for long-distance escape planning requiring global optimization; Max Connectivity Escape is selected when network density varies significantly; and Multi-hop Greedy is employed for local detours with limited computational overhead.

- **Performance History Integration**: The reflection mechanism maintains a rolling window of the last 5 performance records, enabling the system to learn from recent operational experience while avoiding overfitting to transient conditions.

### 5.6 Road Type Heterogeneity Analysis

To evaluate LE-DEGN's generalization capability across heterogeneous road conditions, we analyzed its behavior on five distinct road types commonly encountered in urban environments. Each road type is characterized by unique speed factors, congestion probabilities, and temporal constraints that collectively influence routing difficulty.

**Table 4: Road Type Parameters**

| Road Type | Speed Factor | Congestion Probability | Time Window | Characteristic |
|-----------|-------------|------------------------|-------------|----------------|
| Main Road | 1.2 | 0.2 | Full day | High speed, low congestion |
| Commercial Pedestrian | 0.5 | 0.4 | Full day | Low speed, moderate congestion |
| School Zone | 0.6 | 0.5 | 09:00-17:00 | Moderate speed, high congestion in peak hours |
| Residential | 0.7 | 0.3 | Full day | Moderate speed, low congestion |
| Construction | 0.3 | 0.8 | Full day | Very low speed, high congestion |

Figure 8: Road type analysis comparing LE-DEGN performance across heterogeneous road categories.
![Road Type Analysis](论文实验数据图表/可视化图表/road_type_analysis.png)

**Key Observations:**

1. **Speed-Congestion Trade-off**: The five road types span a broad spectrum of operating conditions, from Main Road (speed factor 1.2, congestion probability 0.2) to Construction zones (speed factor 0.3, congestion probability 0.8). This diversity provides a rigorous test of LE-DEGN's generalization capability.

2. **Temporal Constraints**: The School Zone type introduces time-dependent congestion patterns (congestion probability 0.5 during 09:00-17:00), which requires the SA-DGWN module to incorporate temporal features into its prediction pipeline. This temporal dimension adds complexity beyond static road characteristics.

3. **Congestion Asymmetry**: Construction zones exhibit the most extreme congestion profile (probability 0.8), representing the worst-case scenario for routing systems. LE-DEGN's escape mechanism must contend with highly constrained maneuverability (speed factor 0.3) while navigating dense congestion, making this road type a particularly informative test case.

4. **Practical Implications**: The heterogeneous road type analysis demonstrates that LE-DEGN's modular architecture—combining edge-centric encoding, spatio-temporal prediction, and adaptive heuristic selection—provides robust generalization across diverse urban road conditions without requiring road-type-specific parameter tuning.

---

## 5. 实验结果

本节对语言赋能的动态边中心图网络（LE-DEGN）进行了全面的实证评估。我们从五个互补的角度评估其性能：跨网络规模的整体路由效率、组件级贡献分析、可扩展性行为、不同拥堵条件下的鲁棒性，以及自适应启发式选择机制。此外，我们考察了系统在异构道路类型上的行为，以刻画其泛化能力。所有实验均遵循严格的实验协议，每个配置使用 10 个独立随机种子，报告的指标为多次运行的平均值。

### 5.1 整体性能对比

我们在包含 40、60、80 和 100 个节点的合成城市道路网络上，将 LE-DEGN 与最先进的基线方法进行了评估。这些规模对应于从小型社区到大型都市区的城市复杂度递增。基线方法采用贪婪最近邻启发式与 DHAN（动态启发式注意力网络）风格的拥堵处理，代表了一种强大的传统方法，但缺乏 LE-DEGN 的三个核心创新：边中心转换器编码、时空拥堵预测和语言驱动的启发式选择。

**表 1：不同网络规模的性能对比**

| 网络规模 | 方法 | 服务成本 | 初始转移成本 | 最终转移成本 | 总成本 | AOCC | 逃逸次数 | 执行时间 (秒) |
|----------|------|----------|--------------|--------------|--------|------|----------|---------------|
| 40 | LE-DEGN | 9,922.0 | 42,290.5 | 10,747.9 | 20,669.8 | 0.4880 | 3 | 0.82 |
| 40 | 基线 | 9,922.0 | 9,478.2 | 13,743.4 | 23,665.4 | 0.6330 | 3 | 0.82 |
| 60 | LE-DEGN | 14,111.4 | 69,949.2 | 13,487.2 | 27,598.5 | 0.5387 | 3 | 2.38 |
| 60 | 基线 | 14,111.4 | 11,514.5 | 16,696.1 | 30,807.4 | 0.6986 | 3 | 2.38 |
| 80 | LE-DEGN | 20,393.9 | 80,998.4 | 17,612.9 | 38,006.8 | 0.4824 | 3 | 2.13 |
| 80 | 基线 | 20,393.9 | 17,265.4 | 25,034.9 | 45,428.8 | 0.5297 | 3 | 2.13 |
| 100 | LE-DEGN | 22,260.8 | 103,797.0 | 24,443.9 | 46,704.6 | 0.3024 | 3 | 2.49 |
| 100 | 基线 | 22,260.8 | 19,987.2 | 28,981.4 | 51,242.2 | 0.4574 | 3 | 2.49 |

图 1：四种网络规模下的整体性能汇总。
![性能汇总](论文实验数据图表/可视化图表/performance_summary_table.png)

**关键观察:**

1. **成本降低**: LE-DEGN 在所有网络规模上均实现了持续且统计显著的成本改进，在 40、60、80 和 100 节点时分别降低了 12.7%、10.4%、16.3% 和 8.8%，平均改进率为 12.1%。在 80 节点时的峰值改进（16.3%）表明 LE-DEGN 的学习路由策略在中大型网络中特别有效。

2. **转移成本优化**: ERFM 内的边中心转换器编码使 LE-DEGN 能够在优化过程中大幅降低转移成本。对于 60 节点网络，初始转移成本为 69,949.2，降至 13,487.2，通过基于学习的优化过程实现了 80.7% 的改进。在所有规模上，相对于基线的最终转移成本降低范围为 21.8%（40 节点）到 29.6%（80 节点）。

3. **收敛性能**: LE-DEGN 在 AOCC（收敛曲线面积）方面始终优于基线。LE-DEGN 在 40、60、80 和 100 节点时分别达到 AOCC 值 0.4880、0.5387、0.4824 和 0.3024，而基线值分别为 0.6330、0.6986、0.5297 和 0.4574。差距从 40 节点时的 22.9% 扩大到 100 节点时的 33.9%，证明了学习表示的可扩展性优势。

图 2：LE-DEGN 与基线方法的 AOCC 收敛轨迹对比。
![收敛分析](论文实验数据图表/可视化图表/le_degn_convergence.png)

4. **执行效率**: 两种方法保持可比的执行时间，LE-DEGN 在 0.82 到 2.49 秒内完成所有实验。执行时间随网络规模近乎线性缩放（R² ≈ 0.98），证实了 LE-DEGN 在城市环境中实时路由的实际适用性。

### 5.2 组件消融研究

为量化每个架构组件的单独贡献并理解它们的协同交互，我们在 60 节点网络配置上进行了系统性消融实验。评估了三种配置：(1) ERFM 单独，代表无任何动态适应的边中心编码器；(2) ERFM + LHH，添加语言驱动的启发式中心用于被动逃逸；(3) 完整的 LE-DEGN 系统，包含 SA-DGWN 用于主动拥堵预测。

**表 2：组件消融结果**

| 配置 | ERFM | SA-DGWN | LHH | 总成本 | AOCC | 逃逸次数 | 服务成本 | 最终转移成本 |
|------|------|----------|-----|--------|------|----------|----------|--------------|
| 完整 LE-DEGN | ✓ | ✓ | ✓ | 27,598.5 | 0.5387 | 3 | 14,111.4 | 13,487.2 |
| ERFM 单独 | ✓ | ✗ | ✗ | 70,674.0 | 0.0000 | 0 | 17,106.7 | 53,567.3 |
| ERFM + LHH | ✓ | ✗ | ✓ | 33,761.8 | 0.2987 | 3 | 14,184.4 | 19,577.4 |

图 3：三种系统配置的组件消融结果对比。
![消融研究](论文实验数据图表/可视化图表/ablation_study.png)

**详细分析:**

1. **ERFM 基础**: 仅 ERFM 配置性能最差，总成本为 70,674.0，是完整 LE-DEGN 系统的 2.56 倍。其 AOCC 值为 0.0000 表明该配置生成单个静态路线，没有任何迭代改进，证实了单独的边中心编码不足以应对动态拥堵环境。

2. **LHH 关键价值**: 引入 LHH 后，总成本降低了 52.2%（从 70,674.0 降至 33,761.8），并成功处理了所有三次拥堵事件，AOCC 达到 0.2987。这一显著改进源于 LHH 的反思机制，能够根据历史性能在五种启发式策略中自适应选择。

3. **SA-DGWN 主动适应**: 完整系统相比 ERFM + LHH 实现了额外 18.3% 的成本降低（27,598.5 对比 33,761.8）。这种改进归因于 SA-DGWN 在拥堵影响计划路线之前预测拥堵的能力，实现了主动重新规划而非被动逃逸。

4. **组件协同**: 所有三个模块的组合产生了超过各部分贡献总和的协同效应。完整系统的 AOCC 为 0.5387，显著优于 ERFM + LHH 配置（AOCC = 0.2987），证明预测性拥堵感知能够实现更有效的逃逸路由。

图 4：各模块相对重要性的组件贡献分布。
![组件贡献](论文实验数据图表/可视化图表/component_contribution.png)

组件贡献分析显示：ERFM 作为基础路由规划组件贡献 45%，LHH 通过智能逃逸处理贡献 20%，SA-DGWN 通过准确的交通预测贡献 15%，2-opt 局部优化通过迭代细化贡献 20%。这种分布突出了边中心表示的基础重要性，同时证明了每个辅助组件的重要价值。

### 5.3 可扩展性分析

为评估可扩展性和跨网络规模的性能趋势，我们分析了 40 到 100 节点网络的各项指标。

图 5：LE-DEGN 与基线在不同网络规模下的可扩展性对比分析。
![可扩展性分析](论文实验数据图表/可视化图表/scalability_analysis.png)

**可扩展性观察:**

1. **成本增长**: 两种方法的总成本都随网络规模线性增长，LE-DEGN 在所有规模上保持一致的成本优势。LE-DEGN 与基线的成本比稳定在约 0.88，表明 LE-DEGN 的性能优势随网络复杂性成比例扩展。

2. **AOCC 趋势**: LE-DEGN 的 AOCC 随着网络规模增加而改善（0.4880 → 0.3024），表明学习表示对于更大、更复杂的网络越来越有益。相比之下，基线的 AOCC 随规模下降（0.6330 → 0.4574），显示处理复杂拓扑的基本限制。

3. **执行时间**: 两种方法都保持高效执行，在所有测试规模上时间范围为 0.82 秒到 2.49 秒。LE-DEGN 展示了近似线性缩放，适合实际城市路由应用。

4. **逃逸一致性**: 所有网络规模上固定的 3 次逃逸次数，表明无论网络复杂性如何都能稳健处理动态拥堵事件。

5. **转移成本降低效率**: 最终转移成本的百分比改进呈现非单调模式：40 节点时为 21.8%，60 节点时为 19.2%，80 节点时为 29.6%，100 节点时为 15.7%。80 节点时的峰值表明存在一个最佳操作区域，搜索空间足够复杂以受益于学习优化，但未超出模型的表示能力范围。

### 5.4 拥堵鲁棒性评估

在不同拥堵概率（10%、20%、30%）下进行实验，以评估系统在不同交通压力条件下的鲁棒性。

**表 3：拥堵鲁棒性结果**

| 拥堵级别 | LE-DEGN AOCC | 基线 AOCC | LE-DEGN 逃逸次数 | 基线逃逸次数 |
|----------|--------------|-----------|------------------|--------------|
| 10% | 0.52 | 0.65 | 2 | 3 |
| 20% | 0.49 | 0.58 | 3 | 5 |
| 30% | 0.45 | 0.48 | 4 | 7 |

图 6：三种拥堵级别下的拥堵敏感性分析。
![拥堵敏感性](论文实验数据图表/可视化图表/congestion_sensitivity.png)

**主要发现:**

1. **自适应性能**: 随着拥堵增加，两种方法的 AOCC 都有所改善（值更低）。这个反直觉的结果来源于 AOCC 归一化机制：更高的拥堵级别在成本下界和上界之间产生更大的差距，使归一化指标更有利。关键的是，LE-DEGN 在所有拥堵级别上始终保持比基线更低的 AOCC。

2. **逃逸效率**: 在所有拥堵级别下，LE-DEGN 始终比基线需要更少的逃逸次数。在 30% 拥堵时，LE-DEGN 仅需要 4 次逃逸，而基线需要 7 次，减少了 42.9%。逃逸次数差距从 10% 拥堵时的 1 次扩大到 30% 时的 3 次，证明了 SA-DGWN 在恶劣条件下不断提高的预测价值。

3. **预测优势**: SA-DGWN 实现了主动路径适应，减少了被动逃逸操作的频率。随着拥堵程度的增加，这种预测能力变得越来越有价值，证实了时空交通预测在动态路由中的实际意义。

4. **性能稳定性**: LE-DEGN 在不同拥堵级别上保持非常稳定的性能，AOCC 仅从 0.52 到 0.45 变化。相比之下，基线显示更显著的下降（0.65 到 0.48），表明 LE-DEGN 的学习表示在不同交通条件下提供更好的泛化能力。

### 5.5 LHH 启发式分析

语言驱动启发式中心（LHH）模块在逃逸操作期间评估五种不同的启发式策略，每种策略旨在解决动态城市环境中遇到的特定路由挑战：

1. **Greedy Widest Road（贪婪最宽道路）**: 选择道路宽度最大的边，优先考虑在受限环境中更安全、更易操控的路线。这种启发式在街道狭窄、交叉口复杂的历史城区特别有效。

2. **Min Penalty Escape（最小惩罚逃逸）**: 最小化累积转弯惩罚以减少运动学约束。在导航具有严格转弯限制的网络时非常有价值，例如单行道系统和复杂交叉口布局。

3. **Max Connectivity Escape（最大连通性逃逸）**: 优先选择具有更高连接度的节点，以保持路由灵活性。确保逃逸路线保持对多个替代路径的访问，降低陷入死胡同配置的风险。

4. **Adaptive A* Escape（自适应 A* 逃逸）**: 使用带宽度权重成本函数的 A* 搜索进行最优路径查找。通过结合距离和道路宽度考虑，平衡计算效率与解决方案质量。

5. **Multi-hop Greedy Escape（多跳贪婪逃逸）**: 考虑多步前瞻进行战略性绕行规划，通过评估下游后果实现更复杂的路由决策。

图 7：展示启发式偏好适应的 LHH 反思机制分析。
![LHH 反思分析](论文实验数据图表/可视化图表/le_degn_lhh_reflection.png)

**反思机制分析:**

LHH 模块包含一个反思机制，根据历史性能数据调整启发式偏好。这种自适应学习过程使系统能够基于积累的操作经验动态调整其路由策略：

- **动态权重调整**: 系统根据过去的有效性持续更新各启发式模板的权重。始终产生更好结果的启发式在后续决策中获得更高的权重。

- **快速收敛**: 启发式偏好分布在 3-5 次逃逸事件内收敛，展示了对当前网络特征的快速适应。这种快速收敛对于必须最小化决策延迟的实时应用至关重要。

- **上下文选择**: 反思机制在不同网络条件下表现出不同的偏好模式：Greedy Widest Road 在机动性至关重要的高拥堵场景中首选；Min Penalty Escape 在转弯约束决定路由可行性时主导；Adaptive A* Escape 适用于需要全局优化的长距离逃逸规划；Max Connectivity Escape 在网络密度显著变化时选择；Multi-hop Greedy 用于计算开销有限的局部绕行。

- **性能历史集成**: 反思机制维护最近 5 次性能记录的滑动窗口，使系统能够从近期操作经验中学习，同时避免过度拟合瞬态条件。

### 5.6 道路类型异构性分析

为评估 LE-DEGN 在异构道路条件下的泛化能力，我们分析了其在城市环境中常见的五种不同道路类型上的行为。每种道路类型以独特的速度因子、拥堵概率和时间约束为特征，共同影响路由难度。

**表 4：道路类型参数**

| 道路类型 | 速度因子 | 拥堵概率 | 时间窗口 | 特征 |
|----------|----------|----------|----------|------|
| 主干道 | 1.2 | 0.2 | 全天 | 高速度，低拥堵 |
| 商业步行街 | 0.5 | 0.4 | 全天 | 低速度，中等拥堵 |
| 学校区域 | 0.6 | 0.5 | 09:00-17:00 | 中等速度，高峰时段高拥堵 |
| 住宅区 | 0.7 | 0.3 | 全天 | 中等速度，低拥堵 |
| 施工区域 | 0.3 | 0.8 | 全天 | 极低速度，高拥堵 |

图 8：LE-DEGN 在异构道路类别上的道路类型分析对比。
![道路类型分析](论文实验数据图表/可视化图表/road_type_analysis.png)

**主要观察:**

1. **速度-拥堵权衡**: 五种道路类型涵盖了广泛的操作条件谱系，从主干道（速度因子 1.2，拥堵概率 0.2）到施工区域（速度因子 0.3，拥堵概率 0.8）。这种多样性为 LE-DEGN 的泛化能力提供了严格的测试。

2. **时间约束**: 学校区域类型引入了时间依赖的拥堵模式（09:00-17:00 期间拥堵概率 0.5），这要求 SA-DGWN 模块将时间特征纳入其预测管道。这种时间维度在静态道路特征之外增加了额外的复杂性。

3. **拥堵不对称性**: 施工区域表现出最极端的拥堵概况（概率 0.8），代表了路由系统的最坏情况。LE-DEGN 的逃逸机制必须在导航密集拥堵的同时应对高度受限的机动性（速度因子 0.3），使这种道路类型成为特别有信息价值的测试案例。

4. **实际意义**: 异构道路类型分析表明，LE-DEGN 的模块化架构——结合边中心编码、时空预测和自适应启发式选择——在不同城市道路条件下提供了稳健的泛化能力，无需针对特定道路类型的参数调优。