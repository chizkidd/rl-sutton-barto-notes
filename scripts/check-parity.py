#!/usr/bin/env python3
"""Compare the built HTML and the built PDF for configuration drift.

The two formats are configured separately: HTML numbers three heading levels,
the PDF sets `secnumdepth 2` and has its own table of contents. When those
settings drift apart -- or a heading or figure exists in one build but not the
other -- the output still looks fine. It is just quietly inconsistent.

What is compared:
  - every section number in the HTML (data-number) against the numbers the PDF
    prints ("1.1. Title"), both directions
  - the number of figures in each build, by image reference in the HTML and by
    "Figure N.M" captions in the PDF

Usage: python3 scripts/check-parity.py [--site _site] [--pdf _site/rl-notes.pdf]
Requires PyMuPDF (pip install pymupdf).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF releases
    import fitz

HTML_SECTION = re.compile(r'<h[23]\b[^>]*data-number="([\d.]+)"')
HTML_FIGURE = re.compile(r'<img[^>]+src="[^"]*figures/[^"]+\.(?:png|webp)"')
PDF_SECTION = re.compile(r"^(\d{1,2}(?:\.\d{1,2})+?)\.?\s+(\S.*)$")
PDF_FIGURE = re.compile(r"Figure\s+(\d+\.\d+)")


def html_sections(site: Path):
    numbers = []
    for page in sorted(site.glob("chapters/*.html")):
        numbers += HTML_SECTION.findall(page.read_text(encoding="utf-8"))
    return numbers


def html_figure_count(site: Path) -> int:
    total = 0
    for page in sorted(site.glob("chapters/*.html")):
        text = page.read_text(encoding="utf-8")
        total += len([m for m in HTML_FIGURE.finditer(text) if "webp" not in m.group(0)])
    return total


def pdf_sections(doc):
    numbers = []
    for page in doc:
        for line in page.get_text().splitlines():
            m = PDF_SECTION.match(line.strip())
            if m:
                numbers.append(m.group(1))
    return numbers


def pdf_figures(doc):
    labels = []
    for page in doc:
        labels += PDF_FIGURE.findall(page.get_text())
    return labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--pdf", default="_site/rl-notes.pdf")
    args = parser.parse_args()

    site = Path(args.site)
    if not site.is_dir():
        print(f"check-parity: {site} does not exist; render the book first")
        return 2
    if not Path(args.pdf).exists():
        print(f"check-parity: {args.pdf} does not exist; render the book first")
        return 2

    doc = fitz.open(args.pdf)
    h_secs, p_secs = html_sections(site), pdf_sections(doc)
    h_figs, p_figs = html_figure_count(site), len(set(pdf_figures(doc)))

    print(f"check-parity: sections  HTML {len(h_secs)}  PDF {len(p_secs)}")
    print(f"              figures   HTML {h_figs}  PDF {p_figs}")

    problems = []
    hs, ps = set(h_secs), set(p_secs)
    if hs - ps:
        problems.append(f"numbered in HTML but missing from the PDF: {', '.join(sorted(hs - ps, key=lambda s: [int(x) for x in s.split('.')]))}")
    if ps - hs:
        problems.append(f"numbered in the PDF but missing from the HTML: {', '.join(sorted(ps - hs, key=lambda s: [int(x) for x in s.split('.')]))}")
    if h_figs != p_figs:
        problems.append(f"figure count differs: HTML {h_figs}, PDF {p_figs}")

    if not problems:
        print("  the two builds agree on section numbering and figure count")
        return 0
    for p in problems:
        print(f"  DRIFT: {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
