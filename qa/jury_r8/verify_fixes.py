#!/usr/bin/env python3
"""R8 juror2: byte-verify my 3 R7 cited fixes + census in deployed v63."""
import re, os

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(os.path.join(OUT, "style_v63.css"), encoding="utf-8", errors="replace").read()
cssl = css.split("\n")
js = open(os.path.join(OUT, "app_v63.js"), encoding="utf-8", errors="replace").read()
jsl = js.split("\n")
idx = open(os.path.join(OUT, "index_v63.html"), encoding="utf-8", errors="replace").read()

def find_lines(hay, lines, pat, label, maxhits=12):
    rx = re.compile(pat)
    hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if rx.search(l)]
    print(f"\n== {label} ==  ({len(hits)} hits)")
    for n, l in hits[:maxhits]:
        print(f"  L{n}: {l[:150]}")
    if len(hits) > maxhits:
        print(f"  ... +{len(hits)-maxhits} more")
    return hits

# ---- FIX 1: mobile table scroll context + sticky th + bottom fade ----
find_lines(css, cssl, r"max-width:\s*699px", "FIX1 @media(max-width:699px) blocks")
find_lines(css, cssl, r"\.card:has\(table\)", "FIX1 .card:has(table)")
find_lines(css, cssl, r"max-height:\s*70vh", "FIX1 max-height:70vh")
find_lines(css, cssl, r"fade", "FIX1/2 fade rules (any)")

# ---- FIX 2: tonight-strip 2x2 at <=430 ----
find_lines(css, cssl, r"\.tonight-strip", "FIX2 .tonight-strip rules")
find_lines(css, cssl, r"repeat\(\s*2\s*,\s*1fr\)", "FIX2 repeat(2,1fr)")
find_lines(css, cssl, r"max-width:\s*430px", "FIX2/3 @media max-430 blocks")

# ---- FIX 3: button.small 44px floor in coarse block ----
find_lines(css, cssl, r"button\.small|\.small\b", "FIX3 .small selectors")
find_lines(css, cssl, r"hover:\s*none\s*\)?\s*,\s*\(pointer:\s*coarse", "FIX3 coarse-pointer media opens")
find_lines(css, cssl, r"min-height:\s*44px", "FIX3 all 44px min-heights")

# ---- standing greps (R7 discipline) ----
find_lines(css, cssl, r"min-height:\s*0|min-width:\s*0", "release-gate: min-h/w:0 anywhere")
find_lines(css, cssl, r"#3a8fe0|#e8253c", "off-token hexes (old hover / old accent)")
find_lines(css, cssl, r"font-size:\s*(\d+\.?\d*)px", "ALL px font-size literals", maxhits=40)
find_lines(js, jsl, r"font-size", "font-size in app.js", maxhits=20)
find_lines(js, jsl, r"cold|10-25s|first search", "cold-index copy in app.js", maxhits=12)
find_lines(js, jsl, r"style=\"[^\"]*margin-top", "inline margin-top emissions", maxhits=20)
find_lines(js, jsl, r"escapeHtml|esc\(", "esc() usage", maxhits=30)
find_lines(css, cssl, r"position:\s*sticky", "sticky rules")
find_lines(css, cssl, r"linear-gradient\(\s*180deg[^)]*transparent", "bottom-fade gradients")
print("\n== index.html checks ==")
for pat, lab in [(r"landing|gate", "landing/gate refs in index.html"), (r"APP_VERSION", "APP_VERSION"),
                 (r"sponsor|Upright", "sponsor refs in index.html")]:
    rx = re.compile(pat, re.I)
    for i, l in enumerate(idx.split("\n")):
        if rx.search(l):
            print(f"  index L{i+1}: {l.strip()[:140]}")
print("\ncss bytes:", len(css), "js bytes:", len(js))
