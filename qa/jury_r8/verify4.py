#!/usr/bin/env python3
"""Jury R8 J5 part 4: css-side v63 claims + payload integrity + players timing."""
import re, json, pathlib, time, urllib.request

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")

def show(label, text, pat, maxhits=10, flags=0):
    hits = [(text.count("\n", 0, m.start()) + 1, text[max(0, m.start()-40):m.start()+120].replace("\n", " ⏎ ")) for m in re.finditer(pat, text, flags)]
    print(f"\n=== {label} ({len(hits)}) ===")
    for ln, s in hits[:maxhits]:
        print(f"  L{ln}: …{s.strip()[:150]}")

show("focus-within (css)", css, r"focus-within")
show("tonight-strip responsive (css)", css, r"tonight-strip")
show("sticky/scroll context (css)", css, r"scroll-context|sticky-header|data-scrolled|header.*sticky|sticky.*head", maxhits=12)
show("small-button 44px (css)", css, r"small.*44|44px", maxhits=12)
show("section-h (css)", css, r"section-h")
show("dataStamp impl (js)", js, r"dataStamp", maxhits=6)
show("cold copy (js)", js, r"cold|warming|still loading", maxhits=8, flags=re.I)
show("gate code (js L8-30)", js, r"landingGate|gate-hidden|gateEnter", maxhits=10)

# manifest + og image
man = json.loads((Q / "manifest.json").read_text())
print("\nmanifest:", json.dumps(man, indent=1)[:700])

t0 = time.time()
try:
    with urllib.request.urlopen("https://cahl.neural-forge.io/static/img/cahl-icon-512.png", timeout=30) as r:
        b = r.read()
    print("og:image cahl-icon-512.png:", r.status, len(b), "B")
    (Q / "cahl-icon-512.png").write_bytes(b)
except Exception as e:
    print("og:image ERR:", e)
print("og fetch %.2fs" % (time.time() - t0))

# /api/players timing (worst endpoint)
t0 = time.time()
try:
    with urllib.request.urlopen("https://cahl.neural-forge.io/api/players", timeout=60) as r:
        b = r.read()
    print("/api/players:", r.status, f"{len(b):,}B", f"{time.time()-t0:.2f}s")
    (Q / "api_players.json").write_bytes(b)
except Exception as e:
    print("/api/players ERR after %.1fs:" % (time.time() - t0), e)

# payload integrity scan
print("\n=== payload integrity scan ===")
bad_tokens = ["Bye Week", "Team Blue", "Team Red", "TBD", "undefined", "NaN", "null"]
for name in ("api_today.json", "api_today_scores.json", "api_teams.json", "api_leaders.json", "api_league.json", "api_team.json"):
    raw = (Q / name).read_text(encoding="utf-8", errors="replace")
    hits = {t: raw.count(t) for t in bad_tokens if t in raw}
    print(f"  {name}: {hits if hits else 'clean'}")

today = json.loads((Q / "api_today.json").read_text())
games = today.get("today") or today.get("games") or []
print("today games:", len(games))
for g in games[:6]:
    print("  ", {k: g.get(k) for k in ("time", "home", "away", "facility", "league", "status", "score") if k in g})

scores = json.loads((Q / "api_today_scores.json").read_text())
print("today/scores keys:", list(scores.keys())[:8])
gs = scores.get("games") or []
print("scores games:", len(gs))
for g in gs[:4]:
    print("  ", json.dumps(g)[:220])
