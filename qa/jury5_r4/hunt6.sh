#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== hero-glow CSS exists? ==="
grep -n "hero-glow" style.css

echo ""
echo "=== \$auto usage in app.js (is the livePill checkbox wired?) ==="
grep -n '\$auto' app.js

echo ""
echo "=== livePill click/change handlers ==="
grep -n "livePill\|autoToggle\|live-pill" app.js style.css | head -15
