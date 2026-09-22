#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- TABS / TAB_HASH / hash routing ---'
grep -n "TABS\s*=\|TAB_HASH\|hashchange" app_v55.js | head -8
echo '--- palette Pages entries ---'
grep -n -B2 -A8 "kind: 'page'\|pages =" app_v55.js | head -30
echo '--- today cols head labels ---'
grep -n "today-cols-head" app_v55.js style_v55.css | head -4
grep -n -A6 "todayColsHead\|cols-head" app_v55.js | head -20
echo '--- Bye Week filter at ingest? ---'
grep -n -i "bye" app_v55.js | head -8
echo '--- where JS_VERSION badge displays ---'
grep -n "JS_VERSION" app_v55.js
echo '--- standings api ---'
curl -sS -m 30 "https://cahl.neural-forge.io/api/standings" -o api_standings.json; wc -c api_standings.json
grep -o "Bye Week" api_standings.json | wc -l
