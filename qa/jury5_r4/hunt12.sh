#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== kpalRender full (grouping check) ==="
sed -n '2868,2890p' app.js

echo ""
echo "=== today/scores first 2 games: any date field? ==="
/Users/traviscurnutte/.hermes/hermes-agent/venv/bin/python3 -c "
import json, urllib.request, ssl
d = json.load(urllib.request.urlopen('https://cahl.neural-forge.io/api/today/scores', timeout=60, context=ssl.create_default_context()))
for g in d['games'][:3]:
    print(sorted(g.keys()))
" 2>/dev/null
