# -*- coding: utf-8 -*-
"""Render dist/ from the item bank, the KC graph and app_template.html.

Everything is inlined into a single index.html so the app has zero runtime
dependencies: no CDN, no web font, no math library, no separate content file
that could 404. That matters because the point is a study tool that still works
on a phone in a parking lot with one bar of signal -- or none.

Pipeline:
    build/bank/*.json  (verified items from the generation workflow)
        -> merge + structural audit (verify_bank.py)
        -> LaTeX to MathML at build time (render_math.mjs, vendored KaTeX)
        -> inline into app_template.html
        -> dist/index.html + manifest + service worker + icons

BUMP BUILD_SERIAL ON EVERY REPUBLISH. It is part of the service-worker cache
name; without a bump, an installed copy serves yesterday's questions forever.
"""
from __future__ import annotations

import io
import json
import pathlib
import struct
import subprocess
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
BANK = BUILD / "bank"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

sys.path.insert(0, str(BUILD))
from kc_graph import KCS, KC_BY_ID, ANCHORS, validate as validate_graph   # noqa: E402
from misconceptions import (MISCONCEPTIONS, MISCONCEPTION_BY_ID, FAMILIES,  # noqa: E402
                            validate as validate_mis)
import verify_bank                                                        # noqa: E402

BUILD_SERIAL = 4
# Deliberately NOT the student's name. This repo is public (GitHub Pages needs
# it to be), so no student's name goes in it -- the app asks her on first launch
# and keeps the answer in her own device's storage.
STUDENT_NAME = ""
TUTOR_CODE = "unitcircle"   # obfuscation, not security -- see docs/DESIGN.md


