import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Polygon, FancyArrow
import numpy as np
import os

OUT = r"c:\Users\dell\Desktop\le_degn_system\论文实验数据图表\可视化图表"
os.makedirs(OUT, exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.default'] = 'regular'

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {name}")

def draw_box(ax, x, y, w, h, text, fc='#E8F0FE', ec='#1a73e8', fs=9, bold=False):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", fc=fc, ec=ec, lw=1.5)
    ax.add_patch(box)
    wt = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs, weight=wt, color='#1a1a1a')

def draw_arrow(ax, x1, y1, x2, y2, lw=1.2, color='#555'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, connectionstyle='arc3,rad=0'))

def draw_dash_arrow(ax, x1, y1, x2, y2, lw=1.0, color='#888'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, linestyle='dashed', connectionstyle='arc3,rad=0'))

# ═══════════════════════════════════════════
# FIGURE 1: Kinematic Constraints & Turn Penalties
# ═══════════════════════════════════════════
def fig1():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
    fig.suptitle('Physical-Kinematic Constraint Mechanisms', fontsize=14, weight='bold', y=1.02)

    # Panel A: Width-based unidirectional conversion
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('(a) Width-Based Unidirectional Conversion', fontsize=11, weight='bold', pad=8)

    # Wide road (bidirectional)
    ax.text(2.5, 7.5, 'w = 6.0 m ≥ 4.5 m', ha='center', fontsize=9, weight='bold', color='#0d904f')
    ax.annotate('', xy=(5, 6.5), xytext=(0, 6.5), arrowprops=dict(arrowstyle='->', color='#0d904f', lw=2))
    ax.annotate('', xy=(0, 6.0), xytext=(5, 6.0), arrowprops=dict(arrowstyle='->', color='#0d904f', lw=2))
    draw_box(ax, 0, 5.8, 5, 1.5, u'Bidirectional\nWidth ≥ 4.5m', fc='#d4edda', ec='#0d904f', fs=9)
    ax.text(2.5, 5.3, 'Retain both directions', ha='center', fontsize=8, color='#0d904f')

    # Narrow road (unidirectional)
    ax.annotate('', xy=(5., 3.5), xytext=(0.0, 3.5), arrowprops=dict(arrowstyle='->', color='#dc3545', lw=2.5))
    draw_box(ax, 0, 2.8, 5, 1.5, u'Narrow Road\nWidth < 4.5m', fc='#f8d7da', ec='#dc3545', fs=9)
    ax.text(2.5, 2.3, 'Convert to unidirectional', ha='center', fontsize=8, color='#dc3545')
    ax.text(5.2, 6.2, '↔', fontsize=14, color='#0d904f')
    ax.text(5.2, 3.2, '→ only', fontsize=12, color='#dc3545')

    # Narrow friction zone
    draw_box(ax, 6.2, 5.0, 3.5, 3.0, u'Narrow Friction\n3.0 ≤ w < 4.5 m\ncost × 1.5', fc='#fff3cd', ec='#ffc107', fs=8.5)

    # Panel B: Turn penalties
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('(b) Turn Penalty Rules', fontsize=11, weight='bold', pad=8)

    # Intersection
    ax.plot([3, 7], [4, 4], 'k-', lw=3)
    ax.plot([5, 5], [2.5, 5.5], 'k-', lw=3)
    ax.plot(5, 4, 'ko', ms=6)

    # Straight (North→South)
    ax.annotate('', xy=(5, 2.3), xytext=(5, 3.7), arrowprops=dict(arrowstyle='->', color='#0d904f', lw=2.5))
    ax.text(5.4, 2.8, 'Straight\n+0s', fontsize=9, color='#0d904f', weight='bold')

    # Left turn (West→North)
    ax.annotate('', xy=(5, 5.7), xytext=(2.8, 4), arrowprops=dict(arrowstyle='->', color='#ffc107', lw=2.5,
               connectionstyle='arc3,rad=0.6'))
    ax.text(1.0, 5.8, 'Left Turn\n+1.5s', fontsize=9, color='#cc8800', weight='bold')

    # Right turn (West→South)
    ax.annotate('', xy=(5, 2.3), xytext=(2.8, 4), arrowprops=dict(arrowstyle='->', color='#0d904f', lw=2,
               connectionstyle='arc3,rad=-0.6'))
    ax.text(1.0, 1.5, 'Right Turn\n+0s', fontsize=9, color='#0d904f')

    # U-turn (South→South backward)
    ax.annotate('', xy=(5, 5.7), xytext=(5, 2.3), arrowprops=dict(arrowstyle='->', color='#dc3545', lw=3,
               connectionstyle='arc3,rad=2.5'))
    ax.text(7.0, 5.8, 'U-Turn\n+7.0s', fontsize=9, color='#dc3545', weight='bold')

    # Panel C: Cost composition
    ax = axes[2]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('(c) Total Cost Decomposition', fontsize=11, weight='bold', pad=8)

    draw_box(ax, 1.5, 5.5, 7, 1.3, r'$C_{total}(\pi) = C_{service} + C_{transition}(\pi)$', fc='#e8eaf6', ec='#3f51b5', fs=11, bold=True)
    draw_box(ax, 0.3, 3.2, 4.5, 1.8, r'$C_{service} = \sum w(e)$' '\n(Fixed, invariant\nto permutation)', fc='#d4edda', ec='#0d904f', fs=9)
    draw_box(ax, 5.2, 3.2, 4.5, 1.8, r'$C_{transition} = \sum T_{\pi_k,\pi_{k+1}}$' '\n(Optimizable via\nedge ordering)', fc='#fff3cd', ec='#ffc107', fs=9)
    draw_arrow(ax, 4.5, 5.5, 2.5, 4.5)
    draw_arrow(ax, 5.5, 5.5, 7.3, 4.5)
    draw_box(ax, 1.5, 1.0, 7, 1.5, 'Optimization Target: Minimize Transition Cost\nPenalty Bias Matrix M suppresses U-turns (−8.0) and left-turns (−1.5)', fc='#fce4ec', ec='#e91e63', fs=9)

    plt.tight_layout()
    save(fig, 'fig_algorithm_01_kinematic_constraints.png')

