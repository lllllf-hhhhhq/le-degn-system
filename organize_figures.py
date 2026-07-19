#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇总论文实验数据到专门文件夹
"""

import os
import shutil
from pathlib import Path

def organize_paper_figures():
    base_dir = Path('c:/Users/dell/Desktop/le_degn_system')
    target_dir = base_dir / '论文实验数据图表'
    
    # 创建目标文件夹
    target_dir.mkdir(exist_ok=True)
    print(f"✓ 创建文件夹: {target_dir}")
    
    # 定义要移动的文件类型
    files_to_move = {
        '可视化图表': [
            'le_degn_network.png',
            'le_degn_convergence.png',
            'le_degn_components.png',
            'le_degn_lhh_reflection.png',
            'le_degn_dashboard.png',
            'scalability_analysis.png',
            'ablation_study.png',
            'road_type_analysis.png',
            'component_contribution.png',
            'congestion_sensitivity.png',
            'performance_summary_table.png',
        ],
        '数据表格': [
            'performance_results.csv',
            'scalability_results.csv',
            'ablation_results.csv',
            'road_type_parameters.csv',
            'ablation_results.json',
        ],
        '论文描述': [
            'paper_english_descriptions.txt',
            'DELIVERY_CHECKLIST.md',
        ]
    }
    
    # 创建子文件夹
    for subdir in files_to_move.keys():
        subdir_path = target_dir / subdir
        subdir_path.mkdir(exist_ok=True)
    
    # 移动文件
    moved_count = 0
    for subdir, filenames in files_to_move.items():
        subdir_path = target_dir / subdir
        for filename in filenames:
            src = base_dir / filename
            dst = subdir_path / filename
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ 复制到 {subdir}: {filename}")
                moved_count += 1
            else:
                print(f"  ✗ 文件不存在: {filename}")
    
    # 创建README文件
    readme_content = """# LE-DEGN 论文实验数据图表汇总

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
"""
    readme_path = target_dir / 'README.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"✓ 创建文件: README.md")
    
    print(f"\n{'='*60}")
    print(f"✓ 总计整理了 {moved_count} 个文件到文件夹")
    print(f"✓ 文件夹路径: {target_dir}")
    print(f"{'='*60}")

if __name__ == '__main__':
    organize_paper_figures()
