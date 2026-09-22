#!/usr/bin/env python3
"""R10 juror4: fetch deployed v70 assets + version + timed API probes."""
import json, time, urllib.request, gzip, io, os, sys

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed"
os.makedirs(OUT, exist_ok=True)

def fetch(path, timeout=60):
    t0 = time.time()
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) JuryR10QAProbe",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = r.headers.get("Content-Encoding", "")
            if enc == "gzip":
                raw = gzip.decompress(raw)
            dt = time.time() - t0
            return raw, dt, r.status, len(raw)
    except Exception as e:
        return None, time.time() - t0, str(e), 0

# 1. version
raw, dt, st, n = fetch("/api/version")
print(f"/api/version {dt:.2f}s status={st} body={raw[:120] if raw else None}")

# 2. index.html first to see asset URLs
raw, dt, st, n = fetch("/")
print(f"/ {dt:.2f}s status={st} bytes={n}")
if raw:
    with open(f"{OUT}/index.html", "wb") as f:
        f.write(raw)
    idx = raw.decode("utf-8", "replace")
    # print asset refs + version strings
    import re
    for m in re.finditer(r'(?:src|href)="([^"]*(?:app\.js|style\.css|landing\.css)[^"]*)"', idx):
        print("  ASSET:", m.group(1))
    for m in re.finditer(r'(?:APP_VERSION|JS_VERSION)\s*=\s*(\d+)', idx):
        print("  VER:", m.group(0))

# 3. fetch assets at v70 (and unpinned as fallback)
for url, name in [
    ("/static/js/app.js?v=70", "app.js"),
    ("/static/css/style.css?v=70", "style.css"),
    ("/static/css/landing.css?v=70", "landing.css"),
]:
    raw, dt, st, n = fetch(url)
    if raw is None or (len(raw) > 0 and b"<!DOCTYPE" in raw[:200]):
        raw, dt, st, n = fetch(url.split("?")[0])
    if raw:
        with open(f"{OUT}/{name}", "wb") as f:
            f.write(raw)
    print(f"{name}: {dt:.2f}s status={st} bytes={n} head={raw[:60] if raw else None!r}")
