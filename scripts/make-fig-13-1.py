#!/usr/bin/env python3
"""Redraw figure 13.1, the four normal densities, at printer resolution.

The PNG this replaces was a 631x336 render, about 91 dpi, and the book places
the figure 6.9 in wide, so it printed visibly soft. The curves are the normal
probability density

    p(x) = exp(-((x - mu)^2) / (2 sigma^2)) / (sigma sqrt(2 pi))

for the four (mean, variance) pairs the original figure showed. Drawing them
at the width the book uses puts the file at 300 dpi, and keeping the original
631:336 aspect ratio means the placed height does not change either. Palette,
axes, grid, legend and tick positions are matched to the original.

It overwrites figures/ch13-13-7-prob-density-function.png in place. Run
scripts/make-webp.py afterwards to refresh the gallery copy, then render.

Usage: python3 scripts/make-fig-13-1.py
"""

import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
    import matplotlib
except ImportError:
    print("make-fig-13-1: matplotlib, numpy and Pillow are required "
          "(pip install matplotlib numpy pillow)")
    sys.exit(2)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (the backend has to be set first)

OUT = Path("figures") / "ch13-13-7-prob-density-function.png"

# Inches: 6.9 is the width the PDF gives the figure, 3.68 keeps 631:336.
WIDTH, HEIGHT = 6.9, 3.68
DPI = 300

BG = "#f8f8f6"
GRID = "#e7e7e5"
TEXT = "#7a7a7a"

# (mean, variance, colour), in the order and palette of the original figure.
CURVES = [
    (0.0, 0.2, "#1a53c4"),
    (0.0, 1.0, "#c0392b"),
    (0.0, 5.0, "#239b56"),
    (-2.0, 0.5, "#ca8a04"),
]


def pdf(x, mu, var):
    sigma = np.sqrt(var)
    return np.exp(-((x - mu) ** 2) / (2 * var)) / (sigma * np.sqrt(2 * np.pi))


def main() -> int:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "axes.facecolor": BG,
        "figure.facecolor": BG,
        "axes.edgecolor": BG,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "mathtext.fontset": "dejavusans",
    })

    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), dpi=DPI)
    fig.subplots_adjust(left=0.075, right=0.968, top=0.935, bottom=0.185)

    x = np.linspace(-5, 5, 1001)
    for mu, var, colour in CURVES:
        ax.plot(x, pdf(x, mu, var), color=colour, linewidth=1.5,
                label=rf"$\mu$={mu:g},  $\sigma^2$={var:.1f}")

    ax.set_xlim(-5, 5)
    ax.set_ylim(0, 1.0)
    ax.set_xticks(range(-5, 6))
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xlabel("x")
    ax.set_axisbelow(True)

    legend = ax.legend(loc="upper right", frameon=False, fontsize=9,
                       handlelength=2.0, labelspacing=0.8, borderaxespad=0.4)
    for text in legend.get_texts():
        text.set_color(TEXT)

    fig.savefig(OUT, dpi=DPI, facecolor=BG)

    # Flatten to RGB, since the PDF embeds it as a plain image rather than an
    # alpha blob, and keep 300 dpi in the PNG's pHYs chunk so the pixel size
    # and the printed size agree.
    with Image.open(OUT) as img:
        img.convert("RGB").save(OUT, dpi=(DPI, DPI))

    with Image.open(OUT) as img:
        print(f"make-fig-13-1: wrote {OUT} ({img.width}x{img.height} at {DPI} dpi)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
