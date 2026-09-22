#!/usr/bin/env python3
"""R6-3 audit part 4: sub-9px census w/ selectors, light contrast, misc."""
import re
from collections import Counter

css = open('style_v59.css', encoding='utf-8').read()
lines = css.splitlines()

print('=== SUB-9PX FONT-SIZE USES (selector context) ===')
cur_sel = ''
for i, l in enumerate(lines):
    s = re.match(r'^([.#][a-zA-Z][^,{]*)\{', l.strip())
    if s:
        cur_sel = s.group(1).strip()
    m = re.search(r'font-size:\s*([0-9.]+)px', l)
    if m and float(m.group(1)) < 9:
        print(f'L{i+1} [{cur_sel or "?"}]: {m.group(1)}px | {l.strip()[:100]}')

print('\n=== HEADER H1 ===')
for i, l in enumerate(lines):
    if 'header h1' in l and 'font-size' in l:
        print(f'L{i+1}: {l.strip()[:130]}')

print('\n=== font-variant-numeric COUNT ===')
print(len(re.findall(r'font-variant-numeric', css)), 'occurrences;',
      len(re.findall(r'font-variant-numeric:\s*tabular-nums', css)), 'tabular-nums')

print('\n=== LIGHT THEME CONTRAST ===')
def lum(hx):
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb)+0.05)/(min(la, lb)+0.05)
for label, fg, bg in [
    ('light accent #ce1126 / panel #ffffff', 'ce1126', 'ffffff'),
    ('light union #0057b8 / panel #ffffff', '0057b8', 'ffffff'),
    ('light faint #8a99ad / panel #ffffff', '8a99ad', 'ffffff'),
    ('light muted #5d6f88 / panel #ffffff', '5d6f88', 'ffffff'),
]:
    r = ratio(fg, bg)
    aa = 'PASS' if r >= 4.5 else ('AA-large only' if r >= 3 else 'FAIL')
    print(f'{label}: {r:.2f}:1 [{aa}]')

print('\n=== MONO FAMILY HARD-SIZE vs TOKEN USES ===')
mono_hard = [l.strip()[:90] for l in lines
             if re.search(r'font-family:\s*var\(--mono\)', l) and 'font-size' in l]
print(f'mono rules with inline px size: {len(mono_hard)}')
mono_inherit = len([l for l in lines if re.search(r'font-family:\s*var\(--mono\)', l)])
print(f'total --mono family decls: {mono_inherit}')

print('\n=== RINK-HEAD COLOR CHECK (dark: var(--union) = #2a7fd4 = 4.46:1 sub-AA) ===')
for i, l in enumerate(lines):
    if '.rink-head' in l and '{' in l:
        j = i
        while j < len(lines) and '}' not in lines[j]:
            print(f'L{j+1}: {lines[j].strip()[:110]}')
            j += 1
        break

print('\n=== TONIGHT-KPI 3rd child accent (live KPI) ===')
for i, l in enumerate(lines):
    if 'tonight-kpi:nth-child(3)' in l:
        print(f'L{i+1}: {l.strip()[:120]}')
