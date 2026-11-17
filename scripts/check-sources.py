#!/usr/bin/env python3
"""Check that the figure table in figures/SOURCES.md still matches the book.

The table restates what the book already knows -- each figure's number, its
chapter, and its full caption -- so it goes stale without complaining: a caption
edited in one place, a figure dropped, a row left behind, a row moved to the
wrong chapter. Every one of those still renders fine; only the table is wrong.

What is checked, row by row:
  - the row's PNG is in figures/
  - the row's [.qmd] link names a real chapter, the chapter that its figure
    number belongs to, holding the {#fig-...} anchor the link points at
  - the number is in the built book, and the caption matches what the book
    prints, word for word (math included, after undoing the build's markup)

and across rows: no figure numbered twice, and no figure in the build without a
row. Nothing here runs in CI; like the other checks it is one command.

Usage: python3 scripts/check-sources.py [--site _site] [--table figures/SOURCES.md] [--figures figures]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bookhtml  # noqa: E402  (needs the path above when run from elsewhere)

LINK = re.compile(r"\[`([^`]+)`\]\(([^)]+)\)")
LABEL = re.compile(r"\{#(fig-[A-Za-z0-9-]+)\}")
CHAPTER_FILE = re.compile(r"^ch(\d{2})-")


def read_rows(table: str):
    """(line number, five cells) for each figure row, in table order."""
    for line_no, line in enumerate(table.splitlines(), 1):
        if not line.startswith("| [`"):
            continue
        yield line_no, [cell.strip() for cell in line.strip().strip("|").split("|")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--table", default="figures/SOURCES.md")
    parser.add_argument("--figures", default="figures")
    args = parser.parse_args()

    site, table_path, figures = Path(args.site), Path(args.table), Path(args.figures)
    if not site.is_dir():
        print(f"check-sources: {site} does not exist; render the book first")
        return 2
    if not table_path.exists():
        print(f"check-sources: {table_path} does not exist")
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

    print(f"check-sources: {checked} row(s) against {len(built)} figure(s) in {site}/")
    if not problems:
        print("  every row matches the book: file, chapter, anchor, number and caption")
        return 0
    for problem in problems:
        print(f"  {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
