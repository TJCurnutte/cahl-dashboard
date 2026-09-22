#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== client-side Bye Week handling ==="
grep -n -i "bye" app.js | head -12

echo ""
echo "=== team select / dropdown render ==="
grep -n "state.teams.map\|teamSelect\|id=\"teamSelect\"\|teamPicker" app.js | head -8
