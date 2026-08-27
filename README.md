# Precalc 1113

A diagnostic and practice PWA for **Kaleice**, taking MATH 1113 Precalculus at Georgia State
University Perimeter College. Static, offline-capable, installable, and instrumented so her
tutor can see not just *what* she got wrong but *which rule she ran* to get there.

**Live:** https://javendean.github.io/precalc-1113/

---

## What it does

**For Kaleice**

- A ~25-question adaptive check-up that finds the two or three things actually worth her time.
- When she misses something, it asks a question from *underneath* it — because the real problem
  is usually a step further back than where it shows up.
- Results that lead with what is solid, then name the specific things to fix, then let her
  review every miss with full working.
- Targeted practice on the weak spots, with immediate teaching.
- Installs to her home screen and works with no signal.

**For the tutor**

- **Session agenda** — an ordered list of what to do next session, with probes.
- **Root causes** — the deepest broken thing, not the symptom that surfaced.
- **Error patterns** — her mistakes grouped by the *belief* behind them.
- **Confidence vs correctness** — the 2×2 a grade cannot show you.
- **How she works** — pace, reading time, second-guessing, hint usage.
- **Every answer** — the raw log.

---

## The two ideas that make it useful

### 1. The prerequisite descent

58 knowledge components in two tiers, joined by real dependency edges. Tier 0 is the algebra
substrate (exponent laws, factoring, signs, fractions); Tier 1 is precalculus proper, aligned to
**OpenStax Precalculus 2e**, the text MATH 1113 uses.

A student failing precalculus rarely has a precalculus problem. `log_solve` sits on a **20-KC
prerequisite closure** bottoming out at `exp_laws` and `frac_arith`. She will report the problem
as "logs." The graph is what lets the app disagree with her, and it is why the diagnostic can
cover a whole course in 25 questions instead of 200 — it only descends where something failed.

### 2. Misconception-tagged distractors

45 named misconceptions in 8 error families. Every wrong option is the value a student *actually
gets* by committing one specific, named error. So a wrong answer reports a diagnosis.

The **family** layer is the part that changes a tutoring session. A student who writes all three of

```
(a+b)² = a² + b²     log(a+b) = log a + log b     sin(A+B) = sin A + sin B
```

does not have an algebra problem, a logarithm problem and a trigonometry problem. She has **one**
belief — that everything distributes over addition — costing her marks in three chapters.
`LINEARITY_ILLUSION` reports that as a single finding with a single fix.

---

## Build

```bash
cd build
python build.py            # audits the bank, renders LaTeX, writes dist/
node test_engine.mjs       # engine tests against the SHIPPED dist/index.html
node pwa_check.mjs         # real headless Chrome, incl. an offline cold reload
```

`build.py` refuses to ship on a bad answer key, an unresolvable misconception tag, malformed
LaTeX, or an item that references a figure that does not exist.

**Bump `BUILD_SERIAL` in `build.py` on every republish.** It is part of the service-worker cache
name; without a bump, an installed copy serves yesterday's questions forever.

### Publish

```bash
git subtree push --prefix dist origin gh-pages
```

---

## Layout

```
build/
  kc_graph.py         58 knowledge components + prerequisite edges
  misconceptions.py   45 named errors in 8 families, each with a tutor-facing fix
  bank/*.json         the item bank (generated, then independently re-solved)
  verify_bank.py      structural audit — the last gate before a real student
  render_math.mjs     LaTeX → MathML at BUILD time (vendored KaTeX 0.16.47)
  app_template.html   the whole app: one file, one inline script
  build.py            assembles dist/, writes the SW and hand-rolled PNG icons
  test_engine.mjs     engine tests
  pwa_check.mjs       CDP-over-WebSocket browser + offline check
dist/                 what gets published
docs/DESIGN.md        the build contract and the reasoning behind it
```

---

## Notes

- **No backend, by design.** The apps in this environment that use one (`EAS-Prep`,
  `MathCST-Prep`) need the tutor's laptop awake — fine when the tutor is the user, disqualifying
  when a student is. See `docs/DESIGN.md` §2.1.
- **No math library at runtime.** LaTeX is rendered to MathML at build time, so the app ships no
  KaTeX, no web font and no CDN. `pwa_check.mjs` verifies the math lays out with real width in a
  real browser, offline.
- **Progress transfers by link.** Her session compresses into a URL fragment, which is never sent
  to a web server — the data goes from her device to the tutor's directly.
- **No student's name is in this repo.** GitHub Pages needs the repo public, so the build ships
  without a name and the app asks once on first launch, keeping it in her own device's storage.
  `.gitignore` blocks session data. The repo carries questions only.
- The tutor-view code is **obfuscation, not security**. It exists so she does not wander into
  clinical language about herself.
