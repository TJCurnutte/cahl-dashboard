#!/usr/bin/env python3
"""Jury R8 J5 part 6: teams payload Bye Week, leaders shape, leadIdx, sticky scroll."""
import re, json, pathlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")

# api_teams structure + Bye Week location
teams = json.loads((Q / "api_teams.json").read_text())
print("api_teams type:", type(teams).__name__, "len:", len(teams))
sample = teams[0] if isinstance(teams, list) else None
print("entry keys:", list(sample.keys()) if sample else "?")
for i, t in enumerate(teams if isinstance(teams, list) else []):
    nm = str(t.get("name") or t.get("team") or "")
    if nm in ("Bye Week", "Team Blue", "Team Red"):
        print(f"  [{i}] {nm!r} league={t.get('league') or t.get('league_name')!r} id={str(t.get('id') or t.get('team_id'))[:20]}…")
lg = json.loads((Q / "api_league.json").read_text())
pt = (lg.get("leaders") or {}).get("points") or []
print("\nleague leaders points[0] full:", json.dumps(pt[0]) if pt else "EMPTY")
print("league leaders points[1] full:", json.dumps(pt[1]) if len(pt) > 1 else "")

# leadIdx usage
for m in re.finditer(r"leadIdx", js):
    ln = js.count("\n", 0, m.start()) + 1
    print(f"\nleadIdx L{ln}: {js[max(0,m.start()-150):m.start()+200]}".replace(chr(10), " | "))

# sticky header + scroll listener
print("\nposition:sticky count in css:", len(re.findall(r"position:\s*sticky", css)))
for m in re.finditer(r"position:\s*sticky[^;]*;?\s*/\*?.{0,80}", css):
    ln = css.count("\n", 0, m.start()) + 1
    sel = css[max(0, css.rfind("}", 0, m.start())):m.start() + 60].strip().split("\n")[-1]
    print(f"  css L{ln}: {sel[:110]}")
for m in re.finditer(r"addEventListener\(\s*['\"]scroll", js):
    ln = js.count("\n", 0, m.start()) + 1
    print(f"  js scroll listener L{ln}: {js[max(0,m.start()-120):m.start()+180]}".replace(chr(10), " | "))

# gate a11y: dialog aria + focus trap
print("\ngate focus trap refs:", len(re.findall(r"focus", js[:3000])))
# escape key on gate?
print("Escape handler refs in first 3k chars:", js[:3000].count("Escape"), "| keydown count:", len(re.findall(r"keydown", js[:3000])))
