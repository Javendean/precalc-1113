# Precalc 1113 — Design

**A diagnostic and practice PWA for Kaleice, taking MATH 1113 Precalculus at Georgia State
University Perimeter College with Ashraful Chowdhury. Built for her device; instrumented for
her tutor.**

Built autonomously overnight on 2026-08-27. This document is the build contract.

---

## 1. What the operator asked for

1. A PWA for Kaleice.
2. **A diagnostic sequence** that gauges proficiency and finds the areas of weakness to focus on.
3. **Visibility on her progress** for the tutor.
4. **Insights into what she does and how she does it**, to inform tutoring sessions.

Requirement 4 is the one that shapes the architecture. A score tells a tutor nothing he could
not get from her graded quiz. What a tutor cannot get anywhere else is *the procedure she runs*
— which rule she over-applies, whether she is confidently wrong or quietly guessing, whether she
is slow because she is thinking or fast because she is pattern-matching. So the app is built to
capture the *process*, and the item bank is built so that process is machine-readable.

---

## 2. Two decisions that fix the architecture

### 2.1 It must not depend on the tutor's laptop

The existing study apps in this environment (`EAS-Prep`, `MathCST-Prep`, `Verbo`) are
FastAPI + React servers that run on the operator's machine and reach the phone through a
Cloudflare tunnel. Their own launch skill documents the disqualifying failure mode:

> **Closing the laptop** → the tutor runs server-side on this machine, so the phone needs this
> machine awake and the process running.
> — `MathCST-Prep/.claude/skills/launching-mathcst-prep/SKILL.md`

Those apps were built for the operator, on the operator's machine. This one is for **someone
else's phone**, used at 11pm the night before a quiz. The precedent that matches is `HealthPrep`
— built for a different student, shipped as a self-contained static PWA on GitHub Pages, works
offline with no server at all.

**Decision: static PWA on GitHub Pages. No backend. Data local to her device.**
Delivery from `HealthPrep`; learning engine from `MathCST-Prep`.

### 2.2 Tutor visibility without a server

Since there is no backend, progress travels as an explicit hand-off:

- The app compresses her session log into a URL fragment and offers one-tap share.
- The tutor opens that link; the same PWA renders the tutor dashboard from the payload.
- A URL **fragment is never transmitted to the web server** — the data goes from her device to
  the tutor's directly, and GitHub never sees it.

This is a real trade-off and it is chosen deliberately: it costs one tap per session, and it
buys an app that is always up, works on a plane, needs no account, and keeps a student's
performance data out of third-party hands. A `SYNC_URL` hook is present and inert so automatic
push can be switched on later without touching the client logic.

**Privacy consequences, enforced in the build:**

GitHub Pages requires a **public** repo on the free tier, so the repo is public — which means no
student's name may appear in it. `STUDENT_NAME` ships empty and the app asks her once on first
launch, keeping the answer in her own device's storage. The repo and its URL are generically
named (`precalc-1113`, not her name). `.gitignore` blocks session data, and no attempt record is
ever committed. The repository carries questions only.

---

## 3. The knowledge-component graph (`build/kc_graph.py`)

58 knowledge components in two tiers, joined by **real prerequisite edges**.

- **Tier 0 — the algebra substrate** (19 KCs): exponent laws, factoring, fraction arithmetic,
  signs, radicals, equation solving.
- **Tier 1 — precalculus proper** (39 KCs): aligned to OpenStax Precalculus 2e chapters 1–11,
  the text GSU MATH 1113 uses.

The tier split is the thesis of the app. A student failing precalculus rarely has a precalculus
problem. `log_solve` sits on a **20-KC prerequisite closure** that bottoms out at `exp_laws`,
`exp_negative` and `frac_arith`. She will report the problem as "logs." The graph is what lets
the app disagree with her.

**22 KCs are marked `anchor`** — diagnostic entry points the course currently leans on.

### The descent

The diagnostic starts at anchors and descends only on failure:

```
ask an anchor item
  correct   -> mark provisional pass, skip its entire prereq subtree
  incorrect -> walk prereq_closure(anchor) DEEPEST-FIRST, one item per KC,
               stopping a branch once a prerequisite passes
```

The deepest KC that still fails is the **root cause**; everything above it is collateral. This
is what keeps a whole-course diagnostic at roughly 25 questions instead of 200, and it is why
the report can say *"negative exponents, which is why logarithms look broken"* rather than
*"weak on logarithms."*

---

## 4. The misconception registry (`build/misconceptions.py`)

45 named misconceptions in **8 error families**. Every incorrect option in the bank carries a
misconception id, and the option text is the value a student actually gets by committing exactly
that error on that stem. A wrong answer therefore reports *which rule she ran*.

The **family** layer is the highest-value idea here. Most struggling students do not have twelve
unrelated problems; they have two or three bad generalizations surfacing in a dozen places. A
student who writes all three of

```
(a+b)^2 = a^2 + b^2      log(a+b) = log a + log b      sin(A+B) = sin A + sin B
```

does not have an algebra problem, a logarithm problem and a trigonometry problem. She has **one**
belief — that every operation distributes over addition — costing her marks in three chapters.
`LINEARITY_ILLUSION` reports that as a single finding with a single fix, so it can be repaired in
one conversation instead of three.

The eight families: `LINEARITY_ILLUSION`, `INVERSE_AS_RECIPROCAL`, `RULE_OVERGENERALIZATION`,
`SIGN_MANAGEMENT`, `NOTATION_LITERALISM`, `DIRECTION_INVERSION`, `INCOMPLETE_SOLUTION_SET`,
`PROCEDURAL_NO_DOMAIN`.

