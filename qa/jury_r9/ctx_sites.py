#!/usr/bin/env python3
"""R9 juror5 part 2: context around each fix site + esc census + dataStamp census."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lines = app.split("\n")

def show(start, end, label):
    print(f"----- {label} (L{start}-{end}) -----")
    for i in range(start - 1, min(end, len(lines))):
        print(f"L{i+1}: {lines[i]}")
    print()

# Context: which renderer is L1576-1582 in?
show(1550, 1600, "L1550-1600 leaders conditional sites")
# Context: L2521 site — which function?
show(2495, 2545, "L2495-2545 league top scorers site")
# Context: L282 leaderSection
show(255, 300, "L255-300 leaderSection")
