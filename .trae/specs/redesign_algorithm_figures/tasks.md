# 重新设计算法设计8张图表 - 实现计划

## [ ] Task 1: 重新生成图1-图4（运动学/线图/ERFM/SA-DGWN）
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 图1: 运动学约束 - 三栏紧凑布局，道路用真实宽度矩形，箭头清晰
  - 图2: 线图转换 - 弯曲箭头，节点A/B/C标注，e1/e2/e3标注
  - 图3: ERFM架构 - Encoder/Decoder并排，Value Head在下方，紧凑布局
  - 图4: SA-DGWN - 微调：加粗边框，更清晰的标签
- **Test Requirements**:
  - `programmatic` TR-1.1: 4张PNG成功生成
  - `human-judgment` TR-1.2: 图表专业美观，无大量空白

## [ ] Task 2: 重新生成图5-图8（LHH/训练/执行/对比）
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 图5: LHH流程 - 环形布局，5启发式扇形排列，无交叉箭头
  - 图6: 训练收敛 - 加粗线条(3pt)，添加置信区间阴影，双Y轴清晰
  - 图7: 三阶段执行 - 等大小框，粗箭头(2pt)，反馈循环用弯曲箭头
  - 图8: 架构对比 - 差异项用红色高亮，对比线加粗
- **Test Requirements**:
  - `programmatic` TR-2.1: 4张PNG成功生成
  - `human-judgment` TR-2.2: 图表专业美观，布局紧凑

## [ ] Task 3: 验证所有图表
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**: 查看所有8张图，确认质量提升
- **Test Requirements**:
  - `human-judgment` TR-3.1: 所有图表看起来专业、美观
  - `human-judgment` TR-3.2: 无丑陋元素（粗黑线、小字、大量空白）