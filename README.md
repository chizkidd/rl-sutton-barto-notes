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

## Tooling

Scripts, checks, CI and build details live in [`EXTRAS.md`](EXTRAS.md); you do not need them to read the notes.

## Anki Deck

`node scripts/export-anki.cjs` turns every bullet that bolds a concept (excluding promptless section labels) into a cloze card with native Anki MathJax (`\(...\)`), tagged by chapter and section, and writes `dist/anki/rl-notes.tsv` for Anki's tab-separated import. The deploy workflow runs the same script into `_site/rl-notes-anki.tsv`, so the download on the site always matches the published book.

**How to import:** download `rl-notes-anki.tsv`, then File → Import in Anki and choose a deck. The file's `#notetype:Cloze` header presets the Cloze note type, so the `{{c1::…}}` markers become real clozes and MathJax equations render natively with no add-ons needed.

If you already imported the deck as Basic, delete those notes in Browse and import the file again. Anki cannot convert an existing note to another note type, so those cards keep the `{{c1::…}}` markers as literal text until they are imported as Cloze.

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
├── EXTRAS.md                    # Scripts, checks and build details
├── LICENSE                      # MIT license
├── .gitignore                   # Ignores _site/, .quarto/, .preview/, dist/, locks, __pycache__, .DS_Store
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
│   ├── check-sources.py         # figures/SOURCES.md and the gallery cards against the built HTML
│   ├── check-epub.py            # EPUB: XHTML, links, anchors, packaging rules fix-epub.py repairs
│   ├── bookhtml.py              # Reads the built HTML's figure captions (shared)
│   ├── check-refs.cjs           # Dead citations, @fig- labels, gallery anchors; linkcheck.py for _site/
│   ├── linkcheck.py             # Shared link and anchor resolution: site pages and EPUB documents
│   ├── build-notation.cjs       # Regenerates notation.qmd from the chapters
│   ├── build-epub-gallery.py    # Regenerates the EPUB figure list from the gallery grid
│   ├── fix-epub.py              # Post-render repair of the EPUB for EPUBCheck
│   ├── make-webp.py             # WebP copies of the figures for the gallery
│   ├── make-figures.py          # Generates 8 original 300 dpi conceptual diagrams (Ch. 3–12)
│   ├── make-fig-13-1.py         # Generates Figure 13.1 (Gaussian PDF) at 300 dpi
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
└── figures/                     # 9 programmatically generated PNGs + WebP gallery copies
    ├── SOURCES.md               # Every figure: file, chapter, number and caption
    ├── ch03-mdp-loop.png
    ├── ch06-td-backups.png
    ├── ch12-lambda-weights.png
    ├── ch13-13-7-prob-density-function.png
    └── webp/                    # Matching 24 figures (+ EPUB cover) as WebP, for the gallery
```

*All 24 figures are generated programmatically at 300 dpi via `scripts/make-figures.py` and `scripts/make-fig-13-1.py` (Ch. 3, 4, 6, 7, 8, 9, 11, 12, 13), with an EPUB cover generated by `scripts/make-cover.py`. Chapters 01, 02, 05, and 10 have no figures, and additional textbook diagrams are cited in Sutton & Barto (2020).*

## Reference

Sutton, R. S., & Barto, A. G. (2020). *Reinforcement Learning: An Introduction* (2nd ed., 2018; 2020 corrected reprint). MIT Press.

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
