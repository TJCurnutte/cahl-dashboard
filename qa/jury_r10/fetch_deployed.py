# J10-1: fetch deployed v70 assets, header-check, save to qa/jury_r10/deployed/
import urllib.request, os, json

OUT = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed"
os.makedirs(OUT, exist_ok=True)

ASSETS = [
    ("index.html", "https://cahl.neural-forge.io/"),
    ("style.css", "https://cahl.neural-forge.io/static/css/style.css?v=70"),
    ("app.js", "https://cahl.neural-forge.io/static/js/app.js?v=70"),
    ("landing.css", "https://cahl.neural-forge.io/static/css/landing.css?v=70"),
    ("version.json", "https://cahl.neural-forge.io/api/version"),
]

req_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome-free-jury"}

for name, url in ASSETS:
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read()
            ctype = r.headers.get("Content-Type", "?")
            clen = r.headers.get("Content-Length", str(len(body)))
            path = os.path.join(OUT, name)
            with open(path, "wb") as f:
                f.write(body)
            print(f"{name}: HTTP {r.status} {ctype} clen={clen} bytes={len(body)}")
    except Exception as e:
        print(f"{name}: ERROR {e}")

# version check
try:
    v = json.load(open(os.path.join(OUT, "version.json")))
    print("version.json:", v)
except Exception as e:
    print("version.json parse error:", e)
