#!/usr/bin/env python3
"""R8 j2 probe 2: landing.css fetch, sponsor strip, watchdog, census, contrast."""
import re, os, json, urllib.request, math

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"

# --- fetch landing.css + confirm main asset hrefs in index ---
idx = open(os.path.join(OUT, "index_v63.html"), encoding="utf-8").read()
for m in re.finditer(r'(href|src)="([^"]+)"', idx):
    v = m.group(2)
    if any(k in v for k in (".css", ".js", "favicon", "og-", "apple")):
        print("ASSET:", v)

req = urllib.request.Request("https://cahl.neural-forge.io/static/css/landing.css?v=63",
                             headers={"User-Agent": "cahl-jury-r8-j2"})
land = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
open(os.path.join(OUT, "landing_v63.css"), "w").write(land)
print("\nlanding.css bytes:", len(land), "lines:", land.count("\n") + 1)

css = open(os.path.join(OUT, "style_v63.css"), encoding="utf-8").read()
js = open(os.path.join(OUT, "app_v63.js"), encoding="utf-8").read()
cssl, jsl = css.split("\n"), js.split("\n")

def show(lines, pat, label, n=14, ctx=0):
    rx = re.compile(pat)
    hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if rx.search(l)]
    print(f"\n== {label} == ({len(hits)} hits)")
    for ln, l in hits[:n]:
        print(f"  L{ln}: {l[:160]}")
    return hits

# --- sponsor strip on Today (app.js emitter + css) ---
show(jsl, r"sponsor|upright|Upright", "SPONSOR in app.js", n=16)
show(css.split("\n"), r"\.sponsor", "SPONSOR css in style.css", n=10)
show(land.split("\n"), r"\.sponsor|gate-", "GATE/SPONSOR css in landing.css", n=40)

# --- landing gate session-skip logic ---
show(jsl, r"landingGate|gateEnter|sessionStorage", "GATE logic in app.js", n=20)

# --- watchdog timing (R7-4: 20s vs api 30s race -> v63 claims 40s + debounced retry) ---
show(jsl, r"armSkeletonWatchdog|WATCHDOG|40000|40_000|20000|8000", "watchdog timings", n=24)

# --- api() ceiling ---
show(jsl, r"AbortController|setTimeout\(\s*\w*abort|30000|signal:", "api() abort ceiling", n=12)

# --- tonight-strip base + numerals ---
print("\n== .tonight-strip base rule ==")
for i in range(1650, 1668):
    print(f"  L{i+1}: {cssl[i].strip()[:160]}")
show(cssl, r"tonight-num|tonight-kpi|tonight-lab", "tonight numerals", n=12)

# --- font-size census: distinct px values in style.css + landing.css ---
def census(txt, label):
    vals = re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", txt)
    from collections import Counter
    c = Counter(vals)
    print(f"\n== font-size census {label}: {len(c)} distinct sizes ==")
    print("  ", sorted(((float(k), v) for k, v in c.items())))
    small = [k for k in c if float(k) < 9.5]
    print("   sub-9.5px sizes:", small or "NONE")
census(css, "style.css")
census(land, "landing.css")
show(jsl, r"font-size", "font-size literals in app.js", n=6)

# --- rink-head AA fix + pill-count residual + accent ---
show(cssl, r"rink-head", "rink-head color", n=8)
show(cssl, r"pill-count", "pill-count", n=6)
show(cssl, r"--accent:\s*#|--faint:\s*#|--muted:\s*#", "core tokens", n=10)

# --- hasOpp guard on team recent_result ---
show(jsl, r"recent_result|hasOpp", "recent_result hasOpp guard", n=12)

# --- overflow-x rules: who is the table scroll container? ---
show(cssl, r"overflow(-x|-y)?\s*:", "all overflow rules", n=30)

# --- contrast helper ---
def lum(hexc):
    hexc = hexc.lstrip("#")
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
print("\n== WCAG ==")
for name, fg, bg in [("accent #ef3d54 on #070b12", "#ef3d54", "#070b12"),
                     ("accent #ef3d54 on panel #0d1522", "#ef3d54", "#0d1522"),
                     ("rink-head #4a9ae6 on panel #0d1522", "#4a9ae6", "#0d1522"),
                     ("rink-head #4a9ae6 on bg #070b12", "#4a9ae6", "#070b12"),
                     ("faint on panel", "#7d92ad", "#0d1522")]:
    print(f"  {name}: {ratio(fg, bg):.2f}:1")

# --- today payload shape ---
t = json.load(open(os.path.join(OUT, "today_v63.json")))
games = t.get("games") or t.get("today") or []
print("\n== /api/today ==", "keys:", list(t.keys())[:8])
print("   games:", len(games), "| leagues:", len(t.get("leagues", [])))
for g in games[:6]:
    print("   ", g.get("time"), g.get("home"), "vs", g.get("away"), "@", g.get("facility"), "| played:", g.get("played"), "| status:", g.get("status"))
