# LE-DEGN 算法架构与数学建模文档 - 实施计划

## [x] Task 1: 编写算法概览与问题建模章节
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 编写文档第一章：算法整体概览（一行话总结 + 四层架构图）
  - 编写文档第二章：问题建模（中国邮路问题定义、混合路网扩展、优化目标）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-1.1: 算法概览能让人一分钟内理解算法做什么
  - `human-judgement` TR-1.2: 问题建模公式与代码实现一致

## [x] Task 2: 编写路网环境与线图转换章节
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 编写路网生成（网格→高斯扰动→连通性修复）
  - 编写线图转换原理（为什么转、怎么转、转移代价）
  - 编写道路类型参数表
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: 线图转换解释清楚，非专业读者能理解
  - `human-judgement` TR-2.2: 参数表完整准确

## [x] Task 3: 编写核心模型与评估指标章节
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 编写 ERFM 模型（图卷积三层结构）
  - 编写 SA-DGWN（时空图卷积）
  - 编写 LHH 语言超启发式
  - 编写 AOCC 评估指标
  - 编写完整符号汇总表
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个模型的公式正确
  - `human-judgement` TR-3.2: AOCC 指标解释清楚（cost vs AOCC 的关系）
  - `human-judgement` TR-3.3: 符号表完整

## [x] Task 4: 编写关键要点总结与常见问题
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 
  - 创新点总结
  - 实验结论速览
  - 常见问题解答（LLM是什么、AOCC解释、cost与AOCC关系等）
  - 文件目录与运行说明
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `human-judgement` TR-4.1: 常见问题覆盖与学长对话中可能被问到的所有点
  - `human-judgement` TR-4.2: 文档有清晰的目录结构