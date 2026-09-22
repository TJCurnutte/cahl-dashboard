#!/bin/bash
# Juror 5/5 R4 — new-tell hunt in deployed v54 assets
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== fmtTime definition ==="
awk '/function fmtTime/,/^    }/' app.js | head -20

echo ""
echo "=== rink-lines watermark (v54 signature) ==="
grep -c "rink-lines" style.css app.js
grep -n "rink-lines" style.css | head -8

echo ""
echo "=== off-palette hexes in CSS (link-blue/amber family) ==="
grep -n "2a7fd4\|42, 127, 212\|42,127,212\|f59e0b\|eab308\|amber" style.css | head

echo ""
echo "=== debug cruft in app.js ==="
grep -n "console\.log\|debugger;\|TODO\|FIXME\|lorem" app.js | head -5
echo "count: $(grep -c 'console\.log\|debugger;\|TODO\|FIXME\|lorem' app.js)"

echo ""
echo "=== hardcoded localhost / placeholder text ==="
grep -n "localhost\|127\.0\.0\.1\|example\.com\|placeholder-key\|YOUR_API" app.js style.css | head

echo ""
echo "=== dataStamp render (UPDATED line) ==="
awk '/dataStamp/,0' app.js | head -12

echo ""
echo "=== board-howto copy ==="
grep -n "board-howto" app.js | head -4
