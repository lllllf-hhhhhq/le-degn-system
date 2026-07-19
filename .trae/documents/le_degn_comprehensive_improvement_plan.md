# LE-DEGN 全面改进计划

## 1. 摘要

基于对代码的深度分析，发现三层次问题：(1) 消融实验设计存在逻辑缺陷——三个配置使用了不同的初始化策略；(2) 代码架构耦合度高——36个类集中在单文件2000+行，消融实验独立重写逻辑；(3) 算法有可优化空间。本计划提出体系化的修复、重构、优化与验证方案。

## 2. 当前状态分析

### 2.1 已完成的工作（此前会话）

| 提交 | 内容 |
|------|------|
| `345d7c0` | 初始代码库推送 |
| `b90650c` | 三项修复：消融共享路网、Baseline真实验逃逸、贪心NN起点 |
| `eea89c0` | 新增 `real_data_loader.py` |
| `6f27c3a` | 工作流总结报告 |
| `9c541e3` | 修复后消融实验结果 + Nominatim绕过 |

### 2.2 当前代码缺陷（深度分析发现）

#### 缺陷 1：消融实验初始化策略不一致（严重）

`ablation_study.py` 中三个配置使用了不同的初始化策略：

| 配置 | 初始化方式 | init_transition | 问题 |
|------|-----------|----------------|------|
| Full LE-DEGN | 贪心最近邻（`execute_dynamic` Phase 1） | 12,614 | 正确 |
| ERFM-only | ERFM argmax 解码（温度0.3） | 41,438 | 错误——应从相同起点出发 |
| ERFM+LHH | ERFM 随机采样解码（`plan_global_route`，温度0.5） | 68,294 | 错误——应从相同起点出发 |

核心问题：ERFM+LHH 的 init_transition（68,294）到 final_transition（14,136）下降80%，但这80%不是 LHH 的贡献，而是 2-opt 优化了 ERFM 随机产生的极差路径。Full LE-DEGN 从贪心NN出发只有6.6%的优化空间。两个无法对比。

#### 缺陷 2：消融实验缺配置

缺少 **ERFM + SA-DGWN（无 LHH）** 配置。当前消融无法区分 SA-DGWN 主动预测和 LHH 被动逃逸的独立贡献——只能看到 ERFM+LHH vs Full 的差异，但不知道 SA-DGWN 单独贡献多少。

#### 缺陷 3：消融代码重复实现路由逻辑

`run_erfm_only()` 和 `run_erfm_with_lhh()` 各自重写了路径规划、逃逸处理、2-opt 优化逻辑（共 200+ 行），而不是调用 `LEDEGNSystem.execute_dynamic()`。当 `execute_dynamic` 被修复后，消融函数仍是旧逻辑。

#### 缺陷 4：单文件代码架构

`le_degn_system.py` 约 2100 行，包含 36 个类/函数。Section 划分虽然清晰，但所有模块耦合在一个文件中，不利于：
- 单元测试
- 独立验证各组件正确性
- 后续扩展到真实数据

### 2.3 当前数据可信度评估

| 指标 | 可信度 | 原因 |
|------|--------|------|
| Service Cost | 高 | 消融间已一致（14,111），路网共享修复生效 |
| ERFM-only vs Full | 低 | 初始化策略不同，无法直接对比 |
| LHH 贡献度 | 低 | ERFM+LHH 初始值因随机解码虚高 |
| SA-DGWN 贡献度 | 无法评估 | 缺独立消融配置 |
| Baseline vs LE-DEGN | 中 | Baseline 逃逸修复后更公平，但初始贪心NN可能使LE-DEGN优化空间过窄 |

## 3. 修改方案

### 3.1 模块 A：消融实验重构（修复数据可信度）

**目标**：所有消融配置使用统一接口，每个配置从相同的贪心NN基线出发。

**修改文件**：`ablation_study.py`

**具体变更**：

