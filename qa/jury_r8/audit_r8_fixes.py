#!/usr/bin/env python3
"""R8 juror3: verify R7-cited fixes in deployed v63 CSS bytes."""
import re

CSS = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/style_v63.css"
css = open(CSS, encoding="utf-8", errors="replace").read()

def section(title):
    print(f"\n### {title} ###")

# 1. rink-head color
section("1. .rink-head rules")
for m in re.finditer(r'\.rink-head[^{]*\{[^}]*\}', css):
    print(m.group(0))

# 2. tonight-strip grid columns incl. breakpoints
section("2. tonight-strip rules (all)")
for m in re.finditer(r'\.tonight-strip[^{,]*\{[^}]*\}', css):
    print(m.group(0))

# 3. focus-within parity
section("3. tbody hover/focus rules")
for line in css.splitlines():
    if 'focus' in line and ('tr' in line or 'tbody' in line):
        print(line.strip())

# 4. hero-glow-breathe retired?
section("4. hero-glow residue")
print("hero-glow-breathe occurrences:", css.count('hero-glow-breathe'))

# 5. section-h
section("5. h3.section-h")
for m in re.finditer(r'h3\.section-h[^{]*\{[^}]*\}', css):
    print(m.group(0))

# 6. sb-card scrim
section("6. sb-card[data-scrim]")
for m in re.finditer(r'\.sb-card\[data-scrim[^{]*\{[^}]*\}', css):
    print(m.group(0))

# 7. font-size literal census
section("7. font-size literal px census")
vals = re.findall(r'font-size:\s*([\d.]+)px', css)
from collections import Counter
c = Counter(vals)
print("distinct:", sorted(c, key=float), "| total decls:", len(vals))
print("counts:", dict(sorted(c.items(), key=lambda kv: float(kv[0]))))

# 8. token var usage counts
section("8. mono token use counts")
for tok in ['--mono-xs', '--mono-sm', '--mono-md']:
    print(tok, ":", len(re.findall(r'font-size:\s*var\(' + tok + r'\)', css)))

# 9. raw-hex census (defensible vs raw)
section("9. raw hex colors (#xxx / #xxxxxx) count")
hexes = re.findall(r'#[0-9a-fA-F]{3,8}\b', css)
hc = Counter(h.lower() for h in hexes)
print("total hex occurrences:", len(hexes), "distinct:", len(hc))
print(dict(hc.most_common(20)))

# 10. keyframes census
section("10. keyframes")
print(re.findall(r'@keyframes\s+([\w-]+)', css))

# 11. 44px floors
section("11. 44px / min-height floors")
print("min-height: 44px:", css.count('min-height: 44px'), "| height: 44px:", css.count('height: 44px'), "| 44px total:", css.count('44px'))

# 12. tabular-nums, backdrop-filter, zebra, sticky
section("12. craft invariants")
print("tabular-nums:", css.count('tabular-nums'), "| backdrop-filter:", len(re.findall(r'backdrop-filter', css)),
      "| position: sticky:", css.count('position: sticky'), "| prefers-reduced-motion:", css.count('prefers-reduced-motion'))

# 13. accent + faint + union tokens
section("13. key tokens")
for var in ['--accent', '--faint', '--union:', '--union-deep', '--union-hover', '--muted', '--otl']:
    for m in re.finditer(re.escape(var) + r'\s*:\s*([^;]+);', css):
        print(var, '=', m.group(1).strip())
