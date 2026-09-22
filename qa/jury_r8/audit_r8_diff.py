#!/usr/bin/env python3
"""R8 juror3 audit: v61 (R7 baseline) vs v63 (deployed) CSS diff summary."""
import re, subprocess

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
V63 = f"{R8}/style_v63.css"
V61 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r7/style_v61.css"

# --- unified diff stats via file read (no git) ---
added, removed = [], []
with open(V63, encoding="utf-8", errors="replace") as f_new, open(V61, encoding="utf-8", errors="replace") as f_old:
    import difflib
    for line in difflib.unified_diff(f_old.readlines(), f_new.readlines(), fromfile="v61", tofile="v63", n=2):
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:].rstrip())
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:].rstrip())

print(f"=== v61 -> v63: +{len(added)} / -{len(removed)} lines ===\n")

def show(tag, lines, cap=80):
    print(f"--- {tag} ({len(lines)} lines, showing {min(len(lines),cap)}) ---")
    for l in lines[:cap]:
        print(l)
    if len(lines) > cap:
        print(f"... ({len(lines)-cap} more)")
    print()

show("ADDED", added)
show("REMOVED", removed, 80)
