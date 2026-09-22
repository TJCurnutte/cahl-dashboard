#!/usr/bin/env python3
"""Jury R8 J5 part 7: sticky rules, teams typeahead source, players payload sanity."""
import re, json, pathlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")

print("=== position:sticky contexts ===")
for m in re.finditer(r"position:\s*sticky", css):
    ln = css.count("\n", 0, m.start()) + 1
    block_start = css.rfind("\n", 0, css.rfind("}", 0, m.start()))
    print(f"  css L{ln}: {css[block_start:m.end()+120].strip()[:220]}")

print("\n=== team search index source ===")
for m in re.finditer(r"api/teams", js):
    ln = js.count("\n", 0, m.start()) + 1
    print(f"  L{ln}: {js[max(0,m.start()-160):m.start()+160]}".replace(chr(10), " | "))

print("\n=== players payload sanity ===")
p = json.loads((Q / "api_players.json").read_text())
print("type:", type(p).__name__, "len:", len(p) if isinstance(p, list) else list(p.keys()))
rows = p if isinstance(p, list) else (p.get("players") or [])
print("rows:", len(rows))
if rows:
    print("row keys:", list(rows[0].keys()))
    names = [str(r.get("name") or "") for r in rows[:400]]
    weird = [n for n in names if not n.strip() or "undefined" in n or "null" in n]
    print("weird names in first 400:", weird[:5] or "none")
    vals = [r.get("points") or r.get("value") or 0 for r in rows[:50]]
    print("first-50 points:", vals[:15])

print("\n=== hasOpp hero site context (L1364) ===")
ln0 = 1355
print("\n".join(f"{i+1}| {l}" for i, l in enumerate(js.split('\n')[ln0:ln0+22])))

print("\n=== error copy near L2446 (raw || fallback) ===")
ls = js.split("\n")
print("\n".join(f"{i+2440}| {ls[i+2439]}" for i in range(8)))
