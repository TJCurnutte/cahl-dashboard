#!/usr/bin/env python3
"""R9 juror5 part 6: v63 vs v67 app.js diff of leader-row sites + teams shape + league payload null census."""
import os, re, json, difflib, urllib.request, ssl, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
R8 = os.path.expanduser("~/cahl-dashboard/qa/jury_r8")

# find saved v63 app.js
cands = []
for root, dirs, files in os.walk(R8):
    for f in files:
        if "app.js" in f:
            cands.append(os.path.join(root, f))
print("v63 app.js candidates:", cands)

if cands:
    v63 = open(cands[0], "r", errors="replace").read()
    v67 = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
    print("v63 len:", len(v63), "v67 len:", len(v67))
    # find the Top Scorers emitter in v63
    for m in re.finditer(r"Top Scorers", v63):
        ln = v63[:m.start()].count("\n") + 1
        print(f"v63 'Top Scorers' at L{ln}")
        print("   ", v63.split("\n")[ln-1][:250])
    for m in re.finditer(r"Top Scorers", v67):
        ln = v67[:m.start()].count("\n") + 1
        print(f"v67 'Top Scorers' at L{ln}")
        print("   ", v67.split("\n")[ln-1][:250])
    # unified diff snippets around selectPlayer emits
    sm = difflib.SequenceMatcher(None, v63.split("\n"), v67.split("\n"), autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    print(f"\n{len(ops)} changed hunks")
    for tag, i1, i2, j1, j2 in ops:
        if any("selectPlayer" in l for l in v67.split("\n")[j1:j2]) or any("selectPlayer" in l for l in v63.split("\n")[i1:i2]):
            print(f"--- {tag} v63[{i1+1}:{i2}] -> v67[{j1+1}:{j2}]")
            for l in v63.split("\n")[i1:i2][:4]:
                print("  -", l[:230])
            for l in v67.split("\n")[j1:j2][:4]:
                print("  +", l[:230])

# teams shape
teams = json.load(open(os.path.join(OUT, "teams.json")))
print("\n== /api/teams shape ==")
print("type:", type(teams).__name__)
if isinstance(teams, dict):
    print("keys:", list(teams.keys())[:15])
    for k, v in teams.items():
        if isinstance(v, list) and v:
            print(f"  {k}: n={len(v)}, first item keys:", list(v[0].keys())[:10] if isinstance(v[0], dict) else v[0])
        elif isinstance(v, dict):
            print(f"  {k}: dict keys {list(v.keys())[:8]}")
