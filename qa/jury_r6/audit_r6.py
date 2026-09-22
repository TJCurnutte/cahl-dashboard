#!/usr/bin/env python3
"""R6-3 visual-craft audit of deployed v59 bytes (Chrome-free)."""
import re, sys

css = open('style_v59.css', encoding='utf-8').read()
js = open('app_v59.js', encoding='utf-8').read()

print('=== STANDING LEDGER (v59 bytes) ===')
for name in ['heat-val', 'heat-name', 'gd-empty', 'sb-name', 't-home', 'tl-game.otl']:
    hits = [(i + 1, l.strip()[:110]) for i, l in enumerate(css.splitlines())
            if re.search(re.escape(name), l) and 'font-size' in l]
    print(f'-- {name}:')
    for ln, l in hits[:4]:
        print(f'   L{ln}: {l}')

print('\n--- mono tokens ---')
for tok in ['mono-xs', 'mono-sm', 'mono-md']:
    defs = [i + 1 for i, l in enumerate(css.splitlines()) if f'--{tok}:' in l]
    uses = len(re.findall(rf'var\(--{tok}\)', css))
    print(f'--{tok}: defs={defs} uses={uses}')

print('\n--- dark accent ---')
for hexv in ['e8253c', 'ef3d54']:
    lines = [i + 1 for i, l in enumerate(css.splitlines()) if hexv.lower() in l.lower()]
    print(f'{hexv}: {lines}')

print('\n=== PX FONT-SIZE CENSUS ===')
sizes = re.findall(r'font-size:\s*([0-9.]+)px', css)
from collections import Counter
c = Counter(sizes)
print(f'distinct px sizes: {len(c)}')
for k in sorted(c, key=float):
    print(f'  {k}px x{c[k]}')

print('\n=== NEW R6 BLOCK SIZE AUDIT ===')
m = re.search(r'R6 — TODAY PAGE ENRICHMENT(.*?)FIX PASS R1-D', css, re.S)
if m:
    block = m.group(1)
    print(sorted(set(re.findall(r'font-size:\s*([0-9.]+)px', block)), key=float),
          'in', len([l for l in block.splitlines() if 'font-size' in l]), 'font-size lines')
    # sub-10px audit inside new block
    small = [s for s in re.findall(r'font-size:\s*([0-9.]+)px', block) if float(s) < 10]
    print('sub-10px values in new block:', small)

print('\n=== OFF-TOKEN HEX SCAN (whole v59 css) ===')
hexes = Counter(h.upper() for h in re.findall(r'#[0-9a-fA-F]{6}\b', css))
allowed = {'002654', 'CE1126', 'A2AAAD', 'FFFFFF', '0E1622', 'FFFFFF'}
off = {h: n for h, n in hexes.items() if h not in allowed and not h.startswith('00')}
print(f'total distinct 6-hex: {len(hexes)}; top: {hexes.most_common(12)}')

print('\n=== JS CHECKS ===')
print('renderTeam guard:', 'renderTeam' in js, '| abort/timeout:', 'AbortController' in js,
      '| retry:', bool(re.search(r'retry', js, re.I)))
print('autoToggle wiring:', 'autoToggle' in js)

print('\n=== CONTRAST MATH (WCAG) ===')
def lum(hx):
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)
pairs = [
    ('accent #e8253c on bg #0a0f17', 'e8253c', '0a0f17'),
    ('accent #e8253c on panel #101a26', 'e8253c', '101a26'),
    ('alt accent #ef3d54 on bg #0a0f17', 'ef3d54', '0a0f17'),
    ('faint on panel (dark)', '5c6b7d', '101a26'),
    ('muted on panel (dark)', '8b98a9', '101a26'),
    ('text-2 on panel (dark)', 'c9d3de', '101a26'),
    ('union #002654 on light panel #ffffff', '002654', 'ffffff'),
    ('union-deep #003a75 on light panel #ffffff', '003a75', 'ffffff'),
]
for label, fg, bg in pairs:
    print(f'{label}: {ratio(fg, bg):.2f}:1')

print('\n=== TOKEN GRAB (for report accuracy) ===')
for var in ['--accent:', '--faint:', '--muted:', '--panel:', '--bg:', '--text-2:', '--union:']:
    m = re.search(re.escape(var) + r'\s*([^;]+);', css)
    if m:
        print(var, m.group(1).strip())
