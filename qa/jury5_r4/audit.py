# Byte-precise audit of deployed CAHL v54 app.js — juror 5/5 (credibility lens)
import re
from collections import Counter

data = open('app.js', 'rb').read()
print('== BYTE-LEVEL ESCAPE AUDIT (app.js) ==')
for pat, label in [
    (rb'\\{2,}u2026', 'DOUBLE-backslash u2026 (renders literal "\\u2026")'),
    (rb'\\{1}u2026', 'single-backslash u2026 (correct JS escape -> ellipsis)'),
    (rb'\\{2,}u[0-9a-f]{4}', 'DOUBLE-backslash any uXXXX escape'),
    (rb'\\{3,}u[0-9a-f]{4}', 'TRIPLE+ backslash any uXXXX escape'),
]:
    m = re.findall(pat, data)
    print(f'{label}: {len(m)}')

print()
print('== SINGLE-BACKSLASH ESCAPE INVENTORY (should all be intentional JS escapes) ==')
m = re.findall(rb'\\u[0-9a-fA-F]{4}', data)
print(Counter(m))

print()
print('== LITERAL BACKSLASH IN USER-VISIBLE STRINGS (rendered text with backslash) ==')
# strings like '<div class="typeahead-item muted">Searching\u2026</div>' are fine (JS escape);
# flag any \'\\u\' that appears inside HTML text nodes with an ODD backslash count >= 3
for i, line in enumerate(data.split(b'\n'), 1):
    for m in re.finditer(rb'(\\+u[0-9a-fA-F]{4})', line):
        if len(m.group(1)) >= 4:  # 4+ backslashes in source = 2+ literal
            print(f'L{i}: {m.group(0)} in: {line[max(0,m.start()-40):m.end()+40][:100]}')

print()
print('== "vs" WORD INVENTORY (app.js) ==')
for i, line in enumerate(data.split(b'\n'), 1):
    if re.search(rb"[>'\"]vs[<'\"]", line):
        print(f'L{i}: {line.strip()[:160].decode("utf-8", "replace")}')

print()
print('== VERSION SYNC ==')
html = open('index.html', 'rb').read()
for m in re.finditer(rb'(JS_VERSION|APP_VERSION)[^\n]{0,60}', data):
    print('app.js :', m.group(0))
for m in re.finditer(rb'(JS_VERSION|APP_VERSION|\?v=)[^\n<]{0,40}', html):
    print('index  :', m.group(0))
