#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== command palette groups/sections ==="
grep -n "pal-group\|palGroup\|pal-head\|group:" app.js | head -12

echo ""
echo "=== heat-track / heat-bar (zero-state anti-fuse) ==="
awk '/^\.heat-track \{/,/\}/' style.css
awk '/^\.heat-bar \{/,/\}/' style.css
awk '/^\.heat-bar--lead/,/\}/' style.css

echo ""
echo "=== sb-live pulse (live grammar) ==="
grep -n "sb-live" style.css | head -6
