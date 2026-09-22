#!/usr/bin/env python3
"""R6-3 audit part 2: multiline rules, light theme, focus parity, exact contrast."""
import re

css = open('style_v59.css', encoding='utf-8').read()
lines = css.splitlines()

def rule_block(sel_re, maxspan=14):
    """Find selector line, return the following rule body until closing brace."""
    out = []
    for i, l in enumerate(lines):
        if re.search(sel_re, l) and '{' in l:
            body = []
            j = i
            while j < len(lines) and '}' not in lines[j] and (j - i) < maxspan:
                body.append(lines[j].strip())
                j += 1
            out.append((i + 1, ' '.join(body)[:220]))
    return out

print('=== MULTILINE RULE CHECKS ===')
for sel in [r'\.heat-val\b', r'\.heat-name\b', r'\.gd-empty\b', r'\.sb-name\b',
            r'header h1', r'\.brand-text', r'font-variant-numeric']:
    for ln, body in rule_block(sel)[:3]:
        print(f'L{ln}: {body}')
    print()

print('=== tbody focus-visible parity (R5 fix #3 status) ===')
fv = [(i + 1, l.strip()[:130]) for i, l in enumerate(lines)
      if 'focus-visible' in l and ('tr' in l or 'tbody' in l)]
print(f'tr/tbody focus-visible rules: {len(fv)}')
for ln, l in fv[:5]:
    print(f'  L{ln}: {l}')
hover = [(i + 1, l.strip()[:130]) for i, l in enumerate(lines)
         if re.search(r'tbody tr:hover|tbody tr:has', l)]
for ln, l in hover[:5]:
    print(f'  hover L{ln}: {l}')

print('\n=== LIGHT THEME TOKENS ===')
light = re.search(r'data-theme="light"\s*\{([^}]+)\}', css)
if light:
    for tok in ['--accent', '--bg', '--panel', '--faint', '--muted', '--text-2', '--union']:
        m = re.search(re.escape(tok) + r':\s*([^;]+);', light.group(1))
        if m:
            print(f'light {tok}: {m.group(1).strip()}')

print('\n=== EXACT CONTRAST (real v59 tokens) ===')
def lum(hx):
    hx = hx.lstrip('#')
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb)+0.05)/(min(la, lb)+0.05)
pairs = [
    ('DARK accent #e8253c / bg #070b12', 'e8253c', '070b12'),
    ('DARK accent #e8253c / panel #0e1420', 'e8253c', '0e1420'),
    ('CANDIDATE #ef3d54 / bg #070b12', 'ef3d54', '070b12'),
    ('CANDIDATE #ef3d54 / panel #0e1420', 'ef3d54', '0e1420'),
    ('DARK faint #5a6a82 / panel #0e1420', '5a6a82', '0e1420'),
    ('DARK muted #8494ab / panel #0e1420', '8494ab', '0e1420'),
    ('DARK text-2 #c3cddb / panel #0e1420', 'c3cddb', '0e1420'),
    ('DARK union #2a7fd4 / panel #0e1420', '2a7fd4', '0e1420'),
]
for label, fg, bg in pairs:
    r = ratio(fg, bg)
    aa = 'PASS' if r >= 4.5 else ('AA-large only' if r >= 3 else 'FAIL')
    print(f'{label}: {r:.2f}:1 [{aa}]')
if light:
    lt = {}
    for tok in ['accent', 'bg', 'panel', 'faint', 'muted', 'text-2', 'union']:
        m = re.search(r'--' + tok + r':\s*#([0-9a-fA-F]{6})', light.group(1))
        if m:
            lt[tok] = m.group(1)
    for tok, fg in lt.items():
        if 'panel' in lt:
            r = ratio(fg, lt['panel'])
            aa = 'PASS' if r >= 4.5 else ('AA-large only' if r >= 3 else 'FAIL')
            print(f'LIGHT {tok} #{fg} / panel #{lt["panel"]}: {r:.2f}:1 [{aa}]')

print('\n=== TONIGHT-STRIP MOBILE (4-col at 390px?) ===')
m = re.search(r'R6 — TODAY PAGE ENRICHMENT(.*?)FIX PASS R1-D', css, re.S)
block = m.group(1) if m else ''
print('mobile media overrides grid-template-columns?', 'grid-template-columns' in block.split('@media')[-1] if '@media' in block else 'no media block')
mob = re.search(r'@media[^{]*599[^{]*\{(.*?)\}\s*\}\s*$', block, re.S)
print((block.split('@media (max-width: 599px)')[-1][:400]) if '@media (max-width: 599px)' in block else 'NO 599px MEDIA')

print('\n=== ENRICHMENT JS WIRING ===')
js = open('app_v59.js', encoding='utf-8').read()
for cls in ['tonight-strip', 'tonight-kpi', 'tonight-num', 'tonight-label', 'scored-strip', 'scored-chip', 'scored-nums', 'rink-head']:
    print(f'{cls}: {"wired" if cls in js else "MISSING"}')

print('\n=== JS_VERSION / AUTO SYNC ===')
print('JS_VERSION 59 in app.js:', '59' in js[:4000])
idx = open('index_v59.html', encoding='utf-8').read()
m = re.search(r'static/js/app\.js\?v=(\d+)', idx)
m2 = re.search(r'static/css/style\.css\?v=(\d+)', idx)
print('index refs: js?v=' + (m.group(1) if m else '?') + ' css?v=' + (m2.group(1) if m2 else '?'))
