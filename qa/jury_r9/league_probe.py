#!/usr/bin/env python3
"""R9 juror5 part 5: player-row link sites 2.0 — ALL sites emitting selectPlayer in a row template,
plus how data flows (does the live league payload null player_id?)."""
import urllib.request, ssl, json, os, re, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lines = app.split("\n")

print("== ALL selectPlayer( emit sites (row templates) ==")
for m in re.finditer(r"selectPlayer", app):
    ln = app[:m.start()].count("\n") + 1
    seg = app[max(0, m.start()-80): m.start()+160].replace("\n", " ")
    print(f"  L{ln}: …{seg[:220]}…")

print("\n== spTok / player token nav sites ==")
for m in re.finditer(r"spTok|selectPlayerToken", app):
    ln = app[:m.start()].count("\n") + 1
    seg = app[max(0, m.start()-60): m.start()+120].replace("\n", " ")
    print(f"  L{ln}: …{seg[:180]}…")

# check league payload player_id nullability live
BASE = "https://cahl.neural-forge.io"
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

teams = json.load(open(os.path.join(OUT, "teams.json"))) if os.path.exists(os.path.join(OUT, "teams.json")) else None
if teams is None:
    req = urllib.request.Request(BASE + "/api/teams", headers=UA)
    with urllib.request.urlopen(req, timeout=55, context=ctx) as r:
        teams = json.loads(r.read())
    json.dump(teams, open(os.path.join(OUT, "teams.json"), "w"))

leagues = teams.get("leagues") if isinstance(teams, dict) else None
lid = None
if leagues:
    # pick the league the R8 round tested: first league id
    lid = leagues[0].get("id")
print("league id used:", lid)

t0 = time.time()
req = urllib.request.Request(BASE + f"/api/league/{lid}", headers=UA)
with urllib.request.urlopen(req, timeout=55, context=ctx) as r:
    ldata = json.loads(r.read())
dt = time.time() - t0
print(f"/api/league/{lid}: {dt:.2f}s, keys: {list(ldata.keys())[:10]}")

leaders = ldata.get("leaders") or {}
pts = leaders.get("points") or []
nulls = [p.get("name") for p in pts if not p.get("player_id")]
print(f"league leaders points n={len(pts)}, null player_id rows={len(nulls)} {nulls[:5]}")

standings = ldata.get("standings") or []
print(f"standings n={len(standings)}, sample team_id present:", bool(standings and standings[0].get("team_id")))
allzero = all((s.get('pts') or 0) == 0 for s in standings)
print("standings all-zero pts:", allzero, "| playoff_cutoff:", ldata.get("playoff_cutoff"))
