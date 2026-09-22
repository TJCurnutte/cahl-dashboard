#!/usr/bin/env python3
"""R10 juror5 part 9 (final): live-pill/has-live/pal markup in shell + app; app.py supabase region."""
import re

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
SH = open(D + "index.html", encoding="utf-8", errors="replace").read()
A = open(D + "app.js", encoding="utf-8", errors="replace").read()
AL = A.splitlines()

print("=== shell: live-pill / pal-ov / refresh ===")
for i, l in enumerate(SH.splitlines()):
    if re.search(r"live-pill|pal-ov|id=.refresh|autoToggle", l):
        print(f"  shell L{i+1}: {l.strip()[:170]}")

print("=== app.js: has-live toggling ===")
for i, l in enumerate(AL):
    if "has-live" in l:
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== app.js: pal-ov class list / open toggling ===")
for i, l in enumerate(AL):
    if re.search(r"classList\.(add|remove|toggle)\(['\"]open|palOv|paletteOverlay", l):
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== app.py L326-345 + L470-490 (supabase layer) ===")
ap = open("/Users/traviscurnutte/cahl-dashboard/app.py", encoding="utf-8", errors="replace").read().splitlines()
for j in range(325, 348):
    print(f"{j+1}: {ap[j][:150]}")
print("   ...")
for j in range(469, 490):
    print(f"{j+1}: {ap[j][:150]}")
