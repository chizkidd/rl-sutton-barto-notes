#!/usr/bin/env python3
"""Generate a clean 1600x2400 EPUB cover image matching the book's academic palette.

Usage: python3 scripts/make-cover.py [--out figures/epub-cover.png]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

NAVY = "#13293d"
DEEP = "#0d1f2f"
TEAL = "#2a9d8f"
AMBER = "#f59e0b"
SKY = "#93c5fd"
WHITE = "#f8fafc"
MUTED = "#cbd5e1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="figures/epub-cover.png")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8.0, 12.0), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Background & subtle accent bands
    ax.add_patch(Rectangle((0, 0), 8, 12, fc=NAVY, ec="none"))
    ax.add_patch(Rectangle((0, 0), 0.32, 12, fc=TEAL, ec="none"))
    ax.add_patch(Rectangle((0.32, 0), 0.06, 12, fc=AMBER, ec="none"))

    # Subtle geometric MDP / backup tree motif in upper-middle band
    ax.add_patch(Rectangle((0.38, 4.15), 7.62, 3.05, fc=DEEP, ec="none", alpha=0.55))
    root = (4.2, 6.55)
    lvl1 = [(2.4, 5.75), (4.2, 5.75), (6.0, 5.75)]
    lvl2 = [(1.6, 4.80), (2.7, 4.80), (3.7, 4.80), (4.7, 4.80), (5.7, 4.80), (6.8, 4.80)]
    for i, p1 in enumerate(lvl1):
        ax.plot([root[0], p1[0]], [root[1], p1[1]], color=SKY, lw=2.2, alpha=0.55)
        for p2 in lvl2[2 * i: 2 * i + 2]:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=TEAL, lw=1.8, alpha=0.55)
            ax.add_patch(Circle(p2, 0.14, fc=DEEP, ec=TEAL, lw=2.0, zorder=5))
        ax.add_patch(Circle(p1, 0.11, fc=AMBER, ec=WHITE, lw=1.2, zorder=6))
    ax.add_patch(Circle(root, 0.20, fc=NAVY, ec=SKY, lw=2.6, zorder=6))

    # Decorative subtle Bellman formula watermark
    ax.text(4.2, 4.38, r"$v_*(s) = \max_a \sum_{s', r} p(s', r \mid s, a)\,[r + \gamma v_*(s')]$",
            ha="center", va="center", fontsize=11.5, color=SKY, alpha=0.65, family="DejaVu Serif")

    # Top kicker
    ax.text(0.85, 10.95, "COMPANION STUDY NOTES", ha="left", va="center",
            fontsize=11.5, weight="bold", color=AMBER, family="DejaVu Sans")
    ax.plot([0.85, 3.75], [10.65, 10.65], color=TEAL, lw=2.2)

    # Main Title
    ax.text(0.85, 9.75, "Reinforcement\nLearning:", ha="left", va="top",
            fontsize=32, weight="bold", color=WHITE, family="DejaVu Serif", linespacing=1.18)
    ax.text(0.85, 8.15, "An Introduction", ha="left", va="top",
            fontsize=24, style="italic", color=SKY, family="DejaVu Serif")

    # Subtitle & Edition
    ax.text(0.85, 3.45, "Companion Notes to Sutton & Barto\n(2nd Edition, 2020) · Chapters 1–13",
            ha="left", va="top", fontsize=14, color=MUTED, family="DejaVu Serif", linespacing=1.45)

    # Bottom pill & author
    ax.add_patch(FancyBboxPatch((0.85, 2.05), 5.6, 0.48, boxstyle="round,pad=0.06",
                                fc=DEEP, ec=TEAL, lw=1.2))
    ax.text(3.65, 2.29, "Tabular & Approximate Methods  ·  42 Diagrams",
            ha="center", va="center", fontsize=10.2, color=SKY, family="DejaVu Sans", weight="bold")

    ax.text(0.85, 1.15, "Chizoba Obasi", ha="left", va="center",
            fontsize=17, weight="bold", color=WHITE, family="DejaVu Serif")
    ax.text(0.85, 0.72, "CC BY-NC-SA 4.0  ·  MIT License", ha="left", va="center",
            fontsize=10.5, color=MUTED, family="DejaVu Sans")

    fig.savefig(out, dpi=200, facecolor=NAVY)
    plt.close(fig)
    print(f"  wrote {out} (1600x2400)")


if __name__ == "__main__":
    main()
