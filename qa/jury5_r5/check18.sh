#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- index.html body structure (nav/tabbar/footer) ---'
sed -n '95,131p' index_v55.html
echo '--- fixed bottom nav CSS? ---'
grep -n "position: *fixed" style_v55.css | head -8
