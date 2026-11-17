#!/usr/bin/env node
// Checks that the notes spell the same symbol the same way everywhere.
//
// The book is 200+ equations deep and written across months, so notation drifts:
// a weight vector is \mathbf{w} in 500 places and a bare w_t in a few others, and
// a reader has to work out whether the difference means something. These rules
// are the ones that are unambiguous enough to fail a build on:
//
//   weights        a weight vector is \mathbf{w}; bare w with a sub/superscript
//                  means a scalar and is almost always a slip
//   definitions    "\doteq" is the notes' symbol for "is defined as"; ":=" and
//                  "\triangleq" are the same thing spelled differently
//   text-in-math   \text{} must not be used for emphasis inside math; \mathbf{}
//                  is for symbols, \textbf{} inside math renders inconsistently
//                  between LaTeX and KaTeX
//
// Usage: node scripts/lint-notation.cjs [file.qmd ...]

const fs = require('fs');
const path = require('path');

const SKIP_DIRS = new Set(['_site', '.quarto', '.preview', 'node_modules', 'artifacts', 'figures', '.git', 'dist']);

function collect(dir, out) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name)) collect(path.join(dir, entry.name), out);
    } else if (entry.name.endsWith('.qmd')) out.push(path.join(dir, entry.name));
  }
  return out.sort();
}

// Every math region, with the line it starts on. Line numbers let the report
// point straight at the offending equation.
function mathRegions(src) {
  const regions = [];
  const lines = src.split('\n');
  let fenced = false;
  let blockStart = -1;
  lines.forEach((line, index) => {
    if (line.startsWith('```')) {
      fenced = !fenced;
      return;
    }
    if (fenced) return;
    const stripped = line.replace(/`[^`]*`/g, '');
    // Display math: a line that is exactly $$ ... $$ or opens a $$ block.
    const dollars = (stripped.match(/\$\$/g) || []).length;
    if (blockStart === -1 && dollars % 2 === 1) {
      blockStart = index;
      return;
    }
    if (blockStart !== -1) {
      if (dollars % 2 === 1) {
        regions.push({ line: blockStart + 1, text: lines.slice(blockStart, index + 1).join('\n') });
        blockStart = -1;
      }
      return;
    }
    // Inline math on this line.
    for (const m of stripped.matchAll(/\$([^$]+)\$/g)) regions.push({ line: index + 1, text: m[1] });
  });
  if (blockStart !== -1) regions.push({ line: blockStart + 1, text: lines.slice(blockStart).join('\n') });
  return regions;
}

const RULES = [
  {
    id: 'weights',
    // A time-indexed weight vector is \mathbf{w}. Scalar components such as
    // "2w_1 + w_8" in a worked example are italic on purpose, so only the
    // vector forms are flagged.
    test: (math) =>
      math
        .replace(/\\mathbf\{w\}/g, '')
        .match(/(?<![a-zA-Z\\])(?:w[_^]\{?t|\\hat\{?w|\\tilde\{?w|\\bar\{?w)/g) || [],
    describe: (hit) => `"${hit}" — the weight vector is \\mathbf{w}`,
  },
  {
    id: 'definitions',
    test: (math) => math.match(/:=|\\triangleq/g) || [],
    describe: (hit) => `"${hit}" — the notes use \\doteq for "is defined as"`,
  },
  {
    id: 'bold-macros',
    // \mathbf is for vectors like w, \boldsymbol for greek like theta.
    test: (math) => math.match(/\\mathbf\{\\theta\}|\\boldsymbol\{w\}|\\bm\{/g) || [],
    describe: (hit) => `"${hit}" — vectors use \\mathbf, greek uses \\boldsymbol`,
  },
];

function main() {
  const files = process.argv.slice(2).length ? process.argv.slice(2) : collect('.', []);
  const findings = [];
  let regions = 0;

  for (const file of files) {
    const src = fs.readFileSync(file, 'utf8');
    for (const region of mathRegions(src)) {
      regions += 1;
      for (const rule of RULES) {
        for (const hit of rule.test(region.text)) {
          findings.push({ file, line: region.line, rule: rule.id, message: rule.describe(hit) });
        }
      }
    }
  }

  const byRule = findings.reduce((acc, f) => ({ ...acc, [f.rule]: (acc[f.rule] || 0) + 1 }), {});
  if (!findings.length) {
    console.log(`lint-notation: ${regions} math regions, no inconsistencies found`);
    return 0;
  }
  for (const f of findings) {
    console.log(`${f.file}:${f.line}: [${f.rule}] ${f.message}`);
  }
  console.log(`\nlint-notation: ${findings.length} issue(s) in ${regions} math regions`);
  console.log(`  ${Object.entries(byRule).map(([k, v]) => `${k}: ${v}`).join(', ')}`);
  return 1;
}

process.exit(main());
