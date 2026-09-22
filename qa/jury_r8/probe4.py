#!/usr/bin/env python3
"""R8 j2 probe 4: tokens (union-deep), fonts href, team watchdog ctx, box-sizing, cold msg ctx."""
import re, os

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(os.path.join(OUT, "style_v63.css"), encoding="utf-8").read()
cssl = css.split("\n")
js = open(os.path.join(OUT, "app_v63.js"), encoding="utf-8").read()
jsl = js.split("\n")
idx = open(os.path.join(OUT, "index_v63.html"), encoding="utf-8").read()

print("== union/union-deep tokens ==")
for i, l in enumerate(cssl[:60]):
    if re.search(r"--union", l):
        print(f"  L{i+1}: {l.strip()[:120]}")

print("\n== fonts href in index.html ==")
for l in idx.split("\n"):
    if "fonts.googleapis" in l or "family=" in l:
        print("  ", l.strip()[:220])

print("\n== box-sizing reset ==")
for i, l in enumerate(cssl[:80]):
    if "box-sizing" in l:
        print(f"  L{i+1}: {l.strip()[:100]}")

print("\n== team inline watchdog context L1975-2000 ==")
for i in range(1974, 2000):
    print(f"  L{i+1}: {jsl[i].strip()[:150]}")

print("\n== shared watchdog full L1433-1460 ==")
for i in range(1432, 1460):
    print(f"  L{i+1}: {jsl[i].strip()[:150]}")

print("\n== cold-index message context L520-540 ==")
for i in range(519, 540):
    print(f"  L{i+1}: {jsl[i].strip()[:150]}")

print("\n== gate focus management in app.js L10-25 ==")
for i in range(9, 26):
    print(f"  L{i+1}: {jsl[i].strip()[:150]}")

# WCAG: white on gate CTA #1f6cb8; and is #1f6cb8 == --union-deep?
def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126*r + 0.7152*g + 0.0722*b
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la+0.05)/(lb+0.05)
print("\n== WCAG: white on #1f6cb8:", round(ratio("#ffffff", "#1f6cb8"), 2), ":1")

# count distinct font-size values including var() uses for the record
vars_used = re.findall(r"font-size:\s*var\((--[\w-]+)\)", css)
from collections import Counter
print("font-size: var() uses:", Counter(vars_used))
