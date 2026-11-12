#!/usr/bin/env python3
"""Fail the build when a page is left mostly empty or when text spills past the margin.

    python3 scripts/check-pagination.py _site/rl-notes.pdf
    python3 scripts/check-pagination.py _site/rl-notes.pdf --list   # for a baseline

Rules, in PostScript points and taken from the book's page template:

  * a page may not leave more than HOLE_LIMIT of empty space at its foot
  * content may not reach more than OVERFLOW_LIMIT below the text block

A few points of descent below the block are normal - the last line's descenders
sit there on any full page - so overflow starts a little further down.

Some pages are short by design - part dividers, chapter openers, chapter ends -
so the check holds a budget instead of an allowlist: pagination-budget.json
records how many pages may exceed the limit. A per-page list is fragile, because
the same page begins with a different line under a different TeX release; the
count is not. Adding a hole past the budget fails the build, and so does any
overflow, which has no budget at all.

Needs PyMuPDF: python3 -m pip install pymupdf
"""

import argparse
import json
import os
import re
import sys

try:
    import pymupdf as fitz
except ImportError:  # older wheels expose the same API as `fitz`
    try:
        import fitz
    except ImportError:
        print("check-pagination.py needs PyMuPDF: python3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(2)

BOTTOM = 738.0        # bottom of the text block
HOLE_LIMIT = 200.0    # allowed empty space at the foot of a page
OVERFLOW_LIMIT = 6.0  # descent below the block that counts as spilling over
HEADER_LIMIT = 45.0   # running headers sit above this
FOOTER_LIMIT = 760.0  # folio numbers sit below this

DEFAULT_BUDGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagination-budget.json")


def signature(page):
    """Identify a page by its first two lines, so entries survive a reflow.

    One line is not enough: every page of a chapter repeats the running header,
    and chapter-end pages repeat the chapter title.
    """
    found = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                found.append(re.sub(r"\s+", " ", text))
                if len(found) == 2:
                    return " / ".join(found)[:110]
    return found[0][:110] if found else "<blank page>"


def measure(page):
    """Return (bottom of the content, slack left above the block)."""
    bottoms = [
        block["bbox"][3]
        for block in page.get_text("dict")["blocks"]
        if block["bbox"][3] < FOOTER_LIMIT and block["bbox"][1] > HEADER_LIMIT
    ]
    bottom = max(bottoms) if bottoms else 0.0
    return bottom, BOTTOM - bottom


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--budget", default=DEFAULT_BUDGET)
    parser.add_argument("--max-holes", type=int, default=None)
    parser.add_argument("--list", action="store_true", help="print every page's slack and exit 0")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"missing PDF: {args.pdf}", file=sys.stderr)
        return 2

    budget = 0
    if os.path.isfile(args.budget):
        with open(args.budget) as handle:
            budget = int(json.load(handle).get("max_holes", 0))
    if args.max_holes is not None:
        budget = args.max_holes

    doc = fitz.open(args.pdf)
    try:
        pages = [(number, signature(page), *measure(page)) for number, page in enumerate(doc, start=1)]
    finally:
        doc.close()

    if args.list:
        for number, sig, bottom, slack in pages:
            print(f"p{number:>3}  slack={slack:7.1f}  bottom={bottom:6.1f}  {sig}")
        return 0

    overflows = [(n, sig, slack, bottom) for n, sig, bottom, slack in pages if slack < -OVERFLOW_LIMIT]
    holes = [(n, sig, slack) for n, sig, bottom, slack in pages if slack > HOLE_LIMIT]

    for number, sig, slack, bottom in overflows:
        print(f"::error file={args.pdf}::p{number}: content ends at {bottom:.1f}pt, past the {BOTTOM:.0f}pt block - {sig}")

    print(f"pages with more than {HOLE_LIMIT:.0f}pt of empty space: {len(holes)} (budget {budget})")
    for number, sig, slack in holes:
        print(f"  p{number}: {slack:.0f}pt - {sig}")
    if len(holes) > budget:
        print(f"::error file={args.pdf}::{len(holes)} pages leave more than {HOLE_LIMIT:.0f}pt empty, budget is {budget}")

    failed = overflows or len(holes) > budget
    print(f"\nchecked {len(pages)} pages: {len(overflows)} spilling past the margin, {len(holes)} over the hole limit")
    if failed:
        return 1
    if len(holes) < budget:
        print(f"budget can be tightened to {len(holes)} in pagination-budget.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
