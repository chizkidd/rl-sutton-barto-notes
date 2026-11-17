#!/usr/bin/env python3
"""Freeze the anchor ids the site publishes onto the headings that produce them.

Pandoc derives a heading id from its text, so renaming a heading silently
breaks every external link to it. This takes the ids from the HTML that is
already built and writes them into the sources as explicit `{#id}`.

Matching is positional, not by title: the same heading text appears many times
("Takeaways", "Example 1", "Summary"), and matching titles across a file hands
several headings the same id. Both lists are in document order, so they are
aligned as sequences and compared title by title; any heading that does not
line up is skipped rather than guessed at.

Usage: python3 scripts/freeze-anchors.py [--site _site] [--dry-run] [--levels 2,3]
"""

import argparse
import difflib
import html
import re
import sys
from pathlib import Path

SRC_HEADING = re.compile(r"^(#{2,4})\s+(.*?)\s*$")
HTML_HEADING = re.compile(r"<h([2-4])\b[^>]*\bid=\"([^\"]+)\"[^>]*>(.*?)</h\1>", re.S)


def norm(text: str) -> str:
    """Heading text as it appears in both lists: no tags, no number, no math."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\u00a0", " ")
    text = re.sub(r"^\s*\d+(\.\d+)*\.?\s*", "", text)  # leading section number
    text = re.sub(r"\$\$?.*?\$\$?", " ", text)  # math renders differently on each side
    text = re.sub(r"[^A-Za-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def html_headings(page: Path):
    out = []
    for m in HTML_HEADING.finditer(page.read_text(encoding="utf-8")):
        out.append((int(m.group(1)), norm(m.group(3)), m.group(2)))
    return out


def source_headings(lines, levels):
    """(index, level, title, has_id) for every heading in the file."""
    out = []
    fenced = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = SRC_HEADING.match(line)
        if not m:
            continue
        level = len(m.group(1))
        if level not in levels:
            continue
        title = re.sub(r"\{[^}]*\}\s*$", "", m.group(2)).strip()
        out.append((i, level, title, "{#" in line))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--levels", default="2,3", help="comma separated heading levels to freeze")
    args = parser.parse_args()
    levels = {int(x) for x in args.levels.split(",")}

    site = Path(args.site)
    if not site.is_dir():
        print(f"freeze-anchors: {site} does not exist; render the book first")
        return 2

    total = frozen = skipped = 0
    for qmd in sorted(Path("chapters").glob("ch*.qmd")):
        page = site / "chapters" / (qmd.stem + ".html")
        if not page.exists():
            print(f"  skip {qmd.name}: no built page")
            continue

        built = [h for h in html_headings(page) if h[0] in levels]
        lines = qmd.read_text(encoding="utf-8").split("\n")
        source = source_headings(lines, levels)
        if not built or not source:
            continue

        # Align the two sequences, then map positions one to one.
        matcher = difflib.SequenceMatcher(a=[h[1] for h in built], b=[norm(h[2]) for h in source])
        changed = 0
        for block in matcher.get_matching_blocks():
            for k in range(block.size):
                b_level, b_title, b_id = built[block.a + k]
                line_index, s_level, s_title, has_id = source[block.b + k]
                total += 1
                if has_id:
                    continue
                if b_level != s_level:
                    skipped += 1
                    continue
                lines[line_index] = f"{'#' * s_level} {s_title} {{#{b_id}}}"
                frozen += 1
                changed += 1
        if changed:
            if not args.dry_run:
                qmd.write_text("\n".join(lines), encoding="utf-8")
            print(f"  {qmd.name}: {changed} id(s) {'would be ' if args.dry_run else ''}written")

    print(
        f"freeze-anchors: {'would freeze' if args.dry_run else 'froze'} {frozen} of {total} headings "
        f"({skipped} skipped where the lists disagreed)"
    )

    # The book renders as one Pandoc document, so ids must be unique across all
    # chapters, not just within one: two chapters sharing {#takeaways} build
    # fine page by page and colllide only in the PDF and EPUB.
    seen, collisions = {}, []
    for qmd in sorted(Path("chapters").glob("ch*.qmd")):
        for m in re.finditer(r"\{#[A-Za-z0-9-]+\}", qmd.read_text(encoding="utf-8")):
            ident = m.group(0)[2:-1]
            if ident in seen:
                collisions.append(f"#{ident} in {seen[ident]} and {qmd.name}")
            seen[ident] = qmd.name
    if collisions:
        print(f"  {len(collisions)} id(s) used in more than one chapter:")
        for c in collisions:
            print(f"    {c}")
        return 1
    print(f"  {len(seen)} ids, no duplicates across the book")
    return 0


if __name__ == "__main__":
    sys.exit(main())
