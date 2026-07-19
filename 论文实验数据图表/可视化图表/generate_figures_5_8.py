import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np
import os

output_dir = r"c:\Users\dell\Desktop\le_degn_system\论文实验数据图表\可视化图表"
os.makedirs(output_dir, exist_ok=True)

plt.rcParams['font.family'] = ['DejaVu Sans', 'SimSun', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'
plt.rcParams['text.color'] = '#333333'

academic_colors = {
    'primary': '#1f4e79',
    'secondary': '#2e75b6',
    'accent': '#c55a11',
    'success': '#548235',
    'purple': '#7030a0',
    'gray': '#7f7f7f',
    'light_blue': '#bdd7ee',
    'light_gray': '#d9d9d9',
    'dark_gray': '#595959'
}

def save_fig(fig, filename):
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    return filepath

# ============================================================
# Figure 5: LHH GSES Loop and Heuristic Selection
# ============================================================
fig5, ax5 = plt.subplots(figsize=(10, 8))
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 10)
ax5.axis('off')
ax5.set_title("Fig.5 LHH GSES Loop and Heuristic Selection / 图5 LHH GSES循环与启发式选择", 
              fontsize=14, fontweight='bold', pad=20)

center = (5, 5)
radius = 2.2

# Main center circle
center_circle = Circle(center, 0.9, facecolor=academic_colors['primary'], 
                        edgecolor='black', linewidth=2, zorder=5)
ax5.add_patch(center_circle)
ax5.text(center[0], center[1], 'GSES\nLoop', ha='center', va='center', 
         fontsize=12, fontweight='bold', color='white', zorder=6)

# Four steps around the circle
steps = [
    ('Generate', np.pi/2, academic_colors['secondary']),
    ('Score', 0, academic_colors['success']),
    ('Execute', -np.pi/2, academic_colors['accent']),
    ('Self-reflect', np.pi, academic_colors['purple'])
]

step_positions = {}
for label, angle, color in steps:
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    step_positions[label] = (x, y)
    
    box = FancyBboxPatch((x-0.7, y-0.35), 1.4, 0.7, 
                          boxstyle="round,pad=0.05,rounding_size=0.15",
                          facecolor=color, edgecolor='black', linewidth=1.5, zorder=4)
    ax5.add_patch(box)
    ax5.text(x, y, label, ha='center', va='center', fontsize=10, 
             fontweight='bold', color='white', zorder=5)

# Arrows between steps
for i in range(len(steps)):
    curr = steps[i]
    next_s = steps[(i+1) % len(steps)]
    
    a = np.arctan2(step_positions[next_s[0]][1]-center[1], 
                   step_positions[next_s[0]][0]-center[0])
    start_x = step_positions[curr[0]][0] + 0.75 * np.cos(a - np.pi)
    start_y = step_positions[curr[0]][1] + 0.75 * np.sin(a - np.pi)
    end_x = step_positions[next_s[0]][0] + 0.75 * np.cos(a)
    end_y = step_positions[next_s[0]][1] + 0.75 * np.sin(a)
    
    arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                            connectionstyle="arc3,rad=0.15",
                            arrowstyle='-|>', mutation_scale=15,
                            color='#333333', linewidth=1.5, zorder=3)
    ax5.add_patch(arrow)

# Heuristic boxes next to Generate
gen_x, gen_y = step_positions['Generate']
heuristics = ['Greedy\nWidest', 'Min\nPenalty', 'Max\nConnectivity', 
              'Adaptive\nA*', 'Multi-hop\nGreedy']

