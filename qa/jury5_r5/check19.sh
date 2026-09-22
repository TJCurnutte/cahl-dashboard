#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- nav CSS (bottom bar on mobile?) ---'
grep -n -B3 -A14 "^nav {" style_v55.css | head -30
grep -n -B2 -A12 "nav a {" style_v55.css | head -20
echo '--- nav media rules ---'
grep -n "nav {" style_v55.css
echo '--- aria-current styling ---'
grep -n "aria-current" style_v55.css | head -3
