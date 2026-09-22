#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- gameLiveState / isLiveGame impl (false-LIVE guard) ---'
grep -n -A22 "function gameLiveState" app_v55.js | head -30
grep -n -A10 "function isLiveGame" app_v55.js | head -12
echo '--- footer credit / data-note mobile positioning ---'
grep -n -B2 -A8 "\.credit" style_v55.css | head -30
echo '--- data-note position ---'
grep -n -A6 "\.data-note" style_v55.css | head -10
