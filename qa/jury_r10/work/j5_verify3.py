#!/usr/bin/env python3
"""R10 juror5 part 3: static-path asset fetch, live API payload analysis, dead-team probe, WCAG."""
import json, time, urllib.request, gzip, hashlib, re, os

BASE = "https://cahl.neural-forge.io"
J5 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/work/j5"
D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"

def fetch(path, timeout=59, out=None):
    t0 = time.time()
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            wire = len(raw)
            if r.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            dt = time.time() - t0
            if out and raw:
                open(os.path.join(J5, out), "wb").write(raw)
            return raw, dt, r.status, wire
    except Exception as e:
        return None, time.time() - t0, str(e), 0

print("=== A. exact ?v=70 static URLs (the ones the shell references) ===")
for path, cmp_file in [("/static/js/app.js?v=70", "app.js"),
                       ("/static/css/style.css?v=70", "style.css"),
                       ("/static/css/landing.css?v=70", "landing.css")]:
    raw, dt, st, wire = fetch(path, 40)
    if raw:
        h = hashlib.sha256(raw).hexdigest()[:12]
        ref = hashlib.sha256(open(D + cmp_file, "rb").read()).hexdigest()[:12]
        print(f"{path}  {dt:.2f}s status=200 bytes={len(raw)} sha={h} matches_plain={h == ref}")
    else:
        print(f"{path}  {dt:.2f}s status={st}")

print("=== B. dead-team self-heal live probe ===")
raw, dt, st, wire = fetch("/api/team/E25EA9F0-0F26-BD6A-F23ECD21D7F432C8", 40)
print(f"/api/team/<dead-id>  {dt:.2f}s status={st} body={raw[:200] if raw else None}")

print("=== C. leagues + league payload ===")
raw, dt, st, wire = fetch("/api/leagues", 40, "api_leagues.json")
print(f"/api/leagues  {dt:.2f}s status={st} bytes={len(raw) if raw else 0}")
leagues = []
if raw:
    try:
        data = json.loads(raw)
        leagues = data if isinstance(data, list) else data.get("leagues", [])
        print(f"  n_leagues={len(leagues)} sample={[l.get('name') if isinstance(l, dict) else l for l in leagues[:6]]}")
    except Exception as e:
        print("  parse err", e)
if leagues:
    nm = leagues[0].get("name") if isinstance(leagues[0], dict) else leagues[0]
    from urllib.parse import quote
    raw, dt, st, wire = fetch("/api/league/" + quote(str(nm)), 45, "api_league.json")
    print(f"/api/league/{nm}  {dt:.2f}s status={st} bytes={len(raw) if raw else 0}")
    if raw:
        try:
            ld = json.loads(raw)
            lids = ld.get("leaders", {})
            for k, rows in (lids.items() if isinstance(lids, dict) else []):
                if isinstance(rows, list):
                    ids = [r.get("player_id") for r in rows]
                    print(f"  leaders.{k}: n={len(rows)} player_id present={sum(1 for x in ids if x)}/{len(rows)}")
        except Exception as e:
            print("  parse err", e)

print("=== D. saved payload analysis ===")
t = json.load(open(J5 + "/api_today.json"))
games = t.get("games", t if isinstance(t, list) else [])
print(f"/api/today: type={type(t).__name__} n_games={len(games) if isinstance(games, list) else 'n/a'}")
s = json.dumps(t)
for tok in ["placeholder", "TBD", "null, null", "undefined"]:
    print(f"  contains '{tok}': {tok in s}")
tm = json.load(open(J5 + "/api_teams.json"))
tl = tm if isinstance(tm, list) else tm.get("teams", [])
names = [x.get("name", "") for x in tl if isinstance(x, dict)]
print(f"/api/teams: n={len(tl)}")
for bad in ["Bye Week", "Team Blue", "Team Red"]:
    hits = [n for n in names if bad.lower() in n.lower()]
    print(f"  '{bad}' present: {len(hits)} {hits[:2]}")
ld = json.load(open(J5 + "/api_leaders.json"))
def walk_leaders(d):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and ("player_id" in v[0] or "value" in v[0]):
                out[k] = v
            elif isinstance(v, dict):
                out.update(walk_leaders(v))
    return out
lv = walk_leaders(ld)
for k, rows in lv.items():
    ids = [r.get("player_id") for r in rows]
    print(f"/api/leaders {k}: n={len(rows)} player_id present={sum(1 for x in ids if x)}/{len(rows)}")
p = json.load(open(J5 + "/api_players.json"))
pl = p if isinstance(p, list) else p.get("players", [])
print(f"/api/players: type={type(p).__name__} n={len(pl) if isinstance(pl, list) else '?'} top_keys={list(p.keys())[:8] if isinstance(p, dict) else 'list'}")
if isinstance(pl, list) and pl:
    print(f"  sample keys: {list(pl[0].keys())[:12]}")

print("=== E. WCAG on changed/new tokens ===")
def lum(hexc):
    hexc = hexc.lstrip('#')
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
print(f"  white on --union-hover #2b71c4 (changed): {cr('#ffffff', '#2b71c4'):.2f}:1")
print(f"  white on --union-cta #1f6cb8: {cr('#ffffff', '#1f6cb8'):.2f}:1")
print(f"  sponsor-gold #b8925e on panel dark (approx #10151c): {cr('#b8925e', '#10151c'):.2f}:1")
print(f"  light-theme gold #7a5c2e on #f5f2ec: {cr('#7a5c2e', '#f5f2ec'):.2f}:1")

print("=== F. OG/meta from shell ===")
sh = open(D + "index.html", encoding="utf-8").read()
for m in re.finditer(r'<meta[^>]*(?:og:image|og:title|description)[^>]*>', sh):
    print(" ", m.group(0)[:160])

print("=== G. RM coverage: keyframes vs RM blocks ===")
sc = open(D + "style.css", encoding="utf-8").read()
lines = sc.splitlines()
kf = re.findall(r"@keyframes\s+([\w-]+)", sc)
rm_ranges = []
for i, l in enumerate(lines):
    if "prefers-reduced-motion" in l:
        depth = 0; start = i; j = i
        while j < len(lines):
            depth += lines[j].count("{") - lines[j].count("}")
            if depth == 0 and j > i: break
            j += 1
        rm_ranges.append((start + 1, j + 1))
print(f"  keyframes: {kf}")
print(f"  RM block line-ranges: {rm_ranges}")
covered = set()
for a, b in rm_ranges:
    block = "\n".join(lines[a-1:b])
    for k in kf:
        if k in block: covered.add(k)
print(f"  keyframes named inside RM blocks: {sorted(covered)}")
print(f"  NOT named in any RM block: {sorted(set(kf) - covered)}")
