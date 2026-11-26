#!/usr/bin/env python3
"""Generate clean, original 300-dpi conceptual diagrams for RL study notes.

Replaces textbook-derived hand scans with original programmatic schematics and
mathematical plots (plus the existing Gaussian PDF generator in make-fig-13-1.py).

Usage: python3 scripts/make-figures.py [--out figures]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# Consistent clean academic palette
NAVY = "#1d3557"
BLUE = "#2c5f8a"
TEAL = "#2a9d8f"
AMBER = "#d97706"
CORAL = "#c84b31"
SLATE = "#475569"
LIGHT_BG = "#f8fafc"
LIGHT_BLUE = "#e6f0f8"
LIGHT_TEAL = "#e6f6f3"
LIGHT_AMBER = "#fef3c7"

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "mathtext.fontset": "cm",
    "axes.edgecolor": SLATE,
    "axes.linewidth": 0.9,
})


def save(fig: plt.Figure, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


def fig_ch03_mdp_loop(out: Path) -> None:
    """Original Agent-Environment interaction loop schematic."""
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    agent = FancyBboxPatch((3.6, 3.1), 2.8, 1.0, boxstyle="round,pad=0.12",
                           fc=LIGHT_BLUE, ec=NAVY, lw=1.8)
    env = FancyBboxPatch((3.6, 0.5), 2.8, 1.0, boxstyle="round,pad=0.12",
                         fc=LIGHT_TEAL, ec=TEAL, lw=1.8)
    ax.add_patch(agent)
    ax.add_patch(env)
    ax.text(5.0, 3.6, "Agent", ha="center", va="center", fontsize=13, weight="bold", color=NAVY)
    ax.text(5.0, 3.28, r"Policy $\pi(a \mid s)$", ha="center", va="center", fontsize=9.5, color=SLATE)
    ax.text(5.0, 1.0, "Environment", ha="center", va="center", fontsize=13, weight="bold", color=TEAL)
    ax.text(5.0, 0.68, r"Dynamics $p(s', r \mid s, a)$", ha="center", va="center", fontsize=9.5, color=SLATE)

    # Action arrow (right side: Agent -> Env)
    ax.annotate("", xy=(6.55, 1.0), xytext=(6.55, 3.6),
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5",
                                connectionstyle="arc3,rad=-0.45", lw=1.8, color=NAVY))
    ax.text(8.55, 2.3, "Action\n" + r"$A_t \in \mathcal{A}(S_t)$", ha="center", va="center",
            fontsize=10.5, color=NAVY, weight="bold")

    # State & Reward arrows (left side: Env -> Agent)
    ax.annotate("", xy=(3.45, 3.8), xytext=(3.45, 1.15),
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5",
                                connectionstyle="arc3,rad=-0.42", lw=1.8, color=TEAL))
    ax.annotate("", xy=(3.45, 3.35), xytext=(3.45, 0.8),
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5",
                                connectionstyle="arc3,rad=-0.58", lw=1.6, color=AMBER, ls="--"))

    # Time-step tick marker
    ax.plot([1.05, 1.75], [2.3, 2.3], color=SLATE, lw=1.2, ls=":")
    ax.text(1.4, 2.52, r"$t \to t+1$", ha="center", va="bottom", fontsize=9, color=SLATE, style="italic")

    ax.text(2.45, 3.05, r"State $S_{t+1}$", ha="right", va="center", fontsize=10.5, color=TEAL, weight="bold")
    ax.text(1.55, 1.45, r"Reward $R_{t+1}$", ha="center", va="center", fontsize=10.5, color=AMBER, weight="bold")

    save(fig, out, "ch03-mdp-loop.png")


def fig_ch04_gpi(out: Path) -> None:
    """Original Generalized Policy Iteration (GPI) interaction schematic."""
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.0)
    ax.axis("off")

    # Left panel: cyclic loop
    eval_box = FancyBboxPatch((0.5, 3.2), 3.3, 1.0, boxstyle="round,pad=0.1",
                              fc=LIGHT_BLUE, ec=BLUE, lw=1.6)
    imp_box = FancyBboxPatch((0.5, 0.8), 3.3, 1.0, boxstyle="round,pad=0.1",
                             fc=LIGHT_TEAL, ec=TEAL, lw=1.6)
    ax.add_patch(eval_box)
    ax.add_patch(imp_box)
    ax.text(2.15, 3.8, "Evaluation", ha="center", va="center", fontsize=11.5, weight="bold", color=NAVY)
    ax.text(2.15, 3.45, r"$V \to v_\pi$", ha="center", va="center", fontsize=10, color=SLATE)
    ax.text(2.15, 1.4, "Improvement", ha="center", va="center", fontsize=11.5, weight="bold", color=TEAL)
    ax.text(2.15, 1.05, r"$\pi \to \mathrm{greedy}(V)$", ha="center", va="center", fontsize=10, color=SLATE)

    ax.annotate("", xy=(3.5, 1.9), xytext=(3.5, 3.1),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.45",
                                connectionstyle="arc3,rad=-0.25", lw=1.6, color=BLUE))
    ax.annotate("", xy=(0.8, 3.1), xytext=(0.8, 1.9),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.45",
                                connectionstyle="arc3,rad=-0.25", lw=1.6, color=TEAL))
    ax.text(4.15, 2.5, r"$V$", fontsize=11, color=BLUE, weight="bold")
    ax.text(0.15, 2.5, r"$\pi$", fontsize=11, color=TEAL, weight="bold")

    # Right panel: converging geometry toward (v*, pi*)
    x = np.linspace(5.3, 9.3, 100)
    y_eval = 4.2 - 0.55 * (9.3 - x) ** 0.85
    y_imp = 4.2 - 1.15 * (9.3 - x) ** 0.85
    ax.plot(x, y_eval, color=BLUE, lw=2.0, label=r"$V = v_\pi$")
    ax.plot(x, y_imp, color=TEAL, lw=2.0, label=r"$\pi = \mathrm{greedy}(V)$")
    ax.scatter([9.3], [4.2], color=CORAL, s=65, zorder=5)
    ax.text(9.35, 4.35, r"$(v_*, \pi_*)$", ha="right", va="bottom", fontsize=11, color=CORAL, weight="bold")

    # Zig-zag trajectory between the two curves
    pts = [(5.7, 1.5), (6.3, 2.85), (7.0, 2.35), (7.6, 3.4), (8.2, 3.2), (8.7, 3.85), (9.2, 4.13)]
    for i in range(len(pts) - 1):
        c = BLUE if i % 2 == 0 else TEAL
        ax.annotate("", xy=pts[i + 1], xytext=pts[i],
                    arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.3", lw=1.3, color=c))
    ax.text(7.3, 4.45, r"$V = v_\pi$", color=BLUE, fontsize=9.5, weight="bold")
    ax.text(7.8, 1.85, r"$\pi = \mathrm{greedy}(V)$", color=TEAL, fontsize=9.5, weight="bold")
    ax.text(7.5, 0.15, "Alternating updates converge to optimality", ha="center", fontsize=9, color=SLATE, style="italic")

    save(fig, out, "ch04-gpi-loop.png")


def fig_ch06_td_backups(out: Path) -> None:
    """Original side-by-side 1-step backup schematics: TD(0), Sarsa, Q-learning, Expected Sarsa."""
    fig, axes = plt.subplots(1, 4, figsize=(9.2, 3.0))
    titles = ["TD(0)", "Sarsa", "Q-learning", "Expected Sarsa"]

    def draw_state(ax, x, y, label=None, dx=0.22):
        ax.add_patch(Circle((x, y), 0.14, fc="white", ec=NAVY, lw=1.6, zorder=4))
        if label:
            ax.text(x + dx, y, label, va="center", fontsize=9.5, color=NAVY)

    def draw_action(ax, x, y, label=None, dx=0.2):
        ax.add_patch(Circle((x, y), 0.10, fc=BLUE, ec=NAVY, lw=1.2, zorder=4))
        if label:
            ax.text(x + dx, y, label, va="center", fontsize=9.5, color=BLUE)

    for ax, title in zip(axes, titles):
        ax.set_xlim(-1.2, 1.4)
        ax.set_ylim(-0.3, 2.7)
        ax.axis("off")
        ax.set_title(title, fontsize=11, weight="bold", color=NAVY, pad=6)

    # 1. TD(0): S -> A -> S'
    ax = axes[0]
    ax.plot([0, 0], [2.2, 1.3], color=SLATE, lw=1.5)
    ax.plot([0, 0], [1.3, 0.4], color=SLATE, lw=1.5)
    draw_state(ax, 0, 2.2, r"$S_t$")
    draw_action(ax, 0, 1.3, r"$A_t$")
    draw_state(ax, 0, 0.4, r"$S_{t+1}$")
    ax.text(-0.18, 0.85, r"$R_{t+1}$", ha="right", va="center", fontsize=9, color=AMBER)

    # 2. Sarsa: (S,A) -> S' -> A'
    ax = axes[1]
    ax.plot([0, 0], [2.2, 1.3], color=SLATE, lw=1.5)
    ax.plot([0, 0], [1.3, 0.4], color=SLATE, lw=1.5)
    draw_action(ax, 0, 2.2, r"$S_t, A_t$")
    draw_state(ax, 0, 1.3, r"$S_{t+1}$")
    draw_action(ax, 0, 0.4, r"$A_{t+1}$")
    ax.text(-0.18, 1.75, r"$R_{t+1}$", ha="right", va="center", fontsize=9, color=AMBER)

    # 3. Q-learning: (S,A) -> S' -> max over a'
    ax = axes[2]
    ax.plot([0, 0], [2.2, 1.3], color=SLATE, lw=1.5)
    for x_a in (-0.65, 0.0, 0.65):
        ax.plot([0, x_a], [1.3, 0.4], color=SLATE, lw=1.4)
        draw_action(ax, x_a, 0.4)
    arc = patches.Arc((0, 1.3), 0.72, 0.72, theta1=215, theta2=325, color=CORAL, lw=1.8)
    ax.add_patch(arc)
    ax.text(0, 0.76, r"$\max$", ha="center", va="center", fontsize=8.5, color=CORAL, weight="bold")
    draw_action(ax, 0, 2.2, r"$S_t, A_t$")
    draw_state(ax, 0, 1.3, r"$S_{t+1}$")
    ax.text(-0.18, 1.75, r"$R_{t+1}$", ha="right", va="center", fontsize=9, color=AMBER)

    # 4. Expected Sarsa: (S,A) -> S' -> weighted expectation over a'
    ax = axes[3]
    ax.plot([0, 0], [2.2, 1.3], color=SLATE, lw=1.5)
    for x_a in (-0.65, 0.0, 0.65):
        ax.plot([0, x_a], [1.3, 0.4], color=TEAL, lw=1.4)
        draw_action(ax, x_a, 0.4)
    ax.text(0, 0.05, r"$\sum_a \pi(a \mid S_{t+1}) Q$", ha="center", va="center", fontsize=8.5, color=TEAL)
    draw_action(ax, 0, 2.2, r"$S_t, A_t$")
    draw_state(ax, 0, 1.3, r"$S_{t+1}$")
    ax.text(-0.18, 1.75, r"$R_{t+1}$", ha="right", va="center", fontsize=9, color=AMBER)

    fig.tight_layout()
    save(fig, out, "ch06-td-backups.png")


def fig_ch07_nstep_spectrum(out: Path) -> None:
    """Original n-step return spectrum from TD(0) through n-step TD to Monte Carlo."""
    fig, ax = plt.subplots(figsize=(8.0, 3.2))
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.6, 3.6)
    ax.axis("off")

    cols = [(1.0, "1-step\n(TD(0))", 1), (3.0, "2-step", 2), (5.0, "3-step", 3), (8.0, r"$\infty$-step" + "\n(Monte Carlo)", 4)]
    for x, label, depth in cols:
        ax.text(x, 3.25, label, ha="center", va="center", fontsize=10, weight="bold", color=NAVY)
        ys = np.linspace(2.6, 0.35, 5)
        for step in range(depth):
            ax.plot([x, x], [ys[step], ys[step + 1]], color=BLUE, lw=1.6)
            ax.add_patch(Circle((x, ys[step]), 0.13, fc="white", ec=NAVY, lw=1.5, zorder=4))
            mid = 0.5 * (ys[step] + ys[step + 1])
            ax.add_patch(Circle((x, mid), 0.075, fc=BLUE, ec=NAVY, lw=1.0, zorder=4))
        if depth < 4:
            # Bootstrapped leaf state
            ax.add_patch(Circle((x, ys[depth]), 0.13, fc=LIGHT_AMBER, ec=AMBER, lw=1.8, zorder=4))
            ax.text(x + 0.25, ys[depth], r"$V(S_{t+" + str(depth) + "})$", va="center", fontsize=8.5, color=AMBER)
        else:
            # Terminal square
            sq = patches.Rectangle((x - 0.13, ys[4] - 0.13), 0.26, 0.26, fc=TEAL, ec=NAVY, lw=1.4, zorder=4)
            ax.add_patch(sq)
            ax.text(x + 0.25, ys[4], r"$S_T$", va="center", fontsize=9, color=TEAL, weight="bold")

    ax.text(6.5, 1.5, r"$\cdots$", ha="center", va="center", fontsize=18, color=SLATE)
    ax.annotate("", xy=(8.6, -0.25), xytext=(0.4, -0.25),
                arrowprops=dict(arrowstyle="<->,head_width=0.25,head_length=0.4", lw=1.5, color=SLATE))
    ax.text(0.4, -0.48, "Lower variance, more bias", ha="left", fontsize=8.5, color=SLATE, style="italic")
    ax.text(8.6, -0.48, "Zero bias, higher variance", ha="right", fontsize=8.5, color=SLATE, style="italic")

    save(fig, out, "ch07-nstep-spectrum.png")


def fig_ch08_dyna_unified(out: Path) -> None:
    """Original two-panel schematic: Dyna architecture and the 2D unified RL plane."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.8))

    # Left: Dyna cycle
    ax1.set_xlim(-0.3, 10.3)
    ax1.set_ylim(-0.2, 6.2)
    ax1.axis("off")
    ax1.set_title("Dyna: Learning + Planning", fontsize=11, weight="bold", color=NAVY)

    boxes = {
        "exp": (0.1, 2.45, 2.4, 1.1, "Real\nExperience", LIGHT_TEAL, TEAL),
        "val": (3.5, 4.6, 3.0, 1.1, "Value / Policy\n(Q, π)", LIGHT_BLUE, NAVY),
        "mod": (3.5, 0.3, 3.0, 1.1, "Learned Model\n(S, A → R, S')", LIGHT_AMBER, AMBER),
        "sim": (7.5, 2.45, 2.5, 1.1, "Simulated\nExperience", "#f1f5f9", SLATE),
    }
    for x, y, w, h, txt, fc, ec in boxes.values():
        ax1.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", fc=fc, ec=ec, lw=1.6))
        ax1.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=9.0, weight="bold", color=ec)

    # Acting (top-left outer arc) and Direct RL (inner arrow)
    ax1.annotate("", xy=(1.0, 3.65), xytext=(3.4, 5.25),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35",
                                 connectionstyle="arc3,rad=0.2", lw=1.5, color=TEAL))
    ax1.text(1.45, 4.95, "Acting", ha="center", va="center", fontsize=8.3, color=TEAL, weight="bold")

    ax1.annotate("", xy=(3.4, 4.75), xytext=(1.7, 3.65),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=1.5, color=BLUE))
    ax1.text(2.95, 3.92, "Direct RL", ha="center", va="center", fontsize=8.3, color=BLUE, weight="bold")

    # Model learning (bottom-left)
    ax1.annotate("", xy=(3.4, 0.95), xytext=(1.3, 2.35),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=1.5, color=AMBER))
    ax1.text(1.55, 1.25, "Model\nlearning", ha="center", va="center", fontsize=8.2, color=AMBER, weight="bold")

    # Sample model (bottom-right)
    ax1.annotate("", xy=(8.7, 2.35), xytext=(6.6, 0.95),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=1.5, color=SLATE))
    ax1.text(8.45, 1.25, "Sample\nmodel", ha="center", va="center", fontsize=8.2, color=SLATE, weight="bold")

    # Planning (top-right)
    ax1.annotate("", xy=(6.6, 5.05), xytext=(8.7, 3.65),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=1.5, color=CORAL))
    ax1.text(8.45, 4.75, "Planning", ha="center", va="center", fontsize=8.5, color=CORAL, weight="bold")

    # Right: 2D Unified RL plane (Depth vs Width)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_xticks([1.2, 8.8])
    ax2.set_xticklabels(["Sample\nupdates", "Expected\nupdates"], fontsize=9.5, color=NAVY)
    ax2.set_yticks([1.2, 8.8])
    ax2.set_yticklabels(["Shallow\n(1-step)", "Deep\n(full episode)"], fontsize=9.5, color=NAVY)
    ax2.set_xlabel("Backup width", fontsize=10, weight="bold", color=SLATE)
    ax2.set_ylabel("Backup depth", fontsize=10, weight="bold", color=SLATE)
    ax2.set_title("Two Dimensions of RL Updates", fontsize=11, weight="bold", color=NAVY)
    ax2.grid(True, ls=":", alpha=0.5)

    corners = [
        (1.4, 1.4, "TD(0) / Sarsa /\nQ-learning", BLUE),
        (8.6, 1.4, "Dynamic\nProgramming", TEAL),
        (1.4, 8.6, "Monte Carlo", AMBER),
        (8.6, 8.6, "Exhaustive\nSearch", CORAL),
        (1.4, 5.0, "n-step TD /\nTD(λ)", NAVY),
        (5.0, 5.0, "n-step Q(σ) /\nTree Backup", SLATE),
    ]
    for cx, cy, lbl, col in corners:
        ax2.scatter([cx], [cy], s=70, color=col, zorder=5)
        dx = 0.35 if cx < 5 else (-0.35 if cx > 6 else 0.0)
        ha = "left" if cx < 5 else ("right" if cx > 6 else "center")
        dy = 0.7 if cx == 5.0 else 0.0
        ax2.text(cx + dx, cy + dy, lbl, ha=ha, va="center", fontsize=8.8, weight="bold", color=col)

    fig.tight_layout(w_pad=2.5)
    save(fig, out, "ch08-dyna-unified.png")


