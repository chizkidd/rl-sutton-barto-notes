#!/usr/bin/env python3
"""Generate crisp, original 300-dpi conceptual diagrams for RL study notes.

Produces 23 programmatic schematics and mathematical plots across Chapters 3–12
(plus Figure 13.1 via scripts/make-fig-13-1.py = 24 figures total), designed for
high legibility, generous spacing, and zero text/border collisions across HTML,
PDF, and EPUB outputs.

Usage:
    python3 scripts/make-figures.py [--out figures] [--preview-dir DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle, Polygon
import matplotlib.patheffects as pe
import numpy as np

# Consistent academic palette
NAVY = "#1d3557"
BLUE = "#2c5f8a"
TEAL = "#2a9d8f"
AMBER = "#d97706"
CORAL = "#c84b31"
SLATE = "#475569"
DARK = "#1e293b"
LIGHT_BG = "#f8fafc"
LIGHT_BLUE = "#e6f0f8"
LIGHT_TEAL = "#e6f6f3"
LIGHT_AMBER = "#fef3c7"
LIGHT_CORAL = "#fde8e4"
LIGHT_SLATE = "#f1f5f9"

HALO = [pe.withStroke(linewidth=3.2, foreground="white")]

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "mathtext.fontset": "cm",
    "axes.edgecolor": SLATE,
    "axes.linewidth": 1.0,
})


def save(fig: plt.Figure, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


def draw_state(ax, x, y, r=0.16, fc="white", ec=NAVY, lw=1.8, zorder=5):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=zorder))


def draw_action(ax, x, y, r=0.10, fc=BLUE, ec=NAVY, lw=1.3, zorder=5):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=zorder))


def draw_terminal(ax, x, y, half=0.15, fc=TEAL, ec=NAVY, lw=1.6, zorder=5):
    ax.add_patch(Rectangle((x - half, y - half), 2 * half, 2 * half,
                           fc=fc, ec=ec, lw=lw, zorder=zorder))


# ---------------------------------------------------------------------------
# Chapter 3
# ---------------------------------------------------------------------------

def fig_ch03_mdp_loop(out: Path) -> None:
    """Figure 3.1: Original Agent-Environment interaction loop schematic."""
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    ax.set_xlim(0.0, 10.6)
    ax.set_ylim(0.1, 4.9)
    ax.axis("off")

    agent = FancyBboxPatch((3.7, 3.35), 3.1, 1.15, boxstyle="round,pad=0.14",
                           fc=LIGHT_BLUE, ec=NAVY, lw=2.0)
    env = FancyBboxPatch((3.7, 0.50), 3.1, 1.15, boxstyle="round,pad=0.14",
                         fc=LIGHT_TEAL, ec=TEAL, lw=2.0)
    ax.add_patch(agent)
    ax.add_patch(env)
    ax.text(5.25, 4.10, "Agent", ha="center", va="center", fontsize=14.5, weight="bold", color=NAVY)
    ax.text(5.25, 3.68, r"Policy $\pi(a \mid s)$", ha="center", va="center", fontsize=11.5, color=SLATE)
    ax.text(5.25, 1.25, "Environment", ha="center", va="center", fontsize=14.5, weight="bold", color=TEAL)
    ax.text(5.25, 0.83, r"Dynamics $p(s', r \mid s, a)$", ha="center", va="center", fontsize=11.5, color=SLATE)

    # Action arrow (right side: Agent -> Env)
    ax.annotate("", xy=(7.02, 1.10), xytext=(7.02, 3.90),
                arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.55",
                                connectionstyle="arc3,rad=-0.45", lw=2.1, color=NAVY))
    ax.text(9.35, 2.50, "Action\n" + r"$A_t \in \mathcal{A}(S_t)$", ha="center", va="center",
            fontsize=12.5, color=NAVY, weight="bold")

    # State & Reward arrows (left side: Env -> Agent)
    ax.annotate("", xy=(3.50, 4.15), xytext=(3.50, 1.30),
                arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.55",
                                connectionstyle="arc3,rad=-0.40", lw=2.1, color=TEAL))
    ax.annotate("", xy=(3.50, 3.60), xytext=(3.50, 0.80),
                arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.55",
                                connectionstyle="arc3,rad=-0.56", lw=1.9, color=AMBER, ls="--"))

    # Time-step divider marker
    ax.plot([0.85, 1.65], [2.48, 2.48], color=SLATE, lw=1.5, ls=":")
    ax.text(1.25, 2.66, r"$t \to t+1$", ha="center", va="bottom", fontsize=11.0, color=SLATE, style="italic")

    ax.text(2.45, 3.55, r"State $S_{t+1}$", ha="right", va="center", fontsize=12.5, color=TEAL, weight="bold")
    ax.text(1.55, 1.35, r"Reward $R_{t+1}$", ha="center", va="center", fontsize=12.5, color=AMBER, weight="bold")

    save(fig, out, "ch03-mdp-loop.png")


# ---------------------------------------------------------------------------
# Chapter 4
# ---------------------------------------------------------------------------

def fig_ch04_gpi(out: Path) -> None:
    """Figure 4.1: Generalized Policy Iteration — cyclic convergence & exact wedge geometry."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.6), gridspec_kw={"width_ratios": [1.0, 1.25]})

    # --- Left panel: pi <-> V loop converging via vertical dots to (pi*, v*) ---
    ax1.set_xlim(0.0, 6.2)
    ax1.set_ylim(0.0, 6.0)
    ax1.axis("off")
    ax1.set_title("GPI Interaction Loop", fontsize=13.5, weight="bold", color=NAVY, pad=10)

    # Top cycle: pi on left, V on right
    pi_box = FancyBboxPatch((0.55, 3.65), 1.35, 0.95, boxstyle="round,pad=0.12",
                            fc=LIGHT_TEAL, ec=TEAL, lw=2.0)
    v_box = FancyBboxPatch((4.25, 3.65), 1.35, 0.95, boxstyle="round,pad=0.12",
                           fc=LIGHT_BLUE, ec=BLUE, lw=2.0)
    ax1.add_patch(pi_box)
    ax1.add_patch(v_box)
    ax1.text(1.225, 4.125, r"$\pi$", ha="center", va="center", fontsize=16, weight="bold", color=TEAL)
    ax1.text(4.925, 4.125, r"$V$", ha="center", va="center", fontsize=16, weight="bold", color=NAVY)

    # Top arc: Evaluation (pi -> V)
    ax1.annotate("", xy=(4.15, 4.55), xytext=(2.00, 4.55),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5",
                                 connectionstyle="arc3,rad=-0.38", lw=2.1, color=BLUE))
    ax1.text(3.08, 5.45, "Evaluation", ha="center", va="center", fontsize=12.5, weight="bold", color=NAVY)
    ax1.text(3.08, 5.05, r"$V \to v_\pi$", ha="center", va="center", fontsize=11.5, color=BLUE)

    # Bottom arc: Improvement (V -> pi)
    ax1.annotate("", xy=(2.00, 3.68), xytext=(4.15, 3.68),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5",
                                 connectionstyle="arc3,rad=-0.38", lw=2.1, color=TEAL))
    ax1.text(3.08, 2.88, "Improvement", ha="center", va="center", fontsize=12.5, weight="bold", color=TEAL)
    ax1.text(3.08, 2.48, r"$\pi \to \mathrm{greedy}(V)$", ha="center", va="center", fontsize=11.5, color=SLATE)

    # Vertical convergence dots leading down to equilibrium (pi* <-> v*)
    for dy in (1.92, 1.68, 1.44):
        ax1.add_patch(Circle((3.08, dy), 0.055, fc=SLATE, ec="none"))

    # Fixed point box at bottom
    opt_box = FancyBboxPatch((1.35, 0.25), 3.45, 0.92, boxstyle="round,pad=0.12",
                             fc=LIGHT_CORAL, ec=CORAL, lw=2.0)
    ax1.add_patch(opt_box)
    ax1.text(3.08, 0.80, r"$\pi_* \;\rightleftarrows\; v_*$", ha="center", va="center",
             fontsize=15.5, weight="bold", color=CORAL)
    ax1.text(3.08, 0.42, "Optimal fixed point", ha="center", va="center",
             fontsize=10.5, color=SLATE, style="italic")

    # --- Right panel: crisp converging wedge meeting at (v*, pi*) ---
    ax2.set_xlim(0.0, 7.6)
    ax2.set_ylim(0.0, 6.0)
    ax2.axis("off")
    ax2.set_title("Geometric Convergence to Optimality", fontsize=13.5, weight="bold", color=NAVY, pad=10)

    # Upper line: V = v_pi, Lower line: pi = greedy(V), meeting cleanly at apex (6.7, 5.1)
    x_apex, y_apex = 6.65, 5.05
    m_top = 0.36
    m_bot = 0.84

    def y_top(x):
        return y_apex - m_top * (x_apex - x)

    def y_bot(x):
        return y_apex - m_bot * (x_apex - x)

    xs_top = np.linspace(0.65, x_apex, 100)
    xs_bot = np.linspace(1.65, x_apex, 100)
    ax2.plot(xs_top, y_top(xs_top), color=BLUE, lw=2.4, zorder=3)
    ax2.plot(xs_bot, y_bot(xs_bot), color=TEAL, lw=2.4, zorder=3)

    # Aligned rotated labels along the two boundary lines
    ax2.text(2.45, y_top(2.45) + 0.42, r"$V = v_\pi$  (evaluation)", color=BLUE,
             fontsize=11.5, weight="bold", ha="center", va="bottom", rotation=17)
    ax2.text(4.85, y_bot(4.85) - 0.58, r"$\pi = \mathrm{greedy}(V)$  (improvement)", color=TEAL,
             fontsize=11.5, weight="bold", ha="center", va="top", rotation=35)

    # Mathematically snapped zig-zag from explicit start point (V_0, pi_0)
    x_cur, y_cur = 1.55, 1.35
    ax2.scatter([x_cur], [y_cur], color=DARK, s=60, zorder=6)
    ax2.text(x_cur - 0.22, y_cur - 0.05, r"$(V_0, \pi_0)$", ha="right", va="center",
             fontsize=11.5, weight="bold", color=DARK)

    # Solve exact intersections iteratively
    m_eval = 2.6   # steep upward-right evaluation step toward V = v_pi
    m_imp = -0.22  # slight downward-right improvement step toward pi = greedy(V)
    pts = [(x_cur, y_cur)]
    for step in range(8):
        if step % 2 == 0:
            # Intersect y - y_cur = m_eval * (x - x_cur) with y = y_apex - m_top * (x_apex - x)
            # m_eval * x - m_eval * x_cur + y_cur = m_top * x + (y_apex - m_top * x_apex)
            x_next = ((y_apex - m_top * x_apex) + m_eval * x_cur - y_cur) / (m_eval - m_top)
            y_next = y_top(x_next)
        else:
            # Intersect y - y_cur = m_imp * (x - x_cur) with y = y_apex - m_bot * (x_apex - x)
            x_next = ((y_apex - m_bot * x_apex) + m_imp * x_cur - y_cur) / (m_imp - m_bot)
            y_next = y_bot(x_next)
        if x_next >= x_apex - 0.18:
            pts.append((x_apex, y_apex))
            break
        pts.append((x_next, y_next))
        x_cur, y_cur = x_next, y_next

    for i in range(len(pts) - 1):
        col = BLUE if i % 2 == 0 else TEAL
        ax2.annotate("", xy=pts[i + 1], xytext=pts[i],
                     arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.36",
                                     lw=1.7, color=col, shrinkA=0, shrinkB=1),
                     zorder=5)

    # Apex marker (v*, pi*)
    ax2.scatter([x_apex], [y_apex], color=CORAL, s=85, zorder=7)
    ax2.text(x_apex + 0.05, y_apex + 0.25, r"$(v_*, \pi_*)$", ha="center", va="bottom",
             fontsize=13.0, color=CORAL, weight="bold")

    ax2.text(3.8, 0.22, "Alternating evaluation & improvement steps converge to the fixed point",
             ha="center", va="center", fontsize=10.5, color=SLATE, style="italic")

    fig.tight_layout(w_pad=1.8)
    save(fig, out, "ch04-gpi-loop.png")


# ---------------------------------------------------------------------------
# Chapter 6 (renders BOTH upscaled 1x4 and 2x2 preview)
# ---------------------------------------------------------------------------

