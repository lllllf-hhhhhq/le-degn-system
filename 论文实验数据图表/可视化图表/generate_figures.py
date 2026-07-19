import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# Global settings
DPI = 300
FIGSIZE = (12, 9)
COLORS = {
    'blue': '#1f77b4',
    'orange': '#ff7f0e',
    'green': '#2ca02c',
    'red': '#d62728',
    'purple': '#9467bd',
    'lightblue': '#aec7e8',
    'pink': '#ffbb78',
}

plt.rcParams['font.family'] = 'DejaVu Sans'


def save_fig(fig, name):
    path = f"c:\\Users\\dell\\Desktop\\le_degn_system\\论文实验数据图表\\可视化图表\\{name}"
    fig.savefig(path, dpi=DPI, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
    print(f"Saved: {path}")


# ============================================================
# Figure 1: Kinematic Constraints and Turn Penalties
# ============================================================
def draw_fig1():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("Kinematic Constraints and Turn Penalties", fontsize=18, fontweight='bold', pad=20)

    # Three columns
    col_width = 4.0
    cols_x = [0.5, 4.5, 8.5]

    # ---------- Left Column: Width-Based Unidirectional ----------
    x = cols_x[0]
    ax.text(x + 1.5, 8.3, "Width < 4.5m → One-way", fontsize=13, ha='center', va='center', fontweight='bold')

    # Wide road (5.0m)
    wide_rect = FancyBboxPatch((x + 0.2, 6.0), 2.6, 0.8, boxstyle="round,pad=0.3",
                                facecolor=COLORS['green'], edgecolor='black', linewidth=1.5)
    ax.add_patch(wide_rect)
    ax.text(x + 1.5, 6.4, "5.0m (Bidirectional)", fontsize=11, ha='center', va='center', color='white', fontweight='bold')
    # Bidirectional arrow
    ax.annotate('', xy=(x + 2.5, 5.5), xytext=(x + 0.5, 5.5),
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(x + 1.5, 5.2, "Two-way", fontsize=11, ha='center', va='center')

    # Narrow road (3.0m)
    narrow_rect = FancyBboxPatch((x + 0.5, 3.2), 2.0, 0.6, boxstyle="round,pad=0.3",
                                  facecolor=COLORS['red'], edgecolor='black', linewidth=1.5)
    ax.add_patch(narrow_rect)
    ax.text(x + 1.5, 3.5, "3.0m (One-way)", fontsize=11, ha='center', va='center', color='white', fontweight='bold')
    # One-way arrow
    ax.annotate('', xy=(x + 2.2, 2.6), xytext=(x + 0.8, 2.6),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(x + 1.5, 2.3, "One-way", fontsize=11, ha='center', va='center')
    ax.text(x + 1.5, 1.6, "Remove reverse edge", fontsize=11, ha='center', va='center', color=COLORS['red'])

    # ---------- Middle Column: Narrow Lane Friction ----------
    x = cols_x[1]
    ax.text(x + 1.5, 8.3, "3.0 ≤ Width < 4.5m → Cost × 1.5", fontsize=13, ha='center', va='center', fontweight='bold')

    # Medium road
    med_rect = FancyBboxPatch((x + 0.5, 5.8), 2.0, 0.7, boxstyle="round,pad=0.3",
                               facecolor=COLORS['orange'], edgecolor='black', linewidth=1.5)
    ax.add_patch(med_rect)
    ax.text(x + 1.5, 6.15, "3.8m", fontsize=11, ha='center', va='center', color='white', fontweight='bold')

    # Formula box
    formula_rect = FancyBboxPatch((x + 0.3, 3.8), 2.4, 0.9, boxstyle="round,pad=0.3",
                                   facecolor='white', edgecolor=COLORS['orange'], linewidth=2)
    ax.add_patch(formula_rect)
    ax.text(x + 1.5, 4.25, r"$cost = cost_{base} \times 1.5$", fontsize=13, ha='center', va='center')

    ax.text(x + 1.5, 3.0, "Friction Penalty", fontsize=13, ha='center', va='center', color=COLORS['orange'], fontweight='bold')

    # ---------- Right Column: Turn Penalties ----------
    x = cols_x[2]
    ax.text(x + 1.5, 8.3, "Turn Penalties at Intersection", fontsize=13, ha='center', va='center', fontweight='bold')

    # Draw intersection (cross)
    road_w = 0.5
    # Vertical road
    v_rect = FancyBboxPatch((x + 1.25, 2.5), road_w, 3.5, boxstyle="round,pad=0.1",
                             facecolor='#cccccc', edgecolor='black', linewidth=1)
    ax.add_patch(v_rect)
    # Horizontal road
    h_rect = FancyBboxPatch((x + 0.25, 4.0), 3.0, road_w, boxstyle="round,pad=0.1",
                             facecolor='#cccccc', edgecolor='black', linewidth=1)
    ax.add_patch(h_rect)

    # Straight arrow (up)
    ax.annotate('', xy=(x + 1.5, 5.8), xytext=(x + 1.5, 4.7),
                arrowprops=dict(arrowstyle='->', color=COLORS['green'], lw=2.5))
    ax.text(x + 2.3, 5.3, "Straight: +0.0s", fontsize=11, ha='left', va='center', color=COLORS['green'])

    # Left turn arrow (curved left)
    left_turn = FancyArrowPatch((x + 1.5, 4.25), (x + 0.4, 4.25),
                                 connectionstyle="arc3,rad=0.4", arrowstyle='->',
                                 mutation_scale=20, color=COLORS['orange'], lw=2.5)
    ax.add_patch(left_turn)
    ax.text(x + 0.3, 3.5, "Left turn: +1.5s", fontsize=11, ha='center', va='center', color=COLORS['orange'])

    # U-turn arrow (big U)
    uturn = FancyArrowPatch((x + 1.5, 4.25), (x + 1.5, 2.7),
                             connectionstyle="arc3,rad=0.7", arrowstyle='->',
                             mutation_scale=20, color=COLORS['red'], lw=3)
    ax.add_patch(uturn)
    ax.text(x + 2.6, 3.5, "U-turn: +7.0s", fontsize=11, ha='left', va='center', color=COLORS['red'], fontweight='bold')

    save_fig(fig, "fig1_kinematic_constraints.png")


# ============================================================
# Figure 2: Primal Graph to Line Graph Transformation
# ============================================================
def draw_fig2():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("Primal Graph to Line Graph Transformation", fontsize=18, fontweight='bold', pad=20)

    # ---------- Left: Primal Graph ----------
    ax.text(2.5, 8.0, "Primal Graph", fontsize=16, ha='center', va='center', fontweight='bold', color=COLORS['blue'])

    # Triangle nodes
    A = (2.5, 6.5)
    B = (1.0, 3.5)
    C = (4.0, 3.5)
    r = 0.25

    for pos, label in [(A, 'A'), (B, 'B'), (C, 'C')]:
        circ = Circle(pos, r, facecolor=COLORS['blue'], edgecolor='black', linewidth=1.5, zorder=5)
        ax.add_patch(circ)
        ax.text(pos[0], pos[1], label, fontsize=12, ha='center', va='center', color='white', fontweight='bold', zorder=6)

    # Edges with arrows
    ax.annotate('', xy=(B[0]+0.2, B[1]+0.35), xytext=(A[0]-0.15, A[1]-0.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(1.4, 5.3, "e3", fontsize=11, ha='center', va='center', color='black')

    ax.annotate('', xy=(C[0]-0.2, C[1]+0.35), xytext=(A[0]+0.15, A[1]-0.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(3.6, 5.3, "e2", fontsize=11, ha='center', va='center', color='black')

    ax.annotate('', xy=(C[0]-0.3, C[1]), xytext=(B[0]+0.3, B[1]),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(2.5, 3.2, "e1", fontsize=11, ha='center', va='center', color='black')

    ax.text(2.5, 2.0, "Nodes = Junctions", fontsize=11, ha='center', va='center')
    ax.text(2.5, 1.5, "Edges = Roads", fontsize=11, ha='center', va='center')

    # ---------- Middle: Transform Arrow ----------
    transform_arrow = FancyArrowPatch((4.8, 5.0), (7.2, 5.0),
                                       connectionstyle="arc3,rad=0.3", arrowstyle='->',
                                       mutation_scale=25, color='black', lw=3)
    ax.add_patch(transform_arrow)
    ax.text(6.0, 6.0, "Transform", fontsize=13, ha='center', va='center', fontweight='bold')

    # ---------- Right: Line Graph ----------
    ax.text(9.5, 8.0, "Line Graph", fontsize=16, ha='center', va='center', fontweight='bold', color=COLORS['orange'])

    # Triangle nodes for line graph
    e1 = (9.5, 3.5)
    e2 = (11.0, 6.5)
    e3 = (8.0, 6.5)

    for pos, label in [(e1, 'e1'), (e2, 'e2'), (e3, 'e3')]:
        circ = Circle(pos, r, facecolor=COLORS['orange'], edgecolor='black', linewidth=1.5, zorder=5)
        ax.add_patch(circ)
        ax.text(pos[0], pos[1], label, fontsize=12, ha='center', va='center', color='white', fontweight='bold', zorder=6)

    # Edges
    ax.annotate('', xy=(e2[0]-0.2, e2[1]-0.35), xytext=(e1[0]+0.15, e1[1]+0.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.annotate('', xy=(e3[0]+0.2, e3[1]-0.35), xytext=(e2[0]-0.15, e2[1]-0.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.annotate('', xy=(e1[0]-0.15, e1[1]+0.2), xytext=(e3[0]+0.2, e3[1]-0.35),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    ax.text(9.5, 2.0, "Nodes = Roads", fontsize=11, ha='center', va='center')
    ax.text(9.5, 1.5, "Edges = Connectivity", fontsize=11, ha='center', va='center')

    save_fig(fig, "fig2_line_graph_transform.png")


# ============================================================
# Figure 3: ERFM Encoder-Decoder Architecture
# ============================================================
def draw_fig3():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("ERFM Encoder-Decoder Architecture", fontsize=18, fontweight='bold', pad=20)

    # ---------- Left Input ----------
    in1 = FancyBboxPatch((0.5, 5.5), 1.8, 1.0, boxstyle="round,pad=0.3",
                          facecolor=COLORS['blue'], edgecolor='black', linewidth=1.5)
    ax.add_patch(in1)
    ax.text(1.4, 6.0, "Edge Features\n(13-D)", fontsize=11, ha='center', va='center', color='white', fontweight='bold')

    in2 = FancyBboxPatch((0.5, 4.0), 1.8, 1.0, boxstyle="round,pad=0.3",
                          facecolor=COLORS['blue'], edgecolor='black', linewidth=1.5)
    ax.add_patch(in2)
    ax.text(1.4, 4.5, "Global Attr\n(4-D)", fontsize=11, ha='center', va='center', color='white', fontweight='bold')

    # ---------- Encoder ----------
    enc = FancyBboxPatch((3.0, 3.5), 3.0, 3.5, boxstyle="round,pad=0.3",
                          facecolor=COLORS['orange'], edgecolor='black', linewidth=2)
    ax.add_patch(enc)
    ax.text(4.5, 6.5, "Encoder", fontsize=14, ha='center', va='center', color='white', fontweight='bold')

    # Internal blocks
    for i, label in enumerate(["Transformer Block 1", "Transformer Block 2", "Transformer Block 3"]):
        y = 5.7 - i * 0.7
        blk = FancyBboxPatch((3.3, y), 2.4, 0.5, boxstyle="round,pad=0.15",
                              facecolor='white', edgecolor=COLORS['orange'], linewidth=1.5)
        ax.add_patch(blk)
        ax.text(4.5, y + 0.25, label, fontsize=10, ha='center', va='center', color='black')

    ax.text(4.5, 3.8, "+ PenaltyBiasAttention", fontsize=11, ha='center', va='center', color='white', fontweight='bold')

    # Arrows from input to encoder
    ax.annotate('', xy=(3.0, 6.0), xytext=(2.3, 6.0),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.annotate('', xy=(3.0, 4.5), xytext=(2.3, 4.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # ---------- Decoder ----------
    dec = FancyBboxPatch((7.0, 4.0), 2.5, 2.5, boxstyle="round,pad=0.3",
                          facecolor=COLORS['green'], edgecolor='black', linewidth=2)
    ax.add_patch(dec)
    ax.text(8.25, 5.8, "Decoder", fontsize=14, ha='center', va='center', color='white', fontweight='bold')
    ax.text(8.25, 5.0, "Autoregressive\nSampling", fontsize=11, ha='center', va='center', color='white')
    ax.text(8.25, 4.3, "→ Tour π", fontsize=12, ha='center', va='center', color='white', fontweight='bold')

    # Arrow encoder -> decoder
    ax.annotate('', xy=(7.0, 5.25), xytext=(6.0, 5.25),
                arrowprops=dict(arrowstyle='->', color='black', lw=2.5))

    # ---------- Value Head ----------
    vh = FancyBboxPatch((3.5, 0.8), 2.0, 1.2, boxstyle="round,pad=0.3",
                         facecolor=COLORS['purple'], edgecolor='black', linewidth=2)
    ax.add_patch(vh)
    ax.text(4.5, 1.7, "Value Head", fontsize=12, ha='center', va='center', color='white', fontweight='bold')
    ax.text(4.5, 1.1, "→ V(s)", fontsize=12, ha='center', va='center', color='white', fontweight='bold')

    # Arrow encoder -> value head
    ax.annotate('', xy=(4.5, 2.0), xytext=(4.5, 3.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=2.5))

    save_fig(fig, "fig3_erfm_architecture.png")


# ============================================================
# Figure 4: SA-DGWN Spatio-Temporal Network
# ============================================================
def draw_fig4():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("SA-DGWN Spatio-Temporal Network", fontsize=18, fontweight='bold', pad=20)

    layers = [
        ("Input", "Speed & Flow\n(12 timesteps)", COLORS['blue']),
        ("Dilated Causal Conv", "Dilated Causal Conv\nd = 1, 2, 4, 8", COLORS['lightblue']),
        ("Graph Conv", "Graph Conv\nA/D normalized", COLORS['green']),
        ("Gating", "Gating\nσ(W · h)", '#ff99cc'),
        ("Output", "Congestion Probability\np̂ ∈ [0, 1]", COLORS['orange']),
    ]

    box_w = 5.0
    box_h = 1.2
    x_center = 5.0
    y_start = 7.5
    y_gap = 1.4

    for i, (name, text, color) in enumerate(layers):
        y = y_start - i * y_gap
        rect = FancyBboxPatch((x_center - box_w/2, y - box_h/2), box_w, box_h,
                               boxstyle="round,pad=0.3", facecolor=color,
                               edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x_center, y, text, fontsize=12, ha='center', va='center', color='black', fontweight='bold')

        if i < len(layers) - 1:
            y_next = y_start - (i+1) * y_gap
            arrow = FancyArrowPatch((x_center, y - box_h/2 - 0.05), (x_center, y_next + box_h/2 + 0.05),
                                     arrowstyle='->', mutation_scale=20, color='black', lw=2)
            ax.add_patch(arrow)

    # Right side labels
    ax.text(8.5, 6.8, "Temporal", fontsize=13, ha='center', va='center', fontweight='bold',
            rotation=90, color=COLORS['blue'])
    ax.text(8.5, 4.0, "Spatial", fontsize=13, ha='center', va='center', fontweight='bold',
            rotation=90, color=COLORS['green'])

    # Brackets or lines to indicate grouping
    ax.plot([8.0, 8.0], [7.0, 5.5], color=COLORS['blue'], lw=2, linestyle='--')
    ax.plot([8.0, 8.0], [4.8, 3.3], color=COLORS['green'], lw=2, linestyle='--')

    save_fig(fig, "fig4_sadgwn_structure.png")


if __name__ == "__main__":
    draw_fig1()
    draw_fig2()
    draw_fig3()
    draw_fig4()
    print("All 4 figures generated successfully!")
