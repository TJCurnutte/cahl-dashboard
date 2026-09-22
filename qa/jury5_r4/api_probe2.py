#!/usr/bin/env python3
# Find the real endpoint names in app.js, then probe them for data-hygiene tells.
import re, json, urllib.request, ssl

src = open('/Users/traviscurnutte/cahl-dashboard/qa/jury5_r4/app.js').read()
paths = sorted(set(re.findall(r"[\'\`](/api/[a-z0-9_\-/{}$\.]*)", src)))
print('endpoints referenced in app.js:')
for p in paths:
    print('  ', p)

BASE = 'https://cahl.neural-forge.io'
ctx = ssl.create_default_context()

def get(path, timeout=90):
    try:
        with urllib.request.urlopen(BASE + path, timeout=timeout, context=ctx) as r:
            return json.loads(r.read().decode('utf-8', 'replace'))
    except Exception as e:
        return {'__error': str(e)}

bad_terms = ('bye week', 'tba', 'tbd', 'n/a', 'vs', 'scrim')

def scan(obj, path='$'):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += scan(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += scan(v, f'{path}[{i}]')
    elif isinstance(obj, str):
        low = obj.strip().lower()
        if low in bad_terms or 'bye week' in low:
            hits.append((path, obj.strip()[:80]))
    return hits

print()
results = {}
for p in paths:
    if '{}' in p or '$' in p:
        continue  # templated, needs ids
    d = get(p)
    if isinstance(d, dict) and '__error' in d:
        results[p] = d
        continue
    hits = scan(d)
    results[p] = {'hits': hits[:10], 'n_hits': len(hits)}

print(json.dumps(results, indent=1, ensure_ascii=False)[:4000])
