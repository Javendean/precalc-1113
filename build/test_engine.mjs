/* Headless test of the real engine.
 *
 * Loads dist/index.html, pulls out the app script, and runs it inside a vm
 * context with a minimal DOM shim. The point is to exercise the SHIPPED code,
 * not a reimplementation of it -- if the build inlines something broken, these
 * tests see exactly what a phone would see.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const HTML = fs.readFileSync(path.join(DIR, '..', 'dist', 'index.html'), 'utf8');

let fails = 0, checks = 0;
function ok(cond, msg) {
  checks++;
  if (!cond) { fails++; console.log('  FAIL  ' + msg); }
}

/* ----------------------------- DOM shim ----------------------------- */
function makeEl(id = '') {
  const el = {
    id, _html: '', className: '', style: {
      setProperty() {}, removeProperty() {}, getPropertyValue() { return ''; },
    },
    dataset: {}, disabled: false, children: [], onclick: null,
    type: '', value: '', placeholder: '', readOnly: false,
    classList: {
      _s: new Set(),
      add(...c) { c.forEach(x => this._s.add(x)); },
      remove(...c) { c.forEach(x => this._s.delete(x)); },
      toggle(c, on) { on ? this._s.add(c) : this._s.delete(c); },
      contains(c) { return this._s.has(c); },
    },
    setAttribute(k, v) { this[k] = v; },
    getAttribute(k) { return this[k]; },
    appendChild(c) { this.children.push(c); this.lastChild = c; return c; },
    removeChild(c) {
      const i = this.children.indexOf(c);
      if (i >= 0) this.children.splice(i, 1);
      return c;
    },
    get textContent() { return this._html.replace(/<[^>]*>/g, ''); },
    set textContent(v) { this._html = String(v); this.children = []; },
    get innerHTML() { return this._html; },
    set innerHTML(v) { this._html = String(v); this.children = []; },
    get outerHTML() { return this._html; },
    set outerHTML(v) { this._html = String(v); },
  };
  return el;
}
const els = new Map();
const document = {
  getElementById(id) {
    if (!els.has(id)) els.set(id, makeEl(id));
    return els.get(id);
  },
  createElement() { return makeEl(); },
  addEventListener() {},
};

let store = {};
const localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: k => { delete store[k]; },
};

const location = { hash: '#/', origin: 'https://example.test', pathname: '/precalc/' };

const sandbox = {
  document, localStorage, location, console,
  window: { scrollTo() {}, addEventListener() {} },
  navigator: {},
  setTimeout: fn => { fn(); return 0; },
  Math, JSON, Object, Array, String, Number, Set, Map, Date, isNaN, parseInt, parseFloat, RegExp,
};
sandbox.globalThis = sandbox;

