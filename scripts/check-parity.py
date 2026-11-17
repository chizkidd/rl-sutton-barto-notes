#!/usr/bin/env python3
"""Compare the built HTML and the built PDF for configuration drift.

The two formats are configured separately: HTML numbers three heading levels,
the PDF sets `secnumdepth 2` and has its own table of contents. When those
settings drift apart -- or a heading, figure or caption exists in one build but
not the other -- the output still looks fine. It is just quietly inconsistent.

What is compared:
  - section numbers, HTML `data-number` against the numbers the PDF prints,
    ignoring the PDF's table-of-contents pages (they repeat every number, with
    dot leaders, before the content starts)
  - figure captions, by number and by text: the HTML `figcaption` says
    "Figure 3.1: ..." and the PDF says "Figure 3.1. ...", which is a difference
    in punctuation, not in content

Usage: python3 scripts/check-parity.py [--site _site] [--pdf _site/rl-notes.pdf]
Requires PyMuPDF (pip install pymupdf).
"""

import argparse
import html
import re
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF releases
    import fitz

HTML_SECTION = re.compile(r'<h[2-4]\b[^>]*data-number="([\d.]+)"')
HTML_CAPTION = re.compile(r"<figcaption[^>]*>\s*(.*?)</figcaption>", re.S)
PDF_SECTION = re.compile(r"^(\d{1,2}(?:\.\d{1,2})+?)\.?\s+(\S.*)$")
PDF_CAPTION = re.compile(r"^Figure\s+(\d+\.\d+)\.\s*(.*)$")
TOC_LEADER = re.compile(r"\.\s\.\s\.")


def norm(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace("\u00a0", " ")
    text = re.sub(r"[^A-Za-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def words(text: str):
    return {w for w in norm(text).split() if len(w) > 2}


def similarity(a: str, b: str) -> float:
    """Share of the shorter caption's words that the other caption has."""
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 1.0 if a.strip() == b.strip() else 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def html_sections(site: Path):
    numbers = []
    for page in sorted(site.glob("chapters/*.html")):
        numbers += HTML_SECTION.findall(page.read_text(encoding="utf-8"))
    return numbers


def html_captions(site: Path):
    """number -> caption text, from the figcaptions."""
    out = {}
    for page in sorted(site.glob("chapters/*.html")):
        text = page.read_text(encoding="utf-8")
        for m in HTML_CAPTION.finditer(text):
            # "Figure&nbsp;3.1: ..." has no real whitespace until it is unescaped
            label = re.match(r"\s*Figure\s+([\d.]+)\s*[:.]\s*(.*)$", html.unescape(m.group(1)), re.S)
            if not label:
                continue
            out[label.group(1)] = label.group(2)
    return out


def pdf_sections(doc):
    numbers, in_toc = [], True
    for page in doc:
        for line in page.get_text().splitlines():
            line = line.strip()
            if not line:
                continue
            if line == "Table of contents":
                in_toc = True  # a TOC page header; the last one ends with the body
                continue
            if TOC_LEADER.search(line):
                continue
            m = PDF_SECTION.match(line)
            if m:
                if not in_toc:
                    numbers.append(m.group(1))
                continue
            # first real heading or body line after the TOC switches us out of it
            if in_toc and not line[0].isdigit():
                in_toc = False
    return numbers


def pdf_captions(doc):
    """number -> caption text, from the lines the PDF prints."""
    out = {}
    for page in doc:
        for line in page.get_text().splitlines():
            m = PDF_CAPTION.match(line.strip())
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2)
    return out


def sort_key(number: str):
    return [int(p) for p in number.split(".")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--pdf", default="_site/rl-notes.pdf")
    parser.add_argument("--min-similarity", type=float, default=0.6)
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
    h_caps, p_caps = html_captions(site), pdf_captions(doc)

    print(f"check-parity: sections  HTML {len(h_secs)}  PDF {len(p_secs)}")
    print(f"              figures   HTML {len(h_caps)}  PDF {len(p_caps)}")

    problems = []
    hs, ps = set(h_secs), set(p_secs)
    if hs - ps:
        problems.append(f"numbered in HTML but missing from the PDF: {', '.join(sorted(hs - ps, key=sort_key))}")
    if ps - hs:
        problems.append(f"numbered in the PDF but missing from the HTML: {', '.join(sorted(ps - hs, key=sort_key))}")

    only_html = sorted(set(h_caps) - set(p_caps), key=sort_key)
    only_pdf = sorted(set(p_caps) - set(h_caps), key=sort_key)
    if only_html:
        problems.append(f"figures only in the HTML: {', '.join(only_html)}")
    if only_pdf:
        problems.append(f"figures only in the PDF: {', '.join(only_pdf)}")

    for number in sorted(set(h_caps) & set(p_caps), key=sort_key):
        score = similarity(h_caps[number], p_caps[number])
        if score < args.min_similarity:
            problems.append(
                f"caption {number} differs ({score:.0%} word overlap): "
                f'HTML "{" ".join(h_caps[number].split())[:70]}" / PDF "{" ".join(p_caps[number].split())[:70]}"'
            )

    if not problems:
        print("  the two builds agree on section numbering and on every figure caption")
        return 0
    for p in problems:
        print(f"  DRIFT: {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
