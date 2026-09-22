#!/usr/bin/env python3
"""Jury R9 juror2 — verify FIX 1: mobile table scroll context + fade deletion (v67 bytes)."""
import os, re, hashlib, difflib

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
J5 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9")

sty = open(os.path.join(J2, "style.css"), errors="replace").read()
sty5 = open(os.path.join(J5, "style_v67.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()

print("== equivalence: my fetch vs juror5 fetch ==")
for a, b, n in [(sty, sty5, "style.css")]:
    same = a == b
    print(n, "identical" if same else f"DIFFERS ({len(a)} vs {len(b)})")
    if not same:
        d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
        print("   diff lines:", len(d))
        for L in d[:20]:
            print("   ", L[:160])

def find(pat, txt, label, flags=0, ctx=140):
    hits = 0
    for m in re.finditer(pat, txt, flags):
        ln = txt[:m.start()].count("\n") + 1
        print(f"  [{label}] L{ln}: {m.group(0)[:ctx]!r}")
        hits += 1
    if not hits:
        print(f"  [{label}] -- ZERO matches --")
    return hits

print("\n== FIX 1a: table-level scroll context in <=699 media ==")
# the media block context around any .card:has(table) rules
for m in re.finditer(r"@media[^{]*max-width:\s*699[^{]*\{", sty):
    ln = sty[:m.start()].count("\n") + 1
    # capture block body (naive brace walk)
    i = sty.find("{", m.start()); depth = 0; j = i
    while j < len(sty):
        if sty[j] == "{": depth += 1
        elif sty[j] == "}":
            depth -= 1
            if depth == 0: break
        j += 1
    body = sty[i:j]
    if "card" in body or "table" in body:
        print(f"  @media block L{ln} (len {len(body)}):")
        for seg in body.split("\n"):
            s = seg.strip()
            if s and (":has(table)" in s or "max-height" in s or "overflow" in s or "position:sticky" in s or "::after" in s or "swipe" in s.lower()):
                print("    ", s[:160])

print("\n== FIX 1b: all .card:has(table) occurrences in style.css ==")
find(r"[^\n]*\.card:has\(table\)[^\n]*", sty, "card:has(table)")

print("\n== FIX 1c: 'swipe' affordance chip ==")
find(r"[^\n]*[Ss]wipe[^\n]*", sty, "swipe")

print("\n== FIX 1d: base table overflow rules (context) ==")
find(r"[^\n]*table\{[^}]*overflow[^}]*\}", sty, "table-overflow")
find(r"[^\n]*th\{[^}]*sticky[^}]*\}", sty, "th-sticky")

print("\n== FIX 2: team inline watchdog vs shared ==")
find(r"[^\n]*armSkeletonWatchdog[^\n]*", app, "shared-wd")
find(r"[^\n]*data-wd-retry[^\n]*|data-retrying[^\n]*", app, "wd-retry")
# inline team watchdog: 8s nudge / 20s hard error near team content
find(r"[^\n]*Timed out after[^\n]*", app, "timedout")
find(r"[^\n]*20000[^\n]*", app, "20000")
find(r"[^\n]*8000[^\n]*", app, "8000")

print("\n== FIX 3: raw data.error interpolations ==")
find(r"[^\n]\$\{data\.error\}", app, "raw-data.error")
find(r"[^\n]*\$\{esc\(data\.error\)\}", app, "escaped")
