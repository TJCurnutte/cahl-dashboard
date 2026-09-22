#!/usr/bin/env python3
"""Jury R8 J5 part 2: ledger census, raw error sites, landing.css, WCAG math."""
import re, json, pathlib
from collections import Counter

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"
js = (Q / "app.js").read_text(encoding="utf-8", errors="replace")
css = (Q / "style.css").read_text(encoding="utf-8", errors="replace")
lcss = (Q / "landing.css").read_text(encoding="utf-8", errors="replace")
root = (Q / "root.html").read_text(encoding="utf-8", errors="replace")

# --- raw un-escaped data.error sites (the exact R7-A class) ---
print("=== RAW ${data.error} interpolation sites (no esc) ===")
for m in re.finditer(r"\$\{data\.error\}", js):
    start = js.rfind("\n", 0, m.start()) + 1
    end = js.find("\n", m.end())
    line_no = js.count("\n", 0, m.start()) + 1
    line = js[start:end if end > 0 else None]
    escd = re.search(r"esc\(\s*data\.error\s*\)", line)
    print(f"  L{line_no}: {'ESCAPED' if escd else '***RAW***'} :: {line.strip()[:170]}")

# --- full error-copy audit: any other raw upstream interpolation? ---
print("\n=== error copy frames ===")
for m in re.finditer(r"class=[\"']error[\"'][^`]{0,120}", js):
    s = m.group(0)[:160].replace("\n", "\\n")
    ln = js.count("\n", 0, m.start()) + 1
    print(f"  L{ln}: {s}")

# --- font-size census (literals only; tokens counted separately) ---
fs = re.findall(r"font-size:\s*([\d.]+)px", css)
c = Counter(fs)
print("\n=== CSS literal font-size census ===")
print(" distinct:", len(c), " total decls:", sum(c.values()))
print(" ", sorted(((k, v) for k, v in c.items()), key=lambda kv: float(kv[0])))
print(" font-size:var uses:", len(re.findall(r"font-size:\s*var\(--", css)))

# --- inline style census in JS ---
inline_styles = re.findall(r'style=\\?"', js)
print("\ninline style= occurrences in app.js:", len(inline_styles))
for m in re.finditer(r"style=\\?\"([^\"\\]{0,90})", js):
    s = m.group(1)
    ln = js.count("\n", 0, m.start()) + 1
    print(f"  L{ln}: {s[:90]}")
