#!/usr/bin/env python3
"""Inspect /api/players new shape + finish probes that failed."""
import json, time, urllib.request, gzip, os

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10"

def fetch(path, timeout=90):
    t0 = time.time()
    req = urllib.request.Request(Request_URL := BASE + path, headers={  # noqa
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

print("=== /api/players shape ===")
raw, dt, st, hdrs = fetch("/api/players")
if raw:
    with open(f"{OUT}/players.json", "wb") as f:
        f.write(raw)
    body = json.loads(raw)
    print(f"  {dt:.2f}s decoded={len(raw):,}B type={type(body).__name__}")
    if isinstance(body, dict):
        print(f"  keys={list(body.keys())}")
        for k, v in body.items():
            if isinstance(v, list):
                print(f"    '{k}': {len(v)} items; first={json.dumps(v[0])[:220] if v else None}")
                names = [x.get("name", "") for x in v if isinstance(x, dict)]
                bad = [n for n in names if n in ("Bye Week", "Team Blue", "Team Red")]
                print(f"    hygiene in '{k}': {len(bad)} bad rows")
            else:
                print(f"    '{k}': {json.dumps(v)[:220]}")
    # client-side parse: how does app.js consume it?
    app = open(f"{OUT}/deployed/app.js", encoding="utf-8", errors="replace").read()
    import re
    for m in re.finditer(r".*allPlayers\s*=.*", app):
        print("  CLIENT:", m.group(0).strip()[:140])
    for m in re.finditer(r".*api\('/api/players'\).*", app):
        print("  CLIENT:", m.group(0).strip()[:140])

print("\n=== endpoints that crashed last run ===")
for ep in ["/api/today", "/api/today/scores", "/api/leaders", "/api/league", "/api/teams?search=Nomads", "/api/players/lookup?q=Brandt"]:
    raw, dt, st, h = fetch(ep)
    size = len(raw) if raw else 0
    head = raw[:100] if raw else b""
    print(f"  {ep}: {dt:.2f}s status={st} bytes={size:,} head={head!r}")
