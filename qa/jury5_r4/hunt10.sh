#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== allTeams population (typeahead source) ==="
sed -n '240,270p' app.js

echo ""
echo "=== players table build: bye filter? ==="
sed -n '2310,2345p' app.js
