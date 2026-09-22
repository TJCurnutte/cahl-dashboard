import urllib.request, time, concurrent.futures, json

BASE = "https://cahl.neural-forge.io"

def get(path, timeout=15, bust=False):
    t0 = time.time()
    url = BASE + path + ("?_b=" + str(time.time()) if bust and "?" not in path else "")
    req = urllib.request.Request(url, headers={"User-Agent": "cahl-jury-r4/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return round((time.time()-t0)*1000), r.status, len(body), body
    except Exception as e:
        return round((time.time()-t0)*1000), type(e).__name__, 0, b""

# warm look (already hit / once) then a small concurrent burst of 4 core APIs
paths = ["/api/today", "/api/teams", "/api/state?league=1", "/api/schedule"]
t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    results = list(ex.map(lambda p: get(p, bust=True), paths))
burst_total = round((time.time()-t0)*1000)
for p, (ms, st, ln, _) in zip(paths, results):
    print(f"BURST {p}: {ms}ms status={st} bytes={ln}")
print(f"BURST wall total: {burst_total}ms")

# deployed css + index (for motion/reduced-motion + palette CSS audit)
for path in ["/static/css/style.css?v=54", "/?v=54"]:
    ms, st, ln, body = get(path, timeout=15)
    print(f"{path}: {ms}ms status={st} bytes={ln}")
    if body and st == 200:
        fn = "/Users/traviscurnutte/cahl-dashboard/qa/r4_j4_style_v54.css" if "style" in path else "/Users/traviscurnutte/cahl-dashboard/qa/r4_j4_index_v54.html"
        with open(fn, "wb") as f:
            f.write(body)