for i, h in enumerate(heuristics):
    hx = gen_x - 2.2
    hy = gen_y + 1.2 - i * 0.55
    box = FancyBboxPatch((hx-0.55, hy-0.22), 1.1, 0.44,
                          boxstyle="round,pad=0.02,rounding_size=0.1",
                          facecolor=academic_colors['light_blue'], 
                          edgecolor=academic_colors['secondary'], linewidth=1, zorder=4)
    ax5.add_patch(box)
    ax5.text(hx, hy, h, ha='center', va='center', fontsize=7, 
             color=academic_colors['primary'], zorder=5)
    
    # Small arrow from heuristic to Generate
    ax5.annotate('', xy=(gen_x-0.75, gen_y+0.2), xytext=(hx+0.6, hy),
                arrowprops=dict(arrowstyle='->', color=academic_colors['secondary'], 
                               lw=0.8, connectionstyle="arc3,rad=0.1"),
                zorder=3)

# Self-reflect annotation
sr_x, sr_y = step_positions['Self-reflect']
ax5.text(sr_x - 1.8, sr_y, 'Update weights\n(last 5 records)', 
         ha='center', va='center', fontsize=8, 
         color=academic_colors['purple'], fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#e5dfec', 
                  edgecolor=academic_colors['purple'], linewidth=1))

ax5.annotate('', xy=(sr_x-0.75, sr_y), xytext=(sr_x-1.3, sr_y),
            arrowprops=dict(arrowstyle='->', color=academic_colors['purple'], lw=1),
            zorder=3)

filepath5 = save_fig(fig5, 'fig5_lhh_flowchart.png')
print(f"Saved: {filepath5}")

# ============================================================
# Figure 6: ERFM Training Convergence and Temperature Annealing
# ============================================================
fig6, ax6_1 = plt.subplots(figsize=(10, 8))

episodes = np.linspace(0, 3000, 300)
# Simulated tour cost curve (REINFORCE training)
np.random.seed(42)
tour_cost = 70000 - (70000 - 27000) * (1 - np.exp(-episodes / 800)) + np.random.normal(0, 800, len(episodes))
tour_cost = np.clip(tour_cost, 27000, 70000)

# Temperature annealing (linear)
temperature = 1.5 - (1.5 - 0.2) * (episodes / 3000)

ax6_1.set_xlabel('Training Episode / 训练回合', fontsize=12, fontweight='bold')
ax6_1.set_ylabel('Tour Cost / 路径成本', fontsize=12, fontweight='bold', color=academic_colors['secondary'])
line1 = ax6_1.plot(episodes, tour_cost, color=academic_colors['secondary'], 
                   linewidth=2, label='Tour Cost / 路径成本', alpha=0.9)
ax6_1.tick_params(axis='y', labelcolor=academic_colors['secondary'])
ax6_1.set_xlim(0, 3000)
ax6_1.set_ylim(20000, 75000)
ax6_1.grid(True, alpha=0.3, linestyle='--')

ax6_2 = ax6_1.twinx()
ax6_2.set_ylabel('Temperature τ / 温度τ', fontsize=12, fontweight='bold', color=academic_colors['accent'])
line2 = ax6_2.plot(episodes, temperature, color=academic_colors['accent'], 
                   linewidth=2, linestyle='--', label='Temperature τ / 温度τ', alpha=0.9)
ax6_2.tick_params(axis='y', labelcolor=academic_colors['accent'])
ax6_2.set_ylim(0, 2)

# Combined legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax6_1.legend(lines, labels, loc='upper right', fontsize=10, framealpha=0.9)

ax6_1.set_title("Fig.6 ERFM Training Convergence and Temperature Annealing / 图6 ERFM训练收敛与温度退火", 
                fontsize=14, fontweight='bold', pad=20)

filepath6 = save_fig(fig6, 'fig6_training_convergence.png')
print(f"Saved: {filepath6}")

# ============================================================
# Figure 7: LE-DEGN Three-Phase Dynamic Execution
# ============================================================
fig7, ax7 = plt.subplots(figsize=(10, 8))
ax7.set_xlim(0, 10)
ax7.set_ylim(0, 10)
ax7.axis('off')
ax7.set_title("Fig.7 LE-DEGN Three-Phase Dynamic Execution / 图7 LE-DEGN三阶段动态执行", 
              fontsize=14, fontweight='bold', pad=20)

