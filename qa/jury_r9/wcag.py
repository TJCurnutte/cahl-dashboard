#!/usr/bin/env python3
"""R9 juror5 part 14: WCAG contrast for landing surfaces, both themes."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()

def lum(hex_):
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    def f(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

# tokens
def token(name, theme_block):
    m = re.search(rf"--{name}:\s*(#[0-9a-fA-F]{{6}})", theme_block)
    return m.group(1) if m else None

dark_block = re.search(r":root\s*\{[^}]+\}", sty).group(0)
light_block = re.search(r"\[data-theme=\"light\"\]\s*\{[^}]+\}", sty).group(0)

dark = {n: token(n, dark_block) for n in ["bg", "panel", "panel-2", "inset", "text", "text-2", "muted", "faint", "sponsor-gold", "union-cta", "union"]}
light = {n: token(n, light_block) for n in ["bg", "panel", "panel-2", "inset", "text", "text-2", "muted", "faint", "sponsor-gold", "union", "union-cta"] if token(n, light_block)}
print("dark tokens:", dark)
print("light tokens:", light)

pairs = [
    ("lp-title text/bg", "text", "bg"),
    ("lp-sub muted/bg", "muted", "bg"),
    ("lp-note/fine/hint faint/bg", "faint", "bg"),
    ("feature h3 text/panel", "text", "panel"),
    ("feature p muted/panel", "muted", "panel"),
    ("sponsor-blurb muted/panel", "muted", "panel"),
    ("sponsor-kicker gold/inset", "sponsor-gold", "inset"),
    ("f-icon gold/inset (11px)", "sponsor-gold", "inset"),
    ("lp-links a muted/bg", "muted", "bg"),
    ("lp-fine a muted/bg", "muted", "bg"),
]
print("\n== WCAG (dark / light) ==")
for label, fk, bk in pairs:
    r = []
    for theme in (dark, light):
        if theme.get(fk) and theme.get(bk):
            r.append(ratio(theme[fk], theme[bk]))
        else:
            r.append(None)
    print(f"  {label}: dark {r[0]:.2f}:1 / light {r[1]:.2f}:1" if all(r) else f"  {label}: {r}")

# CTA white on union-cta (dark uses #1f6cb8; light theme? check if --union-cta in light block)
cta = "ffffff"
print(f"\n  CTA white/#1f6cb8: {ratio(cta, '#1f6cb8'):.2f}:1 (large text AA=3, normal AA=4.5)")
print(f"  gate-cta ghost text/panel-2 dark: {ratio(dark['text'], dark['panel-2']):.2f}:1 / light: {ratio(light['text'], light['panel-2']):.2f}:1")
print(f"  lp-title 44px w800 (large text — AA 3:1): pass" if ratio(dark['text'], dark['bg']) > 3 else "FAIL")
