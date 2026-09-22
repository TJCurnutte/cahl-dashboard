#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- full 430px header block ---'
sed -n '1840,1900p' style_v55.css
echo '--- #3a8fe0 usage ---'
grep -n -B2 -A2 "3a8fe0" style_v55.css
echo '--- 2fd08c / ff5d6e usage (state colors?) ---'
grep -n "2fd08c\|ff5d6e" style_v55.css | head -8