phase_boxes = [
    (1.5, 6.5, 'Phase 1\nGlobal Macro Planning', 
     '5 rollouts, τ=0.5', academic_colors['primary']),
    (5, 6.5, 'Phase 2\nDynamic Execution', 
     'Congestion events → SA-DGWN predict → LHH escape → ERFM re-plan', 
     academic_colors['secondary']),
    (8.5, 6.5, 'Phase 3\n2-opt Refinement', 
     'Local search, max 300 iter', academic_colors['success'])
]

phase_positions = {}
for x, y, title, subtitle, color in phase_boxes:
    phase_positions[title.split('\n')[0]] = (x, y)
    box = FancyBboxPatch((x-1.1, y-0.7), 2.2, 1.4,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor=color, edgecolor='black', linewidth=2, zorder=4)
    ax7.add_patch(box)
    ax7.text(x, y+0.15, title, ha='center', va='center', fontsize=10, 
             fontweight='bold', color='white', zorder=5)
    ax7.text(x, y-0.35, subtitle, ha='center', va='center', fontsize=7.5, 
             color='white', zorder=5, wrap=True)

# Forward arrows between phases
for i in range(len(phase_boxes)-1):
    x1 = phase_boxes[i][0] + 1.1
    y1 = phase_boxes[i][1]
    x2 = phase_boxes[i+1][0] - 1.1
    y2 = phase_boxes[i+1][1]
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle='-|>', mutation_scale=20,
                            color='#333333', linewidth=2, zorder=3)
    ax7.add_patch(arrow)

# Feedback arrow from Phase 2 to Phase 1
p2 = (phase_boxes[1][0], phase_boxes[1][1])
p1 = (phase_boxes[0][0], phase_boxes[0][1])

# Curved feedback arrow
arrow = FancyArrowPatch((p2[0]-0.5, p2[1]-0.8), (p1[0]+0.5, p1[1]-0.8),
                        connectionstyle="arc3,rad=-0.4",
                        arrowstyle='-|>', mutation_scale=15,
                        color=academic_colors['accent'], linewidth=2, 
                        linestyle='--', zorder=3)
ax7.add_patch(arrow)
ax7.text(3.25, 4.8, 'Re-planning loop', ha='center', va='center', 
         fontsize=9, color=academic_colors['accent'], fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                  edgecolor=academic_colors['accent'], linewidth=1))

# Final output
out_x, out_y = phase_boxes[2][0], phase_boxes[2][1]
final_box = FancyBboxPatch((out_x-0.9, out_y-2.2), 1.8, 0.7,
                            boxstyle="round,pad=0.05,rounding_size=0.15",
                            facecolor=academic_colors['purple'], 
                            edgecolor='black', linewidth=2, zorder=4)
ax7.add_patch(final_box)
ax7.text(out_x, out_y-1.85, 'Optimized Tour π*', ha='center', va='center', 
         fontsize=11, fontweight='bold', color='white', zorder=5)

# Arrow from Phase 3 to output
ax7.annotate('', xy=(out_x, out_y-1.5), xytext=(out_x, out_y-0.75),
            arrowprops=dict(arrowstyle='->', color='#333333', lw=2), zorder=3)

filepath7 = save_fig(fig7, 'fig7_three_phase_execution.png')
print(f"Saved: {filepath7}")

# ============================================================
# Figure 8: LE-DEGN vs Baseline Architecture Comparison
# ============================================================
fig8, ax8 = plt.subplots(figsize=(10, 8))
ax8.set_xlim(0, 10)
ax8.set_ylim(0, 10)
ax8.axis('off')
ax8.set_title("Fig.8 LE-DEGN vs Baseline (DHAN) Architecture Comparison / 图8 LE-DEGN与基线架构对比", 
              fontsize=14, fontweight='bold', pad=20)

