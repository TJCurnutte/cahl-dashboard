#!/usr/bin/env python3
"""R10 juror5 part 6: openPlayer def, RM selector map, today payload, catch msg, from_supabase."""
import re, json, os

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
J5 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/work/j5/"
AL = open(D + "app.js", encoding="utf-8", errors="replace").read().splitlines()
SC = open(D + "style.css", encoding="utf-8", errors="replace").read().splitlines()

print("=== openPlayer refs ===")
for i, l in enumerate(AL):
    if "openPlayer" in l:
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== full catch L2210-2228 ===")
for j in range(2209, 2228):
    print(f"{j+1}: {AL[j][:150]}")

print("=== api() core L885-910 ===")
for j in range(884, 910):
    print(f"{j+1}: {AL[j][:150]}")

print("=== RM: selector context for each animation decl ===")
# find enclosing selector for a line: walk back to line ending with '{' at depth 0
def selector_of(ln):
    buf = []
    for j in range(ln - 1, max(0, ln - 12), -1):
        buf.insert(0, SC[j].strip())
        if "{" in SC[j]:
            break
    return " ".join(buf)
targets = [260, 362, 379, 411, 468, 769, 778, 834, 870, 945, 953, 1280, 1310]
for t in targets:
    print(f"  L{t}: {selector_of(t)[:150]}")

print("=== today payload structure ===")
t = json.load(open(J5 + "api_today.json"))
print("keys:", list(t.keys()))
for k, v in t.items():
    if isinstance(v, list):
        print(f"  {k}: list n={len(v)}")
        if v and isinstance(v[0], dict):
            print(f"    sample keys: {list(v[0].keys())[:14]}")
    elif isinstance(v, dict):
        print(f"  {k}: dict keys={list(v.keys())[:10]}")
    else:
        print(f"  {k}: {str(v)[:80]}")

print("=== from_supabase / partial markers in saved payloads ===")
for f in ["api_today.json", "api_teams.json", "api_leaders.json", "api_players.json"]:
    s = open(J5 + f, encoding="utf-8", errors="replace").read()
    pt = chr(34) + "partial" + chr(34) + ": true"
    pf = chr(34) + "partial" + chr(34) + ": false"
    print(f"  {f}: from_supabase={'from_supabase' in s} partial_true={pt in s} partial_false={pf in s}")

print("=== today games empty? ===")
games = t.get("games") or t.get("schedule") or []
print("games value type/len:", type(games).__name__, len(games) if hasattr(games, '__len__') else '')

print("=== landing.css remaining literal sizes vs system scale ===")
lc = open(D + "landing.css", encoding="utf-8", errors="replace").read()
sizes = sorted(set(re.findall(r"font-size:\s*([\d.]+)px", lc)), key=float)
print("  sizes:", sizes, "| system scale: 13/14/16/20/26/30/34 (+var tokens)")
print("  off-scale:", [s for s in sizes if s not in {"13", "14", "16", "20", "26", "30", "34"}])

print("=== style.css literal font-size census (app scale) ===")
sz2 = sorted(set(re.findall(r"font-size:\s*([\d.]+)px", "\n".join(SC))), key=float)
print("  sizes:", sz2)

print("=== landing hero title + gate-cta final state ===")
for i, l in enumerate(lc.splitlines()):
    if ".lp-title" in l and "font-size" in l:
        print(f"  L{i+1}: {l.strip()[:110]}")
    if ".lp-cta-sm" in l or ".gate-cta {" in l:
        print(f"  L{i+1}: {l.strip()[:110]}")

print("=== pos-chip / link class on guarded rows (consistency) ===")
print("  L282 keeps class=link ONLY when guarded (inside template ternary):",
      ('class=' + chr(92)*2 + '"link' + chr(92)*2 + '"` : ' + chr(39)*2 + ']>' ) in open(D+"app.js", encoding="utf-8", errors="replace").read())
