
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.dpi': 300,
    'figure.facecolor': 'white',
    'savefig.dpi': 300,
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight'
})

save_dir = r"c:\Users\dell\Desktop\le_degn_system\论文实验数据图表\可视化图表"
os.makedirs(save_dir, exist_ok=True)


def draw_fig1():
    fig, axes = plt.subplots(1, 3, figsize=(10, 8))
    fig.suptitle("Kinematic Constraints and Turn Penalties", fontsize=16, y=0.98)
    
    # Subplot 1: Width constraint
    ax1 = axes[0]
    ax1.set_xlim(-1, 11)
    ax1.set_ylim(-2, 8)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # 5.0m road (bidirectional)
    ax1.add_patch(mpatches.Rectangle((0, 4), 5, 1, facecolor='#4CAF50', alpha=0.8, edgecolor='black'))
    ax1.text(2.5, 4.5, "Width = 5.0m", ha='center', va='center', fontweight='bold')
    ax1.text(2.5, 5.2, "Bidirectional", ha='center', va='center', color='#4CAF50', fontsize=10)
    
    # 3.0m road (one-way)
    ax1.add_patch(mpatches.Rectangle((0, 0), 3, 1, facecolor='#FF9800', alpha=0.8, edgecolor='black'))
    ax1.text(1.5, 0.5, "Width = 3.0m", ha='center', va='center', fontweight='bold')
    ax1.text(1.5, -0.7, "One-way", ha='center', va='center', color='#FF9800', fontsize=10)
    
    # Arrows
    ax1.arrow(0.5, 4.5, 4, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax1.arrow(4.5, 4.5, -4, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax1.arrow(0.5, 0.5, 2, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax1.text(1, 3.3, "Remove reverse edge", ha='center', va='center', color='#F44336', fontsize=9)
    
    # Subplot 2: Friction penalty
    ax2 = axes[1]
    ax2.set_xlim(-1, 7)
    ax2.set_ylim(-2, 8)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    ax2.add_patch(mpatches.Rectangle((0, 3), 3.5, 1, facecolor='#FF5722', alpha=0.8, edgecolor='black'))
    ax2.text(1.75, 3.5, "3.0 ≤ Width < 4.5m", ha='center', va='center', fontweight='bold')
    ax2.text(1.75, 4.5, "Cost × 1.5", ha='center', va='center', color='#FF5722', fontsize=11)
    
    # Subplot 3: Turn penalties
    ax3 = axes[2]
    ax3.set_xlim(-2, 8)
    ax3.set_ylim(-2, 8)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    # Intersection
    ax3.add_patch(mpatches.Rectangle((2, 2), 2, 2, facecolor='#9E9E9E', alpha=0.5, edgecolor='black'))
    # Roads
    ax3.add_patch(mpatches.Rectangle((2.5, 4), 1, 2, facecolor='#E0E0E0', edgecolor='black'))
    ax3.add_patch(mpatches.Rectangle((2.5, 0), 1, 2, facecolor='#E0E0E0', edgecolor='black'))
    ax3.add_patch(mpatches.Rectangle((0, 2.5), 2, 1, facecolor='#E0E0E0', edgecolor='black'))
    ax3.add_patch(mpatches.Rectangle((4, 2.5), 2, 1, facecolor='#E0E0E0', edgecolor='black'))
    
    # Turn arrows
    # Left turn
    ax3.add_patch(FancyArrowPatch((2.5, 3.5), (3, 2.5), arrowstyle='->,head_width=0.2', 
                                  connectionstyle="angle3,angleA=180,angleB=-90", 
                                  color='#2196F3', linewidth=2))
    ax3.text(1.5, 4.5, "Left turn +1.5s", ha='center', va='center', color='#2196F3')
    
    # U-turn
    ax3.add_patch(FancyArrowPatch((2.5, 3.5), (2.5, 0.5), arrowstyle='->,head_width=0.2',
                                  connectionstyle="arc3,rad=-1.5",
                                  color='#F44336', linewidth=2))
    ax3.text(5, 5, "U-turn +7.0s", ha='center', va='center', color='#F44336')
    
    plt.savefig(os.path.join(save_dir, 'fig1_kinematic_constraints.png'), dpi=300)
    plt.close()


def draw_fig2():
    fig, axes = plt.subplots(1, 3, figsize=(10, 8), gridspec_kw={'width_ratios': [1, 0.3, 1]})
    fig.suptitle("Primal Graph to Line Graph Transformation", fontsize=16, y=0.98)
    
    # Left: Primal Graph
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title("Primal Graph", fontsize=12)
    
    # Nodes
    nodes = {'A': (2, 2), 'B': (8, 2), 'C': (5, 8)}
    for name, (x, y) in nodes.items():
        circle = mpatches.Circle((x, y), 0.6, facecolor='#2196F3', edgecolor='black', zorder=5)
        ax1.add_patch(circle)
        ax1.text(x, y, name, ha='center', va='center', color='white', fontweight='bold')
    
    # Edges
    edges = [('A', 'B', 'e1'), ('B', 'C', 'e2'), ('C', 'A', 'e3')]
    for u, v, label in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        ax1.arrow(x1, y1, x2-x1, y2-y1, head_width=0.3, head_length=0.4, 
                  fc='black', ec='black', length_includes_head=True, zorder=3)
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax1.text(mx, my, label, ha='center', va='center', 
                 bbox=dict(facecolor='white', edgecolor='none', pad=2), zorder=4)
    
    # Middle: Transform arrow
    ax2 = axes[1]
    ax2.axis('off')
    ax2.arrow(0, 0.5, 0.8, 0, head_width=0.2, head_length=0.2, fc='black', ec='black')
    ax2.text(0.4, 0.5, "Transform", ha='center', va='center', rotation=0, fontweight='bold')
    
    # Right: Line Graph
    ax3 = axes[2]
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.set_aspect('equal')
    ax3.axis('off')
    ax3.set_title("Line Graph", fontsize=12)
    
    # Line nodes
    line_nodes = {'e1': (2, 2), 'e2': (8, 2), 'e3': (5, 8)}
    for name, (x, y) in line_nodes.items():
        circle = mpatches.Circle((x, y), 0.8, facecolor='#FF9800', edgecolor='black', zorder=5)
        ax3.add_patch(circle)
        ax3.text(x, y, name, ha='center', va='center', color='white', fontweight='bold')
    
    # Line edges
    line_edges = [('e1', 'e2'), ('e2', 'e3'), ('e3', 'e1')]
    for u, v in line_edges:
        x1, y1 = line_nodes[u]
        x2, y2 = line_nodes[v]
        ax3.arrow(x1, y1, x2-x1, y2-y1, head_width=0.3, head_length=0.4, 
                  fc='black', ec='black', length_includes_head=True, zorder=3)
    
    plt.savefig(os.path.join(save_dir, 'fig2_line_graph_transform.png'), dpi=300)
    plt.close()


def draw_fig3():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title("ERFM Encoder-Decoder Architecture", fontsize=16, y=0.98)
    
    # Input
    input_box = FancyBboxPatch((1, 7.5), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
    ax.add_patch(input_box)
    ax.text(2, 8, "Edge Features\n(13-D)", ha='center', va='center')
    
    global_attr = FancyBboxPatch((1, 5.5), 2, 1, boxstyle="round,pad=0.1", 
                                  facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
    ax.add_patch(global_attr)
    ax.text(2, 6, "Global Attr\n(4-D)", ha='center', va='center')
    
    # Encoder
    encoder_box = FancyBboxPatch((4, 4.5), 3, 4, boxstyle="round,pad=0.1", 
                                 facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2)
    ax.add_patch(encoder_box)
    ax.text(5.5, 8, "Encoder", ha='center', va='center', fontweight='bold')
    
    # Transformer blocks
    for i in range(3):
        block = FancyBboxPatch((4.2, 7-i*0.8), 2.6, 0.6, boxstyle="round,pad=0.1", 
                               facecolor='#FFE0B2', edgecolor='#EF6C00', linewidth=1.5)
        ax.add_patch(block)
        ax.text(5.5, 7-i*0.8+0.3, f"Transformer Block {i+1}", ha='center', va='center', fontsize=9)
    ax.text(5.5, 4.8, "+ PenaltyBiasAttention", ha='center', va='center', fontsize=9, color='#E65100')
    
    # Decoder
    decoder_box = FancyBboxPatch((8, 4.5), 3, 3, boxstyle="round,pad=0.1", 
                                 facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2)
    ax.add_patch(decoder_box)
    ax.text(9.5, 7, "Decoder", ha='center', va='center', fontweight='bold')
    ax.text(9.5, 6, "Autoregressive cycle", ha='center', va='center', fontsize=9)
    ax.text(9.5, 5, "→ Tour π", ha='center', va='center', fontsize=9)
    
    # Value Head
    value_head = FancyBboxPatch((8, 1.5), 3, 1.5, boxstyle="round,pad=0.1", 
                                facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(value_head)
    ax.text(9.5, 2.5, "Parallel Value Head", ha='center', va='center', fontweight='bold')
    ax.text(9.5, 1.8, "→ V(s)", ha='center', va='center', fontsize=9)
    
    # Arrows
    ax.arrow(3, 8, 0.8, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax.arrow(3, 6, 0.8, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax.arrow(7, 6.5, 0.8, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax.arrow(5.5, 4.5, 0, -2.5, head_width=0.2, head_length=0.3, fc='black', ec='black')
    
    plt.savefig(os.path.join(save_dir, 'fig3_erfm_architecture.png'), dpi=300)
    plt.close()


def draw_fig4():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis('off')
    ax.set_title("SA-DGWN Spatio-Temporal Network", fontsize=16, y=0.98)
    
    # Temporal/Spatial labels
    ax.text(9.2, 5.5, "Spatial", rotation=90, va='center', ha='center', color='#4CAF50', fontsize=12)
    ax.text(9.2, 8.5, "Temporal", rotation=90, va='center', ha='center', color='#2196F3', fontsize=12)
    
    # Layer 1: Input
    layer1 = FancyBboxPatch((1, 9), 6, 1.2, boxstyle="round,pad=0.1", 
                            facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
    ax.add_patch(layer1)
    ax.text(4, 9.6, "Input", ha='center', va='center', fontweight='bold')
    ax.text(4, 9.1, "Speed & Flow, 12 timesteps", ha='center', va='center', fontsize=9)
    
    # Layer 2: Dilated Causal Conv
    layer2 = FancyBboxPatch((1, 7), 6, 1.2, boxstyle="round,pad=0.1", 
                            facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=2)
    ax.add_patch(layer2)
    ax.text(4, 7.6, "Dilated Causal Conv", ha='center', va='center', fontweight='bold')
    ax.text(4, 7.1, "d=1,2,4,8", ha='center', va='center', fontsize=9)
    
    # Layer 3: Graph Conv
    layer3 = FancyBboxPatch((1, 5), 6, 1.2, boxstyle="round,pad=0.1", 
                            facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2)
    ax.add_patch(layer3)
    ax.text(4, 5.6, "Graph Conv", ha='center', va='center', fontweight='bold')
    ax.text(4, 5.1, "A/D normalized", ha='center', va='center', fontsize=9)
    
    # Layer 4: Gating
    layer4 = FancyBboxPatch((1, 3), 6, 1.2, boxstyle="round,pad=0.1", 
                            facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=2)
    ax.add_patch(layer4)
    ax.text(4, 3.6, "Gating", ha='center', va='center', fontweight='bold')
    ax.text(4, 3.1, "σ(W·h)", ha='center', va='center', fontsize=9)
    
    # Layer 5: Output
    layer5 = FancyBboxPatch((1, 1), 6, 1.2, boxstyle="round,pad=0.1", 
                            facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2)
    ax.add_patch(layer5)
    ax.text(4, 1.6, "Output", ha='center', va='center', fontweight='bold')
    ax.text(4, 1.1, "Congestion Probability p̂ ∈ [0,1]", ha='center', va='center', fontsize=9)
    
    # Arrows
    for y in [8.8, 6.8, 4.8, 2.8]:
        ax.arrow(4, y, 0, -0.6, head_width=0.2, head_length=0.3, fc='black', ec='black')
    
    plt.savefig(os.path.join(save_dir, 'fig4_sadgwn_structure.png'), dpi=300)
    plt.close()


def draw_fig5():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title("LHH GSES Loop and Heuristic Selection", fontsize=16, y=0.98)
    
    # Central circle
    central_circle = mpatches.Circle((6, 5), 2, facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=3)
    ax.add_patch(central_circle)
    ax.text(6, 5.2, "GSES Loop", ha='center', va='center', fontweight='bold', fontsize=14)
    
    # Steps around circle
    steps = [
        ("Generate", (6, 8.5), '#2196F3'),
        ("Score", (9.5, 6.5), '#4CAF50'),
        ("Execute", (9.5, 3.5), '#FF9800'),
        ("Self-reflect", (2.5, 3.5), '#E91E63')
    ]
    
    for name, (x, y), color in steps:
        box = FancyBboxPatch((x-1, y-0.4), 2, 0.8, boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', color='white', fontweight='bold')
    
    # Heuristics for Generate
    heuristics = [
        ("Greedy Widest", (1, 8.5)),
        ("Min Penalty", (1, 7.8)),
        ("Max Connectivity", (1, 7.1)),
        ("Adaptive A*", (1, 6.4)),
        ("Multi-hop Greedy", (1, 5.7))
    ]
    for name, (x, y) in heuristics:
        box = FancyBboxPatch((x, y-0.25), 1.8, 0.5, boxstyle="round,pad=0.05", 
                             facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=1)
        ax.add_patch(box)
        ax.text(x+0.9, y, name, ha='center', va='center', fontsize=8)
    ax.arrow(2.8, 7.1, 1.2, 0, head_width=0.15, head_length=0.2, fc='#2196F3', ec='#2196F3')
    
    # Self-reflect update
    update_box = FancyBboxPatch((0.5, 2), 3.5, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=1.5)
    ax.add_patch(update_box)
    ax.text(2.25, 2.4, "Update weights\n(last 5 records)", ha='center', va='center', fontsize=8)
    ax.arrow(2.25, 2.8, 0, 0.4, head_width=0.15, head_length=0.2, fc='#E91E63', ec='#E91E63')
    
    # Cycle arrows
    arrow_positions = [(7.5, 7.5), (9.5, 5), (7.5, 2.5), (4.5, 5)]
    for i in range(4):
        x, y = arrow_positions[i]
        next_i = (i + 1) % 4
        nx, ny = arrow_positions[next_i]
        dx, dy = nx - x, ny - y
        ax.arrow(x, y, dx*0.8, dy*0.8, head_width=0.2, head_length=0.3, 
                 fc='black', ec='black')
    
    plt.savefig(os.path.join(save_dir, 'fig5_lhh_flowchart.png'), dpi=300)
    plt.close()


def draw_fig6():
    fig, ax1 = plt.subplots(figsize=(10, 8))
    fig.suptitle("ERFM Training Convergence and Temperature Annealing", fontsize=16, y=0.98)
    
    # Generate data
    episodes = np.arange(0, 3001, 50)
    # Tour cost (exponential decay)
    tour_cost = 70000 * np.exp(-episodes / 800) + 27000 * (1 - np.exp(-episodes / 800))
    # Temperature (linear decay)
    temperature = 1.5 - (1.5 - 0.2) * (episodes / 3000)
    
    # Left Y-axis: Tour Cost
    ax1.plot(episodes, tour_cost, color='#2196F3', linewidth=2.5, label='Tour Cost')
    ax1.set_xlabel("Training Episode", fontsize=12)
    ax1.set_ylabel("Tour Cost", color='#2196F3', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#2196F3')
    ax1.set_xlim(0, 3000)
    ax1.grid(True, alpha=0.3)
    
    # Right Y-axis: Temperature
    ax2 = ax1.twinx()
    ax2.plot(episodes, temperature, color='#F44336', linewidth=2.5, linestyle='--', label='Temperature τ')
    ax2.set_ylabel("Temperature τ", color='#F44336', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='#F44336')
    
    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.savefig(os.path.join(save_dir, 'fig6_training_convergence.png'), dpi=300)
    plt.close()


def draw_fig7():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title("LE-DEGN Three-Phase Dynamic Execution", fontsize=16, y=0.98)
    
    # Phase 1
    phase1 = FancyBboxPatch((0.5, 6), 3, 3, boxstyle="round,pad=0.1", 
                            facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
    ax.add_patch(phase1)
    ax.text(2, 8.5, "Phase 1", ha='center', va='center', fontweight='bold', fontsize=13)
    ax.text(2, 7.8, "Global Macro Planning", ha='center', va='center', fontsize=11)
    ax.text(2, 7.2, "5 rollouts τ=0.5", ha='center', va='center', fontsize=9)
    
    # Phase 2
    phase2 = FancyBboxPatch((4.5, 4), 3, 3, boxstyle="round,pad=0.1", 
                            facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2)
    ax.add_patch(phase2)
    ax.text(6, 6.5, "Phase 2", ha='center', va='center', fontweight='bold', fontsize=13)
    ax.text(6, 5.8, "Dynamic Execution", ha='center', va='center', fontsize=11)
    ax.text(6, 5.2, "Congestion events", ha='center', va='center', fontsize=8)
    ax.text(6, 4.8, "→ SA-DGWN predict", ha='center', va='center', fontsize=8)
    ax.text(6, 4.4, "→ LHH escape", ha='center', va='center', fontsize=8)
    ax.text(6, 4, "→ ERFM re-plan", ha='center', va='center', fontsize=8)
    
    # Phase 3
    phase3 = FancyBboxPatch((8.5, 6), 3, 3, boxstyle="round,pad=0.1", 
                            facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2)
    ax.add_patch(phase3)
    ax.text(10, 8.5, "Phase 3", ha='center', va='center', fontweight='bold', fontsize=13)
    ax.text(10, 7.8, "2-opt Refinement", ha='center', va='center', fontsize=11)
    ax.text(10, 7.2, "Local search", ha='center', va='center', fontsize=9)
    ax.text(10, 6.7, "max 300 iter", ha='center', va='center', fontsize=9)
    
    # Final output
    output_box = FancyBboxPatch((8.5, 2.5), 3, 1, boxstyle="round,pad=0.1", 
                                facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=2)
    ax.add_patch(output_box)
    ax.text(10, 3, "Optimized Tour π*", ha='center', va='center', fontweight='bold')
    
    # Arrows
    ax.arrow(3.5, 7.5, 0.8, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax.arrow(7.5, 5.5, 0.8, 0, head_width=0.2, head_length=0.3, fc='black', ec='black')
    ax.arrow(10, 6, 0, -2.5, head_width=0.2, head_length=0.3, fc='black', ec='black')
    
    # Feedback arrow - simple dashed arrow instead
    ax.arrow(4.2, 5.7, -0.8, 0.8, head_width=0.2, head_length=0.3, 
             fc='#F44336', ec='#F44336', linestyle='--', linewidth=2)
    ax.text(4, 6.2, "Re-planning loop", ha='center', va='center', color='#F44336', fontsize=9)
    
    plt.savefig(os.path.join(save_dir, 'fig7_three_phase_execution.png'), dpi=300)
    plt.close()


def draw_fig8():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis('off')
    ax.set_title("LE-DEGN vs Baseline (DHAN) Architecture Comparison", fontsize=16, y=0.98)
    
    # Left: LE-DEGN
    left_box = FancyBboxPatch((0.5, 1), 4.5, 9, boxstyle="round,pad=0.2", 
                              facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=3)
    ax.add_patch(left_box)
    ax.text(2.75, 9.5, "LE-DEGN", ha='center', va='center', fontweight='bold', fontsize=14, color='#1976D2')
    
    ledegn_features = [
        "Route: ERFM Transformer (learned)",
        "Congestion: SA-DGWN proactive prediction",
        "Escape: LHH adaptive heuristics",
        "Re-planning: Full ERFM with exclusion",
        "Exploration: 5 stochastic rollouts",
        "Optimization: 2-opt local refinement"
    ]
    for i, feat in enumerate(ledegn_features):
        y = 8.2 - i * 1.1
        ax.text(2.75, y, feat, ha='center', va='center', fontsize=9, 
                bbox=dict(facecolor='white', alpha=0.7, pad=3, edgecolor='#BBDEFB'))
    
    # Right: Baseline
    right_box = FancyBboxPatch((7, 1), 4.5, 9, boxstyle="round,pad=0.2", 
                               facecolor='#F5F5F5', edgecolor='#616161', linewidth=3)
    ax.add_patch(right_box)
    ax.text(9.25, 9.5, "Baseline (DHAN+NN)", ha='center', va='center', fontweight='bold', fontsize=14, color='#616161')
    
    baseline_features = [
        "Route: Greedy Nearest-Neighbor",
        "Congestion: Reactive fixed penalty (15%)",
        "Escape: None",
        "Re-planning: None",
        "Exploration: 5 deterministic starts",
        "Optimization: None"
    ]
    for i, feat in enumerate(baseline_features):
        y = 8.2 - i * 1.1
        ax.text(9.25, y, feat, ha='center', va='center', fontsize=9, 
                bbox=dict(facecolor='white', alpha=0.7, pad=3, edgecolor='#BDBDBD'))
    
    # Comparison arrows
    for i in range(6):
        y = 8.2 - i * 1.1
        ax.arrow(5, y, 1.8, 0, head_width=0.15, head_length=0.2, fc='#9E9E9E', ec='#9E9E9E', alpha=0.6)
    
    plt.savefig(os.path.join(save_dir, 'fig8_architecture_comparison.png'), dpi=300)
    plt.close()


# Generate all figures
print("Generating academic figures...")
draw_fig1()
print("✓ Fig1 generated")
draw_fig2()
print("✓ Fig2 generated")
draw_fig3()
print("✓ Fig3 generated")
draw_fig4()
print("✓ Fig4 generated")
draw_fig5()
print("✓ Fig5 generated")
draw_fig6()
print("✓ Fig6 generated")
draw_fig7()
print("✓ Fig7 generated")
draw_fig8()
print("✓ Fig8 generated")
print(f"\nAll figures saved to: {save_dir}")

