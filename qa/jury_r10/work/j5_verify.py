#!/usr/bin/env python3
"""R10 juror5: byte-level verification of v70 vs my R9 citations."""
import re, difflib, json

A = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/app.js", encoding="utf-8", errors="replace").read()
AL = A.splitlines()
LC = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/landing.css", encoding="utf-8", errors="replace").read()
LLL = LC.splitlines()
SC = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/style.css", encoding="utf-8", errors="replace").read()
SH = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/index.html", encoding="utf-8", errors="replace").read()
OLD = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/app_v67.js", encoding="utf-8", errors="replace").read()
OLDLC = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/landing_v67.css", encoding="utf-8", errors="replace").read()
OLDSC_P = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/assets_r9/style.css"

print("=== 1. UNCONDITIONAL leader rows (R9-A headliner) ===")
uncond = [(i+1, l.strip()[:110]) for i, l in enumerate(AL) if "<tr class=link onclick=selectPlayer" in l or "<tr class=\"link\" onclick=\"selectPlayer" in l]
print(f"unconditional '<tr class=link onclick=selectPlayer' sites: {len(uncond)}")
for n, l in uncond: print(f"  L{n}: {l}")

print("=== 2. Conditional guarded row sites ===")
cond = [(i+1, l.strip()[:130]) for i, l in enumerate(AL) if "selectPlayer" in l and ("player_id ?" in l or "playerId ?" in l or "token ?" in l)]
print(f"conditional selectPlayer row sites: {len(cond)}")
for n, l in cond: print(f"  L{n}: {l}")
allsp = [(i+1, l.strip()[:110]) for i, l in enumerate(AL) if "selectPlayer(" in l and "function selectPlayer" not in l and "window.selectPlayer" not in l]
print(f"ALL selectPlayer references: {len(allsp)}")
for n, l in allsp: print(f"  L{n}: {l}")

print("=== 3. leaderSection / Analytics / League renderer check ===")
for pat in ["leaderSection", "Top Scorers", "loadLeagueContent", "loadAnalyticsContent"]:
    hits = [(i+1) for i, l in enumerate(AL) if pat in l]
    print(f"  {pat}: lines {hits[:8]}")

print("=== 4. landing.css font-size literals (R9 fix #2) ===")
fs = re.findall(r"font-size:\s*([\d.]+)px", LC)
from collections import Counter
print(f"literal px font-sizes: {len(fs)} distinct={sorted(set(fs), key=float)} counts={dict(Counter(fs))}")
print(f"var() font-sizes: {len(re.findall(r'font-size:[ ]*var[(]', LC))}")
fso = re.findall(r"font-size:\s*([\d.]+)px", OLDLC)
print(f"v67 landing literal px: {len(fso)} distinct={sorted(set(fso), key=float)}")

print("=== 5. backdrop-filter census ===")
for name, txt in [("landing.css", LC), ("style.css", SC)]:
    hits = [(i+1, l.strip()[:100]) for i, l in enumerate(txt.splitlines()) if "backdrop-filter" in l]
    print(f"  {name}: {len(hits)}")
    for n, l in hits: print(f"    L{n}: {l}")

print("=== 6. sponsor mark ===")
for pat in ["upright-crown", "upright-lockup"]:
    hits = [(i+1) for i, l in enumerate(AL) if pat in l]
    print(f"  app.js {pat}: {hits}")
hits = [(i+1) for i, l in enumerate(SH.splitlines()) if "upright-lockup" in l or "upright-crown" in l]
print(f"  shell: {hits}")

print("=== 7. inline-styled h3 + inline style census ===")
ih3 = [(i+1, l.strip()[:90]) for i, l in enumerate(AL) if re.search(r"<h3[^>]*style=", l)]
print(f"inline-styled h3: {len(ih3)}")
for n, l in ih3: print(f"  L{n}: {l}")
print(f"inline style= total in app.js: {len(re.findall(r'style=[>]', A.replace(chr(34)+chr(34), chr(34))))}")
print(f"onclick= total in app.js: {len(re.findall(r'onclick=', A))}")

print("=== 8. dataStamp ticking (R9 verified carry) ===")
hits = [(i+1, l.strip()[:100]) for i, l in enumerate(AL) if "paintStamp" in l or "setInterval(paintStamp" in l]
for n, l in hits: print(f"  L{n}: {l}")

print("=== 9. Supabase persistence (NEW v70) ===")
hits = [(i+1, l.strip()[:120]) for i, l in enumerate(AL) if re.search(r"supabase|SUPABASE", l, re.I)]
print(f"supabase refs: {len(hits)}")
for n, l in hits[:14]: print(f"  L{n}: {l}")

print("=== 10. dead-team self-heal ===")
hits = [(i+1, l.strip()[:120]) for i, l in enumerate(AL) if "no longer available" in l or "cahl-team" in l]
print(f"refs: {len(hits)}")
for n, l in hits[:10]: print(f"  L{n}: {l}")

print("=== 11. esc( on error interpolations ===")
raw_err = [(i+1, l.strip()[:110]) for i, l in enumerate(AL) if re.search(r"(data\.error|e\.message)", l) and "esc(" not in l]
print(f"UNescaped data.error/e.message interpolation sites: {len(raw_err)}")
for n, l in raw_err: print(f"  L{n}: {l}")

print("=== 12. keyframes + RM ===")
kf = re.findall(r"@keyframes\s+([\w-]+)", SC)
print(f"style.css keyframes ({len(kf)}): {kf}")
kf2 = re.findall(r"@keyframes\s+([\w-]+)", LC)
print(f"landing.css keyframes ({len(kf2)}): {kf2}")
rm = [(i+1, l.strip()[:80]) for i, l in enumerate(SC.splitlines()) if "prefers-reduced-motion" in l]
print(f"style.css RM blocks at: {[n for n,_ in rm]}")
rm2 = [(i+1) for i, l in enumerate(LLL) if "prefers-reduced-motion" in l]
print(f"landing.css RM blocks at: {rm2}")

print("=== 13. versions ===")
m = re.search(r"APP_VERSION\s*=\s*(\d+)", SH); print(f"shell APP_VERSION: {m.group(1) if m else None}")
m2 = re.search(r"JS_VERSION\s*=\s*(\d+)", A); print(f"app.js JS_VERSION: {m2.group(1) if m2 else None}")

print("=== 14. app.js diff v67 -> v70 (hunk map) ===")
d = list(difflib.unified_diff(OLD.splitlines(), AL, lineterm="", n=1))
hunks = [l for l in d if l.startswith("@@")]
print(f"hunks: {len(hunks)}")
for h in hunks: print(f"  {h}")

print("=== 15. landing.css diff v67 -> v70 ===")
d2 = list(difflib.unified_diff(OLDLC.splitlines(), LLL, lineterm="", n=0))
h2 = [l for l in d2 if l.startswith("@@")]
print(f"hunks: {len(h2)}")
print("\n".join(d2[:80]))
