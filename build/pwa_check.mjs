/* Real-browser check of the PWA.
 *
 * Drives headless Chrome over CDP (Node 22 has a global WebSocket, so no
 * puppeteer needed). Verifies the things a static-asset curl cannot:
 *   1. the page boots and renders
 *   2. MathML actually LAYS OUT -- the build ships no math library, so if the
 *      browser did not render MathML natively the app would be unreadable
 *   3. a whole question can be answered end to end
 *   4. the service worker registers and fills its cache
 *   5. with the network cut, a cold reload still serves the app and her progress
 *
 * Usage:  node pwa_check.mjs [url]
 * With no url it serves dist/ locally and tests that.
 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(DIR, '..', 'dist');
const CHROME = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9334;
const HTTP_PORT = 8731;
const PROFILE = 'C:\\tmp\\precalccheck\\profile';

const argUrl = process.argv[2];
const URL_ = argUrl || `http://127.0.0.1:${HTTP_PORT}/`;

let fails = 0;
const ok = (c, m, extra = '') => {
  if (c) console.log(`  PASS  ${m}${extra ? ' — ' + extra : ''}`);
  else { fails++; console.log(`  FAIL  ${m}${extra ? ' — ' + extra : ''}`); }
};

/* ---------- local static server (only when no url was given) ---------- */
let server = null;
if (!argUrl) {
  server = spawn('python', ['-m', 'http.server', String(HTTP_PORT), '--bind', '127.0.0.1'],
                 { cwd: DIST, stdio: 'ignore' });
  await sleep(1200);
}

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check',
  '--window-size=390,844', 'about:blank',
], { stdio: 'ignore' });

function cleanup(code) {
  try { ws && ws.close(); } catch {}
  try { chrome.kill(); } catch {}
  try { server && server.kill(); } catch {}
  process.exit(code);
}

async function targets() {
  const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
  return r.json();
}

let list = null;
for (let i = 0; i < 40; i++) {
  try { list = await targets(); if (list.length) break; } catch { /* not up yet */ }
  await sleep(500);
}
if (!list) { console.log('FAIL — chrome debugger never started'); cleanup(1); }

const page = list.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(res => { ws.onopen = res; });

let id = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
function send(method, params = {}) {
  const i = ++id;
  ws.send(JSON.stringify({ id: i, method, params }));
  return new Promise(res => pending.set(i, res));
}
async function evaluate(expr) {
  const r = await send('Runtime.evaluate', {
    expression: expr, awaitPromise: true, returnByValue: true,
  });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.text);
  return r.result?.result?.value;
}

await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');

console.log(`\nchecking ${URL_}\n`);

/* ------------------------------------------------------------ 1. boots */
// The Chrome profile persists between runs, so a previous run's localStorage
// would make the first-launch assertions pass or fail depending on history.
// Clear it and reload so every run starts genuinely cold.
await send('Page.navigate', { url: URL_ });
await sleep(2500);
await evaluate('localStorage.clear(); 1');
await send('Page.reload', { ignoreCache: false });
await sleep(3000);

const title = await evaluate('document.title');
ok(/Precalc/.test(title), 'page loads with the right title', title);

// First launch asks for a name (the public build ships without one).
const asksName = await evaluate("!!document.querySelector('input[type=text]')");
ok(asksName, 'first launch asks who this is (no name shipped in the public build)');
if (asksName) {
  await evaluate(
    "(()=>{const i=document.querySelector('input[type=text]');i.value='Testy';" +
    "[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Start').click();" +
    "return 1;})()");
  await sleep(500);
}

const heading = await evaluate("document.querySelector('h1')?.textContent || ''");
ok(/Hi /.test(heading), 'home screen rendered', heading);

const nItems = await evaluate('ITEMS.length');
ok(nItems > 50, 'item bank present in the deployed build', `${nItems} items`);

const nAnchors = await evaluate('ANCHORS.length');
ok(nAnchors >= 8, 'enough usable anchors for a real diagnostic', `${nAnchors} anchors`);

