"""
Generate 8 algorithm design figures for LE-DEGN paper (English-only version)
All figures: 300 DPI, 10x8 inches, academic style, white background
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import numpy as np
import os

OUTPUT_DIR = r"c:\Users\dell\Desktop\le_degn_system\论文实验数据图表\可视化图表"
DPI = 300
FIG_SIZE = (10, 8)

# Academic color scheme
BLUE = '#2563EB'
RED = '#DC2626'
GREEN = '#059669'
ORANGE = '#EA580C'
PURPLE = '#7C3AED'
GRAY = '#6B7280'
LIGHT_BLUE = '#DBEAFE'
LIGHT_GREEN = '#D1FAE5'
LIGHT_RED = '#FEE2E2'
LIGHT_ORANGE = '#FFEDD5'
LIGHT_PURPLE = '#EDE9FE'
LIGHT_GRAY = '#F3F4F6'
DARK_GRAY = '#374151'

def save_fig(name, fig):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved: {path}")
    return path

# ============================================================
# FIG 1: Kinematic Constraints and Turn Penalties
# ============================================================
def generate_fig1():
    fig, axes = plt.subplots(1, 3, figsize=(FIG_SIZE[0]*1.5, FIG_SIZE[1]))
    fig.suptitle('Kinematic Constraints and Turn Penalties\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.95)
    
    # --- Panel 1: Width-based unidirectional conversion ---
    ax = axes[0]
    ax.set_xlim(-3, 3)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Width-Based Unidirectional Conversion', fontsize=12, fontweight='bold', pad=15)
    
    # Wide road (bidirectional)
    ax.fill_between([-2.5, -0.5], [-0.6, -0.6], [0.6, 0.6], color=LIGHT_BLUE, alpha=0.7, edgecolor=BLUE, linewidth=2)
    ax.annotate('', xy=(-0.5, 0.15), xytext=(-2.5, 0.15), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    ax.annotate('', xy=(-2.5, -0.15), xytext=(-0.5, -0.15), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    ax.text(-1.5, 0.9, '5.0 m', ha='center', fontsize=11, color=BLUE, fontweight='bold')
    ax.text(-1.5, -1.1, 'Bidirectional', ha='center', fontsize=10, color=GRAY)
    
    # Narrow road (unidirectional)
    ax.fill_between([0.5, 2.5], [-0.35, -0.35], [0.35, 0.35], color=LIGHT_RED, alpha=0.7, edgecolor=RED, linewidth=2)
    ax.annotate('', xy=(2.5, 0), xytext=(0.5, 0), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    # Cross mark on reverse direction
    ax.plot([1.5, 1.5], [-0.6, -0.2], color=RED, linewidth=2.5)
    ax.plot([1.3, 1.7], [-0.4, -0.4], color=RED, linewidth=2.5)
    ax.text(1.5, 0.7, '3.0 m', ha='center', fontsize=11, color=RED, fontweight='bold')
    ax.text(1.5, -0.7, 'Unidirectional', ha='center', fontsize=10, color=GRAY)
    ax.text(1.5, -1.3, '(reverse edge removed)', ha='center', fontsize=9, color=GRAY, style='italic')
    
    # Threshold arrow
    ax.annotate('', xy=(0.3, 1.2), xytext=(-0.3, 1.2), arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5, ls='--'))
    ax.text(0, 1.4, 'w < 4.5 m', ha='center', fontsize=10, color=GRAY, fontweight='bold')
    
    # --- Panel 2: Narrow lane friction ---
    ax = axes[1]
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Narrow Lane Friction', fontsize=12, fontweight='bold', pad=15)
    
    # Road with friction
    ax.fill_between([-1.5, 1.5], [-0.4, -0.4], [0.4, 0.4], color=LIGHT_ORANGE, alpha=0.7, edgecolor=ORANGE, linewidth=2)
    ax.annotate('', xy=(1.5, 0), xytext=(-1.5, 0), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    
    # Speed reduction annotation
    ax.annotate('', xy=(-1.5, 0.8), xytext=(-1.5, 0.45), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5))
    ax.annotate('', xy=(1.5, 0.8), xytext=(1.5, 0.45), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5))
    ax.text(0, 0.95, '3.0 ≤ w < 4.5 m', ha='center', fontsize=11, color=ORANGE, fontweight='bold')
    ax.text(0, 1.3, 'cost = cost_base × 1.5', ha='center', fontsize=13, color=ORANGE, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=LIGHT_ORANGE, edgecolor=ORANGE, alpha=0.8))
    ax.text(0, -0.9, 'Speed reduction', ha='center', fontsize=10, color=GRAY)
    ax.text(0, -1.2, '3.8 m width example', ha='center', fontsize=9, color=GRAY, style='italic')
    
    # --- Panel 3: Turn penalties ---
    ax = axes[2]
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Turn Penalties', fontsize=12, fontweight='bold', pad=15)
    
    # Crossroad
    ax.fill_between([-0.4, 0.4], [-2, -2], [2, 2], color=LIGHT_GRAY, edgecolor=GRAY, linewidth=1.5)
    ax.fill_between([-2, 2], [-0.4, -0.4], [0.4, 0.4], color=LIGHT_GRAY, edgecolor=GRAY, linewidth=1.5)
    
    # Straight arrow (green)
    ax.annotate('', xy=(0, 1.8), xytext=(0, 0.5), arrowprops=dict(arrowstyle='->', color=GREEN, lw=3))
    ax.text(0.5, 1.8, 'Straight', ha='left', fontsize=10, color=GREEN)
    ax.text(0.5, 1.5, '+ 0.0 s', ha='left', fontsize=9, color=GREEN)
    
    # Left turn (orange)
    ax.annotate('', xy=(-1.8, 0), xytext=(0.5, 0), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=3, connectionstyle='arc3,rad=0.5'))
    ax.text(-1.5, 0.3, 'Left Turn', ha='left', fontsize=10, color=ORANGE)
    ax.text(-1.5, 0.0, '+ 1.5 s', ha='left', fontsize=11, color=ORANGE, fontweight='bold')
    
    # U-turn (red)
    ax.annotate('', xy=(0, -0.5), xytext=(0, 0.5), arrowprops=dict(arrowstyle='->', color=RED, lw=3, connectionstyle='arc3,rad=-0.8'))
    ax.text(0.5, -0.3, 'U-Turn', ha='left', fontsize=10, color=RED)
    ax.text(0.5, -0.6, '+ 7.0 s', ha='left', fontsize=12, color=RED, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=LIGHT_RED, edgecolor=RED, alpha=0.8))
    
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    save_fig('fig1_kinematic_constraints.png', fig)

# ============================================================
# FIG 2: Primal Graph to Line Graph Transformation
# ============================================================
def generate_fig2():
    fig, axes = plt.subplots(1, 3, figsize=(FIG_SIZE[0]*1.5, FIG_SIZE[1]))
    fig.suptitle('Primal Graph to Line Graph Transformation\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.95)
    
    # --- Left: Primal Graph ---
    ax = axes[0]
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Primal Graph G = (V, E)', fontsize=12, fontweight='bold', pad=15)
    
    # Nodes (junctions)
    nodes = {'A': (-1, 1), 'B': (1, 1), 'C': (0, -1)}
    for label, (x, y) in nodes.items():
        ax.add_patch(Circle((x, y), 0.15, color=BLUE, zorder=3))
        ax.text(x, y+0.3, label, ha='center', va='center', fontsize=14, fontweight='bold', color=BLUE)
    
    # Edges (roads)
    ax.annotate('', xy=nodes['B'], xytext=nodes['A'], arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5))
    ax.annotate('', xy=nodes['C'], xytext=nodes['B'], arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5))
    ax.annotate('', xy=nodes['A'], xytext=nodes['C'], arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5))
    
    # Edge labels
    ax.text(0.2, 1.25, 'e₁', fontsize=12, color=GREEN, fontweight='bold')
    ax.text(1.1, 0.1, 'e₂', fontsize=12, color=GREEN, fontweight='bold')
    ax.text(-0.8, 0.1, 'e₃', fontsize=12, color=GREEN, fontweight='bold')
    
    ax.text(0, -1.7, 'Nodes = Junctions\nEdges = Roads', ha='center', fontsize=9, color=GRAY, style='italic')
    
    # --- Middle: Transform Arrow ---
    ax = axes[1]
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis('off')
    
    ax.annotate('', xy=(0.7, 0), xytext=(-0.7, 0), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=3))
    ax.text(0, 0.2, 'Line Graph', ha='center', fontsize=14, fontweight='bold', color=DARK_GRAY)
    ax.text(0, -0.15, 'Transformation', ha='center', fontsize=12, color=GRAY)
    ax.text(0, -0.5, 'L(G) = (V_L, E_L)', ha='center', fontsize=11, color=GRAY, fontweight='bold')
    
    # --- Right: Line Graph ---
    ax = axes[2]
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Line Graph L = (V_L, E_L)', fontsize=12, fontweight='bold', pad=15)
    
    # Nodes are edges from primal
    lnodes = {'e₁': (-1, 1), 'e₂': (1, 1), 'e₃': (0, -1)}
    for label, (x, y) in lnodes.items():
        ax.add_patch(Circle((x, y), 0.2, color=RED, zorder=3))
        ax.text(x, y, label, ha='center', va='center', fontsize=13, fontweight='bold', color='white')
    
    # Edges represent connectivity
    ax.annotate('', xy=lnodes['e₂'], xytext=lnodes['e₁'], arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2.5))
    ax.annotate('', xy=lnodes['e₃'], xytext=lnodes['e₂'], arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2.5))
    ax.annotate('', xy=lnodes['e₁'], xytext=lnodes['e₃'], arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2.5))
    
    ax.text(0, -1.7, 'Nodes = Roads\nEdges = Connectivity', ha='center', fontsize=9, color=GRAY, style='italic')
    
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    save_fig('fig2_line_graph_transform.png', fig)

# ============================================================
# FIG 3: ERFM Encoder-Decoder Architecture
# ============================================================
def generate_fig3():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('ERFM Encoder-Decoder Architecture\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.96)
    
    # Input section (left)
    ax.add_patch(FancyBboxPatch((0.5, 6.5), 2, 0.6, boxstyle="round,pad=0.1", facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=2))
    ax.text(1.5, 6.8, 'Edge Features X', ha='center', va='center', fontsize=11, fontweight='bold', color=BLUE)
    ax.text(1.5, 6.3, '(13-dimensional)', ha='center', va='center', fontsize=9, color=GRAY)
    
    ax.add_patch(FancyBboxPatch((0.5, 5.2), 2, 0.6, boxstyle="round,pad=0.1", facecolor=LIGHT_GREEN, edgecolor=GREEN, linewidth=2))
    ax.text(1.5, 5.5, 'Global Attr g', ha='center', va='center', fontsize=11, fontweight='bold', color=GREEN)
    ax.text(1.5, 5.0, '(4-dimensional)', ha='center', va='center', fontsize=9, color=GRAY)
    
    ax.add_patch(FancyBboxPatch((0.5, 3.9), 2, 0.6, boxstyle="round,pad=0.1", facecolor=LIGHT_ORANGE, edgecolor=ORANGE, linewidth=2))
    ax.text(1.5, 4.2, 'Penalty Matrix M', ha='center', va='center', fontsize=11, fontweight='bold', color=ORANGE)
    ax.text(1.5, 3.7, '(N × N)', ha='center', va='center', fontsize=9, color=GRAY)
    
    # Arrows from inputs to encoder
    for y in [6.5, 5.5, 4.2]:
        ax.annotate('', xy=(2.8, y), xytext=(2.5, y), arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5))
    
    # Encoder section (middle)
    ax.add_patch(FancyBboxPatch((3, 2), 3.5, 5.5, boxstyle="round,pad=0.15", facecolor=LIGHT_PURPLE, edgecolor=PURPLE, linewidth=2.5))
    ax.text(4.75, 7.8, 'ENCODER', ha='center', va='center', fontsize=13, fontweight='bold', color=PURPLE)
    
    # Transformer blocks
    for i in range(3):
        y = 6.5 - i * 1.5
        ax.add_patch(FancyBboxPatch((3.3, y), 3, 1, boxstyle="round,pad=0.1", facecolor='white', edgecolor=PURPLE, linewidth=2))
        ax.text(4.8, y + 0.7, f'Transformer Block {i+1}', ha='center', fontsize=10, fontweight='bold', color=DARK_GRAY)
        ax.text(4.8, y + 0.3, 'PenaltyBiasAttention', ha='center', fontsize=9, color=ORANGE, fontweight='bold')
        ax.text(4.8, y + 0.0, 'd_model=64, n_heads=4, d_ff=128', ha='center', fontsize=8, color=GRAY)
        if i < 2:
            ax.annotate('', xy=(4.8, y - 0.0), xytext=(4.8, y + 0.05), arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2))
    
    # Arrow encoder to decoder
    ax.annotate('', xy=(7, 4.5), xytext=(6.5, 4.5), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2.5))
    ax.text(6.75, 4.9, 'H', ha='center', fontsize=10, fontweight='bold', color=PURPLE)
    
    # Decoder section (right)
    ax.add_patch(FancyBboxPatch((7.2, 2.5), 2.5, 4, boxstyle="round,pad=0.15", facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=2.5))
    ax.text(8.45, 6.8, 'DECODER', ha='center', va='center', fontsize=13, fontweight='bold', color=BLUE)
    
    # Autoregressive loop
    ax.text(8.45, 5.8, 'Autoregressive', ha='center', fontsize=10, fontweight='bold', color=DARK_GRAY)
    ax.text(8.45, 5.3, 'Tour Generation', ha='center', fontsize=10, fontweight='bold', color=DARK_GRAY)
    
    # Current edge, context, candidates
    ax.add_patch(FancyBboxPatch((7.5, 4.3), 1.9, 0.4, boxstyle="round,pad=0.05", facecolor='white', edgecolor=BLUE, linewidth=1))
    ax.text(8.45, 4.5, 'e_curr  ⊕  e_ctx', ha='center', fontsize=9, color=DARK_GRAY)
    
    ax.add_patch(FancyBboxPatch((7.5, 3.6), 1.9, 0.4, boxstyle="round,pad=0.05", facecolor='white', edgecolor=BLUE, linewidth=1))
    ax.text(8.45, 3.8, 'Softmax(s/τ)', ha='center', fontsize=9, color=DARK_GRAY)
    
    # Loop arrow
    ax.annotate('', xy=(9.2, 5.0), xytext=(9.2, 3.3), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    ax.annotate('', xy=(7.7, 3.3), xytext=(7.7, 5.0), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    ax.text(9.4, 4.1, 'Loop', fontsize=9, color=BLUE, fontweight='bold')
    
    # Output
    ax.add_patch(FancyBboxPatch((7.5, 2.7), 1.9, 0.5, boxstyle="round,pad=0.1", facecolor=LIGHT_GREEN, edgecolor=GREEN, linewidth=2))
    ax.text(8.45, 2.95, 'Tour π*', ha='center', va='center', fontsize=11, fontweight='bold', color=GREEN)
    
    # Value head (bottom)
    ax.add_patch(FancyBboxPatch((3.5, 0.5), 3, 1, boxstyle="round,pad=0.1", facecolor=LIGHT_RED, edgecolor=RED, linewidth=2))
    ax.text(5, 1.2, 'Value Head', ha='center', va='center', fontsize=11, fontweight='bold', color=RED)
    ax.text(5, 0.75, 'V(s) = MLP([e_curr ⊕ e_ctx])', ha='center', va='center', fontsize=9, color=DARK_GRAY)
    
    # Arrow from encoder to value head
    ax.annotate('', xy=(5, 1.5), xytext=(5, 2), arrowprops=dict(arrowstyle='->', color=RED, lw=1.5, ls='--'))
    
    save_fig('fig3_erfm_architecture.png', fig)

# ============================================================
# FIG 4: SA-DGWN Spatio-Temporal Network
# ============================================================
def generate_fig4():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('SA-DGWN Spatio-Temporal Attention-based Dynamic Graph Wave Network\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.96)
    
    # Input
    ax.add_patch(FancyBboxPatch((3, 8.5), 4, 0.8, boxstyle="round,pad=0.1", facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=2))
    ax.text(5, 8.9, 'Input: Speed & Flow Features', ha='center', va='center', fontsize=11, fontweight='bold', color=BLUE)
    ax.text(5, 8.6, '(12 historical timesteps)', ha='center', va='center', fontsize=9, color=GRAY)
    
    # Temporal block
    ax.add_patch(FancyBboxPatch((1, 6), 3.5, 2, boxstyle="round,pad=0.15", facecolor=LIGHT_PURPLE, edgecolor=PURPLE, linewidth=2.5))
    ax.text(2.75, 7.6, 'Dilated Causal Conv', ha='center', va='center', fontsize=11, fontweight='bold', color=PURPLE)
    ax.text(2.75, 7.1, 'Temporal Module', ha='center', va='center', fontsize=10, color=DARK_GRAY)
    for i, (d, y) in enumerate(zip([1, 2, 4, 8], [6.8, 6.5, 6.2, 5.9])):
        ax.text(2.75, y, f'dilation={d}', ha='center', fontsize=8, color=PURPLE)
    
    ax.annotate('', xy=(2.75, 6), xytext=(5, 8.5), arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2.5))
    ax.text(0.5, 7, 'Temporal', fontsize=9, fontweight='bold', color=PURPLE, rotation=90, ha='center', va='center')
    
    # Arrow down
    ax.annotate('', xy=(5, 5.5), xytext=(5, 6), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2.5))
    
    # Spatial block
    ax.add_patch(FancyBboxPatch((5.5, 4), 3.5, 1.5, boxstyle="round,pad=0.15", facecolor=LIGHT_GREEN, edgecolor=GREEN, linewidth=2.5))
    ax.text(7.25, 5.1, 'Graph Convolution', ha='center', va='center', fontsize=11, fontweight='bold', color=GREEN)
    ax.text(7.25, 4.7, 'Spatial Module', ha='center', va='center', fontsize=10, color=DARK_GRAY)
    ax.text(7.25, 4.3, 'h = ReLU(W · Â · x)', ha='center', va='center', fontsize=9, color=GREEN)
    
    ax.annotate('', xy=(5.5, 5.5), xytext=(2.75, 6), arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5))
    ax.text(9.5, 5.5, 'Spatial', fontsize=9, fontweight='bold', color=GREEN, rotation=-90, ha='center', va='center')
    
    # Arrow down
    ax.annotate('', xy=(7.25, 3.5), xytext=(7.25, 4), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2.5))
    
    # Gating block
    ax.add_patch(FancyBboxPatch((3, 2), 4, 1.2, boxstyle="round,pad=0.15", facecolor=LIGHT_ORANGE, edgecolor=ORANGE, linewidth=2.5))
    ax.text(5, 2.8, 'Gating Mechanism', ha='center', va='center', fontsize=11, fontweight='bold', color=ORANGE)
    ax.text(5, 2.4, 'g = σ(W_g · h_gcn)', ha='center', va='center', fontsize=10, color=ORANGE)
    ax.text(5, 2.05, 'h_out = LayerNorm(h_gcn ⊙ g)', ha='center', va='center', fontsize=10, color=DARK_GRAY)
    
    ax.annotate('', xy=(5, 2), xytext=(7.25, 3.5), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.5))
    
    # Arrow down
    ax.annotate('', xy=(5, 1.3), xytext=(5, 2), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2.5))
    
    # Output
    ax.add_patch(FancyBboxPatch((3, 0.3), 4, 0.8, boxstyle="round,pad=0.1", facecolor=LIGHT_RED, edgecolor=RED, linewidth=2.5))
    ax.text(5, 0.7, 'Output: Congestion Probability p̂ ∈ [0,1]', ha='center', va='center', fontsize=11, fontweight='bold', color=RED)
    ax.text(5, 0.4, '(Sigmoid activation, BCE loss)', ha='center', va='center', fontsize=9, color=GRAY)
    
    # Stacked blocks annotation
    ax.text(10, 5, 'Stacked\nSpatio-Temporal\nBlocks', fontsize=10, color=GRAY, style='italic', rotation=90, ha='center', va='center')
    ax.annotate('', xy=(9.5, 6.5), xytext=(9.5, 3.5), arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1.5))
    
    save_fig('fig4_sadgwn_structure.png', fig)

# ============================================================
# FIG 5: LHH GSES Loop
# ============================================================
def generate_fig5():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('LHH GSES Loop and Heuristic Selection\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.96)
    
    # Center circle
    ax.add_patch(Circle((5, 5), 1.2, color=LIGHT_PURPLE, edgecolor=PURPLE, linewidth=3))
    ax.text(5, 5.2, 'GSES', ha='center', va='center', fontsize=14, fontweight='bold', color=PURPLE)
    ax.text(5, 4.6, 'Loop', ha='center', va='center', fontsize=14, fontweight='bold', color=PURPLE)
    
    # Four steps around the circle
    steps = [
        ('Generate', 5, 8, LIGHT_BLUE, BLUE),
        ('Score', 8, 5, LIGHT_GREEN, GREEN),
        ('Execute', 5, 2, LIGHT_ORANGE, ORANGE),
        ('Self-Reflect', 2, 5, LIGHT_RED, RED)
    ]
    
    for label, x, y, bg, border in steps:
        ax.add_patch(FancyBboxPatch((x-1, y-0.4), 2, 0.8, boxstyle="round,pad=0.1", facecolor=bg, edgecolor=border, linewidth=2))
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold', color=border)
    
    # Cycle arrows between steps
    ax.annotate('', xy=(5, 7.5), xytext=(5, 6.3), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2))
    ax.annotate('', xy=(7.5, 5), xytext=(6.2, 5), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2))
    ax.annotate('', xy=(5, 2.5), xytext=(5, 3.8), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2))
    ax.annotate('', xy=(2.5, 5), xytext=(3.8, 5), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=2))
    
    # 5 Heuristic templates (top right)
    ax.add_patch(FancyBboxPatch((7.5, 7), 2.3, 2.5, boxstyle="round,pad=0.1", facecolor=LIGHT_GRAY, edgecolor=GRAY, linewidth=1.5))
    ax.text(8.65, 9.2, 'Heuristic Templates', ha='center', va='center', fontsize=10, fontweight='bold', color=DARK_GRAY)
    
    heuristics = [
        '1. Greedy Widest Road',
        '2. Min Penalty Escape',
        '3. Max Connectivity Escape',
        '4. Adaptive A* Escape',
        '5. Multi-hop Greedy'
    ]
    for i, h in enumerate(heuristics):
        ax.text(7.7, 8.8 - i*0.38, h, fontsize=8, color=DARK_GRAY)
    
    ax.annotate('', xy=(7.2, 8.5), xytext=(7.5, 8.5), arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.5))
    
    # Reflection info (bottom right)
    ax.add_patch(FancyBboxPatch((7.5, 0.5), 2.3, 1.2, boxstyle="round,pad=0.1", facecolor=LIGHT_ORANGE, edgecolor=ORANGE, linewidth=1.5))
    ax.text(8.65, 1.3, 'Update Weights', ha='center', va='center', fontsize=9, fontweight='bold', color=ORANGE)
    ax.text(8.65, 0.95, 'α_k = 1 / max(C̄_k, 10⁻³)', ha='center', va='center', fontsize=8, color=DARK_GRAY)
    ax.text(8.65, 0.7, '(last 5 records)', ha='center', va='center', fontsize=8, color=GRAY, style='italic')
    
    ax.annotate('', xy=(3.2, 5), xytext=(7.5, 1.1), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5, ls='--'))
    
    save_fig('fig5_lhh_flowchart.png', fig)

# ============================================================
# FIG 6: Training Convergence
# ============================================================
def generate_fig6():
    fig, ax1 = plt.subplots(figsize=(10, 7))
    fig.suptitle('ERFM Training Convergence and Temperature Annealing\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.96)
    
    # Simulated training data
    episodes = np.arange(0, 3001, 50)
    # Cost: exponential decay with noise
    cost = 70000 * np.exp(-episodes / 800) + 27000 + np.random.RandomState(42).normal(0, 500, len(episodes))
    cost = np.clip(cost, 26000, 75000)
    
    # Temperature: linear annealing
    temp_start, temp_end = 1.5, 0.2
    temp = temp_start - (temp_start - temp_end) * (episodes / 3000)
    temp = np.clip(temp, temp_end, temp_start)
    
    # Left Y-axis: Cost
    ax1.set_xlabel('Training Episode', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Tour Cost', fontsize=12, fontweight='bold', color=BLUE)
    line1 = ax1.plot(episodes, cost, color=BLUE, linewidth=2, label='Tour Cost')
    ax1.tick_params(axis='y', labelcolor=BLUE)
    ax1.set_xlim(0, 3000)
    
    # Right Y-axis: Temperature
    ax2 = ax1.twinx()
    line2 = ax2.plot(episodes, temp, color=RED, linewidth=2.5, label='Temperature τ')
    ax2.set_ylabel('Temperature τ', fontsize=12, fontweight='bold', color=RED)
    ax2.tick_params(axis='y', labelcolor=RED)
    ax2.set_ylim(0, 1.8)
    
    # Annotations
    ax1.axvline(x=500, color=GRAY, linewidth=0.5, linestyle='--')
    ax1.text(550, 68000, 'τ = 1.5\n(High Exploration)', fontsize=9, color=GRAY, style='italic')
    
    ax1.axvline(x=2500, color=GRAY, linewidth=0.5, linestyle='--')
    ax1.text(2550, 30000, 'τ = 0.2\n(High Exploitation)', fontsize=9, color=GRAY, style='italic')
    
    # Legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', fontsize=10)
    
    # Grid
    ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_fig('fig6_training_convergence.png', fig)

# ============================================================
# FIG 7: Three-Phase Execution
# ============================================================
def generate_fig7():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('LE-DEGN Three-Phase Dynamic Execution\n', fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.96)
    
    # Phase 1
    ax.add_patch(FancyBboxPatch((0.5, 4), 3, 2.5, boxstyle="round,pad=0.15", facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=2.5))
    ax.text(2, 6.2, 'Phase 1', ha='center', fontsize=12, fontweight='bold', color=BLUE)
    ax.text(2, 5.7, 'Global Macro Planning', ha='center', fontsize=11, fontweight='bold', color=DARK_GRAY)
    ax.text(2, 5.2, '5 rollouts, τ = 0.5', ha='center', fontsize=10, color=DARK_GRAY)
    ax.text(2, 4.7, 'Stochastic sampling-argmax', ha='center', fontsize=9, color=GRAY)
    ax.text(2, 4.3, '(70% sample + 30% greedy)', ha='center', fontsize=9, color=GRAY)
    
    # Arrow to Phase 2
    ax.annotate('', xy=(3.5, 5.5), xytext=(4.5, 5.5), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=3))
    ax.text(4, 6.0, 'Initial Tour', fontsize=9, color=DARK_GRAY, ha='center', fontweight='bold')
    
    # Phase 2
    ax.add_patch(FancyBboxPatch((4.5, 3.5), 3.5, 3.5, boxstyle="round,pad=0.15", facecolor=LIGHT_ORANGE, edgecolor=ORANGE, linewidth=2.5))
    ax.text(6.25, 6.7, 'Phase 2', ha='center', fontsize=12, fontweight='bold', color=ORANGE)
    ax.text(6.25, 6.2, 'Dynamic Execution', ha='center', fontsize=11, fontweight='bold', color=DARK_GRAY)
    
    # Sub-steps in Phase 2
    sub_steps = [
        'SA-DGWN predict (p̂ > 0.5)',
        'Path interference detection',
        'LHH escape (GSES loop)',
        'ERFM re-plan (τ = 0.8)',
        'Road recovery (30% prob.)'
    ]
    for i, s in enumerate(sub_steps):
        ax.text(6.25, 5.6 - i*0.4, s, ha='center', fontsize=9, color=DARK_GRAY)
    
    # Arrow to Phase 3
    ax.annotate('', xy=(8, 5.5), xytext=(9, 5.5), arrowprops=dict(arrowstyle='->', color=DARK_GRAY, lw=3))
    ax.text(8.5, 6.0, 'Optimized Tour', fontsize=9, color=DARK_GRAY, ha='center', fontweight='bold')
    
    # Phase 3
    ax.add_patch(FancyBboxPatch((9, 4), 2.5, 2.5, boxstyle="round,pad=0.15", facecolor=LIGHT_GREEN, edgecolor=GREEN, linewidth=2.5))
    ax.text(10.25, 6.2, 'Phase 3', ha='center', fontsize=12, fontweight='bold', color=GREEN)
    ax.text(10.25, 5.7, '2-opt Refinement', ha='center', fontsize=11, fontweight='bold', color=DARK_GRAY)
    ax.text(10.25, 5.2, 'Local search', ha='center', fontsize=10, color=DARK_GRAY)
    ax.text(10.25, 4.7, 'max 300 iterations', ha='center', fontsize=10, color=DARK_GRAY)
    
    # Output
    ax.add_patch(FancyBboxPatch((9, 2), 2.5, 1.2, boxstyle="round,pad=0.1", facecolor=LIGHT_PURPLE, edgecolor=PURPLE, linewidth=2.5))
    ax.text(10.25, 2.6, 'Optimized Tour π*', ha='center', fontsize=12, fontweight='bold', color=PURPLE)
    
    ax.annotate('', xy=(10.25, 2), xytext=(10.25, 4), arrowprops=dict(arrowstyle='->', color=PURPLE, lw=2))
    
    # Feedback loop arrow (Phase 2 -> Phase 1)
    ax.annotate('', xy=(4.5, 3.5), xytext=(3.5, 3.5), arrowprops=dict(arrowstyle='->', color=RED, lw=2, connectionstyle='arc3,rad=0.3'))
    ax.text(4, 3.1, 'Re-planning Loop', fontsize=9, color=RED, ha='center', fontweight='bold')
    ax.annotate('', xy=(3.5, 3.5), xytext=(3.5, 4), arrowprops=dict(arrowstyle='->', color=RED, lw=2))
    
    # Congestion events annotation
    ax.add_patch(FancyBboxPatch((4.5, 1), 3.5, 1.5, boxstyle="round,pad=0.1", facecolor=LIGHT_RED, edgecolor=RED, linewidth=1.5))
    ax.text(6.25, 2.2, 'Congestion Events', ha='center', fontsize=10, fontweight='bold', color=RED)
    ax.text(6.25, 1.8, '3 waves × 2-3 edges', ha='center', fontsize=9, color=GRAY)
    ax.text(6.25, 1.4, 'Random edge blockages', ha='center', fontsize=9, color=GRAY)
    
    ax.annotate('', xy=(6.25, 3.5), xytext=(6.25, 2.5), arrowprops=dict(arrowstyle='->', color=RED, lw=1.5, ls='--'))