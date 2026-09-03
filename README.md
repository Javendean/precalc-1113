# Precalc 1113

An adaptive diagnostic and practice PWA for MATH 1113 Precalculus. It does two things a
graded quiz cannot: it finds the *prerequisite* underneath a wrong answer, and it reports
*which rule the student actually applied* to get there.

Static, offline-capable, installable, no backend. Built for one real student and in use.

**Live:** https://javendean.github.io/precalc-1113/

---

## The engineering idea

### 1. Prerequisite descent

`build/kc_graph.py` holds 58 knowledge components in two tiers, joined by real dependency
edges — not curricular order.

- **Tier 0 (19 KCs)** is the algebra substrate: exponent laws, factoring, fraction
  arithmetic, signs, radicals.
- **Tier 1 (39 KCs)** is precalculus proper, chaptered against OpenStax Precalculus 2e.

A student failing precalculus rarely has a precalculus problem. `log_solve` sits on a 20-KC
prerequisite closure that bottoms out at `exp_laws` and `frac_arith`. The student reports the
problem as "logs." The graph is what lets the app disagree.

The diagnostic runs breadth-first, then depth:

```
Phase 1  ask all 22 anchor KCs once      -> the report covers the whole course
Phase 2  for each anchor that failed:
           walk prereq_closure(anchor) DEEPEST-FIRST, one item per KC,
           stop that branch at the first prerequisite that also fails
```

The deepest still-failing KC is the root cause; everything above it is collateral. Phase 1
comes first on purpose: if descents were spliced in inline, a student who struggled in
chapter 1 would spend the whole question budget there and the report would say nothing at
all about trigonometry.

That is why a whole-course diagnostic fits in ~26 questions (hard cap 32) instead of 200,
and why the report can say *"negative exponents, which is why logarithms look broken"*
instead of *"weak on logarithms."* `build/kc_graph.py` fails the build on a cycle or an
unknown prerequisite id, because a broken graph means a wrong root cause.

### 2. Misconception-tagged distractors

`build/misconceptions.py` holds 51 named misconceptions grouped into 8 error families. Every
wrong option in the bank carries a misconception id, and the option text is the value a
student actually gets by committing exactly that error on that stem. So a wrong answer
returns a diagnosis, not just a zero.

The family layer is the part that changes a tutoring session. A student who writes all three of

```
(a+b)² = a² + b²     log(a+b) = log a + log b     sin(A+B) = sin A + sin B
```

does not have an algebra problem, a logarithm problem and a trigonometry problem. She has one
belief — that everything distributes over addition — costing her marks in three chapters.
`LINEARITY_ILLUSION` reports that as a single finding with a single fix, and carries the
whiteboard fix and a one-question probe with it.

### 3. Process telemetry

Per item, silently: pre-answer confidence, time to first interaction, total time, answer
changes (tracked directionally — right→wrong is a different pathology from wrong→right),
whether the hint was opened, and the misconception behind the chosen distractor.

Crossing confidence with correctness gives the 2×2 a grade cannot: confident-and-wrong is a
misconception the student will resist, unsure-and-right is fragile knowledge that needs
consolidation, not reteaching. Confident-and-wrong is ranked first on the tutor's agenda and
first in the practice queue.

Proficiency is a per-KC BKT posterior (`L0=0.30, T=0.35, slip=0.10, guess=0.25`) with recency
decay. Because the diagnostic contributes only 1–2 observations per KC, every figure is shown
with its evidence count and anything under 2 observations renders as provisional. Elo and
Leitner from the source engine were deliberately left out: no exam date and a handful of
sessions means neither would ever accumulate enough observations to mean anything.

---

## What it produces

**For the student** — an adaptive check-up of about 26 questions, thin feedback during it so
measurement stays clean, then a results screen that leads with what is solid, names two or
three focus areas, and lets her review every miss with full working. Then targeted practice
on the weak KCs, teaching immediately.

