#!/usr/bin/env python3
"""Jury R8 J5 part 3: payloads, WCAG, remaining v63 claims."""
import re, json, pathlib, math
from collections import Counter

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")

def lum(hexc):
    hexc = hexc.lstrip("#")
    if len(hexc) == 3:
        hexc = "".join(c * 2 for c in hexc)
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(fg, bg):
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

print("=== WCAG computed ===")
pairs = [
    ("CTA white on #1f6cb8", "#ffffff", "#1f6cb8"),
    ("CTA white on --union #2a7fd4 (hover)", "#ffffff", "#2a7fd4"),
    ("CTA white on --union-deep (if hover dark)", "#ffffff", "#1d5c9e"),
    ("rink-head #4a9ae6 on dark panel #0d1420", "#4a9ae6", "#0d1420"),
    ("rink-head #4a9ae6 on dark bg #070b12", "#4a9ae6", "#070b12"),
    ("sponsor hover #b8925e on inset", "#b8925e", "#0a0f18"),
    ("gate-sub muted on panel", "#8fa3bd", "#0d1420"),
]
for name, fg, bg in pairs:
    try:
        print(f"  {name}: {ratio(fg, bg):.2f}:1")
    except Exception as e:
        print(f"  {name}: ERR {e}")

# token values actually in css
for tok in ("--union:", "--union-deep:", "--panel:", "--inset:", "--bg:", "--muted:", "--faint:", "--text-2:"):
    m = re.search(re.escape(tok) + r"\s*([^;]+);", css)
    if m:
        print("  token", tok, m.group(1).strip()[:60])

# --- payloads ---
print("\n=== /api/today ===")
today = json.loads((Q / "api_today.json").read_text())
print(json.dumps(today, indent=1)[:1800])

print("\n=== /api/leaders ===")
lead = json.loads((Q / "api_leaders.json").read_text())
print(json.dumps(lead, indent=1)[:900])

print("\n=== /api/league (keys + standings head) ===")
lg = json.loads((Q / "api_league.json").read_text())
print("keys:", list(lg.keys()))
st = lg.get("standings") or []
print("standings rows:", len(st))
for row in st[:4]:
    print("  ", {k: row.get(k) for k in list(row.keys())[:12]})

print("\n=== /api/team (overview keys + recent_result + next_game) ===")
tm = json.loads((Q / "api_team.json").read_text())
ov = tm.get("overview") or {}
print("overview keys:", list(ov.keys()))
print("recent_result:", json.dumps(ov.get("recent_result"))[:300])
print("next_game:", json.dumps(ov.get("next_game"))[:300])
print("team_name:", ov.get("team_name"))

# --- remaining v63 claims in bytes ---
print("\n=== remaining v63 claims ===")
for pat, label in [
    (r"40_?000|40000", "watchdog 40s"),
    (r"tonight-strip", "tonight-strip rules"),
    (r"dataStamp", "dataStamp sites"),
    (r"focus-within", "focus-within parity"),
    (r"scroll-context|data-scroll", "sticky scroll context"),
    (r"cahl-entered", "gate session key"),
    (r"cold.?index|Still warming|warming up", "cold-index copy"),
    (r"debounce", "debounce refs"),
]:
    hits = [(js.count("\n", 0, m.start()) + 1, js[m.start():m.start() + 110].split("\n")[0]) for m in re.finditer(pat, js, re.I)]
    print(f"\n  {label} ({len(hits)}):")
    for ln, s in hits[:8]:
        print(f"    L{ln}: {s.strip()[:110]}")
