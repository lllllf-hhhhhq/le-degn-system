# LE-DEGN 实验数据部分重写（使用用户指定图表） - 实现计划

## [x] Task 1: 分析数据文件与图表匹配
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 精读全部5份数据文件（performance_results.csv, ablation_results.csv/json, scalability_results.csv, road_type_parameters.csv）
  - 确认每个CSV中的精确数值（特别是AOCC=0.6986, 0.4824, 0.4574等）
  - 将11张图表按内容匹配到6个子章节
- **Acceptance Criteria Addressed**: 数据精确匹配
- **Test Requirements**:
  - `programmatic` TR-1.1: 提取所有数值与CSV完全一致
  - `human-judgment` TR-1.2: 图表匹配逻辑合理

## [x] Task 2: 撰写英文实验数据部分
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 撰写5.1-5.6六个子章节的英文内容
  - 引用具体图表文件名：performance_summary_table.png、le_degn_convergence.png、ablation_study.png、component_contribution.png、scalability_analysis.png、congestion_sensitivity.png、le_degn_lhh_reflection.png、road_type_analysis.png
  - 新增5.6道路类型分析子章节，基于road_type_parameters.csv
  - 遵循国际期刊学术英语标准
- **Acceptance Criteria Addressed**: 使用用户指定图表重写实验部分
- **Test Requirements**:
  - `human-judgment` TR-2.1: 英文符合国际期刊标准
  - `human-judgment` TR-2.2: 每个子章节有对应的图表引用
  - `human-judgment` TR-2.3: 新增的道路类型分析子章节内容合理

## [x] Task 3: 撰写中文翻译
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - 完整翻译英文内容为中文
  - 保持学术语调与技术准确性
  - 术语与算法设计文档一致
- **Acceptance Criteria Addressed**: 中英双语文档
- **Test Requirements**:
  - `human-judgment` TR-3.1: 中文翻译准确完整
  - `human-judgment` TR-3.2: 术语一致（ERFM/SA-DGWN/LHH/AOCC）

## [x] Task 4: 格式化与整合文档
- **Priority**: P1
- **Depends On**: Task 3
- **Description**:
  - 将中英文合并为单一双语文档
  - 格式化表格（表1-表4）
  - 统一图表引用格式：`Figure X: [description](path/to/figure.png)`
  - 添加Section 5开头段落
- **Acceptance Criteria Addressed**: 使用用户指定图表重写实验部分
- **Test Requirements**:
  - `human-judgment` TR-4.1: 文档结构清晰
  - `programmatic` TR-4.2: 所有图表路径正确

## [x] Task 5: 质量验证
- **Priority**: P1
- **Depends On**: Task 4
- **Description**:
  - 核对所有表格数值与CSV文件一致
  - 验证图表引用不重复、不遗漏
  - 检查中英文术语一致性
  - 验证学术英语语法
- **Acceptance Criteria Addressed**: 数据精确匹配, 中英双语文档
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有数值与源数据一致
  - `human-judgment` TR-5.2: 图表引用无重复
  - `human-judgment` TR-5.3: 中英文对应完整