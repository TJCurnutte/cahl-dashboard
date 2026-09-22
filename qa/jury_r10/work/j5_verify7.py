#!/usr/bin/env python3
"""R10 juror5 part 7: definitive RM coverage for palette animations + L1205-1230 context."""
import re

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
SC = open(D + "style.css", encoding="utf-8", errors="replace").read().splitlines()

print("=== L1205-1235 full ===")
for j in range(1204, 1235):
    print(f"{j+1}: {SC[j][:170]}")

print("=== every line containing 'animation' in style.css ===")
for i, l in enumerate(SC):
    if "animation" in l:
        print(f"  L{i+1}: {l.strip()[:150]}")

print("=== every line containing 'pal-ov' or '.pal ' or '.pal,' or '.pal{' ===")
for i, l in enumerate(SC):
    if re.search(r"\.pal-ov|\.pal[\s,{:.]", l):
        print(f"  L{i+1}: {l.strip()[:150]}")

print("=== spinner selectors ===")
for i, l in enumerate(SC):
    if "spinner" in l:
        print(f"  L{i+1}: {l.strip()[:150]}")

print("=== count '@media' blocks and find ALL prefers-reduced-motion occurrences ===")
for i, l in enumerate(SC):
    if "prefers-reduced-motion" in l:
        print(f"  L{i+1}: {l.strip()[:120]}")
