#!/usr/bin/env python3
"""Jury R8 juror2: fetch deployed v63 assets chrome-free, save + fingerprint."""
import urllib.request, hashlib, os, time, json

BASE = "https://cahl.neural-forge.io"
OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
os.makedirs(OUT, exist_ok=True)

def get(path, save=None):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "cahl-jury-r8-j2 (chrome-free audit)"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        st, fu = r.status, r.geturl()
    dt = time.time() - t0
    if save:
        with open(os.path.join(OUT, save), "wb") as f:
            f.write(body)
    return dict(path=path, status=st, final=fu, bytes=len(body), secs=round(dt, 2),
                sha16=hashlib.sha256(body).hexdigest()[:16], head=body[:110].decode("utf-8", "replace"))

targets = [
    ("/api/version", "version_v63.json"),
    ("/", "index_v63.html"),
    ("/static/css/style.css?v=63", "style_v63.css"),
    ("/static/js/app.js?v=63", "app_v63.js"),
    ("/api/today", "today_v63.json"),
]
results = []
for path, save in targets:
    try:
        r = get(path, save)
    except Exception as e:
        r = dict(path=path, error=repr(e))
    results.append(r)
    print(json.dumps(r, ensure_ascii=False))

# list prior-round saved deployed copies for diffing
qa = "/Users/traviscurnutte/cahl-dashboard/qa"
for root, dirs, files in os.walk(qa):
    for f in sorted(files):
        if f.endswith((".css", ".js", ".html")) and any(k in f for k in ("v6", "style", "app", "index")):
            p = os.path.join(root, f)
            print("PRIOR:", p.replace(qa, "qa"), os.path.getsize(p))
