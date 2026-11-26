#!/usr/bin/env node
// Turns the notes into an Anki deck with native Anki MathJax (\(...\)).
//
// Every bullet that bolds a meaningful term becomes a cloze card, tagged by
// chapter and section. Promptless heading bullets (e.g. "**Goal**:" with only
// sub-bullets below) and generic structural labels ("not", "YES", "Pros") are
// skipped so every card stands on its own during review.
//
// Usage: node scripts/export-anki.cjs [--out path.tsv] [file.qmd ...]
//   default output: dist/anki/rl-notes.tsv
//
// The file is tab separated with header lines Anki understands, so
// File -> Import accepts it directly. #notetype:Cloze presets the built-in
// Cloze note type, which turns {{c1::...}} markers into real clozes.

const fs = require('fs');
const path = require('path');

const OUT_DEFAULT = path.join('dist', 'anki', 'rl-notes.tsv');

// Generic structural labels or emphasis words that make poor standalone clozes.
const SKIP_TERMS = new Set([
  'goal',
  'issue',
  'fix',
  'pros',
  'cons',
  'advantages',
  'disadvantages',
  'note',
  'example',
  'examples',
  'summary',
  'result',
  'results',
  'not',
  'yes',
  'no',
]);

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Convert markdown + inline $...$ LaTeX to Anki-safe HTML with native MathJax.
// Math spans are extracted before HTML/markdown formatting so TeX syntax is
// preserved intact (while still escaping < and > inside MathJax for #html:true).
function toAnkiHtml(text) {
  const mathSlots = [];
  let s = text;

  // Strip raw HTML comments if any
  s = s.replace(/<!--[\s\S]*?-->/g, '');
  // Convert markdown links [label](url) -> label
  s = s.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1');
  // Normalize inline display math $$...$$ into inline math $...$
  s = s.replace(/\$\$([^$]+)\$\$/g, '$$$1$$');

  // Protect inline math $...$ and convert to Anki MathJax \(...\)
  s = s.replace(/\$([^$\n]+)\$/g, (_, expr) => {
    const idx = mathSlots.length;
    mathSlots.push(`\\(${escapeHtml(expr.trim())}\\)`);
    return `\u0000M${idx}\u0000`;
  });

  // Escape HTML entities in prose so inequalities (<, >) aren't eaten as tags
  s = escapeHtml(s);

  // Convert inline code `...` -> <code>...</code>
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Strip remaining bold markers and convert *italic* / _italic_ to <em>
  s = s.replace(/\*\*\*/g, '');
  s = s.replace(/\*\*/g, '');
  s = s.replace(/(^|[\s([{"'])\*([^*\n]+?)\*(?=[\s)\]}.,;:!?"']|$)/g, '$1<em>$2</em>');
  s = s.replace(/(^|[\s([{"'])_([^_\n]+?)_(?=[\s)\]}.,;:!?"']|$)/g, '$1<em>$2</em>');

  // Restore MathJax spans
  s = s.replace(/\u0000M(\d+)\u0000/g, (_, idx) => mathSlots[Number(idx)]);

  return s.replace(/\s+/g, ' ').trim();
}

// Strip Quarto heading attributes like {#sec-ch07-7-1} or {.unnumbered}
// without chopping LaTeX commands like $\text{TD}(n)$ or $\overline{\text{VE}}$.
function cleanHeading(raw) {
  return raw
    .replace(/^#+\s+/, '')
    .replace(/\s*\{[#.][^}]*\}\s*$/, '')
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
    .replace(/\$[^$]*\$/g, ' ')
    .replace(/\\[a-zA-Z]+/g, ' ')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 40);
}

// Wrap a cloze answer safely: if the answer ends with '}', add a trailing space
// so Anki doesn't confuse LaTeX '}' with the cloze delimiter '}}', and escape '::'.
function formatCloze(answerHtml) {
  let safe = answerHtml.replace(/::/g, ': :');
  while (safe.includes('}}')) safe = safe.replace(/\}\}/g, '} }');
  if (safe.endsWith('}')) safe += ' ';
  return `{{c1::${safe}}}`;
}

// One entry per top-level bullet carrying a meaningful bold term and prompt context.
function cardsFrom(file, heading, bullets) {
  const cards = [];
  for (const { text, children } of bullets) {
    // Match ***bold-italic*** or **bold**
    const match = text.match(/\*\*\*([\s\S]+?)\*\*\*|\*\*([\s\S]+?)\*\*/);
    if (!match) continue;

    const rawMatch = match[0];
    const rawInner = (match[1] ?? match[2]).trim();
    const cleanedTerm = rawInner.replace(/[\s:;,.]+$/, '').trim();
    if (!cleanedTerm) continue;

    // Skip generic structural labels (e.g. "Goal", "Pros", "not", "YES")
    const plainCheck = cleanedTerm
      .replace(/\$[^$]*\$/g, '')
      .replace(/[*_`]/g, '')
      .trim()
      .toLowerCase();
    if (SKIP_TERMS.has(plainCheck)) continue;

    // Skip promptless header-only bullets (<= 2 non-cloze words outside the bold term)
    const outsideWords = text
      .replace(rawMatch, ' ')
      .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/[^A-Za-z0-9\s]/g, ' ')
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    if (outsideWords.length <= 2) continue;

    // Replace the exact first bold span with a placeholder before converting to HTML,
    // so we never accidentally cloze an earlier identical substring.
    const trail = rawInner.slice(cleanedTerm.length);
    const placeholder = '\u0001CLOZE_TARGET\u0001';
    const markedText = text.replace(rawMatch, `${placeholder}${trail}`);
    const bodyHtml = toAnkiHtml(markedText);
    const termHtml = toAnkiHtml(cleanedTerm);
    const front = bodyHtml.replace(placeholder, formatCloze(termHtml));

    const extraParts = [
      heading.section ? `Section: ${toAnkiHtml(heading.section)}` : null,
      ...children.map((c) => `• ${toAnkiHtml(c)}`),
    ].filter(Boolean);

    const tags = [
      'rl',
      file.replace(/^.*ch(\d+).*$/, 'ch$1'),
      ...heading.path.map(slug).filter(Boolean),
    ].join(' ');

    cards.push({ text: front, extra: extraParts.join('\n'), tags });
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
      h1 = cleanHeading(line);
      h2 = h3 = '';
      continue;
    }
    if (/^##\s+/.test(line)) {
      h2 = cleanHeading(line);
      h3 = '';
      continue;
    }
    if (/^###\s+/.test(line)) {
      h3 = cleanHeading(line);
      continue;
    }
    if (/^- /.test(line)) {
      bullets.push({
        text: line.replace(/^-\s+/, ''),
        children: [],
        heading: {
          section: [h1, h2, h3].filter(Boolean).join(' › '),
          path: [h2, h3].filter(Boolean),
        },
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
    .map((r) =>
      [r.text, r.extra, r.tags]
        .map((f) => f.replace(/\t/g, ' ').replace(/\n/g, '<br>'))
        .join('\t')
    )
    .join('\n');
  fs.writeFileSync(
    out,
    `#separator:tab\n#html:true\n#notetype:Cloze\n#tags column:3\n${body}\n`
  );

  console.log(`export-anki: ${rows.length} cards from ${bullets} bullets in ${sources.length} files`);
  console.log(`  written to ${out}`);
  const ratio = ((rows.length / bullets) * 100).toFixed(0);
  console.log(`  ${ratio}% of bullets become a cloze card`);
}

main();
