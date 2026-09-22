#!/usr/bin/env python3
"""R10 juror5 part 8: live-pill markup class, spinner usage sites, pal markup."""
import re

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
A = open(D + "app.js", encoding="utf-8", errors="replace").read()
AL = A.splitlines()
SC = open(D + "style.css", encoding="utf-8", errors="replace").read().splitlines()

print("=== live-pill markup in app.js ===")
for i, l in enumerate(AL):
    if "live-pill" in l:
        print(f"  L{i+1}: {l.strip()[:160]}")

print("=== live-pill styles ===")
for i, l in enumerate(SC):
    if "live-pill" in l:
        print(f"  L{i+1}: {l.strip()[:160]}")

print("=== spinner markup usage in app.js ===")
for i, l in enumerate(AL):
    if "spinner" in l:
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== .spinner full decl ===")
for j in range(946, 956):
    print(f"{j+1}: {SC[j][:160]}")

print("=== .pal-ov / .pal markup usage (palette open) ===")
for i, l in enumerate(AL):
    if "pal-ov" in l:
        print(f"  L{i+1}: {l.strip()[:140]}")

print("=== does RM block or any rule kill .pal-ov.open / .pal animation? ===")
hits = [(i+1, l.strip()[:120]) for i, l in enumerate(SC) if "pal-ov.open" in l or (".pal" in l and "animation: none" in l)]
print(hits if hits else "  NO animation:none kill for .pal-ov.open or .pal")

print("=== kpal spinner context (L3040-3050) ===")
for j in range(3039, 3052):
    print(f"{j+1}: {AL[j][:150]}")
