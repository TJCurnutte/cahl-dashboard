#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- autoToggle markup in index.html ---'
grep -n -A3 -B3 'autoToggle' index_v55.html
echo '--- autoToggle wiring in app.js (context) ---'
grep -n -B2 -A6 "autoToggle" app_v55.js | head -40
echo '--- live-pill / status pill CSS ---'
grep -n "live-pill\|live-badge\|status-chip" style_v55.css | head -10
echo '--- palette groups labels ---'
grep -n "pal-grp" style_v55.css | head -3
echo '--- GOAL DIFF / heat viz classes defined? ---'
grep -c "heat-" style_v55.css
grep -c "gd-strip\|gd-dot" style_v55.css
echo '--- tnx/font tnum ---'
grep -c "font-variant-numeric" style_v55.css
echo '--- prefers-reduced-motion ---'
grep -c "prefers-reduced-motion" style_v55.css
