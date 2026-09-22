#!/usr/bin/env python3
"""R10 juror5 part 2: hunk bodies, style diff, esc census, token rows, shell URLs."""
import re, difflib, hashlib

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
A = open(D+"app.js", encoding="utf-8", errors="replace").read()
AL = A.splitlines()
SC = open(D+"style.css", encoding="utf-8", errors="replace").read()
SH = open(D+"index.html", encoding="utf-8", errors="replace").read()
OLD = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/app_v67.js", encoding="utf-8", errors="replace").read()

# my own shell vs deployed shell
MINE = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/work/j5/shell.html", "rb").read()
print("my shell sha256[:12]:", hashlib.sha256(MINE).hexdigest()[:12], "len", len(MINE))
print("deployed sha256[:12]:", hashlib.sha256(SH.encode()).hexdigest()[:12])

print("=== shell asset URLs ===")
for m in re.finditer(r'<(?:script|link)[^>]*(?:src|href)="([^"]+)"', SH):
    print(" ", m.group(1))

print("=== app.js v67->v70 full hunks ===")
d = list(difflib.unified_diff(OLD.splitlines(), AL, lineterm="", n=4))
cur = []
for line in d:
    if line.startswith("@@"):
        if cur: print("\n".join(cur)); print("---")
        cur = [line]
    elif cur and not line.startswith(("+++", "---")):
        cur.append(line)
if cur: print("\n".join(cur))

print("=== style.css v67 -> v70 diff ===")
try:
    OLDSC = open("/Users/traviscurnutte/cahl-dashboard/qa/jury_r9/assets_r9/style.css", encoding="utf-8", errors="replace").read()
    print("old style bytes:", len(OLDSC))
    d2 = list(difflib.unified_diff(OLDSC.splitlines(), SC.splitlines(), lineterm="", n=2))
    print(f"hunks: {len([l for l in d2 if l.startswith('@@')])}")
    print("\n".join(d2[:60]))
except FileNotFoundError as e:
    print("no v67 style capture:", e)

print("=== token rows region L690-725 ===")
for i in range(689, 725):
    print(f"{i+1}: {AL[i][:150]}")

print("=== dead-team region L1995-2020 ===")
for i in range(1994, 2020):
    print(f"{i+1}: {AL[i][:150]}")

print("=== hunk regions L2180-2215 ===")
for i in range(2179, 2215):
    print(f"{i+1}: {AL[i][:150]}")

print("=== localStorage init L45-60 ===")
for i in range(44, 60):
    print(f"{i+1}: {AL[i][:150]}")

print("=== esc RENDER-site census (interpolation of data.error / e.message) ===")
bad = []
for i, l in enumerate(AL):
    for m in re.finditer(r"\$\{([^}]*\.(?:error|message)[^}]*)\}", l):
        expr = m.group(1)
        if "esc(" not in expr and "esc (" not in expr:
            bad.append((i+1, expr[:90], l.strip()[:110]))
print(f"unescaped interpolation sites: {len(bad)}")
for n, e, l in bad: print(f"  L{n}  ${{{e}}}  |  {l}")
good = [(i+1) for i, l in enumerate(AL) if re.search(r"\$\{[^}]*esc\((?:data\.error|e\.message|data && data\.error)[^}]*\}", l)]
print(f"escaped render sites: {good}")

print("=== inline style= count (fixed) ===")
print("style=\" occurrences:", len(re.findall(r'style="', A)))
print("onclick=\" occurrences:", len(re.findall(r'onclick="', A)))

LC = open(D+"landing.css", encoding="utf-8", errors="replace").read()

print("=== token definitions used w/o fallback exist in style.css :root ===")
for tok in ["--union-cta", "--union-hover", "--sponsor-gold", "--mono-sm", "--mono-xs", "--display"]:
    defs = len(re.findall(re.escape(tok) + r"\s*:", SC))
    uses_l = len(re.findall(re.escape(tok) + r"\)", LC))
    print(f"  {tok}: defs in style.css={defs}, uses in landing.css={uses_l}")

print("=== client fetch ceilings (players) ===")
for i, l in enumerate(AL):
    if re.search(r"AbortSignal|setTimeout\(|abort", l) and re.search(r"\b(25|30|45|60)000\b", l):
        print(f"  L{i+1}: {l.strip()[:130]}")

print("=== team fetch URL (for dead-team probe) ===")
for i, l in enumerate(AL):
    if "/api/team" in l:
        print(f"  L{i+1}: {l.strip()[:130]}")
