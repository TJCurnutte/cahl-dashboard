#!/usr/bin/env python3
"""R6-3 audit part 3: focus rule body, light theme, hex contexts, size-set delta, fix candidates."""
import re

css = open('style_v59.css', encoding='utf-8').read()
old = open('../jury_r5/style_v55.css', encoding='utf-8').read()
lines = css.splitlines()

print('=== FOCUS-VISIBLE RULE BODY (L~1368-1380) ===')
print('\n'.join(lines[1366:1381]))

print('\n=== LIGHT THEME BLOCK ===')
m = re.search(r'html\[data-theme="light"\]\s*\{(.{0,900})', css, re.S)
if m:
    body = m.group(1)
    for tok in ['--accent', '--bg', '--panel', '--faint', '--muted', '--text-2', '--union', '--union-deep']:
        t = re.search(re.escape(tok) + r':\s*([^;]+);', body)
        if t:
            print(f'light {tok}: {t.group(1).strip()}')

print('\n=== OFF-TOKEN HEX CONTEXTS ===')
for hx in ['FF5D6E', '2FD08C', 'F0A24B', '3a8fe0']:
    ctx = [(i + 1, l.strip()[:120]) for i, l in enumerate(lines) if hx.lower() in l.lower()]
    print(f'--{hx}: {len(ctx)} hits')
    for ln, l in ctx[:3]:
        print(f'   L{ln}: {l}')

print('\n=== SIZE-SET DELTA v55 -> v59 ===')
def sizes(t):
    return set(re.findall(r'font-size:\s*([0-9.]+)px', t))
s_old, s_new = sizes(old), sizes(css)
print('added in v59:', sorted(s_new - s_old, key=float))
print('removed in v59:', sorted(s_old - s_new, key=float))
print(f'count: v55={len(s_old)} v59={len(s_new)}')

print('\n=== AUTO-TOGGLE :has FEEDBACK (R5 convergent fix verify) ===')
at = [(i + 1, l.strip()[:120]) for i, l in enumerate(lines) if 'autoToggle' in l]
for ln, l in at[:5]:
    print(f'L{ln}: {l}')

print('\n=== RINK-HEAD FIX CANDIDATES (contrast on dark bg/panel) ===')
def lum(hx):
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb)+0.05)/(min(la, lb)+0.05)
for cand in ['2a7fd4', '3f8fdd', '4a9ae6', '5aa5ec', '6ab0f2']:
    print(f'#{cand} / panel #0e1420: {ratio(cand, "0e1420"):.2f}:1 | / bg #070b12: {ratio(cand, "070b12"):.2f}:1')

print('\n=== TONIGHT-TIME / TONIGHT-NUM FONT FAMILIES (inheritance) ===')
for sel in ['tonight-time', 'tonight-num', 'tonight-kpi', 'scored-teams', 'scored-nums', 'rink-head']:
    for i, l in enumerate(lines):
        if f'.{sel}' in l and '{' in l:
            print(f'L{i+1}: {l.strip()[:150]}')
            break

print('\n=== SB-NAME 20PX MEDIA (L1173 ctx) ===')
print('\n'.join(x.strip()[:120] for x in lines[1170:1176]))