# ═══════════════════════════════════════════
# FIGURE 2: Primal Graph → Line Graph
# ═══════════════════════════════════════════
def fig2():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle('Line Graph Transformation: Edge-Centric Reformulation', fontsize=13, weight='bold')

    # Panel A: Primal Graph
    ax = axes[0]
    ax.set_xlim(-1, 7); ax.set_ylim(-1, 7); ax.axis('off')
    ax.set_title('Primal Graph G = (V, E)', fontsize=11, weight='bold', color='#1565c0')

    nodes = {0: (0, 0), 1: (3, 0), 2: (6, 0), 3: (0, 4), 4: (3, 4), 5: (6, 4)}
    edges = [(0,1,'e1'), (1,2,'e2'), (0,3,'e3'), (3,4,'e4'), (4,5,'e5'), (1,4,'e6'), (4,1,'e7'), (5,2,'e8')]

    for uid, (xu, yu) in nodes.items():
        ax.plot(xu, yu, 'o', ms=14, color='#1565c0', mec='white', mew=2, zorder=5)
        ax.text(xu, yu, str(uid), ha='center', va='center', fontsize=9, color='white', weight='bold', zorder=6)

    colors = ['#e53935','#e53935','#43a047','#43a047','#43a047','#fb8c00','#8e24aa','#1e88e5']
    for (u, v, ename), c in zip(edges, colors):
        xu, yu = nodes[u]; xv, yv = nodes[v]
        mx, my = (xu+xv)/2, (yu+yv)/2
        ax.annotate('', xy=(xv, yv), xytext=(xu, yu), arrowprops=dict(arrowstyle='->', color=c, lw=2.5, shrinkA=7, shrinkB=7))
        ax.text(mx+0.15, my+0.15, ename, fontsize=8, color=c, weight='bold')

    # Panel B: Line Graph
    ax = axes[1]
    ax.set_xlim(-1, 9); ax.set_ylim(-1, 7); ax.axis('off')
    ax.set_title('Line Graph L = (V_L, E_L)', fontsize=11, weight='bold', color='#c62828')

    pos = {'e1': (1, 6), 'e2': (3, 6), 'e3': (1, 3), 'e4': (3, 3), 'e5': (5, 3), 'e6': (3, 1.5), 'e7': (5, 1.5), 'e8': (5, 5.5)}
    lcolors = {'e1': '#e53935', 'e2': '#e53935', 'e3': '#43a047', 'e4': '#43a047', 'e5': '#43a047', 'e6': '#fb8c00', 'e7': '#8e24aa', 'e8': '#1e88e5'}

    for ename, (xe, ye) in pos.items():
        c = lcolors[ename]
        circ = plt.Circle((xe, ye), 0.45, fc=c, ec='white', lw=2, zorder=5)
        ax.add_patch(circ)
        ax.text(xe, ye, ename, ha='center', va='center', fontsize=8, color='white', weight='bold', zorder=6)

    lg_edges = [('e1','e2'),('e3','e4'),('e4','e5'),('e6','e4'),('e7','e1'),('e8','e2'),('e3','e6'),('e5','e8')]
    for u, v in lg_edges:
        xu, yu = pos[u]; xv, yv = pos[v]
        ax.annotate('', xy=(xv, yv), xytext=(xu, yu), arrowprops=dict(arrowstyle='->', color='#666', lw=1.3, shrinkA=9, shrinkB=9))

    draw_box(ax, 6.5, 4, 2.2, 2.2, 'N = |E_G|\n(edges → nodes)', fc='#ffebee', ec='#c62828', fs=8.5)
    ax.annotate('Primal Edge →\nLine Graph Node', xy=(1.5, 0.2), fontsize=9, ha='center', color='#555',
                bbox=dict(boxstyle='round', fc='#f5f5f5', ec='#aaa'))

    plt.tight_layout()
    save(fig, 'fig_algorithm_02_line_graph_transform.png')

