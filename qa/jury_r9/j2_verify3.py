#!/usr/bin/env python3
"""Jury R9 juror2 — part 3: gate logic, ledger re-greps, contrast, API timing."""
import os, re, json, time, urllib.request, ssl, math

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
sty = open(os.path.join(J2, "style.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()

def show(pat, txt, label, ctx=150, flags=0, cap=12):
    hits = [(txt[:m.start()].count("\n")+1, m.group(0)[:ctx]) for m in re.finditer(pat, txt, flags)]
    print(f"[{label}] {len(hits)} hits")
    for ln, s in hits[:cap]:
        print(f"  L{ln}: {s!r}")
    return hits

print("== K. gate logic in app.js ==")
show(r"[^\n]*(?:landingGate|gateEnter|gate-hidden|cahl-entered)[^\n]*", app, "gate")
show(r"[^\n]*#app\b[^\n]*hidden[^\n]*|app\.hidden[^\n]*|getElementById\('app'\)[^\n]*", app, "app-toggle", cap=8)

print("\n== L. standing ledger ==")
show(r"upcoming\.concat\([^\)]*\)", app, "concat-finals")
show(r"[^\n]*tonight-strip[^\n]*", sty, "tonight-strip-css")
show(r"[^\n]*prefers-reduced-motion[^\n]*\{", sty, "rm-blocks-style")
lnd = open(os.path.join(J2, "landing.css"), errors="replace").read()
show(r"prefers-reduced-motion", lnd, "rm-landing")
show(r"[^\n]*animateNumbers[^\n]*", app, "countup")
show(r"[^\n]*matchMedia[^\n]*", app, "matchmedia", cap=8)
show(r"[^\n]*dataStamp[^\n]*", app, "datastamp", cap=6)
show(r"[^\n]*sponsor-strip[^\n]*", app, "sponsor-emit", cap=6)
show(r"style=\"margin-top:[^\"]*\"", app, "inline-mt")
show(r"[^\n]*:checked[^\n]*", sty, "checked-css", cap=6)

print("\n== M. release-gate grep: min-h/w:0 inside max-width media ==")
in_media = False; depth = 0
for i, line in enumerate(sty.split("\n"), 1):
    if re.search(r"@media[^{]*max-width", line): in_media = True
    if in_media and re.search(r"min-height:\s*0|min-width:\s*0\b(?!:)", line) and "min-width:0;" in line.replace(" ", ""):
        print(f"  L{i}: {line.strip()[:120]!r}")
    if in_media and line.strip() == "}" and depth == 0:
        pass
# simpler: report all min-height:0 / min-width:0 lines with the nearest preceding @media
cur_media = "?"
for i, line in enumerate(sty.split("\n"), 1):
    m = re.search(r"@media([^{]*)\{", line)
    if m: cur_media = m.group(1).strip()
    if re.search(r"min-(height|width):\s*0", line):
        print(f"  L{i} (media={cur_media}): {line.strip()[:110]!r}")

print("\n== N. hex census: off-token literals in style.css ==")
hexes = {}
for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", sty):
    h = m.group(0).lower()
    hexes[h] = hexes.get(h, 0) + 1
known = {"#002654", "#ce1126", "#a2aaad", "#ffffff", "#070b12", "#ef3d54", "#2a7fd4", "#4a9ae6",
         "#1f6cb8", "#b8925e", "#7a5c2e", "#7d92ad", "#5d6b80", "#e8253c", "#3a8fe0"}
odd = {h: c for h, c in hexes.items() if h not in known and len(h) == 7}
print("  total distinct 6-digit:", len([h for h in hexes if len(h) == 7]))
print("  non-recognized:", dict(sorted(odd.items(), key=lambda x: -x[1])[:14]))

print("\n== O. contrast math ==")
def lum(hx):
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126*r + 0.7152*g + 0.0722*b
def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1+0.05)/(l2+0.05)
# panel/inset values from style.css tokens
toks = dict(re.findall(r"(--panel\d?|--panel-2|--panel-3|--inset|--bg|--muted|--faint|--text-2|--border|--border-soft|--union|--accent)\s*:\s*(#[0-9a-fA-F]{6})", sty))
print("  dark tokens:", toks)
light = dict(re.findall(r"(--panel\d?|--panel-2|--panel-3|--inset|--bg|--muted|--faint|--sponsor-gold)\s*:\s*(#[0-9a-fA-F]{6})", sty[sty.find('[data-theme="light"]') if '[data-theme="light"]' in sty else 0:]))
print("  light tokens (first block):", dict(list(light.items())[:10]))
print(f"  white on #1f6cb8: {cr('#ffffff', '#1f6cb8'):.2f}")
print(f"  #b8925e on --inset {toks.get('--inset')}: {cr('#b8925e', toks.get('--inset', '#0d1420')):.2f}")
print(f"  #b8925e on --panel {toks.get('--panel')}: {cr('#b8925e', toks.get('--panel', '#0c1220')):.2f}")
print(f"  #7a5c2e on light --inset: {cr('#7a5c2e', light.get('--inset', '#e8eef5')):.2f}")
print(f"  --muted {toks.get('--muted')} on --panel-3 {toks.get('--panel-3')}: {cr(toks.get('--muted', '#8fa3bd'), toks.get('--panel-3', '#111a28')):.2f}")
print(f"  --muted on --panel: {cr(toks.get('--muted', '#8fa3bd'), toks.get('--panel', '#0c1220')):.2f}")
print(f"  --faint {toks.get('--faint')} on --bg {toks.get('--bg')}: {cr(toks.get('--faint', '#7d92ad'), toks.get('--bg', '#070b12')):.2f}")
print(f"  accent #ef3d54 on --panel: {cr('#ef3d54', toks.get('--panel', '#0c1220')):.2f}")
print(f"  accent on --bg: {cr('#ef3d54', toks.get('--bg', '#070b12')):.2f}")

print("\n== P. API timing (single-shot, fresh) ==")
ctx2 = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
def timed(path, tmo=55):
    req = urllib.request.Request("https://cahl.neural-forge.io" + path, headers=UA)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=tmo, context=ctx2) as r:
            data = r.read()
            return time.time()-t0, len(data), r.status
    except Exception as e:
        return time.time()-t0, 0, str(e)[:60]
d1, s1, st1 = timed("/api/today")
print(f"  /api/today: {d1:.2f}s, {s1}B, {st1}")
try:
    j = json.loads(open(os.path.join(J2, "..", "j2_today.json")).read()) if False else None
except Exception:
    pass
d2, s2, st2 = timed("/api/players")
print(f"  /api/players: {d2:.2f}s, {s2}B ({s2/1e6:.2f}MB), {st2}")
open(os.path.join(J2, "j2_today.json"), "wb").write(json.dumps({"today_s": d1, "players_s": d2, "players_B": s2}).encode())
# today payload summary
d3, s3, st3 = timed("/api/today")
try:
    tj = json.loads(open("/dev/null").read())
except Exception:
    pass
print("  (today payload fetched twice for freshness; first size above)")
