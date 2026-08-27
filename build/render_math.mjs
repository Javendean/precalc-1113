/* Convert every $...$ LaTeX span in the item bank to MathML, at BUILD time.
 *
 * The point is that the shipped app carries no math library at all: no KaTeX
 * JS, no web fonts, no CDN. MathML Core is native in current Chrome, Safari and
 * Firefox, so a phone renders it with zero bytes downloaded.
 *
 * Usage:  node render_math.mjs <in.json> <out.json>
 * A LaTeX parse error is fatal -- shipping a broken formula to a student who is
 * already unsure of herself is worse than failing the build.
 */
import fs from 'node:fs';
import katex from './vendor/katex/katex.mjs';

const [, , inPath, outPath] = process.argv;
if (!inPath || !outPath) {
  console.error('usage: node render_math.mjs <in.json> <out.json>');
  process.exit(2);
}

let errors = 0, rendered = 0;

function renderTex(tex, where) {
  try {
    rendered++;
    return katex.renderToString(tex, {
      output: 'mathml',
      throwOnError: true,
      strict: false,
      trust: false,
displayMode: false,
    });
  } catch (e) {
    errors++;
    console.error(`  LaTeX error in ${where}: ${tex}\n    ${e.message.split('\n')[0]}`);
    return null;
  }
}

/* Split on single-dollar math, leaving surrounding prose untouched. */
function convert(s, where) {
  if (typeof s !== 'string' || s.indexOf('$') < 0) return escapeHtml(s);
  let out = '', i = 0;
  while (i < s.length) {
    const a = s.indexOf('$', i);
    if (a < 0) { out += escapeHtml(s.slice(i)); break; }
    const b = s.indexOf('$', a + 1);
    if (b < 0) { out += escapeHtml(s.slice(i)); break; }
    out += escapeHtml(s.slice(i, a));
    const html = renderTex(s.slice(a + 1, b), where);
    out += html === null ? escapeHtml(s.slice(a, b + 1)) : html;
    i = b + 1;
  }
  return out;
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* A readable, math-free version for places that must not emit markup
   (the tutor probe list, share payloads, test output).
   Brace groups nest -- \dfrac{x^{-3}}{x^{5}} -- so this matches braces by
   counting rather than by regex, which silently fails on the nested case. */
function readGroup(s, i) {
  // s[i] must be '{'; returns [contents, indexAfterClosingBrace]
  if (s[i] !== '{') return [null, i];
  let depth = 0;
  for (let j = i; j < s.length; j++) {
    if (s[j] === '{') depth++;
    else if (s[j] === '}') {
      depth--;
      if (depth === 0) return [s.slice(i + 1, j), j + 1];
    }
  }
  return [null, i];
}

function texToText(t) {
  let out = '', i = 0;
  while (i < t.length) {
    if (t[i] === '\\') {
      const m = /^\\([a-zA-Z]+)/.exec(t.slice(i));
      if (m) {
        const cmd = m[1];
        let j = i + m[0].length;
        if (cmd === 'dfrac' || cmd === 'frac' || cmd === 'tfrac') {
          const [a, j1] = readGroup(t, j);
          const [b, j2] = readGroup(t, j1);
          if (a !== null && b !== null) {
            out += '(' + texToText(a) + ')/(' + texToText(b) + ')';
            i = j2; continue;
          }
        } else if (cmd === 'sqrt') {
          const [a, j1] = readGroup(t, j);
          if (a !== null) { out += 'sqrt(' + texToText(a) + ')'; i = j1; continue; }
        } else if (cmd === 'left' || cmd === 'right') {
          i = j; continue;
        } else {
          out += cmd; i = j; continue;
        }
      }
      out += t[i] === '\\' ? '' : t[i];
      i++; continue;
    }
    if (t[i] === '{' || t[i] === '}') { i++; continue; }
    out += t[i]; i++;
  }
  return out;
}

function plain(s) {
  return String(s)
    .replace(/\$([^$]*)\$/g, (_, t) => texToText(t).replace(/\s+/g, ' ').trim())
    .replace(/\s+/g, ' ')
    .trim();
}

const bank = JSON.parse(fs.readFileSync(inPath, 'utf8'));

for (const it of bank.items) {
  const w = it.id;
  it.plain = plain(it.stem);
  it.stem = convert(it.stem, w + '.stem');
  it.hint = convert(it.hint, w + '.hint');
  it.worked = (it.worked || []).map((s, i) => convert(s, `${w}.worked[${i}]`));
  it.options = it.options.map((o, i) => ({
    ...o,
    plain: plain(o.text),
    text: convert(o.text, `${w}.opt[${i}]`),
  }));
}

fs.writeFileSync(outPath, JSON.stringify(bank));
console.log(`rendered ${rendered} LaTeX spans across ${bank.items.length} items; ${errors} errors`);
if (errors) process.exit(1);