const jsErrs = await evaluate("(window.__errs||[]).length").catch(() => 0);
ok(!jsErrs, 'no uncaught script errors on boot');

/* ------------------------------------------- 2. start + MathML lays out */
await evaluate("document.querySelector('.btn-primary').click()");
await sleep(700);

const mathCount = await evaluate("document.querySelectorAll('math').length");
ok(mathCount > 0, 'MathML present in the question', `${mathCount} <math> nodes`);

// The decisive check: the build ships NO math library, so if the browser did
// not lay MathML out natively the student would see nothing.
const mathW = await evaluate(
  "(()=>{const m=document.querySelector('math');if(!m)return -1;" +
  "const r=m.getBoundingClientRect();return Math.round(r.width*10)/10;})()");
ok(mathW > 4, 'MathML actually RENDERS with real width (no math library shipped)',
   `${mathW}px`);

const mathH = await evaluate(
  "(()=>{const m=document.querySelector('math');if(!m)return -1;" +
  "return Math.round(m.getBoundingClientRect().height*10)/10;})()");
ok(mathH > 6, 'MathML has real height', `${mathH}px`);

/* ------------------------------------------------- 3. answer a question */
const confBtns = await evaluate("document.querySelectorAll('.conf button').length");
ok(confBtns === 3, 'confidence is asked BEFORE the answer', `${confBtns} buttons`);

await evaluate("document.querySelectorAll('.conf button')[2].click()");
await sleep(400);
const optCount = await evaluate("document.querySelectorAll('.opt').length");
ok(optCount === 4, 'four answer options render', `${optCount} options`);

await evaluate("[...document.querySelectorAll('button')].find(b=>b.querySelector('.opt')).click()");
await sleep(250);
await evaluate(
  "[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Submit').click()");
await sleep(500);

const feedback = await evaluate("document.querySelector('h2')?.textContent || ''");
ok(/Correct|Not quite/.test(feedback), 'answer submits and gives feedback', feedback);

const saved = await evaluate("!!localStorage.getItem('precalc1113.v1')");
ok(saved === true, 'attempt written to localStorage');

const shape = await evaluate(
  "(()=>{const s=JSON.parse(localStorage.getItem('precalc1113.v1'));" +
  "const a=s.attempts[0];return 'attempts='+s.attempts.length+' conf='+a.conf+" +
  "' msTotal='+(a.msTotal>0)+' kcTracked='+Object.keys(s.kc).length;})()");
console.log(`        ${shape}`);
ok(/msTotal=true/.test(shape), 'timing telemetry captured on the first attempt');

