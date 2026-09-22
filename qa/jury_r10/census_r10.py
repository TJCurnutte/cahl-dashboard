#!/usr/bin/env python3
"""R10-3/5 (visual craft) fix-verification census: R9 citations -> v70 deployed bytes."""
import re, hashlib, sys

R10 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10"
R9 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r9"

style = open(f"{R10}/deployed/css_style.css", encoding="utf-8", errors="replace").read()
landing = open(f"{R10}/deployed/css_landing.css", encoding="utf-8", errors="replace").read()
app = open(f"{R10}/deployed/js_app.js", encoding="utf-8", errors="replace").read()

style67 = open(f"{R9}/style_v67.css", encoding="utf-8", errors="replace").read()
landing67 = open(f"{R9}/landing_v67.css", encoding="utf-8", errors="replace").read()
app67 = open(f"{R9}/app_v67.js", encoding="utf-8", errors="replace").read()

print("=== baseline identity checks ===")
for name, path, expect in [("style_v67", f"{R9}/style_v67.css", "9670ff78"),
                           ("app_v67", f"{R9}/app_v67.js", "079d3033")]:
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:8]
    print(f"{name}: sha {h} (R9 recorded {expect}) -> {'MATCH' if h == expect else 'DIFFERENT'}")
# style_v67 recorded sha was for deployed style.css?v=67 (88,795 B) — our saved copy may differ; report bytes
print(f"style_v67 bytes: {len(style67.encode())} | app_v67 bytes: {len(app67.encode())} | landing_v67: {len(landing67.encode())}")

print("\n=== FIX 1: landing.css font-size census ===")
sizes = re.findall(r"font-size:\s*([\d.]+)px", landing)
from collections import Counter
c = Counter(sizes)
allowed = {"13", "14", "16", "20", "26", "30", "34"}
off = {k: v for k, v in c.items() if k not in allowed}
print(f"v70 landing.css font-size decls: {sorted(c.items(), key=lambda x: float(x[0]))}")
print(f"off-scale (not in 13/14/16/20/26/30/34): {off if off else 'NONE — census clean'}")
print(f"total px decls: {sum(c.values())}, off-scale decls: {sum(off.values())}")
# v67 comparison
c67 = Counter(re.findall(r"font-size:\s*([\d.]+)px", landing67))
print(f"v67 landing.css census for comparison: {sorted(c67.items(), key=lambda x: float(x[0]))}")
# tokens used in landing?
tok_uses = len(re.findall(r"var\(--fs-", landing)) + len(re.findall(r"var\(--mono-", landing))
print(f"landing var(--fs-*/--mono-*) uses: {tok_uses}")
# any font-size via var tokens or non-px (rem/em)?
other = re.findall(r"font-size:\s*(?![\d.]+px)([^;]+);", landing)
print(f"non-px font-size decls: {Counter(other) if other else 'none'}")

print("\n=== FIX 2: duplicate light-theme .rink-head rule ===")
hits = [(m.start(), style.count("\n", 0, m.start()) + 1) for m in re.finditer(r'html\[data-theme="light"\] \.rink-head', style)]
print(f"v70 occurrences of html[data-theme=light] .rink-head: {len(hits)} at lines {[l for _, l in hits]}")
hits67 = len(re.findall(r'html\[data-theme="light"\] \.rink-head', style67))
print(f"v67 occurrences: {hits67}")

print("\n=== FIX 3: palette :focus-within cue ===")
fw = [(m.start(), style.count("\n", 0, m.start()) + 1) for m in re.finditer(r":focus-within", style)]
print(f":focus-within occurrences in style.css: {len(fw)} at lines {[l for _, l in fw]}")
for pos, line in fw:
    seg = style[max(0, pos - 120): pos + 200].replace("\n", " | ")
    print(f"  L{line}: ...{seg}...")
# v67 comparison
fw67 = len(re.findall(r":focus-within", style67))
print(f"v67 :focus-within count: {fw67}")
# palette input row selector present?
print(f".pal-input-row in v70 style.css: {len(re.findall(r'pal-input-row', style))} refs")

print("\n=== FIX 4: CTA hover token #2b71c4 ===")
for hexv in ["2b71c4", "1f6cb8", "3a8fe0", "2a7fd4"]:
    n70 = len(re.findall(hexv, style + landing))
    print(f"#{hexv}: v70 style+landing refs = {n70}")
uh = [(m.start(), style.count("\n", 0, m.start()) + 1) for m in re.finditer(r"--union-hover:[^;]+;", style + landing)]
for pos, line in uh:
    seg = (style + landing)[pos: pos + 60]
    print(f"  union-hover decl: {seg} (file offset line ~{line})")
uh67 = re.findall(r"--union-hover:[^;]+;", style67 + landing67)
print(f"v67 union-hover decls: {uh67}")

print("\n=== CONTEXT CLAIM: Today sponsor strip unified to lockup ===")
# app.js: which sponsor image does the Today strip use?
for m in re.finditer(r"(crown[^\"'\s]*|upright-lockup[^\"'\s]*)\.(png|svg|jpg)", app):
    line = app.count("\n", 0, m.start()) + 1
    print(f"app.js L{line}: {m.group(0)}")
for m in re.finditer(r"(crown|upright-lockup)[^\"']*\.(png|svg)", landing):
    line = landing.count("\n", 0, m.start()) + 1
    print(f"landing.css L{line}: {m.group(0)}")
print(f"app.js 'crown' refs: {len(re.findall('crown', app))} | 'lockup' refs: {len(re.findall('lockup', app, re.I))}")
idx = open(f"{R10}/index.html").read()
print(f"index.html img refs: {re.findall(r'img/[a-zA-Z0-9._-]+', idx)}")

print("\n=== CONTEXT CLAIM: landing raw-hex fallbacks dropped ===")
raw = re.findall(r"#[0-9a-fA-F]{3,8}\b", landing)
print(f"landing.css v70 raw hex literals: {sorted(set(raw))} ({len(raw)} total)")
varuses = len(re.findall(r"var\(", landing))
print(f"landing.css v70 var() uses: {varuses}")
raw67 = re.findall(r"#[0-9a-fA-F]{3,8}\b", landing67)
print(f"landing.css v67 raw hex: {sorted(set(raw67))} ({len(raw67)} total)")

print("\n=== /api/players latency note (Supabase env-gated) ===")
for m in re.finditer(r"SUPABASE|from_supabase|supabase", app):
    line = app.count("\n", 0, m.start()) + 1
    ctx = app[max(0, m.start() - 40): m.start() + 60].replace("\n", " | ")
    print(f"app.js L{line}: {ctx}")
