#!/usr/bin/env python3
"""Repair the EPUB's packaging after a render, so it passes EPUBCheck and stays lean.

Quarto and pandoc emit a few things that EPUB 3.3 does not allow, plus pandoc
duplicates every image referenced in both a chapter and the figure gallery:

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
  - duplicate binary media files (e.g. chapter figure + gallery figure): identical
    bytes are collapsed to a single canonical EPUB/media/* entry, XHTML src links
    are rewritten to it, and duplicate manifest <item> tags are removed.

Everything is idempotent: running it on an already repaired archive changes
nothing. It is wired into _quarto.yml as a post-render step, so `quarto render`
produces a conforming, deduplicated EPUB without a separate command.

Usage: python3 scripts/fix-epub.py [--epub _site/rl-notes.epub] [--lang en]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
import re
import sys
import tempfile
import zipfile
from pathlib import Path

TAG = re.compile(r"<(div|mfrac)\b[^>]*>")
HTML_TAG = re.compile(r"<html\b[^>]*>")
ITEM_TAG = re.compile(r'\s*<item\b[^>]*href="([^"]+)"[^>]*/>\s*')


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


def deduplicate_media(
    archive: zipfile.ZipFile,
    opf_name: str,
    opf: str,
    docs: dict[str, str],
) -> tuple[str, dict[str, str], set[str]]:
    """Collapse identical media files (by SHA-256) to one canonical archive path."""
    opf_dir = posixpath.dirname(opf_name)
    by_hash: dict[str, str] = {}
    remap: dict[str, str] = {}  # duplicate full archive path -> canonical archive path

    for name in sorted(archive.namelist()):
        if not name.startswith(posixpath.join(opf_dir, "media/") if opf_dir else "media/"):
            continue
        digest = hashlib.sha256(archive.read(name)).hexdigest()
        if digest in by_hash:
            remap[name] = by_hash[digest]
        else:
            by_hash[digest] = name

    if not remap:
        return opf, docs, set()

    # Rewrite relative src/href references inside XHTML documents
    updated_docs = {}
    for doc_name, body in docs.items():
        doc_dir = posixpath.dirname(doc_name)
        new_body = body
        for dup_path, canon_path in remap.items():
            dup_rel = posixpath.relpath(dup_path, doc_dir)
            canon_rel = posixpath.relpath(canon_path, doc_dir)
            new_body = new_body.replace(f'"{dup_rel}"', f'"{canon_rel}"')
        updated_docs[doc_name] = new_body

    # Remove duplicate <item> entries from OPF manifest
    dup_opf_hrefs = {posixpath.relpath(p, opf_dir) for p in remap}

    def drop_dup_item(match: re.Match) -> str:
        href = match.group(1)
        if href in dup_opf_hrefs:
            return "\n"
        return match.group(0)

    new_opf = ITEM_TAG.sub(drop_dup_item, opf)
    return new_opf, updated_docs, set(remap.keys())


def fix_opf(opf: str, docs: dict[str, str], lang: str) -> str:
    """Language, date, optional description/rights, and manifest mathml declarations."""
    opf = re.sub(r'xml:lang="[^"]*"', f'xml:lang="{lang}"', opf)
    opf = re.sub(r"<dc:language>[^<]*</dc:language>", f"<dc:language>{lang}</dc:language>", opf)

    modified = re.search(r'<meta property="dcterms:modified">([^<]+)</meta>', opf)
    if modified:
        opf = re.sub(
            r"<dc:date([^>]*)>[^<]*</dc:date>",
            lambda m: f"<dc:date{m.group(1)}>{modified.group(1)[:10]}</dc:date>",
            opf,
        )

    if "<dc:description>" not in opf:
        desc = (
            "    <dc:description>Independent personal study notes accompanying "
            "Sutton &amp; Barto, Reinforcement Learning: An Introduction (2nd ed., MIT Press, 2018; 2020 corrected edition)."
            "</dc:description>\n"
        )
        opf = opf.replace("</metadata>", f"{desc}  </metadata>", 1)

    if "<dc:rights>" not in opf:
        rights = (
            "    <dc:rights>Independent study notes by Chizoba Obasi (CC BY 4.0; code/scripts MIT). "
            "Textbook referenced: Sutton &amp; Barto (2020), CC BY-NC-ND 2.0."
            "</dc:rights>\n"
        )
        opf = opf.replace("</metadata>", f"{rights}  </metadata>", 1)

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


def rebuild(source: Path, replacements: dict[str, str], drop: set[str]) -> None:
    """Rewrite the archive, keeping `mimetype` first and uncompressed."""
    with zipfile.ZipFile(source) as src, tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / source.name
        with zipfile.ZipFile(target, "w") as dst:
            for info in src.infolist():
                if info.filename in drop:
                    continue
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
        dedup_opf, cleaned, dropped_media = deduplicate_media(archive, opf_name, opf, cleaned)

    replacements = {name: body for name, body in cleaned.items() if body != docs[name]}
    fixed_opf = fix_opf(dedup_opf, cleaned, args.lang)
    if fixed_opf != opf:
        replacements[opf_name] = fixed_opf

    if not replacements and not dropped_media:
        print("fix-epub: the archive already conforms; nothing to repair")
        return 0
    rebuild(epub, replacements, dropped_media)
    msg = f"fix-epub: repaired {len(replacements)} file(s)"
    if dropped_media:
        msg += f" and deduplicated {len(dropped_media)} media file(s)"
    print(f"{msg} in {epub.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
