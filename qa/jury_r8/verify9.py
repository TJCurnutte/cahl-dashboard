#!/usr/bin/env python3
"""Jury R8 J5 part 8: league leaders render path + selectPlayer dead-link check."""
import re, json, pathlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")

def show(label, pat, before=100, after=350, maxhits=4):
    print(f"\n=== {label} ===")
    for m in list(re.finditer(pat, js))[:maxhits]:
        ln = js.count("\n", 0, m.start()) + 1
        print(f"--- L{ln} ---")
        print(js[max(0, m.start()-before):m.end()+after])

show("renderLeague top scorers", r"[Tt]op [Ss]corers")
show("selectPlayer def", r"(function selectPlayer|window\.selectPlayer)", before=0, after=450, maxhits=2)
# does renderLeague use data.leaders?
show("league leaders usage", r"data\.leaders", before=60, after=200, maxhits=5)
