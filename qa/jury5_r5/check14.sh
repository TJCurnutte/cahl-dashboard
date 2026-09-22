#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- /api/players cold-ish timing (bounded 55s) ---'
curl -sS -m 55 -o api_players.json -w 'http=%{http_code} time=%{time_total}s size=%{size_download}\n' "https://cahl.neural-forge.io/api/players"
echo '--- lookup timing ---'
curl -sS -m 30 -o api_lookup.json -w 'http=%{http_code} time=%{time_total}s size=%{size_download}\n' "https://cahl.neural-forge.io/api/players/lookup?q=ackley"
head -c 300 api_lookup.json
