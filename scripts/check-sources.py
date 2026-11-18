#!/usr/bin/env python3
"""Check that the figure table and the gallery still match the book.

Two places restate what the book already knows about its figures: every row of
figures/SOURCES.md (number, chapter, full caption) and every card of the gallery
grid in gallery.qmd (number and the opening of the caption). Both go stale
without complaining -- a caption edited in one place, a figure dropped, a row
left behind, a card quoting text the book no longer prints -- and every one of
those still renders fine.

What is checked, row by row:
  - the row's PNG is in figures/
  - the row's [.qmd] link names a real chapter, the chapter that its figure
    number belongs to, holding the {#fig-...} anchor the link points at
  - the number is in the built book, and the caption matches what the book
    prints, word for word (math included, after undoing the build's markup)

across rows: no figure numbered twice, and no figure in the build without a row.

Then the gallery grid, against the same built figcaptions:
  - every card's number is still in the book, and no number has two cards
  - the card's caption is the book's own words, verbatim, from the start of the
    caption it prints: the grid shows each caption's opening, and anything else
    is text the chapters do not have
  - no figure in the book without a card

The grid is read by build-epub-gallery.py's own parser, so this check and the
EPUB list generator cannot disagree about what a card says. Nothing here runs in
CI; like the other checks it is one command.

Usage: python3 scripts/check-sources.py [--site _site] [--table figures/SOURCES.md]
                                       [--figures figures] [--gallery gallery.qmd]
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bookhtml  # noqa: E402  (needs the path above when run from elsewhere)

LINK = re.compile(r"\[`([^`]+)`\]\(([^)]+)\)")
LABEL = re.compile(r"\{#(fig-[A-Za-z0-9-]+)\}")
CHAPTER_FILE = re.compile(r"^ch(\d{2})-")
GRID_NUMBER = re.compile(r">Figure ([\d.]+)</a>")


def read_rows(table: str):
    """(line number, five cells) for each figure row, in table order."""
    for line_no, line in enumerate(table.splitlines(), 1):
        if not line.startswith("| [`"):
            continue
        yield line_no, [cell.strip() for cell in line.strip().strip("|").split("|")]


def grid_entries(text: str):
    """build-epub-gallery.py's parser, so the check sees the cards as it does."""
    reader = Path(__file__).resolve().parent / "build-epub-gallery.py"
    spec = importlib.util.spec_from_file_location("build_epub_gallery", reader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.grid_entries(text)


def grid_lines(text: str) -> dict[str, int]:
    """figure number -> the line of gallery.qmd that prints its card."""
    lines: dict[str, int] = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        for number in GRID_NUMBER.findall(line):
            lines.setdefault(number, line_no)
    return lines


def comparable(text: str) -> str:
    """A caption as plain comparable text: entities decoded, quotes folded.

    The grid is written as markdown inside an html block, so a straight `'`
    there is what the build writes as `’`; everything else -- including the
    `$...$` around math -- is compared as written.
    """
    text = html.unescape(text).replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", text).strip()


def check_gallery(gallery: Path, built: dict[str, str]) -> tuple[list[str], int]:
    """Problems in the gallery grid, and how many cards it has."""
    text = gallery.read_text(encoding="utf-8")
    entries = grid_entries(text)
    if not entries:
        return [f"{gallery}: found no gallery figures; is the grid still there?"], 0

    lines = grid_lines(text)
    problems = []
    seen: set[str] = set()
    for _, _, number, caption in entries:
        where = f"{gallery}:{lines[number]}" if number in lines else f"{gallery}: figure {number}"
        if number in seen:
            problems.append(f"{where}: figure {number} has a second card in the grid")
            continue
        seen.add(number)
        if number not in built:
            problems.append(f"{where}: figure {number} is not in the book, so the card is stale")
            continue
        full = comparable(bookhtml.caption_markdown(built[number]))
        lead = comparable(caption)
        if not lead:
            problems.append(f"{where}: the card for figure {number} has no caption")
        elif not full.startswith(lead) or (len(full) > len(lead) and full[len(lead)].isalnum()):
            problems.append(f"{where}: the caption for {number} is not how the book opens it: "
                            f"{bookhtml.first_difference(lead, full)}")

    for number in sorted(set(built) - seen, key=bookhtml.sort_key):
        problems.append(f"{gallery}: figure {number} is in the book but has no card in the grid")
    return problems, len(entries)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--table", default="figures/SOURCES.md")
    parser.add_argument("--figures", default="figures")
    parser.add_argument("--gallery", default="gallery.qmd")
    args = parser.parse_args()

    site, table_path, figures = Path(args.site), Path(args.table), Path(args.figures)
    gallery = Path(args.gallery)
    if not site.is_dir():
        print(f"check-sources: {site} does not exist; render the book first")
        return 2
    if not table_path.exists():
        print(f"check-sources: {table_path} does not exist")
        return 2
    if not gallery.exists():
        print(f"check-sources: {gallery} does not exist")
        return 2

    built = bookhtml.html_captions(site)
    problems = []

    def note(line_no: int, message: str) -> None:
        problems.append(f"{table_path}:{line_no}: {message}")

    seen: dict[str, int] = {}
    checked = 0
    for line_no, cells in read_rows(table_path.read_text(encoding="utf-8")):
        if len(cells) != 5:
            note(line_no, f"row has {len(cells)} cells, not 5 (a stray | in a caption?)")
            continue
        png_cell, chapter_cell, number, caption, links = cells
        checked += 1

        png = LINK.match(png_cell)
        if not png or not (figures / png.group(2)).exists():
            note(line_no, f"figure file {png.group(2) if png else png_cell!r} is missing")
        chapter = LINK.search(links)
        if not chapter:
            note(line_no, "row has no [.qmd] link to the chapter that uses the figure")
            number_ok = False
        else:
            qmd_path, _, anchor = chapter.group(2).partition("#")
            qmd = Path("chapters") / Path(qmd_path).name
            number_ok = True
            if not qmd.exists():
                note(line_no, f"links {qmd}, which is not a chapter file")
                number_ok = False
            else:
                source = qmd.read_text(encoding="utf-8")
                if anchor not in set(LABEL.findall(source)):
                    note(line_no, f"the anchor #{anchor} is not in {qmd}")
                chapter_no = CHAPTER_FILE.match(qmd.name)
                if chapter_no and int(chapter_no.group(1)) != int(number.split(".")[0]):
                    note(line_no, f"figure {number} belongs to chapter {number.split('.')[0]}, "
                                  f"but the row links {qmd}")
                    number_ok = False

        if number in seen:
            note(line_no, f"figure {number} is already in the table at line {seen[number]}")
        seen.setdefault(number, line_no)

        if number not in built:
            if number_ok:
                note(line_no, f"figure {number} is not in the built book, so the row is stale")
            continue
        expected = bookhtml.caption_markdown(built[number])
        given = " ".join(caption.split())
        if given != expected:
            note(line_no, f"caption for {number} has drifted at "
                          f"{bookhtml.first_difference(given, expected)}")

    for number in sorted(set(built) - set(seen), key=bookhtml.sort_key):
        problems.append(f"{table_path}: figure {number} is in the book but has no row in the table")

    gallery_problems, cards = check_gallery(gallery, built)
    problems += gallery_problems

    print(f"check-sources: {checked} row(s) and {cards} gallery card(s) "
          f"against {len(built)} figure(s) in {site}/")
    if not problems:
        print("  every row matches the book: file, chapter, anchor, number and caption")
        print("  every gallery card opens on the book's own words for its figure")
        return 0
    for problem in problems:
        print(f"  {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
