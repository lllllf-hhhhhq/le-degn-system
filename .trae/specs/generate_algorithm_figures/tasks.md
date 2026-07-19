# 生成算法设计章节8张图表 - 实现计划

## [ ] Task 1: 生成全英文版本图1-图4
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 所有图表文字改为纯英文（去掉中文翻译）
  - 图1: 运动学约束 → "Kinematic Constraints and Turn Penalties"
  - 图2: 线图转换 → "Primal Graph to Line Graph Transformation"  
  - 图3: ERFM架构 → "ERFM Encoder-Decoder Architecture"
  - 图4: SA-DGWN结构 → "SA-DGWN Spatio-Temporal Network"
- **Test Requirements**:
  - `programmatic` TR-1.1: 4张PNG文件成功生成（覆盖旧版本）
  - `human-judgment` TR-1.2: 图表仅含英文，无中文

## [ ] Task 2: 生成全英文版本图5-图8
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 所有图表文字改为纯英文（去掉中文翻译）
  - 图5: LHH流程图 → "LHH GSES Loop and Heuristic Selection"
  - 图6: 训练收敛 → "ERFM Training Convergence and Temperature Annealing"
  - 图7: 三阶段执行 → "LE-DEGN Three-Phase Dynamic Execution"
  - 图8: 架构对比 → "LE-DEGN vs Baseline (DHAN) Architecture Comparison"
- **Test Requirements**:
  - `programmatic` TR-2.1: 4张PNG文件成功生成（覆盖旧版本）
  - `human-judgment` TR-2.2: 图表仅含英文，无中文

## [ ] Task 3: 验证全英文图表
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**: 验证所有8张图已保存为全英文版本
- **Test Requirements**:
  - `programmatic` TR-3.1: 8个PNG文件均存在于目标文件夹
  - `human-judgment` TR-3.2: 所有图表仅含英文，无中文字符