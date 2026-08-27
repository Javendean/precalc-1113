# -*- coding: utf-8 -*-
"""Structural audit of the item bank, run before anything is inlined.

This is the last gate between a generated item and a real student. A wrong
answer key does not merely fail to teach -- it actively teaches something false
to someone who is already unsure of herself. So the rule is: anything that
cannot be verified offline gets dropped, loudly, rather than shipped quietly.

Returns (kept, problems). `build.py` refuses to ship if problems are fatal.
"""
from __future__ import annotations

import re

FATAL = "FATAL"
WARN = "WARN"


def _balanced_dollars(s):
    return s.count("$") % 2 == 0


def _balanced_braces(s):
    depth = 0
    for ch in s:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


# Commands the vendored KaTeX build accepts and that we actually use. An
# unknown command is usually a hallucinated macro and will fail to render.
_KNOWN_CMD = set("""
dfrac frac tfrac sqrt left right pi theta alpha beta phi lambda mu infty pm mp
cdot times div le ge ne approx equiv sim propto in notin subset cup cap
sin cos tan csc sec cot arcsin arccos arctan sinh cosh tanh
log ln exp lim sum prod int
text mathrm mathbf mathit operatorname
begin end array matrix pmatrix bmatrix cases aligned
quad qquad hspace  space
circ deg prime
overline underline vec hat bar
langle rangle lvert rvert lfloor rfloor cdots ldots dots angle
displaystyle limits
neq leq geq rightarrow to leftarrow Rightarrow
varnothing emptyset cup
""".split())


def _unknown_commands(s):
    return sorted({m for m in re.findall(r"\\([a-zA-Z]+)", s) if m not in _KNOWN_CMD})


def verify(items, kc_ids, mis_ids):
    problems = []
    kept = []
    seen_ids = set()

    def bad(level, item_id, msg):
        problems.append((level, item_id, msg))

    for it in items:
        iid = it.get("id", "<no id>")
        fatal_here = []

        # --- identity ---
        if not iid or iid in seen_ids:
            fatal_here.append("duplicate or missing id")
        seen_ids.add(iid)

        if it.get("kc") not in kc_ids:
            fatal_here.append("unknown kc %r" % it.get("kc"))

        # --- options ---
        opts = it.get("options") or []
        if len(opts) != 4:
            fatal_here.append("has %d options, expected 4" % len(opts))
        n_correct = sum(1 for o in opts if o.get("correct"))
        if n_correct != 1:
            fatal_here.append("has %d correct options, expected exactly 1" % n_correct)

        texts = [str(o.get("text", "")).strip() for o in opts]
        if len(set(texts)) != len(texts):
            fatal_here.append("duplicate option text")
        if any(not t for t in texts):
            fatal_here.append("empty option text")

        # --- misconception tags ---
        untagged = 0
        for o in opts:
            if o.get("correct"):
                if o.get("mis"):
                    bad(WARN, iid, "correct option carries a misconception tag; dropped it")
                    o["mis"] = None
                continue
            tag = o.get("mis")
            if not tag:
                untagged += 1
            elif tag not in mis_ids:
                # An invented tag would produce a false diagnosis about a real
                # student, which is worse than no diagnosis at all.
                fatal_here.append("option tagged with unknown misconception %r" % tag)
        if untagged > 1:
            bad(WARN, iid, "%d distractors have no misconception tag" % untagged)

        # --- LaTeX integrity ---
        blobs = [it.get("stem", ""), it.get("hint", "")] + \
                list(it.get("worked") or []) + texts
        for b in blobs:
            b = str(b)
            if not _balanced_dollars(b):
                fatal_here.append("unbalanced $ in %r" % b[:60])
                break
            if not _balanced_braces(b):
                fatal_here.append("unbalanced braces in %r" % b[:60])
                break
            unk = _unknown_commands(b)
            if unk:
                fatal_here.append("unknown LaTeX command(s) %s in %r" % (unk, b[:60]))
                break

        # --- content sanity ---
        if not str(it.get("stem", "")).strip():
            fatal_here.append("empty stem")
        if not str(it.get("hint", "")).strip():
            bad(WARN, iid, "no hint")
        d = it.get("difficulty")
        if not isinstance(d, int) or not (1 <= d <= 5):
            bad(WARN, iid, "difficulty %r out of range; clamped to 3" % d)
            it["difficulty"] = 3
        if not isinstance(it.get("est_seconds"), int) or it["est_seconds"] <= 0:
            it["est_seconds"] = 45

        # Items that need a picture cannot be answered in this app.
        low = str(it.get("stem", "")).lower()
        for phrase in ("the graph below", "the figure", "shown below", "the diagram",
                       "the table below", "pictured"):
            if phrase in low:
                fatal_here.append("refers to a figure that does not exist (%r)" % phrase)
                break

        if fatal_here:
            for f in fatal_here:
                bad(FATAL, iid, f)
        else:
            kept.append(it)

    return kept, problems


def coverage_report(kept, kcs):
    """Which KCs have enough items to be usable in the diagnostic."""
    by_kc = {}
    for it in kept:
        by_kc.setdefault(it["kc"], []).append(it)
    empty, thin, ok = [], [], []
    for k in kcs:
        n = len(by_kc.get(k["id"], []))
        if n == 0:
            empty.append(k["id"])
        elif n < (3 if k["anchor"] else 2):
            thin.append((k["id"], n))
        else:
            ok.append(k["id"])
    return {"empty": empty, "thin": thin, "ok": ok, "by_kc": by_kc}
