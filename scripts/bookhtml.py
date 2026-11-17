#!/usr/bin/env python3
"""Read what the built HTML book says about its figures.

Two checks need this and must agree on it: check-parity.py compares the HTML
captions against the PDF's, and check-sources.py compares them against the table
in figures/SOURCES.md. Both only need the HTML, so this module stays free of the
PDF and of PyMuPDF, which check-parity.py imports for its own half.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

CAPTION = re.compile(r"<figcaption[^>]*>\s*(.*?)</figcaption>", re.S)
MATH_SPAN = re.compile(r'<span class="math[^"]*">(.*?)</span>', re.S)


def html_captions(site: Path) -> dict[str, str]:
    """number -> the caption's HTML, e.g. "3.1" -> "<strong>Backup ...</strong> Each ..."."""
    out = {}
    for page in sorted(site.glob("chapters/*.html")):
        text = page.read_text(encoding="utf-8")
        for match in CAPTION.finditer(text):
            # "Figure&nbsp;3.1: ..." has no real whitespace until it is unescaped
            label = re.match(r"\s*Figure\s+([\d.]+)\s*[:.]\s*(.*)$", html.unescape(match.group(1)), re.S)
            if label:
                out[label.group(1)] = label.group(2)
    return out


def caption_markdown(caption: str) -> str:
    """A caption as the source would write it, so the two can be compared.

    The build turns `$v_\\pi$` into a math span and `**text**` into <strong>, and
    this undoes both: math spans become dollars again, other tags and entities
    go, and whitespace collapses to single spaces.
    """
    text = MATH_SPAN.sub(lambda m: f"${m.group(1)}$", caption)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def first_difference(a: str, b: str) -> str:
    """The first word where two captions part company, with a little context."""
    wa, wb = a.split(), b.split()
    i = 0
    while i < len(wa) and i < len(wb) and wa[i] == wb[i]:
        i += 1
    left = " ".join(wa[max(0, i - 2):i]) or "(start)"
    right = wb[i] if i < len(wb) else "(end)"
    return f'{left} "{wa[i] if i < len(wa) else "(end)"}" -> "{right}"'


def sort_key(number: str) -> list[int]:
    """Sort figure numbers numerically: 3.2 before 3.10."""
    return [int(part) for part in number.split(".") if part.isdigit()]
