#!/usr/bin/env python3
"""Fail the build when a page is left mostly empty or when text spills past the margin.

    python3 scripts/check-pagination.py _site/rl-notes.pdf
    python3 scripts/check-pagination.py _site/rl-notes.pdf --list   # for a baseline

Rules, in PostScript points and taken from the book's page template:

  * a page may not leave more than HOLE_LIMIT of empty space at its foot
  * content may not reach more than OVERFLOW_LIMIT below the text block

A few points of descent below the block are normal - the last line's descenders
sit there on any full page - so overflow starts a little further down.

Pages that already broke the first rule when this check was added are recorded
in pagination-baseline.json keyed by their first line of text. They keep the
build green until someone fixes them; anything new fails. Remove an entry once
its page is fixed, and the check will start guarding it too.

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

DEFAULT_BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagination-baseline.json")


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
    parser.add_argument("--baseline", default=DEFAULT_BASELINE)
    parser.add_argument("--list", action="store_true", help="print every page's slack and exit 0")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"missing PDF: {args.pdf}", file=sys.stderr)
        return 2

    baseline = set()
    if os.path.isfile(args.baseline):
        with open(args.baseline) as handle:
            baseline = set(json.load(handle).get("holes", []))

    doc = fitz.open(args.pdf)
    try:
        pages = [(number, signature(page), *measure(page)) for number, page in enumerate(doc, start=1)]
    finally:
        doc.close()

    if args.list:
        for number, sig, bottom, slack in pages:
            print(f"p{number:>3}  slack={slack:7.1f}  bottom={bottom:6.1f}  {sig}")
        return 0

    holes, overflows = [], []
    for number, sig, bottom, slack in pages:
        if slack < -OVERFLOW_LIMIT:
            overflows.append((number, sig, slack, bottom))
        elif slack > HOLE_LIMIT and sig not in baseline:
            holes.append((number, sig, slack))

    for number, sig, slack, bottom in overflows:
        print(f"::error file={args.pdf}::p{number}: content ends at {bottom:.1f}pt, past the {BOTTOM:.0f}pt block - {sig}")
    for number, sig, slack in holes:
        print(f"::error file={args.pdf}::p{number}: {slack:.0f}pt of empty space at the foot - {sig}")

    if holes or overflows:
        print(f"\n{len(overflows)} page(s) spilling past the margin, {len(holes)} page(s) with >{HOLE_LIMIT:.0f}pt of empty space.")
        return 1

    used = {sig for _, sig, _, slack in pages if slack > HOLE_LIMIT}
    stale = sorted(baseline - used)
    print(f"checked {len(pages)} pages: no new holes, nothing past the margin")
    if stale:
        print(f"note: {len(stale)} baseline entr(y/ies) no longer apply and can be removed:")
        for sig in stale[:5]:
            print(f"  - {sig}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
