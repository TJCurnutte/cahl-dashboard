#!/usr/bin/env python3
"""R10-3/5 part 2: v67->v70 diffs, material census, contrast math, JS census, API probes."""
import re, difflib, subprocess, json, time, gzip
from collections import Counter

R10 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10"
R9 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r9"

style = open(f"{R10}/deployed/css_style.css", encoding="utf-8", errors="replace").read()
landing = open(f"{R10}/deployed/css_landing.css", encoding="utf-8", errors="replace").read()
app = open(f"{R10}/deployed/js_app.js", encoding="utf-8", errors="replace").read()
idx = open(f"{R10}/index.html", encoding="utf-8", errors="replace").read()
style67 = open(f"{R9}/style_v67.css", encoding="utf-8", errors="replace").read()
landing67 = open(f"{R9}/landing_v67.css", encoding="utf-8", errors="replace").read()
app67 = open(f"{R9}/app_v67.js", encoding="utf-8", errors="replace").read()

print("=== v67 -> v70 unified diffs (unified, context 0) ===")
for name, a, b in [("landing.css", landing67, landing), ("style.css", style67, style), ("app.js", app67, app)]:
    d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0))
    print(f"\n--- {name}: {len([l for l in d if l.startswith('+') and not l.startswith('+++')])} added / "
          f"{len([l for l in d if l.startswith('-') and not l.startswith('---')])} removed ---")
    for l in d[:80]:
        print(l[:200])

print("\n=== material census v70 ===")
import re as _re
for name, css in [("style.css", style), ("landing.css", landing)]:
    mh44 = len(_re.findall(r"min-height:\s*44px", css))
    print(f"{name}: backdrop-filter={css.count('backdrop-filter')}, "
          f"keyframes={css.count('@keyframes')}, "
          f"prefers-reduced-motion={css.count('prefers-reduced-motion')}, "
          f"focus-visible={css.count('focus-visible')}, "
          f"tnum={len(_re.findall('font-variant-numeric|tabular-nums', css))}, "
          f"zebra nth-child={css.count('nth-child')}, "
          f"text-shadow={css.count('text-shadow')}, "
          f"box-shadow={css.count('box-shadow')}, "
          f"min-height:44={mh44}, "
          f"transition={css.count('transition:')}")
# dashboard style.css font-size census
pat_px = r"font-size:\s*([\d.]+)px"
csz = Counter(re.findall(pat_px, style))
print(f"style.css px font-size census: {sorted(csz.items(), key=lambda x: float(x[0]))}")
sub13 = {k: v for k, v in csz.items() if float(k) < 13}
print(f"sub-13px in dashboard: {sub13 if sub13 else 'NONE'}")
# keyframes list + RM coverage of animations
kf = re.findall(r"@keyframes\s+([\w-]+)", style) + re.findall(r"@keyframes\s+([\w-]+)", landing)
print(f"keyframes v70: {kf}")
# blur sites
for name, css in [("style", style), ("landing", landing)]:
    for m in re.finditer(r"backdrop-filter[^;]+;", css):
        line = css.count("\n", 0, m.start()) + 1
        ctx = m.group(0)
        print(f"{name}.css L{line}: {ctx}")

print("\n=== contrast: union-hover #2b71c4 white-text on #1f6cb8 (hover state) ===")
def lum(hexs):
    r, g, b = (int(hexs[i:i+2], 16)/255 for i in (0, 2, 4))
    def f(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126*r + 0.7152*g + 0.0722*b
def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
pairs = [("hover white on #2b71c4", "ffffff", "2b71c4"),
         ("idle white on #1f6cb8", "ffffff", "1f6cb8"),
         ("dark accent #ef3d54 on #070b12 bg", "ef3d54", "070b12"),
         ("dark accent #ef3d54 on panel", "ef3d54", "0d1520"),
         ("sponsor gold #b8925e dark panel", "b8925e", "0d1520"),
         ("sponsor gold #7a5c2e light panel", "7a5c2e", "ffffff"),
         ("rink-head #4a9ae6 on dark panel", "4a9ae6", "0d1520"),
         ("faint #7d92ad dark bg", "7d92ad", "070b12"),
         ("faint light #5d6b80 light bg", "5d6b80", "ffffff")]
for label, fg, bg in pairs:
    print(f"{label}: {cr(fg, bg):.2f}:1")

print("\n=== landing #ffffff context ===")
for m in re.finditer(r"#ffffff", landing):
    line = landing.count("\n", 0, m.start()) + 1
    print(f"landing L{line}: {landing[max(0,m.start()-80):m.start()+60].strip()[:160]}")

print("\n=== app.js census v70 ===")
n_inline = app.count('style="')
n_esc = len(re.findall(r"esc\(", app))
n_fs_js = len(re.findall(r"font-size:\s*[\d.]+px", app))
print(f"inline style= attrs: {n_inline}")
print(f"esc( uses: {n_esc}")
print(f"font-size literals in JS: {n_fs_js} {'(NONE)' if n_fs_js == 0 else ''}")
av = re.findall(r"APP_VERSION\s*=\s*[\"']?(\d+)", app)
print(f"APP_VERSION: {av}")
print(f"upright/crown refs: lockup={app.count('upright-lockup')}, crown={app.lower().count('crown')}")

print("\n=== index.html checks ===")
print(f"?v=70 refs: {idx.count('v=70')}")
fg = re.findall(r"fonts.googleapis[^\"']+", idx)
print(f"fonts link: {fg}")
print(f"preconnect: {idx.count('preconnect')}")

print("\n=== API probes ===")
def probe(path, label):
    t0 = time.time()
    try:
        out = subprocess.run(["curl", "-s", "-o", "/tmp/r10_probe.out", "-w",
                              "%{http_code} %{size_download} %{time_total} %{header_json}",
                              f"https://cahl.neural-forge.io{path}"],
                             capture_output=True, text=True, timeout=90)
        w = out.stdout.split()
        hdrs = json.loads(w[3]) if len(w) > 3 else {}
        enc = hdrs.get("content-encoding", ["?"])
        print(f"{label}: HTTP {w[0]}, {int(w[1])/1e6:.2f} MB, {float(w[2]):.2f}s, content-encoding={enc}")
        return open("/tmp/r10_probe.out", "rb").read()
    except Exception as e:
        print(f"{label}: FAILED {e}")
        return b""

b = probe("/api/today", "/api/today")
if b:
    try:
        j = json.loads(b)
        games = j.get("games", j)
        print(f"  today: {len(games) if isinstance(games, list) else 'dict'} entries; "
              f"bye/team-blue refs: {len(re.findall(r'bye week|team blue|team red', b.decode(errors='replace'), re.I))}")
    except Exception as e:
        print(f"  today parse: {e}")
b2 = probe("/api/players", "/api/players (single-shot, labeled)")
if b2:
    try:
        j = json.loads(b2)
        players = j.get("players", j if isinstance(j, list) else [])
        print(f"  players: {len(players)} entries; keys sample: {list(players[0].keys())[:8] if players else 'n/a'}")
        print(f"  from_supabase flag: {j.get('from_supabase', 'absent') if isinstance(j, dict) else 'n/a'}")
    except Exception as e:
        print(f"  players parse: {e}; first 200B: {b2[:200]}")
probe("/api/version", "/api/version")
