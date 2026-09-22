#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- endpoints app.js calls ---'
grep -o "/api/[a-z_/]*" app_v55.js | sort | uniq -c | sort -rn
