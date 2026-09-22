#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- em-dashes NOT in comments (user-facing strings) ---'
grep -n $'\xe2\x80\x94' app_v55.js | grep -v ':[0-9]*: *//' | head -20
echo '--- LEAGUE LEADERS context ---'
grep -n "LEAGUE LEADERS" app_v55.js
echo '--- dataStamp in index.html ---'
grep -n 'dataStamp\|UPDATED' index_v55.html
echo '--- vs @ / next_game in app.js ---'
grep -n 'vs @' app_v55.js | head -5
grep -n 'next_game\|nextGame' app_v55.js | head -10
echo '--- Bye/Team Blue in style.css ---'
grep -n 'Bye Week\|Team Blue\|Team Red' style_v55.css | head -5
