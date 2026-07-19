# LE-DEGN 算法设计章节重写 Spec

## Why
现有算法设计文档过于简略，存在两个严重问题：
1. **未覆盖代码全部模块**：文档写到3.7就说"代码在232行截断"结束了，但实际代码有2104行，包含ERFM训练器、SA-DGWN、LHH引擎、LEDEGNSystem集成系统、BaselineDHAN对比方法等核心模块全未涉及
2. **DHAN突然出现**：实验结果部分引用了"DHAN baseline"，但算法设计章节完全没有定义和解释这个方法，审稿人无法理解

## What Changes
- 重写 `gemini-export-街景车路径优化算法设计_2026-05-20 10_18_36.md`，扩展为完整的算法设计章节
- 覆盖全部10个代码Section对应的算法模块
- 新增 DHAN baseline 的定义和数学描述
- 全部公式使用 LaTeX 标准格式
- 图表占位符合理分布
- 中英双语输出

## Impact
- Affected specs: 新建独立spec
- Affected code: `c:\Users\dell\Desktop\le_degn_system\gemini-export-街景车路径优化算法设计_2026-05-20 10_18_36.md`

## ADDED Requirements

### Requirement: 完整覆盖所有代码模块
系统 SHALL 在算法设计章节覆盖 le_degn_system.py 的全部10个Section：
- Section 0: PerformanceTracker + AOCC
- Section 1: RoadNetworkEnv（路网生成）
- Section 2: LineGraphBuilder（线图构建、特征提取、转移代价矩阵、惩罚矩阵）
- Section 3: ERFM（PenaltyBiasAttention → EdgeTransformerBlock → Encoder/Decoder）
- Section 4: SA-DGWN（DilatedCausalConv → GraphConv → SpatioTemporalBlock → 训练）
- Section 5: LHH（五种启发式模板 → GSESLoop → 反思机制）
- Section 6: ERFMTrainer（REINFORCE训练、tour cost计算）
- Section 7: LEDEGNSystem（三阶段集成、2-opt、动态执行）
- Section 8: BaselineDHAN（定义、贪心最近邻、惩罚模型）
- Section 9: Visualizer

#### Scenario: 审稿人理解 DHAN
- **WHEN** 审稿人阅读算法设计章节
- **THEN** 文档明确给出 BaselineDHAN 的完整定义：贪心最近邻 + DHAN式拥堵惩罚（15%增量）、5起点采样

### Requirement: LaTeX公式标准
系统 SHALL 所有数学公式使用标准LaTeX格式：行内公式用 `$...$`，块级公式用 `$$...$$`

### Requirement: 中英双语文档
系统 SHALL 输出完整的中英双语版本，英文在前、中文在后

## MODIFIED Requirements
（无）

## REMOVED Requirements
- 删除"代码截断于232行"的错误声明（代码实际完整至2104行）
- 删除"神经网络未执行"的过度谦虚声明（ERFM和SA-DGWN有完整训练流程）