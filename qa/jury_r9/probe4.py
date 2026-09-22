#!/usr/bin/env python3
"""R9 juror5 part 10: dead-team retry + repro id, landing.css blur rules, hero-next-pulse, L2329 data source, v63->v67 hunk summary."""
import os, re, json, difflib, urllib.request, ssl, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lnd = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()
BASE = "https://cahl.neural-forge.io"
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

# 1. dead-team repro id + retry
rep = os.path.expanduser("~/cahl-dashboard/qa/dead_team_repro.js")
if os.path.exists(rep):
    src = open(rep, errors="replace").read()
    ids = re.findall(r"['\"]([A-Za-z0-9-]{16,})['\"]", src)
    print("== dead_team_repro.js ids ==", ids[:6])
    dead_id = ids[0] if ids else "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
else:
    dead_id = "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
for attempt in range(2):
    try:
        req = urllib.request.Request(BASE + f"/api/team/{dead_id}", headers=UA)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=55, context=ctx) as r:
            body = r.read(); st = r.status
        print(f"dead-team try{attempt+1}: {st} {time.time()-t0:.1f}s :: {body.decode('utf-8','replace')[:300]}")
        break
    except urllib.error.HTTPError as e:
        print(f"dead-team try{attempt+1}: HTTP {e.code} :: {e.read()[:200]}")
    except Exception as e:
        print(f"dead-team try{attempt+1}: ERR {str(e)[:150]}")

# scraper side: what does a dead team page return (local repo)
for py in ["~/cahl-dashboard/scraper.py", "~/cahl-dashboard/app.py"]:
    p = os.path.expanduser(py)
    if os.path.exists(p):
        s = open(p, errors="replace").read()
        for m in re.finditer(r"no longer available", s):
            ln = s[:m.start()].count("\n") + 1
            print(f"{py}:{ln}: {s.split(chr(10))[ln-1].strip()[:160]}")

# 2. landing.css backdrop rules
print("\n== landing.css backdrop-filter rules ==")
for m in re.finditer(r"[^}]*backdrop-filter[^}]*}", lnd):
    seg = m.group(0)
    print("  ", " ".join(seg.split())[:220])

# 3. hero-next-pulse + rise-in: decorative or purposeful? RM coverage
print("\n== hero-next-pulse / rise-in ==")
for kf in ["hero-next-pulse", "rise-in"]:
    for m in re.finditer(rf"@keyframes {kf}\s*\{{[^}}]*\}}", sty):
        print(f"  {kf}:", " ".join(m.group(0).split())[:200])
    uses = [sty[:mm.start()].count("\n") + 1 for mm in re.finditer(kf, sty)]
    print(f"  {kf} refs at css lines:", uses)

# RM blocks content
print("\n== style.css RM blocks ==")
for m in re.finditer(r"@media\s*\(prefers-reduced-motion[^{]*\{", sty):
    start = m.start()
    depth = 0; i = sty.find("{", start)
    j = i
    while j < len(sty):
        if sty[j] == "{": depth += 1
        elif sty[j] == "}":
            depth -= 1
            if depth == 0: break
        j += 1
    print("  RM block:", " ".join(sty[start:j+1].split())[:400], "\n")

# 4. what feeds L2329 (data.points) — find the enclosing fetch
i = app.find("data.points")
print("== context before L2329 data.points ==")
seg = app[max(0, i-2200):i+200]
# find nearest fetch
for fm in re.finditer(r"await api\(|fetch\(`[^`]+`|/api/(\w[\w/]*)", seg):
    print("   data source hint:", fm.group(0)[:80])

# 5. v63->v67 all hunks (compact)
v63 = open(os.path.expanduser("~/cahl-dashboard/qa/jury_r8/app.js"), "r", errors="replace").read()
l63 = v63.split("\n"); l67 = app.split("\n")
sm = difflib.SequenceMatcher(None, l63, l67, autojunk=False)
print("\n== v63->v67 app.js hunks ==")
for tag, i1, i2, j1, j2 in [o for o in sm.get_opcodes() if o[0] != "equal"]:
    print(f"  {tag} v63[{i1+1}:{i2}] -> v67[{j1+1}:{j2}]  ({i2-i1}->{j2-j1} lines)")
    for l in l67[j1:j2][:2]:
        print("     +", l.strip()[:150])
