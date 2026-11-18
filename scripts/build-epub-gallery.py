#!/usr/bin/env python3
"""Builds the epub figure list inside gallery.qmd from the html grid.

The gallery renders twice: an interactive grid of <picture> thumbnails for the
html build, and a plain list of images for the epub, which cannot follow links
into chapters that only exist as web pages. Both carry the same 42 captions, so
the grid is the single source of truth and the list is generated from it: edit a
caption in the grid, rerun this, and the two cannot drift.

The list is the block wrapped in `{.content-visible when-format="epub"}`, which
this finds in place and rewrites from the grid's <figure> blocks - path, alt
text, number and caption all come from there, so nothing in it is hand-edited.

Usage: python3 scripts/build-epub-gallery.py [--check]
       --check exits 1 if the committed list is out of date, without writing.
"""

import argparse
import pathlib
import re
import sys

GALLERY = pathlib.Path("gallery.qmd")

EPUB_OPEN = '::: {.content-visible when-format="epub"}'
# the epub list is inserted before the pdf-only summary when it is missing
PDF_OPEN = '::: {.content-visible when-format="pdf"}'
INTRO = (
    "Every diagram redrawn for these notes, numbered as it appears in the book "
    "(chapter.figure), with the caption used next to it in the text."
)

FIGURE = re.compile(r"<figure>(.*?)</figure>", re.S)
IMG = re.compile(r'<img src="([^"]+)" alt="([^"]*)"')
NUMBER = re.compile(r">Figure ([\d.]+)</a>\s*:\s*(.*?)</figcaption>", re.S)


def grid_entries(text: str):
    """(image path, alt text, figure number, caption) for each grid figure."""
    entries = []
    for block in FIGURE.findall(text):
        img, label = IMG.search(block), NUMBER.search(block)
        if not img or not label:
            continue
        # keep entities as written: the caption is markdown, not html
        caption = re.sub(r"<[^>]+>", "", label.group(2)).strip()
        entries.append((img.group(1), img.group(2), label.group(1), caption))
    return entries


def render(entries) -> str:
    lines = [EPUB_OPEN, "", INTRO, ""]
    for path, alt, number, caption in entries:
        lines += [f'![]({path}){{fig-alt="{alt}"}}', "", f"**Figure {number}**: {caption}", ""]
    lines += [":::", ""]
    return "\n".join(lines)


def replace_block(text: str, entries) -> str:
    """Swap the epub block for a freshly generated one, or add it if missing."""
    block = render(entries)
    if EPUB_OPEN in text:
        open_at = text.index(EPUB_OPEN)
        close_at = text.index("\n:::", open_at) + len("\n:::")
        tail = text[close_at:].lstrip("\n")
        return text[:open_at] + block + ("\n" + tail if tail else "")
    return text.replace(PDF_OPEN, block + PDF_OPEN, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the list is stale")
    args = parser.parse_args()

    text = GALLERY.read_text(encoding="utf-8")
    entries = grid_entries(text)
    if not entries:
        print("build-epub-gallery: found no gallery figures; is the grid still there?")
        return 2

    updated = replace_block(text, entries)
    if updated == text:
        print(f"build-epub-gallery: {len(entries)} figures, list is up to date")
        return 0
    if args.check:
        print(f"build-epub-gallery: the epub figure list does not match the grid's "
              f"{len(entries)} figures; run python3 scripts/build-epub-gallery.py")
        return 1
    GALLERY.write_text(updated, encoding="utf-8")
    print(f"build-epub-gallery: wrote the {len(entries)}-figure list from the grid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
