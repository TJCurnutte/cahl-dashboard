#!/usr/bin/env python3
"""R10 juror4 API probes: players timing + payload + persistence headers; all other endpoints timed."""
import json, time, urllib.request, gzip, os

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
            return raw, time.time() - t0, r.status, dict(r.headers)
    except Exception as e:
        return None, time.time() - t0, str(e), {}

print("=== /api/players single-shot (warm/cold as-found) ===")
raw, dt, st, hdrs = fetch("/api/players")
if raw:
    players = json.loads(raw)
    print(f"  {dt:.2f}s  decoded={len(raw):,}B  players={len(players)}")
    print(f"  age={hdrs.get('Age')}  cache-control={hdrs.get('Cache-Control')}")
    print(f"  x-vercel-cache={hdrs.get('X-Vercel-Cache')}  server-timing={hdrs.get('Server-Timing')}")
    # payload hygiene census
    names = [p.get("name", "") for p in players]
    bad = [n for n in names if n in ("Bye Week", "Team Blue", "Team Red")]
    print(f"  hygiene: {len(bad)} Bye-Week/Team-Blue/Red rows")
    with open(f"{OUT}/players.json", "wb") as f:
        f.write(raw)
else:
    print(f"  FAILED: {st} after {dt:.2f}s")

print("\n=== /api/players burst x5 (parallel) ===")
import concurrent.futures as cf
t0 = time.time()
with cf.ThreadPoolExecutor(5) as ex:
    futs = [ex.submit(fetch, "/api/players") for _ in range(5)]
    results = [f.result() for f in futs]
wall = time.time() - t0
for i, (raw, dt, st, h) in enumerate(results, 1):
    n = len(json.loads(raw)) if raw else 0
    print(f"  #{i}: {dt:.2f}s status={st} players={n}")
print(f"  wall: {wall:.2f}s")

print("\n=== other endpoints ===")
for ep in ["/api/version", "/api/today", "/api/today/scores", "/api/leaders", "/api/league", "/api/teams?search=Nomads", "/api/players/lookup?q=Brandt"]:
    raw, dt, st, h = fetch(ep)
    size = len(raw) if raw else 0
    print(f"  {ep}: {dt:.2f}s status={st} bytes={size:,}")