def read_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    # ---------------------------------------------------------------- graph
    validate_graph()
    validate_mis(set(KC_BY_ID))
    print("graph ok: %d KCs (%d anchors), %d misconceptions in %d families"
          % (len(KCS), len(ANCHORS), len(MISCONCEPTIONS), len(FAMILIES)))

    # ---------------------------------------------------------------- bank
    # `python build.py <dir>` builds from an alternative bank. Used to exercise
    # the whole pipeline against a synthetic bank before the real one lands.
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bank_dir = pathlib.Path(args[0]).resolve() if args else BANK
    files = sorted(bank_dir.glob("*.json"))
    if not files:
        sys.exit("no item files in %s -- run the generation workflow first" % bank_dir)
    print("bank: %s" % bank_dir)
    raw = []
    items = []
    for f in files:
        d = read_json(f)
        chunk = d["items"] if isinstance(d, dict) else d
        raw.append((f.name, len(chunk)))
        for it in chunk:
            it.setdefault("source", f.stem)
        items.extend(chunk)
    for name, n in raw:
        print("  %-28s %3d items" % (name, n))

    kept, problems = verify_bank.verify(
        items, set(KC_BY_ID), set(MISCONCEPTION_BY_ID))
    fatal = [p for p in problems if p[0] == verify_bank.FATAL]
    warn = [p for p in problems if p[0] == verify_bank.WARN]
    print("\naudit: %d in -> %d kept, %d dropped" % (len(items), len(kept), len(items) - len(kept)))
    for lvl, iid, msg in fatal[:40]:
        print("  DROP %-16s %s" % (iid, msg))
    if len(fatal) > 40:
        print("  ... and %d more" % (len(fatal) - 40))
    for lvl, iid, msg in warn[:15]:
        print("  warn %-16s %s" % (iid, msg))

    cov = verify_bank.coverage_report(kept, KCS)
    usable_anchors = [a for a in ANCHORS if len(cov["by_kc"].get(a, [])) >= 1]
    print("\ncoverage: %d KCs with items, %d empty, %d thin"
          % (len(cov["ok"]), len(cov["empty"]), len(cov["thin"])))
    if cov["empty"]:
        print("  empty: %s" % ", ".join(cov["empty"]))
    if cov["thin"]:
        print("  thin : %s" % ", ".join("%s(%d)" % t for t in cov["thin"]))
    print("  usable anchors: %d / %d" % (len(usable_anchors), len(ANCHORS)))
    if len(usable_anchors) < 8:
        sys.exit("FATAL: only %d usable anchors -- the diagnostic would be too "
                 "shallow to be worth a student's time." % len(usable_anchors))

    # ------------------------------------------------- LaTeX -> MathML
    tmp_in, tmp_out = BUILD / "_bank_in.json", BUILD / "_bank_out.json"
    tmp_in.write_text(json.dumps({"items": kept}, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([_node(), str(BUILD / "render_math.mjs"), str(tmp_in), str(tmp_out)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        sys.exit("FATAL: LaTeX rendering failed; refusing to ship broken formulas.")
    kept = read_json(tmp_out)["items"]
    tmp_in.unlink(missing_ok=True)
    tmp_out.unlink(missing_ok=True)

    # ---------------------------------------------------------------- payload
    # A synthetic build is stamped so it can never be published by accident.
    # publish.sh refuses on this flag. Operating unattended, this is the rail
    # that stops a throwaway bank reaching a real student.
    synthetic = "synth" in bank_dir.name.lower()
    if synthetic:
        print("\n*** SYNTHETIC BANK -- build is stamped and must not be published ***")

    payload = {
        "serial": BUILD_SERIAL,
        "student": STUDENT_NAME,
        "tutorCode": TUTOR_CODE,
        "synthetic": synthetic,
        "kcs": [{"id": k["id"], "name": k["name"], "tier": k["tier"],
                 "chapter": k["chapter"], "prereqs": k["prereqs"],
                 "anchor": bool(k["anchor"]), "blurb": k["blurb"]} for k in KCS],
        "families": {f: {"name": v["name"], "summary": v["summary"], "fix": v["fix"]}
                     for f, v in FAMILIES.items()},
        "misconceptions": {m["id"]: {"name": m["name"], "family": m["family"],
                                     "signature": m["signature"], "root": m["root"],
                                     "fix": m["fix"], "probe": m["probe"]}
                           for m in MISCONCEPTIONS},
        "items": [{"id": it["id"], "kc": it["kc"], "difficulty": it["difficulty"],
                   "stem": it["stem"], "plain": it.get("plain", ""),
                   "hint": it["hint"], "worked": it.get("worked", []),
                   "options": [{"text": o["text"], "plain": o.get("plain", ""),
                                "correct": bool(o.get("correct")),
                                "mis": o.get("mis") or None} for o in it["options"]]}
                  for it in kept],
    }

    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # A literal </script> inside the JSON would close the block early.
    assert "</script>" not in blob, "item text contains a script-closing tag"

    tpl = (BUILD / "app_template.html").read_text(encoding="utf-8")
    assert "/*__DATA__*/" in tpl, "template lost its data placeholder"
    html = tpl.replace("/*__DATA__*/", blob)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    # ---------------------------------------------------------------- manifest
    manifest = {
        "name": "Precalc 1113",
        "short_name": "Precalc",
        "description": "Diagnostic and practice for MATH 1113 Precalculus.",
        "start_url": ".", "scope": ".", "display": "standalone",
        "orientation": "portrait", "background_color": "#10141f",
        "theme_color": "#10141f",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icon-512-maskable.png", "sizes": "512x512", "type": "image/png",
             "purpose": "maskable"},
        ],
    }
    (DIST / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # ---------------------------------------------------------------- sw
    cache = "precalc1113-v%d-%d" % (BUILD_SERIAL, len(payload["items"]))
    (DIST / "sw.js").write_text(SW % cache, encoding="utf-8")

    # ---------------------------------------------------------------- icons
    # Static art -- it only changes when wave() does, so regenerate lazily.
    # (A 512x512 RGBA buffer plus zlib is also the one part of this build that
    # can MemoryError on a loaded machine; skipping it keeps rebuilds cheap.)
    force_icons = "--icons" in sys.argv
    for name, size, pad in (("icon-192.png", 192, 0.06),
                            ("icon-512.png", 512, 0.06),
                            ("icon-512-maskable.png", 512, 0.0)):
        p = DIST / name
        if force_icons or not p.exists():
            png(p, size, wave(size, pad))
            print("  icon %s written" % name)

    print("\nbuilt dist/  items=%d  kcs=%d  cache=%s" % (len(payload["items"]), len(KCS), cache))
    for p in sorted(DIST.iterdir()):
        print("  %-26s %9s B" % (p.name, "{:,}".format(p.stat().st_size)))
    if fatal:
        print("\n%d items were dropped by the audit -- see DROP lines above." % len(fatal))


def _node():
    return "node"


SW = """/* Offline shell for the Precalc 1113 PWA. */
const CACHE = '%s';
const FILES = ['./', './index.html', './manifest.webmanifest',
               './icon-192.png', './icon-512.png', './icon-512-maskable.png'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).catch(() => {}));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit => {
      if (hit) {
        fetch(e.request).then(r => {
          if (r && r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        }).catch(() => {});
        return hit;
      }
      return fetch(e.request)
        .then(r => {
          if (r && r.ok && new URL(e.request.url).origin === self.location.origin) {
            const copy = r.clone();
            caches.open(CACHE).then(c => c.put(e.request, copy));
          }
          return r;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});
"""


# ---------------------------------------------------------------------------
# Icons -- written by hand as PNG chunks so the build needs no Pillow.
# ---------------------------------------------------------------------------
def png(path, size, pixel):
    """Write a size x size RGBA PNG. `pixel(x, y)` returns an (r,g,b,a) tuple."""
    raw = bytearray()
    for y in range(size):
        raw.append(0)                       # filter type 0 (None) per scanline
        for x in range(size):
            raw.extend(pixel(x, y))

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    body = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    path.write_bytes(body)


BG = (16, 20, 31, 255)
ACC = (79, 156, 255, 255)


def wave(size, pad_ratio):
    """A sine wave: instantly legible as trigonometry at 48px on a home screen."""
    import math

    pad = size * max(pad_ratio, 0.16)       # keep art inside the maskable safe zone
    span = size - 2 * pad
    cy = size / 2.0
    amp = span * 0.30
    thick = max(2.0, size * 0.075)
    r_out = size * 0.235
    c = size / 2.0

    # Precompute the curve so each pixel does a cheap nearest-sample check.
    N = size * 2
    pts = []
    for i in range(N + 1):
        t = i / N
        x = pad + t * span
        y = cy - amp * math.sin(2 * math.pi * t)
        pts.append((x, y))

    def px(x, y):
        fx, fy = x + 0.5, y + 0.5
        if pad_ratio > 0:                   # rounded-square plate
            dx = max(abs(fx - c) - (size / 2 - r_out), 0)
            dy = max(abs(fy - c) - (size / 2 - r_out), 0)
            if dx * dx + dy * dy > r_out * r_out:
                return (0, 0, 0, 0)
        if fx < pad - thick or fx > size - pad + thick:
            return BG
        i = int((fx - pad) / span * N)
        best = 1e9
        for j in range(max(0, i - 3), min(N, i + 4)):
            ex, ey = pts[j]
            d = (ex - fx) ** 2 + (ey - fy) ** 2
            if d < best:
                best = d
        return ACC if best <= (thick / 2) ** 2 else BG

    return px


if __name__ == "__main__":
    main()
