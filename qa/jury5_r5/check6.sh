#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- inline onclick vs delegated split (count + sample) ---'
grep -n "onclick=" app_v55.js | head -12
echo '--- zero-state copy for LEAGUE LEADERS when no data ---'
grep -n -B3 -A12 "pacemakers" app_v55.js | sed -n '1,40p'
