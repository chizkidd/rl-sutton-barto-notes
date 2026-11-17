#!/usr/bin/env python3
"""Repair the EPUB's packaging after a render, so it passes EPUBCheck.

Quarto and pandoc emit a few things that EPUB 3.3 does not allow. None of them
break a reader, which is why the book looked fine for so long; they are still
validation errors, and every one of them is either a no-op for readers or
metadata pandoc left blank:

  - `alt` on the figure <div>. Quarto copies `fig-alt` onto the div as well as
    the <img>; `alt` only means anything on an image, so readers ignore it.
    The <img>'s own alt is kept.
  - `displaystyle` on <mfrac>. MathML allows it on <mstyle> only, so no engine
    reads it on a fraction; it is dropped rather than moved, since moving it
    would change how the fraction is typeset.
  - `dc:language`/`xml:lang` "C", which pandoc uses when it is given no
    language, is not a language tag (the book is in English). Setting `lang` in
    _quarto.yml would fix this too, but it reaches LaTeX and repaginates the
    PDF, so the archive is corrected here and the other formats are left alone.
  - an empty `dc:date`; the publication date is taken from the
    `dcterms:modified` timestamp, which Quarto always writes.
  - the nav document uses MathML in a TOC entry but its manifest item does not
    declare the `mathml` property.

Everything is idempotent: running it on an already repaired archive changes
nothing. It is wired into _quarto.yml as a post-render step, so `quarto render`
produces a conforming EPUB without a separate command. To check the result you
need a JDK and EPUBCheck, which are not part of the repo:

  java -jar epubcheck.jar _site/rl-notes.epub

Usage: python3 scripts/fix-epub.py [--epub _site/rl-notes.epub] [--lang en]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

TAG = re.compile(r"<(div|mfrac)\b[^>]*>")
HTML_TAG = re.compile(r"<html\b[^>]*>")
MATHML_ITEM = re.compile(r'<item\b[^>]*href="([^"]+)"[^>]*/>')


def clean_markup(text: str, lang: str) -> str:
    """Drop the two attributes EPUB forbids and set the document language."""

    def strip(match: re.Match) -> str:
        tag = match.group(0)
        if match.group(1) == "div":
            return re.sub(r'\s+alt="[^"]*"', "", tag)
        return re.sub(r'\s+displaystyle="[^"]*"', "", tag)

    text = TAG.sub(strip, text)

    def retag(match: re.Match) -> str:
        tag = match.group(0)
        for attribute in ("lang", "xml:lang"):
            tag = re.sub(rf'{attribute}="[^"]*"', f'{attribute}="{lang}"', tag)
        return tag

    return HTML_TAG.sub(retag, text)


def fix_opf(opf: str, docs: dict[str, str], lang: str) -> str:
    """Language, date and the manifest's mathml declarations."""
    opf = re.sub(r'xml:lang="[^"]*"', f'xml:lang="{lang}"', opf)
    opf = re.sub(r"<dc:language>[^<]*</dc:language>", f"<dc:language>{lang}</dc:language>", opf)

    modified = re.search(r'<meta property="dcterms:modified">([^<]+)</meta>', opf)
    if modified:
        opf = re.sub(
            r"<dc:date([^>]*)>[^<]*</dc:date>",
            lambda m: f"<dc:date{m.group(1)}>{modified.group(1)[:10]}</dc:date>",
            opf,
        )

    # any content document that carries MathML must say so in its manifest item
    for href, body in docs.items():
        if "<math" not in body:
            continue
        name = href.split("/")[-1]
        pattern = re.compile(r'(<item\b[^>]*href="[^"]*' + re.escape(name) + r'"[^>]*?)(/?>)')

        def declare(m: re.Match) -> str:
            tag = m.group(1)
            properties = re.search(r'properties="([^"]*)"', tag)
            if properties:
                if "mathml" in properties.group(1):
                    return m.group(0)
                return tag.replace(properties.group(0), f'properties="{properties.group(1)} mathml"') + m.group(2)
            return f'{tag} properties="mathml"{m.group(2)}'

        opf = pattern.sub(declare, opf)
    return opf


def rebuild(source: Path, replacements: dict[str, str]) -> None:
    """Rewrite the archive, keeping `mimetype` first and uncompressed."""
    with zipfile.ZipFile(source) as src, tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / source.name
        with zipfile.ZipFile(target, "w") as dst:
            for info in src.infolist():
                data = src.read(info.filename)
                if info.filename in replacements:
                    data = replacements[info.filename].encode("utf-8")
                entry = zipfile.ZipInfo(info.filename, info.date_time)
                entry.external_attr = info.external_attr
                entry.compress_type = zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED
                dst.writestr(entry, data)
        source.write_bytes(target.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epub", default=str(Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site")) / "rl-notes.epub"))
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()

    epub = Path(args.epub)
    if not epub.exists():
        print(f"fix-epub: {epub} does not exist; nothing to repair")
        return 0

    with zipfile.ZipFile(epub) as archive:
        names = archive.namelist()
        opf_name = next((n for n in names if n.endswith(".opf")), None)
        if opf_name is None:
            print(f"fix-epub: {epub} holds no .opf; is it an EPUB?")
            return 2
        docs = {
            name: archive.read(name).decode("utf-8")
            for name in names
            if name.lower().endswith((".xhtml", ".html"))
        }
        opf = archive.read(opf_name).decode("utf-8")

    cleaned = {name: clean_markup(body, args.lang) for name, body in docs.items()}
    replacements = {name: body for name, body in cleaned.items() if body != docs[name]}
    fixed_opf = fix_opf(opf, cleaned, args.lang)
    if fixed_opf != opf:
        replacements[opf_name] = fixed_opf

    if not replacements:
        print("fix-epub: the archive already conforms; nothing to repair")
        return 0
    rebuild(epub, replacements)
    print(f"fix-epub: repaired {len(replacements)} file(s) in {epub.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