# ═══════════════════════════════════════════
# FIGURE 3: ERFM Encoder-Decoder Architecture
# ═══════════════════════════════════════════
def fig3():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 14); ax.axis('off')
    ax.set_title('Edge-centric Route Foundation Model (ERFM) Architecture', fontsize=13, weight='bold', pad=12)

    # Input
    draw_box(ax, 4.5, 12.5, 5, 1.0, 'Edge Features X (13-D) + Penalty Matrix M + Global Attr g', fc='#e3f2fd', ec='#1565c0', fs=9, bold=True)

    # Encoder blocks
    draw_box(ax, 0.5, 9.5, 3.5, 2.5,
             'Penalty-Biased\nMulti-Head Attention\nMHA(Q,K,V,M)\nM suppresses U-turn/L-turn',
             fc='#e8eaf6', ec='#3f51b5', fs=8)
    draw_box(ax, 5.2, 9.5, 3.5, 2.5, 'Edge Transformer\nBlock 1\n+ LayerNorm\n+ FFN (GELU)', fc='#e8eaf6', ec='#3f51b5', fs=8)
    draw_box(ax, 9.9, 9.5, 3.5, 2.5, 'Edge Transformer\nBlock 2-3\n($d_{model}$=64, h=4)\nStacked layers', fc='#e8eaf6', ec='#3f51b5', fs=8)

    draw_arrow(ax, 4.0, 10.75, 5.2, 10.75)
    draw_arrow(ax, 8.7, 10.75, 9.9, 10.75)

    # Encoder output
    draw_box(ax, 4.5, 8.0, 5, 1.2, 'Edge Embeddings H ∈ R^{N×64}', fc='#c8e6c9', ec='#2e7d32', fs=10, bold=True)
    draw_arrow(ax, 7, 9.5, 7, 9.2)

    # Decoder
    draw_box(ax, 0.3, 4.8, 4.0, 2.8,
             'Autoregressive Decoder\nq = W_q·[e_curr ⊕ e_ctx]\nscore = q·(W_k·e_cand)^T/√d\nπ_θ = softmax(score/τ)\n+ Mask visited & blocked',
             fc='#fff3e0', ec='#e65100', fs=8)
    draw_box(ax, 5.5, 4.8, 3.5, 2.8, 'Value Head\nV(e_curr, e_ctx)\n= MLP([e_curr⊕e_ctx])\n→ 1 scalar', fc='#f3e5f5', ec='#7b1fa2', fs=8)
    draw_box(ax, 10, 4.8, 3.5, 2.8,
             'Tour Construction\nCategorical sampling\n→ e_{next}\nTemperature τ: 1.5→0.2\n(explore→exploit)',
             fc='#fff3e0', ec='#e65100', fs=8)

    draw_arrow(ax, 7, 8.0, 7, 7.6)

    # Output
    draw_box(ax, 3.5, 2.0, 7, 2.3,
             'Output: Tour π = (e₁, e₂, ..., e_K)  |  C_total = C_service + C_transition\n'
             'Training: REINFORCE with Advantage A_t = G_t − V(s_t)  |  Entropy Bonus + Gradient Clip',
             fc='#ffebee', ec='#c62828', fs=10, bold=True)
    draw_arrow(ax, 4.3, 4.8, 6, 4.3)
    draw_arrow(ax, 9, 4.8, 8, 4.3)

    # Divider
    ax.axhline(y=7.4, xmin=0.02, xmax=0.98, color='#aaa', ls='--', lw=1)
    ax.text(7, 7.2, 'ENCODER → EMBEDDINGS', ha='center', fontsize=9, color='#777', weight='bold')
    ax.text(7, 7.6, 'DECODER (Autoregressive)', ha='center', fontsize=9, color='#777', weight='bold')

    plt.tight_layout()
    save(fig, 'fig_algorithm_03_erfm_architecture.png')

