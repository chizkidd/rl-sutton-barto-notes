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

and across the package: the defects `fix-epub.py` repairs after a render, so a
regression shows up here instead of only in a full EPUBCheck run (which needs a
JDK and a jar that are not part of the repo):
  - `alt` on a <div>, which EPUB allows on images only
  - `displaystyle` on <mfrac>, which MathML allows on <mstyle> only
  - a blank `dc:date`
  - a `dc:language` that is not a language tag
  - a document that uses MathML while its manifest item omits `properties="mathml"`

These are validity rules, not rendering bugs -- a reader ignores every one of
them -- so they are reported as invalid rather than broken. The repair in
fix-epub.py is still what makes the archive conform; this just fails first.

The link rules are what check-refs.cjs does for _site/, so they live in
linkcheck.py and this script supplies only the archive: the documents it holds,
and the ids inside them.

Usage: python3 scripts/check-epub.py [--epub _site/rl-notes.epub]
"""

import argparse
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import linkcheck  # noqa: E402  (needs the path above when run from elsewhere)

DIV = re.compile(r"<div\b[^>]*>")
MFRAC = re.compile(r"<mfrac\b[^>]*>")
ITEM = re.compile(r"<item\b[^>]*>")
ATTRIBUTE = re.compile(r'([\w:.-]+)="([^"]*)"')
LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*$")
DC_LANGUAGE = re.compile(r"<dc:language\b[^>]*>([^<]*)</dc:language>")
DC_DATE = re.compile(r"<dc:date\b[^>]*>([^<]*)</dc:date>")
ALT = re.compile(r'\salt="')
DISPLAYSTYLE = re.compile(r'\sdisplaystyle="')


def manifest(opf_name: str, opf: str) -> dict[str, dict[str, str]]:
    """href resolved inside the archive -> that item's attributes."""
    items = {}
    for tag in ITEM.findall(opf):
        attributes = dict(ATTRIBUTE.findall(tag))
        href = attributes.get("href")
        if href:
            path = posixpath.normpath(posixpath.join(posixpath.dirname(opf_name), unquote(href)))
            items[path] = attributes
    return items


def conformance(opf_name: str, opf: str, docs: dict[str, str]) -> list[tuple[str, list[str]]]:
    """(title, entries) for each packaging defect, in the order fix-epub repairs them."""
    alt, displaystyle = [], []
    for name, body in docs.items():
        alt += [f"{name}: {tag}" for tag in DIV.findall(body) if ALT.search(tag)]
        displaystyle += [f"{name}: {tag}" for tag in MFRAC.findall(body) if DISPLAYSTYLE.search(tag)]

    problems = []
    if alt:
        problems.append((f"{len(alt)} <div> carr{'ies' if len(alt) == 1 else 'y'} alt, "
                         f"which EPUB allows on images only", alt))
    if displaystyle:
        problems.append((f"{len(displaystyle)} <mfrac> carr{'ies' if len(displaystyle) == 1 else 'y'} "
                         f"displaystyle, which MathML allows on <mstyle> only", displaystyle))

    language = DC_LANGUAGE.search(opf)
    if not language:
        problems.append((f"{opf_name} has no dc:language", [opf_name]))
    elif not LANGUAGE_TAG.match(language.group(1).strip()):
        problems.append((f'dc:language is "{language.group(1).strip()}", not a language tag',
                         [f"{opf_name}: <dc:language>{language.group(1)}</dc:language>"]))

    date = DC_DATE.search(opf)
    if not date:
        problems.append((f"{opf_name} has no dc:date, so the book has no publication date",
                         [opf_name]))
    elif not date.group(1).strip():
        problems.append((f"dc:date is blank, which EPUBCheck reports as a zero-length date",
                         [f"{opf_name}: <dc:date> is empty"]))

    items = manifest(opf_name, opf)
    undeclared = [
        name for name, body in docs.items()
        if "<math" in body and "mathml" not in items.get(name, {}).get("properties", "").split()
    ]
    if undeclared:
        problems.append((f"{len(undeclared)} document(s) use MathML but their manifest item "
                         f'does not declare properties="mathml"', undeclared))
    return problems


def show(kind: str, groups: list[tuple[str, list[str]]]) -> None:
    for title, entries in groups:
        print(f"  {kind}: {title}:")
        for entry in entries[:10]:
            print(f"    {entry}")
        if len(entries) > 10:
            print(f"    ... and {len(entries) - 10} more")


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
        ids = {name: linkcheck.document_ids(body) for name, body in text.items()}

        malformed = []
        found = {linkcheck.WEB_ONLY: [], linkcheck.MISSING: [], linkcheck.ANCHOR: []}
        for name in docs:
            try:
                ET.fromstring(text[name])
            except ET.ParseError as e:
                malformed.append(f"{name}: {e}")
                continue  # its references would only repeat the parse failure

            for finding in linkcheck.check_document(
                name, text[name], ids, lambda landing: landing in present, web_only_error=True
            ):
                found[finding.kind].append(f"{name} -> {finding.ref}")
        web_paths, broken, no_anchor = found[linkcheck.WEB_ONLY], found[linkcheck.MISSING], found[linkcheck.ANCHOR]

        opf_name = next((n for n in archive.namelist() if n.endswith(".opf")), None)
        opf = archive.read(opf_name).decode("utf-8") if opf_name else ""

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

    invalid = [(f"the archive has no .opf, so it is not an EPUB package", [epub.name])] if not opf_name \
        else conformance(opf_name, opf, text)

    if not problems and not invalid:
        print("  every chapter parses, every reference resolves, every anchor exists")
        print("  nothing for fix-epub.py to repair: packaging passes the EPUBCheck rules it fixes")
        return 0
    show("BROKEN", problems)
    show("INVALID", invalid)
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
