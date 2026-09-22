#!/usr/bin/env python3
"""R10 finish: burst /api/players, /api/league real id, playersPartial UI census."""
import json, time, urllib.request, gzip, os
import concurrent.futures as cf

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10"

def fetch(path, timeout=90):
    t0 = time.time()
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) JuryR10QAProbe",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            return raw, time.time() - t0, r.status
    except Exception as e:
        return None, time.time() - t0, str(e)

print("=== /api/players burst x5 (parallel, single-flight check) ===")
t0 = time.time()
with cf.ThreadPoolExecutor(5) as ex:
    futs = [ex.submit(fetch, "/api/players") for _ in range(5)]
    results = [f.result() for f in futs]
wall = time.time() - t0
for i, (raw, dt, st) in enumerate(results, 1):
    if raw:
        body = json.loads(raw)
        n = len(body.get("players", [])) if isinstance(body, dict) else len(body)
        part = body.get("partial") if isinstance(body, dict) else "?"
        print(f"  #{i}: {dt:.2f}s status={st} players={n} partial={part}")
    else:
        print(f"  #{i}: {dt:.2f}s status={st} FAILED")
print(f"  wall: {wall:.2f}s")

print("\n=== /api/league with real id ===")
raw, dt, st = fetch("/api/today")
league_id = json.loads(raw)["leagues"][0]["id"]
raw, dt, st = fetch(f"/api/league/{league_id}")
print(f"  /api/league/{league_id[:12]}...: {dt:.2f}s status={st} bytes={len(raw) if raw else 0:,}")
if raw:
    body = json.loads(raw)
    for k, v in body.items():
        print(f"    {k}: {type(v).__name__}" + (f" ({len(v)})" if isinstance(v, (list, dict)) else f" = {v}"))
    # leaders player_id census on live league payload (R9-5's dead-links find)
    for sec in ("points", "goals", "assists"):
        rows = body.get(sec) or []
        nulls = sum(1 for r in rows if not r.get("player_id"))
        print(f"    leaders.{sec}: {len(rows)} rows, {nulls} null player_id")
    # standings hygiene
    standings = body.get("standings") or []
    bad = [r.get("name", "") for r in standings if r.get("name") in ("Bye Week", "Team Blue", "Team Red")]
    print(f"    standings hygiene: {len(bad)} bad rows of {len(standings)}")

print("\n=== playersPartial UI rendering in app.js ===")
app = open(f"{OUT}/deployed/app.js", encoding="utf-8", errors="replace").read()
for i, ln in enumerate(app.split("\n"), 1):
    if "playersPartial" in ln:
        print(f"  L{i}: {ln.strip()[:120]}")
