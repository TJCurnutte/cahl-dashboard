#!/usr/bin/env python3
"""R8 juror3 part 7: pal-input-row focus-within, weighted total computation."""
import re

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
css = open(f"{R8}/style_v63.css", encoding="utf-8", errors="replace").read()
land = open(f"{R8}/landing_v63.css", encoding="utf-8", errors="replace").read()

print("### pal-input-row focus styling (is de-styled input compensated?) ###")
for m in re.finditer(r'\.pal-input-row[^{,]*\{[^}]*\}', css):
    t = m.group(0)
    if 'focus' in t or 'within' in t or 'border' in t or 'background' in t:
        print(t[:220])

print("\n### section-h in JS (loose) ###")
js = open(f"{R8}/app_v63.js", encoding="utf-8", errors="replace").read()
i = js.find('section-h')
while i != -1:
    print(repr(js[max(0,i-90):i+70].replace('\n',' ')))
    i = js.find('section-h', i+1)

print("\n### WEIGHTED TOTAL ###")
scores = {
    "identity": 9.3, "type": 9.4, "color": 9.5, "layout": 9.4,
    "density": 9.3, "interaction": 9.4, "motion": 9.5,
    "depth": 9.4, "consistency": 9.3, "mobile": 9.5,
}
weights = {
    "identity": .12, "type": .12, "color": .10, "layout": .12, "density": .12,
    "interaction": .10, "motion": .08, "depth": .08, "consistency": .08, "mobile": .08,
}
total = 0.0
parts = []
for k in scores:
    c = scores[k] * weights[k]
    parts.append(f"{k} {scores[k]}x{weights[k]:.2f}={c:.3f}")
    total += c
print(" | ".join(parts))
print(f"TOTAL = {total:.3f} -> {round(total,1):.1f}")

# alternates for honesty check
for delta_name, adj in [("pessimistic", -0.05), ("optimistic", +0.05)]:
    t2 = sum((scores[k] + adj) * weights[k] for k in scores)
    print(f"{delta_name}: {t2:.3f}")
