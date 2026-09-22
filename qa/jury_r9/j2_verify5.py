#!/usr/bin/env python3
"""Jury R9 juror2 — part 5: raw-hex context, th sticky top, gate focus/inert, mono tokens, blur census."""
import os, re

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
sty = open(os.path.join(J2, "style.css"), errors="replace").read()
lnd = open(os.path.join(J2, "landing.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()
lines_s = sty.split("\n"); lines_a = app.split("\n")

print("== V. raw-hex contexts ==")
for ln in [1386, 1717, 1879, 1880]:
    print(f"  style L{ln}: {lines_s[ln-1].strip()[:150]!r}")
    print(f"    ctx: {lines_s[ln-4].strip()[:80]!r} / {lines_s[ln-3].strip()[:80]!r}")

print("\n== W. th sticky top rule ==")
for i, l in enumerate(lines_s, 1):
    if "position: sticky" in l and "top: 0" in l:
        print(f"  L{i}: {l.strip()[:140]!r}")
# base table rule
for i, l in enumerate(lines_s, 1):
    if re.search(r"^\s*table\s*\{", l) or "table {" in l and i < 520:
        print(f"  L{i}: {l.strip()[:120]!r}")

print("\n== X. mono token defs ==")
for m in re.finditer(r"--mono-(?:xs|sm|md)\s*:\s*[^;]+;", sty):
    print(f"  L{sty[:m.start()].count(chr(10))+1}: {m.group(0)}")

print("\n== Y. backdrop-filter census (both css) ==")
for name, txt in [("style.css", sty), ("landing.css", lnd)]:
    hits = [(txt[:m.start()].count("\n")+1, txt[max(0,m.start()-70):m.start()+40].replace("\n"," ")) for m in re.finditer(r"backdrop-filter", txt)]
    print(f"  {name}: {len(hits)}")
    for ln, s in hits:
        print(f"    L{ln}: …{s!r}")

print("\n== Z. gate focus/inert/escape handling ==")
print("  app.js L1-45:")
for i, l in enumerate(lines_a[:45], 1):
    print(f"  L{i}: {l[:150]}")
for pat in [r"inert", r"aria-hidden',?\s*'true'\)", r"Escape", r"focus\(\)"]:
    hits = [(app[:m.start()].count("\n")+1) for m in re.finditer(pat, app)]
    print(f"  app.js {pat!r}: {hits[:10]}")

print("\n== AA. tonight-strip media context (L2110-2125) ==")
for i in range(2106, 2126):
    print(f"  L{i}: {lines_s[i-1].strip()[:130]!r}")

print("\n== AB. lp-cta-sm cascade check (landing L59 vs gate-cta L93) ==")
print("  landing L59:", lnd.split("\n")[58].strip()[:120])
print("  landing L93-95:", " | ".join(x.strip()[:60] for x in lnd.split("\n")[92:95]))

print("\n== AC. today payload detail (parsed) ==")
import json
tj = json.loads(open(os.path.join(J2, "j2_today.json")).read())
for g in tj.get("today", [])[:6]:
    print("  ", g.get("time"), g.get("home"), "vs", g.get("away"), "@", g.get("facility"), "| played:", g.get("played"), "| final:", g.get("final"))
print("  leagues:", len(tj.get("leagues", [])))
