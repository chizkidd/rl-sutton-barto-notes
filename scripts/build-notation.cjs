#!/usr/bin/env node
// Builds notation.qmd: a symbol index for the book.
//
// The notes define symbols wherever they first appear, which is right for
// reading and useless for looking things up: nothing tells you that the
// importance-sampling ratio rho is defined in 5.5 rather than in the chapter
// where you met it. This scans the chapters for each symbol, records the first
// section that defines it and how many sections use it, and writes a page that
// links straight to those sections.
//
// Descriptions are hand-written (a script cannot summarise notation); the
// locations are generated, so they cannot go stale.
//
// Usage: node scripts/build-notation.cjs [--out notation.qmd]

const fs = require('fs');
const path = require('path');

const SYMBOLS = [
  { display: '$S_t, A_t$', meaning: 'state and action at time $t$', pattern: /S_t|A_t/g },
  { display: '$R_{t+1}$', meaning: 'reward received after step $t$', pattern: /R_\{t\+1\}|R_t/g },
  { display: '$G_t$', meaning: 'return: discounted sum of future rewards', pattern: /G_t/g },
  { display: '$\\gamma$', meaning: 'discount rate', pattern: /\\gamma/g },
  { display: '$\\pi(a \\mid s)$', meaning: 'policy: probability of each action in a state', pattern: /\\pi/g },
  { display: '$v_\\pi(s), q_\\pi(s,a)$', meaning: 'state-value and action-value under $\\pi$', pattern: /v_\\pi|q_\\pi/g },
  { display: '$v_*(s), q_*(s,a)$', meaning: 'optimal state-value and action-value', pattern: /v_\*|q_\*/g },
  { display: '$p(s\',r \\mid s,a)$', meaning: 'dynamics: transition probability and reward', pattern: /p\(s'?,r/g },
  { display: '$\\varepsilon$', meaning: 'exploration rate in $\\varepsilon$-greedy', pattern: /\\varepsilon/g },
  { display: '$\\alpha$', meaning: 'step size (learning rate)', pattern: /\\alpha/g },
  { display: '$\\delta_t$', meaning: 'TD error', pattern: /\\delta_t|\\delta/g },
  { display: '$\\rho_{t:T-1}$', meaning: 'importance-sampling ratio', pattern: /\\rho/g },
  { display: '$\\mathbf{w}$', meaning: 'weight vector of a function approximator', pattern: /\\mathbf\{w\}/g },
  { display: '$\\hat{v}(s,\\mathbf{w})$', meaning: 'approximated value with weights $\\mathbf{w}$', pattern: /\\hat\{v\}|\\hat\{q\}/g },
  { display: '$\\mathbf{x}(s)$', meaning: 'feature vector for state $s$', pattern: /\\mathbf\{x\}/g },
  { display: '$\\mathbf{z}_t$', meaning: 'eligibility trace', pattern: /\\mathbf\{z\}/g },
  { display: '$\\lambda$', meaning: 'trace decay rate', pattern: /\\lambda/g },
  { display: '$n$', meaning: 'number of steps in $n$-step methods', pattern: /(?<![a-zA-Z\\])n\$(?![\w])/g },
  { display: '$\\theta$', meaning: 'policy parameters', pattern: /\\boldsymbol\{\\theta\}|\\theta/g },
  { display: '$\\nabla$', meaning: 'gradient with respect to the parameters', pattern: /\\nabla/g },
  { display: '$\\mu$', meaning: 'behaviour policy (off-policy), or a mean', pattern: /\\mu/g },
  { display: '$\\sigma$', meaning: 'standard deviation', pattern: /\\sigma/g },
  { display: '$\\mathbb{E}[\\cdot]$', meaning: 'expectation', pattern: /\\mathbb\{E\}/g },
  { display: '$\\doteq$', meaning: '"is defined as"', pattern: /\\doteq/g },
];

// Only math counts: a symbol mentioned in prose is not a use of the symbol.
function mathOnly(body) {
  const text = body.join('\n');
  const chunks = [];
  for (const m of text.matchAll(/\$\$[\s\S]*?\$\$|\$[^$]*\$/g)) chunks.push(m[0]);
  return chunks.join('\n');
}

function sentences(text) {
  // Split a chapter into sections: each "## Heading {#id}" starts one.
  const out = [];
  const lines = text.split('\n');
  let current = { id: null, title: null, number: null, body: [] };
  for (const line of lines) {
    const m = line.match(/^##\s+(.*?)\s*(?:\{#(sec-[A-Za-z0-9-]+)\})?\s*$/);
    if (m) {
      if (current.id) out.push(current);
      const number = m[2] ? m[2].match(/^sec-ch\d+-(\d+)-(\d+)$/) : null;
      current = {
        id: m[2] || null,
        title: m[1].replace(/\{.*$/, '').trim(),
        number: number ? `${Number(number[1])}.${number[2]}` : null,
        body: [],
      };
      continue;
    }
    current.body.push(line);
  }
  if (current.id) out.push(current);
  return out;
}

function main() {
  const out = process.argv.includes('--out')
    ? process.argv[process.argv.indexOf('--out') + 1]
    : 'notation.qmd';

  const chapters = fs
    .readdirSync('chapters')
    .filter((f) => /^ch\d+.*\.qmd$/.test(f))
    .sort();

  const sections = [];
  for (const file of chapters) {
    const number = Number(file.match(/^ch(\d+)/)[1]);
    for (const s of sentences(fs.readFileSync(path.join('chapters', file), 'utf8'))) {
      sections.push({ ...s, chapter: number, file: file.replace(/\.qmd$/, '.html') });
    }
  }

  const rows = [];
  for (const symbol of SYMBOLS) {
    const hits = sections.filter((s) => {
      const body = mathOnly(s.body);
      symbol.pattern.lastIndex = 0;
      return symbol.pattern.test(body);
    });
    if (!hits.length) {
      console.error(`  !! "${symbol.display}" never appears; check its pattern`);
      continue;
    }
    const first = hits[0];
    const link = `[§${first.number}](../chapters/${first.file}#${first.id})`;
    rows.push({
      display: symbol.display,
      meaning: symbol.meaning,
      first: link,
      count: hits.length,
    });
  }

  const table = [
    '| Symbol | Meaning | First defined | Sections using it |',
    '|:--|:--|:--|--:|',
    ...rows.map((r) => `| ${r.display} | ${r.meaning} | ${r.first} | ${r.count} |`),
  ].join('\n');

  fs.writeFileSync(
    out,
    `# Notation Index {.unnumbered}

The book uses the textbook's notation throughout. Each symbol below links to the
section where it is defined; the last column counts the sections that use it, so
a symbol with a single hit is probably described only in passing.

${table}

*Generated by \`scripts/build-notation.cjs\` from the chapter sources; re-run it after adding symbols.*
`,
  );

  console.log(`build-notation: ${rows.length} symbols -> ${out}`);
  for (const r of rows.slice(0, 3)) console.log(`  ${r.display} first at ${r.first} (${r.count} sections)`);
}

main();
