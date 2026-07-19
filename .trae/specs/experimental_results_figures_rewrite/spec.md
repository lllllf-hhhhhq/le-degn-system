# LE-DEGN 实验数据部分重写（使用用户指定图表） Spec

## Why
用户需要基于新上传的11张可视化图表和5份数据文件，重新撰写论文的实验数据部分（Section 5），替换之前通用的"此处应有图表"占位符为具体的图表引用，确保图表引用与用户实际生成的图表一一对应。

## What Changes
- 重写 `LE_DEGN_Experimental_Results_Revised.md`，替换所有通用占位符为具体图表的实际文件名引用
- 根据 `scalability_results.csv` 和 `performance_results.csv` 的精确数据修正数值
- 根据图表内容新增道路类型分析子章节
- 保持中英双语格式

## Impact
- Affected specs: 新建独立spec
- Affected code: `c:\Users\dell\Desktop\le_degn_system\LE_DEGN_Experimental_Results_Revised.md`

## ADDED Requirements

### Requirement: 使用用户指定图表重写实验部分
系统 SHALL 使用用户上传的11张可视化图表和5份数据文件，重写论文实验数据部分，每个子章节引用对应的具体图表文件。

#### Scenario: 整体性能对比引用正确图表
- **WHEN** 读者阅读 5.1 整体性能对比
- **THEN** 文档引用 `performance_summary_table.png` 展示性能汇总表，引用 `le_degn_convergence.png` 展示收敛曲线

#### Scenario: 消融研究引用正确图表
- **WHEN** 读者阅读 5.2 组件消融研究
- **THEN** 文档引用 `ablation_study.png` 展示消融结果，引用 `component_contribution.png` 展示组件贡献分布

#### Scenario: 可扩展性分析引用正确图表
- **WHEN** 读者阅读 5.3 可扩展性分析
- **THEN** 文档引用 `scalability_analysis.png` 展示可扩展性趋势

#### Scenario: 拥堵鲁棒性引用正确图表
- **WHEN** 读者阅读 5.4 拥堵鲁棒性评估
- **THEN** 文档引用 `congestion_sensitivity.png` 展示拥堵敏感性分析

#### Scenario: LHH分析引用正确图表
- **WHEN** 读者阅读 5.5 LHH启发式分析
- **THEN** 文档引用 `le_degn_lhh_reflection.png` 展示反思机制

#### Scenario: 道路类型分析引用正确图表
- **WHEN** 读者阅读 5.6 道路类型分析
- **THEN** 文档引用 `road_type_analysis.png` 并根据 `road_type_parameters.csv` 数据分析不同道路类型特征

### Requirement: 数据精确匹配
系统 SHALL 确保所有表格数值与 `performance_results.csv`、`ablation_results.csv`、`ablation_results.json`、`scalability_results.csv` 中的数据完全一致。

#### Scenario: 性能数据验证
- **WHEN** 核对 AOCC 数值
- **THEN** 60节点Baseline AOCC为0.6986（非0.699），80节点LE-DEGN AOCC为0.4824（非0.482），100节点Baseline AOCC为0.4574（非0.457）

### Requirement: 中英双语文档
系统 SHALL 提供完整的中英双语版本，保持学术语调和技术准确性。

#### Scenario: 双语一致性
- **WHEN** 对比中英文版本
- **THEN** 两个版本内容对应、术语一致（ERFM/SA-DGWN/LHH/AOCC）

## MODIFIED Requirements
（无修改，新建文档）

## REMOVED Requirements
（无移除）