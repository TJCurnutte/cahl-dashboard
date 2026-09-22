#!/usr/bin/env python3
"""R9 juror5 part 8: league payload w/ real id + analytics endpoint source + null census on L2521/L282 live data."""
import os, re, json, urllib.request, ssl, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
BASE = "https://cahl.neural-forge.io"
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

def get(path, timeout=55):
    req = urllib.request.Request(BASE + path, headers=UA)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read(), r.status, time.time() - t0

# what does loadAnalyticsContent fetch?
i = app.find("async function loadAnalyticsContent")
if i == -1: i = app.find("loadAnalyticsContent")
seg = app[i:i+1600]
print("== loadAnalyticsContent head ==")
print(seg[:1500])

# league fetch url
for m in re.finditer(r"fetch\(`/api/league/[^`]*`", app):
    print("\nleague fetch template:", m.group(0))

# real league id from teams.json
teams = json.load(open(os.path.join(OUT, "teams.json")))
lid = teams[0]["league_id"]
lname = teams[0]["league_name"]
data, st, dt = get(f"/api/league/{lid}")
print(f"\n== /api/league/{lid[:12]}… ({lname}): {st} {dt:.2f}s bytes={len(data)}")
j = json.loads(data)
leaders = j.get("leaders") or {}
for k in ["points", "goals", "assists"]:
    rows = leaders.get(k) or []
    nulls = sum(1 for p in rows if not p.get("player_id"))
    print(f"  leaders.{k}: n={len(rows)}, null player_id={nulls}")
    if rows:
        print("    sample:", {kk: rows[0].get(kk) for kk in ["name", "team", "player_id", "rank", "value"]})
standings = j.get("standings") or []
print(f"  standings n={len(standings)}; pts all-zero:", all((s.get('pts') or 0) == 0 for s in standings))
print("  playoff_cutoff:", j.get("playoff_cutoff"), "| season:", j.get("season"))
if standings:
    print("  sample standing:", {kk: standings[0].get(kk) for kk in ["team", "gp", "w", "l", "otl", "pts", "team_id"]})

# players endpoint timing + payload (R8-A carry)
print("\n== /api/players timing ==")
pdata, pst, pdt = get("/api/players", timeout=58)
print(f"/api/players: {pst} {pdt:.2f}s bytes={len(pdata)} encoding-header-checked-below")
jp = json.loads(pdata)
plist = jp if isinstance(jp, list) else (jp.get("players") or [])
print("players n:", len(plist))
if plist:
    print("sample keys:", list(plist[0].keys())[:12])
