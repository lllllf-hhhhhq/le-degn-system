# 生成算法设计章节8张图表 Spec

## Why
算法设计章节（3.1-3.13）中标注了8处"此处应有图表"占位符，需要生成对应的学术级可视化图表，使论文图文并茂、审稿人易于理解。

## What Changes
生成8张PNG格式学术图表，保存至 `论文实验数据图表/可视化图表/` 文件夹：

1. **fig1_kinematic_constraints.png** - 运动学约束与转向惩罚机制示意图（窄道变单向、窄道摩擦系数1.5、左转1.5s/掉头7.0s惩罚）
2. **fig2_line_graph_transform.png** - 原图到线图的转换示意图（原图节点→边，线图边→节点）
3. **fig3_erfm_architecture.png** - ERFM编码器-解码器架构示意图（3层TransformerBlock、PenaltyBiasAttention、Decoder自回归）
4. **fig4_sadgwn_structure.png** - SA-DGWN时空预测网络结构图（DilatedCausalConv→GraphConv→Gating）
5. **fig5_lhh_flowchart.png** - LHH启发式选择与反思机制流程图（GSES循环：Generate→Score→Execute→Self-reflect）
6. **fig6_training_convergence.png** - ERFM训练收敛曲线与温度退火示意图（成本下降曲线+τ从1.5→0.2）
7. **fig7_three_phase_execution.png** - LE-DEGN三阶段动态执行流程图（宏观规划→动态执行→2-opt优化）
8. **fig8_architecture_comparison.png** - LE-DEGN vs Baseline(DHAN)架构对比图（左右对比：学习表示vs原始矩阵、主动预测vs被动惩罚等）

## Impact
- Affected code: 8个新PNG文件写入 `论文实验数据图表/可视化图表/`

## ADDED Requirements

### Requirement: 生成8张学术级图表
系统 SHALL 使用matplotlib生成8张300 DPI的PNG图表，每张图包含中英文标题。

#### Scenario: 图表1 - 运动学约束
- **WHEN** 运行图表生成脚本
- **THEN** 生成展示三种约束规则的示意图：宽度<4.5m变单向、3.0≤宽度<4.5m摩擦×1.5、左转1.5s/掉头7.0s

#### Scenario: 图表2 - 线图转换
- **WHEN** 运行图表生成脚本
- **THEN** 生成展示原图（节点为路口、边为道路）到线图（节点为道路、边为连通关系）的转换

#### Scenario: 图表3-8
- **WHEN** 运行图表生成脚本
- **THEN** 生成对应架构图、流程图、对比图

## MODIFIED Requirements
（无）

## REMOVED Requirements
（无）