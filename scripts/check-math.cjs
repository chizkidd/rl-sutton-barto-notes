#!/usr/bin/env node
// Renders every math chunk in the book through KaTeX -- the renderer the HTML
// build actually uses ("html-math-method: katex" in _quarto.yml) -- and fails
// when KaTeX cannot parse a chunk, or when the text it draws contains a
// literal "$".
//
// The PDF goes through LaTeX and the browser goes through KaTeX, so anything
// only one of them understands never shows up in the source or the PDF: it
// surfaces as a red error box or visible TeX in the HTML edition alone.
//
// KaTeX's MathML annotation repeats the source TeX ("$" and all), so the check
// renders HTML-only output and inspects the characters that are actually drawn.
//
// Usage: node scripts/check-math.cjs [file.qmd ...]
//   KATEX_DIR  path to an installed katex package (default: normal resolution)

const fs = require('fs');
const path = require('path');

const katexDir = process.env.KATEX_DIR || 'katex';
let katex;
try {
  katex = require(katexDir);
} catch (err) {
  console.error(`check-math: cannot load KaTeX from "${katexDir}" (set KATEX_DIR, or install katex).`);
  process.exit(2);
}

const SKIP_DIRS = new Set(['_site', '.quarto', '.preview', 'node_modules', 'artifacts', 'figures', '.git']);

function collect(dir, out) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name)) collect(path.join(dir, entry.name), out);
    } else if (entry.name.endsWith('.qmd')) {
      out.push(path.join(dir, entry.name));
    }
  }
  return out;
}

// Blank out regions that never reach KaTeX, keeping every newline so that line
// numbers still point at the original source: HTML comments, fenced code, and
// inline code spans (which may legitimately contain "$").
function sanitize(src) {
  const blank = (m) => m.replace(/[^\n]/g, ' ');
  return src
    .replace(/<!--[\s\S]*?-->/g, blank)
    .replace(/^```[\s\S]*?^```/gm, blank)
    .replace(/`[^`\n]*`/g, blank);
}

function extract(text) {
  const chunks = [];
  const n = text.length;
  let i = 0;
  while (i < n) {
    const c = text[i];
    if (c === '\\') {
      const open = text[i + 1];
      if (open === '(' || open === '[') {
        const close = open === '(' ? '\\)' : '\\]';
        const end = text.indexOf(close, i + 2);
        if (end > 0) {
          chunks.push({ start: i + 2, end, display: open === '[' });
          i = end + 2;
          continue;
        }
      }
      i += 2;
      continue;
    }
    if (c === '$') {
      if (text[i + 1] === '$') {
        let end = text.indexOf('$$', i + 2);
        if (end < 0) {
          chunks.push({ start: i, end: n, display: true, unclosed: true });
          break;
        }
        chunks.push({ start: i + 2, end, display: true });
        i = end + 2;
        continue;
      }
      let j = i + 1;
      let end = -1;
      while (j < n) {
        if (text[j] === '\\') { j += 2; continue; }
        if (text[j] === '$') {
          if (text[j + 1] === '$') { j += 2; continue; }
          end = j;
          break;
        }
        j++;
      }
      if (end > 0) {
        chunks.push({ start: i + 1, end, display: false });
        i = end + 1;
        continue;
      }
    }
    i++;
  }
  return chunks.map((ch) => ({ ...ch, tex: text.slice(ch.start, ch.end) }));
}

const lineOf = (text, idx) => text.slice(0, idx).split('\n').length;
const snippet = (s) => s.replace(/\s+/g, ' ').trim().slice(0, 90);

const args = process.argv.slice(2);
const files = args.length ? args : collect(process.cwd(), []);

if (!files.length) {
  console.error('check-math: no .qmd files found');
  process.exit(2);
}

let checked = 0;
const failures = [];

for (const file of files) {
  const text = sanitize(fs.readFileSync(file, 'utf8'));
  for (const chunk of extract(text)) {
    checked++;
    const where = `${file}:${lineOf(text, chunk.start)}`;
    const kind = chunk.display ? 'display' : 'inline';

    if (chunk.unclosed) {
      failures.push(`${where} [display] unclosed "$$" delimiter\n    ${snippet(chunk.tex)}`);
      continue;
    }

    let html;
    try {
      html = katex.renderToString(chunk.tex, {
        displayMode: chunk.display,
        throwOnError: true,
        strict: 'ignore',
        output: 'html',
      });
    } catch (err) {
      failures.push(`${where} [${kind}] does not parse: ${String(err.message).replace(/\s+/g, ' ')}\n    ${snippet(chunk.tex)}`);
      continue;
    }

    // Escape hatches such as \$5 are meant to print a dollar sign.
    const plain = html.replace(/<[^>]*>/g, '');
    if (plain.includes('$') && !chunk.tex.includes('\\$')) {
      failures.push(`${where} [${kind}] prints a literal "$" in the HTML build\n    ${snippet(chunk.tex)}`);
    }
  }
}

const version = (katex.version || 'unknown');
if (failures.length) {
  console.error(`\n${failures.length} math problem(s) found (KaTeX ${version}):\n`);
  for (const f of failures) console.error(`  ${f}\n`);
  console.error('These render correctly in the PDF but not in the HTML edition.');
  process.exit(1);
}

console.log(`check-math: ${checked} math chunks in ${files.length} files render cleanly (KaTeX ${version})`);
