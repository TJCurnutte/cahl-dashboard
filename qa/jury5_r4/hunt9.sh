#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== teamSelect options built from what? ==="
sed -n '1765,1800p' app.js

echo ""
echo "=== teams filter anywhere? ==="
grep -n "state.teams" app.js | head -12
