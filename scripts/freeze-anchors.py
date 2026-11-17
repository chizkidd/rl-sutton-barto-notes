#!/usr/bin/env python3
"""Freeze the anchor ids the site currently publishes onto the headings.

Pandoc derives a heading's id from its text, so renaming a heading silently
breaks every external link and bookmark to it. This takes the ids from the HTML
that is already built and writes them into the sources as explicit `{#id}`,
which is the only way a link can survive a rename.

It only touches headings that have no explicit id, and it refuses to change an
existing id.

Usage: python3 scripts/freeze-anchors.py [--site _site] [--dry-run]
"""

import argparse
import html
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^#{2,3}\s+(.*?)\s*$")
HTML_HEADING = re.compile(r"<h([23])\b[^>]*\bid=\"([^\"]+)\"[^>]*>(.*?)</h\1>", re.S)


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def numeric_prefix(title: str) -> str:
    m = re.match(r"^([\d.]+)\s+", title)
    return m.group(1) if m else ""


def ids_from_html(page: Path):
    """map (level, title-without-number) -> id, in document order"""
    out = {}
    text = page.read_text(encoding="utf-8")
    for m in HTML_HEADING.finditer(text):
        level, hid, inner = int(m.group(1)), m.group(2), strip_tags(m.group(3))
        title = re.sub(r"^[\d.]+\s*", "", inner).strip()
        out.setdefault((level, title), hid)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    site = Path(args.site)
    if not site.is_dir():
        print(f"freeze-anchors: {site} does not exist; render first")
        return 2

    total = changed = 0
    for qmd in sorted(Path("chapters").glob("ch*.qmd")):
        page = site / "chapters" / (qmd.stem + ".html")
        if not page.exists():
            print(f"  skip {qmd.name}: no built page")
            continue
        known = ids_from_html(page)
        lines = qmd.read_text(encoding="utf-8").split("\n")
        touched = 0
        for i, line in enumerate(lines):
            m = HEADING.match(line)
            if not m or "{#" in line:
                continue
            level = len(line) - len(line.lstrip("#"))
            title = m.group(1)
            title = re.sub(r"\{[^}]*\}$", "", m.group(1)).strip()
            key = (level, re.sub(r"^[\d.]+\s*", "", title).strip())
            hid = known.get(key)
            if not hid:
                continue
            total += 1
            lines[i] = f"{'#' * level} {title} {{#{hid}}}"
            touched += 1
        if touched:
            changed += touched
            if not args.dry_run:
                qmd.write_text("\n".join(lines), encoding="utf-8")
            print(f"  {qmd.name}: {touched} heading id(s) frozen")

    print(f"freeze-anchors: {'would freeze' if args.dry_run else 'froze'} {changed} of {total} headings without ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
