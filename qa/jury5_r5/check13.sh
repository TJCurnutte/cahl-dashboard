#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- heat row zero-state CSS (min-width fusion bug from R5 v50?) ---'
grep -n -B2 -A8 "\.heat-row\|\.heat-bar\|\.heat-fill" style_v55.css | head -40
echo '--- heat zero guard in app.js ---'
grep -n -B4 -A14 "heat-row" app_v55.js | head -40
echo '--- goal diff empty guard ---'
grep -n "gd-empty" style_v55.css | head -3
