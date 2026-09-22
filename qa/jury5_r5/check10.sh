#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- league data (Sunday B East) ---'
LEAGUE="9D24B2B45A34B5CAE923A8DAD1BC20A938A35CD3733E115A4DD7FC65626424A674E699EB7CB1D0A36A057220F70A78081722EDE2931A0902EEB476FA4AB09456"
curl -sS -m 60 "https://cahl.neural-forge.io/api/league/$LEAGUE" -o api_league.json
wc -c api_league.json
grep -o "Bye Week" api_league.json | wc -l
head -c 700 api_league.json
printf '\n--- scores endpoint ---\n'
curl -sS -m 45 "https://cahl.neural-forge.io/api/today/scores" -o api_scores.json
wc -c api_scores.json
grep -o "Bye Week\|Team Blue\|Team Red" api_scores.json | sort | uniq -c
head -c 400 api_scores.json
