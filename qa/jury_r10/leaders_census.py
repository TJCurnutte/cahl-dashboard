#!/usr/bin/env python3
"""leaders player_id census on live /api/leaders payload."""
import json, urllib.request, gzip

req = urllib.request.Request("https://cahl.neural-forge.io/api/leaders",
                             headers={"User-Agent": "JuryR10QA", "Accept-Encoding": "gzip"})
with urllib.request.urlopen(req, timeout=30) as r:
    raw = r.read()
    if r.headers.get("Content-Encoding", "") == "gzip":
        raw = gzip.decompress(raw)
body = json.loads(raw)
for k, v in body.items():
    if isinstance(v, list):
        nulls = sum(1 for x in v if not x.get("player_id"))
        print(f"leaders.{k}: {len(v)} rows, {nulls} null player_id")
    else:
        print(k, "=", str(v)[:80])
