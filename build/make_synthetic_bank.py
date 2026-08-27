# -*- coding: utf-8 -*-
"""Generate a THROWAWAY bank that exercises the whole pipeline.

The items are mathematically trivial and pedagogically worthless on purpose --
this exists only so build.py, test_engine.mjs and pwa_check.mjs can be shaken
out end to end before the real generated bank arrives. Never publish a build
made from this.

    python make_synthetic_bank.py       # writes build/bank_synth/
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from kc_graph import KCS                                    # noqa: E402
from misconceptions import MISCONCEPTIONS                   # noqa: E402

OUT = HERE / "bank_synth"
OUT.mkdir(exist_ok=True)

# Misconceptions that name this KC, so tags resolve the way real ones will.
BY_KC = {}
for m in MISCONCEPTIONS:
    for k in m["kcs"]:
        BY_KC.setdefault(k, []).append(m["id"])

GENERIC = [m["id"] for m in MISCONCEPTIONS
           if m["family"] in ("SIGN_MANAGEMENT", "RULE_OVERGENERALIZATION")]

written = 0
for k in KCS:
    n = 5 if k["anchor"] else 3
    tags = (BY_KC.get(k["id"], []) + GENERIC)
    items = []
    for i in range(n):
        a, b = i + 2, i + 3
        pool = [t for t in tags if t]
        picks = [pool[j % len(pool)] for j in range(i, i + 3)]
        items.append({
            "id": "%s-%02d" % (k["id"], i + 1),
            "kc": k["id"],
            "difficulty": 1 + (i % 5),
            "est_seconds": 45,
            "stem": "Synthetic probe %d for %s: compute $%d + %d$." % (i + 1, k["name"], a, b),
            "hint": "Add the two numbers.",
            "worked": ["$%d + %d$" % (a, b), "$= %d$" % (a + b)],
            "options": [
                {"key": "a", "text": "$%d$" % (a + b), "correct": True},
                {"key": "b", "text": "$%d$" % (a * b), "correct": False, "mis": picks[0]},
                {"key": "c", "text": "$%d$" % (a - b), "correct": False, "mis": picks[1]},
                # +7 rather than +1: at i=0, a*b and a+b+1 collide and the
                # audit (correctly) drops the item for duplicate options.
                {"key": "d", "text": "$%d$" % (a + b + 7), "correct": False, "mis": picks[2]},
            ],
        })
    (OUT / ("%s.json" % k["id"])).write_text(
        json.dumps({"kc": k["id"], "items": items}, ensure_ascii=False), encoding="utf-8")
    written += len(items)

print("synthetic bank: %d items across %d KCs -> %s" % (written, len(KCS), OUT))
print("THROWAWAY -- never publish a build made from this.")
