import urllib.request, time, json

def get(url, timeout=12):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "cahl-jury-r4/1.0", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return round((time.time()-t0)*1000), r.status, len(body), body
    except Exception as e:
        return round((time.time()-t0)*1000), type(e).__name__, 0, b""

# 1) app.js source for static audit
ms, st, ln, body = get("https://cahl.neural-forge.io/static/js/app.js?v=54")
print(f"app.js: {ms}ms status={st} bytes={ln}")
if body:
    with open("/Users/traviscurnutte/cahl-dashboard/qa/r4_j4_app_v54.js", "wb") as f:
        f.write(body)

# 2) index page (single shot)
for path in ["/", "/api/state", "/api/league", "/api/team", "/api/players", "/api/analytics"]:
    ms, st, ln, _ = get("https://cahl.neural-forge.io" + path)
    print(f"{path}: {ms}ms status={st} bytes={ln}")