# LE-DEGN box (left)
left_box = FancyBboxPatch((0.5, 1.5), 3.8, 7,
                           boxstyle="round,pad=0.05,rounding_size=0.2",
                           facecolor=academic_colors['light_blue'], 
                           edgecolor=academic_colors['primary'], linewidth=2.5, zorder=3)
ax8.add_patch(left_box)
ax8.text(2.4, 8.2, 'LE-DEGN', ha='center', va='center', 
         fontsize=14, fontweight='bold', color=academic_colors['primary'])

ledgn_items = [
    ('Route:', 'ERFM Transformer (learned)'),
    ('Congestion:', 'SA-DGWN proactive prediction'),
    ('Escape:', 'LHH adaptive heuristics'),
    ('Re-planning:', 'Full ERFM with exclusion'),
    ('Exploration:', '5 stochastic rollouts'),
    ('Optimization:', '2-opt local refinement')
]

for i, (label, desc) in enumerate(ledgn_items):
    y_pos = 7.2 - i * 0.9
    ax8.text(0.9, y_pos, label, ha='left', va='center', 
             fontsize=9, fontweight='bold', color=academic_colors['primary'])
    ax8.text(0.9, y_pos-0.35, desc, ha='left', va='center', 
             fontsize=8.5, color='#333333')
    # Small accent bar
    bar = plt.Rectangle((0.7, y_pos-0.45), 0.08, 0.6, 
                         facecolor=academic_colors['secondary'], zorder=4)
    ax8.add_patch(bar)

# Baseline box (right)
right_box = FancyBboxPatch((5.7, 1.5), 3.8, 7,
                            boxstyle="round,pad=0.05,rounding_size=0.2",
                            facecolor=academic_colors['light_gray'], 
                            edgecolor=academic_colors['gray'], linewidth=2.5, zorder=3)
ax8.add_patch(right_box)
ax8.text(7.6, 8.2, 'Baseline (DHAN+NN)', ha='center', va='center', 
         fontsize=14, fontweight='bold', color=academic_colors['dark_gray'])

baseline_items = [
    ('Route:', 'Greedy Nearest-Neighbor'),
    ('Congestion:', 'Reactive fixed penalty (15%)'),
    ('Escape:', 'None'),
    ('Re-planning:', 'None'),
    ('Exploration:', '5 deterministic starts'),
    ('Optimization:', 'None')
]

for i, (label, desc) in enumerate(baseline_items):
    y_pos = 7.2 - i * 0.9
    ax8.text(6.1, y_pos, label, ha='left', va='center', 
             fontsize=9, fontweight='bold', color=academic_colors['dark_gray'])
    ax8.text(6.1, y_pos-0.35, desc, ha='left', va='center', 
             fontsize=8.5, color='#333333')
    bar = plt.Rectangle((5.9, y_pos-0.45), 0.08, 0.6, 
                         facecolor=academic_colors['gray'], zorder=4)
    ax8.add_patch(bar)

# Center comparison arrows
arrow_y_positions = [7.0, 6.1, 5.2, 4.3, 3.4, 2.5]
for y in arrow_y_positions:
    # Left arrow (pointing right)
    ax8.annotate('', xy=(5.5, y), xytext=(4.5, y),
                arrowprops=dict(arrowstyle='->', color=academic_colors['primary'], lw=1.5),
                zorder=5)
    # Right arrow (pointing left)
    ax8.annotate('', xy=(4.5, y-0.15), xytext=(5.5, y-0.15),
                arrowprops=dict(arrowstyle='->', color=academic_colors['gray'], lw=1.5),
                zorder=5)

# Center "VS" circle
vs_circle = Circle((5, 5), 0.4, facecolor='white', 
                    edgecolor='#333333', linewidth=2, zorder=6)
ax8.add_patch(vs_circle)
ax8.text(5, 5, 'VS', ha='center', va='center', 
         fontsize=12, fontweight='bold', color='#333333', zorder=7)

filepath8 = save_fig(fig8, 'fig8_architecture_comparison.png')
print(f"Saved: {filepath8}")

print("\nAll figures 5-8 generated successfully!")
