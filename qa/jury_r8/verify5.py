#!/usr/bin/env python3
"""Jury R8 J5 part 5: team filter, L1489 context, league framing, esc census."""
import re, json, pathlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")

def ctx(label, pat, before=200, after=400, maxhits=6, flags=0):
    print(f"\n=== {label} ===")
    for m in list(re.finditer(pat, js, flags))[:maxhits]:
        s = max(0, m.start() - before)
        e = min(len(js), m.end() + after)
        ln = js.count("\n", 0, m.start()) + 1
        print(f"  --- L{ln} ---")
        print("  " + js[s:e].replace("\n", "\n  ")[:900])

ctx("teams ingest / filter", r"state\.teams\s*=", before=0, after=500, maxhits=3)
ctx("bye/scrim filter anywhere", r"[Bb]ye\s*[Ww]eek", before=150, after=250, maxhits=8)
ctx("L1489 inline-styled heading", r"margin:18px 0 10px;color:var\(--text\)", before=250, after=120, maxhits=2)
ctx("leaderSection def", r"function leaderSection", before=0, after=600, maxhits=1)
ctx("playoff race on zero standings", r"playoff_cutoff", before=100, after=400, maxhits=3)

lg = json.loads((Q / "api_league.json").read_text())
print("\nleague playoff_cutoff:", lg.get("playoff_cutoff"), "| season:", json.dumps(lg.get("season"))[:120])
print("league championship:", json.dumps(lg.get("championship"))[:150])
print("league leaders keys:", list((lg.get("leaders") or {}).keys()))
lp = (lg.get("leaders") or {}).get("points") or []
print("league leaders points[:3]:", [(p.get('name'), p.get('value') or p.get('points')) for p in lp[:3]])

# standings zero-frame: does app.js gate the race viz on data?
for pat in [r"allZero|all_zero|zeroSeason|season hasn", r"clinch|elim"]:
    ms = list(re.finditer(pat, js))
    print(f"\npattern {pat!r}: {len(ms)} hits")
    for m in ms[:4]:
        ln = js.count("\n", 0, m.start()) + 1
        print(f"  L{ln}: {js[max(0,m.start()-80):m.start()+160]}".replace(chr(10), ' | '))

# esc census total
print("\nesc( total calls:", len(re.findall(r"\besc\(", js)))
