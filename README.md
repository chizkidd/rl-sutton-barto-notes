![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.RL-Sutton-Barto-notes)

# RL Notes — Sutton & Barto

Personal study notes from *Reinforcement Learning: An Introduction* (Sutton & Barto, 2nd Ed.), written as a Quarto book and published to GitHub Pages.

## Read It

| Format | Link |
|---|---|
| Website | [chizkidd.github.io/rl-sutton-barto-notes](https://chizkidd.github.io/rl-sutton-barto-notes/) |
| PDF | [rl-notes.pdf](https://chizkidd.github.io/rl-sutton-barto-notes/rl-notes.pdf) |
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

Three workflows share the pinned toolchain (Quarto 1.5.57, TinyTeX 2025.12 against frozen TeX Live 2025), and every action is pinned to a commit SHA rather than a tag, so a given commit always builds with the same inputs.

| Workflow | Runs on | What it does |
|---|---|---|
| `deploy.yml` | push to `main`, manual | Renders the book, fails if `_site/rl-notes.pdf` is missing or empty, publishes `_site/` to GitHub Pages |
| `math-check.yml` | push, manual | Renders every math chunk through KaTeX and fails on a parse error, an unclosed `$$`, or a stray visible `$` |
| `tex-canary.yml` | 06:00 UTC on the 1st of each month, manual | Builds the PDF twice — pinned and current TinyTeX — then compares page count, page text and rasterised pages, warning (never failing the build) when the newer toolchain lays the book out differently |

The canary is a warning by design: drift is information, not a broken build. Its report appears in the run's job summary, listing the pages that differ.

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
├── .gitignore                   # Ignores _site/, .quarto/, locks, .DS_Store
├── _quarto.yml                  # Book config: chapter order, theme, PDF settings
├── index.qmd                    # Preface: coverage table + notation table
├── gallery.qmd                  # Figure gallery: every diagram by chapter
├── custom.scss                  # Custom styles (light + dark mode)
├── sidebar-toggle.html          # Sidebar collapse/expand buttons
├── references.bib               # BibTeX references
├── .github/
│   └── workflows/
│       ├── deploy.yml           # Render book (HTML + PDF), deploy to GitHub Pages
│       ├── math-check.yml       # KaTeX-render every math chunk, fail on a parse error
│       └── tex-canary.yml       # Monthly build with current TinyTeX, warn on layout drift
├── scripts/
│   ├── check-math.cjs           # Used by math-check.yml
│   └── compare-pdf.py           # Used by tex-canary.yml
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
└── figures/                     # 47 redrawn book figures (42 PNG, 5 SVG)
    ├── ch03-3-1.png             # chNN-N-N[-label].png — chapter NN, book figure N-N
    ├── ch06-6-4-sarsa.png
    ├── ch12-12-10-watkins-q-lambda.png
    ├── fig71_nstep_td.svg       # Chapter 7 figures, redrawn as SVG
    ├── fig75_tree_backup.svg
    └── ...
```

*Figure counts per chapter: ch03 (3), ch04 (1), ch05 (1), ch06 (5), ch07 (5 PNG + 5 SVG), ch08 (6), ch09 (4), ch11 (7), ch12 (9), ch13 (1). Chapters 01, 02 and 10 have no figures.*

Figures use one of two naming schemes: `chNN-N-N[-label].png` for chapters 3–6 and 8–13, and `figNN_slug.svg` for chapter 7's redrawn diagrams.

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
