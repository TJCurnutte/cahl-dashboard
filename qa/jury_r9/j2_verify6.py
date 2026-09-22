#!/usr/bin/env python3
"""Jury R9 juror2 — part 6: api() timeout, pill-count, app.js literals, logo fit, radius."""
import os, re, struct, urllib.request, ssl

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
sty = open(os.path.join(J2, "style.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()
lines_a = app.split("\n"); lines_s = sty.split("\n")

print("== BD. api() timeout ==")
i = app.find("async function api(")
if i < 0: i = app.find("function api(")
print(app[i:i+900] if i >= 0 else "api() not found")

print("\n== BE. pill-count ==")
for m in re.finditer(r"[^\n]*pill-count[^\n]*", sty):
    print(f"  L{sty[:m.start()].count(chr(10))+1}: {m.group(0).strip()[:140]!r}")

print("\n== BF. font-size literals in app.js ==")
lit = re.findall(r"font-size:\s*[\d.]+px", app)
print("  count:", len(lit), lit[:6])

print("\n== BG. tabular-nums census (style.css) ==")
tn = [sty[:m.start()].count("\n")+1 for m in re.finditer(r"tabular-nums|font-variant-numeric", sty)]
print("  hits:", len(tn), tn[:12])

print("\n== BH. radius tokens ==")
for m in re.finditer(r"--radius[a-z-]*\s*:\s*[^;]+;", sty):
    print(f"  L{sty[:m.start()].count(chr(10))+1}: {m.group(0)}")

print("\n== BI. lp-cta-sm rules in landing.css ==")
for m in re.finditer(r"[^\n]*lp-cta-sm[^\n]*", lnd := open(os.path.join(J2, "landing.css"), errors="replace").read()):
    print(f"  L{lnd[:m.start()].count(chr(10))+1}: {m.group(0).strip()[:140]!r}")

print("\n== BJ. logo dims (nav fit @390px) ==")
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}
for name in ["cahl-logo-hd.png", "upright-lockup.png"]:
    try:
        req = urllib.request.Request(f"https://cahl.neural-forge.io/static/img/{name}", headers=UA)
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            d = r.read()
        if d[:8] == b"\x89PNG\r\n\x1a\n" and d[12:16] == b"IHDR":
            w, h = struct.unpack(">II", d[16:24])
            print(f"  {name}: {w}x{h}px, {len(d)/1024:.0f}KB  (lp-brand @34px h -> {34*w/h:.0f}px wide; hero min(340px,78%)=271px -> h={271*h/w:.0f}px)")
        else:
            print(f"  {name}: not PNG header, {len(d)}B")
    except Exception as e:
        print(f"  {name}: ERR {e}")

print("\n== BK. nav fit calc @390 ==")
# lp-nav: padding 12px 22px, gap 18px; children: lp-brand img + (lp-links hidden <719) + CTA
# CTA @390 (<=430? no, 390<=430 yes): min-height 50, padding 0 26, font-size 17
cta_text = "Open Dashboard"
approx_text_w = len(cta_text) * 17 * 0.52  # Saira ~0.5em avg
print(f"  available: 390-44=346px; CTA ~{approx_text_w+52:.0f}px (text {approx_text_w:.0f} + pad 52 + border)")
print(f"  => logo budget ~{346-approx_text_w-52-18:.0f}px wide at 34px height")