**For the tutor** — a separate view: ordered session agenda with probes, root causes rather
than symptoms, errors grouped by the belief behind them, the confidence/correctness 2×2, pace
and second-guessing, and the raw log.

---

## Architecture

No backend, and that constraint drove the design. A server would need a machine awake to
serve a phone at 11pm the night before a quiz. So: one static `dist/index.html` with
everything inlined, served by GitHub Pages, installable, works with no signal.

- **No math library at runtime.** LaTeX is rendered to MathML at build time with vendored
  KaTeX 0.16.47. The shipped app carries no KaTeX, no web font, no CDN. `pwa_check.mjs`
  verifies the math lays out with real width in a real browser, offline.
- **Progress transfers by link.** A session compresses into a URL fragment. A fragment is
  never sent to a web server, so the data goes from the student's device to the tutor's
  directly and GitHub never sees it.
- **No names in this repo.** The repo is public because GitHub Pages requires it on the free
  tier, so the build ships with `STUDENT_NAME` empty; the app asks once on first launch and
  keeps the answer in the device's own storage. `.gitignore` blocks session data. The repo
  carries questions only.
- **The tutor view's code is obfuscation, not security.** It exists so the student does not
  wander into clinical language about herself, and it is documented as such.

---

## Item bank: verified structurally, not independently re-solved

218 items covering all 58 KCs. `build/verify_bank.py` is the last gate before a real student:
it drops, loudly, any item with anything other than exactly one correct option, an
unresolvable misconception tag, unbalanced or unknown LaTeX, duplicate option text, or a
reference to a figure that does not exist. The build then exits fatally if that leaves too few
usable anchors, or if any formula fails to render.

**What has not been done: no item's answer key has been independently re-solved by a second
pass.** 172 items are author-asserted (the adversarial-verifier stage of the generation run
failed on an API session limit); 46 are hand-written and checked once. Structural verification
rules out unusable items; it cannot rule out a plausible item whose keyed answer is simply
wrong. `docs/VERIFICATION-STATUS.md` records this in full and should be read before treating
any question here as authoritative.

---

## Build

```bash
cd build
python build.py            # audits the bank, renders LaTeX, writes dist/
node test_engine.mjs       # 2765 checks against the SHIPPED dist/index.html
node pwa_check.mjs         # real headless Chrome, incl. an offline cold reload
```

`test_engine.mjs` extracts the inline script from the shipped `dist/index.html` and runs it in
a `vm` with a stubbed DOM. It plants a known-broken KC and asserts the descent terminates on
it, plus graph integrity, one key per item, every distractor tag resolving, BKT monotonicity,
the session cap, and the share payload round-trip. `pwa_check.mjs` drives headless Chrome over
CDP using Node 22's global WebSocket (no puppeteer) and reloads cold under
`Network.emulateNetworkConditions {offline:true}`.

**Bump `BUILD_SERIAL` in `build.py` on every republish.** It is part of the service-worker
cache name; without a bump, an installed copy serves yesterday's questions forever.

```bash
git subtree push --prefix dist origin gh-pages   # publish
```

---

## Layout

```
build/
  kc_graph.py         58 knowledge components + prerequisite edges, with a cycle check
  misconceptions.py   51 named errors in 8 families, each with a tutor-facing fix and probe
  bank/*.json         the item bank, one file per knowledge component
  verify_bank.py      structural audit — the last gate before a real student
  render_math.mjs     LaTeX -> MathML at BUILD time (vendored KaTeX 0.16.47)
  app_template.html   the whole app: one file, one inline script
  build.py            assembles dist/, writes the SW and hand-rolled PNG icons
  test_engine.mjs     engine tests against the shipped artifact
  pwa_check.mjs       CDP-over-WebSocket browser + offline check
dist/                 what gets published
docs/DESIGN.md        the build contract and the reasoning behind it
docs/VERIFICATION-STATUS.md   what is and is not verified about the questions
```
