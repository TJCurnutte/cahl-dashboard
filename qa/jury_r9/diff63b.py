#!/usr/bin/env python3
"""R9 juror5 part 7: v63 L2510 diff hunk + teams list shape + live league payload null census."""
import os, re, json, difflib, urllib.request, ssl, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
v63 = open(os.path.expanduser("~/cahl-dashboard/qa/jury_r8/app.js"), "r", errors="replace").read()
v67 = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
l63 = v63.split("\n"); l67 = v67.split("\n")

print("== v63 L2509-2511 (the R8-B cited site) ==")
for i in range(2508, 2511):
    print(f"v63 L{i+1}:", l63[i][:260])
print("\n== v67 L2520-2522 ==")
for i in range(2519, 2522):
    print(f"v67 L{i+1}:", l67[i][:260])

sm = difflib.SequenceMatcher(None, l63, l67, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
print(f"\n{len(ops)} changed hunks; hunks touching v63 L2440-2530:")
for tag, i1, i2, j1, j2 in ops:
    if 2430 <= i1 <= 2535:
        print(f"--- {tag} v63[{i1+1}:{i2}] -> v67[{j1+1}:{j2}]")
        for l in l63[i1:i2][:3]:
            print("  -", l[:240])
        for l in l67[j1:j2][:3]:
            print("  +", l[:240])

# esc fix sites: v63 L2306/2317/2446 diff
print("\n== v63 esc sites L2300-2320 & L2444-2450 (before) ==")
print("v63 L2306:", l63[2305][:200])
print("v63 L2317:", l63[2316][:200])
print("v63 L2446:", l63[2445][:200])

# teams list
teams = json.load(open(os.path.join(OUT, "teams.json")))
print("\n== /api/teams (list) ==")
print("n teams:", len(teams), "| first item keys:", list(teams[0].keys())[:12])
leagues = {}
for t in teams:
    leagues.setdefault(t.get("league_id") or t.get("league") or "?", 0)
    leagues[t.get("league_id") or t.get("league") or "?"] += 1
print("league_id distribution:", dict(list(leagues.items())[:12]))
# find a 'day' league with actual stats (not preseason-thin exhibition)
sample = teams[:3]
for t in sample:
    print("  sample:", {k: t.get(k) for k in list(teams[0].keys())[:8]})
