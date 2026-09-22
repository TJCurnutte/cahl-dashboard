#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== self-heal reload block (must NOT reload every boot) ==="
grep -n "vserverheal" app.js | head -3
awk '/vserverheal/{c=NR} NR>=c-8 && NR<=c+8' app.js | head -20

echo ""
echo "=== Season Heat bar CSS (anti-fuse: min-width, gap) ==="
grep -n "heat-\|gd-" style.css | head -25

echo ""
echo "=== mobile today-row card stack ==="
grep -n "480px\|430px\|max-600" style.css | head -12

echo ""
echo "=== tabular-nums coverage ==="
grep -n "font-variant-numeric\|tabular" style.css | head -12

echo ""
echo "=== zebra / sticky header ==="
grep -n "nth-child(odd)\|nth-child(even)\|position: *sticky" style.css | head -10

echo ""
echo "=== reduced-motion ==="
grep -n "prefers-reduced-motion" style.css | head -5