Each carries a `fix` written for a tutor at a whiteboard and a `probe` — a fast question that
exposes the bug in isolation.

---

## 5. Process telemetry — "what she does and how she does it"

Captured per item, silently:

| Signal | Why a tutor wants it |
|---|---|
| **Pre-answer confidence** (guessing / shaky / confident) | Crossed with correctness it gives the only 2×2 that matters. |
| Time to first interaction | Reading and comprehension time, separated from working time. |
| Total time on item | Slow-and-right is fine; fast-and-wrong is impulsive pattern-matching. |
| Answer changes | Second-guessing. Tracked directionally: right→wrong changes are a distinct pathology from wrong→right. |
| Hint opened | Where she knows she is stuck versus where she does not. |
| Chosen distractor's misconception | The actual diagnosis. |

### The calibration 2×2

| | Correct | Incorrect |
|---|---|---|
| **Confident** | Mastered — stop spending time here | **Misconception.** Highest priority: she will resist correction because it feels right |
| **Unsure** | Fragile — knows it, does not trust it. Needs consolidation, not reteaching | Gap — teachable, nothing to unlearn first |

Confident-and-wrong is the most valuable cell and the one a grade cannot show. It is ranked
first on the tutor's agenda, following the hypercorrection effect already encoded in
`MathCST-Prep/backend/math_tutor/learning.py`.

---

## 6. Learning engine

Ported to JavaScript from `MathCST-Prep/backend/math_tutor/learning.py`, whose parameters are
already tuned and unit-tested:

- **BKT** per KC — `L0=0.30, T=0.35, slip=0.10, guess_mc=0.25`.
- **Recency decay** — displayed proficiency droops as a KC goes stale (`tau = 48h`).
- **Elo** — item difficulty for practice selection, targeting P(correct) 0.70–0.85.
- **Leitner** — spaced review boxes for practice mode.
- **Review priority** — `4·conf·wrong + 1.5·|conf−correct| + 1·(box==1)`, so confident errors
  dominate the queue.

**Honesty constraint:** the diagnostic contributes only 1–2 observations per KC, so BKT
posteriors are wide. Every proficiency figure is displayed with its evidence count, and any KC
with fewer than 2 observations is rendered as *provisional*. The app must not launder two
questions into a confident mastery claim about a real person.

---

## 7. Diagnostic session shape

Target **25 items / ~20 minutes**, hard-capped at 30.

Feedback during the diagnostic is deliberately thin — correct or incorrect, one line, no
teaching — so that measurement stays clean and momentum stays high. Full worked solutions and
misconception explanations are unlocked on the results screen, where she can review every item
she missed. Practice mode, by contrast, teaches immediately.

Ordering interleaves Tier-1 anchors with their Tier-0 descents so the session never becomes a
march through remedial algebra, which would read as an accusation.

---

## 8. Views

| Route | Audience | Purpose |
|---|---|---|
| `#/` | Kaleice | Welcome, resume, start diagnostic |
| `#/diagnostic` | Kaleice | The adaptive sequence |
| `#/results` | Kaleice | Strengths first, then 2–3 focus areas, then review missed items |
| `#/practice` | Kaleice | Targeted practice on weak KCs, spaced |
| `#/share` | Kaleice | One-tap send-to-tutor |
| `#/tutor` | Javen | Root causes, families, calibration, pace, agenda, raw log |

The tutor route is behind a light code. That is **obfuscation, not security** — it exists so the
student does not wander into clinical language about herself, and it is documented as such.

---

## 9. Build pipeline

Follows `HealthPrep/build/build.py` exactly:

```
build/kc_graph.py + misconceptions.py + bank/*.json + app_template.html
        -> build/build.py ->
dist/index.html  (everything inlined: no CDN, no fonts, no second file to 404)
dist/manifest.webmanifest, dist/sw.js, dist/icon-*.png (hand-written via zlib/struct)
```

**LaTeX is rendered to MathML at build time** with the KaTeX already vendored in
`MathCST-Prep/frontend/node_modules/katex`. The shipped app therefore carries **zero math-library
runtime** — no KaTeX JS, no web fonts, no CDN. MathML Core is native in current Chrome, Safari
and Firefox, which is what her phone runs.

`BUILD_SERIAL` is part of the service-worker cache name and **must be bumped on every
republish**, or installed copies serve stale questions forever.

---

## 10. Testing

Both suites run against the **shipped artifact**, per the HealthPrep precedent:

- `build/test_engine.mjs` — loads `dist/index.html`, extracts the inline script, runs it in a
  `vm` context with a stubbed DOM. Asserts: graph integrity, descent terminates and finds the
  planted root cause, every item has exactly one key, every distractor tag resolves, BKT
  monotonicity, session cap, share payload round-trips.
- `build/pwa_check.mjs` — drives headless Chrome over **CDP using Node 22's global WebSocket**
  (no puppeteer). Verifies boot, service-worker registration, cache fill, and a cold reload
  under `Network.emulateNetworkConditions {offline:true}`.
- `build/verify_bank.py` — offline structural audit of the item bank: unique ids, exactly one
  correct option, every `mis` id resolves against the registry, balanced LaTeX, no duplicate
  option text, KC coverage.

---

## 11. Non-goals

No accounts. No backend. No LLM tutor (it would require a server and the operator's
subscription, reintroducing the laptop dependency §2.1 exists to remove). No multi-student
support. No grading integration with GSU. Content is aligned to OpenStax, not copied from it.