def _draw_ch06_panel(ax, kind: str) -> None:
    ax.set_xlim(-1.15, 1.38)
    ax.set_ylim(-0.35, 2.65)
    ax.axis("off")

    titles = {
        "td0": "TD(0)",
        "sarsa": "Sarsa",
        "qlearn": "Q-learning",
        "exp_sarsa": "Expected Sarsa",
    }
    ax.set_title(titles[kind], fontsize=14, weight="bold", color=NAVY, pad=8)

    if kind == "td0":
        ax.plot([0, 0], [2.25, 0.45], color=SLATE, lw=2.0)
        draw_state(ax, 0, 2.25, r=0.17)
        draw_action(ax, 0, 1.35, r=0.115)
        draw_state(ax, 0, 0.45, r=0.17, fc=LIGHT_AMBER, ec=AMBER, lw=2.1)
        ax.text(0.26, 2.25, r"$S_t$", va="center", fontsize=13, color=NAVY, weight="bold")
        ax.text(0.24, 1.35, r"$A_t$", va="center", fontsize=13, color=BLUE, weight="bold")
        ax.text(0.26, 0.45, r"$S_{t+1}$", va="center", fontsize=13, color=AMBER, weight="bold")
        ax.text(-0.20, 0.90, r"$R_{t+1}$", ha="right", va="center", fontsize=12.5, color=AMBER, weight="bold")

    elif kind == "sarsa":
        ax.plot([0, 0], [2.25, 0.45], color=SLATE, lw=2.0)
        draw_action(ax, 0, 2.25, r=0.115)
        draw_state(ax, 0, 1.35, r=0.17)
        draw_action(ax, 0, 0.45, r=0.115, fc=AMBER, ec=NAVY)
        ax.text(0.24, 2.25, r"$S_t, A_t$", va="center", fontsize=12.5, color=BLUE, weight="bold")
        ax.text(0.26, 1.35, r"$S_{t+1}$", va="center", fontsize=13, color=NAVY, weight="bold")
        ax.text(0.24, 0.45, r"$A_{t+1}$", va="center", fontsize=12.5, color=AMBER, weight="bold")
        ax.text(-0.20, 1.80, r"$R_{t+1}$", ha="right", va="center", fontsize=12.5, color=AMBER, weight="bold")

    elif kind == "qlearn":
        ax.plot([0, 0], [2.25, 1.35], color=SLATE, lw=2.0)
        for xa in (-0.72, 0.0, 0.72):
            ax.plot([0, xa], [1.35, 0.45], color=SLATE, lw=1.8)
            draw_action(ax, xa, 0.45, r=0.115)
        arc = patches.Arc((0, 1.35), 0.78, 0.78, theta1=212, theta2=328, color=CORAL, lw=2.3, zorder=6)
        ax.add_patch(arc)
        ax.text(0, 0.78, r"$\max$", ha="center", va="center", fontsize=12, color=CORAL,
                weight="bold", path_effects=HALO, zorder=7)
        draw_action(ax, 0, 2.25, r=0.115)
        draw_state(ax, 0, 1.35, r=0.17)
        ax.text(0.24, 2.25, r"$S_t, A_t$", va="center", fontsize=12.5, color=BLUE, weight="bold")
        ax.text(0.26, 1.35, r"$S_{t+1}$", va="center", fontsize=13, color=NAVY, weight="bold")
        ax.text(-0.20, 1.80, r"$R_{t+1}$", ha="right", va="center", fontsize=12.5, color=AMBER, weight="bold")
        ax.text(0, -0.05, r"$\max_a\, Q(S_{t+1}, a)$", ha="center", va="center",
                fontsize=11.5, color=CORAL, weight="bold")

    elif kind == "exp_sarsa":
        ax.plot([0, 0], [2.25, 1.35], color=SLATE, lw=2.0)
        for xa in (-0.72, 0.0, 0.72):
            ax.plot([0, xa], [1.35, 0.45], color=TEAL, lw=1.9)
            draw_action(ax, xa, 0.45, r=0.115, fc=TEAL, ec=NAVY)
        draw_action(ax, 0, 2.25, r=0.115)
        draw_state(ax, 0, 1.35, r=0.17)
        ax.text(0.24, 2.25, r"$S_t, A_t$", va="center", fontsize=12.5, color=BLUE, weight="bold")
        ax.text(0.26, 1.35, r"$S_{t+1}$", va="center", fontsize=13, color=NAVY, weight="bold")
        ax.text(-0.20, 1.80, r"$R_{t+1}$", ha="right", va="center", fontsize=12.5, color=AMBER, weight="bold")
        ax.text(0, -0.05, r"$\sum_a \pi(a \mid S_{t+1}) Q$", ha="center", va="center",
                fontsize=11.5, color=TEAL, weight="bold")


def fig_ch06_td_backups(out: Path, preview_dir: Path | None = None) -> None:
    """Figure 6.1: Upscaled 1x4 one-step TD backups (+ optional 2x2 comparison preview)."""
    # 1x4 compact, tall & legible
    fig, axes = plt.subplots(1, 4, figsize=(9.4, 3.6))
    for ax, kind in zip(axes, ("td0", "sarsa", "qlearn", "exp_sarsa")):
        _draw_ch06_panel(ax, kind)
    fig.tight_layout(w_pad=0.7)
    save(fig, out, "ch06-td-backups.png")

    if preview_dir is not None:
        # Also save copies of both 1x4 and 2x2 to preview_dir for visual comparison
        fig1, axes1 = plt.subplots(1, 4, figsize=(9.4, 3.6))
        for ax, kind in zip(axes1, ("td0", "sarsa", "qlearn", "exp_sarsa")):
            _draw_ch06_panel(ax, kind)
        fig1.tight_layout(w_pad=0.7)
        save(fig1, preview_dir, "fig61_1x4_preview.png")

        fig2, axes2 = plt.subplots(2, 2, figsize=(7.0, 6.2))
        for ax, kind in zip(axes2.flat, ("td0", "sarsa", "qlearn", "exp_sarsa")):
            _draw_ch06_panel(ax, kind)
        fig2.tight_layout(h_pad=1.6, w_pad=1.4)
        save(fig2, preview_dir, "fig61_2x2_preview.png")


# ---------------------------------------------------------------------------
# Chapter 7
# ---------------------------------------------------------------------------

def fig_ch07_nstep_spectrum(out: Path) -> None:
    """Figure 7.1: Full n-step TD return spectrum (1, 2, 3, ..., n-step, infinity/MC)."""
    fig, ax = plt.subplots(figsize=(9.6, 4.5))
    ax.set_xlim(-0.2, 11.4)
    ax.set_ylim(-0.75, 4.45)
    ax.axis("off")

    top_y = 3.45
    step_dy = 0.68

    # 1-step, 2-step, 3-step
    for x, label, depth in [(0.9, "1-step\n(TD(0))", 1), (2.8, "2-step", 2), (4.7, "3-step", 3)]:
        ax.text(x, 4.10, label, ha="center", va="center", fontsize=12.5, weight="bold", color=NAVY)
        for s in range(depth):
            y0, y1 = top_y - s * step_dy, top_y - (s + 1) * step_dy
            ax.plot([x, x], [y0, y1], color=BLUE, lw=2.0)
            draw_state(ax, x, y0, r=0.145)
            draw_action(ax, x, 0.5 * (y0 + y1), r=0.085)
        y_leaf = top_y - depth * step_dy
        draw_state(ax, x, y_leaf, r=0.145, fc=LIGHT_AMBER, ec=AMBER, lw=2.1)
        ax.text(x + 0.24, y_leaf, rf"$V(S_{{t+{depth}}})$", va="center", fontsize=11.0,
                color=AMBER, weight="bold")

    # Horizontal ellipsis between 3-step and n-step
    ax.text(6.15, 2.25, r"$\cdots$", ha="center", va="center", fontsize=22, color=SLATE)

    # n-step column (with vertical ellipsis down to V(S_{t+n}))
    xn = 7.45
    ax.text(xn, 4.10, r"$n$-step", ha="center", va="center", fontsize=12.5, weight="bold", color=NAVY)
    for s in range(2):
        y0, y1 = top_y - s * step_dy, top_y - (s + 1) * step_dy
        ax.plot([xn, xn], [y0, y1], color=BLUE, lw=2.0)
        draw_state(ax, xn, y0, r=0.145)
        draw_action(ax, xn, 0.5 * (y0 + y1), r=0.085)
    # 3rd state + action stub into vertical ellipsis
    y_s2 = top_y - 2 * step_dy
    draw_state(ax, xn, y_s2, r=0.145)
    ax.plot([xn, xn], [y_s2, y_s2 - 0.34], color=BLUE, lw=2.0)
    draw_action(ax, xn, y_s2 - 0.34, r=0.085)
    for dy in (y_s2 - 0.58, y_s2 - 0.76, y_s2 - 0.94):
        ax.add_patch(Circle((xn, dy), 0.036, fc=SLATE, ec="none"))
    y_nleaf = 0.55
    ax.plot([xn, xn], [y_nleaf + 0.38, y_nleaf], color=BLUE, lw=2.0)
    draw_action(ax, xn, y_nleaf + 0.38, r=0.085)
    draw_state(ax, xn, y_nleaf, r=0.145, fc=LIGHT_AMBER, ec=AMBER, lw=2.1)
    ax.text(xn + 0.24, y_nleaf, r"$V(S_{t+n})$", va="center", fontsize=11.0, color=AMBER, weight="bold")

    # infinity-step (Monte Carlo) column with vertical ellipsis down to terminal square S_T
    xm = 9.95
    ax.text(xm, 4.10, r"$\infty$-step" + "\n(Monte Carlo)", ha="center", va="center",
            fontsize=12.5, weight="bold", color=NAVY)
    for s in range(2):
        y0, y1 = top_y - s * step_dy, top_y - (s + 1) * step_dy
        ax.plot([xm, xm], [y0, y1], color=BLUE, lw=2.0)
        draw_state(ax, xm, y0, r=0.145)
        draw_action(ax, xm, 0.5 * (y0 + y1), r=0.085)
    draw_state(ax, xm, y_s2, r=0.145)
    ax.plot([xm, xm], [y_s2, y_s2 - 0.34], color=BLUE, lw=2.0)
    draw_action(ax, xm, y_s2 - 0.34, r=0.085)
    for dy in (y_s2 - 0.58, y_s2 - 0.76, y_s2 - 0.94):
        ax.add_patch(Circle((xm, dy), 0.036, fc=SLATE, ec="none"))
    y_term = 0.25
    ax.plot([xm, xm], [y_term + 0.42, y_term], color=BLUE, lw=2.0)
    draw_action(ax, xm, y_term + 0.42, r=0.085)
    draw_terminal(ax, xm, y_term, half=0.15)
    ax.text(xm + 0.25, y_term, r"$S_T$", va="center", fontsize=12.0, color=TEAL, weight="bold")

    # Bottom spectrum bar
    ax.annotate("", xy=(10.7, -0.30), xytext=(0.45, -0.30),
                arrowprops=dict(arrowstyle="<->,head_width=0.3,head_length=0.45", lw=1.8, color=SLATE))
    ax.text(0.45, -0.58, "Lower variance, higher bootstrapping bias", ha="left",
            fontsize=11.0, color=SLATE, style="italic")
    ax.text(10.7, -0.58, "Zero bias, higher sampling variance", ha="right",
            fontsize=11.0, color=SLATE, style="italic")

    save(fig, out, "ch07-nstep-spectrum.png")


def fig_ch07_nstep_sarsa(out: Path) -> None:
    """Figure 7.2: Backup diagrams for n-step Sarsa and n-step Expected Sarsa."""
    fig, ax = plt.subplots(figsize=(10.2, 4.7))
    ax.set_xlim(-0.2, 12.6)
    ax.set_ylim(-0.35, 4.75)
    ax.axis("off")

    top_y = 3.65
    step_dy = 0.72

    # 1-step, 2-step, 3-step Sarsa (action-anchored)
    for x, label, depth in [(0.9, "1-step\n(Sarsa(0))", 1), (2.7, "2-step", 2), (4.5, "3-step", 3)]:
        ax.text(x, 4.32, label, ha="center", va="center", fontsize=12.0, weight="bold", color=NAVY)
        for s in range(depth):
            y0, y1 = top_y - s * step_dy, top_y - (s + 1) * step_dy
            ax.plot([x, x], [y0, y1], color=BLUE, lw=2.0)
            draw_action(ax, x, y0, r=0.095)
            draw_state(ax, x, 0.5 * (y0 + y1), r=0.145)
        y_leaf = top_y - depth * step_dy
        draw_action(ax, x, y_leaf, r=0.105, fc=AMBER, ec=NAVY)

    ax.text(5.75, 2.35, r"$\cdots$", ha="center", va="center", fontsize=22, color=SLATE)

    # Helper for ellipsis chains (action-anchored)
    def draw_ellipsis_top(x):
        for s in range(2):
            y0, y1 = top_y - s * step_dy, top_y - (s + 1) * step_dy
            ax.plot([x, x], [y0, y1], color=BLUE, lw=2.0)
            draw_action(ax, x, y0, r=0.095)
            draw_state(ax, x, 0.5 * (y0 + y1), r=0.145)
        y2 = top_y - 2 * step_dy
        draw_action(ax, x, y2, r=0.095)
        for dy in (y2 - 0.30, y2 - 0.48, y2 - 0.66):
            ax.add_patch(Circle((x, dy), 0.036, fc=SLATE, ec="none"))
        return y2 - 0.94

    # 4. n-step Sarsa
    xn = 7.0
    ax.text(xn, 4.32, r"$n$-step" + "\nSarsa", ha="center", va="center", fontsize=12.0, weight="bold", color=NAVY)
    y_bot = draw_ellipsis_top(xn)
    ax.plot([xn, xn], [y_bot, y_bot - 0.72], color=BLUE, lw=2.0)
    draw_action(ax, xn, y_bot, r=0.095)
    draw_state(ax, xn, y_bot - 0.36, r=0.145)
    draw_action(ax, xn, y_bot - 0.72, r=0.105, fc=AMBER, ec=NAVY)
    ax.text(xn, y_bot - 1.05, r"$Q(S_{t+n}, A_{t+n})$", ha="center", va="center",
            fontsize=10.5, color=AMBER, weight="bold")

    # 5. infinity-step (MC)
    xm = 9.05
    ax.text(xm, 4.32, r"$\infty$-step" + "\n(Monte Carlo)", ha="center", va="center",
            fontsize=12.0, weight="bold", color=NAVY)
    y_bot = draw_ellipsis_top(xm)
    ax.plot([xm, xm], [y_bot, y_bot - 0.50], color=BLUE, lw=2.0)
    draw_action(ax, xm, y_bot, r=0.095)
    draw_terminal(ax, xm, y_bot - 0.50, half=0.15)
    ax.text(xm, y_bot - 0.88, r"$S_T$", ha="center", va="center", fontsize=11.5, color=TEAL, weight="bold")

    # 6. n-step Expected Sarsa
    xe = 11.75
    ax.text(xe, 4.32, r"$n$-step" + "\nExpected Sarsa", ha="center", va="center",
            fontsize=12.0, weight="bold", color=TEAL)
    y_bot = draw_ellipsis_top(xe)
    ax.plot([xe, xe], [y_bot, y_bot - 0.36], color=BLUE, lw=2.0)
    draw_action(ax, xe, y_bot, r=0.095)
    y_s = y_bot - 0.36
    for dx in (-0.52, 0.0, 0.52):
        ax.plot([xe, xe + dx], [y_s, y_s - 0.45], color=TEAL, lw=1.9)
        draw_action(ax, xe + dx, y_s - 0.45, r=0.095, fc=TEAL, ec=NAVY)
    draw_state(ax, xe, y_s, r=0.145)
    ax.text(xe, y_s - 0.78, r"$\bar{V}(S_{t+n})$", ha="center", va="center",
            fontsize=11.0, color=TEAL, weight="bold")

    save(fig, out, "ch07-nstep-sarsa.png")