/* ------------------------- load the app script ---------------------- */
const scripts = [...HTML.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(scripts.length === 1, `index.html has exactly one inline script (got ${scripts.length})`);

const src = scripts[0] + `
;globalThis.__T = {
  DATA, KCS, ITEMS, MIS, FAM, KC_BY_ID, ITEMS_BY_KC, ITEM_BY_ID, ANCHORS,
  DIAG_CAP, DIAG_TARGET, CONF_VALUE,
  bktUpdate, displayedProficiency, reviewPriority, prereqClosure, startPractice,
  weakKcs, getP: () => P,
  blank, load, save, kcState, tested, kcPassed, pickItem, buildPlan, nextEntry,
  onDiagnosticResult, record, rootCauses, familyFindings, calibration,
  queueDescent, rootKnownUnder,
  processStats, agenda, encodeShare, decodeShare, packSession, toB64u, fromB64u,
  getS: () => S, setS: v => { S = v; },
  setImporting: v => { VIEWING_IMPORT = v; }, isImporting: () => VIEWING_IMPORT,
  KEY,
};`;

vm.createContext(sandbox);
vm.runInContext(src, sandbox, { filename: 'app.js' });
const T = sandbox.__T;

console.log(`loaded: ${T.ITEMS.length} items · ${T.KCS.length} KCs · ` +
            `${T.ANCHORS.length} usable anchors · ${Object.keys(T.MIS).length} misconceptions\n`);

/* ===================================================================== */
console.log('1. item bank integrity');
/* ===================================================================== */
{
  const ids = new Set();
  let taggedDistractors = 0, totalDistractors = 0;
  for (const it of T.ITEMS) {
    ok(!ids.has(it.id), `duplicate item id ${it.id}`);
    ids.add(it.id);
    ok(!!T.KC_BY_ID[it.kc], `${it.id}: unknown kc ${it.kc}`);
    ok(it.options.length === 4, `${it.id}: ${it.options.length} options`);
    const correct = it.options.filter(o => o.correct);
    ok(correct.length === 1, `${it.id}: ${correct.length} correct options`);
    const texts = it.options.map(o => o.text);
    ok(new Set(texts).size === 4, `${it.id}: duplicate option text`);
    ok(!!it.stem && it.stem.length > 0, `${it.id}: empty stem`);
    for (const o of it.options) {
      if (o.correct) { ok(!o.mis, `${it.id}: correct option carries a misconception tag`); continue; }
      totalDistractors++;
      if (o.mis) {
        taggedDistractors++;
        ok(!!T.MIS[o.mis], `${it.id}: unresolvable misconception ${o.mis}`);
      }
    }
  }
  const pct = Math.round(100 * taggedDistractors / Math.max(1, totalDistractors));
  console.log(`   ${T.ITEMS.length} items · ${taggedDistractors}/${totalDistractors} ` +
              `distractors carry a diagnosis (${pct}%)`);
  ok(pct >= 70, `only ${pct}% of distractors are diagnostic; the tutor report degrades below ~70%`);
}

/* ===================================================================== */
console.log('\n2. prerequisite graph');
/* ===================================================================== */
{
  for (const k of T.KCS) {
    const c = T.prereqClosure(k.id);
    ok(c.indexOf(k.id) < 0, `${k.id}: appears in its own prereq closure (cycle)`);
    // deepest-first: a KC must appear after everything it depends on
    for (let i = 0; i < c.length; i++) {
      for (const p of T.KC_BY_ID[c[i]].prereqs) {
        const j = c.indexOf(p);
        ok(j < 0 || j < i, `${k.id}: closure order violated -- ${p} after ${c[i]}`);
      }
    }
  }
  const deep = T.KCS.map(k => [k.id, T.prereqClosure(k.id).length])
                    .sort((a, b) => b[1] - a[1])[0];
  console.log(`   all closures acyclic and deepest-first; deepest is ${deep[0]} (${deep[1]})`);
}

/* ===================================================================== */
console.log('\n3. BKT behaves');
/* ===================================================================== */
{
  let p = 0.3;
  for (let i = 0; i < 6; i++) { const q = T.bktUpdate(p, true); ok(q > p, 'correct must raise P(known)'); p = q; }
  ok(p > 0.9, `six correct answers should approach mastery (got ${p.toFixed(3)})`);
  let w = 0.9;
  for (let i = 0; i < 4; i++) { const q = T.bktUpdate(w, false); ok(q < w, 'wrong must lower P(known)'); w = q; }
  ok(T.bktUpdate(0, true) >= 0 && T.bktUpdate(1, false) <= 1, 'P stays in [0,1]');
  ok(T.displayedProficiency(1.0, 0) > T.displayedProficiency(1.0, 96), 'stale knowledge decays');
  ok(T.reviewPriority(0.9, false, 1) > T.reviewPriority(0.2, false, 1),
     'confident errors must outrank unsure errors');
}

/* ===================================================================== */
console.log('\n4. the descent finds a PLANTED root cause');
/* ===================================================================== */
function simulate(brokenSet, label) {
  store = {};
  const S = T.blank();
  T.setS(S);
  S.diag.started = Date.now();
  S.diag.plan = T.buildPlan();
  S.diag.idx = 0;
  S.diag.desc = [];
  S.diag.didx = 0;
  S.diag.asked = [];
  const askedKcs = [];

  // A KC is answered correctly iff it is not broken and nothing it depends on
  // is broken -- i.e. breakage propagates upward, like it does in a real student.
  const answers = id =>
    !brokenSet.has(id) && !T.prereqClosure(id).some(p => brokenSet.has(p));

  let guard = 0;
  for (;;) {
    if (++guard > 500) { ok(false, `${label}: diagnostic did not terminate`); break; }
    const e = T.nextEntry();
    if (!e) break;
    const item = T.pickItem(e.kc, e.depth === 0 ? 3 : 2);
    if (!item) { T.getS().diag.idx++; continue; }
    const correct = answers(e.kc);
    const wrongOpt = item.options.filter(o => !o.correct)[0];
    askedKcs.push(e.kc);
    S.diag.asked.push(item.id);
    T.record({
      id: item.id, kc: item.kc, ts: Date.now(), correct,
      chosen: correct ? item.options.findIndex(o => o.correct) : item.options.indexOf(wrongOpt),
      mis: correct ? null : (wrongOpt.mis || null),
      conf: correct ? 'confident' : 'shaky',
      msFirst: 3000, msTotal: 30000, changes: 0, chFromCorrect: false, hint: false,
    });
    T.onDiagnosticResult(e, correct);
  }
  return { S, asked: S.diag.asked.length, askedKcs };
}

{
  const broken = new Set(['exp_negative']);
  const { asked } = simulate(broken, 'exp_negative');
  const roots = T.rootCauses().map(r => r.kc);
  ok(asked > 0, 'diagnostic asked at least one question');
  ok(asked <= T.DIAG_CAP, `asked ${asked} questions, cap is ${T.DIAG_CAP}`);
  ok(roots.indexOf('exp_negative') >= 0,
     `planted root exp_negative not reported (got: ${roots.join(', ') || 'none'})`);
  // The whole thesis: it must NOT blame the downstream symptom.
  const logRoots = roots.filter(r => r.indexOf('log_') === 0);
  ok(logRoots.length === 0,
     `blamed downstream symptom(s) ${logRoots.join(',')} instead of the prerequisite`);
  console.log(`   broke exp_negative -> asked ${asked} questions -> roots: ${roots.join(', ')}`);
}
{
  const broken = new Set(['unit_circle']);
  const { asked } = simulate(broken, 'unit_circle');
  const roots = T.rootCauses().map(r => r.kc);
  ok(roots.indexOf('unit_circle') >= 0,
     `planted root unit_circle not reported (got: ${roots.join(', ') || 'none'})`);
  console.log(`   broke unit_circle  -> asked ${asked} questions -> roots: ${roots.join(', ')}`);
}
{
  const { asked } = simulate(new Set(), 'perfect student');
  const roots = T.rootCauses();
  ok(roots.length === 0, `a student who gets everything right has ${roots.length} root causes`);
  ok(asked <= T.DIAG_CAP, 'perfect run respects the cap');
  console.log(`   perfect student    -> asked ${asked} questions -> no roots (correct)`);
}
{
  // Worst case: everything broken. Must still terminate inside the cap.
  const all = new Set(T.KCS.map(k => k.id));
  const { asked } = simulate(all, 'everything broken');
  ok(asked <= T.DIAG_CAP, `worst case asked ${asked}, cap is ${T.DIAG_CAP}`);
  console.log(`   everything broken  -> asked ${asked} questions (cap ${T.DIAG_CAP})`);
}

/* --- coverage: struggling early must not cost her the later chapters --- */
{
  // A student broken in the very first chapter must STILL be asked every
  // anchor, or the report would silently say nothing about trigonometry.
  for (const [broken, label] of [
    [new Set(['distribute', 'signed_numbers', 'frac_arith']), 'broken in chapter 1'],
    [new Set(T.KCS.map(k => k.id)), 'broken everywhere'],
  ]) {
    const { askedKcs } = simulate(broken, label);
    const missed = T.ANCHORS.filter(a => askedKcs.indexOf(a) < 0);
    ok(missed.length === 0,
       `${label}: ${missed.length} anchors never asked (${missed.slice(0, 5).join(', ')})`);
    const trig = askedKcs.filter(k => /trig|unit_circle|angles|inverse_trig/.test(k)).length;
    ok(trig > 0, `${label}: trigonometry never probed at all`);
    console.log(`   ${label}: all ${T.ANCHORS.length} anchors asked, ${trig} trig probes`);
  }
}

/* ===================================================================== */
console.log('\n5. tutor analytics');
/* ===================================================================== */
{
  simulate(new Set(['exp_negative', 'distribute']), 'analytics');
  const S = T.getS();
  const st = T.processStats();
  ok(st && st.n === S.attempts.length, 'processStats counts every attempt');
  const cal = T.calibration();
  const sum = cal.confRight.length + cal.confWrong.length +
              cal.unsureRight.length + cal.unsureWrong.length;
  ok(sum === S.attempts.length, `calibration 2x2 sums to ${sum}, expected ${S.attempts.length}`);
  const fams = T.familyFindings();
  for (const f of fams) {
    ok(!!T.FAM[f.family], `family finding references unknown family ${f.family}`);
    ok(f.count > 0 && f.spread > 0, 'family finding has real counts');
    ok(!!f.fix && f.fix.length > 20, `family ${f.family} has no usable fix text`);
  }
  const ag = T.agenda();
  for (const g of ag) {
    ok(!!g.title && !!g.why && !!g.how, 'every agenda entry is actionable');
  }
  console.log(`   ${st.n} attempts · ${fams.length} error families · ${ag.length} agenda items`);
}

/* ===================================================================== */
console.log('\n6. share payload round-trips');
/* ===================================================================== */
{
  simulate(new Set(['unit_circle']), 'share');
  const before = T.getS();
  const code = T.encodeShare();
  ok(/^[A-Za-z0-9\-_]+$/.test(code), 'share code is URL-safe');
  const { state, stale } = T.decodeShare(code);
  ok(!stale, 'round-trip is not flagged stale');
  ok(state.attempts.length === before.attempts.length,
     `decoded ${state.attempts.length} attempts, expected ${before.attempts.length}`);
  ok(state.name === before.name, 'name survives the round trip');
  for (let i = 0; i < state.attempts.length; i++) {
    const a = before.attempts[i], b = state.attempts[i];
    ok(a.id === b.id && a.correct === b.correct && a.conf === b.conf &&
       a.msTotal === b.msTotal && (a.mis || null) === (b.mis || null),
       `attempt ${i} corrupted in transit`);
  }
  // The tutor view rebuilds its analysis from the decoded state alone.
  T.setS(state);
  const roots = T.rootCauses().map(r => r.kc);
  ok(roots.indexOf('unit_circle') >= 0, 'analysis survives the transfer');
  console.log(`   ${code.length} chars · ${state.attempts.length} attempts · analysis intact`);

  let threw = false;
  try { T.decodeShare('not-a-real-code'); } catch (e) { threw = true; }
  ok(threw, 'a malformed code must throw rather than render nonsense');

  // Unicode must survive: MathML uses U+2212 and friends.
  ok(T.fromB64u(T.toB64u('a−b · π')) === 'a−b · π',
     'base64 round-trip preserves non-ASCII');
}

/* ===================================================================== */
console.log('\n6b. viewing a shared session never overwrites the viewer\'s own data');
/* ===================================================================== */
{
  // Javen opens her link on HIS phone. His own record must survive.
  simulate(new Set(['exp_negative']), 'his own data');
  const his = JSON.stringify(T.getS());
  store[T.KEY] = his;

  const hers = T.blank();
  hers.name = 'Someone Else';
  hers.attempts = [];
  T.setImporting(true);
  T.setS(hers);
  T.save();
  ok(store[T.KEY] === his, 'save() is inert while an imported session is on screen');

  T.setImporting(false);
  T.load();
  ok(T.getS().name !== 'Someone Else', 'his own session reloads after leaving the tutor view');
  console.log('   imported session is read-only; local record intact');
}

/* ===================================================================== */
console.log('\n6c. practice puts confident-and-wrong first');
/* ===================================================================== */
{
  store = {};
  const S = T.blank();
  S.name = 'X';
  T.setS(S);
  const kc = T.ANCHORS.find(a => (T.ITEMS_BY_KC[a] || []).length >= 3);
  const pool = T.ITEMS_BY_KC[kc];
  // She answered the LAST item confidently and got it wrong; the first she got
  // right while unsure. Practice must lead with the confident error.
  const wrongOne = pool[pool.length - 1];
  T.record({ id: pool[0].id, kc, ts: Date.now(), correct: true, chosen: 0, mis: null,
             conf: 'guessing', msFirst: 1000, msTotal: 9000, changes: 0,
             chFromCorrect: false, hint: false });
  T.record({ id: wrongOne.id, kc, ts: Date.now(), correct: false, chosen: 1,
             mis: null, conf: 'confident', msFirst: 1000, msTotal: 9000, changes: 0,
             chFromCorrect: false, hint: false });
  T.startPractice(kc);
  const q = T.getP();
  ok(q && q.queue.length > 0, 'practice builds a queue');
  ok(q.queue[0].id === wrongOne.id,
     `practice leads with the confident error (got ${q.queue[0] && q.queue[0].id}, ` +
     `expected ${wrongOne.id})`);
  ok(T.reviewPriority(0.88, false, 1) > T.reviewPriority(0.88, true, 3),
     'a confident error outranks a confident success');
  console.log(`   ${kc}: queue leads with ${q.queue[0].id} (answered confidently, wrong)`);
}

/* ===================================================================== */
console.log('\n7. every KC used by the diagnostic actually has items');
/* ===================================================================== */
{
  for (const a of T.ANCHORS) {
    ok((T.ITEMS_BY_KC[a] || []).length > 0, `anchor ${a} has no items but is in the plan`);
  }
  const plan = T.buildPlan();
  ok(plan.length === T.ANCHORS.length, 'plan covers every usable anchor');
  ok(plan.every(e => e.depth === 0), 'initial plan is anchors only');
  console.log(`   ${plan.length} anchors planned, all backed by items`);
}

/* ===================================================================== */
console.log(`\n${checks - fails}/${checks} checks passed`);
if (fails) { console.log(`${fails} FAILURES`); process.exit(1); }
console.log('ALL GREEN');
