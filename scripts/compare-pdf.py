#!/usr/bin/env python3
"""Compare two builds of the book and report how they differ.

    python3 scripts/compare-pdf.py PINNED.pdf LATEST.pdf

Exit codes:
    0  no drift - same page count, same text, same rendered pages
    2  drift detected (the caller turns this into a warning)
    1  could not compare (missing input or PyMuPDF unavailable)

Needs PyMuPDF (`pip install pymupdf`). Text is compared page by page after
collapsing whitespace; pages are also rasterised at a low DPI and hashed, so a
shift that leaves the words intact is still caught.
"""

import difflib
import hashlib
import os
import re
import sys

try:
    import pymupdf as fitz
except ImportError:  # older wheels expose the same API as `fitz`
    try:
        import fitz
    except ImportError:
        print("compare-pdf.py needs PyMuPDF: python3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)


def pages_text(doc):
    """One list of cleaned lines per page, so a diff can point at a real line."""
    pages = []
    for page in doc:
        lines = [re.sub(r"\s+", " ", line).strip() for line in page.get_text().splitlines()]
        pages.append([line for line in lines if line])
    return pages


def pages_pixels(doc, dpi=60):
    return {
        number: hashlib.sha256(page.get_pixmap(dpi=dpi).samples).hexdigest()[:12]
        for number, page in enumerate(doc, start=1)
    }


def first_difference(left, right):
    for index, (a, b) in enumerate(zip(left, right), start=1):
        if a != b:
            return index
    if len(left) != len(right):
        return min(len(left), len(right)) + 1
    return None


def main(argv):
    if len(argv) != 3:
        print("usage: compare-pdf.py PINNED.pdf LATEST.pdf", file=sys.stderr)
        return 1
    pinned_path, latest_path = argv[1], argv[2]
    for path in (pinned_path, latest_path):
        if not os.path.isfile(path):
            print(f"missing input: {path}", file=sys.stderr)
            return 1

    pinned, latest = fitz.open(pinned_path), fitz.open(latest_path)
    try:
        pinned_text, latest_text = pages_text(pinned), pages_text(latest)
        pinned_pixels, latest_pixels = pages_pixels(pinned), pages_pixels(latest)
    finally:
        pinned.close()
        latest.close()

    text_page = first_difference(pinned_text, latest_text)
    pixel_pages = sorted(
        page for page, digest in pinned_pixels.items() if latest_pixels.get(page) != digest
    )
    drift = bool(text_page or pixel_pages or len(pinned_text) != len(latest_text))

    print(f"### Verdict: {'**DRIFT**' if drift else 'no drift'}")
    print()
    print("| | pinned | latest |")
    print("| --- | --- | --- |")
    print(f"| pages | {len(pinned_text)} | {len(latest_text)} |")
    print(f"| text | {'identical' if text_page is None and len(pinned_text) == len(latest_text) else 'differs'} | |")
    print(f"| rendered pages differing | {len(pixel_pages)} of {len(pinned_pixels)} | |")
    print()

    if text_page is not None:
        print(f"First page whose text differs: **{text_page}**")
        print()
        left = pinned_text[text_page - 1] if text_page <= len(pinned_text) else []
        right = latest_text[text_page - 1] if text_page <= len(latest_text) else []
        diff = list(difflib.unified_diff(left, right, "pinned", "latest", n=1, lineterm=""))
        print("```diff")
        for line in diff[:16]:
            print(line[:220])
        if len(diff) > 16:
            print(f"... {len(diff) - 16} more diff lines")
        print("```")
        print()

    if pixel_pages:
        shown = ", ".join(str(page) for page in pixel_pages[:20])
        more = " ..." if len(pixel_pages) > 20 else ""
        print(f"Pages that render differently: {shown}{more}")
        print()
        print("Identical words can still move or reflow; those pages are listed above.")
        print()

    if not drift:
        print("The book renders identically with the latest toolchain.")

    return 2 if drift else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
