#!/usr/bin/env python3
"""Resolve the references in a rendered document, for the site and for the EPUB.

check-refs.cjs walks _site/ and check-epub.py walks an archive, but the rule for
a reference is the same in both: resolve it against the directory of the document
it appears in, percent-decode it, then require that the file exists and that any
#fragment names an id in the document it lands in. That rule lives here once, so
the two containers cannot drift apart.

check-refs.cjs runs this file for the built pages; check-epub.py imports
check_document() and supplies the archive's own notion of "present".

Usage: python3 scripts/linkcheck.py [--site _site] [--json]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import re
import sys
import urllib.parse
from typing import Callable, Iterable, NamedTuple

REFERENCE = re.compile(r'\b(?:href|src)="([^"]*)"')
ID = re.compile(r'\bid="([^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")

# Other render passes and the deploy workflow write these, so a --to html render
# legitimately does not have them; their absence says nothing about the site.
OTHER_FORMATS = (".pdf", ".epub", ".tsv")

MISSING = "missing"  # lands on a file that is not in the container
ANCHOR = "anchor"  # lands on a file, but its #fragment names no id there
WEB_ONLY = "web-only"  # points into the web build, which an EPUB does not carry
SKIPPED = "skipped"  # absent, but another step is expected to produce it


class Finding(NamedTuple):
    kind: str
    ref: str
    offset: int
    landing: str | None


def document_ids(text: str) -> set[str]:
    """The anchor targets a reference can land on in one document."""
    return set(ID.findall(text))


def leaves_container(ref: str) -> bool:
    """True for references that open something outside the book."""
    return not ref or ref.startswith(EXTERNAL) or ref.startswith("//")


def resolve(base: str, ref: str) -> tuple[str | None, str] | None:
    """(landing document, fragment) for one reference, or None if it is not ours.

    A bare "#fragment" points into the document it appears in and comes back with
    landing None.
    """
    target, _, fragment = ref.partition("#")
    target, fragment = urllib.parse.unquote(target), urllib.parse.unquote(fragment)
    landing = posixpath.normpath(posixpath.join(base, target)) if target else None
    return landing, fragment


def is_web_build_path(landing: str) -> bool:
    """A page that only exists in the web build, e.g. chapters/ch03-....html."""
    return landing.endswith(".html") and "chapters/" in landing


def check_document(
    name: str,
    text: str,
    ids: dict[str, set[str]],
    exists: Callable[[str], bool],
    *,
    skip: Iterable[str] = (),
    web_only_error: bool = False,
) -> list[Finding]:
    """Every reference in `text` that does not resolve, in document order.

    name    : the document's path inside the container, posix and relative
    ids     : the whole container's anchors, keyed the same way as `name`
    exists  : callable(landing) -> whether that file is in the container
    skip    : extensions whose absence is not a failure (a partial render)
    web_only_error : a chapters/*.html reference is its own kind of failure, as
                     it is inside an EPUB, not in the site where it is correct
    """
    findings: list[Finding] = []
    base = posixpath.dirname(name)
    skip = tuple(extension.lower() for extension in skip)
    for match in REFERENCE.finditer(text):
        ref = match.group(1)
        if leaves_container(ref):
            continue
        resolved = resolve(base, ref)
        if resolved is None:
            continue
        landing, fragment = resolved

        if landing is not None and not exists(landing):
            extension = posixpath.splitext(landing)[1].lower()
            if web_only_error and is_web_build_path(landing):
                kind = WEB_ONLY
            elif extension in skip:
                kind = SKIPPED
            else:
                kind = MISSING
            findings.append(Finding(kind, ref, match.start(), landing))
            continue

        owner = landing if landing is not None else name
        if fragment and fragment not in ids.get(owner, ()):
            findings.append(Finding(ANCHOR, ref, match.start(), landing))
    return findings


def scan(root: pathlib.Path) -> dict:
    """Check a built HTML tree: every page's references, keyed by path in root."""
    pages = sorted(p for p in root.rglob("*.html") if p.is_file())
    texts = {p.relative_to(root).as_posix(): p.read_text("utf-8", "replace") for p in pages}
    ids = {name: document_ids(text) for name, text in texts.items()}
    exists = lambda landing: (root / landing).exists()

    problems, links, skipped = [], 0, 0
    for name, text in texts.items():
        links += sum(1 for m in REFERENCE.finditer(text) if not leaves_container(m.group(1)))
        for finding in check_document(name, text, ids, exists, skip=OTHER_FORMATS):
            if finding.kind == SKIPPED:
                skipped += 1
                continue
            line = text.count("\n", 0, finding.offset) + 1
            if finding.kind == ANCHOR:
                message = f'link "{finding.ref}" points at an anchor that does not exist'
            else:
                message = f'link "{finding.ref}" does not resolve to a file in {root}/'
            problems.append({"file": f"{root}/{name}", "line": line, "message": message})
    return {"root": str(root), "pages": len(pages), "links": links,
            "skipped": skipped, "problems": problems}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.site)
    if not root.is_dir():
        if args.json:
            print(json.dumps({"root": str(root), "absent": True, "pages": 0, "links": 0,
                              "skipped": 0, "problems": []}))
        else:
            print(f"linkcheck: no {root}/ build, so the built-page link check was skipped")
        return 0

    report = scan(root)
    if args.json:
        print(json.dumps(report))
    else:
        print(f"linkcheck: {report['links']} links across {report['pages']} built pages checked")
        if report["skipped"]:
            print(f"  ({report['skipped']} link(s) to pdf/epub/tsv skipped: "
                  f"a full render or the deploy workflow produces those)")
        for p in report["problems"]:
            print(f"  {p['file']}:{p['line']}: {p['message']}")
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
