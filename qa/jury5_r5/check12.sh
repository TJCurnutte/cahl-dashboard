#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- standings section of league payload (Bye check + zero-state) ---'
/Users/traviscurnutte/.hermes/hermes-agent/venv/bin/python3 - <<'EOF'
import json
d=json.load(open('api_league.json'))
print('keys:', list(d.keys()))
st=d.get('standings') or []
print('standings rows:', len(st))
for r in st[:6]:
    print({k:r.get(k) for k in ('team','gp','w','l','otl','pts','team_id')})
s=json.dumps(d)
for pat in ['Bye Week','Team Blue','Team Red','vs @']:
    print(repr(pat), s.count(pat))
print('season:', d.get('season'))
EOF
