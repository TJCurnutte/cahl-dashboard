#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- fmtTime impl ---'
grep -n -A8 "function fmtTime" app_v55.js | head -12
echo '--- error/timeout user-facing strings ---'
grep -n "timed out\|Timeout\|failed to\|Failed\|error" app_v55.js | grep -iv "console\|// \|catch (e) { }\|\.error(" | head -15
echo '--- hardcoded stale season/date strings ---'
grep -n "2025\|2024\|season\b" app_v55.js | grep -iv "//" | head -10
echo '--- TBD fallbacks count ---'
grep -c "TBD" app_v55.js
echo '--- onclick= inline handlers (consistency tell) ---'
grep -c "onclick=" app_v55.js
echo '--- esc() usage before innerHTML interpolation of API strings (sample) ---'
grep -n "innerHTML" app_v55.js | wc -l
echo '--- palette empty copy ---'
grep -n "pal-empty\|No matches" app_v55.js | head -3
echo '--- team count / api/teams check ---'
curl -sS -m 30 "https://cahl.neural-forge.io/api/teams" -o api_teams.json; wc -c api_teams.json
