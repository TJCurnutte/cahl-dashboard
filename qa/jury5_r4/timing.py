#!/usr/bin/env python3
# Timing check on the endpoints that historically beat the app timeout (cold-start risk)
import json, time, urllib.request, ssl, concurrent.futures

BASE = 'https://cahl.neural-forge.io'
ctx = ssl.create_default_context()

def timed(path):
    t0 = time.time()
    try:
        with urllib.request.urlopen(BASE + path, timeout=90, context=ctx) as r:
            n = len(r.read())
        return path, round(time.time() - t0, 2), n
    except Exception as e:
        return path, round(time.time() - t0, 2), f'ERR {e}'

for p in ['/api/players', '/api/teams', '/api/leaders', '/api/today']:
    t0 = time.time()
    print(timed(p))

# one parallel burst of 6 lookups to test single-flight/serialization
print()
print('burst of 6 concurrent /api/players/lookup?q=pat:')
def lookup(i):
    t0 = time.time()
    try:
        with urllib.request.urlopen(BASE + '/api/players/lookup?q=pat', timeout=120, context=ctx) as r:
            r.read()
        return round(time.time() - t0, 2)
    except Exception as e:
        return f'ERR {e}'
with concurrent.futures.ThreadPoolExecutor(6) as ex:
    print(sorted(ex.map(lookup, range(6))))
