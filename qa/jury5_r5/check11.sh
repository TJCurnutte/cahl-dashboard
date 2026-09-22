#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- league payload keys + standings/season ---'
/Users/traviscurnutte/.hermes/hermes-agent/venv/bin/python3 -m json.tool api_league.json > league_pretty.json 2>/dev/null; head -50 league_pretty.json
grep -o '"standings"' api_league.json | wc -l
grep -o '"season"' api_league.json | wc -l
echo '--- scores game statuses ---'
grep -o '"status":"[^"]*"' api_scores.json
