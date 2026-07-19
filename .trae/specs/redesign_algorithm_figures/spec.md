# 重新设计算法设计8张图表 Spec

## Why
当前8张算法设计图表存在严重视觉问题：元素过小、布局松散、大量空白、箭头丑陋、颜色搭配不协调，不符合国际期刊的配图标准。需要重新设计为专业、美观、信息密度合理的学术图表。

## What Changes
重新设计8张PNG图表，覆盖原文件：

1. **fig1_kinematic_constraints.png** - 运动学约束：放大元素、紧凑三栏布局、道路用真实矩形表示
2. **fig2_line_graph_transform.png** - 线图转换：用弯曲箭头替代粗黑线、节点标注清晰
3. **fig3_erfm_architecture.png** - ERFM架构：紧凑布局、Encoder/Decoder并排、Value Head融入主线
4. **fig4_sadgwn_structure.png** - SA-DGWN：保持现状（此图质量尚可）
5. **fig5_lhh_flowchart.png** - LHH流程：环形布局替代交叉箭头、5启发式用扇形排列
6. **fig6_training_convergence.png** - 训练收敛：加粗线条、添加阴影区域、更专业的配色
7. **fig7_three_phase_execution.png** - 三阶段执行：等大小框、粗箭头、清晰反馈循环
8. **fig8_architecture_comparison.png** - 架构对比：添加差异高亮、对比箭头更明显

## Impact
- Affected files: 8个PNG文件覆盖写入

## ADDED Requirements

### Requirement: 专业学术图表设计
系统 SHALL 重新生成8张图表，满足：
- 元素大小适中，占满画布（避免大量空白）
- 使用专业配色（IEEE/ACM期刊风格：蓝、橙、绿、红）
- 箭头清晰美观（使用FancyArrowPatch）
- 字体大小统一（标题16pt，标签12pt）
- 布局紧凑合理，信息密度高

#### Scenario: 审稿人查看图表
- **WHEN** 审稿人阅读论文图表
- **THEN** 图表看起来专业、清晰、美观，符合顶级期刊标准

## MODIFIED Requirements
（无）

## REMOVED Requirements
（无）