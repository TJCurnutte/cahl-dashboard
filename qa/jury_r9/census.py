#!/usr/bin/env python3
"""R9 juror5 part 3: esc census, dataStamp census, live payload checks, landing markup."""
import urllib.request, ssl, json, os, re, time

BASE = "https://cahl.neural-forge.io"
OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lines = app.split("\n")
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()
lndcss = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
htm = open(os.path.join(OUT, "index.html"), "r", errors="replace").read()

# ---- FIX 2 census: every data.error interpolation site, esc'd or raw ----
print("== data.error interpolation census (app.js) ==")
pat = re.compile(r"\$\{[^}]*data\.error[^}]*\}")
for m in pat.finditer(app):
    ln = app[:m.start()].count("\n") + 1
    raw = "esc(" not in m.group(0)
    print(f"  L{ln} {'RAW!!!' if raw else 'esc-ok'} :: {m.group(0)[:90]}")
# also generic .error / message interpolations near render sites
print("\n== e.message / err interpolation census ==")
for m in re.finditer(r"\$\{(?:esc\()?e?r?r?o?r?[^}]{0,60}\.message[^}]*\}", app):
    ln = app[:m.start()].count("\n") + 1
    seg = m.group(0)
    print(f"  L{ln} :: {seg[:100]}")

# ---- FIX 3 census: dataStamp ----
print("\n== dataStamp / UPDATED stamp census ==")
for kw in ["UPDATED", "paintStamp", "setInterval", "new Date()"]:
    hits = [app[:m.start()].count("\n") + 1 for m in re.finditer(re.escape(kw), app)]
    print(f"  {kw}: lines {hits}")

print("\n== dataStamp function body ==")
idx = app.find("function paintStamp")
if idx == -1:
    idx = app.find("paintStamp")
print(app[max(0, idx-200): idx+900] if idx != -1 else "paintStamp NOT FOUND")

# ---- live payloads ----
def get(path, timeout=55):
    req = urllib.request.Request(BASE + path, headers=UA)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        data = r.read()
        return data, r.status, time.time() - t0

print("\n== live payloads ==")
for path in ["/api/today", "/api/teams", "/api/leaders"]:
    try:
        data, st, dt = get(path)
        j = json.loads(data)
        print(f"  {path}: {st} {dt:.2f}s bytes={len(data)}")
        if path == "/api/today":
            print("    keys:", list(j.keys())[:12])
            games = j.get("games") or j.get("today") or []
            print("    games n:", len(games) if isinstance(games, list) else type(games))
            blob = data.decode("utf-8", "replace")
            for tok in ["Bye Week", "Team Blue", "Team Red"]:
                print(f"    contains {tok!r}:", tok in blob)
        if path == "/api/teams":
            blob = data.decode("utf-8", "replace")
            for tok in ["Bye Week", "Team Blue", "Team Red"]:
                print(f"    contains {tok!r}:", tok in blob)
            if isinstance(j, dict):
                for k in ["teams", "leagues"]:
                    if k in j and isinstance(j[k], list):
                        print(f"    {k} n={len(j[k])}")
        if path == "/api/leaders":
            print("    keys:", list(j.keys())[:12])
            pts = j.get("points") or []
            nulls = sum(1 for p in (pts if isinstance(pts, list) else []) if not p.get("player_id"))
            print(f"    points n={len(pts) if isinstance(pts, list) else '?'}, null player_id rows: {nulls}")
    except Exception as e:
        print(f"  {path}: ERR {str(e)[:120]}")
