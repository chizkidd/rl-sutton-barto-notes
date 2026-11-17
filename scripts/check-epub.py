#!/usr/bin/env python3
"""Check the built EPUB for the ways it breaks silently.

An EPUB is XHTML, so an unclosed <br>, <img> or <source> makes readers show an
error page instead of the chapter. And because the book is built from sources
meant for the web, a link can point at something that only exists there: a
source file like chapter.qmd, a chapters/*.html page, or an anchor that used to
be in another document. All of those render perfectly as HTML and only fail
inside the reader.

What is checked, per document in the archive:
  - it parses as XML
  - every href and src resolves to a file inside the archive (absolute URLs are
    skipped; those open a web page and are meant to leave the book)
  - every #fragment, including one inside a relative link, names an id that
    exists in the document it lands in

Usage: python3 scripts/check-epub.py [--epub _site/rl-notes.epub]
"""

import argparse
import posixpath
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REFERENCE = re.compile(r'\b(?:href|src)="([^"]*)"')
ID = re.compile(r'\bid="([^"]+)"')
ABSOLUTE = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")


def is_web_path(target: str) -> bool:
    """A path that only exists in the web build, e.g. chapters/ch03-....html."""
    return target.endswith(".html") and "chapters/" in target


def check(epub: Path) -> int:
    try:
        archive = zipfile.ZipFile(epub)
    except zipfile.BadZipFile:
        print(f"check-epub: {epub} is not a zip archive; render the book first")
        return 2
    with archive:
        docs = sorted(n for n in archive.namelist() if n.lower().endswith((".xhtml", ".html")))
        if not docs:
            print(f"check-epub: {epub} holds no xhtml; is it an EPUB?")
            return 2

        present = set(archive.namelist())
        text = {name: archive.read(name).decode("utf-8", "replace") for name in docs}
        # every document's ids, so a link can be checked against its landing page
        ids = {name: set(ID.findall(body)) for name, body in text.items()}

        malformed, broken, web_paths, no_anchor = [], [], [], []
        for name in docs:
            try:
                ET.fromstring(text[name])
            except ET.ParseError as e:
                malformed.append(f"{name}: {e}")
                continue  # its references would only repeat the parse failure

            base = posixpath.dirname(name)
            for ref in REFERENCE.findall(text[name]):
                if ref.startswith(ABSOLUTE):
                    continue
                target, _, frag = ref.partition("#")
                target, frag = urllib.parse.unquote(target), urllib.parse.unquote(frag)

                if target:  # "#frag" alone points into this same document
                    landing = posixpath.normpath(posixpath.join(base, target))
                    if landing not in present:
                        entry = f"{name} -> {ref}"
                        (web_paths if is_web_path(target) else broken).append(entry)
                        continue
                else:
                    landing = name
                if frag and frag not in ids.get(landing, set()):
                    no_anchor.append(f"{name} -> {ref}")

    print(f"check-epub: {len(docs)} xhtml chapter(s) in {epub.name}")
    problems = []
    if malformed:
        problems.append((f"{len(malformed)} not well-formed, so readers show an error page "
                         f"instead of the chapter", malformed))
    if web_paths:
        problems.append((f"{len(web_paths)} link(s) into the web build's chapters/*.html, "
                         f"which do not exist inside an EPUB", web_paths))
    if broken:
        problems.append((f"{len(broken)} reference(s) point at a file that is not in the book",
                         broken))
    if no_anchor:
        problems.append((f"{len(no_anchor)} link(s) point at an anchor that does not exist "
                         f"in the document they land in", no_anchor))

    if not problems:
        print("  every chapter parses, every reference resolves, every anchor exists")
        return 0
    for title, entries in problems:
        print(f"  BROKEN: {title}:")
        for entry in entries[:10]:
            print(f"    {entry}")
        if len(entries) > 10:
            print(f"    ... and {len(entries) - 10} more")
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