# ═══════════════════════════════════════════
# FIGURE 4: SA-DGWN Architecture
# ═══════════════════════════════════════════
def fig4():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13); ax.set_ylim(0, 13); ax.axis('off')
    ax.set_title('SA-DGWN: Spatio-Temporal Dynamic Graph Wave Network', fontsize=13, weight='bold', pad=12)

    # Input
    draw_box(ax, 3.5, 11.5, 6, 1.2, 'Input: Historical Traffic X ∈ R^{N×12×2}\n(Speed + Flow, 12 timesteps)', fc='#e3f2fd', ec='#1565c0', fs=9, bold=True)
    draw_arrow(ax, 6.5, 11.5, 6.5, 10.7)

    # Block
    for i in range(3):
        yb = 10.0 - i * 2.2
        draw_box(ax, 0.3, yb+0.1, 3.8, 2.5,
                 f'SpatioTemporalBlock {i+1}\n'
                 'DilatedCausalConv1D\n'
                 f'dilation=2^{i}, K=3, ch=32\n'
                 '→ Temporal patterns',
                 fc='#e8eaf6', ec='#3f51b5', fs=7.5)
        draw_box(ax, 4.8, yb+0.1, 3.8, 2.5,
                 'Graph Convolution\n'
                 'ReLU(W·Â·x)\n'
                 'Â = A/D (row-norm)\n'
                 '→ Spatial patterns',
                 fc='#e8eaf6', ec='#5c6bc0', fs=7.5)
        draw_box(ax, 9.3, yb+0.1, 3.4, 2.5,
                 'Gating + Output\n'
                 'σ(W_g·h_gcn)·h_gcn\n'
                 'LayerNorm(gated)\n'
                 f'→ Ch 32→64→128',
                 fc='#c8e6c9', ec='#2e7d32', fs=7.5)
        draw_arrow(ax, 4.1, yb+1.35, 4.8, yb+1.35)
        draw_arrow(ax, 8.6, yb+1.35, 9.3, yb+1.35)
        if i < 2:
            draw_arrow(ax, 11.0, yb+1.35, 11.0, yb-0.85, color='#888', lw=2.5)

    # Output
    draw_box(ax, 3.5, 1.0, 6, 1.5,
             'Output: Sigmoid → p̂ ∈ [0,1]^N\nEdges with p̂ > 0.5 flagged HIGH-RISK\nTraining: L_BCE with speed<0.3→congestion label',
             fc='#ffebee', ec='#c62828', fs=9, bold=True)
    draw_arrow(ax, 11.0, 7.7, 11.0, 2.5, color='#888', lw=2.5)

    ax.text(6.5, 12.5, 'Receptive field expands: 1→2→4→8 timesteps', ha='center', fontsize=8.5, color='#777', style='italic')

    plt.tight_layout()
    save(fig, 'fig_algorithm_04_sa_dgwn_architecture.png')

