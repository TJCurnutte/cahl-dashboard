#!/usr/bin/env python3
"""R8 j2 probe 3: landing.css read, table-overflow selector, focus parity, floors, contrast."""
import re, os

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(os.path.join(OUT, "style_v63.css"), encoding="utf-8").read()
cssl = css.split("\n")
js = open(os.path.join(OUT, "app_v63.js"), encoding="utf-8").read()
jsl = js.split("\n")
land = open(os.path.join(OUT, "landing_v63.css"), encoding="utf-8").read()
landl = land.split("\n")

print("===== landing.css FULL =====")
for i, l in enumerate(landl):
    print(f"{i+1}| {l}")

print("\n===== style.css L485-515 (table scroll rule) =====")
for i in range(484, 515):
    print(f"{i+1}| {cssl[i]}")

print("\n===== rink-head base L1700-1712 =====")
for i in range(1699, 1712):
    print(f"{i+1}| {cssl[i]}")

# focus-within row parity (R7-3 carry)
print("\n===== focus-within / focus-visible on rows =====")
for i, l in enumerate(cssl):
    if re.search(r"focus-within|focus-visible", l):
        print(f"  L{i+1}: {l.strip()[:150]}")

# media-block tap-floor regression: min-height/width:0 INSIDE any @media block
print("\n===== min-h/w:0 inside @media blocks (regression class) =====")
depth = 0
inmedia = False
medhdr = ""
for i, l in enumerate(cssl):
    opens = l.count("{")
    closes = l.count("}")
    if re.match(r"\s*@media", l):
        inmedia = True
        medhdr = l.strip()
    if inmedia and re.search(r"min-height:\s*0|min-width:\s*0", l):
        print(f"  L{i+1} [{medhdr[:60]}]: {l.strip()[:120]}")
    depth += opens - closes
    if depth <= 0:
        inmedia = False
        depth = 0

# esc() on the R7-5 raw error sites
print("\n===== raw data.error / upstream body interpolation =====")
for i, l in enumerate(jsl):
    if re.search(r"data\.error|e\.message|errorText|responseText", l) and ("innerHTML" in l or "+ '" in l or "`" in l or "html +=" in l or "html =" in l):
        print(f"  L{i+1}: {l.strip()[:170]}")

# sponsor strip position in todayPageHtml
print("\n===== sponsor strip context (app.js L1225-1245) =====")
for i in range(1224, 1245):
    print(f"  L{i+1}: {jsl[i].strip()[:160]}")

# contrast math
def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126*r + 0.7152*g + 0.0722*b
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la+0.05)/(lb+0.05)
print("\n===== WCAG calcs =====")
for name, fg, bg in [
    ("white on accent #ef3d54 (gate CTA?)", "#ffffff", "#ef3d54"),
    ("#070b12 text on accent #ef3d54", "#070b12", "#ef3d54"),
    ("sponsor gold #b8925e on panel #0d1522", "#b8925e", "#0d1522"),
    ("sponsor gold #b8925e on panel-2 #131b2b", "#b8925e", "#131b2b"),
    ("gate-sub #8494ab on gate-card", "#8494ab", "#0d1522"),
    ("pill-count #8494ab@.7 on panel-2 approx", "#a4aebd", "#131b2b"),
    ("rink-head dark (check below)", "#4a9ae6", "#0d1522"),
]:
    print(f"  {name}: {ratio(fg, bg):.2f}:1")

# timed /api/players single shot (cold-index copy context)
import time, urllib.request, json
t0 = time.time()
try:
    with urllib.request.urlopen("https://cahl.neural-forge.io/api/players", timeout=45) as r:
        n = len(r.read())
    print(f"\n/api/players: {time.time()-t0:.1f}s, {n} bytes")
except Exception as e:
    print(f"\n/api/players FAILED after {time.time()-t0:.1f}s: {e!r}")
