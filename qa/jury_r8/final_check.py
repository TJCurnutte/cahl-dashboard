#!/usr/bin/env python3
"""R8 j2 final: asset HEAD checks + weighted total."""
import urllib.request, json

def head(path):
    try:
        req = urllib.request.Request("https://cahl.neural-forge.io" + path, method="HEAD",
                                     headers={"User-Agent": "cahl-jury-r8-j2"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return f"{r.status} {r.headers.get('Content-Type')} {r.headers.get('Content-Length')}B"
    except Exception as e:
        return f"FAIL {e!r}"

for p in ["/static/img/cahl-logo-hd.png", "/static/img/upright-crown.png",
          "/static/css/landing.css?v=63", "/favicon.ico"]:
    print(f"{p}: {head(p)}")

scores = {"identity": 9.7, "type": 9.7, "color": 9.7, "layout": 9.7, "density": 9.4,
          "interaction": 9.6, "motion": 9.7, "depth": 9.7, "consistency": 9.5, "mobile": 9.7}
weights = {"identity": .12, "type": .12, "color": .10, "layout": .12, "density": .12,
           "interaction": .10, "motion": .08, "depth": .08, "consistency": .08, "mobile": .08}
total = sum(scores[k] * weights[k] for k in scores)
print("\nweighted components:")
for k in scores:
    print(f"  {k}: {scores[k]} x {weights[k]} = {scores[k]*weights[k]:.3f}")
print(f"RAW TOTAL = {total:.4f} -> {round(total,1)}")
print(f"post-fix est = {total + 0.024 + 0.008 + 0.010:.4f}")