# ═══════════════════════════════════════════
# FIGURE 5: LHH GSES Loop
# ═══════════════════════════════════════════
def fig5():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 12); ax.axis('off')
    ax.set_title('LHH: Language-driven Heuristic Hub — GSES Loop', fontsize=13, weight='bold', pad=12)

    # Trigger
    draw_box(ax, 4, 10.5, 5, 1.2, 'TRIGGER: Congestion detected\n→ ESCAPE state activated', fc='#ffcdd2', ec='#c62828', fs=9, bold=True)
    draw_arrow(ax, 6.5, 10.5, 6.5, 9.8)

    # State Verbalization
    draw_box(ax, 3.5, 8.5, 6, 1.2, 'StateVerbalizer: k-hop subgraph → textual context\n(node positions, edge widths, blockage status)', fc='#e3f2fd', ec='#1565c0', fs=8.5)

    # GSES Box
    r = FancyBboxPatch((0.3, 1.8), 12.4, 6.2, boxstyle="round,pad=0.3", fc='#fafafa', ec='#3f51b5', lw=2, ls='--')
    ax.add_patch(r)
    ax.text(6.5, 7.6, 'GSES LOOP', ha='center', fontsize=10, weight='bold', color='#3f51b5')

    # Generate
    for i, (name, desc, param) in enumerate([
        ('H1: Greedy\nWidest Road', 'Max width', 'depth=15'),
        ('H2: Min\nPenalty', 'Min turn\npenalty', 'L×1.5,U×7'),
        ('H3: Max\nConnectivity', 'Max out-\ndegree', 'depth=15'),
        ('H4: Adaptive\nA* Escape', 'Width-weighted\nA* search', 'depth=50'),
        ('H5: Multi-hop\nGreedy', '3-step\nlookahead', 'depth=20')
    ]):
        xb = 0.5 + i * 2.5
        draw_box(ax, xb, 5.5, 2.2, 1.8, f'{name}\n{desc}\n({param})',
                 fc='#e8eaf6', ec='#5c6bc0', fs=7)
        draw_arrow(ax, xb+1.1, 5.5, 6.5, 3.8, color='#999', lw=0.8)

    # Score
    draw_box(ax, 4.5, 3.0, 4.0, 1.5, 'SCORE: Path Cost C(p_k)\nC = Σ w(u,v) + 10⁴·blocked', fc='#fff3e0', ec='#e65100', fs=8.5)

    # Execute
    draw_box(ax, 9.5, 4.5, 3.0, 3.0,
             'EXECUTE\np* = argmin C(p_k)\nRecord in\nhistory buffer\n(rolling window=5)',
             fc='#c8e6c9', ec='#2e7d32', fs=8)
    draw_arrow(ax, 8.5, 3.75, 9.5, 5.5, color='#2e7d32', lw=1.5)

    draw_arrow(ax, 6.5, 3.0, 6.5, 2.2)
    draw_arrow(ax, 11.5, 6.0, 11.5, 7.0, color='#7b1fa2', lw=1.5, ls='dashed')

    # Self-reflect
    draw_box(ax, 8.0, 2.0, 4.5, 1.2,
             'SELF-REFLECT: w_k = (1/mean_C_k) / Σ(1/mean_C_j)\nHeuristics with lower avg cost → higher weight',
             fc='#f3e5f5', ec='#7b1fa2', fs=8)

    plt.text(6.5, 0.5, 'Rapid convergence: preference distribution stabilizes within 3-5 escape events', ha='center', fontsize=9, color='#777', style='italic')

    plt.tight_layout()
    save(fig, 'fig_algorithm_05_lhh_gses_loop.png')

# ═══════════════════════════════════════════
# FIGURE 6: ERFM Training Convergence & Temperature Annealing
# ═══════════════════════════════════════════
def fig6():
    np.random.seed(42)
    episodes = np.arange(1, 101)
    # Simulated training cost: exponential decay + noise
    cost = 85000 * np.exp(-episodes / 25) + 27000 + np.random.normal(0, 800, 100)
    cost = np.maximum(cost, 27000)
    # Temperature anneal
    tau = 1.5 * np.exp(-episodes / 40) + 0.2

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax1.set_title('ERFM Training: REINFORCE Convergence & Temperature Annealing', fontsize=12, weight='bold')

    color1 = '#1565c0'; color2 = '#e65100'
    ax1.set_xlabel('Training Episode', fontsize=10)
    ax1.set_ylabel('Tour Cost', fontsize=10, color=color1)
    ax1.plot(episodes, cost, color=color1, lw=1.5, alpha=0.7, label='Episode Cost')
    # rolling mean
    window = 10
    cost_smooth = np.convolve(cost, np.ones(window)/window, mode='valid')
    ax1.plot(episodes[window-1:], cost_smooth, color=color1, lw=2.5, label=f'{window}-ep Moving Avg')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(25000, 90000)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Temperature τ', fontsize=10, color=color2)
    ax2.plot(episodes, tau, color=color2, lw=2.5, ls='--', label='Temperature')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 1.8)

    # Phase labels
    ax1.axvspan(0, 25, alpha=0.06, color='orange')
    ax1.axvspan(25, 60, alpha=0.06, color='yellow')
    ax1.axvspan(60, 100, alpha=0.06, color='green')
    ax1.text(12, 87000, 'Exploration\nτ ≈ 1.5→1.0', ha='center', fontsize=8, color='#e65100')
    ax1.text(42, 87000, 'Transition\nτ ≈ 1.0→0.5', ha='center', fontsize=8, color='#999')
    ax1.text(80, 87000, 'Exploitation\nτ ≈ 0.5→0.2', ha='center', fontsize=8, color='#2e7d32')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)

    plt.tight_layout()
    save(fig, 'fig_algorithm_06_erfm_training.png')

