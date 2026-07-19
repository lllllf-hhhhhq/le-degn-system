# LE-DEGN 论文特定图表生成 - Product Requirement Document

## Overview
- **Summary**: 为LE-DEGN论文生成三张专门的实验图表：路网高斯微扰图、连通性修复流程图、AOCC收敛对比图
- **Purpose**: 提供论文所需的视觉证据，展示算法关键步骤和性能优势
- **Target Users**: 论文作者、审稿人

## Goals
- 生成图表1：历史城区路网网格高斯微扰与坐标映射图
- 生成图表2：路网连通性修复与汇节点补全算法流程图
- 生成图表3：不同寻路算法在限定计算限时内的 AOCC 收敛轨迹对比图
- 所有图表符合学术期刊标准（300 DPI，清晰标注，中英文说明）

## Non-Goals (Out of Scope)
- 修改现有算法代码
- 添加新的寻路算法
- 修改核心实验流程

## Background & Context
现有代码库包含完整的LE-DEGN实现，具备路网生成、连通性修复和AOCC计算功能。

## Functional Requirements
- **FR-1**: 展示网格到高斯微扰的坐标映射过程
- **FR-2**: 可视化连通性修复算法的完整流程
- **FR-3**: 对比多个算法的AOCC收敛轨迹

## Non-Functional Requirements
- **NFR-1**: 所有图表分辨率 ≥ 300 DPI
- **NFR-2**: 图表包含清晰的图例和标注
- **NFR-3**: 提供中英文图表标题和说明

## Constraints
- **Technical**: 使用现有Python环境和matplotlib
- **Dependencies**: 现有le_degn_system.py代码

## Assumptions
- 现有算法实现完整可运行
- 路网生成代码的高斯微扰逻辑可用
- 连通性修复函数实现完整

## Acceptance Criteria

### AC-1: 高斯微扰与坐标映射图
- **Given**: 路网生成代码可运行
- **When**: 运行图表生成脚本
- **Then**: 生成包含原始网格、高斯微扰、坐标映射三部分的复合图表
- **Verification**: `programmatic`

### AC-2: 连通性修复流程图
- **Given**: _ensure_strong_connectivity函数实现完整
- **When**: 分析代码流程并生成流程图
- **Then**: 生成展示节点补全、出度修复、强连通修复三阶段的流程图
- **Verification**: `human-judgment`

### AC-3: AOCC收敛对比图
- **Given**: 可以运行多个算法进行对比
- **When**: 执行基准实验
- **Then**: 生成展示LE-DEGN、DHAN+NN、随机搜索等算法的AOCC收敛曲线对比图
- **Verification**: `programmatic`

## Open Questions
- [ ] 需要对比哪些具体的寻路算法？（除了DHAN+NN外）
