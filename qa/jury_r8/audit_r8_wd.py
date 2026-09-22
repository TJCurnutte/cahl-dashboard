#!/usr/bin/env python3
"""R8 juror3 part 5: watchdog vs api timeout arithmetic, outline contexts, misc."""
import re

R8 = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r8"
js = open(f"{R8}/app_v63.js", encoding="utf-8", errors="replace").read()
css = open(f"{R8}/style_v63.css", encoding="utf-8", errors="replace").read()

print("### watchdog / timeout values ###")
for m in re.finditer(r'setTimeout\([^;]{0,80}?(\d{3,5})\)', js):
    pass
# find wd40 assignment
for m in re.finditer(r'(?:const|let|var)?\s*wd\w*\s*=\s*setTimeout\(([^;]{0,120})', js):
    print("WD:", m.group(0)[:180])
# all numeric setTimeout/AbortController timeouts
print("setTimeout values:", sorted(set(int(x) for x in re.findall(r'setTimeout\([^)]*?,\s*(\d{3,5})\s*\)', js))))
print("AbortSignal.timeout / abort values:", re.findall(r'AbortController[\s\S]{0,200}', js)[:1])
for m in re.finditer(r'abort[^;]{0,60}(\d{4,5})', js):
    print("abort-related:", m.group(0)[:120])
print("API_TIMEOUT-ish consts:", re.findall(r'(?:TIMEOUT|Deadline|DEADLINE|_MS)\s*=\s*[\d.e_]+', js))

print("\n### outline:none contexts ###")
for m in re.finditer(r'[^\n]*outline:\s*none[^\n]*', css):
    print(m.group(0).strip()[:170])

print("\n### focus-visible full selectors ###")
for m in re.finditer(r'[^\n{}]*focus-visible[^\n{]*', css):
    print(m.group(0).strip()[:170])

print("\n### api() function head ###")
m = re.search(r'(?:async\s+)?function\s+api\s*\([^)]*\)\s*\{[\s\S]{0,900}', js)
print(m.group(0)[:900] if m else "api() not found by that signature")

print("\n### cold-index + retry UX strings ###")
for s in ['Index cold', 'timed out', 'data-retrying', 'Couldn\\u2019t load']:
    idx = js.find(s.replace('\\u2019', '\u2019')) if '\\u' in s else js.find(s)
    print(f"{s!r}: found={idx != -1}")