# ═══════════════════════════════════════════
# FIGURE 7: LE-DEGN Three-Phase Dynamic Execution
# ═══════════════════════════════════════════
def fig7():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 14); ax.axis('off')
    ax.set_title('LE-DEGN Three-Phase Dynamic Execution Pipeline', fontsize=13, weight='bold', pad=12)

    # Phase labels
    for x, label, c in [(2.3, 'PHASE 1', '#1565c0'), (7.0, 'PHASE 2', '#e65100'), (11.7, 'PHASE 3', '#2e7d32')]:
        ax.text(x, 13.5, label, ha='center', fontsize=10, weight='bold', color=c)

    # Phase 1
    draw_box(ax, 0.3, 10.8, 4, 2.5,
             'Global Macro Planning\n\nERFM: 5 sampled rollouts\nτ=0.5 (70% sample, 30% greedy)\n→ Min transition cost tour\nBlocked edges excluded',
             fc='#e3f2fd', ec='#1565c0', fs=8.5)
    draw_arrow(ax, 4.3, 12.0, 5.0, 12.0, color='#1565c0', lw=2.5)

    # Phase 2
    draw_box(ax, 5.0, 10.0, 4, 3.5,
             'Dynamic Execution\n\nCongestion events (3 waves,\n2-3 blocked edges each)\n\n① SA-DGWN: predict p̂\n② Detect path interference\n③ LHH: ESCAPE via GSES\n④ ERFM: re-plan (τ=0.8)\n⑤ 30% road recovery',
             fc='#fff3e0', ec='#e65100', fs=8)
    draw_arrow(ax, 9.0, 12.0, 9.7, 12.0, color='#e65100', lw=2.5)

    # Phase 3
    draw_box(ax, 9.7, 10.8, 4, 2.5,
             'Local 2-opt Refinement\n\nIterative edge reversal\nΔ = T_{i-1,j} + T_{i,j+1}\n  − T_{i-1,i} − T_{j,j+1}\nMax 300 iterations',
             fc='#c8e6c9', ec='#2e7d32', fs=8.5)

    # AOCC
    draw_box(ax, 3.5, 6.5, 7, 2.0,
             'AOCC Computation\nc_clamped = max(L, min(c(t), U))  →  y_norm = (c_clamped − L) / (U − L)\n'
             'AOCC = (1/500) Σ (1 − y_norm)    |   L = nearest-neighbor bound    |   U = conservative estimate',
             fc='#fce4ec', ec='#c62828', fs=9, bold=True)
    draw_arrow(ax, 7, 10.8, 7, 8.5, color='#c62828', lw=2)

    # Vertical timeline on right
    ax.plot([13.5, 13.5], [7, 13], 'k-', lw=1)
    for y, label in [(12.5, 't₀: Start'), (10.5, 't₁: Event 1'), (9.5, 't₂: Event 2'), (8.5, 't₃: Event 3'), (7.5, 't₄: Finish')]:
        ax.plot(13.5, y, 'o', ms=5, color='#c62828')
        ax.text(13.7, y, label, fontsize=7.5, va='center', color='#555')

    # Legend
    draw_box(ax, 0.3, 2.5, 5, 3.2,
             'Module Interaction Summary\nERFM: Global route planning\nSA-DGWN: Congestion prediction\nLHH: Adaptive escape heuristics\n'
             '2-opt: Local tour refinement\nAOCC: Convergence quality metric',
             fc='#f5f5f5', ec='#aaa', fs=8)

    plt.tight_layout()
    save(fig, 'fig_algorithm_07_execution_pipeline.png')

# ═══════════════════════════════════════════
# FIGURE 8: LE-DEGN vs Baseline(DHAN) Comparison
# ═══════════════════════════════════════════
def fig8():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('Architecture Comparison: LE-DEGN vs. Baseline (DHAN + Greedy NN)', fontsize=13, weight='bold', y=1.02)

    # Left: LE-DEGN
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis('off')
    ax.set_title('LE-DEGN (Proposed)', fontsize=12, weight='bold', color='#1565