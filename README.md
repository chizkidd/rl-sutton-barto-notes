![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.RL-Sutton-Barto-notes)

# RL Notes — Sutton & Barto

Personal study notes from *Reinforcement Learning: An Introduction* (Sutton & Barto, 2nd Ed.), written as a Quarto book and published to GitHub Pages.

## Read It

| Format | Link |
|---|---|
| Website | [chizkidd.github.io/rl-sutton-barto-notes](https://chizkidd.github.io/rl-sutton-barto-notes/) |
| PDF | [rl-notes.pdf](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes.pdf) |
| EPUB | [rl-notes.epub](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes.epub) |
| Anki deck | [rl-notes-anki.tsv](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes-anki.tsv) |
| Source | [github.com/chizkidd/rl-sutton-barto-notes](https://github.com/chizkidd/rl-sutton-barto-notes) |

The PDF covers all 13 chapters and is rebuilt with the site on every push to `main`.

## Chapters

| Chapter | Topic |
|---|---|
| 1 | Introduction to RL |
| 2 | Multi-Armed Bandits |
| 3 | Finite Markov Decision Processes |
| 4 | Dynamic Programming |
| 5 | Monte Carlo Methods |
| 6 | Temporal-Difference Learning |
| 7 | n-step Bootstrapping |
| 8 | Planning & Learning with Tabular Methods |
| 9 | On-policy Prediction with Approximation |
| 10 | On-policy Control with Approximation |
| 11 | Off-policy Methods with Approximation |
| 12 | Eligibility Traces |
| 13 | Policy Gradient Methods |

Every chapter is written up; there are no placeholders.

## Local Development

**Prerequisites:** [Quarto](https://quarto.org/docs/get-started/) plus a LaTeX distribution for the PDF (TinyTeX is installed automatically by the workflow).

```bash
git clone https://github.com/chizkidd/rl-sutton-barto-notes
cd rl-sutton-barto-notes

quarto preview   # live reload at http://localhost:4200
quarto render    # full build into _site/ (HTML + PDF + EPUB)
```

Rendered output lands in `_site/`, with the PDF at `_site/rl-notes.pdf` and the EPUB at `_site/rl-notes.epub`. All of it is gitignored.

The CI builds with **Quarto 1.5.57** and **TinyTeX 2025.12** pinned to the frozen TeX Live 2025 package repository, so every run gets identical inputs. A newer local TeX Live is fine for writing, but it breaks some pages slightly differently from the published PDF — worth knowing before treating a local page-number difference as a regression.

## Continuous Integration

One workflow, `.github/workflows/deploy.yml`: it renders the book and publishes `_site/` to GitHub Pages on every push to `main`. It fails only if the render fails or `_site/rl-notes.pdf` comes out empty, which are the two things that actually break the site.

The toolchain is pinned (Quarto 1.5.57, TinyTeX 2025.12 against the frozen TeX Live 2025 repository) and every action is pinned to a commit SHA, so the PDF lays out the same way on every run.

## Extras

Each of these is a one-command tool. The checks and generators are local-only — none of them run in CI; the deploy workflow runs `export-anki.cjs` so the downloadable deck matches the book.

```bash
node scripts/export-anki.cjs       # bullets -> Anki cloze deck (dist/anki/rl-notes.tsv)
python3 scripts/check-parity.py    # compare the built HTML and PDF for drift
python3 scripts/check-epub.py      # epub: XHTML, link and anchor resolution
python3 scripts/check-sources.py   # figures/SOURCES.md against the built book
node scripts/check-refs.cjs        # dead citations, figure refs, gallery anchors, then linkcheck.py
node scripts/build-notation.cjs    # regenerate notation.qmd
python3 scripts/build-epub-gallery.py  # rebuild the epub figure list from the gallery grid
python3 scripts/make-webp.py       # WebP copies of the figures for the gallery
python3 scripts/freeze-anchors.py  # write the built heading ids into the chapters
```

**Notation index** — `notation.qmd` maps 24 symbols to the section that defines them and counts the sections that use them. It is generated from the sources, so the locations cannot go stale; the descriptions are hand-written.

**Figure gallery** — `gallery.qmd` renders an interactive grid of thumbnails for the HTML build and a plain figure list for the EPUB, which cannot follow links into pages that only exist as HTML. Only the grid is hand-written: `build-epub-gallery.py` regenerates the list from it (path, alt text, number and caption), so a caption is edited in one place. `--check` reports a stale list instead of writing.

**Parity check** — `check-parity.py` compares section numbers and the full text of every figure caption between `_site/` and `rl-notes.pdf`, because the two formats are configured separately (`number-depth: 3` against `secnumdepth 2`) and drift silently. Captions are compared word for word, so changing a single word in a caption fails the check; math is dropped because the HTML holds TeX source and the PDF typeset glyphs.

**EPUB check** — `check-epub.py` unzips `_site/rl-notes.epub` and fails if any chapter is not well-formed XHTML (an unclosed `<br>`, `<img>` or `<source>` makes readers show an error page instead of the chapter), if any `href` or `src` does not resolve to a file inside the archive (a `.qmd` source path or a `chapters/*.html` page looks fine on the web and is missing from the book), or if any `#fragment` names an id that the document it lands in does not have. None of those show up until the book is opened in a reader. The last two rules are `linkcheck.py`, the same code `check-refs.cjs` runs against `_site/`, so a link is judged the same way on the site and inside the archive; this script supplies only the documents and anchors of the zip.

**Figure table check** — `check-sources.py` holds `figures/SOURCES.md` to the build. For every row it wants the PNG in `figures/`, a chapter link whose `{#fig-…}` anchor is really in that chapter and whose number belongs to it, a figure number the book still has, and the caption the book prints word for word — math included, since the comparison undoes the build's markup rather than dropping it. It also reports a figure in the book with no row, and a number with two. The captions come from `bookhtml.py`, the same reader `check-parity.py` uses, so "what the book says" is defined once.

**Reference check** — `check-refs.cjs` verifies every `[@key]` citation against `references.bib`, every `@fig-` reference against its label, all 84 gallery links against the chapter anchors, and then every `href`/`src` of the 16 built pages in `_site/`, resolving each to a file and every `#fragment` to an id. The resolution is `linkcheck.py`, shared with the EPUB check above so the two cannot drift apart, and it covers same-page `#anchor` links too. That last part covers the generated pages — the notation index is written by `build-notation.cjs`, so a wrong path prefix in it never shows up in the sources; that is how 24 dead links once shipped. Links to the pdf, epub and Anki deck are skipped when those files are absent, because a `--to html` render does not produce them. This pass shells out to `python3 scripts/linkcheck.py`, so the check needs Python alongside Node.

**EPUB and releases** — the book builds EPUB alongside HTML and PDF, and tagged releases keep a frozen copy of the PDF for citation. See Releases.

**Image weight** — `figures/webp/` holds display-size WebP copies (1.2 MB against 14.7 MB of PNGs) that the gallery serves through `<picture>`, falling back to PNG. The PDF keeps the PNGs.

## Anki Deck

`node scripts/export-anki.cjs` turns every bullet that bolds a term into a cloze card, tagged by chapter and section, and writes `dist/anki/rl-notes.tsv` for Anki's tab-separated import (note type: Cloze). The deploy workflow runs the same script into `_site/rl-notes-anki.tsv`, so the download on the site always matches the published book.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which renders the book, fails if `_site/rl-notes.pdf` is missing or empty, and publishes `_site/` to GitHub Pages.

First-time setup:

1. Push the repository to GitHub.
2. Go to **Settings → Pages → Source** and select **GitHub Actions**.
3. Push a commit to `main` to trigger the first deploy.

## Project Structure

```
RL-Sutton-Barto-notes/
├── README.md                    # This file
├── LICENSE                      # MIT license
├── .gitignore                   # Ignores _site/, .quarto/, .preview/, locks, __pycache__, .DS_Store
├── _quarto.yml                  # Book config: chapter order, theme, PDF settings
├── index.qmd                    # Preface: coverage table + notation table
├── gallery.qmd                  # Figure gallery: every diagram by chapter
├── custom.scss                  # Custom styles (light + dark mode)
├── sidebar-toggle.html          # Sidebar collapse/expand buttons
├── references.bib               # BibTeX references
├── .github/
│   └── workflows/
│       └── deploy.yml           # Render the book, publish _site/ to GitHub Pages
├── notation.qmd                 # Generated notation index (appendices)
├── scripts/
│   ├── export-anki.cjs          # Bullets -> Anki cloze deck (also run by deploy.yml)
│   ├── check-parity.py          # HTML vs PDF: section numbering and caption text
│   ├── check-sources.py         # figures/SOURCES.md against the built HTML
│   ├── check-epub.py            # EPUB: XHTML, link and anchor resolution
│   ├── bookhtml.py              # Reads the built HTML's figure captions (shared)
│   ├── check-refs.cjs           # Dead citations, @fig- labels, gallery anchors; linkcheck.py for _site/
│   ├── linkcheck.py             # Shared link and anchor resolution: site pages and EPUB documents
│   ├── build-notation.cjs       # Regenerates notation.qmd from the chapters
│   ├── build-epub-gallery.py    # Regenerates the EPUB figure list from the gallery grid
│   ├── make-webp.py             # WebP copies of the figures for the gallery
│   └── freeze-anchors.py        # Freezes heading ids; fails if one is used twice
├── chapters/                    # One .qmd per chapter (13)
│   ├── ch01-introduction.qmd
│   ├── ch02-multi-armed-bandits.qmd
│   ├── ch03-finite-mdps.qmd
│   ├── ch04-dynamic-programming.qmd
│   ├── ch05-monte-carlo.qmd
│   ├── ch06-temporal-difference.qmd
│   ├── ch07-nstep-bootstrapping.qmd
│   ├── ch08-planning-learning.qmd
│   ├── ch09-on-policy-prediction-approximation.qmd
│   ├── ch10-on-policy-control-approximation.qmd
│   ├── ch11-off-policy-methods-approximation.qmd
│   ├── ch12-eligibility-traces.qmd
│   └── ch13-policy-gradient-methods.qmd
└── figures/                     # 42 figure PNGs (the book's diagrams)
    ├── ch03-3-1.png             # chNN-N-N[-label].png — chapter NN, book figure N-N
    ├── ch06-6-4-sarsa.png
    ├── ch12-12-10-watkins-q-lambda.png
    ├── webp/                    # Same 42 figures as WebP, for the gallery
    ├── fig71_nstep_td.svg       # Chapter 7 SVG alternates, commented out
    ├── fig75_tree_backup.svg
    └── ...
```

*Figure counts per chapter: ch03 (3), ch04 (1), ch05 (1), ch06 (5), ch07 (5), ch08 (6), ch09 (4), ch11 (7), ch12 (9), ch13 (1). Chapters 01, 02 and 10 have no figures.*

The PNGs follow `chNN-N-N[-label].png` throughout, including chapter 7 (`ch07-7-1-n-step-td.png`). The five `.svg` files in chapter 7 keep the older `figNN_slug.svg` name; they are the superseded attempts described below.

Chapter 7 also keeps five SVG attempts next to its PNGs. They are commented out in the chapter source and are not part of the build, so `figures/SOURCES.md` — which maps every image to its chapter, figure number and caption — lists the 42 PNGs that actually appear.

## Reference

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

## Citation

If you use these notes, please cite:

```bibtex
@misc{obasi2026rlnotes,
  author = {Obasi, Chizoba},
  title  = {Reinforcement Learning: An Introduction — Personal Study Notes},
  year   = {2026},
  url    = {https://chizkidd.github.io/rl-sutton-barto-notes/}
}
```
