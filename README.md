![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.RL-Sutton-Barto-notes)

# RL Notes — Sutton & Barto

Personal study notes from *Reinforcement Learning: An Introduction* (Sutton & Barto, 2nd Ed.), written as a Quarto book and published to GitHub Pages.

## Read It

| Format | Link |
|---|---|
| Website | [chizkidd.github.io/rl-sutton-barto-notes](https://chizkidd.github.io/rl-sutton-barto-notes/) |
| PDF | [rl-notes.pdf](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes.pdf) |
| Anki deck | [rl-notes-anki.tsv](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes-anki.tsv) |
| Source | [github.com/chizkidd/RL-Sutton-Barto-notes](https://github.com/chizkidd/RL-Sutton-Barto-notes) |

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
git clone https://github.com/chizkidd/RL-Sutton-Barto-notes
cd RL-Sutton-Barto-notes

quarto preview   # live reload at http://localhost:4200
quarto render    # full build into _site/ (HTML + PDF)
```

Rendered output lands in `_site/`, with the PDF at `_site/rl-notes.pdf`. Both are gitignored.

The CI builds with **Quarto 1.5.57** and **TinyTeX 2025.12** pinned to the frozen TeX Live 2025 package repository, so every run gets identical inputs. A newer local TeX Live is fine for writing, but it breaks some pages slightly differently from the published PDF — worth knowing before treating a local page-number difference as a regression.

## Continuous Integration

One workflow, `.github/workflows/deploy.yml`: it renders the book and publishes `_site/` to GitHub Pages on every push to `main`. It fails only if the render fails or `_site/rl-notes.pdf` comes out empty, which are the two things that actually break the site.

The toolchain is pinned (Quarto 1.5.57, TinyTeX 2025.12 against the frozen TeX Live 2025 repository) and every action is pinned to a commit SHA, so the PDF lays out the same way on every run.

## Study Tooling

Three small scripts read the chapter sources. None of them run in CI and none are needed to build the book.

```bash
node scripts/coverage.cjs          # which sections of the book are covered
node scripts/lint-notation.cjs     # fail on a symbol spelled two ways
node scripts/export-anki.cjs       # build an Anki deck from the bullet points
```

`coverage.cjs` compares the notes against `data/book-toc.json` — the 121 sections of the second edition, extracted from the official PDF's table of contents rather than typed by hand. Both lists are in book order, so it aligns them with dynamic programming and lets either side skip, which is what keeps a heading from being paired with the wrong section just because they share a word. Current result: **121/121 sections**. Add `--json` for the full pairing, or `--fail-under 100` to turn a dropped section into a non-zero exit.

`lint-notation.cjs` holds the two rules the notes kept breaking: the weight vector is `\mathbf{w}` (not a bare `w_t`), and "is defined as" is `\doteq` (not `:=`). It reports `file:line` and exits non-zero. Nothing runs it automatically; call it when you want it.

`export-anki.cjs` turns every bullet that bolds a term into a cloze card — 420 cards from 1120 bullets — with the section path as the extra field and `rl::chNN::section` tags, written to `dist/anki/rl-notes.tsv` for Anki's tab-separated import (note type: Cloze). The deploy workflow rebuilds it into `_site/rl-notes-anki.tsv`, so the download on the site always matches the published book.

Every figure also carries real alt text: the caption with its LaTeX flattened to words, in both `chapters/*.qmd` and `gallery.qmd`.

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
├── .gitignore                   # Ignores _site/, .quarto/, .preview/, locks, .DS_Store
├── _quarto.yml                  # Book config: chapter order, theme, PDF settings
├── index.qmd                    # Preface: coverage table + notation table
├── gallery.qmd                  # Figure gallery: every diagram by chapter
├── custom.scss                  # Custom styles (light + dark mode)
├── sidebar-toggle.html          # Sidebar collapse/expand buttons
├── references.bib               # BibTeX references
├── .github/
│   └── workflows/
│       └── deploy.yml           # Render the book, publish _site/ to GitHub Pages
├── scripts/
│   ├── export-anki.cjs          # Bullets -> Anki cloze deck (also run by deploy.yml)
│   ├── check-math.cjs           # Optional: KaTeX-render every math chunk
│   ├── lint-notation.cjs        # Optional: symbol consistency
│   └── coverage.cjs             # Optional: section coverage against the book's TOC
├── data/
│   └── book-toc.json            # The 2nd edition's 121 sections, from its PDF TOC
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
    ├── fig71_nstep_td.svg       # Chapter 7 SVG alternates, commented out
    ├── fig75_tree_backup.svg
    └── ...
```

*Figure counts per chapter: ch03 (3), ch04 (1), ch05 (1), ch06 (5), ch07 (5), ch08 (6), ch09 (4), ch11 (7), ch12 (9), ch13 (1). Chapters 01, 02 and 10 have no figures.*

Figures use one of two naming schemes: `chNN-N-N[-label].png` for chapters 3–6 and 8–13, and `figNN_slug.svg` for chapter 7's earlier diagrams.

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