def fig_ch09_coarse_rbf(out: Path) -> None:
    """Original two-panel feature representation plot: 2D coarse coding & 1D Gaussian RBFs."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.6))

    # Left: 2D overlapping circular receptive fields
    rng = np.random.default_rng(7)
    centers = rng.uniform(0.18, 0.82, size=(14, 2))
    # Guarantee two query states share exactly one circle
    s1 = np.array([0.42, 0.48])
    s2 = np.array([0.62, 0.56])
    centers[0] = np.array([0.52, 0.52])
    r = 0.165
    for i, (cx, cy) in enumerate(centers):
        in_s1 = np.hypot(s1[0] - cx, s1[1] - cy) <= r
        in_s2 = np.hypot(s2[0] - cx, s2[1] - cy) <= r
        if in_s1 and in_s2:
            fc, ec, alpha, lw = LIGHT_AMBER, AMBER, 0.55, 2.0
        elif in_s1 or in_s2:
            fc, ec, alpha, lw = LIGHT_BLUE, BLUE, 0.35, 1.3
        else:
            fc, ec, alpha, lw = "none", SLATE, 0.35, 0.9
        ax1.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=lw, alpha=alpha))

    ax1.scatter([s1[0], s2[0]], [s1[1], s2[1]], color=CORAL, s=55, zorder=6)
    ax1.text(s1[0] - 0.03, s1[1] - 0.05, r"$s$", fontsize=11, weight="bold", color=CORAL, ha="right")
    ax1.text(s2[0] + 0.03, s2[1] + 0.03, r"$s'$", fontsize=11, weight="bold", color=CORAL, ha="left")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_aspect("equal")
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title("2D Coarse Coding (Shared Receptive Fields)", fontsize=10.5, weight="bold", color=NAVY)

    # Right: 1D Gaussian RBFs
    x = np.linspace(0, 10, 400)
    mus = [1.5, 3.5, 5.5, 7.5, 9.0]
    sigma = 1.05
    palette = [NAVY, BLUE, TEAL, AMBER, CORAL]
    for idx, (mu, col) in enumerate(zip(mus, palette), 1):
        y = np.exp(-0.5 * ((x - mu) / sigma) ** 2)
        ax2.plot(x, y, color=col, lw=1.8, label=rf"$x_{idx}(s)$")
        ax2.fill_between(x, 0, y, color=col, alpha=0.08)
    s_q = 4.6
    ax2.axvline(s_q, color=SLATE, ls="--", lw=1.1)
    ax2.text(s_q + 0.12, 0.95, r"state $s$", fontsize=9, color=SLATE)
    ax2.set_xlabel("1D State Space", fontsize=9.5, color=SLATE)
    ax2.set_ylabel("Feature Activation", fontsize=9.5, color=SLATE)
    ax2.set_ylim(0, 1.12)
    ax2.set_title("1D Gaussian Radial Basis Functions", fontsize=10.5, weight="bold", color=NAVY)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.tight_layout()
    save(fig, out, "ch09-coarse-rbf.png")


def fig_ch11_linear_projection(out: Path) -> None:
    """Original geometric schematic of linear VFA projection in value-function space."""
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Draw 2D linear subspace plane (parallelogram)
    plane = patches.Polygon([(0.8, 1.3), (7.5, 0.8), (9.3, 3.2), (2.6, 3.7)],
                            closed=True, fc=LIGHT_BLUE, ec=BLUE, lw=1.6, alpha=0.75)
    ax.add_patch(plane)
    ax.text(1.45, 1.55, r"Representable subspace $\{ \hat{v}(\mathbf{w}) = \mathbf{X}\mathbf{w} \}$",
            fontsize=9.2, color=NAVY, style="italic")

    # True value function v_pi above the plane
    v_pi = (4.2, 5.15)
    p_ve = (4.2, 2.45)     # Orthogonal projection Pi v_pi (min VE)
    p_td = (5.7, 2.2)      # TD fixed point (min PBE = 0)
    p_be = (6.8, 2.55)     # Min BE
    p_tde = (7.4, 1.75)    # Min TDE

    # Orthogonal projection line + right-angle tick
    ax.plot([v_pi[0], p_ve[0]], [v_pi[1], p_ve[1]], color=NAVY, lw=1.8, ls="--")
    ax.plot([p_ve[0], p_ve[0] + 0.25, p_ve[0] + 0.25],
            [p_ve[1] + 0.25, p_ve[1] + 0.25, p_ve[1]], color=NAVY, lw=1.1)
    ax.text(v_pi[0] - 0.18, 3.8, r"$\Pi$", fontsize=12, color=NAVY, weight="bold", ha="right")

    # Bellman operator arrow from p_td out of plane, then projected back
    bv_td = (5.7, 4.35)
    ax.annotate("", xy=bv_td, xytext=p_td,
                arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=1.5, color=TEAL))
    ax.annotate("", xy=p_td, xytext=bv_td,
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.3",
                                connectionstyle="arc3,rad=-0.25", lw=1.2, ls=":", color=TEAL))
    ax.text(6.05, 4.42, r"$B_\pi \hat{v}(\mathbf{w}_{\mathrm{TD}})$", fontsize=9.5, color=TEAL, weight="bold")
    ax.text(6.35, 3.72, r"$\Pi B_\pi \hat{v} = \hat{v}$", fontsize=8.8, color=TEAL, style="italic")

    # Plot points
    pts = [
        (v_pi, r"$v_\pi$ (true value)", CORAL, (0.2, 0.15)),
        (p_ve, r"$\Pi v_\pi$ (min $\overline{\mathrm{VE}}$)", NAVY, (-0.15, -0.38)),
        (p_td, r"$\mathbf{w}_{\mathrm{TD}}$ (min $\overline{\mathrm{PBE}}$)", TEAL, (-0.1, -0.45)),
        (p_be, r"min $\overline{\mathrm{BE}}$", AMBER, (0.2, 0.12)),
        (p_tde, r"min $\overline{\mathrm{TDE}}$", SLATE, (0.22, -0.15)),
    ]
    for (px, py), lbl, col, (dx, dy) in pts:
        ax.scatter([px], [py], color=col, s=60, zorder=6)
        ax.text(px + dx, py + dy, lbl, fontsize=9.5, color=col, weight="bold", va="center")

    save(fig, out, "ch11-linear-projection.png")


def fig_ch12_lambda_weights(out: Path) -> None:
    """Original plot of geometric n-step return weights (1-lambda)*lambda^(n-1) across lambda values."""
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ns = np.arange(1, 11)
    width = 0.25
    configs = [(0.2, NAVY, -width), (0.5, TEAL, 0.0), (0.8, AMBER, width)]

    for lam, col, offset in configs:
        w = (1.0 - lam) * (lam ** (ns - 1))
        ax.bar(ns + offset, w, width=width, color=col, alpha=0.88,
               label=rf"$\lambda = {lam}$  (remaining tail: $\lambda^{{10}} = {lam**10:.3f}$)")

    ax.set_xticks(ns)
    ax.set_xticklabels([f"{n}-step" for n in ns], fontsize=8.5)
    ax.set_ylabel(r"Weight $(1-\lambda)\lambda^{n-1}$", fontsize=10, color=NAVY)
    ax.set_xlabel("Component $n$-step return inside $G_t^\\lambda$", fontsize=10, color=NAVY)
    ax.set_title(r"Geometric Weighting of $n$-Step Returns in the $\lambda$-Return", fontsize=11, weight="bold", color=NAVY)
    ax.legend(frameon=False, fontsize=8.8)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save(fig, out, "ch12-lambda-weights.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="figures")
    args = parser.parse_args()
    out = Path(args.out)

    print(f"Generating 8 original conceptual figures into {out}/ ...")
    fig_ch03_mdp_loop(out)
    fig_ch04_gpi(out)
    fig_ch06_td_backups(out)
    fig_ch07_nstep_spectrum(out)
    fig_ch08_dyna_unified(out)
    fig_ch09_coarse_rbf(out)
    fig_ch11_linear_projection(out)
    fig_ch12_lambda_weights(out)
    print("Done (8 original figures generated).")


if __name__ == "__main__":
    main()
