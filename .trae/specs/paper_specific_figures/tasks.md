# LE-DEGN 论文特定图表生成 - The Implementation Plan

## [ ] Task 1: 实现图表1 - 历史城区路网网格高斯微扰与坐标映射图
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 分析现有路网生成代码中的高斯微扰逻辑
  - 创建可视化脚本，展示从规则网格到高斯微扰的坐标映射过程
  - 包含三部分：原始网格、微扰后的网格、坐标迁移标注
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 生成的图表包含三个子图
  - `programmatic` TR-1.2: 使用箭头标注坐标变化
  - `human-judgement` TR-1.3: 图表有清晰的标题、图例和刻度标签

## [ ] Task 2: 实现图表2 - 路网连通性修复与汇节点补全算法流程图
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 分析_ensure_strong_connectivity函数的执行流程
  - 创建流程图可视化三个阶段：孤立节点补全、汇节点修复、强连通补边
  - 使用框图展示算法流程
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-2.1: 流程图有三个明确阶段
  - `human-judgement` TR-2.2: 每个阶段有步骤标注
  - `human-judgement` TR-2.3: 有输入输出标注

## [ ] Task 3: 实现图表3 - AOCC收敛轨迹对比图
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 实现多种算法的对比实验（LE-DEGN、DHAN+NN、随机搜索、最近邻贪心）
  - 记录每个算法在相同时间预算内的AOCC收敛轨迹
  - 生成对比折线图
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 至少对比3种算法
  - `programmatic` TR-3.2: 有明确的时间轴和AOCC轴
  - `human-judgement` TR-3.3: 不同算法有明显颜色区分

## [ ] Task 4: 整合与文档完善
- **Priority**: P1
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 将所有图表放入论文实验数据图表文件夹
  - 生成中英文图表说明文档
  - 提供使用说明
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有文件正确复制到目标文件夹
  - `human-judgement` TR-4.2: 提供详细的使用说明
