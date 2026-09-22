#!/usr/bin/env python3
"""Jury R9 juror5 — fetch deployed v67 assets Chrome-free and byte-verify the R8 fixes."""
import urllib.request, ssl, json, os, sys, re

BASE = "https://cahl.neural-forge.io"
OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
os.makedirs(OUT, exist_ok=True)
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

def get(path, binary=False):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=55, context=ctx) as r:
        data = r.read()
        ctype = r.headers.get("Content-Type", "")
        clen = r.headers.get("Content-Length", "?")
        return data, r.status, dict(r.headers)

results = {}
# 1. shell + version
html, st, hdrs = get("/")
open(os.path.join(OUT, "index.html"), "wb").write(html)
results["/"] = (st, len(html))
ver, st2, _ = get("/api/version")
results["/api/version"] = (st2, ver.decode()[:120])

# 2. JS/CSS at ?v=67
for name, path in [("app.js", "/static/js/app.js?v=67"),
                   ("style.css", "/static/css/style.css?v=67"),
                   ("landing.css", "/static/css/landing.css?v=67")]:
    try:
        data, st, hdrs = get(path)
        open(os.path.join(OUT, name), "wb").write(data)
        results[path] = (st, len(data), hdrs.get("Content-Encoding", "none"))
    except Exception as e:
        results[path] = ("ERR", str(e)[:100])

print("== fetch results ==")
for k, v in results.items():
    print(k, "->", v)

app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()
lnd = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
htm = open(os.path.join(OUT, "index.html"), "r", errors="replace").read()

print("\n== version markers ==")
print("APP_VERSION in shell:", re.findall(r"APP_VERSION\s*=\s*(\d+)", htm))
print("app.js?v= in shell:", sorted(set(re.findall(r"app\.js\?v=(\d+)", htm))))
print("style.css?v= in shell:", sorted(set(re.findall(r"style\.css\?v=(\d+)", htm))))
print("landing.css?v= in shell:", sorted(set(re.findall(r"landing\.css\?v=(\d+)", htm))))
print("JS_VERSION const in app.js:", re.findall(r"JS_VERSION\s*=\s*(\d+)", app))

# FIX 1: Top Scorers / leaderSection conditional onclick on p.player_id
print("\n== FIX 1: conditional player link in Top Scorers / leaderSection ==")
for m in re.finditer(r".{0,160}player_id.{0,220}", app):
    seg = m.group(0)
    if "onclick" in seg or "selectPlayer" in seg or "link" in seg:
        ln = app[:m.start()].count("\n") + 1
        print(f"L{ln}: {seg[:340]!r}")
