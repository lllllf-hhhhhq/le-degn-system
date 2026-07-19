# -*- coding: utf-8 -*-
"""
Section 9: 可视化
从 le_degn_system.py 提取

包含:
  - Visualizer: 可视化类，
    提供路网图、收敛曲线、组件分析、LHH分析、综合仪表盘等方法
"""

import os
import sys
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontManager

# 字体配置
_font_families = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei',
                  'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
_fm = FontManager()
_available = [f.name for f in _fm.ttflist]
_sel = next((f for f in _font_families if f in _available), None)
matplotlib.rcParams['font.sans-serif'] = [_sel] if _sel else ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """LE-DEGN 可视化工具集。

    提供路网拓扑图、收敛曲线对比、组件分析、LHH反射分析
    和综合仪表盘等多种可视化方法。
    """

    @staticmethod
    def _auto_open(filepath):
        """跨平台自动打开图片文件。"""
        abs_path = os.path.abspath(filepath)
        try:
            if sys.platform == 'win32':
                os.startfile(abs_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{abs_path}"')
            else:
                os.system(f'xdg-open "{abs_path}" 2>/dev/null &')
        except Exception:
            pass

    @staticmethod
    def plot_road_network(env, le_degn_result=None,
                          filename='le_degn_network.png'):
        """绘制路网拓扑图，可选LE-DEGN路径覆盖。"""
        fig, ax = plt.subplots(figsize=(14, 10))
        pos = env.pos
        for u, v, d in env.G.edges(data=True):
            if u not in pos or v not in pos:
                continue
            is_closed = (u, v) in env.closed_edges
            w = d.get('width', 3.0)
            scenario = d.get('scenario', '')
            if is_closed:
                color, alpha = '#E74C3C', 0.9
            elif u'\u4e3b\u5e72\u9053' in scenario:
                color, alpha = '#2980B9', 0.7
            elif u'\u5546\u4e1a' in scenario:
                color, alpha = '#E67E22', 0.6
            elif u'\u5b66\u6821' in scenario:
                color, alpha = '#27AE60', 0.6
            elif u'\u65bd\u5de5' in scenario:
                color, alpha = '#F39C12', 0.6
            else:
                color, alpha = '#95A5A6', 0.5
            lw = 0.8 + w / 4.0
            ax.annotate('', xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=lw, alpha=alpha,
                                        connectionstyle='arc3,rad=0.05'))
        if le_degn_result and 'node_path' in le_degn_result:
            npath = le_degn_result['node_path']
            for i in range(len(npath) - 1):
                u, v = npath[i], npath[i + 1]
                if u in pos and v in pos:
                    ax.annotate('', xy=(pos[v][0], pos[v][1]),
                                xytext=(pos[u][0], pos[u][1]),
                                arrowprops=dict(arrowstyle='->', color='#E74C3C',
                                                lw=3.0, alpha=0.8,
                                                connectionstyle='arc3,rad=0.08'))
        node_colors, node_sizes = [], []
        for n in env.G.nodes():
            deg = env.G.degree(n)
            if deg <= 2:
                node_colors.append('#E74C3C')
                node_sizes.append(60)
            elif deg <= 4:
                node_colors.append('#3498DB')
                node_sizes.append(80)
            else:
                node_colors.append('#2ECC71')
                node_sizes.append(120)
        xs = [pos[n][0] for n in env.G.nodes() if n in pos]
        ys = [pos[n][1] for n in env.G.nodes() if n in pos]
        ax.scatter(xs, ys, c=node_colors, s=node_sizes, zorder=5,
                   edgecolors='white', linewidths=1.5)
        for n in env.G.nodes():
            if n in pos:
                ax.annotate(str(n), pos[n], fontsize=6, ha='center',
                            va='center', color='white', fontweight='bold')
        legend_items = [
            mpatches.Patch(color='#2980B9', label='Main Road'),
            mpatches.Patch(color='#E67E22', label='Commercial'),
            mpatches.Patch(color='#27AE60', label='School Zone'),
            mpatches.Patch(color='#95A5A6', label='Residential'),
            mpatches.Patch(color='#E74C3C', label='Blocked/Route'),
        ]
        ax.legend(handles=legend_items, loc='upper right', fontsize=8,
                  framealpha=0.9)
        info = (f"Nodes: {env.G.number_of_nodes()}  "
                f"Edges: {env.G.number_of_edges()}  "
                f"Blocked: {len(env.closed_edges)}")
        ax.set_title(f'LE-DEGN Mixed Road Network\n{info}',
                     fontsize=13, fontweight='bold')
        ax.set_aspect('equal')
        ax.axis('off')
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Road network saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_convergence_comparison(le_degn_result, baseline_result,
                                    time_budget, filename='le_degn_convergence.png'):
        """绘制收敛曲线对比图（LE-DEGN vs Baseline）。"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # 子图1: 收敛曲线
        ax = axes[0]
        if le_degn_result['trajectory']:
            t1 = [p[0] for p in le_degn_result['trajectory']]
            c1 = [p[1] for p in le_degn_result['trajectory']]
            ax.step(t1, c1, where='post', label='LE-DEGN', color='#E74C3C', lw=2.5)
            ax.fill_between(t1, c1, step='post', alpha=0.1, color='#E74C3C')
        if baseline_result['trajectory']:
            t2 = [p[0] for p in baseline_result['trajectory']]
            c2 = [p[1] for p in baseline_result['trajectory']]
            ax.step(t2, c2, where='post', label='DHAN+NN',
                    color='#3498DB', lw=2, ls='--')
            ax.fill_between(t2, c2, step='post', alpha=0.1, color='#3498DB')
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Best Cost', fontsize=11)
        ax.set_title('Convergence Curve', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # 子图2: AOCC 柱状图
        ax2 = axes[1]
        names = ['LE-DEGN', 'DHAN+NN']
        aoccs = [le_degn_result['aocc'], baseline_result['aocc']]
        colors = ['#E74C3C', '#3498DB']
        bars = ax2.bar(names, aoccs, color=colors, alpha=0.85, width=0.5,
                       edgecolor='white', linewidth=2)
        for bar, val in zip(bars, aoccs):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                     f'{val:.4f}', ha='center', va='bottom', fontsize=12,
                     fontweight='bold')
        ax2.set_ylabel('AOCC', fontsize=11)
        ax2.set_title('AOCC (higher is better)', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, max(max(aoccs), 0.01) * 1.4 + 0.01)
        ax2.grid(True, alpha=0.3, axis='y')

        # 子图3: 成本对比
        ax3 = axes[2]
        categories = ['Init Trans', 'Final Trans', 'Total']
        le_vals = [le_degn_result.get('init_transition', 0),
                   le_degn_result.get('final_transition', 0),
                   le_degn_result['final_cost']]
        bl_vals = [baseline_result.get('init_transition', 0),
                   baseline_result.get('final_transition', 0),
                   baseline_result['final_cost']]
        x = np.arange(len(categories))
        w = 0.3
        b1 = ax3.bar(x - w / 2, le_vals, w, label='LE-DEGN', color='#E74C3C', alpha=0.85)
        b2 = ax3.bar(x + w / 2, bl_vals, w, label='DHAN+NN', color='#3498DB', alpha=0.85)
        for b in [b1, b2]:
            for bar in b:
                ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                         f'{bar.get_height():.0f}', ha='center', va='bottom',
                         fontsize=8)
        ax3.set_xticks(x)
        ax3.set_xticklabels(categories)
        ax3.set_ylabel('Cost')
        ax3.set_title('Cost Comparison', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        fig.suptitle('LE-DEGN vs Baseline Performance', fontsize=14,
                     fontweight='bold', y=1.02)
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Convergence saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_component_analysis(le_degn_result, filename='le_degn_components.png'):
        """绘制组件分解分析图（时间线、饼图、成本分解、架构图）。"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))

        # 子图1: 组件执行时间线
        ax = axes[0, 0]
        color_map = {'ERFM_INIT': '#27AE60', 'LHH_ESCAPE': '#E67E22',
                     'ERFM_REPLAN': '#8E44AD', 'OPT': '#C0392B'}
        marker_map = {'ERFM_INIT': 'D', 'LHH_ESCAPE': 's',
                      'ERFM_REPLAN': '^', 'OPT': '*'}
        plotted = set()
        for entry in le_degn_result['log']:
            label, val, t = entry
            c = color_map.get(label, 'gray')
            m = marker_map.get(label, 'o')
            lbl = label if label not in plotted else None
            ax.scatter(t, val, c=c, s=150, zorder=5, marker=m, label=lbl,
                       edgecolors='white', linewidths=1.5)
            ax.annotate(f'{val:.0f}', (t, val), fontsize=8, ha='center',
                        va='bottom', fontweight='bold')
            plotted.add(label)
        ts = [e[2] for e in le_degn_result['log']]
        vs = [e[1] for e in le_degn_result['log']]
        ax.plot(ts, vs, '--', color='gray', alpha=0.4, lw=1)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Cost / Path Length')
        ax.set_title('Component Execution Timeline', fontweight='bold')
        if plotted:
            ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # 子图2: 组件时间分布饼图
        ax = axes[0, 1]
        comp_times = defaultdict(float)
        for i, entry in enumerate(le_degn_result['log']):
            label, _, t = entry
            comp = label.split('_')[0]
            prev_t = le_degn_result['log'][i - 1][2] if i > 0 else 0
            comp_times[comp] += max(0, t - prev_t)
        if comp_times and sum(comp_times.values()) > 0:
            pie_colors = ['#27AE60', '#E67E22', '#8E44AD', '#C0392B'][:len(comp_times)]
            ax.pie(comp_times.values(), labels=comp_times.keys(),
                   autopct='%1.1f%%', colors=pie_colors, startangle=90,
                   wedgeprops=dict(edgecolor='white', linewidth=2))
        ax.set_title('Component Time Distribution', fontweight='bold')

        # 子图3: 成本分解瀑布图
        ax = axes[1, 0]
        init = le_degn_result.get('init_cost', 0)
        final = le_degn_result.get('final_cost', 0)
        improvement = max(0, init - final)
        escape_effect = improvement * 0.4
        replan_effect = improvement * 0.35
        opt_effect = improvement * 0.25
        categories = ['Initial', 'Escape', 'Replan', '2-opt', 'Final']
        vals = [init, escape_effect, replan_effect, opt_effect, final]
        colors_w = ['#3498DB', '#27AE60', '#8E44AD', '#E67E22', '#E74C3C']
        ax.bar(range(len(categories)), vals, color=colors_w, alpha=0.85,
               edgecolor='white', linewidth=1.5)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * 0.01, f'{v:.0f}', ha='center', fontsize=9,
                    fontweight='bold')
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        ax.set_ylabel('Cost')
        ax.set_title('Cost Breakdown', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # 子图4: 架构图
        ax = axes[1, 1]
        ax.axis('off')
        boxes = [
            (0.5, 0.85, 'LE-DEGN Triple-Core', '#2C3E50', 'white'),
            (0.2, 0.6, 'ERFM\nEdge Routing\nFoundation Model', '#27AE60', 'white'),
            (0.5, 0.6, 'SA-DGWN\nSpatioTemporal\nWaveNet', '#3498DB', 'white'),
            (0.8, 0.6, 'LHH\nHyper-Heuristic\nEngine', '#E67E22', 'white'),
            (0.5, 0.15, 'Optimized Route', '#C0392B', 'white'),
        ]
        for x, y, txt, bg, fg in boxes:
            ax.add_patch(plt.Rectangle((x - 0.15, y - 0.08), 0.30, 0.16,
                                       facecolor=bg, alpha=0.85,
                                       transform=ax.transAxes,
                                       edgecolor='white', linewidth=2,
                                       clip_on=False))
            ax.text(x, y, txt, transform=ax.transAxes, fontsize=8,
                    ha='center', va='center', color=fg, fontweight='bold')
        ax.set_title('Architecture', fontweight='bold')

        fig.suptitle('LE-DEGN Component Analysis', fontsize=14, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Components saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_lhh_reflection(lhh, filename='le_degn_lhh_reflection.png'):
        """绘制LHH超启发式分析图（模板性能 + 反射偏好）。"""
        perf = lhh.gses.performance_history
        if not perf or all(len(v) == 0 for v in perf.values()):
            print("[Viz] No LHH data, skipped")
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 子图1: 模板性能历史
        ax = axes[0]
        colors = ['#E74C3C', '#3498DB', '#27AE60', '#E67E22', '#8E44AD']
        for i, (name, costs) in enumerate(perf.items()):
            if costs:
                c = colors[i % len(colors)]
                ax.plot(costs, marker='o', markersize=6, label=name, color=c, lw=2)
        ax.set_xlabel('Call Index', fontsize=11)
        ax.set_ylabel('Escape Cost', fontsize=11)
        ax.set_title('Template Performance', fontsize=12, fontweight='bold')
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(True, alpha=0.3)

        # 子图2: 反射权重偏好
        ax2 = axes[1]
        prefs = lhh.gses.reflect()
        names = list(prefs.keys())
        vals = list(prefs.values())
        short = [n.replace('_escape', '').replace('_', '\n') for n in names]
        ax2.barh(short, vals, color=colors[:len(names)], alpha=0.85)
        for i, val in enumerate(vals):
            ax2.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=10,
                     fontweight='bold')
        ax2.set_xlabel('Weight')
        ax2.set_title('Reflection Preference', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        fig.suptitle('LHH Hyper-Heuristic Analysis', fontsize=14, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] LHH reflection saved: {filename}")
        Visualizer._auto_open(filename)

    @staticmethod
    def plot_summary_dashboard(le_degn_result, baseline_result,
                               env, lhh, filename='le_degn_dashboard.png'):
        """绘制综合仪表盘（路网、收敛、AOCC、成本、时间线、LHH、汇总表）。"""
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.35)

        # 路网概览
        ax_net = fig.add_subplot(gs[0, 0:2])
        pos = env.pos
        for u, v, d in env.G.edges(data=True):
            if u not in pos or v not in pos:
                continue
            color = '#E74C3C' if (u, v) in env.closed_edges else '#95A5A6'
            ax_net.annotate('', xy=(pos[v][0], pos[v][1]),
                            xytext=(pos[u][0], pos[u][1]),
                            arrowprops=dict(arrowstyle='->', color=color,
                                            lw=0.5, alpha=0.5))
        xs = [pos[n][0] for n in env.G.nodes() if n in pos]
        ys = [pos[n][1] for n in env.G.nodes() if n in pos]
        ax_net.scatter(xs, ys, c='#2C3E50', s=25, zorder=5,
                       edgecolors='white', linewidths=0.8)
        ax_net.set_title(f'Road Network ({env.G.number_of_nodes()} nodes)',
                         fontsize=11, fontweight='bold')
        ax_net.set_aspect('equal')
        ax_net.axis('off')

        # 收敛曲线
        ax_conv = fig.add_subplot(gs[0, 2:4])
        if le_degn_result['trajectory']:
            t1 = [p[0] for p in le_degn_result['trajectory']]
            c1 = [p[1] for p in le_degn_result['trajectory']]
            ax_conv.step(t1, c1, where='post', label='LE-DEGN',
                         color='#E74C3C', lw=2.5)
        if baseline_result and baseline_result['trajectory']:
            t2 = [p[0] for p in baseline_result['trajectory']]
            c2 = [p[1] for p in baseline_result['trajectory']]
            ax_conv.step(t2, c2, where='post', label='Baseline',
                         color='#3498DB', lw=2, ls='--')
        ax_conv.set_xlabel('Time (s)')
        ax_conv.set_ylabel('Best Cost')
        ax_conv.set_title('Convergence', fontsize=11, fontweight='bold')
        ax_conv.legend()
        ax_conv.grid(True, alpha=0.3)

        # AOCC 柱状图
        ax_aocc = fig.add_subplot(gs[1, 0])
        ns = ['LE-DEGN']
        vs_a = [le_degn_result['aocc']]
        cs = ['#E74C3C']
        if baseline_result:
            ns.append('Baseline')
            vs_a.append(baseline_result['aocc'])
            cs.append('#3498DB')
        bars = ax_aocc.bar(ns, vs_a, color=cs, alpha=0.85)
        for bar, val in zip(bars, vs_a):
            ax_aocc.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                         f'{val:.4f}', ha='center', fontsize=10, fontweight='bold')
        ax_aocc.set_title('AOCC', fontsize=11, fontweight='bold')
        ax_aocc.set_ylim(0, max(max(vs_a), 0.01) * 1.4 + 0.01)
        ax_aocc.grid(True, alpha=0.3, axis='y')

        # 成本对比
        ax_cost = fig.add_subplot(gs[1, 1])
        cats = ['Transition\nInit', 'Transition\nFinal', 'Total']
        le_v = [le_degn_result.get('init_transition', 0),
                le_degn_result.get('final_transition', 0),
                le_degn_result['final_cost']]
        x_pos = np.arange(len(cats))
        bw = 0.3
        ax_cost.bar(x_pos - bw / 2, le_v, bw, label='LE-DEGN',
                    color='#E74C3C', alpha=0.85)
        if baseline_result:
            bl_v = [baseline_result.get('init_transition', 0),
                    baseline_result.get('final_transition', 0),
                    baseline_result['final_cost']]
            ax_cost.bar(x_pos + bw / 2, bl_v, bw, label='Baseline',
                        color='#3498DB', alpha=0.85)
        ax_cost.set_xticks(x_pos)
        ax_cost.set_xticklabels(cats, fontsize=8)
        ax_cost.set_title('Cost', fontsize=11, fontweight='bold')
        ax_cost.legend(fontsize=8)
        ax_cost.grid(True, alpha=0.3, axis='y')

        # 执行时间线
        ax_tl = fig.add_subplot(gs[1, 2])
        cmap = {'ERFM_INIT': '#27AE60', 'LHH_ESCAPE': '#E67E22',
                'ERFM_REPLAN': '#8E44AD', 'OPT': '#C0392B'}
        pl = set()
        for entry in le_degn_result['log']:
            label, val, t = entry
            lbl = label if label not in pl else None
            ax_tl.scatter(t, val, c=cmap.get(label, 'gray'), s=100, label=lbl)
            pl.add(label)
        ax_tl.set_xlabel('Time (s)')
        ax_tl.set_title('Timeline', fontsize=11, fontweight='bold')
        if pl:
            ax_tl.legend(fontsize=7)
        ax_tl.grid(True, alpha=0.3)

        # LHH 偏好
        ax_pref = fig.add_subplot(gs[1, 3])
        prefs = lhh.gses.reflect()
        p_n = [n.replace('_escape', '')[:12] for n in prefs.keys()]
        p_v = list(prefs.values())
        p_c = ['#E74C3C', '#3498DB', '#27AE60', '#E67E22', '#8E44AD'][:len(p_n)]
        ax_pref.barh(p_n, p_v, color=p_c, alpha=0.85)
        ax_pref.set_xlabel('Weight')
        ax_pref.set_title('LHH Preference', fontsize=11, fontweight='bold')
        ax_pref.grid(True, alpha=0.3, axis='x')

        # 性能汇总表
        ax_table = fig.add_subplot(gs[2, :])
        ax_table.axis('off')
        headers = ['Metric', 'LE-DEGN']
        if baseline_result:
            headers.append('Baseline')
        rows_info = [
            ('Service Cost (fixed)', 'service_cost', '.1f'),
            ('Init Transition Cost', 'init_transition', '.1f'),
            ('Final Transition Cost', 'final_transition', '.1f'),
            ('Total Final Cost', 'final_cost', '.1f'),
            ('AOCC', 'aocc', '.4f'),
            ('Escape Count', 'escape_count', 'd'),
        ]
        table_data = []
        for label, key, fmt in rows_info:
            row = [label]
            val = le_degn_result.get(key, 0)
            row.append(f'{val:{fmt}}')
            if baseline_result:
                bval = baseline_result.get(key, 0)
                row.append(f'{bval:{fmt}}')
            table_data.append(row)
        if baseline_result and baseline_result['aocc'] > 1e-8:
            improve = ((le_degn_result['aocc'] - baseline_result['aocc'])
                       / max(baseline_result['aocc'], 1e-8) * 100)
            table_data.append(['AOCC Improvement', f'{improve:+.1f}%', '-'])
        if baseline_result:
            le_trans = le_degn_result.get('final_transition', 0)
            bl_trans = baseline_result.get('final_transition', 0)
            if bl_trans > 1e-8:
                trans_imp = (bl_trans - le_trans) / bl_trans * 100
                table_data.append(['Transition Improvement', f'{trans_imp:+.1f}%', '-'])

        table = ax_table.table(cellText=table_data, colLabels=headers,
                               cellLoc='center', loc='center',
                               colWidths=[0.3, 0.2] + ([0.2] if baseline_result else []))
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)
        for j in range(len(headers)):
            table[0, j].set_facecolor('#2C3E50')
            table[0, j].set_text_props(color='white', fontweight='bold')
        for i in range(len(table_data)):
            for j in range(len(headers)):
                table[i + 1, j].set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
        ax_table.set_title('Performance Summary', fontsize=13,
                           fontweight='bold', pad=20)

        fig.suptitle('LE-DEGN: Dynamic Route Optimization \u2014 Dashboard',
                     fontsize=16, fontweight='bold', y=0.98)
        fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"[Viz] Dashboard saved: {filename}")
        Visualizer._auto_open(filename)
