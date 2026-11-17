#!/usr/bin/env python3
"""Check the built EPUB for the two ways it breaks silently.

An EPUB is XHTML, so an unclosed <br>, <img> or <source> makes readers show an
error page instead of the chapter, and a link to pages/chapters/*.html points at
a path that only exists in the web build. Both render fine in the HTML output,
so neither is visible until someone opens the book.

Usage: python3 scripts/check-epub.py [--epub _site/rl-notes.epub]
"""

import argparse
import io
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# any reference into the web build's chapter pages, in an href or a src
HTML_CHAPTER_LINK = re.compile(r'(?:href|src)="([^"]*chapters/[^"]*\.html(?:#[^"]*)?)"')


def check(epub: Path) -> int:
    with zipfile.ZipFile(epub) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith((".xhtml", ".html"))]
        if not names:
            print(f"check-epub: {epub} holds no xhtml; is it an EPUB?")
            return 2

        malformed, dead_links = [], []
        for name in sorted(names):
            text = archive.read(name).decode("utf-8", "replace")
            try:
                ET.fromstring(text)
            except ET.ParseError as e:
                malformed.append(f"{name}: {e}")
            for link in HTML_CHAPTER_LINK.findall(text):
                dead_links.append(f"{name} -> {link}")

    print(f"check-epub: {len(names)} xhtml chapter(s) in {epub.name}")
    problems = []
    if malformed:
        problems.append(f"{len(malformed)} not well-formed, so readers show an error "
                        f"page instead of the chapter:")
        problems += [f"    {m}" for m in malformed]
    if dead_links:
        problems.append(f"{len(dead_links)} link(s) into chapters/*.html, which do not "
                        f"exist inside an EPUB:")
        problems += [f"    {d}" for d in dead_links[:10]]
        if len(dead_links) > 10:
            problems.append(f"    ... and {len(dead_links) - 10} more")

    if not problems:
        print("  every chapter parses and no link points at the web build")
        return 0
    for p in problems:
        print(f"  BROKEN: {p}" if not p.startswith("    ") else f"  {p}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epub", default="_site/rl-notes.epub")
    args = parser.parse_args()

    epub = Path(args.epub)
    if not epub.exists():
        print(f"check-epub: {epub} does not exist; render the book first")
        return 2
    return check(epub)


if __name__ == "__main__":
    sys.exit(main())