def fig_ch07_nstep_unified(out: Path) -> None:
    """Figure 7.3: Unified 4-step off-policy & Q(sigma) backup taxonomy (5 aligned columns)."""
    fig, ax = plt.subplots(figsize=(11.6, 6.2))
    ax.set_xlim(-0.3, 15.2)
    ax.set_ylim(-0.35, 6.85)
    ax.axis("off")

    cols = [
        (1.2, "4-step\nTD"),
        (3.6, "4-step\nSarsa"),
        (7.1, "4-step\nTree Backup"),
        (10.8, "4-step\nExpected Sarsa"),
        (13.6, "4-step\n" + r"$Q(\sigma)$"),
    ]
    for cx, title in cols:
        ax.text(cx, 6.40, title, ha="center", va="center", fontsize=12.5, weight="bold", color=NAVY)

    ys = np.linspace(5.60, 0.40, 9)

    # --- Col 1: 4-step TD ---
    x = 1.2
    ax.plot([x, x], [ys[0], ys[8]], color=BLUE, lw=2.0)
    for k in range(4):
        draw_state(ax, x, ys[2 * k], r=0.15)
        draw_action(ax, x, ys[2 * k + 1], r=0.095)
        ax.text(x - 0.26, 0.5 * (ys[2 * k] + ys[2 * k + 1]), r"$\rho$", ha="right", va="center",
                fontsize=12.5, color=CORAL, weight="bold")
    draw_state(ax, x, ys[8], r=0.15, fc=LIGHT_AMBER, ec=AMBER, lw=2.1)

    # --- Col 2: 4-step Sarsa ---
    x = 3.6
    ax.plot([x, x], [ys[0], ys[8]], color=BLUE, lw=2.0)
    draw_action(ax, x, ys[0], r=0.095)
    for k in range(4):
        y_s = ys[2 * k + 1]
        y_a = ys[2 * k + 2]
        draw_state(ax, x, y_s, r=0.15)
        draw_action(ax, x, y_a, r=0.095, fc=(AMBER if k == 3 else BLUE))
        ax.text(x - 0.26, 0.5 * (y_s + y_a), r"$\rho$", ha="right", va="center",
                fontsize=12.5, color=CORAL, weight="bold")

    # --- Col 3: 4-step Tree Backup ---
    x = 7.1
    ax.plot([x, x], [ys[0], ys[8]], color=BLUE, lw=2.0)
    draw_action(ax, x, ys[0], r=0.095)
    ax.text(x + 0.22, ys[0] + 0.02, r"$S_t, A_t$", ha="left", va="center", fontsize=10.5, color=BLUE, weight="bold")
    for k in range(4):
        y_s = ys[2 * k + 1]
        y_a = ys[2 * k + 2]
        ax.text(x - 0.24, 0.5 * (ys[2 * k] + y_s), rf"$R_{{t+{k+1}}}$", ha="right", va="center",
                fontsize=10.0, color=AMBER, weight="bold")
        for dx in (-0.92, 0.92):
            ax.plot([x, x + dx], [y_s, y_a], color=TEAL, lw=1.7)
            draw_action(ax, x + dx, y_a, r=0.09, fc=TEAL, ec=NAVY)
        draw_state(ax, x, y_s, r=0.15)
        ax.text(x + 0.25, y_s + 0.09, rf"$S_{{t+{k+1}}}$", ha="left", va="center",
                fontsize=10.5, color=NAVY, weight="bold")
        draw_action(ax, x, y_a, r=0.095, fc=(TEAL if k == 3 else BLUE))
        if k < 3:
            ax.text(x + 0.16, y_a - 0.03, rf"$A_{{t+{k+1}}}$", ha="left", va="center",
                    fontsize=9.6, color=BLUE, weight="bold", zorder=7)
    ax.text(x, -0.08, "No importance sampling", ha="center", va="center",
            fontsize=10.0, color=TEAL, style="italic", weight="bold")

    # --- Col 4: 4-step Expected Sarsa ---
    x = 10.8
    ax.plot([x, x], [ys[0], ys[7]], color=BLUE, lw=2.0)
    draw_action(ax, x, ys[0], r=0.095)
    for k in range(3):
        y_s = ys[2 * k + 1]
        y_a = ys[2 * k + 2]
        draw_state(ax, x, y_s, r=0.15)
        draw_action(ax, x, y_a, r=0.095)
        ax.text(x - 0.26, 0.5 * (y_s + y_a), r"$\rho$", ha="right", va="center",
                fontsize=12.5, color=CORAL, weight="bold")
    y_s = ys[7]
    for dx in (-0.56, 0.0, 0.56):
        ax.plot([x, x + dx], [y_s, ys[8]], color=TEAL, lw=1.8)
        draw_action(ax, x + dx, ys[8], r=0.09, fc=TEAL, ec=NAVY)
    draw_state(ax, x, y_s, r=0.15)

    # --- Col 5: 4-step Q(sigma) ---
    x = 13.6
    ax.plot([x, x], [ys[0], ys[7]], color=BLUE, lw=2.0)
    draw_action(ax, x, ys[0], r=0.095)
    sigmas = [1, 0, 1, 0]
    for k, sig in enumerate(sigmas):
        y_s = ys[2 * k + 1]
        y_a = ys[2 * k + 2]
        if sig == 1:
            draw_state(ax, x, y_s, r=0.15)
            draw_action(ax, x, y_a, r=0.095)
            ax.text(x - 0.26, 0.5 * (y_s + y_a), r"$\rho$", ha="right", va="center",
                    fontsize=12.5, color=CORAL, weight="bold")
            ax.text(x + 0.28, y_s, r"$\sigma=1$", ha="left", va="center",
                    fontsize=11.0, color=CORAL, weight="bold")
        else:
            for dx in (-0.56, 0.56):
                ax.plot([x, x + dx], [y_s, y_a], color=TEAL, lw=1.8)
                draw_action(ax, x + dx, y_a, r=0.09, fc=TEAL, ec=NAVY)
            if k == 3:
                ax.plot([x, x], [y_s, y_a], color=TEAL, lw=1.8)
            draw_state(ax, x, y_s, r=0.15)
            draw_action(ax, x, y_a, r=0.095, fc=(TEAL if k == 3 else BLUE))
            ax.text(x + 0.28, y_s, r"$\sigma=0$", ha="left", va="center",
                    fontsize=11.0, color=TEAL, weight="bold")

    save(fig, out, "ch07-nstep-unified.png")


# ---------------------------------------------------------------------------
# Chapter 8
# ---------------------------------------------------------------------------

