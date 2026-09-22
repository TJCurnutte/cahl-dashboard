#!/usr/bin/env python3
"""Jury R8 J5: byte-verify R7 fixes + new v63 surfaces in fetched deployed assets."""
import re, json, pathlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")
lcss = (Q / "landing.css").read_text(encoding="utf-8", errors="replace")
root = (Q / "root.html").read_text(encoding="utf-8", errors="replace")

def lines(text):
    return text.split("\n")

def find(text, pat, ctx=0, maxhits=20, flags=0):
    out = []
    ls = lines(text)
    for i, l in enumerate(ls, 1):
        if re.search(pat, l, flags):
            out.append((i, l.strip()[:200]))
            if len(out) >= maxhits:
                break
    return out

def show(title, hits):
    print(f"\n=== {title} ({len(hits)} hits) ===")
    for i, l in hits:
        print(f"  L{i}: {l}")

# ---- R7 fix verification ----
show("FIX1 hasOpp guard (recent_result site)", find(js, r"hasOpp", maxhits=30))
show("recent_result context", find(js, r"recent[_ -]?result", maxhits=15))

print("\n=== FIX2 data.error paint sites (raw vs esc) ===")
for m in re.finditer(r".{0,90}data\.error.{0,90}", js):
    s = m.group(0).replace("\n", "\\n")
    print("  :", s)

print("\n=== FIX3 .section-h ===")
print(" app.js section-h refs:", len(re.findall(r"section-h", js)))
print(" style.css section-h refs:", len(re.findall(r"section-h", css)))
for i, l in find(css, r"section-h", maxhits=8):
    print(f"  css L{i}: {l[:160]}")
print(" inline margin-top:18px remaining:", len(re.findall(r"margin-top:\s*18px", js)))
for i, l in find(js, r"margin-top:\s*18px", maxhits=10):
    print(f"  L{i}: {l[:150]}")

# ---- new v63 claims from the log ----
show("hero-glow-breathe (should be 0 or retired)", find(css, r"hero-glow-breathe|breathe", maxhits=10))
show("rink-head color", find(css, r"rink-head", maxhits=8))
for i, l in find(css, r"#4a9ae6", maxhits=10):
    print(f"  css L{i}: {l[:160]}")
show("sb-card scrim", find(css, r"data-scrim|\.scrim", maxhits=15))
show("sponsor strip in app.js", find(js, r"sponsor|upright", maxhits=15, flags=re.I))
show("gate logic in app.js", find(js, r"landingGate|gateEnter|sessionStorage", maxhits=20))

# ---- standing ledgers ----
print("\n=== ledgers ===")
print(" onclick= in js:", len(re.findall(r"onclick=", js)))
print(" inline style= in js strings:", len(re.findall(r"style=\\?\"", js)))
print(" data-sort sites:", len(re.findall(r"data-sort", js)))
fs = re.findall(r"font-size:\s*([\d.]+)px", css)
from collections import Counter
print(" css literal font-size census:", sorted(Counter(fs).items(), key=lambda x: -len(x[1].encode()))[:0] or Counter(fs).most_common())
print(" esc( defs:", len(re.findall(r"function esc\(|const esc\s*=", js)))
show("watchdog 40s / debounced retry", find(js, r"40_?000|40000|watchdog", maxhits=12))
show("tonight-strip responsive", find(css, r"tonight-strip", maxhits=8))
show("44px floors (coarse)", find(css, r"pointer:\s*coarse|hover:\s*none", maxhits=6))
show("focus-within parity", find(css, r"focus-within", maxhits=8))
show("sticky header scroll context", find(css, r"scroll-context|scrollContext|sticky", maxhits=12))
print(" APP_VERSION in js:", re.findall(r"JS_VERSION\s*=\s*(\d+)", js)[:3])
