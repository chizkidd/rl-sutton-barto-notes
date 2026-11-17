#!/usr/bin/env node
// Reports which sections of the textbook these notes actually cover.
//
// "All 13 chapters" is true but coarse: the second edition has 121 sections, and
// a chapter can look complete while a whole section is missing. This compares
// the book's real table of contents (data/book-toc.json, extracted from the
// official PDF) against the `##` headings of each chapter file.
//
// The notes condense and rename sections, so titles never match exactly, but
// both lists follow the same order. That makes this an alignment problem rather
// than a lookup: match the two sequences in order and allow either side to skip,
// which is what stops a heading from being paired with the wrong section just
// because it shares a word.
//
// Usage: node scripts/coverage.cjs [--json] [--fail-under N]

const fs = require('fs');
const path = require('path');

const TOC = path.join('data', 'book-toc.json');
const STOP = new Set(['the', 'a', 'an', 'of', 'and', 'to', 'in', 'for', 'with', 'on', 'as', 'is', 'are', 'its', 'it']);
const MATCH_FLOOR = 0.45; // share of the shorter title's words that must appear
const GAP = -0.3; // cost of skipping a section or a heading during alignment

function tokens(text) {
  return new Set(
    text
      .toLowerCase()
      .replace(/&/g, 'and')
      .replace(/\\[a-zA-Z]+/g, ' ')
      .replace(/[^a-z0-9 ]+/g, ' ')
      .split(/\s+/)
      .filter((w) => w && !STOP.has(w)),
  );
}

function similarity(a, b) {
  const ta = tokens(a);
  const tb = tokens(b);
  if (!ta.size || !tb.size) return 0;
  let shared = 0;
  for (const t of ta) if (tb.has(t)) shared += 1;
  return shared / Math.min(ta.size, tb.size);
}

function headings(file) {
  return fs
    .readFileSync(file, 'utf8')
    .split('\n')
    .filter((l) => /^##\s+/.test(l))
    .map((l) => l.replace(/^##\s+/, '').replace(/\{.*$/, '').trim());
}

// Needleman-Wunsch over the two ordered lists. Returns the matched pairs and
// the headings that ended up covering no section.
function align(sections, notes) {
  const n = sections.length;
  const m = notes.length;
  const score = Array.from({ length: n }, (_, i) => notes.map((h) => similarity(sections[i].title, h)));
  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));

  for (let i = 1; i <= n; i += 1) {
    for (let j = 1; j <= m; j += 1) {
      const match = score[i - 1][j - 1] >= MATCH_FLOOR ? dp[i - 1][j - 1] + score[i - 1][j - 1] : -Infinity;
      dp[i][j] = Math.max(match, dp[i - 1][j] + GAP, dp[i][j - 1] + GAP);
    }
  }

  const pairs = [];
  let i = n;
  let j = m;
  while (i > 0 && j > 0) {
    const s = score[i - 1][j - 1];
    if (s >= MATCH_FLOOR && Math.abs(dp[i][j] - (dp[i - 1][j - 1] + s)) < 1e-9) {
      pairs.push({ section: sections[i - 1], heading: notes[j - 1], score: s });
      i -= 1;
      j -= 1;
    } else if (dp[i][j] === dp[i - 1][j] + GAP) {
      i -= 1;
    } else {
      j -= 1;
    }
  }
  pairs.reverse();

  const used = new Set(pairs.map((p) => p.heading));
  return { pairs, extra: notes.filter((h) => !used.has(h)) };
}

function main() {
  const args = process.argv.slice(2);
  const failUnder = args.includes('--fail-under') ? Number(args[args.indexOf('--fail-under') + 1]) : null;

  const toc = JSON.parse(fs.readFileSync(TOC, 'utf8'));
  const chapters = fs
    .readdirSync('chapters')
    .filter((f) => /^ch\d+.*\.qmd$/.test(f))
    .sort();

  const report = [];
  for (const file of chapters) {
    const number = Number(file.match(/^ch(\d+)/)[1]);
    const notes = headings(path.join('chapters', file));
    const sections = Object.entries(toc)
      .filter(([key]) => Number(key.split('.')[0]) === number)
      .sort(([a], [b]) => Number(a.split('.')[1]) - Number(b.split('.')[1]))
      .map(([key, title]) => ({ key, title }));

    const { pairs, extra } = align(sections, notes);
    const covered = new Set(pairs.map((p) => p.section.key));
    report.push({
      chapter: number,
      file,
      book: sections.length,
      covered: pairs.length,
      missing: sections.filter((s) => !covered.has(s.key)),
      pairs: pairs.map((p) => ({ key: p.section.key, title: p.section.title, notes: p.heading, score: Number(p.score.toFixed(2)) })),
      extra,
    });
  }

  if (args.includes('--json')) {
    console.log(JSON.stringify(report, null, 2));
    return 0;
  }

  let totalBook = 0;
  let totalCovered = 0;
  console.log('Section coverage against Sutton & Barto, 2nd edition\n');
  for (const row of report) {
    totalBook += row.book;
    totalCovered += row.covered;
    const pct = row.book ? Math.round((row.covered / row.book) * 100) : 0;
    console.log(`ch${String(row.chapter).padStart(2, '0')}  ${row.covered}/${row.book} sections (${pct}%)`);
    for (const m of row.missing) console.log(`   missing ${m.key}  ${m.title}`);
  }
  const pct = Math.round((totalCovered / totalBook) * 100);
  console.log(`\n${totalCovered}/${totalBook} sections covered (${pct}%)`);

  if (failUnder !== null && pct < failUnder) {
    console.error(`coverage ${pct}% is below the required ${failUnder}%`);
    return 1;
  }
  return 0;
}

process.exit(main());
