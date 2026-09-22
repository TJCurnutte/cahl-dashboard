#!/usr/bin/env python3
"""R10 juror5 part 4: RM block bodies, roster click delegation, 502 path, leagues, dead-team retry."""
import re, json, time, urllib.request, gzip, os
from urllib.parse import quote

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
J5 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/work/j5"
AL = open(D + "app.js", encoding="utf-8", errors="replace").read().splitlines()
SC = open(D + "style.css", encoding="utf-8", errors="replace").read().splitlines()

print("=== RM block contents (style.css) ===")
for a, b in [(1216, 1222), (1296, 1299), (1402, 1406), (1607, 1608)]:
    print(f"--- L{a}-{b} ---")
    for i in range(a - 1, min(b + 1, len(SC))):
        print(f"{i+1}: {SC[i][:160]}")
print("=== landing.css RM block ===")
LC = open(D + "landing.css", encoding="utf-8", errors="replace").read().splitlines()
for i in range(210, 218):
    print(f"{i+1}: {LC[i][:160]}")

print("=== selectPlayerToken def + roster-player delegation ===")
for i, l in enumerate(AL):
    if "function selectPlayerToken" in l or "roster-player" in l and ("addEventListener" in l or "closest" in l or "delegate" in l.lower()):
        for j in range(max(0, i - 2), min(len(AL), i + 8)):
            print(f"{j+1}: {AL[j][:150]}")
        print("   ...")

print("=== all 'roster-player' refs ===")
for i, l in enumerate(AL):
    if "roster-player" in l:
        print(f"  L{i+1}: {l.strip()[:130]}")

print("=== try/finally catch structure around team fetch L1988-2060 ===")
for i in range(1987, 2062):
    print(f"{i+1}: {AL[i][:140]}")

print("=== 'partial' handling in app.js ===")
for i, l in enumerate(AL):
    if re.search(r"\bpartial\b", l):
        print(f"  L{i+1}: {l.strip()[:130]}")

print("=== players payload 'partial' value ===")
p = json.load(open(J5 + "/api_players.json"))
print("partial =", p.get("partial"), "| n players =", len(p.get("players", [])))

print("=== leagues endpoint ===")
for i, l in enumerate(AL):
    if re.search(r"fetch\(['\`]/api/league|/api/leagues|api\(['\`]/api/league", l):
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== dead-team probe retry x2 ===")
def fetch(path, timeout=45):
    t0 = time.time()
    req = urllib.request.Request("https://cahl.neural-forge.io" + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) JuryR10QAProbe", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            return raw, time.time() - t0, r.status
    except Exception as e:
        return None, time.time() - t0, str(e)
for attempt in (1, 2):
    raw, dt, st = fetch("/api/team/E25EA9F0-0F26-BD6A-F23ECD21D7F432C8")
    print(f"  attempt {attempt}: {dt:.2f}s status={st} body={(raw[:160] if raw else None)!r}")

print("=== league probe with real league name ===")
raw, dt, st = fetch("/api/league/" + quote("Sunday C West"), 50)
print(f"  /api/league/Sunday C West  {dt:.2f}s status={st} bytes={len(raw) if raw else 0}")
if raw:
    try:
        ld = json.loads(raw)
        lids = ld.get("leaders", {}) if isinstance(ld, dict) else {}
        for k, rows in lids.items():
            if isinstance(rows, list):
                ids = [r.get("player_id") for r in rows]
                print(f"  leaders.{k}: n={len(rows)} player_id present={sum(1 for x in ids if x)}/{len(rows)}")
        st_rows = ld.get("standings", []) if isinstance(ld, dict) else []
        print(f"  standings rows: {len(st_rows)}")
    except Exception as e:
        print("  parse err", e)
