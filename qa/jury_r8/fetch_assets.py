#!/usr/bin/env python3
"""R8 juror 4: fetch deployed v63 assets + light endpoints (Chrome-free)."""
import gzip, io, json, os, time, urllib.request

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/deployed"
os.makedirs(OUT, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def fetch(path, out=None, gzip_ok=False):
    url = BASE + path
    req = urllib.request.Request(url, headers=dict(UA, **({"Accept-Encoding": "gzip"} if gzip_ok else {})))
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=55) as r:
        body = r.read()
        enc = r.headers.get("Content-Encoding", "")
        if enc == "gzip":
            body = gzip.decompress(body)
        dt = time.time() - t0
    size = len(body)
    if out:
        with open(os.path.join(OUT, out), "wb") as f:
            f.write(body)
    return dt, size, enc

results = []
for path, out in [
    ("/", "index.html"),
    ("/static/js/app.js?v=63", "app.js"),
    ("/static/css/style.css?v=63", "style.css"),
]:
    dt, size, enc = fetch(path, out)
    results.append(f"{path}: {dt:.2f}s {size}B")

# light endpoints, timed
for path in ["/api/version", "/api/today", "/api/today/scores", "/api/league", "/api/leaders"]:
    try:
        dt, size, enc = fetch(path, None, gzip_ok=True)
        results.append(f"{path}: {dt:.2f}s {size}B (enc={enc or 'identity'})")
    except Exception as e:
        results.append(f"{path}: ERROR {e}")

ver = fetch("/api/version")
print("\n".join(results))
print("---")
# version payload inline
req = urllib.request.Request(BASE + "/api/version", headers=UA)
print(urllib.request.urlopen(req, timeout=10).read().decode()[:300])
