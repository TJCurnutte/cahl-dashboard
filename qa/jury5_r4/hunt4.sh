#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r4

echo "=== .hero-card base rule (needs position + overflow for ::before/::after clip) ==="
grep -n "^\.hero-card" style.css | head -6
awk '/^\.hero-card \{/{f=1} f{print NR": "$0} f&&/\}/{exit}' style.css

echo ""
echo "=== .hero-name-wrap position (abs-pos clip fix must survive .hero-card > * override) ==="
grep -n "hero-name-wrap" style.css | head -8
