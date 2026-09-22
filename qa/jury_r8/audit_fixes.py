#!/usr/bin/env python3
"""R8 juror4: verify R7-cited fixes in deployed v63 bytes."""
import re, sys

A = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/deployed/app.js", encoding="utf-8").read()
C = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/deployed/style.css", encoding="utf-8").read()
I = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r8/deployed/index.html", encoding="utf-8").read()

def lines(src): return src.split("\n")
AL, CL, IL = lines(A), lines(C), lines(I)

def find(src_lines, pat, label, maxhits=6):
    rx = re.compile(pat)
    hits = [(i+1, l.strip()[:170]) for i, l in enumerate(src_lines) if rx.search(l)]
    print(f"\n== {label} :: {len(hits)} hit(s)")
    for n, l in hits[:maxhits]:
        print(f"  L{n}: {l}")
    if len(hits) > maxhits: print(f"  ... +{len(hits)-maxhits} more")
    return hits

print("########## FIX 1: cold-index copy in renderPlayerTypeahead ##########")
find(AL, r"Index cold", "cold-index copy")
find(AL, r"10-25s|10–25s", "10-25s copy")
find(AL, r"renderPlayerTypeahead", "renderPlayerTypeahead def")

print("\n########## FIX 2: armSkeletonWatchdog wd40 / retry / Retrying ##########")
find(AL, r"40000|wd40|WD_40", "wd40 hard-error 40s")
find(AL, r"armSkeletonWatchdog", "armSkeletonWatchdog refs")
find(AL, r"data-wd-retry|wdRetry|wd-retry", "data-wd-retry")
find(AL, r"data-retrying", "data-retrying debounce")
find(AL, r"Retrying", "Retrying… state")

print("\n########## FIX 3: hasOpp on team recent_result ##########")
find(AL, r"recent_result", "recent_result sites")
find(AL, r"hasOpp", "hasOpp guard")

print("\n########## FIX 4: esc() on data.error in error paints ##########")
find(AL, r"data\.error", "data.error sites")
find(AL, r"esc\(", "esc( uses (count)", maxhits=30)

print("\n########## STANDING: loadTeamContent direct binding ##########")
find(AL, r"window\.loadTeamContent", "window.loadTeamContent")
find(AL, r"JS_VERSION", "JS_VERSION")

print("\n########## STANDING: api() 30s ceiling + retry-once ##########")
find(AL, r"AbortController|abort\(\)", "AbortController")
find(AL, r"30000", "30000 ceiling")
find(AL, r"attempt\s*<\s*2|attempts", "retry-once loop")

print("\n########## STANDING: client-error telemetry ##########")
find(AL, r"client-error|client_error|sendBeacon", "client-error telemetry")

print("\n########## index.html version + boot ##########")
find(IL, r"APP_VERSION|app\.js\?v=|style\.css\?v=|v=63", "version markers")
