#!/usr/bin/env node
// Checks that every internal reference in the sources actually resolves.
//
// Three kinds, all of them silent when they break:
//   - [@key] citations with no entry in references.bib render as a bare "(?)"
//     in the PDF and an empty span on the site
//   - @fig-x references with no matching {#fig-x} label render as literal text
//   - gallery.qmd links chapters/<file>.html#<anchor>, which nothing validates,
//     so moving or renaming a heading breaks the gallery without any warning
//
// Usage: node scripts/check-refs.cjs

const fs = require('fs');
const path = require('path');

const CHAPTERS = fs
  .readdirSync('chapters')
  .filter((f) => f.endsWith('.qmd'))
  .map((f) => path.join('chapters', f));
const SOURCES = [...CHAPTERS, 'index.qmd', 'gallery.qmd'].filter((f) => fs.existsSync(f));

const problems = [];
const note = (file, line, message) => problems.push({ file, line, message });

// --- citations -------------------------------------------------------------
const bib = fs.existsSync('references.bib') ? fs.readFileSync('references.bib', 'utf8') : '';
const bibKeys = new Set([...bib.matchAll(/^@\w+\s*\{\s*([^,\s]+)/gm)].map((m) => m[1]));
if (!bibKeys.size) note('references.bib', 0, 'no bibliography keys found');

for (const file of SOURCES) {
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  lines.forEach((line, i) => {
    // [@key], [@key; @other], [@key, p. 3]
    for (const m of line.matchAll(/\[([^\]]*@[^\]]*)\]/g)) {
      for (const key of m[1].matchAll(/@([A-Za-z0-9_:.#$%&+?<>~/-]+)/g)) {
        if (!bibKeys.has(key[1])) {
          note(file, i + 1, `citation "@${key[1]}" is not in references.bib`);
        }
      }
    }
  });
}

// --- figure references -----------------------------------------------------
const figureIds = new Set();
for (const file of CHAPTERS) {
  for (const m of fs.readFileSync(file, 'utf8').matchAll(/\{#(fig-[A-Za-z0-9-]+)/g)) figureIds.add(m[1]);
}
for (const file of SOURCES) {
  fs.readFileSync(file, 'utf8')
    .split('\n')
    .forEach((line, i) => {
      for (const m of line.matchAll(/@(fig-[A-Za-z0-9-]+)/g)) {
        if (!figureIds.has(m[1])) note(file, i + 1, `reference "@${m[1]}" has no matching {#${m[1]}} label`);
      }
    });
}

// --- gallery anchors -------------------------------------------------------
const gallery = fs.existsSync('gallery.qmd') ? fs.readFileSync('gallery.qmd', 'utf8') : '';
const anchorIds = new Map(); // chapter file -> Set of ids
for (const file of CHAPTERS) {
  const ids = new Set();
  for (const m of fs.readFileSync(file, 'utf8').matchAll(/\{#([A-Za-z0-9-]+)/g)) ids.add(m[1]);
  anchorIds.set(path.basename(file, '.qmd'), ids);
}
let anchorCount = 0;
gallery.split('\n').forEach((line, i) => {
  for (const m of line.matchAll(/href="chapters\/([A-Za-z0-9-]+)\.html#([A-Za-z0-9-]+)"/g)) {
    anchorCount += 1;
    const [, chapter, anchor] = m;
    const ids = anchorIds.get(chapter);
    if (!ids) note('gallery.qmd', i + 1, `links to chapters/${chapter}.html, which is not a chapter file`);
    else if (!ids.has(anchor)) note('gallery.qmd', i + 1, `anchor #${anchor} does not exist in chapters/${chapter}.qmd`);
  }
});

// --- report ----------------------------------------------------------------
console.log(
  `check-refs: ${bibKeys.size} bib keys, ${figureIds.size} figure labels, ${anchorCount} gallery anchors checked`,
);
if (!problems.length) {
  console.log('  no broken references');
  process.exit(0);
}
for (const p of problems) console.log(`  ${p.file}:${p.line}: ${p.message}`);
console.log(`\ncheck-refs: ${problems.length} broken reference(s)`);
process.exit(1);
