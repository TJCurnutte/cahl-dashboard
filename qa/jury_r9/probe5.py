#!/usr/bin/env python3
"""R9 juror5 part 11: enclosing function of L2318-2331 + its fetch; verify league-tab conditional consumes /api/league leaders."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lines = app.split("\n")

# find enclosing async function for a line by scanning backwards for 'function NAME('
def enclosing_fn(target_ln):
    best = None
    for m in re.finditer(r"(?:async\s+)?function\s+(\w+)\s*\(|window\.(\w+)\s*=\s*(?:async\s*)?\(", app):
        ln = app[:m.start()].count("\n") + 1
        if ln <= target_ln:
            name = m.group(1) or m.group(2)
            best = (ln, name)
    return best

for ln in (2318, 2329, 1576, 2521):
    print(f"L{ln} enclosing:", enclosing_fn(ln))

print("\n== context L2300-2345 (players renderers) ==")
for i in range(2299, 2345):
    print(f"L{i+1}: {lines[i][:170]}")
