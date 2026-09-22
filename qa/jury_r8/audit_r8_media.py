#!/usr/bin/env python3
"""R8 juror3 part 2: media-query context, tokens, contrast math."""
import re

CSS = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/style_v63.css"
css = open(CSS, encoding="utf-8", errors="replace").read()

# --- walk rules with media context ---
media_stack = []
print("### tonight-strip / rink-head / focus rules with media context ###")
# crude but effective: split into blocks tracking @media
pos = 0
depth = 0
buf = ""
cur_media = None
i = 0
token = ""
# Simpler: iterate over top-level segments
segments = re.split(r'(@media[^{]+\{)', css)
cur = segments[0]
pairs = [(None, cur)]
idx = 1
while idx < len(segments):
    media = segments[idx]
    body = segments[idx + 1] if idx + 1 < len(segments) else ""
    # find matching close brace (body may contain nested braces)
    depth = 0
    end = 0
    for j, ch in enumerate(body):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                end = j
                break
    else:
        end = len(body)
    pairs.append((media.strip().rstrip('{').strip(), body[:end]))
    idx += 2

for media, body in pairs:
    if '.tonight-strip' in body and 'grid-template-columns' in body:
        for m in re.finditer(r'\.tonight-strip\s*\{[^}]*\}', body):
            print(f"[{media or 'base'}] {m.group(0)}")
    if '.rink-head' in body and 'color' in body:
        for m in re.finditer(r'\.rink-head\s*\{[^}]*\}', body):
            print(f"[{media or 'base'}] {m.group(0)}")

print("\n### all @media queries in sheet ###")
for m in re.finditer(r'@media([^{]+)\{', css):
    print(m.group(1).strip())

print("\n### :root token definitions ###")
for m in re.finditer(r':root\s*\{([^}]*)\}', css):
    for line in m.group(1).splitlines():
        line = line.strip()
        if line and ('font' in line or 'size' in line or 'display' in line or 'mono' in line or 'accent' in line or 'union' in line):
            print(line)

print("\n### --fs / --display / --text-size tokens anywhere ###")
for m in sorted(set(re.findall(r'--(?:fs|display|text)[\w-]*\s*:\s*[^;]+;', css))):
    print(m.strip())

# --- contrast math ---
def lum(hexcolor):
    h = hexcolor.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    def f(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contrast(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

print("\n### contrast verification ###")
print(f"#4a9ae6 on #131b2b (panel dark): {contrast('#4a9ae6', '#131b2b'):.2f}:1")
print(f"#4a9ae6 on #0e1420: {contrast('#4a9ae6', '#0e1420'):.2f}:1")
print(f"#4a9ae6 on #1a2334: {contrast('#4a9ae6', '#1a2334'):.2f}:1")
print(f"#2a7fd4 (old union) on #131b2b: {contrast('#2a7fd4', '#131b2b'):.2f}:1")
print(f"#ef3d54 (accent) on #131b2b: {contrast('#ef3d54', '#131b2b'):.2f}:1")
print(f"#7d92ad (faint dark) on #131b2b: {contrast('#7d92ad', '#131b2b'):.2f}:1")
print(f"#5d6b80 (faint light) on #f2f5fa: {contrast('#5d6b80', '#f2f5fa'):.2f}:1")
print(f"#ce1126 (accent light) on #f2f5fa: {contrast('#ce1126', '#f2f5fa'):.2f}:1")
# panel colors — find them
print("\n### panel/background token values ###")
for m in sorted(set(re.findall(r'--panel[\w-]*\s*:\s*[^;]+;', css))):
    print(m.strip())
for m in sorted(set(re.findall(r'--bg[\w-]*\s*:\s*[^;]+;', css))):
    print(m.strip())
