#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- autoToggle state feedback (body class or aria) in app.js ---'
grep -n "auto\b\|state\.auto\|checked" app_v55.js | head -15
echo '--- CSS for auto-on state (body.auto / label checked) ---'
grep -n "body\.auto\|\.live-pill:has\|livePill\." style_v55.css | head -5
echo '--- TODAY tab render: how are zero games handled ---'
grep -n -A8 "board-howto" app_v55.js | head -30
echo '--- NEXT GAMES / schedule on today when empty ---'
grep -n "No games\|no games\|empty-state\|Empty" app_v55.js | head -10