1. **提取共享的初始贪心NN逻辑为独立函数**：
   ```python
   def compute_greedy_nn_tour(lg, seed=None):
       """所有消融配置共用此函数获取初始路径"""
       TC = lg.transition_cost
       N = lg.num_line_nodes()
       available = list(range(N))
       # ... 多起点贪心NN
       return best_tour, best_trans
   ```

2. **重写 `run_erfm_only()`**：从贪心NN出发 → ERFM 编码后用贪心NN路径作为初始解 → 返回结果（不再用 ERFM argmax 解码从头构建）

3. **重写 `run_erfm_with_lhh()`**：从贪心NN出发 → 用 `LEDEGNSystem` 但禁用 SA-DGWN → 统一调用 execute_dynamic 的改造版

4. **新增 `run_erfm_with_sadgwn()`**（ERFM + SA-DGWN，无 LHH）：
   - 从贪心NN出发
   - SA-DGWN 预测拥堵，触发重规划（ERFM `plan_global_route`）
   - 但无 LHH 逃逸——拥堵时仅 ERFM 重规划

5. **所有配置统一输出**：
   ```python
   result = {
       'init_transition': nn_trans,  # 相同的贪心NN基线
       'final_transition': ...,
       'final_cost': ...,
       'aocc': ...,
       'escape_count': ...,
       'replan_count': ...,
       'service_cost': ...
   }
   ```

**验证标准**：
- 四个配置的 `init_transition` 和 `service_cost` 完全一致
- Full LE-DEGN > ERFM+LHH > ERFM+SA-DGWN > ERFM-only（总成本递增），且差异合理

### 3.2 模块 B：代码架构重组

**目标**：将 `le_degn_system.py` 拆分为模块化结构，层次分明。

**新文件结构**：

```
le_degn_system/
├── __init__.py           # 统一导出接口
├── core/
│   ├── __init__.py
│   ├── metrics.py        # PerformanceTracker, calculate_aocc
│   └── config.py         # 默认超参数配置
├── environment/
│   ├── __init__.py
│   ├── road_network.py   # RoadNetworkEnv（从 le_degn_system.py Section 1 提取）
│   └── line_graph.py     # LineGraphBuilder（Section 2）
├── models/
│   ├── __init__.py
│   ├── erfm.py           # PenaltyBiasMHA, EdgeTransformerBlock, ERFM, ERFMTrainer（Section 3+6）
│   ├── sadgwn.py         # DilatedCausalConv, GraphConv, STBlock, SADGWN, TrafficDataGen（Section 4）
│   └── lhh.py            # HeuristicCandidate, StateVerbalizer, TemplateLibrary, GSESLoop, LHHEngine（Section 5）
├── pipeline/
│   ├── __init__.py
│   ├── system.py         # LEDEGNSystem（Section 7）
│   └── baseline.py       # BaselineDHAN（Section 8）
├── visualization/
│   ├── __init__.py
│   └── viz.py            # Visualizer（Section 9）
├── main.py               # main() 入口
└── ablation.py           # 消融实验（从 ablation_study.py 迁移）
```

**拆分规则**：
- 每个模块不超过 300 行
- 公共工具（PerformanceTracker, calculate_aocc）放 `core/`
- 每个模型组件独立一个文件
- `LEDEGNSystem` 和 `BaselineDHAN` 组成 `pipeline/`
- 保持现有 Section 注释作为文件头部说明

**不变部分**：
- 所有类名、方法签名保持不变
- 所有默认参数值保持不变
- Import 路径调整但语义不变

### 3.3 模块 C：算法优化提议（若经分析可行则实现）

以下优化提议需在重构后逐一验证，不盲目实现：

#### 优化 1：ERFM 在贪心NN基础上的强化学习优化

**当前问题**：Phase 1 现在直接用贪心NN，ERFM 的角色被弱化。  
**提议**：在贪心NN路径上，用 ERFM 的 REINFORCE 策略做局部改进——对路径中相邻 k 条边用 ERFM 采样替代，若转移成本降低则接受。  
**验证**：对比 "贪心NN基线" vs "贪心NN + ERFM局部优化"，确保 ERFM 有正向贡献。

