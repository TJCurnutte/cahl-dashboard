#!/usr/bin/env python3
"""Jury R9 juror2 — deep verify: blocks, th sticky, wd 40s, tokens, landing, copy."""
import os, re

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
sty = open(os.path.join(J2, "style.css"), errors="replace").read()
lnd = open(os.path.join(J2, "landing.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()
htm = open(os.path.join(J2, "index.html"), errors="replace").read()

def block_at(txt, ln_start_marker, label):
    i = txt.find(ln_start_marker)
    if i < 0:
        print(f"  [{label}] marker not found: {ln_start_marker[:60]!r}")
        return
    ln = txt[:i].count("\n") + 1
    j = txt.find("{", i); depth = 0; k = j
    while k < len(txt):
        if txt[k] == "{": depth += 1
        elif txt[k] == "}":
            depth -= 1
            if depth == 0: break
        k += 1
    print(f"  [{label}] block starting L{ln}:")
    for s in txt[i:k+1].split("\n"):
        print("    ", s[:150])

print("== A. <=699 swipe-chip block (full) ==")
block_at(sty, '/* ---- (1) Tables < 700px', "swipe-block")

print("\n== B. <=699 table-scroll block (full) ==")
block_at(sty, '.card:has(table) table {', "table-scroll-block")
# also print 6 lines before it for the comment
i = sty.find('.card:has(table) table {')
print("  ...context before:")
for s in sty[max(0,i-400):i].split("\n")[-8:]:
    print("    ", s[:150])

print("\n== C. th sticky rules ==")
for m in re.finditer(r"[^\n]*\bth\b[^{\n]*\{[^}]*sticky[^}]*", sty):
    ln = sty[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group(0)[:160]!r}")

print("\n== D. card-level max-height:70vh remnants ==")
for m in re.finditer(r"[^\n]*max-height:\s*7?0vh[^\n]*", sty):
    ln = sty[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group(0)[:140]!r}")

print("\n== E. watchdog 40s deadline ==")
for m in re.finditer(r"[^\n]*40000[^\n]*", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group(0)[:140]!r}")

print("\n== F. error-site census (raw vs esc) ==")
for m in re.finditer(r"[^\n]*\$\{(?:esc\()?(?:data\.error|e\.message|err\.message|error(?:\.message)?)\)?\}?[^\n]*", app):
    seg = m.group(0)
    if "esc(" in seg or "data.error" in seg or "e.message" in seg:
        ln = app[:m.start()].count("\n") + 1
        tag = "ESC " if re.search(r"esc\((data\.error|e\.message|err\.message|error)", seg) else "RAW "
        if "${" in seg:
            print(f"  {tag} L{ln}: {seg.strip()[:150]!r}")

print("\n== G. FIX 4: union-cta / sponsor-gold tokens ==")
for name, txt in [("style.css", sty), ("landing.css", lnd)]:
    for pat in [r"--union-cta[^;]*;", r"--sponsor-gold[^;]*;", r"#1f6cb8", r"#b8925e"]:
        hits = [(txt[:m.start()].count("\n")+1, m.group(0)[:80]) for m in re.finditer(pat, txt)]
        print(f"  {name} {pat!r}: {len(hits)} -> {hits[:6]}")

print("\n== H. cold-index copy ==")
for m in re.finditer(r"[^\n]*[Cc]old[^\n]*", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group(0).strip()[:170]!r}")
for m in re.finditer(r"up to ~?\s*\d+s[^\"']*", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  ~30s copy L{ln}: {m.group(0)[:100]!r}")

print("\n== I. landing/nav new surface ==")
print("  landing.css lines:", lnd.count("\n")+1)
for pat in [r"max-width:\s*719", r"max-width:\s*699", r"max-width:\s*479", r"nav-links", r"\.hero\b", r"stack"]:
    hits = [(lnd[:m.start()].count("\n")+1, lnd[m.start():m.start()+60].replace("\n"," ")) for m in re.finditer(pat, lnd)]
    print(f"  landing {pat!r}: {len(hits)} -> {hits[:8]}")
print("  index.html nav refs:", re.findall(r"class=\"[^\"]*nav[^\"]*\"", htm)[:8])
print("  index.html length refs landing:", re.findall(r"landing[^\"]*", htm)[:6])

print("\n== J. landing.css comment drift (localStorage/sessionStorage) ==")
for m in re.finditer(r"[^\n]*(?:localStorage|sessionStorage)[^\n]*", lnd):
    ln = lnd[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group(0).strip()[:130]!r}")
