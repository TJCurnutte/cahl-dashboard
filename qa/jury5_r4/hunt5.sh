#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== hero markup in app.js ==="
grep -n "hero-name-wrap\|hero-glow\|hero-team\b" app.js | head -8

echo ""
echo "=== livePill wiring (status vs control) ==="
grep -n "livePill\|autoToggle" app.js | head -12
