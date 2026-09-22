#!/usr/bin/env python3
"""R9 juror5 part 13: v63 vs v67 inline h3 attribution, hero-next-pulse audit, gate storage, lp-nav blur."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
v63 = open(os.path.expanduser("~/cahl-dashboard/qa/jury_r8/app.js"), "r", errors="replace").read()
v67 = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lnd = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()

print("== v63 inline h3 census ==")
for m in re.finditer(r"<h3[^>]*style=[^>]*>", v63):
    ln = v63[:m.start()].count("\n") + 1
    print(f"  v63 L{ln}: {m.group(0)[:110]}")
print("v63 inline style= count:", len(re.findall(r'style=\\?"', v63)))

print("\n== v67 inline h3 census ==")
for m in re.finditer(r"<h3[^>]*style=[^>]*>", v67):
    ln = v67[:m.start()].count("\n") + 1
    print(f"  v67 L{ln}: {m.group(0)[:110]}")

# hero-next-pulse animation usage
print("\n== hero-next-pulse usage ==")
for m in re.finditer(r"[^}]*hero-next-pulse[^}]*}", sty):
    print("  ", " ".join(m.group(0).split())[:220])

# rise-in usage
for m in re.finditer(r"[^}]*/\*[^*]*\*/[^{]*\{[^}]*rise-in[^}]*\}", sty):
    print("  rise-in:", " ".join(m.group(0).split())[:200])

# gate storage
print("\n== gate storage + dismiss ==")
i = v67.find("function gateDismiss")
print(v67[i:i+520] if i != -1 else "gateDismiss not found")

# lp-nav blur
print("\n== lp-nav rule ==")
m = re.search(r"\.lp-nav\s*\{[^}]*\}", lnd)
print(" ".join(m.group(0).split()) if m else "?")
print("landing backdrop-filter occurrences:")
for m in re.finditer(r".{40}backdrop-filter[^;]*;", lnd):
    print("  ...", m.group(0)[-90:])
