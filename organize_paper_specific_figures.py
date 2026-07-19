#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理论文特定图表到文件夹
"""

import os
import shutil
from pathlib import Path

def organize_paper_specific_figures():
    base_dir = Path('c:/Users/dell/Desktop/le_degn_system')
    source_dir = base_dir / 'paper_figures'
    target_dir = base_dir / '论文实验数据图表' / '可视化图表'
    
    print("✓ 开始整理论文特定图表...\n")
    
    # 源文件列表
    files_to_copy = [
        ('figure_1_grid_perturbation.png', '论文图表1_网格高斯微扰图.png'),
        ('figure_2_connectivity_flowchart.png', '论文图表2_连通性修复流程图.png'),
        ('figure_3_convergence_comparison.png', '论文图表3_AOCC收敛对比图.png'),
    ]
    
    # 复制文件
    copied_count = 0
    for src_file, dst_file in files_to_copy:
        src_path = source_dir / src_file
        dst_path = target_dir / dst_file
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ 复制: {src_file} -> {dst_file}")
            copied_count += 1
        else:
            print(f"  ✗ 文件不存在: {src_file}")
    
    # 创建说明文档
    readme_content = """# 论文特定图表说明

## 📊 图表列表

### 论文图表1：历史城区路网网格高斯微扰与坐标映射图
**文件**: `论文图表1_网格高斯微扰图.png`

**内容**:
- 子图(a): 原始规则网格布局
- 子图(b): 高斯微扰后的历史城区路网
- 子图(c): 坐标迁移箭头标注

**用途**: 展示LE-DEGN路网生成算法的坐标扰动方法

---

### 论文图表2：路网连通性修复与汇节点补全算法流程图
**文件**: `论文图表2_连通性修复流程图.png`

**内容**:
- 阶段1: 孤立节点补全
- 阶段2: 汇节点出度修复
- 阶段3: 强连通分量间补边

**用途**: 解释连通性保障机制的算法流程

---

### 论文图表3：不同寻路算法在限定计算限时内的AOCC收敛轨迹对比图
**文件**: `论文图表3_AOCC收敛对比图.png`

**内容**:
- 收敛曲线对比: LE-DEGN、DHAN+NN、A*启发式、随机搜索
- 最终AOCC柱状图对比
- 收敛速度统计
- 性能提升百分比

**用途**: 展示LE-DEGN相对于基线算法的性能优势

---

## 📋 图表规格
- **分辨率**: 300 DPI
- **格式**: PNG
- **语言**: 中英文双语标题
- **配色**: 符合LE-DEGN系统视觉风格
"""
    
    readme_path = target_dir / '论文特定图表说明.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"\n  ✓ 生成说明文档: 论文特定图表说明.md")
    
    print(f"\n{'='*60}")
    print(f"✓ 成功整理 {copied_count} 张论文特定图表！")
    print(f"✓ 文件位置: {target_dir}")
    print(f"{'='*60}")

if __name__ == '__main__':
    organize_paper_specific_figures()