def fig_ch08_dyna_unified(out: Path) -> None:
    """Figure 8.1: Accurate Dyna architecture (with Environment & Search Control) + 2D RL update space."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.9), gridspec_kw={"width_ratios": [1.18, 1.0]})

    # --- Left: Accurate Dyna Architecture ---
    ax1.set_xlim(-0.2, 11.2)
    ax1.set_ylim(-0.2, 7.2)
    ax1.axis("off")
    ax1.set_title("General Dyna Architecture", fontsize=13.5, weight="bold", color=NAVY, pad=10)

    # Boxes: Policy/Value (top-left/center), Environment (bottom-left), Real Experience (mid-left pill),
    # Learned Model (bottom-right), Simulated Experience (mid-right pill)
    def box(x, y, w, h, txt, fc, ec, fs=11.0):
        ax1.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12", fc=fc, ec=ec, lw=2.0, zorder=4))
        ax1.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, weight="bold", color=ec, zorder=5)

    def pill(x, y, w, h, txt, fc, ec, fs=10.5):
        ax1.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.16,rounding_size=0.45",
                                     fc=fc, ec=ec, lw=1.8, zorder=4))
        ax1.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, weight="bold", color=ec, zorder=5)

    box(1.8, 5.75, 5.0, 1.0, "Policy / Value Functions\n" + r"$(\pi,\; Q)$", LIGHT_BLUE, NAVY, fs=10.8)
    box(1.5, 0.25, 3.2, 0.95, "Environment", LIGHT_TEAL, TEAL, fs=12.0)
    pill(1.65, 3.05, 2.9, 0.90, "Real\nExperience", LIGHT_TEAL, TEAL, fs=10.8)
    box(7.35, 0.25, 3.2, 1.05, "Learned Model\n" + r"$(S, A \to R, S')$", LIGHT_AMBER, AMBER, fs=10.8)
    pill(7.50, 3.55, 2.9, 0.90, "Simulated\nExperience", LIGHT_SLATE, SLATE, fs=10.8)

    # Thick bidirectional channel: Policy/Value <-> Environment (through Real Experience)
    ax1.annotate("", xy=(3.10, 5.62), xytext=(3.10, 4.12),
                 arrowprops=dict(arrowstyle="<->,head_width=0.35,head_length=0.4", lw=3.0, color="#93c5fd"),
                 zorder=2)
    ax1.annotate("", xy=(3.10, 2.88), xytext=(3.10, 1.35),
                 arrowprops=dict(arrowstyle="<->,head_width=0.35,head_length=0.4", lw=3.0, color="#93c5fd"),
                 zorder=2)
    ax1.text(2.80, 2.15, "Acting &\nobserving", ha="right", va="center", fontsize=9.8, color=TEAL, style="italic")

    # Direct RL: Real Experience -> Policy/Value (clean outer-left curve, zero collision)
    ax1.annotate("", xy=(1.85, 5.62), xytext=(1.50, 3.50),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45",
                                 connectionstyle="arc3,rad=-0.42", lw=2.0, color=BLUE),
                 zorder=5)
    ax1.text(0.28, 4.90, "Direct RL\nupdate", ha="center", va="center", fontsize=10.5,
             color=BLUE, weight="bold")

    # Model learning: Real Experience -> Learned Model
    ax1.annotate("", xy=(7.22, 0.90), xytext=(4.68, 3.15),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45", lw=2.0, color=AMBER),
                 zorder=5)
    ax1.text(6.65, 2.48, "Model\nlearning", ha="center", va="center", fontsize=10.5,
             color=AMBER, weight="bold", zorder=6)

    # Search control: Learned Model -> Simulated Experience
    ax1.annotate("", xy=(8.95, 3.38), xytext=(8.95, 1.44),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45", lw=2.0, color=SLATE),
                 zorder=5)
    ax1.text(9.22, 2.40, "Search\ncontrol", ha="left", va="center", fontsize=10.8,
             color=SLATE, weight="bold")

    # Planning update: Simulated Experience -> Policy/Value
    ax1.annotate("", xy=(6.95, 6.00), xytext=(8.55, 4.62),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45",
                                 connectionstyle="arc3,rad=0.18", lw=2.0, color=CORAL),
                 zorder=5)
    ax1.text(9.18, 5.75, "Planning\nupdate", ha="center", va="center", fontsize=10.5,
             color=CORAL, weight="bold")

    # --- Right: Two Dimensions of RL Updates (generously spaced) ---
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_xticks([1.2, 8.8])
    ax2.set_xticklabels(["Sample\nupdates", "Expected\nupdates"], fontsize=11.0, color=NAVY)
    ax2.set_yticks([1.2, 8.8])
    ax2.set_yticklabels(["Shallow\n(1-step)", "Deep\n(full episode)"], fontsize=11.0, color=NAVY)
    ax2.set_xlabel("Backup width", fontsize=11.5, weight="bold", color=SLATE, labelpad=6)
    ax2.set_ylabel("Backup depth", fontsize=11.5, weight="bold", color=SLATE, labelpad=6)
    ax2.set_title("Two Dimensions of RL Updates", fontsize=13.5, weight="bold", color=NAVY, pad=10)
    ax2.grid(True, ls=":", alpha=0.55)

    pts = [
        (1.3, 1.3, "TD(0) / Sarsa /\nQ-learning", BLUE, (0.38, 0.0), "left"),
        (8.7, 1.3, "Dynamic\nProgramming", TEAL, (-0.38, 0.0), "right"),
        (1.3, 8.7, "Monte Carlo", AMBER, (0.38, 0.0), "left"),
        (8.7, 8.7, "Exhaustive\nSearch", CORAL, (-0.38, 0.0), "right"),
        (1.3, 5.0, "n-step TD /\nTD(λ)", NAVY, (0.38, 0.0), "left"),
        (5.6, 5.0, "n-step Q(σ) /\nTree Backup", SLATE, (0.0, 0.85), "center"),
    ]
    for cx, cy, lbl, col, (dx, dy), ha in pts:
        ax2.scatter([cx], [cy], s=85, color=col, zorder=5)
        ax2.text(cx + dx, cy + dy, lbl, ha=ha, va="center", fontsize=10.5, weight="bold", color=col)

    fig.tight_layout(w_pad=2.2)
    save(fig, out, "ch08-dyna-unified.png")


def fig_ch08_onestep_matrix(out: Path) -> None:
    """Figure 8.2: 4x2 comparison matrix of one-step Expected (DP) vs Sample (TD) updates."""
    fig, ax = plt.subplots(figsize=(9.6, 7.6))
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 9.2)
    ax.axis("off")

    x_c0, x_c1, x_c2 = 1.25, 4.55, 8.25
    ax.text(x_c0, 8.70, "Value\nestimated", ha="center", va="center", fontsize=12.5, weight="bold", color=NAVY)
    ax.text(x_c1, 8.70, "Expected Updates\n(Dynamic Programming)", ha="center", va="center",
            fontsize=12.5, weight="bold", color=TEAL)
    ax.text(x_c2, 8.70, "Sample Updates\n(One-Step TD)", ha="center", va="center",
            fontsize=12.5, weight="bold", color=BLUE)

    ax.plot([0.2, 9.8], [8.15, 8.15], color=NAVY, lw=1.8)
    for y in (6.15, 4.15, 2.15):
        ax.plot([0.2, 9.8], [y, y], color="#cbd5e1", lw=1.2)
    ax.plot([2.35, 2.35], [0.25, 9.0], color="#cbd5e1", lw=1.2)
    ax.plot([6.65, 6.65], [0.25, 9.0], color="#cbd5e1", lw=1.2)

    row_ys = [7.15, 5.15, 3.15, 1.15]
    row_labels = [r"$v_\pi(s)$", r"$v_*(s)$", r"$q_\pi(s, a)$", r"$q_*(s, a)$"]
    for ry, rl in zip(row_ys, row_labels):
        ax.text(x_c0, ry, rl, ha="center", va="center", fontsize=14.5, weight="bold", color=NAVY)

    def draw_dp_state_tree(cx, cy, with_max: bool, caption: str):
        y_top, y_mid, y_bot = cy + 0.65, cy + 0.12, cy - 0.42
        xs_a = [cx - 0.95, cx, cx + 0.95]
        for xa in xs_a:
            ax.plot([cx, xa], [y_top, y_mid], color=SLATE, lw=1.6)
            for dx in (-0.30, 0.30):
                ax.plot([xa, xa + dx], [y_mid, y_bot], color=TEAL, lw=1.4)
                draw_state(ax, xa + dx, y_bot, r=0.11)
            draw_action(ax, xa, y_mid, r=0.085)
        draw_state(ax, cx, y_top, r=0.13)
        if with_max:
            ax.add_patch(patches.Arc((cx, y_top), 0.78, 0.56, theta1=205, theta2=335, color=CORAL, lw=2.1, zorder=6))
            ax.text(cx - 0.55, y_top - 0.10, r"$\max$", ha="right", va="center",
                    fontsize=10.5, color=CORAL, weight="bold")
        else:
            ax.text(cx + 0.58, y_top - 0.08, r"$\pi$", fontsize=11.0, color=BLUE,
                    weight="bold", path_effects=HALO, zorder=7)
        ax.text(cx, cy - 0.78, caption, ha="center", va="center", fontsize=11.0, color=DARK, weight="bold")

    def draw_dp_action_tree(cx, cy, with_max: bool, caption: str):
        y_top, y_mid, y_bot = cy + 0.65, cy + 0.12, cy - 0.42
        xs_s = [cx - 0.65, cx + 0.65]
        for xs in xs_s:
            ax.plot([cx, xs], [y_top, y_mid], color=SLATE, lw=1.6)
            for dx in (-0.36, 0.36):
                ax.plot([xs, xs + dx], [y_mid, y_bot], color=TEAL, lw=1.4)
                draw_action(ax, xs + dx, y_bot, r=0.085)
            if with_max:
                ax.add_patch(patches.Arc((xs, y_mid), 0.52, 0.45, theta1=210, theta2=330, color=CORAL, lw=2.0, zorder=6))
            draw_state(ax, xs, y_mid, r=0.12)
        draw_action(ax, cx, y_top, r=0.095)
        if with_max:
            ax.text(cx - 1.05, y_mid - 0.15, r"$\max$", ha="right", va="center",
                    fontsize=10.5, color=CORAL, weight="bold")
        else:
            ax.text(cx + 0.95, y_mid - 0.20, r"$\pi$", ha="left", va="center",
                    fontsize=10.5, color=BLUE, weight="bold")
        ax.text(cx, cy - 0.78, caption, ha="center", va="center", fontsize=11.0, color=DARK, weight="bold")

    # Row 1: Policy Evaluation | TD(0)
    draw_dp_state_tree(x_c1, row_ys[0], False, "Policy evaluation")
    cx, cy = x_c2, row_ys[0]
    ax.plot([cx, cx], [cy + 0.65, cy - 0.42], color=BLUE, lw=2.0)
    draw_state(ax, cx, cy + 0.65, r=0.13)
    draw_action(ax, cx, cy + 0.12, r=0.09)
    draw_state(ax, cx, cy - 0.42, r=0.13, fc=LIGHT_AMBER, ec=AMBER)
    ax.text(cx + 0.22, cy + 0.65, r"$S$", va="center", fontsize=11.0, color=NAVY)
    ax.text(cx + 0.20, cy + 0.12, r"$A$", va="center", fontsize=11.0, color=BLUE)
    ax.text(cx - 0.20, cy - 0.15, r"$R$", ha="right", va="center", fontsize=10.5, color=AMBER)
    ax.text(cx + 0.22, cy - 0.42, r"$S'$", va="center", fontsize=11.0, color=AMBER)
    ax.text(cx, cy - 0.78, "TD(0)", ha="center", va="center", fontsize=11.0, color=DARK, weight="bold")

    # Row 2: Value Iteration | (no model-free sample analogue for v*)
    draw_dp_state_tree(x_c1, row_ys[1], True, "Value iteration")
    ax.text(x_c2, row_ys[1], "—\n(requires model\nfor max over " + r"$a$)", ha="center", va="center",
            fontsize=10.5, color=SLATE, style="italic")

    # Row 3: q-policy evaluation | Sarsa
    draw_dp_action_tree(x_c1, row_ys[2], False, r"$q$-policy evaluation")
    cx, cy = x_c2, row_ys[2]
    ax.plot([cx, cx], [cy + 0.65, cy - 0.42], color=BLUE, lw=2.0)
    draw_action(ax, cx, cy + 0.65, r=0.095)
    draw_state(ax, cx, cy + 0.12, r=0.13)
    draw_action(ax, cx, cy - 0.42, r=0.095, fc=AMBER)
    ax.text(cx + 0.20, cy + 0.65, r"$S, A$", va="center", fontsize=11.0, color=BLUE)
    ax.text(cx - 0.20, cy + 0.38, r"$R$", ha="right", va="center", fontsize=10.5, color=AMBER)
    ax.text(cx + 0.22, cy + 0.12, r"$S'$", va="center", fontsize=11.0, color=NAVY)
    ax.text(cx + 0.20, cy - 0.42, r"$A'$", va="center", fontsize=11.0, color=AMBER)
    ax.text(cx, cy - 0.78, "Sarsa", ha="center", va="center", fontsize=11.0, color=DARK, weight="bold")

    # Row 4: q-value iteration | Q-learning
    draw_dp_action_tree(x_c1, row_ys[3], True, r"$q$-value iteration")
    cx, cy = x_c2, row_ys[3]
    ax.plot([cx, cx], [cy + 0.65, cy + 0.12], color=BLUE, lw=2.0)
    for dx in (-0.52, 0.0, 0.52):
        ax.plot([cx, cx + dx], [cy + 0.12, cy - 0.42], color=SLATE, lw=1.7)
        draw_action(ax, cx + dx, cy - 0.42, r=0.09)
    ax.add_patch(patches.Arc((cx, cy + 0.12), 0.60, 0.52, theta1=210, theta2=330, color=CORAL, lw=2.1, zorder=6))
    draw_action(ax, cx, cy + 0.65, r=0.095)
    draw_state(ax, cx, cy + 0.12, r=0.13)
    ax.text(cx + 0.20, cy + 0.65, r"$S, A$", va="center", fontsize=11.0, color=BLUE)
    ax.text(cx - 0.20, cy + 0.38, r"$R$", ha="right", va="center", fontsize=10.5, color=AMBER)
    ax.text(cx + 0.22, cy + 0.12, r"$S'$", va="center", fontsize=11.0, color=NAVY)
    ax.text(cx - 0.45, cy - 0.08, r"$\max$", ha="right", va="center", fontsize=10.5, color=CORAL, weight="bold")
    ax.text(cx, cy - 0.78, "Q-learning", ha="center", va="center", fontsize=11.0, color=DARK, weight="bold")

    save(fig, out, "ch08-onestep-matrix.png")


def fig_ch08_rtdp_states(out: Path) -> None:
    """Figure 8.3: RTDP state-space reachability (Start ⊂ Relevant ⊂ Irrelevant states)."""
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 4.8)
    ax.axis("off")

    e_outer = Ellipse((3.55, 2.75), 6.2, 3.2, fc=LIGHT_SLATE, ec=SLATE, lw=2.0)
    e_rel = Ellipse((2.65, 2.75), 3.6, 1.95, fc=LIGHT_BLUE, ec=BLUE, lw=2.1)
    e_start = Ellipse((1.75, 2.75), 1.35, 0.85, fc=LIGHT_TEAL, ec=TEAL, lw=2.2)
    for e in (e_outer, e_rel, e_start):
        ax.add_patch(e)

    ax.annotate("Irrelevant states\n(unreachable from any start state\nunder any optimal policy)",
                xy=(5.75, 3.30), xytext=(6.85, 3.65),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=1.7, color=SLATE),
                ha="left", va="center", fontsize=11.0, color=SLATE, weight="bold")

    ax.annotate("Relevant states\n(reachable from some start state\nunder some optimal policy)",
                xy=(3.55, 2.00), xytext=(5.50, 0.85),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=1.7, color=BLUE),
                ha="left", va="center", fontsize=11.0, color=BLUE, weight="bold")

    ax.annotate("Start\nstates",
                xy=(1.75, 2.40), xytext=(1.25, 0.85),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=1.7, color=TEAL),
                ha="center", va="center", fontsize=11.5, color=TEAL, weight="bold")

    save(fig, out, "ch08-rtdp-states.png")


def fig_ch08_heuristic_search(out: Path) -> None:
    """Figure 8.4: Heuristic search — selective lookahead tree with bottom-up backup ordering."""
    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.2, 5.6)
    ax.axis("off")

    root = (5.0, 5.1)
    aL, aR = (2.3, 4.15), (7.7, 4.15)
    ax.plot([root[0], aL[0]], [root[1], aL[1]], color=NAVY, lw=2.0)
    ax.plot([root[0], aR[0]], [root[1], aR[1]], color=NAVY, lw=2.0)

    def draw_mini_backup(x, y, label_num: str, dx_s=0.65, dx_a=0.32, lbl_dx=0.0):
        s1, s2 = (x - dx_s, y - 0.48), (x + dx_s, y - 0.48)
        leaves = []
        for sx, sy in (s1, s2):
            ax.plot([x, sx], [y, sy], color=SLATE, lw=1.5)
            for d in (-dx_a, dx_a):
                lx, ly = sx + d, sy - 0.48
                ax.plot([sx, lx], [sy, ly], color=SLATE, lw=1.4)
                leaves.append((lx, ly))
            ax.add_patch(patches.Arc((sx, sy), 0.36, 0.34, theta1=215, theta2=325, color=CORAL, lw=1.6, zorder=6))
            draw_state(ax, sx, sy, r=0.11)
        for lx, ly in leaves:
            draw_action(ax, lx, ly, r=0.075)
        draw_action(ax, x, y, r=0.085)

        poly = Polygon([
            (x, y + 0.24),
            (x - dx_s - dx_a - 0.22, y - 1.12),
            (x + dx_s + dx_a + 0.22, y - 1.12),
        ], closed=True, fc=LIGHT_BLUE, ec=BLUE, lw=1.3, ls="--", alpha=0.32, zorder=1)
        ax.add_patch(poly)
        ax.text(x + lbl_dx, y - 1.28, label_num, ha="center", va="top", fontsize=11.0,
                color=BLUE, weight="bold")
        return leaves

    l_leaves = draw_mini_backup(aL[0], aL[1], "3", dx_s=0.72, dx_a=0.34)
    draw_mini_backup(l_leaves[0][0], l_leaves[0][1], "1", dx_s=0.52, dx_a=0.25)
    draw_mini_backup(l_leaves[3][0], l_leaves[3][1], "2", dx_s=0.52, dx_a=0.25)

    r_leaves = draw_mini_backup(aR[0], aR[1], "9", dx_s=1.25, dx_a=0.45)
    r_left = draw_mini_backup(r_leaves[0][0], r_leaves[0][1], "6", dx_s=0.68, dx_a=0.30)
    draw_mini_backup(r_left[0][0], r_left[0][1], "4", dx_s=0.46, dx_a=0.22)
    draw_mini_backup(r_left[3][0], r_left[3][1], "5", dx_s=0.46, dx_a=0.22)
    r_right = draw_mini_backup(r_leaves[3][0], r_leaves[3][1], "8", dx_s=0.62, dx_a=0.28, lbl_dx=-0.52)
    draw_mini_backup(r_right[2][0], r_right[2][1], "7", dx_s=0.46, dx_a=0.22)

    draw_state(ax, root[0], root[1], r=0.17, fc=LIGHT_AMBER, ec=AMBER, lw=2.2)
    ax.text(root[0], root[1] + 0.30, r"Current state $S_t$", ha="center", va="bottom",
            fontsize=12.5, weight="bold", color=NAVY)
    ax.text(5.5, 0.05, "Dashed regions show bottom-up backup order (1 → 9) from leaf evaluations back to root actions",
            ha="center", va="center", fontsize=10.5, color=SLATE, style="italic")

    save(fig, out, "ch08-heuristic-search.png")


def fig_ch08_mcts_cycle(out: Path) -> None:
    """Figure 8.5: Four-stage MCTS cycle (Selection -> Expansion -> Simulation -> Backup)."""
    fig, ax = plt.subplots(figsize=(11.4, 4.9))
    ax.set_xlim(-0.3, 14.5)
    ax.set_ylim(-0.3, 5.6)
    ax.axis("off")

    xs = [1.7, 5.25, 8.85, 12.45]
    stages = ["1. Selection", "2. Expansion", "3. Simulation", "4. Backup"]
    colors = [BLUE, TEAL, AMBER, CORAL]

    ax.plot([1.7, 1.7, 12.45, 12.45], [4.65, 5.25, 5.25, 4.65], color=SLATE, lw=1.7)
    ax.annotate("", xy=(1.7, 4.62), xytext=(1.7, 4.85),
                arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=1.7, color=SLATE))
    ax.text(7.08, 5.25, "  Repeat while compute budget remains  ", ha="center", va="center",
            fontsize=11.5, weight="bold", color=NAVY,
            bbox=dict(boxstyle="round,pad=0.25", fc=LIGHT_SLATE, ec=SLATE, lw=1.3))

    for i, (cx, st, col) in enumerate(zip(xs, stages, colors)):
        ax.text(cx, 4.35, st, ha="center", va="center", fontsize=12.5, weight="bold", color=col)
        if i < 3:
            ax.annotate("", xy=(xs[i + 1] - 1.24, 4.35), xytext=(cx + 1.24, 4.35),
                        arrowprops=dict(arrowstyle="-|>,head_width=0.26,head_length=0.36", lw=1.8, color=SLATE))

    # Shared compact search tree geometry relative to panel center cx
    def tree_nodes(cx):
        return {
            "r": (cx, 3.65),
            "a1": (cx - 0.65, 2.95),
            "a2": (cx + 0.65, 2.95),
            "s1": (cx - 0.95, 2.25),
            "s2": (cx - 0.25, 2.25),
            "s3": (cx + 0.65, 2.25),
            "l1": (cx - 1.18, 1.55),
            "l2": (cx - 0.55, 1.55),
            "new": (cx - 0.55, 0.88),
        }

    base_edges = [("r", "a1"), ("r", "a2"), ("a1", "s1"), ("a1", "s2"), ("a2", "s3"), ("s1", "l1"), ("s1", "l2")]
    selected_edges = [("r", "a1"), ("a1", "s1"), ("s1", "l2")]

    for idx, cx in enumerate(xs):
        n = tree_nodes(cx)
        # Base tree edges
        for u, v in base_edges:
            ax.plot([n[u][0], n[v][0]], [n[u][1], n[v][1]], color="#94a3b8", lw=1.5, zorder=2)

        # Stage-specific overlays
        if idx == 0:
            # Selection: highlight UCT path down to expandable leaf l2
            for u, v in selected_edges:
                ax.annotate("", xy=n[v], xytext=n[u],
                            arrowprops=dict(arrowstyle="-|>,head_width=0.26,head_length=0.36",
                                            lw=2.3, color=BLUE, shrinkA=6, shrinkB=7), zorder=4)
            ax.text(cx, 0.35, "Tree policy (UCT)\ntraverses to leaf", ha="center", va="center",
                    fontsize=10.0, color=BLUE, style="italic")

        elif idx == 1:
            # Expansion: add new child node below l2
            ax.annotate("", xy=n["new"], xytext=n["l2"],
                        arrowprops=dict(arrowstyle="-|>,head_width=0.26,head_length=0.36",
                                        lw=2.3, color=TEAL, shrinkA=6, shrinkB=7), zorder=4)
            draw_state(ax, *n["new"], r=0.14, fc=LIGHT_TEAL, ec=TEAL, lw=2.2, zorder=6)
            ax.text(cx, 0.22, "Add child node\nfrom untried action", ha="center", va="center",
                    fontsize=10.0, color=TEAL, style="italic")

        elif idx == 2:
            # Simulation: include expanded node + dashed rollout to terminal triangle
            ax.plot([n["l2"][0], n["new"][0]], [n["l2"][1], n["new"][1]], color="#94a3b8", lw=1.6, zorder=2)
            draw_state(ax, *n["new"], r=0.13, fc=LIGHT_AMBER, ec=AMBER, lw=2.0, zorder=6)
            term = (n["new"][0] + 0.35, 0.12)
            ax.annotate("", xy=(term[0], term[1] + 0.16), xytext=(n["new"][0], n["new"][1] - 0.13),
                        arrowprops=dict(arrowstyle="-|>,head_width=0.26,head_length=0.36",
                                        lw=2.1, ls="--", color=AMBER), zorder=4)
            tri = Polygon([(term[0], term[1] + 0.14), (term[0] - 0.16, term[1] - 0.14),
                           (term[0] + 0.16, term[1] - 0.14)], fc=AMBER, ec=NAVY, lw=1.4, zorder=6)
            ax.add_patch(tri)
            ax.text(n["new"][0] + 0.88, 0.48, "Rollout\npolicy", ha="left", va="center",
                    fontsize=10.0, color=AMBER, weight="bold")

        elif idx == 3:
            # Backup: upward curved return arrows from terminal back to root
            ax.plot([n["l2"][0], n["new"][0]], [n["l2"][1], n["new"][1]], color="#94a3b8", lw=1.6, zorder=2)
            draw_state(ax, *n["new"], r=0.13, fc=LIGHT_CORAL, ec=CORAL, lw=2.0, zorder=6)
            term = (n["new"][0] + 0.35, 0.12)
            tri = Polygon([(term[0], term[1] + 0.14), (term[0] - 0.16, term[1] - 0.14),
                           (term[0] + 0.16, term[1] - 0.14)], fc=AMBER, ec=NAVY, lw=1.4, zorder=6)
            ax.add_patch(tri)
            up_pairs = [(term, n["new"]), (n["new"], n["l2"]), (n["l2"], n["s1"]), (n["s1"], n["a1"]), (n["a1"], n["r"])]
            for u, v in up_pairs:
                ax.annotate("", xy=v, xytext=u,
                            arrowprops=dict(arrowstyle="-|>,head_width=0.24,head_length=0.34",
                                            connectionstyle="arc3,rad=0.25", lw=2.0, color=CORAL,
                                            shrinkA=7, shrinkB=7), zorder=7)
            ax.text(cx + 0.62, 0.65, "Update\n" + r"$N, W$", ha="left", va="center",
                    fontsize=10.5, color=CORAL, weight="bold")

        # Draw base tree nodes on top
        for k in ("r", "s1", "s2", "s3"):
            draw_state(ax, *n[k], r=0.13, zorder=5)
        for k in ("a1", "a2", "l1", "l2"):
            fc = CORAL if (idx == 0 and k == "l2") else BLUE
            draw_action(ax, *n[k], r=0.085, fc=fc, zorder=5)

    save(fig, out, "ch08-mcts-cycle.png")


# ---------------------------------------------------------------------------
# Chapter 9
# ---------------------------------------------------------------------------

def fig_ch09_coarse_rbf(out: Path) -> None:
    """Figure 9.1: 2D coarse coding (high-contrast s, s') & 1D Gaussian RBFs (clear query activations)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.4), gridspec_kw={"width_ratios": [1.0, 1.28]})

    # --- Left: 2D overlapping circular receptive fields ---
    rng = np.random.default_rng(7)
    centers = rng.uniform(0.20, 0.80, size=(13, 2))
    s1 = np.array([0.41, 0.47])
    s2 = np.array([0.61, 0.56])
    centers[0] = np.array([0.51, 0.52])
    r = 0.165
    for cx, cy in centers:
        in_s1 = np.hypot(s1[0] - cx, s1[1] - cy) <= r
        in_s2 = np.hypot(s2[0] - cx, s2[1] - cy) <= r
        if in_s1 and in_s2:
            fc, ec, alpha, lw = LIGHT_AMBER, AMBER, 0.65, 2.3
        elif in_s1 or in_s2:
            fc, ec, alpha, lw = LIGHT_BLUE, BLUE, 0.42, 1.5
        else:
            fc, ec, alpha, lw = "none", SLATE, 0.35, 1.0
        ax1.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=lw, alpha=alpha))

    ax1.scatter([s1[0], s2[0]], [s1[1], s2[1]], color=CORAL, s=85, edgecolors="white", lw=1.2, zorder=7)
    ax1.text(s1[0] - 0.055, s1[1] - 0.065, r"$s$", fontsize=14.5, weight="bold", color=DARK,
             ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=CORAL, lw=1.1, alpha=0.95), zorder=8)
    ax1.text(s2[0] + 0.055, s2[1] + 0.055, r"$s'$", fontsize=14.5, weight="bold", color=DARK,
             ha="left", va="bottom",
             bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=CORAL, lw=1.1, alpha=0.95), zorder=8)
    ax1.set_xlim(0.0, 1.0)
    ax1.set_ylim(-0.08, 1.02)
    ax1.set_aspect("equal")
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title("2D Coarse Coding (Shared Receptive Fields)", fontsize=12.5, weight="bold", color=NAVY, pad=10)

    # Compact color key at bottom of left panel
    legend_handles = [
        patches.Patch(fc=LIGHT_AMBER, ec=AMBER, lw=1.6, label="Shared"),
        patches.Patch(fc=LIGHT_BLUE, ec=BLUE, lw=1.3, label="Single state"),
        patches.Patch(fc="white", ec=SLATE, lw=1.0, label="Inactive"),
    ]
    ax1.legend(handles=legend_handles, loc="lower center", ncol=3, frameon=True,
               facecolor="white", edgecolor="#cbd5e1", fontsize=9.5, handlelength=1.1, columnspacing=0.9)

    # --- Right: 1D Gaussian RBFs with clear query-state activations ---
    x = np.linspace(0, 10, 400)
    mus = [1.5, 3.5, 5.5, 7.5, 9.0]
    sigma = 1.05
    palette = [NAVY, BLUE, TEAL, AMBER, CORAL]
    s_q = 4.65
    activations = []
    for idx, (mu, col) in enumerate(zip(mus, palette), 1):
        y = np.exp(-0.5 * ((x - mu) / sigma) ** 2)
        ax2.plot(x, y, color=col, lw=2.2, label=rf"$x_{idx}(s)$")
        ax2.fill_between(x, 0, y, color=col, alpha=0.09)
        act = float(np.exp(-0.5 * ((s_q - mu) / sigma) ** 2))
        activations.append((idx, act, col))

    ax2.axvline(s_q, color=DARK, ls="--", lw=1.5, zorder=4)
    ax2.text(s_q, 1.09, r"Query state $s$", ha="center", va="bottom", fontsize=11.5,
             weight="bold", color=DARK,
             bbox=dict(boxstyle="round,pad=0.2", fc=LIGHT_SLATE, ec=SLATE, lw=1.0), zorder=7)

    # Mark intersection dots on the active Gaussians and annotate the top two
    for idx, act, col in activations:
        if act > 0.05:
            ax2.scatter([s_q], [act], color=col, s=75, edgecolors="white", lw=1.3, zorder=8)
    # Annotate top two activations cleanly to the left/right
    act_sorted = sorted(activations, key=lambda t: t[1], reverse=True)
    i1, a1, c1 = act_sorted[0]
    i2, a2, c2 = act_sorted[1]
    ax2.annotate(rf"$x_{i1}(s)={a1:.2f}$", xy=(s_q, a1), xytext=(s_q + 0.95, a1 + 0.08),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.3", lw=1.3, color=c1),
                 fontsize=10.5, weight="bold", color=c1, bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=c1, lw=0.9),
                 zorder=9)
    ax2.annotate(rf"$x_{i2}(s)={a2:.2f}$", xy=(s_q, a2), xytext=(s_q - 2.35, a2 - 0.14),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.3", lw=1.3, color=c2),
                 fontsize=10.5, weight="bold", color=c2, bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=c2, lw=0.9),
                 zorder=9)

    ax2.set_xlabel("1D State Space", fontsize=11.5, color=SLATE, weight="bold")
    ax2.set_ylabel("Feature Activation", fontsize=11.5, color=SLATE, weight="bold")
    ax2.tick_params(labelsize=10.5)
    ax2.set_ylim(0, 1.24)
    ax2.set_title("1D Gaussian Radial Basis Functions", fontsize=12.5, weight="bold", color=NAVY, pad=10)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.tight_layout(w_pad=2.0)
    save(fig, out, "ch09-coarse-rbf.png")


