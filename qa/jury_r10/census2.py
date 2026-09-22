#!/usr/bin/env python3
"""R10 final census batch: esc, RM, dataStamp, sponsor, media-block floors, literal deltas v67 vs v70."""
import re, subprocess, urllib.request

D70 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed"
D67 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/deployed"
app = open(f"{D70}/app.js", encoding="utf-8", errors="replace").read()
css = open(f"{D70}/style.css", encoding="utf-8", errors="replace").read()
lcss = open(f"{D70}/landing.css", encoding="utf-8", errors="replace").read()
css67 = open(f"{D67}/style.css", encoding="utf-8", errors="replace").read()
lcss67 = open(f"{D67}/landing.css", encoding="utf-8", errors="replace").read()

def count(text, pat):
    return len(re.findall(pat, text))

print("=== esc census (raw unescaped error interpolations) ===")
raw_err = re.findall(r"\$\{(?!esc\()data\.error[^}]*\}", app)
raw_msg = re.findall(r"\$\{(?!esc\()e\.message[^}]*\}", app)
esc_err = app.count("esc(data.error")
esc_msg = app.count("esc(e.message")
print(f"  raw data.error: {len(raw_err)} | esc'd: {esc_err}")
print(f"  raw e.message: {len(raw_msg)} | esc'd: {esc_msg}")

print("\n=== RM (prefers-reduced-motion) blocks in style.css ===")
blocks = re.findall(r"@media \(prefers-reduced-motion[^)]*\)\s*\{", css)
print(f"  RM blocks: {len(blocks)}")
for m in re.finditer(r"@media \(prefers-reduced-motion[^)]*\)\s*\{", css):
    start = m.end()
    seg = css[start:start+400]
    print("  ->", seg[:260].replace("\n", " ")[:250])
print("  spinner in RM?:", "spinner" in css[css.find("prefers-reduced-motion"):css.find("prefers-reduced-motion")+2000])

print("\n=== dataStamp / paintStamp ===")
for i, ln in enumerate(app.split("\n"), 1):
    if "paintStamp" in ln or "setInterval(paintStamp" in ln:
        print(f"  L{i}: {ln.strip()[:100]}")

print("\n=== sponsor marks ===")
print("  crown refs in app.js:", app.count("crown"))
print("  lockup refs in app.js:", app.count("upright-lockup"))
# does the asset exist?
req = urllib.request.Request("https://cahl.neural-forge.io/static/img/upright-lockup.png", method="HEAD")
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"  HEAD upright-lockup.png: {r.status} {r.headers.get('Content-Length')}B")
except Exception as e:
    print(f"  HEAD upright-lockup.png: {e}")

print("\n=== min-height/width:0 inside @media blocks (release gate) ===")
for name, text in (("style.css", css), ("landing.css", lcss)):
    hits = []
    for m in re.finditer(r"@media[^{]*\{", text):
        seg_start = m.start()
        depth = 1
        i = m.end()
        while i < len(text) and depth:
            if text[i] == "{": depth += 1
            elif text[i] == "}": depth -= 1
            i += 1
        seg = text[m.end():i-1]
        for j, ln in enumerate(seg.split("\n"), 1):
            if re.search(r"min-(height|width):\s*0", ln):
                hits.append((text[:seg_start].count("\n")+1+j, ln.strip()[:90]))
    print(f"  {name}: {len(hits)} min-h/w:0 in media blocks")
    for h in hits:
        print(f"    L{h[0]}: {h[1]}")

print("\n=== font-size literal deltas v67 -> v70 ===")
for name, t67, t70 in (("style.css", css67, css), ("landing.css", lcss67, lcss)):
    c67 = len(re.findall(r"font-size:\s*\d", t67))
    c70 = len(re.findall(r"font-size:\s*\d", t70))
    # unique size values
    s67 = sorted(set(re.findall(r"font-size:\s*([\d.]+)px", t67)), key=float)
    s70 = sorted(set(re.findall(r"font-size:\s*([\d.]+)px", t70)), key=float)
    print(f"  {name}: v67 {c67} lines / sizes {s67}")
    print(f"  {name}: v70 {c70} lines / sizes {s70}")

print("\n=== off-token hex literals in landing.css (fallbacks) ===")
hexes = re.findall(r"#[0-9a-fA-F]{3,6}\b", lcss)
from collections import Counter
print(" ", Counter(hexes))

print("\n=== CTA hover contrast light theme ===")
def lum(hexv):
    h = hexv.lstrip('#'); r,g,b = (int(h[i:i+2],16)/255 for i in (0,2,4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b = f(r),f(g),f(b); return 0.2126*r+0.7152*g+0.0722*b
def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    if l1 < l2: l1, l2 = l2, l1
    return (l1+0.05)/(l2+0.05)
print(f"  white on --union-hover-deep #0d3a73 (light hover): {ratio('#ffffff', '#0d3a73'):.2f}:1")
print(f"  white on --union-hover #2b71c4 (dark hover): {ratio('#ffffff', '#2b71c4'):.2f}:1")
