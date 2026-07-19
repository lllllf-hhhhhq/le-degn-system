# LE-DEGN 算法设计章节重写 - 实现计划

## [x] Task 1: 撰写英文算法设计章节（新增模块部分）
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 在保留原3.1-3.6基础上，新增以下子章节：
  - 3.7 线图构建与边中心表示 (LineGraphBuilder)：边特征工程、转移代价矩阵 T_{ij}、惩罚矩阵 M_{ij}
  - 3.8 ERFM编码器-解码器架构：PenaltyBiasMultiHeadAttention公式、EdgeTransformerBlock、GlobalAttributeEmbedding
  - 3.9 SA-DGWN时空预测网络：扩散因果卷积、图卷积层、SpatioTemporalBlock、BCE训练
  - 3.10 LHH语言驱动启发式中心：五种启发式模板详述、GSESLoop评估-选择-反思循环
  - 3.11 ERFM训练器：REINFORCE策略梯度、tour cost = service + transition分解
  - 3.12 LE-DEGN集成系统：三阶段动态执行流程、2-opt局部优化
  - 3.13 基线对比方法(DHAN)：贪心最近邻定义、拥堵惩罚模型、与LE-DEGN的差异
- **Acceptance Criteria Addressed**: 完整覆盖所有代码模块, DHAN基线定义, LaTeX公式标准
- **Test Requirements**:
  - `human-judgment` TR-1.1: 英文符合国际期刊标准
  - `human-judgment` TR-1.2: 所有代码Section有对应算法描述
  - `human-judgment` TR-1.3: DHAN定义完整可理解

## [x] Task 2: 翻译为中文
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 完整翻译英文内容为学术中文，术语一致
- **Test Requirements**:
  - `human-judgment` TR-2.1: 中文准确完整
  - `human-judgment` TR-2.2: 术语与算法设计一致

## [x] Task 3: 插入图表占位符与格式化
- **Priority**: P1
- **Depends On**: Task 2
- **Description**: 在合理位置插入图表占位符，格式化文档
- **Test Requirements**:
  - `human-judgment` TR-3.1: 图表占位符位置合理
  - `human-judgment` TR-3.2: LaTeX公式格式正确