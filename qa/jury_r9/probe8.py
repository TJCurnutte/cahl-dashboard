#!/usr/bin/env python3
"""R9 juror5 part 15: mono token values, boot gate storage read vs write, Escape handlers."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()

print("== mono/display token defs ==")
for m in re.finditer(r"--(mono-(?:xs|sm|md)|display):\s*[^;]+;", sty):
    print("  ", m.group(0).strip()[:80])

print("\n== boot gate read (cahl-entered) ==")
for m in re.finditer(r".{0,120}cahl-entered.{0,120}", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln}: …{' '.join(m.group(0).split())[:200]}…")

print("\n== Escape/keydown handlers census ==")
for m in re.finditer(r"keydown|key === 'Escape'|key === 'Esc'", app):
    ln = app[:m.start()].count("\n") + 1
    seg = app[max(0, m.start()-60): m.start()+80].replace("\n", " ")
    print(f"  L{ln}: …{seg[:130]}…")
