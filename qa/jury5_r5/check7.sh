#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- style.css version marker / appended blocks ---'
grep -n "v55\|V55\|R5\|FIX PASS" style_v55.css | tail -12
echo '--- v52-era appended mono overlays still present (dead tokens) ---'
grep -c "mono-md\|mono-sm\|mono-xs" style_v55.css
grep -n "font-family: *var(--mono)" style_v55.css | wc -l
grep -n "JetBrains" style_v55.css | wc -l
echo '--- hardcoded mono px sizes remaining ---'
grep -n "JetBrains Mono" style_v55.css | wc -l
echo '--- em-dash in CSS content strings (user-visible) ---'
LC_ALL=C grep -c $'\xe2\x80\x94' style_v55.css
echo '--- three real em-dash render sites in app.js ---'
grep -n "u2014" app_v55.js
echo '--- t-score uses display font? ---'
grep -n -A4 "\.t-score" style_v55.css | head -14
echo '--- scoreboard num font ---'
grep -n -A4 "\.sb-num" style_v55.css | head -8
