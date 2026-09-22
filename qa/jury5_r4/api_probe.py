#!/usr/bin/env python3
# API probe: data-hygiene tells (Bye Week, vs/scrim rows, TBA/TBD leakage)
import json, urllib.request, ssl

BASE = 'https://cahl.neural-forge.io'
ctx = ssl.create_default_context()

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=60, context=ctx) as r:
            return json.loads(r.read().decode('utf-8', 'replace'))
    except Exception as e:
        return {'__error': str(e)}

bad_terms = ('bye week', 'tba', 'tbd', 'tbd/tba', 'n/a', 'vs', 'scrim')

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

out = {}
for endpoint in ['/api/today/scores', '/api/standings', '/api/leagues']:
    data = get(endpoint)
    hits = scan(data)
    out[endpoint] = {'error': data.get('__error'), 'hits': hits[:15], 'n_hits': len(hits)}
    # shape summary
    if isinstance(data, dict):
        out[endpoint]['keys'] = list(data.keys())[:12]

print(json.dumps(out, indent=1, ensure_ascii=False)[:3000])
