# Extras

Each of these is a one-command tool. The checks are local-only — none of them run in CI. Two of the generators do: the deploy workflow runs `export-anki.cjs` so the downloadable deck matches the book, and `_quarto.yml` runs `fix-epub.py` after every render.

```bash
node scripts/export-anki.cjs       # bullets -> Anki cloze deck (dist/anki/rl-notes.tsv)
python3 scripts/check-parity.py    # compare the built HTML and PDF for drift
python3 scripts/check-epub.py      # epub: XHTML, links, anchors, packaging rules fix-epub.py repairs
python3 scripts/check-sources.py   # figures/SOURCES.md and the gallery grid against the built book
node scripts/check-refs.cjs        # dead citations, figure refs, gallery anchors, then linkcheck.py
node scripts/build-notation.cjs    # regenerate notation.qmd
python3 scripts/build-epub-gallery.py  # rebuild the epub figure list from the gallery grid
python3 scripts/fix-epub.py        # repair the epub's packaging (also a post-render step)
python3 scripts/make-webp.py       # WebP copies of the figures for the gallery
python3 scripts/freeze-anchors.py  # write the built heading ids into the chapters
```

**Notation index** — `notation.qmd` maps 24 symbols to the section that defines them and counts the sections that use them. It is generated from the sources, so the locations cannot go stale; the descriptions are hand-written.

**Figure gallery** — `gallery.qmd` renders an interactive grid of thumbnails for the HTML build and a plain figure list for the EPUB, which cannot follow links into pages that only exist as HTML. Only the grid is hand-written: `build-epub-gallery.py` regenerates the list from it (path, alt text, number and caption), so a caption is edited in one place. `--check` reports a stale list instead of writing. Each card opens on the caption the chapter prints for that figure, word for word, and `check-sources.py` holds it to that.

**Parity check** — `check-parity.py` compares section numbers and the full text of every figure caption between `_site/` and `rl-notes.pdf`, because the two formats are configured separately (`number-depth: 3` against `secnumdepth 2`) and drift silently. Captions are compared word for word, so changing a single word in a caption fails the check; math is dropped because the HTML holds TeX source and the PDF typeset glyphs.

**EPUB check** — `check-epub.py` unzips `_site/rl-notes.epub` and fails if any chapter is not well-formed XHTML (an unclosed `<br>`, `<img>` or `<source>` makes readers show an error page instead of the chapter), if any `href` or `src` does not resolve to a file inside the archive (a `.qmd` source path or a `chapters/*.html` page looks fine on the web and is missing from the book), or if any `#fragment` names an id that the document it lands in does not have. None of those show up until the book is opened in a reader. The last two rules are `linkcheck.py`, the same code `check-refs.cjs` runs against `_site/`, so a link is judged the same way on the site and inside the archive; this script supplies only the documents and anchors of the zip. It also fails on the five packaging defects `fix-epub.py` repairs — `alt` on a `<div>`, `displaystyle` on `<mfrac>`, a blank or missing `dc:date`, a `dc:language` that is not a language tag, and a document using MathML whose manifest item omits `properties="mathml"` — reported as INVALID rather than BROKEN, since a reader ignores all five. That way a regression is caught by the one Python command, with no JDK or EPUBCheck jar.

**Figure table check** — `check-sources.py` holds `figures/SOURCES.md` to the build. For every row it wants the PNG in `figures/`, a chapter link whose `{#fig-…}` anchor is really in that chapter and whose number belongs to it, a figure number the book still has, and the caption the book prints word for word — math included, since the comparison undoes the build's markup rather than dropping it. It also reports a figure in the book with no row, and a number with two. The same pass checks the gallery grid in `gallery.qmd`, which restates each caption's opening: every card must start with the book's own words for its figure, and a card the book has no figure for, two cards for one figure, or a figure with no card are all reported. The grid is read by `build-epub-gallery.py`'s parser, so the check and the EPUB list generator cannot disagree about what a card says. The captions come from `bookhtml.py`, the same reader `check-parity.py` uses, so "what the book says" is defined once.

**EPUB conformance** — `check-epub.py` above is structural; it cannot tell you whether the archive is *valid*. EPUBCheck can, and the built EPUB now passes it with 0 fatals, 0 errors, 0 warnings, 0 infos (EPUB 3.3 rules). Reaching that took repairing what Quarto and pandoc emit: `alt` copied onto the figure `<div>` (33 of them), `displaystyle` on `<mfrac>` (15), a `dc:language` of `C` from the build locale, an empty `dc:date`, and a nav item using MathML without declaring it in the manifest. None of those break a reader, and every attribute dropped is one no renderer honours, so nothing looks different. `fix-epub.py` does it after each render — `_quarto.yml` lists it under `project: post-render` — and is idempotent. Doing it there rather than with `lang: en` is deliberate: `lang` also reaches LaTeX and repaginates the PDF. `check-epub.py` fails on those same five defects, so the repair cannot silently stop being needed, or stop being applied, without a local check noticing. Running the full audit yourself still needs a JDK and the EPUBCheck jar (`java -jar epubcheck.jar _site/rl-notes.epub`); neither is in the repo or in CI.

**Reference check** — `check-refs.cjs` verifies every `[@key]` citation against `references.bib`, every `@fig-` reference against its label, all 84 gallery links against the chapter anchors, and then every `href`/`src` of the 16 built pages in `_site/`, resolving each to a file and every `#fragment` to an id. The resolution is `linkcheck.py`, shared with the EPUB check above so the two cannot drift apart, and it covers same-page `#anchor` links too. That last part covers the generated pages — the notation index is written by `build-notation.cjs`, so a wrong path prefix in it never shows up in the sources; that is how 24 dead links once shipped. Links to the pdf, epub and Anki deck are skipped when those files are absent, because a `--to html` render does not produce them. This pass shells out to `python3 scripts/linkcheck.py`, so the check needs Python alongside Node.

**EPUB and releases** — the book builds EPUB alongside HTML and PDF, and tagged releases keep a frozen copy of the PDF for citation. See Releases.

**Image weight** — `figures/webp/` holds display-size WebP copies (1.2 MB against 14.7 MB of PNGs) that the gallery serves through `<picture>`, falling back to PNG. The PDF keeps the PNGs.