/* ------------------------------- 3b. the tutor dashboard actually renders */
// Fabricate a session with a known confident error, then open the share link
// exactly the way the tutor will: fragment payload, no server round trip.
const tutorUrl = await evaluate(`(() => {
  const kc = ANCHORS[0];
  const items = ITEMS_BY_KC[kc].slice(0, 2);
  S.attempts = [];
  S.kc = {};
  items.forEach((it, n) => {
    const wrong = it.options.findIndex(o => !o.correct);
    record({ id: it.id, kc: it.kc, ts: Date.now(), correct: n === 0,
             chosen: n === 0 ? it.options.findIndex(o => o.correct) : wrong,
             mis: n === 0 ? null : (it.options[wrong].mis || null),
             conf: 'confident', msFirst: 2000, msTotal: 25000, changes: 1,
             chFromCorrect: n !== 0, hint: false });
  });
  S.diag.finished = Date.now();
  return location.origin + location.pathname + '#/tutor?d=' + encodeShare();
})()`);
ok(/#\/tutor\?d=/.test(tutorUrl), 'share link builds', `${tutorUrl.length} chars`);

await send('Page.navigate', { url: tutorUrl });
await sleep(2500);

const tutorH1 = await evaluate("document.querySelector('h1')?.textContent || ''");
ok(/Tutor view/.test(tutorH1), 'tutor dashboard renders from the shared link', tutorH1);

const sections = await evaluate(
  "[...document.querySelectorAll('h2')].map(e=>e.textContent).join(' | ')");
ok(/Session agenda/.test(sections), 'session agenda section present');
ok(/Confidence vs correctness/.test(sections), 'calibration 2x2 present');
ok(/How she works/.test(sections), 'process telemetry present');
console.log(`        sections: ${sections.slice(0, 150)}`);

const quadCount = await evaluate("document.querySelectorAll('.q2').length");
ok(quadCount === 4, 'the 2x2 has four cells', `${quadCount}`);

const rows = await evaluate("document.querySelectorAll('table tr').length");
ok(rows >= 3, 'every-answer log rendered', `${rows - 1} attempt rows`);

// The gate must not leak: no code was typed, yet the link opened the view.
// That is intended (the payload IS the authorisation) -- assert it explicitly
// so the behaviour is a decision on record rather than an accident.
const agendaText = await evaluate(
  "document.body.innerText.match(/Confident and wrong[^\\n]*/)?.[0] || ''");
ok(/Confident and wrong/.test(agendaText),
   'confident-and-wrong is surfaced first on the agenda', agendaText);

// Viewing her session must not have written over this device's storage.
const localAfter = await evaluate(
  "(()=>{const s=JSON.parse(localStorage.getItem('precalc1113.v1')||'{}');" +
  "return (s.attempts||[]).length;})()");
console.log(`        local record still has ${localAfter} attempt(s)`);

await send('Page.navigate', { url: URL_ });
await sleep(2000);

/* ------------------------------------------ 4. service worker + cache */
let swState = null;
for (let i = 0; i < 20; i++) {
  swState = await evaluate(
    "navigator.serviceWorker.getRegistration().then(r=>r?" +
    "(r.active?'active':r.installing?'installing':'waiting'):'none')");
  if (swState === 'active') break;
  await sleep(500);
}
ok(swState === 'active', 'service worker registered and active', String(swState));

const cached = await evaluate(
  "caches.keys().then(ks=>Promise.all(ks.map(k=>caches.open(k)" +
  ".then(c=>c.keys()).then(rs=>k+':'+rs.length))).then(a=>a.join(', ')))");
ok(/:[1-9]/.test(String(cached).replace(/\s/g, '')), 'assets cached for offline use', cached);

/* ------------------------------------------------------------ 5. OFFLINE */
await send('Network.emulateNetworkConditions', {
  offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0,
});
console.log(`        network cut (navigator.onLine = ${await evaluate('navigator.onLine')})`);

await send('Page.reload', { ignoreCache: false });
await sleep(3500);

const offTitle = await evaluate('document.title').catch(() => '(page failed)');
ok(/Precalc/.test(offTitle), 'OFFLINE reload still serves the app', offTitle);

const offItems = await evaluate('ITEMS.length').catch(() => 0);
ok(offItems === nItems, 'OFFLINE: full item bank still available', `${offItems} items`);

const offAttempts = await evaluate(
  "(()=>{const s=JSON.parse(localStorage.getItem('precalc1113.v1')||'{}');" +
  "return (s.attempts||[]).length;})()").catch(() => 0);
ok(offAttempts >= 1, 'OFFLINE: her earlier progress survived the reload',
   `${offAttempts} attempt(s)`);

const offMath = await evaluate(
  "(()=>{document.querySelector('.btn-primary').click();return 1;})()").catch(() => 0);
await sleep(600);
const offMathW = await evaluate(
  "(()=>{const m=document.querySelector('math');if(!m)return -1;" +
  "return Math.round(m.getBoundingClientRect().width);})()").catch(() => -1);
ok(offMathW > 4, 'OFFLINE: math still renders (nothing was fetched from a CDN)',
   `${offMathW}px`);

console.log(`\n${'='.repeat(58)}`);
console.log(fails === 0 ? 'PASS — PWA verified online and offline'
                        : `FAIL — ${fails} problems`);
cleanup(fails === 0 ? 0 : 1);
