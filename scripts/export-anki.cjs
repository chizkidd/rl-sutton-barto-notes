#!/usr/bin/env node
// Turns the notes into an Anki deck.
//
// Every bullet that bolds a term is already the shape of a card: "**TD methods**
// learn from incomplete episodes..." asks "which methods learn from incomplete
// episodes?" and answers "TD methods". So the rule is simple and mechanical:
// one card per bold term, the term cloze-deleted, the section path as context.
//
// Usage: node scripts/export-anki.cjs [--out path.tsv] [file.qmd ...]
//   default output: dist/anki/rl-notes.tsv
//
// The file is tab separated with the header lines Anki understands, so
// File -> Import accepts it directly. #notetype:Cloze presets the built-in
// Cloze note type, which is what turns the {{c1::…}} markers into clozes;
// left to itself the import screen picks Basic and they stay literal text.

const fs = require('fs');
const path = require('path');

const OUT_DEFAULT = path.join('dist', 'anki', 'rl-notes.tsv');

// LaTeX the notes use, rendered as the plain text a card should show. Ordered
// longest-first so \mathbf{w} is replaced before \mathbf.
const TEX = [
  [/\\mathbf\{([^{}]*)\}/g, '$1'],
  [/\\boldsymbol\{([^{}]*)\}/g, '$1'],
  [/\\mathbb\{([^{}]*)\}/g, '$1'],
  [/\\operatorname\{([^{}]*)\}/g, '$1'],
  [/\\text\{([^{}]*)\}/g, '$1'],
  [/\\mathrm\{([^{}]*)\}/g, '$1'],
  [/\\hat\{([^{}]*)\}/g, '$1̂'],
  [/\\bar\{([^{}]*)\}/g, '$1̄'],
  [/\\tilde\{([^{}]*)\}/g, '$1̃'],
  [/\\doteq/g, '≐'],
  [/\\approx/g, '≈'],
  [/\\neq/g, '≠'],
  [/\\leq/g, '≤'],
  [/\\geq/g, '≥'],
  [/\\times/g, '×'],
  [/\\cdot/g, '·'],
  [/\\sum/g, 'Σ'],
  [/\\prod/g, 'Π'],
  [/\\nabla/g, '∇'],
  [/\\infty/g, '∞'],
  [/\\in\b/g, '∈'],
  [/\\pi\b/g, 'π'],
  [/\\theta\b/g, 'θ'],
  [/\\gamma\b/g, 'γ'],
  [/\\alpha\b/g, 'α'],
  [/\\beta\b/g, 'β'],
  [/\\lambda\b/g, 'λ'],
  [/\\mu\b/g, 'μ'],
  [/\\rho\b/g, 'ρ'],
  [/\\sigma\b/g, 'σ'],
  [/\\delta\b/g, 'δ'],
  [/\\epsilon\b/g, 'ε'],
  [/\\tau\b/g, 'τ'],
  [/\\eta\b/g, 'η'],
  [/\\max/g, 'max'],
  [/\\min/g, 'min'],
  [/\\log/g, 'log'],
  [/\\left|\\right/g, ''],
  [/\\[,;:!]/g, ' '],
  [/\\quad|\\qquad/g, ' '],
  [/\\[a-zA-Z]+\*?/g, ''], // any command we did not map
];

function plain(text) {
  let out = text;
  out = out.replace(/\$([^$]+)\$/g, '$1');
  for (const [re, rep] of TEX) out = out.replace(re, rep);
  return out
    .replace(/[{}]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function walk(dir, out) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) walk(path.join(dir, entry.name), out);
    else if (entry.name.endsWith('.qmd')) out.push(path.join(dir, entry.name));
  }
  return out.sort();
}

function slug(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 40);
}

// One entry per top-level bullet carrying at least one bold term.
function cardsFrom(file, heading, bullets) {
  const cards = [];
  for (const { text, children } of bullets) {
    const bolds = [...text.matchAll(/\*\*(.+?)\*\*/g)].map((m) => m[1]);
    if (!bolds.length) continue;
    const term = bolds[0].replace(/[\s:;,.]+$/, '');
    // Cloze the first bold term only; later ones would need c2, c3 and export
    // one card per cloze, which makes a single bullet spill into several cards.
    const body = plain(text.replace(/\*\*/g, '')).replace(plain(term), `{{c1::${plain(term)}}}`, 1);
    const extra = [
      heading.section ? `Section: ${heading.section}` : null,
      plain(text.replace(/\*\*/g, '')),
      ...children.map((c) => `• ${plain(c.replace(/\*\*/g, ''))}`),
    ]
      .filter(Boolean)
      .join('\n');
    const tags = ['rl', file.replace(/^.*ch(\d+).*$/, 'ch$1'), ...heading.path.map(slug)].join(' ');
    cards.push({ text: body, extra, tags });
  }
  return cards;
}

function parse(file) {
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  const bullets = [];
  let h1 = '';
  let h2 = '';
  let h3 = '';
  let fenced = false;

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.startsWith('```')) {
      fenced = !fenced;
      continue;
    }
    if (fenced) continue;
    if (/^#\s+/.test(line)) {
      h1 = line.replace(/^#\s+/, '').replace(/\{.*$/, '').trim();
      h2 = h3 = '';
      continue;
    }
    if (/^##\s+/.test(line)) {
      h2 = line.replace(/^##\s+/, '').replace(/\{.*$/, '').trim();
      h3 = '';
      continue;
    }
    if (/^###\s+/.test(line)) {
      h3 = line.replace(/^###\s+/, '').replace(/\{.*$/, '').trim();
      continue;
    }
    if (/^- /.test(line)) {
      bullets.push({
        text: line.replace(/^-\s+/, ''),
        children: [],
        heading: { section: [h1, h2, h3].filter(Boolean).join(' › '), path: [h2, h3].filter(Boolean) },
      });
      continue;
    }
    if (/^\s{2,}- /.test(line) && bullets.length) {
      bullets[bullets.length - 1].children.push(line.replace(/^\s*-\s+/, ''));
    }
  }
  return bullets;
}

function main() {
  const args = process.argv.slice(2);
  let out = OUT_DEFAULT;
  const files = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--out') out = args[++i];
    else files.push(args[i]);
  }
  const sources = files.length ? files : walk('chapters', []);

  const rows = [];
  let bullets = 0;
  for (const file of sources) {
    const parsed = parse(file);
    bullets += parsed.length;
    for (const bullet of parsed) {
      for (const card of cardsFrom(file, bullet.heading, [bullet])) rows.push(card);
    }
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const body = rows
    .map((r) => [r.text, r.extra, r.tags].map((f) => f.replace(/\t/g, ' ').replace(/\n/g, '<br>')).join('\t'))
    .join('\n');
  fs.writeFileSync(
    out,
    `#separator:tab\n#html:true\n#notetype:Cloze\n#tags column:3\n${body}\n`
  );

  console.log(`export-anki: ${rows.length} cards from ${bullets} bullets in ${sources.length} files`);
  console.log(`  written to ${out}`);
  const ratio = ((rows.length / bullets) * 100).toFixed(0);
  console.log(`  ${ratio}% of bullets carry a bold term and become a card`);
}

main();