#### 优化 2：自适应温度调度

**当前问题**：ERFM 训练和推理的 temperature 退火是线性的（1.5→0.2），没有根据优化进度动态调整。  
**提议**：在 ERFM 训练中引入基于 cost 改善率的自适应温度——若连续 N 个 episode 无改善，升高温度增加探索；若持续改善，降低温度加速收敛。  
**验证**：对比固定退火 vs 自适应退火在相同 episode 数下的最优解质量。

#### 优化 3：SA-DGWN 预测阈值自适应

**当前问题**：SA-DGWN 预测阈值固定为 0.5（`le_degn_system.py` L1288）。  
**提议**：根据历史误报/漏报率动态调整阈值，使 F1 分数最大化。  
**验证**：在相同拥堵序列下，对比固定阈值 vs 自适应阈值的逃逸次数和总成本。

### 3.4 模块 D：严谨验证工作流

**验证流程每步独立运行，发现问题则回退修复后重跑**：

#### V1：消融合规性验证
运行 `python -m le_degn_system.ablation`，检查：
- 所有配置 init_transition 完全相等（误差 < 1e-6）
- 所有配置 service_cost 完全相等
- 总成本严格递增：Full < ERFM+LHH < ERFM+SA-DGWN < ERFM-only

#### V2：Baseline 公平性验证
运行 `python -m le_degn_system.main --nodes 60 --time_limit 30`，确认：
- LE-DEGN 和 Baseline 的 init_transition 差距 < 20%
- LE-DEGN 改善幅度应在 5-15% 范围（不再出现 30%+ 的虚高改善）

#### V3：组件贡献一致性验证
- ERFM 贡献 = (ERFM+LHH - Full) / (ERFM-only - Full) * 100%
- SA-DGWN 贡献 = (ERFM+LHH - Full) / (ERFM+LHH - ERFM+SA-DGWN) * 100%
- LHH 贡献 = (ERFM+SA-DGWN - Full) / (ERFM+SA-DGWN - ERFM+LHH) * 100%
- 三项贡献之和应在 100% ± 15% 范围内（允许非线性交互）

#### V4：真实路网集成验证
```bash
python -c "
from real_data_loader import RealRoadNetworkLoader
loader = RealRoadNetworkLoader(city='Shanghai, China', radius=3000)
loader.print_statistics()
# 验证：节点数 > 500, 边数 > 1000, 单向边占比 40-60%
"
```

### 3.5 模块 E：CodeRabbit 审查 + PR 提交流程

1. 重构完成后，运行 CodeRabbit：
   ```bash
   coderabbit review --agent
   ```
2. 根据审查结果逐一修复
3. 用 `gh-address-comments` Skill 处理审查意见
4. 推送到 GitHub，创建 Draft PR，标题：
   `[codex] LE-DEGN 消融实验修复 + 架构重构 + 性能优化`
5. PR 正文包括：变更说明、数据对比（修复前后）、验证结果

## 4. 需要你手动操作的步骤

| 步骤 | 操作 | 触发时机 |
|------|------|----------|
| M1 | GitHub 推送：`git push origin master` | 每次 commit 后（GitHub 恢复后） |
| M2 | CodeRabbit 登录：`coderabbit auth login --agent` | 模块E开始时（CLI可能需要先安装） |
| M3 | 滴滴GAIA申请：访问 gaia.didichuxing.com 提交学术申请 | 真实数据集成阶段 |

## 5. 风险与回退策略

| 风险 | 回退 |
|------|------|
| 架构拆分引入 import 循环 | 保留 `core/` 为所有模块的无依赖底层 |
| 消融实验重构后 Full LE-DEGN 不如 ERFM+LHH（违反直觉） | 检查 SA-DGWN 训练是否收敛；若确认无误，接受此发现在论文中讨论 |
| 优化提议引入新 Bug | 每个优化在独立分支实现，确认后再合并 |
