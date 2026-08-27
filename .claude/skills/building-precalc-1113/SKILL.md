---
name: building-precalc-1113
description: Use when building, testing, republishing or extending the Precalc 1113 study PWA — including adding questions, changing the knowledge-component graph or misconception registry, or answering why the published app is serving stale questions.
---

# Building Precalc 1113

## Overview
A **static** PWA: no server, no backend, no runtime dependencies. `build.py` inlines everything
into one `dist/index.html`, and GitHub Pages serves it. There is deliberately nothing to launch
— unlike `EAS-Prep` / `MathCST-Prep`, which need this machine awake.

## The commands

```bash
cd build
python build.py                 # build from build/bank/  -> dist/
python build.py bank_synth      # build from the throwaway bank (pipeline shake-out only)
python build.py --icons         # also regenerate the PNG icons (normally skipped)
node test_engine.mjs            # 2800+ checks against the SHIPPED dist/index.html
node pwa_check.mjs              # headless Chrome: boot, MathML layout, SW, offline reload
node pwa_check.mjs https://javendean.github.io/precalc-1113/   # check the live site
cd .. && ./publish.sh           # push dist/ to gh-pages (refuses synthetic builds)
```

## The three traps

1. **Bump `BUILD_SERIAL` in `build.py` before every republish.** It is part of the service-worker
   cache name. Without a bump, an already-installed copy on her phone keeps serving the old
   questions forever and no amount of reloading fixes it.
2. **`dist/` is tracked on purpose.** `git subtree push --prefix dist origin gh-pages` needs it
   committed. Do not add it to `.gitignore`.
3. **Bash heredocs on this machine strip backslashes.** Authoring any file containing LaTeX
   (`\dfrac`, `\sqrt`) through `cat <<'EOF'` silently corrupts it. Use the Write tool.

## Adding or changing questions

Items live in `build/bank/<kc_id>.json`, one file per knowledge component:

```json
{"kc":"exp_laws","items":[{"id":"exp_laws-01","kc":"exp_laws","difficulty":3,
 "est_seconds":45,"stem":"Simplify $\\dfrac{x^{-3}}{x^{5}}$.","hint":"...",
 "worked":["...","..."],
 "options":[{"key":"a","text":"$x^{-8}$","correct":true},
            {"key":"b","text":"$x^{2}$","correct":false,"mis":"EXP_QUOT_REVERSED"}]}]}
```

**Every distractor must carry a `mis` id that exists in `misconceptions.py`, and the option text
must be the value a student actually gets by committing that error.** A wrongly tagged distractor
produces a false diagnosis about a real student, which is worse than no diagnosis. `build.py`
hard-fails on an unresolvable tag and drops the item.

`verify_bank.py` also drops items that reference a figure, have duplicate options, have anything
other than exactly one correct option, or contain LaTeX outside the allowed command list.

## Changing the graph

`kc_graph.py` `prereqs` are real dependency edges and they drive the diagnostic's descent. Adding
an edge changes which root cause gets reported. `validate()` fails the build on a cycle or an
unknown id. After any edit, re-run `node test_engine.mjs` — it plants a known-broken KC and
asserts the descent names it rather than the downstream symptom.

The diagnostic is **breadth-first then depth**: every anchor is asked before any descent, so a
student who struggles in chapter 1 still gets probed on trigonometry. A test locks this in; do
not "optimize" it back to inline descents.

## Verifying, not assuming

Both suites run against the built artifact rather than the source. `pwa_check.mjs` is the one
that matters most, because it checks the thing that cannot be checked statically: that MathML
lays out with real width in a real browser **with the network cut**. The app ships no math
library, so if that check ever fails the questions are invisible on her phone.

## Privacy

The repo is public (GitHub Pages needs it to be). **No student name goes in it** — `STUDENT_NAME`
ships empty and the app asks on first launch. Session data never leaves her device except through
a share link, whose payload lives in the URL fragment and is never sent to a server.
