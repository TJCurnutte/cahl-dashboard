#!/usr/bin/env python3
"""Jury R9 juror2 — fetch deployed v67 assets Chrome-free, hash them."""
import urllib.request, ssl, json, os, hashlib

BASE = "https://cahl.neural-forge.io"
OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
os.makedirs(OUT, exist_ok=True)
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

def get(path, timeout=50):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read(), r.status, dict(r.headers)

res = {}
html, st, _ = get("/")
open(os.path.join(OUT, "index.html"), "wb").write(html)
res["/"] = (st, len(html))
ver, st2, _ = get("/api/version")
res["/api/version"] = (st2, ver.decode()[:80])

for name, path in [("app.js", "/static/js/app.js?v=67"),
                   ("style.css", "/static/css/style.css?v=67"),
                   ("landing.css", "/static/css/landing.css?v=67")]:
    data, st, hdrs = get(path)
    open(os.path.join(OUT, name), "wb").write(data)
    res[path] = (st, len(data), hdrs.get("Content-Encoding", "none"),
                 hashlib.sha256(data).hexdigest()[:12])

for k, v in res.items():
    print(k, "->", v)
