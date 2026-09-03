# Verification status of the item bank

**Read this before treating a question in this app as authoritative.**

Last updated: 2026-08-27, after the overnight build.

---

## What was actually verified

| Check | Status | Coverage |
|---|---|---|
| Structural audit (`verify_bank.py`) | ✅ done | **all 218 items** |
| LaTeX parses and renders (KaTeX → MathML) | ✅ done | all 218 items, 3431 spans, 0 errors |
| Exactly one correct option, four distinct options | ✅ done | all 218 |
| Every `mis` tag resolves to a real registry entry | ✅ done | all 218 |
| No item depends on a figure, graph image or table | ✅ done | all 218 |
| Engine behaviour (descent, coverage, share, analytics) | ✅ done | 2755 checks |
| Real browser, online and offline | ✅ done | 30 checks |
| **Independent re-solving of each item's answer key** | ❌ **NOT DONE** | **0 of 218** |
| **Independent check that each distractor matches its tag** | ❌ **NOT DONE** | **0 of 218** |

## Why the last two are missing

The generation workflow ran author → adversarial-verifier per knowledge component. Every author
completed for 46 of 58 KCs, then the run hit the API session limit (resets 7am America/New_York)
and **all 58 verifier agents failed**. No item has been re-solved by a second, independent pass.

The 172 generated items are therefore **author-asserted**. Spot checks during the run were
correct — `-4x^2(3x^3-2x) = -12x^5+8x^3` with the `EXP_PROD_MULTIPLY` distractor at `-12x^6+8x^2`,
and `(3^2)^3 \cdot 3^2 / 3^6 = 9` — but a spot check is not a verification pass.

The 46 hand-authored items (the 12 KCs the run never reached) were written and checked by one
pass, mine. They carry `"source": "hand"` in the bank files. Same caveat: one pass, not two.

## What this means in practice

The structural audit rules out the failure modes that would make an item *unusable* — malformed
LaTeX, two correct answers, an invented misconception id, a reference to a missing figure. It
cannot rule out the failure mode that matters most: **a plausible-looking item whose keyed answer
is simply wrong.**

For a student who is already unsure of herself, that failure mode is worse than no app. Treat the
bank as good-but-unaudited until the pass below is run.

## Completing the verification

The generation workflow is resumable: its script and run id live locally, outside this
repository. Cached agents replay instantly, so a resume re-runs only the verifier agents
that failed.

Two caveats on the resume:

1. It writes verified output to `build/bank/`, which now also holds the promoted author output and
   the hand-authored files. Back `build/bank/` up first so a partial re-run cannot half-overwrite
   a working bank.
2. It will not touch the 12 hand-authored KCs — they were never in that run. Verify those
   separately, or add them to the KC list in the script before resuming.

After any change: `python build.py && node test_engine.mjs && node pwa_check.mjs`.

## Honest summary

The **app** is verified. The **questions** are not independently verified. Those are different
claims and this file exists so they do not get conflated.
