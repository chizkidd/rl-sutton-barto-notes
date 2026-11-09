![visitor badge](https://visitor-badge.laobi.icu/badge?page_id=chizkidd.RL-Sutton-Barto-notes)

# RL Notes — Sutton & Barto

Personal study notes from *Reinforcement Learning: An Introduction* (Sutton & Barto, 2nd Ed.), built as a Quarto book and deployed to GitHub Pages.

## Live Site

[chizkidd.github.io/RL-Sutton-Barto-notes](https://chizkidd.github.io/RL-Sutton-Barto-notes)

## Chapters

| Chapter | Topic | Status |
|---|---|---|
| 1 | Introduction to RL | ✓ |
| 2 | Multi-Armed Bandits | ✓ |
| 3 | Finite Markov Decision Processes | ✓ |
| 4 | Dynamic Programming | ✓ |
| 5 | Monte Carlo Methods | ✓ |
| 6 | Temporal-Difference Learning | ✓ |
| 7 | n-step Bootstrapping | ✓ |
| 8 | Planning & Learning with Tabular Methods | ✓ |
| 9 | On-policy Prediction with Approximation | ✓ |
| 10 | On-policy Control with Approximation | ✓ |
| 11 | Off-policy Methods with Approximation | ✓ |
| 12 | Eligibility Traces | ✓ |
| 13 | Policy Gradient Methods | ✓ |


## Local Development

**Prerequisites:** [Quarto](https://quarto.org/docs/get-started/) installed.

```bash
# Clone the repo
git clone https://github.com/chizkidd/RL-Sutton-Barto-notes
cd RL-Sutton-Barto-notes

# Preview locally with live reload
quarto preview

# Build the static site
quarto render
```

Output goes to `_site/`.

## Deployment

Pushing to `main` automatically deploys to GitHub Pages via the GitHub Actions workflow in `.github/workflows/deploy.yml`.

To set up GitHub Pages for the first time:
1. Push the repo to GitHub
2. Go to **Settings → Pages → Source** and select **GitHub Actions**
3. Push a commit to `main` to trigger the first deploy

## Project Structure

```
RL-Sutton-Barto-notes/
├── README.md                                # Details about repository
├── LICENSE                                  # MIT license
├── .gitignore                               # Ignores _site/, .quarto/, locks, .DS_Store
├── _quarto.yml                              # Book config, chapters list, theme
├── index.qmd                                # Preface: coverage table + notation table
├── custom.scss                              # Custom styles (light + dark mode)
├── sidebar-toggle.html                      # Sidebar collapse/expand buttons
├── references.bib                           # BibTeX references
├── .github/
│   └── workflows/
│       └── deploy.yml                       # Render book, then deploy to GitHub Pages
├── chapters/                                # One .qmd file per chapter (13)
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
└── figures/                                 # 47 redrawn book figures (42 PNG, 5 SVG)
    ├── ch03-3-1.png                         # chNN-N-N[-label].png: chapter NN, figure N-N
    ├── ch06-6-4-sarsa.png
    ├── ch12-12-10-watkins-q-lambda.png
    ├── fig71_nstep_td.svg                   # Chapter 7 figures redrawn as SVG
    ├── fig75_tree_backup.svg
    └── ...
```

Figure counts per chapter: ch03 (3), ch04 (1), ch05 (1), ch06 (5), ch07 (5 PNG + 5 SVG), ch08 (6), ch09 (4), ch11 (7), ch12 (9), ch13 (1). Chapter 10 has no figures.

## Reference

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

---

## Citation

If you use these notes, please cite:

```bibtex
@misc{obasi2026rlnotes,
  author = {Obasi, Chizoba},
  title  = {Reinforcement Learning: An Introduction — Personal Study Notes},
  year   = {2026},
  url    = {https://chizkidd.github.io/RL-Sutton-Barto-notes}
}
```
