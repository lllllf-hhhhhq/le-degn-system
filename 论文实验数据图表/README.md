# LE-DEGN 论文实验数据图表汇总

## 📁 文件夹结构

```
论文实验数据图表/
├── 可视化图表/          (11个PNG文件, 300 DPI)
├── 数据表格/            (5个CSV/JSON文件)
└── 论文描述/            (2个文档文件)
```

## 📊 可视化图表文件 (11个)

### 核心实验图
1. le_degn_network.png - 路网拓扑结构图
2. le_degn_convergence.png - 收敛曲线对比
3. le_degn_components.png - 组件执行时间线
4. le_degn_lhh_reflection.png - LHH超启发式分析
5. le_degn_dashboard.png - 综合仪表盘

### 论文级分析图
6. scalability_analysis.png - 可扩展性分析
7. ablation_study.png - 组件消融研究
8. road_type_analysis.png - 道路类型分析
9. component_contribution.png - 组件贡献度
10. congestion_sensitivity.png - 拥堵鲁棒性
11. performance_summary_table.png - 性能汇总表

## 📈 数据表格文件 (5个)

1. performance_results.csv - 完整性能数据表
2. scalability_results.csv - 可扩展性数据
3. ablation_results.csv - 消融研究数据
4. road_type_parameters.csv - 道路类型参数
5. ablation_results.json - 消融研究原始数据

## 📝 论文描述文件 (2个)

1. paper_english_descriptions.txt - 英文图表标题/描述
2. DELIVERY_CHECKLIST.md - 完整交付清单

## 🎯 主要实验结果摘要

| 网络规模 | LE-DEGN AOCC | Baseline AOCC | 成本改善 |
|---------|-------------|--------------|---------|
| 40节点   | 0.488       | 0.633        | +12.7% |
| 60节点   | 0.539       | 0.699        | +10.4% |
| 80节点   | 0.482       | 0.530        | +16.3% |
| 100节点  | 0.302       | 0.457        | +8.8%  |

**平均转移代价改善: +19.2%**

---
此文件夹包含撰写论文所需的所有实验数据和可视化图表
