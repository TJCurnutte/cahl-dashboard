#!/usr/bin/env python3
"""R8 j2 probe 5: standing fixes in v63 bytes, manifest, card base, body overflow."""
import re, os, json

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(os.path.join(OUT, "style_v63.css"), encoding="utf-8").read()
cssl = css.split("\n")
js = open(os.path.join(OUT, "app_v63.js"), encoding="utf-8").read()
jsl = js.split("\n")
idx = open(os.path.join(OUT, "index_v63.html"), encoding="utf-8").read()

def show(lines, pat, label, n=10):
    rx = re.compile(pat)
    hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if rx.search(l)]
    print(f"\n== {label} == ({len(hits)} hits)")
    for ln, l in hits[:n]:
        print(f"  L{ln}: {l[:150]}")
    return hits

show(jsl, r"concat\(finals\)", "By-Rink concat(finals) in v63")
show(jsl, r"scored-nums|scored-teams", "scored-chip emit", n=6)
show(cssl, r"scored-num|scored-team", "scored-chip css", n=8)
show(jsl, r"scrim", ".scrim emit + css refs", n=8)
show(cssl, r"\.scrim", ".scrim css", n=6)
show(cssl, r"animateNumbers|prefers-reduced-motion", "RM gate refs", n=10)

print("\n== .card base rule ==")
for i, l in enumerate(cssl):
    if re.match(r"\.card\s*\{", l.strip()):
        for j in range(i, min(i + 8, len(cssl))):
            print(f"  L{j+1}: {cssl[j].strip()[:140]}")
        break

print("\n== L158-170 overflow context ==")
for i in range(155, 170):
    print(f"  L{i+1}: {cssl[i].strip()[:130]}")

print("\n== icon/og/apple refs in index.html ==")
for i, l in enumerate(idx.split("\n")):
    if re.search(r"icon|og:|apple-touch|manifest|theme-color", l, re.I):
        print(f"  L{i+1}: {l.strip()[:160]}")

print("\n== landingGate markup L44-75 ==")
for i in range(43, 76):
    print(f"  L{i+1}: {idx.split(chr(10))[i].strip()[:160]}")

# manifest
try:
    with urllib.request.urlopen if False else open(os.path.join(OUT, "manifest.json"), "r") as f:
        pass
except Exception:
    pass
import urllib.request
try:
    req = urllib.request.Request("https://cahl.neural-forge.io/static/manifest.json",
                                 headers={"User-Agent": "cahl-jury-r8-j2"})
    man = urllib.request.urlopen(req, timeout=20).read().decode()
    print("\n== manifest.json ==")
    print(man[:800])
except Exception as e:
    print("manifest FAIL", e)

# table row height check: td padding 9px -> row ~40px; coarse floors?
show(cssl, r"tbody (tr|td)|td\s*\{|tr\s*\{", "row height rules", n=8)
show(cssl, r"touch-action|-webkit-tap-highlight", "tap highlight", n=6)
