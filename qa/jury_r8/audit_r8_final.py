#!/usr/bin/env python3
"""R8 juror3 part 4: hero-glow static rule, JS behaviors, v61 vs v63 census, sponsor strip, misc."""
import re

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(f"{R8}/style_v63.css", encoding="utf-8", errors="replace").read()
css61 = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r7/style_v61.css", encoding="utf-8", errors="replace").read()
js = open(f"{R8}/app_v63.js", encoding="utf-8", errors="replace").read()
js61 = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r7/app_v61.js", encoding="utf-8", errors="replace").read()
html = open(f"{R8}/index_v63.html", encoding="utf-8", errors="replace").read()

def census(sheet):
    vals = re.findall(r'font-size:\s*([\d.]+)px', sheet)
    from collections import Counter
    c = Counter(vals)
    return sorted(c, key=float), len(vals), dict(sorted(c.items(), key=lambda kv: float(kv[0])))

print("### type census v61 vs v63 ###")
d61, n61, c61 = census(css61)
d63, n63, c63 = census(css)
print("v61 distinct:", d61, "| decls:", n61)
print("v61 counts:", c61)
print("v63 distinct:", d63, "| decls:", n63)
print("v63 counts:", c63)

print("\n### hero-glow rule in v63 (static?) ###")
for m in re.finditer(r'\.hero-glow[^{]*\{[^}]*\}', css):
    print(m.group(0))
print("hero-glow mentions:", len(re.findall(r'hero-glow', css)))
# any animation/transition on hero-glow?
for m in re.finditer(r'hero-glow[^{]*\{[^}]*\}', css):
    if 'animation' in m.group(0):
        print("ANIMATION FOUND ON HERO-GLOW:", m.group(0))

print("\n### sponsor-strip in main sheet ###")
for m in re.finditer(r'\.sponsor-strip[^{,]*\{[^}]*\}', css):
    print(m.group(0)[:200])
print("sponsor mentions in main css:", len(re.findall(r'sponsor', css)))

print("\n### JS behavior checks (v63) ###")
checks = {
    "AbortController": 'AbortController' in js,
    "retry-once": 'retry' in js.lower(),
    "reduced-motion gate": 'prefers-reduced-motion' in js,
    "animateNumbers RM gate": bool(re.search(r'animateNumbers[\s\S]{0,400}prefers-reduced-motion', js)),
    "data-scrim emission": 'data-scrim' in js,
    "section-h usage in JS": 'section-h' in js,
    "inline h3 style= in JS": bool(re.search(r'h3[^>]*style=', js)),
    "landing gate logic": 'landingGate' in js,
    "gate sessionStorage": bool(re.search(r'landingGate[\s\S]{0,300}sessionStorage|sessionStorage[\s\S]{0,300}landingGate', js)),
}
for k, v in checks.items():
    print(f"{k}: {v}")

print("\n### JS delta summary v61 -> v63 ###")
import difflib
diff = list(difflib.unified_diff(js61.splitlines(), js.splitlines(), n=0, lineterm=''))
adds = [l for l in diff if l.startswith('+') and not l.startswith('+++')]
dels = [l for l in diff if l.startswith('-') and not l.startswith('---')]
print(f"+{len(adds)} / -{len(dels)} lines")
for l in adds[:40]:
    print(l[:160])

print("\n### zebra / sticky / misc invariants ###")
print("nth-child(odd/even) zebra rules:", len(re.findall(r'nth-child\(odd|nth-child\(even', css)))
print("letter-spacing 0.16em micro caps:", len(re.findall(r'letter-spacing:\s*0\.16em', css)))
print("outline: none occurrences (a11y smell):", len(re.findall(r'outline:\s*none', css)))
print("focus-visible rules:", len(re.findall(r'focus-visible', css)))
print("hover:none/coarse media:", len(re.findall(r'\(hover: none\)|\(pointer: coarse\)', css)))
print("aria in index:", len(re.findall(r'aria-', html)))
print("gate-kicker/gate-title in landing:", end=' ')
land = open(f"{R8}/landing_v63.css", encoding="utf-8", errors="replace").read()
print(['gate-kicker' in land, 'gate-title' in land, 'gate-cta' in land])
print("\n### landing.css body/canvas ###")
for m in re.finditer(r'(?:body|\.gate-card)\s*\{[^}]*\}', land):
    print(m.group(0)[:260])
