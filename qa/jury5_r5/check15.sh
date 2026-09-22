#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- off-palette hexes in CSS (non-CBJ set) ---'
grep -oE '#[0-9a-fA-F]{6}\b' style_v55.css | sort | uniq -c | sort -rn | head -25
echo '--- generic api() timeout/AbortController ---'
grep -n -A10 "async function api(" app_v55.js | head -14
echo '--- mobile <=430 header compression: min-w/h 0 regression ---'
grep -n -B6 -A20 "max-width: *430px" style_v55.css | grep -n "themeToggle\|refreshBtn\|min-width: *0\|min-height: *0" | head -10
echo '--- tap-highlight ---'
grep -c "tap-highlight" style_v55.css
echo '--- sticky thead + zebra ---'
grep -c "position: *sticky" style_v55.css
grep -cn "nth-child.*odd\|nth-child.*even" style_v55.css
echo '--- tl-game otl 8px residue ---'
grep -n "tl-game" style_v55.css | head -6
