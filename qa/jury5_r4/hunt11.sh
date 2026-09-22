#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== palette render (grouping/headers) ==="
grep -n "kpalList\|pal-item\|renderKpal\|kpalRender" app.js | head -10

echo ""
echo "=== raceBadge ==="
grep -n "raceBadge" app.js | head -4
sed -n "$(grep -n 'raceBadge =' app.js | head -1 | cut -d: -f1),+8p" app.js

echo ""
echo "=== today payload shape (first game) ==="
/Users/traviscurnutte/.hermes/hermes-agent/venv/bin/python3 -c "
import json, urllib.request, ssl
d = json.load(urllib.request.urlopen('https://cahl.neural-forge.io/api/today/scores', timeout=60, context=ssl.create_default_context()))
g = d['games']
print('games:', len(g))
print(json.dumps(g[0], indent=1)[:600] if g else 'EMPTY')
" 2>/dev/null || echo "(python probe skipped)"
