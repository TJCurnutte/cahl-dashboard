#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== rink-lines CSS block (full) ==="
sed -n '1575,1640p' style.css

echo ""
echo "=== hero markup: where watermark classes get injected ==="
grep -n "hero-card\|hero-mark\|rink" app.js | head -10
