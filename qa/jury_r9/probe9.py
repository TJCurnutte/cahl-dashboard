#!/usr/bin/env python3
"""R9 juror5 part 16: sponsor strip in app.js, css v63 vs v67 keyframe diff if saved, landing probe file check."""
import os, re, difflib

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()

print("== sponsor strip emit in app.js ==")
for m in re.finditer(r"sponsor-strip|sponsorStrip|upright-lockup", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln}: {app[app.rfind(chr(10), 0, m.start()-100)+1:m.start()+120][:160].strip()}")

# css diff if v63 css saved
for cand in ["~/cahl-dashboard/qa/jury_r8/style.css", "~/cahl-dashboard/qa/jury_r8/deployed/style.css"]:
    p = os.path.expanduser(cand)
    if os.path.exists(p):
        v63 = open(p, errors="replace").read()
        v67 = open(os.path.join(OUT, "style.css"), errors="replace").read()
        sm = difflib.SequenceMatcher(None, v63.split("\n"), v67.split("\n"), autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        print(f"\n== {cand} vs v67 style.css: {len(ops)} hunks ==")
        for tag, i1, i2, j1, j2 in ops[:24]:
            print(f"  {tag} v63[{i1+1}:{i2}] -> v67[{j1+1}:{j2}]")
            for l in v67.split("\n")[j1:j2][:2]:
                print("     +", l.strip()[:140])
        break
else:
    print("\n(no v63 style.css saved — keyframe hero-next-pulse age unverified, audit by value instead)")

# landing probe file
lp = os.path.expanduser("~/cahl-dashboard/qa/landing_probe.js")
print("\nlanding_probe.js exists:", os.path.exists(lp), "| size:", os.path.getsize(lp) if os.path.exists(lp) else 0)
if os.path.exists(lp):
    src = open(lp, errors="replace").read()
    print("probe PASS count mentions:", re.findall(r"(\d+)\s*/\s*(\d+)\s*PASS", src)[:3])