def fig_ch09_ann_architecture(out: Path) -> None:
    """Figure 9.2: Generic feedforward ANN for RL value approximation (3 -> 5 -> 4 -> 1)."""
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.35, 5.55)
    ax.axis("off")

    layer_xs = [1.4, 4.0, 6.6, 9.0]
    layer_sizes = [3, 5, 4, 1]
    layer_colors = [(LIGHT_BLUE, BLUE), (LIGHT_TEAL, TEAL), (LIGHT_TEAL, TEAL), (LIGHT_AMBER, AMBER)]
    layer_titles = [
        "Input Layer\n" + r"$\mathbf{x}(s)$",
        "Hidden Layer 1\n" + r"($\sigma$ activation)",
        "Hidden Layer 2\n" + r"($\sigma$ activation)",
        "Output Layer\n" + r"$\hat{v}(s, \mathbf{w})$",
    ]

    coords = []
    for x, n, title in zip(layer_xs, layer_sizes, layer_titles):
        ys = np.linspace(2.45 - 0.42 * (n - 1), 2.45 + 0.42 * (n - 1), n) if n > 1 else [2.45]
        coords.append([(x, y) for y in ys])
        ax.text(x, 5.00, title, ha="center", va="center", fontsize=11.5, weight="bold", color=NAVY)

    # Fully connected edges
    for l_idx in range(len(coords) - 1):
        for (x1, y1) in coords[l_idx]:
            for (x2, y2) in coords[l_idx + 1]:
                ax.plot([x1, x2], [y1, y2], color="#94a3b8", lw=1.0, alpha=0.65, zorder=2)

    # Nodes
    for l_idx, (pts, (fc, ec)) in enumerate(zip(coords, layer_colors)):
        for i, (x, y) in enumerate(pts):
            ax.add_patch(Circle((x, y), 0.25, fc=fc, ec=ec, lw=2.1, zorder=5))
            if l_idx == 0:
                ax.text(x - 0.45, y, rf"$x_{len(pts)-i}(s)$", ha="right", va="center",
                        fontsize=11.5, color=BLUE, weight="bold")
            elif l_idx == 3:
                ax.text(x + 0.42, y, r"$\hat{v}(s, \mathbf{w})$", ha="left", va="center",
                        fontsize=12.5, color=AMBER, weight="bold")

    # Weight matrix labels between layers
    for i, wlbl in enumerate([r"$\mathbf{W}^{(1)}$", r"$\mathbf{W}^{(2)}$", r"$\mathbf{W}^{(3)}$"]):
        mx = 0.5 * (layer_xs[i] + layer_xs[i + 1])
        ax.text(mx, 0.58, wlbl, ha="center", va="center", fontsize=11.5, color=SLATE, weight="bold")

    # Forward & Backprop indicator arrows along the bottom
    ax.annotate("", xy=(8.9, 0.08), xytext=(1.5, 0.08),
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.4", lw=1.8, color=BLUE))
    ax.text(5.2, 0.14, "Forward pass (compute value estimate)", ha="center", va="bottom",
            fontsize=10.5, color=BLUE, style="italic")

    ax.annotate("", xy=(1.5, -0.22), xytext=(8.9, -0.22),
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.4", lw=1.8, ls="--", color=CORAL))
    ax.text(5.2, -0.26, r"Backpropagation ($\nabla_{\mathbf{w}} \hat{v}$ for semi-gradient TD / MC)",
            ha="center", va="top", fontsize=10.5, color=CORAL, style="italic")

    save(fig, out, "ch09-ann-architecture.png")


# ---------------------------------------------------------------------------
# Chapter 11
# ---------------------------------------------------------------------------

def fig_ch11_counterexample_simple(out: Path) -> None:
    """Figure 11.1: Simple 2-state divergence fragment (w -> 2w, R = 0)."""
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    ax.set_xlim(0, 8.0)
    ax.set_ylim(0, 2.8)
    ax.axis("off")

    ax.add_patch(Circle((2.2, 1.4), 0.62, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=4))
    ax.add_patch(Circle((5.8, 1.4), 0.62, fc=LIGHT_CORAL, ec=CORAL, lw=2.2, zorder=4))
    ax.text(2.2, 1.4, r"$w$", ha="center", va="center", fontsize=16, weight="bold", color=NAVY, zorder=5)
    ax.text(5.8, 1.4, r"$2w$", ha="center", va="center", fontsize=16, weight="bold", color=CORAL, zorder=5)

    ax.annotate("", xy=(5.12, 1.4), xytext=(2.88, 1.4),
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5", lw=2.2, color=DARK))
    ax.text(4.0, 1.78, r"$R = 0$", ha="center", va="bottom", fontsize=12.5, weight="bold", color=AMBER)
    ax.text(4.0, 0.35, "Shared weight $w$: bootstrapping $w$ toward $2\\gamma w$ amplifies $|w|$ when $2\\gamma > 1$",
            ha="center", va="center", fontsize=10.5, color=SLATE, style="italic")

    save(fig, out, "ch11-counterexample-simple.png")


def fig_ch11_bairds_counterexample(out: Path) -> None:
    """Figure 11.2: Baird's 7-state, 2-action star MDP."""
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.set_xlim(-0.6, 12.2)
    ax.set_ylim(-0.5, 6.2)
    ax.axis("off")

    # 6 upper states
    top_xs = np.linspace(1.6, 11.0, 6)
    y_top = 3.95
    y_bus = 5.45
    hub = (6.3, 1.25)

    # Dashed bus (dashed action: uniform 1/6 to upper 6 states)
    ax.plot([0.25, top_xs[-1]], [y_bus, y_bus], color=BLUE, lw=2.0, ls="--", zorder=2)
    # Dashed return curve from hub left around to bus
    ax.plot([hub[0] - 1.05, 0.25, 0.25], [hub[1], hub[1], y_bus], color=BLUE, lw=2.0, ls="--", zorder=2)

    for i, ux in enumerate(top_xs, 1):
        # Bidirectional dashed arrow between bus and state
        ax.annotate("", xy=(ux, y_top + 0.62), xytext=(ux, y_bus),
                    arrowprops=dict(arrowstyle="<->,head_width=0.25,head_length=0.35",
                                    lw=1.7, ls="--", color=BLUE), zorder=3)
        # Solid action arrow down to hub
        ax.annotate("", xy=(hub[0] + (ux - hub[0]) * 0.16, hub[1] + 0.64), xytext=(ux, y_top - 0.60),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.4",
                                    lw=1.9, color=NAVY), zorder=3)
        # Upper state ellipse
        ax.add_patch(Ellipse((ux, y_top), 1.55, 1.15, fc=LIGHT_BLUE, ec=NAVY, lw=2.0, zorder=5))
        ax.text(ux, y_top, rf"$2w_{i}+w_8$", ha="center", va="center",
                fontsize=11.5, weight="bold", color=NAVY, zorder=6)

    # Lower hub state (7th state)
    ax.add_patch(Ellipse(hub, 2.05, 1.22, fc=LIGHT_CORAL, ec=CORAL, lw=2.2, zorder=5))
    ax.text(hub[0], hub[1], r"$w_7 + 2w_8$", ha="center", va="center",
            fontsize=12.5, weight="bold", color=CORAL, zorder=6)

    # Solid self-loop on hub
    ax.annotate("", xy=(hub[0] + 0.72, hub[1] - 0.50), xytext=(hub[0] + 1.02, hub[1] + 0.15),
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.4",
                                connectionstyle="arc3,rad=-1.55", lw=2.0, color=NAVY), zorder=4)

    # Legend / key box at bottom-right
    ax.text(10.0, 1.45, "Solid action:\n" + r"$\pi = 1,\; b = 1/7$" + "\n(always goes to hub)",
            ha="left", va="center", fontsize=10.5, color=NAVY, weight="bold")
    ax.text(10.0, 0.30, "Dashed action:\n" + r"$\pi = 0,\; b = 6/7$" + "\n(uniform over top 6)",
            ha="left", va="center", fontsize=10.5, color=BLUE, weight="bold")
    ax.text(6.3, 5.82, r"All rewards $R = 0$ on every transition", ha="center", va="center",
            fontsize=11.5, color=AMBER, weight="bold")

    save(fig, out, "ch11-bairds-counterexample.png")


def fig_ch11_tsitsiklis_van_roy(out: Path) -> None:
    """Figure 11.3: Tsitsiklis & Van Roy's counterexample (w -> 2w with 1-eps loop and eps terminal)."""
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.set_xlim(0, 9.6)
    ax.set_ylim(-0.1, 4.3)
    ax.axis("off")

    s1, s2, term = (1.8, 2.35), (5.0, 2.35), (7.6, 0.75)
    ax.add_patch(Circle(s1, 0.62, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=5))
    ax.add_patch(Circle(s2, 0.62, fc=LIGHT_CORAL, ec=CORAL, lw=2.2, zorder=5))
    draw_terminal(ax, term[0], term[1], half=0.32, fc=TEAL, ec=NAVY, lw=2.0, zorder=5)

    ax.text(s1[0], s1[1], r"$w$", ha="center", va="center", fontsize=16, weight="bold", color=NAVY, zorder=6)
    ax.text(s2[0], s2[1], r"$2w$", ha="center", va="center", fontsize=16, weight="bold", color=CORAL, zorder=6)
    ax.text(term[0] + 0.55, term[1], "Terminal\n" + r"($V=0$)", ha="left", va="center",
            fontsize=11.5, weight="bold", color=TEAL)

    # w -> 2w
    ax.annotate("", xy=(s2[0] - 0.66, s2[1]), xytext=(s1[0] + 0.66, s1[1]),
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5", lw=2.2, color=DARK))
    ax.text(3.4, 2.68, r"$R = 0$", ha="center", va="bottom", fontsize=12.0, color=AMBER, weight="bold")

    # Self-loop 1 - eps on 2w
    ax.annotate("", xy=(s2[0] + 0.56, s2[1] + 0.34), xytext=(s2[0] + 0.06, s2[1] + 0.64),
                arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45",
                                connectionstyle="arc3,rad=-2.1", lw=2.1, color=CORAL), zorder=4)
    ax.text(5.95, 3.38, r"$1 - \varepsilon$", ha="left", va="center", fontsize=13.5, color=CORAL, weight="bold")

    # Transition eps to terminal
    ax.annotate("", xy=(term[0] - 0.34, term[1] + 0.24), xytext=(s2[0] + 0.48, s2[1] - 0.44),
                arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.45", lw=2.1, color=TEAL), zorder=4)
    ax.text(6.05, 1.28, r"$\varepsilon$", ha="right", va="center", fontsize=13.5, color=TEAL, weight="bold")

    save(fig, out, "ch11-tsitsiklis-van-roy.png")


def fig_ch11_linear_projection(out: Path) -> None:
    """Figure 11.4: Upgraded, spacious geometry of linear VFA (BE, PBE, VE, w_TD, min BE, min TDE)."""
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    ax.set_xlim(-0.2, 12.6)
    ax.set_ylim(-0.2, 7.2)
    ax.axis("off")

    plane = Polygon([(0.4, 1.05), (9.8, 0.35), (12.2, 3.65), (2.8, 4.35)],
                    closed=True, fc=LIGHT_BLUE, ec=BLUE, lw=2.0, alpha=0.72, zorder=1)
    ax.add_patch(plane)
    ax.text(1.4, 1.25, r"Representable linear subspace $\{ \hat{v}(\mathbf{w}) = \mathbf{X}\mathbf{w} \}$",
            fontsize=11.5, color=NAVY, style="italic", weight="bold", zorder=3)
    ax.text(1.4, 6.35, "Ambient value-function space\n" + r"$\mathbb{R}^{|\mathcal{S}|}$",
            ha="center", va="center", fontsize=11.5, color=SLATE, style="italic")

    # --- Left side of plane: arbitrary v_w -> B_pi v_w (BE) -> Pi B_pi v_w (PBE) ---
    vw = (2.75, 2.55)
    bvw = (4.45, 5.60)
    pbvw = (4.45, 2.75)

    ax.annotate("", xy=bvw, xytext=vw,
                arrowprops=dict(arrowstyle="-|>,head_width=0.30,head_length=0.45", lw=2.2, color=NAVY), zorder=6)
    ax.text(3.30, 4.82, "Bellman\nerror (BE)", ha="right", va="center", fontsize=11.0,
            color=NAVY, weight="bold", rotation=57)

    ax.plot([bvw[0], pbvw[0]], [bvw[1], pbvw[1]], color=SLATE, lw=1.6, ls="--", zorder=4)
    ax.plot([pbvw[0], pbvw[0] - 0.24, pbvw[0] - 0.24],
            [pbvw[1] + 0.24, pbvw[1] + 0.24, pbvw[1]], color=SLATE, lw=1.2, zorder=4)

    ax.annotate("", xy=pbvw, xytext=vw,
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.40", lw=2.2, color=BLUE), zorder=6)
    ax.text(3.60, 2.38, r"$\mathrm{PBE}$", ha="center", va="top", fontsize=11.5, color=BLUE, weight="bold")

    ax.scatter([vw[0], bvw[0], pbvw[0]], [vw[1], bvw[1], pbvw[1]],
               color=[NAVY, NAVY, BLUE], s=70, zorder=7)
    ax.text(vw[0] - 0.12, vw[1] - 0.30, r"$\hat{v}(\mathbf{w})$", ha="center", va="top",
            fontsize=11.5, color=NAVY, weight="bold")
    ax.text(bvw[0] + 0.18, bvw[1] + 0.12, r"$B_\pi \hat{v}(\mathbf{w})$", ha="left", va="bottom",
            fontsize=11.5, color=NAVY, weight="bold")
    ax.text(pbvw[0] + 0.05, pbvw[1] - 0.32, r"$\Pi B_\pi \hat{v}(\mathbf{w})$", ha="center", va="top",
            fontsize=11.0, color=BLUE, weight="bold")

    # --- Center: TD fixed point w_TD (PBE = 0, strictly vertical orthogonal B_pi) ---
    p_td = (6.65, 2.40)
    bv_td = (6.65, 5.45)
    ax.annotate("", xy=bv_td, xytext=p_td,
                arrowprops=dict(arrowstyle="<->,head_width=0.28,head_length=0.40", lw=2.1, color=TEAL), zorder=6)
    ax.plot([p_td[0], p_td[0] + 0.24, p_td[0] + 0.24],
            [p_td[1] + 0.24, p_td[1] + 0.24, p_td[1]], color=TEAL, lw=1.3, zorder=5)
    ax.scatter([p_td[0], bv_td[0]], [p_td[1], bv_td[1]], color=TEAL, s=75, zorder=7)
    ax.text(bv_td[0], bv_td[1] + 0.20, r"$B_\pi \hat{v}(\mathbf{w}_{\mathrm{TD}})$", ha="center", va="bottom",
            fontsize=11.5, color=TEAL, weight="bold")
    ax.text(6.85, 4.68, r"$\Pi B_\pi \hat{v} = \hat{v}$" + "\n" + r"$(\overline{\mathrm{PBE}}=0)$",
            ha="left", va="center", fontsize=10.8, color=TEAL, style="italic", zorder=7)
    ax.text(p_td[0], p_td[1] - 0.32, r"$\mathbf{w}_{\mathrm{TD}}$", ha="center", va="top",
            fontsize=12.5, color=TEAL, weight="bold")

    # --- Right-center: true value v_pi & orthogonal projection Pi v_pi (min VE) ---
    v_pi = (9.15, 6.40)
    p_ve = (9.15, 2.75)
    ax.annotate("", xy=v_pi, xytext=p_ve,
                arrowprops=dict(arrowstyle="-|>,head_width=0.30,head_length=0.44", lw=2.2, ls="--", color=CORAL),
                zorder=6)
    ax.plot([p_ve[0], p_ve[0] - 0.24, p_ve[0] - 0.24],
            [p_ve[1] + 0.24, p_ve[1] + 0.24, p_ve[1]], color=CORAL, lw=1.3, zorder=5)
    ax.scatter([v_pi[0], p_ve[0]], [v_pi[1], p_ve[1]], color=[CORAL, NAVY], s=85, zorder=7)
    ax.text(v_pi[0] + 0.22, v_pi[1], r"$v_\pi$ (true value)", ha="left", va="center",
            fontsize=12.5, color=CORAL, weight="bold")
    ax.text(v_pi[0] + 0.18, 4.75, "Value error\n" + r"($\mathrm{VE}$)", ha="left", va="center",
            fontsize=11.0, color=CORAL, weight="bold")
    ax.text(p_ve[0] - 0.10, p_ve[1] - 0.34, r"$\Pi v_\pi$ (min $\overline{\mathrm{VE}}$)",
            ha="center", va="top", fontsize=11.5, color=NAVY, weight="bold")

    p_be = (8.95, 1.30)
    p_tde = (10.75, 3.15)
    ax.scatter([p_be[0]], [p_be[1]], color=AMBER, s=80, zorder=7)
    ax.text(p_be[0], p_be[1] - 0.30, r"min $\overline{\mathrm{BE}}$", ha="center", va="top",
            fontsize=11.5, color=AMBER, weight="bold")
    ax.scatter([p_tde[0]], [p_tde[1]], color=SLATE, s=80, zorder=7)
    ax.text(p_tde[0] - 0.10, p_tde[1] - 0.32, r"min $\overline{\mathrm{TDE}}$", ha="center", va="top",
            fontsize=11.5, color=SLATE, weight="bold")

    save(fig, out, "ch11-linear-projection.png")


def fig_ch11_ve_learnability_mrps(out: Path) -> None:
    """Figure 11.5: VE learnability counterexample — 1-state vs 2-state MRP with identical reward stream."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 3.6), gridspec_kw={"width_ratios": [1.0, 1.55]})

    ax1.set_xlim(0, 6.2)
    ax1.set_ylim(-0.1, 3.6)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("MRP 1 (Single State)", fontsize=13.0, weight="bold", color=NAVY, pad=8)

    c = (3.1, 1.85)
    ax1.add_patch(Circle(c, 0.56, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=5))
    ax1.text(*c, r"$w$", ha="center", va="center", fontsize=16, weight="bold", color=NAVY, zorder=6)

    ax1.annotate("", xy=(2.58, 1.58), xytext=(2.58, 2.12),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=1.95", lw=2.0, color=BLUE), zorder=4)
    ax1.text(0.85, 1.85, r"$R=0$" + "\n(0.5)", ha="center", va="center", fontsize=11.5, color=BLUE, weight="bold")

    ax1.annotate("", xy=(3.62, 1.58), xytext=(3.62, 2.12),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-1.95", lw=2.0, color=AMBER), zorder=4)
    ax1.text(5.35, 1.85, r"$R=2$" + "\n(0.5)", ha="center", va="center", fontsize=11.5, color=AMBER, weight="bold")

    ax1.text(3.1, 0.30, "True value: $v_\\pi = \\frac{1}{1-\\gamma}$", ha="center", va="center",
             fontsize=11.0, color=SLATE, style="italic")

    ax2.set_xlim(0, 9.6)
    ax2.set_ylim(-0.1, 3.6)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("MRP 2 (Two Aliased States, Same Feature $w$)", fontsize=13.0, weight="bold", color=NAVY, pad=8)

    c1, c2 = (3.1, 1.85), (6.5, 1.85)
    for pt in (c1, c2):
        ax2.add_patch(Circle(pt, 0.56, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=5))
        ax2.text(*pt, r"$w$", ha="center", va="center", fontsize=16, weight="bold", color=NAVY, zorder=6)

    ax2.annotate("", xy=(2.58, 1.58), xytext=(2.58, 2.12),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=1.95", lw=2.0, color=BLUE), zorder=4)
    ax2.text(0.85, 1.85, r"$R=0$" + "\n(0.5)", ha="center", va="center", fontsize=11.5, color=BLUE, weight="bold")

    ax2.annotate("", xy=(5.96, 2.12), xytext=(3.64, 2.12),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-0.26", lw=2.0, color=BLUE), zorder=4)
    ax2.text(4.8, 2.75, r"$R=0$ (0.5)", ha="center", va="bottom", fontsize=11.0, color=BLUE, weight="bold")

    ax2.annotate("", xy=(3.64, 1.58), xytext=(5.96, 1.58),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-0.26", lw=2.0, color=AMBER), zorder=4)
    ax2.text(4.8, 0.96, r"$R=2$ (0.5)", ha="center", va="top", fontsize=11.0, color=AMBER, weight="bold")

    ax2.annotate("", xy=(7.02, 1.58), xytext=(7.02, 2.12),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-1.95", lw=2.0, color=AMBER), zorder=4)
    ax2.text(8.75, 1.85, r"$R=2$" + "\n(0.5)", ha="center", va="center", fontsize=11.5, color=AMBER, weight="bold")

    ax2.text(4.8, 0.22, "Identical i.i.d. 50/50 reward stream (0, 2, ...), different true $\\overline{\\mathrm{VE}}$",
             ha="center", va="center", fontsize=10.8, color=SLATE, style="italic")

    fig.tight_layout(w_pad=1.6)
    save(fig, out, "ch11-ve-learnability-mrps.png")


def fig_ch11_be_learnability_mrps(out: Path) -> None:
    """Figure 11.6: BE learnability counterexample — 2-state vs 3-state aliased MRP pair."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.1), gridspec_kw={"width_ratios": [1.0, 1.55]})

    ax1.set_xlim(0, 7.0)
    ax1.set_ylim(-0.1, 4.2)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("MRP A (2 States)", fontsize=13.0, weight="bold", color=NAVY, pad=8)

    pA, pB = (1.6, 2.2), (4.3, 2.2)
    ax1.add_patch(Circle(pA, 0.52, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=5))
    ax1.add_patch(Circle(pB, 0.52, fc=LIGHT_TEAL, ec=TEAL, lw=2.2, zorder=5))
    ax1.text(*pA, "A", ha="center", va="center", fontsize=15, weight="bold", color=NAVY, zorder=6)
    ax1.text(*pB, "B", ha="center", va="center", fontsize=15, weight="bold", color=TEAL, zorder=6)

    ax1.annotate("", xy=(3.80, 1.96), xytext=(2.10, 1.96),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=0.28", lw=2.0, color=SLATE), zorder=4)
    ax1.text(2.95, 1.32, "0 (1.0)", ha="center", va="top", fontsize=11.0, color=SLATE, weight="bold")

    ax1.annotate("", xy=(2.10, 2.44), xytext=(3.80, 2.44),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=0.28", lw=2.0, color=BLUE), zorder=4)
    ax1.text(2.95, 3.05, "+1 (0.5)", ha="center", va="bottom", fontsize=11.0, color=BLUE, weight="bold")

    ax1.annotate("", xy=(4.80, 1.94), xytext=(4.80, 2.46),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-1.95", lw=2.0, color=CORAL), zorder=4)
    ax1.text(6.25, 2.20, "-1\n(0.5)", ha="center", va="center", fontsize=11.0, color=CORAL, weight="bold")

    ax2.set_xlim(0, 10.8)
    ax2.set_ylim(-0.1, 4.2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("MRP B (3 States; B and B' Share Features)", fontsize=13.0, weight="bold", color=NAVY, pad=8)

    qA, qB, qBp = (1.35, 2.30), (4.45, 2.30), (7.75, 2.30)
    ax2.add_patch(FancyBboxPatch((3.72, 1.52), 4.78, 1.56, boxstyle="round,pad=0.14",
                                 fc=LIGHT_TEAL, ec=TEAL, lw=1.4, ls=":", alpha=0.45, zorder=1))
    ax2.text(6.10, 3.36, "Aliased feature vector", ha="center", va="bottom",
             fontsize=10.8, color=TEAL, style="italic", weight="bold")

    ax2.add_patch(Circle(qA, 0.52, fc=LIGHT_BLUE, ec=NAVY, lw=2.2, zorder=5))
    ax2.add_patch(Circle(qB, 0.52, fc=LIGHT_TEAL, ec=TEAL, lw=2.2, zorder=5))
    ax2.add_patch(Circle(qBp, 0.52, fc=LIGHT_TEAL, ec=TEAL, lw=2.2, zorder=5))
    ax2.text(*qA, "A", ha="center", va="center", fontsize=15, weight="bold", color=NAVY, zorder=6)
    ax2.text(*qB, "B", ha="center", va="center", fontsize=15, weight="bold", color=TEAL, zorder=6)
    ax2.text(*qBp, "B'", ha="center", va="center", fontsize=15, weight="bold", color=TEAL, zorder=6)

    ax2.annotate("", xy=(1.85, 2.54), xytext=(3.95, 2.54),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=0.26", lw=2.0, color=BLUE), zorder=4)
    ax2.text(2.90, 3.12, "+1 (1.0)", ha="center", va="bottom", fontsize=11.0, color=BLUE, weight="bold")

    # A -> B (0, 0.5) shallow arc, label cleanly above it inside A-B gap
    ax2.annotate("", xy=(3.95, 2.08), xytext=(1.85, 2.08),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=0.20", lw=2.0, color=SLATE), zorder=4)
    ax2.text(2.90, 2.02, "0 (0.5)", ha="center", va="bottom", fontsize=10.5, color=SLATE, weight="bold")

    # A -> B' (0, 0.5) deep bottom arc
    ax2.annotate("", xy=(7.55, 1.78), xytext=(1.55, 1.78),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=0.36", lw=2.0, color=SLATE), zorder=4)
    ax2.text(4.55, 0.35, "0 (0.5)", ha="center", va="top", fontsize=10.8, color=SLATE, weight="bold")

    # B' -> B (-1, 0.5)
    ax2.annotate("", xy=(5.00, 2.30), xytext=(7.20, 2.30),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4", lw=2.0, color=CORAL), zorder=4)
    ax2.text(6.10, 2.48, "-1 (0.5)", ha="center", va="bottom", fontsize=10.8, color=CORAL, weight="bold")

    # B' -> B' (-1, 0.5)
    ax2.annotate("", xy=(8.25, 2.04), xytext=(8.25, 2.56),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.4",
                                 connectionstyle="arc3,rad=-1.95", lw=2.0, color=CORAL), zorder=4)
    ax2.text(9.75, 2.30, "-1\n(0.5)", ha="center", va="center", fontsize=11.0, color=CORAL, weight="bold")

    fig.tight_layout(w_pad=1.6)
    save(fig, out, "ch11-be-learnability-mrps.png")


# ---------------------------------------------------------------------------
# Chapter 12
# ---------------------------------------------------------------------------

def fig_ch12_lambda_weights(out: Path) -> None:
    """Figure 12.1: Geometric n-step return weights (1-lambda)*lambda^(n-1)."""
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ns = np.arange(1, 11)
    width = 0.26
    configs = [(0.2, NAVY, -width), (0.5, TEAL, 0.0), (0.8, AMBER, width)]

    for lam, col, offset in configs:
        w = (1.0 - lam) * (lam ** (ns - 1))
        ax.bar(ns + offset, w, width=width, color=col, alpha=0.90,
               label=rf"$\lambda = {lam}$  (remaining tail: $\lambda^{{10}} = {lam**10:.3f}$)")

    ax.set_xticks(ns)
    ax.set_xticklabels([f"{n}-step" for n in ns], fontsize=10.5)
    ax.tick_params(axis="y", labelsize=10.5)
    ax.set_ylabel(r"Weight $(1-\lambda)\lambda^{n-1}$", fontsize=12.0, color=NAVY, weight="bold")
    ax.set_xlabel(r"Component $n$-step return inside $G_t^\lambda$", fontsize=12.0, color=NAVY, weight="bold")
    ax.set_title(r"Geometric Weighting of $n$-Step Returns in the $\lambda$-Return",
                 fontsize=13.5, weight="bold", color=NAVY, pad=10)
    ax.legend(frameon=False, fontsize=11.0)
    ax.grid(axis="y", ls=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save(fig, out, "ch12-lambda-weights.png")


def fig_ch12_td_lambda_backups(out: Path) -> None:
    """Figure 12.2: Full TD(lambda) vs Truncated TD(lambda) side-by-side backup comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.2))

    def draw_state_chain(ax, x, y_top, dy, depth, terminal=False):
        for s in range(depth):
            y0, y1 = y_top - s * dy, y_top - (s + 1) * dy
            ax.plot([x, x], [y0, y1], color=BLUE, lw=1.9)
            draw_state(ax, x, y0, r=0.145)
            draw_action(ax, x, 0.5 * (y0 + y1), r=0.085)
        y_end = y_top - depth * dy
        if terminal:
            draw_terminal(ax, x, y_end, half=0.145)
        else:
            draw_state(ax, x, y_end, r=0.145, fc=LIGHT_AMBER, ec=AMBER, lw=2.0)

    ax1.set_xlim(-0.1, 7.1)
    ax1.set_ylim(-0.3, 5.3)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title(r"Full TD($\lambda$) Backup ($G_t^\lambda$)", fontsize=13.5, weight="bold", color=NAVY, pad=10)

    ax1.plot([0.6, 6.4], [4.60, 4.60], color=NAVY, lw=2.0)
    cols1 = [
        (0.9, r"$1-\lambda$", 1, False),
        (2.3, r"$(1-\lambda)\lambda$", 2, False),
        (3.8, r"$(1-\lambda)\lambda^2$", 3, False),
        (6.0, r"$\lambda^{T-t-1}$", 4, True),
    ]
    for cx, wlbl, d, is_term in cols1:
        ax1.text(cx, 4.78, wlbl, ha="center", va="bottom", fontsize=10.8, color=BLUE, weight="bold")
        draw_state_chain(ax1, cx, 4.15, 0.85, d, terminal=is_term)
    ax1.text(4.95, 2.55, r"$\cdots$", ha="center", va="center", fontsize=20, color=SLATE)
    ax1.text(6.0, 0.25, r"Terminal $S_T$", ha="center", va="center", fontsize=10.5, color=TEAL, weight="bold")

    ax2.set_xlim(-0.1, 7.1)
    ax2.set_ylim(-0.3, 5.3)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title(r"Truncated TD($\lambda$) at Horizon $h$ ($G_{t:h}^\lambda$)",
                  fontsize=13.5, weight="bold", color=NAVY, pad=10)

    ax2.plot([0.6, 6.4], [4.60, 4.60], color=NAVY, lw=2.0)
    cols2 = [
        (0.9, r"$1-\lambda$", 1),
        (2.3, r"$(1-\lambda)\lambda$", 2),
        (3.8, r"$(1-\lambda)\lambda^2$", 3),
        (6.0, r"$\lambda^{h-t-1}$", 3),
    ]
    for idx, (cx, wlbl, d) in enumerate(cols2):
        col_txt = CORAL if idx == 3 else BLUE
        ax2.text(cx, 4.78, wlbl, ha="center", va="bottom", fontsize=10.8, color=col_txt, weight="bold")
        draw_state_chain(ax2, cx, 4.15, 0.85, d, terminal=False)
    ax2.text(4.95, 2.85, r"$\cdots$", ha="center", va="center", fontsize=20, color=SLATE)

    y_cut = 4.15 - 3 * 0.85
    ax2.plot([0.2, 6.9], [y_cut, y_cut], color=CORAL, lw=2.0, ls="--", zorder=3)
    ax2.text(3.55, y_cut - 0.45, r"Horizon cutoff at $h$: tail weight $\lambda^{h-t-1}$ bootstraps from $V(S_h)$",
             ha="center", va="top", fontsize=10.2, color=CORAL, style="italic", weight="bold")

    fig.tight_layout(w_pad=1.6)
    save(fig, out, "ch12-td-lambda-backups.png")


def fig_ch12_forward_backward_views(out: Path) -> None:
    """Figure 12.3: Side-by-side Forward View vs Backward View of TD(lambda) with crisp nested arches."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.8))

    def draw_arch(ax, x0, x1, y_base, peak_h, col, label):
        t = np.linspace(0, 1, 80)
        xs_c = x0 + (x1 - x0) * t
        ys_c = y_base + 4.0 * peak_h * t * (1.0 - t)
        ax.plot(xs_c[:-3], ys_c[:-3], color=col, lw=2.0, zorder=4)
        ax.annotate("", xy=(xs_c[-1], ys_c[-1]), xytext=(xs_c[-5], ys_c[-5]),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.35", lw=2.0, color=col),
                    zorder=5)
        ax.text(0.5 * (x0 + x1), y_base + peak_h + 0.14, label, ha="center", va="bottom",
                fontsize=10.5, color=col, weight="bold", path_effects=HALO, zorder=7)

    xs = [1.0, 2.9, 4.8, 6.7, 8.6]
    y_line = 1.45

    # --- Left: Forward View ---
    ax1.set_xlim(0.1, 9.5)
    ax1.set_ylim(0.1, 5.2)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title(r"Forward View (Theoretical $G_t^\lambda$)", fontsize=13.0, weight="bold", color=NAVY, pad=10)

    ax1.plot([xs[0], xs[-1]], [y_line, y_line], color=SLATE, lw=2.0, zorder=2)
    labels = [r"$S_t$", r"$S_{t+1}$", r"$S_{t+2}$", r"$S_{t+3}$", r"$S_T$"]
    for i, (x, lbl) in enumerate(zip(xs, labels)):
        if i == 0:
            draw_state(ax1, x, y_line, r=0.30, fc=LIGHT_AMBER, ec=AMBER, lw=2.4)
        elif i == 4:
            draw_terminal(ax1, x, y_line, half=0.27, fc=TEAL, ec=NAVY, lw=2.0)
        else:
            draw_state(ax1, x, y_line, r=0.27)
        ax1.text(x, y_line - 0.50, lbl, ha="center", va="top", fontsize=11.5, color=NAVY, weight="bold")

    fweights = [r"$1-\lambda$", r"$(1-\lambda)\lambda$", r"$(1-\lambda)\lambda^2$", r"$\lambda^{T-t-1}$"]
    fheights = [0.68, 1.38, 2.10, 2.85]
    for i, (wl, h) in enumerate(zip(fweights, fheights), 1):
        draw_arch(ax1, xs[0] + 0.08, xs[i], y_line + 0.34, h, BLUE, wl)

    ax1.text(4.8, 0.35, "At $S_t$, look forward to combine upcoming $n$-step returns",
             ha="center", va="center", fontsize=10.5, color=SLATE, style="italic")

    # --- Right: Backward View ---
    ax2.set_xlim(0.1, 9.5)
    ax2.set_ylim(0.1, 5.2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title(r"Backward View (Online Traces $\mathbf{z}_t$)", fontsize=13.0, weight="bold", color=NAVY, pad=10)

    ax2.plot([xs[0], xs[-1]], [y_line, y_line], color=SLATE, lw=2.0, zorder=2)
    blabels = [r"$S_{t-3}$", r"$S_{t-2}$", r"$S_{t-1}$", r"$S_t$", r"$S_{t+1}$"]
    for i, (x, lbl) in enumerate(zip(xs, blabels)):
        if i == 3:
            draw_state(ax2, x, y_line, r=0.30, fc=LIGHT_CORAL, ec=CORAL, lw=2.4)
        else:
            draw_state(ax2, x, y_line, r=0.27)
        ax2.text(x, y_line - 0.50, lbl, ha="center", va="top", fontsize=11.5, color=NAVY, weight="bold")

    ax2.text(0.5 * (xs[3] + xs[4]), y_line + 0.32, r"$\delta_t$", ha="center", va="bottom",
             fontsize=14.0, color=CORAL, weight="bold")

    bweights = [r"$\gamma\lambda\,\delta_t$", r"$(\gamma\lambda)^2\delta_t$", r"$(\gamma\lambda)^3\delta_t$"]
    bheights = [0.75, 1.55, 2.35]
    for target_idx, wl, h in zip([2, 1, 0], bweights, bheights):
        draw_arch(ax2, xs[3] - 0.08, xs[target_idx], y_line + 0.34, h, CORAL, wl)

    ax2.text(4.8, 0.35, r"Broadcast current TD error $\delta_t$ backward in proportion to decaying trace $\mathbf{z}_t$",
             ha="center", va="center", fontsize=10.5, color=SLATE, style="italic")

    fig.tight_layout(w_pad=1.6)
    save(fig, out, "ch12-forward-backward-views.png")


def fig_ch12_action_lambda_backups(out: Path) -> None:
    """Figure 12.4: 3-panel Action-Value lambda-backup taxonomy (Sarsa(λ), Watkins's Q(λ), TB(λ))."""
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 5.4))

    titles = [
        r"Sarsa($\lambda$)" + "\n(on-policy sampled)",
        r"Watkins's Q($\lambda$)" + "\n(cuts off on exploratory step)",
        r"Tree-Backup($\lambda$)" + "\n(expected trees, no IS)",
    ]
    for ax, title in zip(axes, titles):
        ax.set_xlim(-0.1, 6.4)
        ax.set_ylim(-0.35, 5.35)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=12.0, weight="bold", color=NAVY, pad=10)

    # --- Panel 1: Sarsa(lambda) ---
    ax = axes[0]
    ax.plot([0.5, 5.8], [4.55, 4.55], color=NAVY, lw=1.9)
    for cx, wlbl, depth, term in [
        (0.8, r"$1-\lambda$", 1, False),
        (2.1, r"$(1-\lambda)\lambda$", 2, False),
        (3.5, r"$(1-\lambda)\lambda^2$", 3, False),
        (5.4, r"$\lambda^{T-t-1}$", 4, True),
    ]:
        ax.text(cx, 4.70, wlbl, ha="center", va="bottom", fontsize=9.8, color=BLUE, weight="bold")
        y0 = 4.10
        dy = 0.88
        for s in range(depth):
            ya, ys_, yb = y0 - s * dy, y0 - (s + 0.5) * dy, y0 - (s + 1) * dy
            ax.plot([cx, cx], [ya, yb], color=BLUE, lw=1.8)
            draw_action(ax, cx, ya, r=0.085)
            draw_state(ax, cx, ys_, r=0.13)
        y_end = y0 - depth * dy
        if term:
            draw_terminal(ax, cx, y_end, half=0.13)
        else:
            draw_action(ax, cx, y_end, r=0.095, fc=AMBER)
    ax.text(4.45, 2.45, r"$\cdots$", ha="center", va="center", fontsize=18, color=SLATE)
    ax.text(3.1, 0.05, "Pure sampled action-value chains", ha="center", va="center",
            fontsize=10.0, color=SLATE, style="italic")

    # --- Panel 2: Watkins's Q(lambda) ---
    ax = axes[1]
    ax.plot([0.5, 5.8], [4.55, 4.55], color=NAVY, lw=1.9)
    # 1-step greedy max, 2-step greedy max, then cutoff at 3rd step (exploratory action)
    for cx, wlbl, depth, is_cut in [
        (0.95, r"$1-\lambda$", 1, False),
        (2.75, r"$(1-\lambda)\lambda$", 2, False),
        (4.85, r"$\lambda^{2}$ (cutoff)", 3, True),
    ]:
        col_w = CORAL if is_cut else BLUE
        ax.text(cx, 4.70, wlbl, ha="center", va="bottom", fontsize=9.8, color=col_w, weight="bold")
        y0, dy = 4.10, 0.92
        for s in range(depth):
            ya, ys_, yb = y0 - s * dy, y0 - (s + 0.5) * dy, y0 - (s + 1) * dy
            ax.plot([cx, cx], [ya, ys_], color=BLUE, lw=1.8)
            draw_action(ax, cx, ya, r=0.085)
            if s < depth - 1:
                # Greedy sampled continuation
                ax.plot([cx, cx], [ys_, yb], color=BLUE, lw=1.8)
                draw_state(ax, cx, ys_, r=0.13)
            else:
                # Final step: max over all actions
                for dx in (-0.42, 0.0, 0.42):
                    ax.plot([cx, cx + dx], [ys_, yb], color=(CORAL if is_cut else SLATE), lw=1.6)
                    draw_action(ax, cx + dx, yb, r=0.08, fc=(CORAL if is_cut else BLUE))
                ax.add_patch(patches.Arc((cx, ys_), 0.48, 0.42, theta1=210, theta2=330,
                                         color=CORAL, lw=2.0, zorder=6))
                draw_state(ax, cx, ys_, r=0.13)
                if is_cut:
                    ax.text(cx, yb - 0.36, "Exploratory\naction cutoff", ha="center", va="top",
                            fontsize=9.5, color=CORAL, weight="bold")
    ax.text(3.1, 0.05, r"Trace zeroes on first nongreedy action", ha="center", va="center",
            fontsize=10.0, color=CORAL, style="italic")

    # --- Panel 3: Tree-Backup(lambda) ---
    ax = axes[2]
    ax.plot([0.5, 5.8], [4.55, 4.55], color=NAVY, lw=1.9)
    for cx, wlbl, depth in [
        (0.95, r"$1-\lambda$", 1),
        (2.85, r"$(1-\lambda)\lambda$", 2),
        (4.85, r"$(1-\lambda)\lambda^2$", 3),
    ]:
        ax.text(cx, 4.70, wlbl, ha="center", va="bottom", fontsize=9.8, color=TEAL, weight="bold")
        y0, dy = 4.10, 0.92
        for s in range(depth):
            ya, ys_, yb = y0 - s * dy, y0 - (s + 0.5) * dy, y0 - (s + 1) * dy
            ax.plot([cx, cx], [ya, ys_], color=BLUE, lw=1.8)
            draw_action(ax, cx, ya, r=0.085)
            # Branch to unchosen actions at every state
            for dx in (-0.42, 0.42):
                ax.plot([cx, cx + dx], [ys_, yb], color=TEAL, lw=1.6)
                draw_action(ax, cx + dx, yb, r=0.078, fc=TEAL)
            ax.plot([cx, cx], [ys_, yb], color=(TEAL if s == depth - 1 else BLUE), lw=1.8)
            draw_state(ax, cx, ys_, r=0.13)
            if s == depth - 1:
                draw_action(ax, cx, yb, r=0.08, fc=TEAL)
    ax.text(5.85, 2.35, r"$\cdots$", ha="center", va="center", fontsize=18, color=SLATE)
    ax.text(3.1, 0.05, "Expected branches at every depth (no IS)", ha="center", va="center",
            fontsize=10.0, color=TEAL, style="italic")

    fig.tight_layout(w_pad=1.0)
    save(fig, out, "ch12-action-lambda-backups.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="figures")
    parser.add_argument("--preview-dir", default=None)
    args = parser.parse_args()
    out = Path(args.out)
    preview = Path(args.preview_dir) if args.preview_dir else None

    print(f"Generating 23 original conceptual figures into {out}/ ...")
    # Ch. 3
    fig_ch03_mdp_loop(out)
    # Ch. 4
    fig_ch04_gpi(out)
    # Ch. 6
    fig_ch06_td_backups(out, preview_dir=preview)
    # Ch. 7
    fig_ch07_nstep_spectrum(out)
    fig_ch07_nstep_sarsa(out)
    fig_ch07_nstep_unified(out)
    # Ch. 8
    fig_ch08_dyna_unified(out)
    fig_ch08_onestep_matrix(out)
    fig_ch08_rtdp_states(out)
    fig_ch08_heuristic_search(out)
    fig_ch08_mcts_cycle(out)
    # Ch. 9
    fig_ch09_coarse_rbf(out)
    fig_ch09_ann_architecture(out)
    # Ch. 11
    fig_ch11_counterexample_simple(out)
    fig_ch11_bairds_counterexample(out)
    fig_ch11_tsitsiklis_van_roy(out)
    fig_ch11_linear_projection(out)
    fig_ch11_ve_learnability_mrps(out)
    fig_ch11_be_learnability_mrps(out)
    # Ch. 12
    fig_ch12_lambda_weights(out)
    fig_ch12_td_lambda_backups(out)
    fig_ch12_forward_backward_views(out)
    fig_ch12_action_lambda_backups(out)
    print("Done (23 original figures generated).")


if __name__ == "__main__":
    main()
