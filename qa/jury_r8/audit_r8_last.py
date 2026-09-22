#!/usr/bin/env python3
"""R8 juror3 part 6: retry signal sharing, h3 style= match, landing.css selector detail."""
import re

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
js = open(f"{R8}/app_v63.js", encoding="utf-8", errors="replace").read()
land = open(f"{R8}/landing_v63.css", encoding="utf-8", errors="replace").read()

print("### api() retry block (does retry reuse ctrl.signal?) ###")
m = re.search(r'const ctrl = new AbortController\(\);[\s\S]{0,2200}', js)
body = m.group(0)[:2200] if m else ""
# print only the fetch/retry-relevant lines
for line in body.splitlines():
    if any(k in line for k in ['fetch', 'signal', 'ctrl', 'retry', 'res =', 'catch', 'await', 'kill']):
        print(line.strip()[:150])

print("\n### h3 style= matches in JS ###")
for m in re.finditer(r'.{80}h3[^>]{0,80}style=.{0,120}', js):
    print(repr(m.group(0)[:260]))

print("\n### section-h usage in JS ###")
for m in re.finditer(r'.{60}section-h.{60}', js):
    print(repr(m.group(0)[:180]))

print("\n### landing.css selectors using off-scale sizes / hex ###")
for size in ['15px', '19px', '25px', '30px', '14px']:
    for m in re.finditer(r'([^{}]{0,80})\{[^}]*font-size:\s*' + re.escape(size) + r'[^}]*\}', land):
        sel = m.group(1).strip().splitlines()[-1].strip() if m.group(1).strip() else '?'
        print(f"{size}: {sel[:90]}")
for hx in ['#1f6cb8', '#b8925e', '#ffffff']:
    for m in re.finditer(r'([^{}]{0,80})\{[^}]*' + re.escape(hx) + r'[^}]*\}', land):
        sel = m.group(1).strip().splitlines()[-1].strip() if m.group(1).strip() else '?'
        print(f"{hx}: {sel[:90]}")

print("\n### gate-cta + gate sizing (44px story) ###")
for m in re.finditer(r'\.gate-cta[^{]*\{[^}]*\}', land):
    print(m.group(0)[:240])

print("\n### landing reduced-motion block ###")
for m in re.finditer(r'@media \(prefers-reduced-motion[^)]*\)\s*\{[\s\S]{0,200}', land):
    print(m.group(0)[:220])
