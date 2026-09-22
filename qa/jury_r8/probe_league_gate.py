#!/usr/bin/env python3
"""R8 juror4: league timing + landing.css gate audit (short probes)."""
import gzip, json, re, time, urllib.request

BASE = "https://cahl.neural-forge.io"
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}

def get(path, timeout=45):
    req = urllib.request.Request(BASE + path, headers=UA)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
        if r.headers.get("Content-Encoding", "") == "gzip":
            b = gzip.decompress(b)
    return time.time() - t0, b

dt, body = get("/api/today")
d = json.loads(body)
print(f"/api/today: {dt:.2f}s games={len(d.get('today', []))}")
leagues = d.get("leagues", [])
print("leagues:", [(l.get("id"), l.get("name")) for l in leagues][:5])
if leagues:
    lid = leagues[0]["id"]
    import urllib.parse
    q = urllib.parse.quote(lid, safe="")
    try:
        dt2, b2 = get(f"/api/league/{q}")
        print(f"/api/league/{q[:40]}…: {dt2:.2f}s {len(b2)}B")
    except Exception as e:
        print(f"/api/league/{q[:40]}…: ERROR {e}")

# landing.css
dt3, b3 = get("/static/css/landing.css?v=63")
L = b3.decode("utf-8", "replace")
open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/deployed/landing.css", "w").write(L)
print(f"\nlanding.css: {dt3:.2f}s {len(b3)}B")
for pat in [r'\.gate-cta', r'\.gate-card', r'backdrop-filter', r'min-height', r'44', r'prefers-reduced-motion', r'focus-visible', r'@keyframes']:
    hits = [(L[:m.start()].count("\n")+1, L.split("\n")[L[:m.start()].count("\n")].strip()[:130]) for m in re.finditer(pat, L)]
    print(f"\n-- {pat}: {len(hits)}")
    for n, l in hits[:6]: print(f"  L{n}: {l}")
