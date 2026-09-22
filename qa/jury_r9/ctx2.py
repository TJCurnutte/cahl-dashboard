#!/usr/bin/env python3
"""R9 juror5 part 4: selectPlayer body, (data||{}).error census, function names for L2521/L282, dead-team heal, landing markup."""
import os, re

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
lines = app.split("\n")
htm = open(os.path.join(OUT, "index.html"), "r", errors="replace").read()

# selectPlayer body
idx = app.find("function selectPlayer")
print("== selectPlayer ==")
print(app[idx:idx+700] if idx != -1 else "NOT FOUND")

# (data||{}).error census
print("\n== (data||{}).error census ==")
for m in re.finditer(r"\$\{[^}]{0,30}\(data\s*\|\|\s*\{\}\)\.error[^}]{0,40}\}", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln} {'RAW!!!' if 'esc(' not in m.group(0) else 'esc-ok'} :: {m.group(0)[:110]}")

# which function encloses L2521 and L282?
def enclosing(ln_target):
    depth_best = None
    for m in re.finditer(r"function\s+(\w+)\s*\(", app):
        ln = app[:m.start()].count("\n") + 1
        if ln <= ln_target:
            depth_best = (ln, m.group(1))
    return depth_best
print("\nenclosing fn L2521:", enclosing(2521))
print("enclosing fn L282:", enclosing(282))
print("enclosing fn L1576:", enclosing(1576))

# dead-team self-heal
print("\n== dead-team self-heal census ==")
for kw in ["no longer available", "cahl-team", "stale"]:
    hits = [app[:m.start()].count("\n") + 1 for m in re.finditer(re.escape(kw), app, re.IGNORECASE)]
    print(f"  {kw!r}: lines {hits[:20]}")
idx = app.lower().find("no longer available")
if idx != -1:
    ln = app[:idx].count("\n") + 1
    print(f"\ncontext around L{ln}:")
    print(app[max(0, idx-1100):idx+700])

# landing markup in shell
print("\n== shell landing structure (id/class census) ==")
for kw in ["landing", "nav", "hero", "feature", "about", "sponsor", "footer", "upright", "chillerstats", "not affiliated", "Open Dashboard"]:
    hits = sorted(set(re.findall(rf"[a-zA-Z0-9_-]*{kw}[a-zA-Z0-9_-]*", htm, re.IGNORECASE)))
    print(f"  {kw}: {hits[:14]}")
print("\nshell size:", len(htm))
