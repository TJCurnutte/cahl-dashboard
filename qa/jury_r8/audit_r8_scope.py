#!/usr/bin/env python3
"""R8 juror3 part 3: scoping of light-theme overrides, 13px census detail, JS + index checks."""
import re

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(f"{R8}/style_v63.css", encoding="utf-8", errors="replace").read()
js = open(f"{R8}/app_v63.js", encoding="utf-8", errors="replace").read()
html = open(f"{R8}/index_v63.html", encoding="utf-8", errors="replace").read()

def rule_context(css, needle, span=400):
    """Print surrounding context for each occurrence of needle."""
    out = []
    for m in re.finditer(re.escape(needle), css):
        s = max(0, m.start() - span)
        out.append(css[s:m.start() + span])
    return out

print("### .rink-head override contexts (look for enclosing selector) ###")
for i, ctx in enumerate(rule_context(css, ".rink-head { color: var(--union-deep); }", 500)):
    print(f"--- occurrence {i+1} (preceding 500 chars) ---")
    print(ctx[-560:])
    print()

print("### what rule block precedes each .rink-head? media/attr scope ###")
# find enclosing block start for each occurrence
for m in re.finditer(r'\.rink-head\s*\{', css):
    start = m.start()
    # walk backwards to find whether inside @media or attribute-scoped block
    pre = css[max(0, start - 700):start]
    opens = pre.count('{')
    closes = pre.count('}')
    depth = opens - closes
    scope = "TOP-LEVEL" if depth <= 0 else f"nested depth {depth}"
    tail = pre[-120:].replace("\n", " | ")
    print(f"occ@{start}: {scope} | ...{tail}")

print("\n### 13px literal contexts (sample 8 of 19) ###")
lines = css.splitlines()
hits = [(i, l.strip()) for i, l in enumerate(lines) if 'font-size: 13px' in l]
print(f"total 13px lines: {len(hits)}")
for i, l in hits[:8]:
    print(f"L{i+1}: {l[:150]}")

print("\n### 14px / 18px contexts (all) ###")
for i, l in enumerate(lines):
    if 'font-size: 14px' in l or 'font-size: 18px' in l:
        print(f"L{i+1}: {l.strip()[:150]}")

print("\n### pt units (print block) ###")
for m in re.finditer(r'font-size:\s*[\d.]+pt[^;]*;', css):
    print(m.group(0))

print("\n### JS font-size literals ###")
print(re.findall(r'font-size[^,;)\]]*', js)[:10] or "none")
print("count px literals in JS style strings:", len(re.findall(r'font-size:\s*\d+px', js)))

print("\n### landing gate / logo / sponsor in index ###")
for kw in ['gate', 'logo', 'Upright', 'upright', 'sponsor', 'CAHL']:
    idxs = [m.start() for m in re.finditer(kw, html)]
    print(f"{kw}: {len(idxs)} hits")

print("\n### landing gate / sponsor in JS ###")
for kw in ['landing', 'gate', 'Upright', 'sponsor', 'data-scrim']:
    n = len(re.findall(kw, js))
    print(f"{kw}: {n} hits")

print("\n### index head (title/meta/css refs) ###")
print(re.search(r'<title>[^<]*</title>', html).group(0) if re.search(r'<title>[^<]*</title>', html) else "no title")
for m in re.finditer(r'<link[^>]+>', html):
    print(m.group(0)[:160])
