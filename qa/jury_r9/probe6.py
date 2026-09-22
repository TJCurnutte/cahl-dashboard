#!/usr/bin/env python3
"""R9 juror5 part 12: landing tokens + WCAG on both themes, .link affordance CSS, sponsor gold, mono var usage in landing.css."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
lnd = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()

# style.css :root + light tokens
print("== style.css :root (dark) ==")
m = re.search(r":root\s*\{[^}]+\}", sty)
print(m.group(0)[:900] if m else "none")
light = re.search(r"\[data-theme=\"light\"\]\s*\{[^}]+\}", sty) or re.search(r"html\[data-theme=.light.\]\s*\{[^}]+\}", sty)
print("\n== light theme block ==")
print(light.group(0)[:900] if light else "none")

# landing.css full read (221 lines - just print rules of interest)
print("\n== landing.css: cta/sponsor/note rules ==")
for kw in ["gate-cta", "sponsor", "lp-note", "lp-sub", "lp-fine", "lp-hint", "lp-links", "lp-f-icon", "upright", "landingGate"]:
    for mm in re.finditer(rf"[^{{]*{kw}[^{{]*\{{[^}}]*\}}", lnd):
        print("  ", " ".join(mm.group(0).split())[:260])

# .link CSS affordance
print("\n== .link / tr.link CSS ==")
for mm in re.finditer(r"(?:tr\.)?link[^{]*\{[^}]*\}", sty):
    print("  ", " ".join(mm.group(0).split())[:200])
