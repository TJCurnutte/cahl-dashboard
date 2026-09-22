#!/usr/bin/env python3
"""R10 juror5: first-hand fetch of deployed v70 assets + timed API probes."""
import json, time, urllib.request, gzip, os, sys

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/work/j5"
os.makedirs(OUT, exist_ok=True)

def fetch(path, timeout=60, label=None):
    t0 = time.time()
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            dt = time.time() - t0
            return raw, dt, r.status, len(raw)
    except Exception as e:
        return None, time.time() - t0, str(e), 0

# --- assets ---
for path, out in [("/", "shell.html"), ("/app.js?v=70", "app70.js"),
                  ("/style.css?v=70", "style70.css"), ("/landing.css?v=70", "landing70.css")]:
    raw, dt, st, n = fetch(path, 40)
    ok = raw is not None
    if ok and out == "shell.html":
        open(os.path.join(OUT, out), "wb").write(raw)
    if ok and out != "shell.html":
        open(os.path.join(OUT, out), "wb").write(raw)
    print(f"{path}  {dt:.2f}s status={st} bytes={n} ok={ok}")

# --- API probes (timed, single-shot) ---
for path, out in [("/api/today", "api_today.json"), ("/api/teams", "api_teams.json"),
                  ("/api/leaders", "api_leaders.json"), ("/api/players", "api_players.json")]:
    raw, dt, st, n = fetch(path, 59)
    if raw:
        open(os.path.join(OUT, out), "wb").write(raw)
    print(f"{path}  {dt:.2f}s status={st} wire_bytes={n} ok={raw is not None}")
