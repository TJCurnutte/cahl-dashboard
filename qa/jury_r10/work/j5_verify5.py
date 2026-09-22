#!/usr/bin/env python3
"""R10 juror5 part 5: openPlayer guard, catch-block paint, RM consumers, repo supabase check."""
import re, json, time, urllib.request, gzip, os

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed/"
AL = open(D + "app.js", encoding="utf-8", errors="replace").read().splitlines()
SC = open(D + "style.css", encoding="utf-8", errors="replace").read().splitlines()

print("=== openPlayer def ===")
for i, l in enumerate(AL):
    if "function openPlayer" in l:
        for j in range(i, min(len(AL), i + 22)):
            print(f"{j+1}: {AL[j][:150]}")
        break

print("=== catch/hardFail paint after team fetch ===")
for i, l in enumerate(AL):
    if "hardFail" in l:
        print(f"  L{i+1}: {l.strip()[:140]}")
idx = [i for i, l in enumerate(AL) if "hardFail" in l]
if idx:
    a, b = max(0, idx[-1] - 4), min(len(AL), idx[-1] + 14)
    for j in range(a, b):
        print(f"{j+1}: {AL[j][:150]}")

print("=== res.ok / res.status handling census ===")
for i, l in enumerate(AL):
    if re.search(r"res\.ok|res\.status|\.status\s*>=?\s*5", l):
        print(f"  L{i+1}: {l.strip()[:130]}")

print("=== pal-fade / pal-pop / rise-in / shimmer / fade-in consumers ===")
for kf in ["pal-fade", "pal-pop", "rise-in", "shimmer", "fade-in", "score-flash", "live-breathe", "live-dot-pulse"]:
    users = [(i+1, SC[i].strip()[:100]) for i, l in enumerate(SC) if kf in l and "@keyframes" not in l]
    print(f"  {kf}: {len(users)} uses")
    for n, l in users[:4]: print(f"    L{n}: {l}")

print("=== rm-block class coverage check ===")
rm_text = "\n".join(SC[1215:1222]) + "\n" + "\n".join(SC[1295:1299]) + "\n" + "\n".join(SC[1401:1406])
# each animation-name user class: is the class (or a wildcard/global kill) named in an RM block?
anim_users = []
for i, l in enumerate(SC):
    m = re.search(r"animation:\s*([\w-]+)", l)
    if m and "@keyframes" not in l:
        anim_users.append((i+1, m.group(1), l.strip()[:90]))
print(f"  animation declarations: {len(anim_users)}")
for n, kf, l in anim_users: print(f"    L{n} {kf}: {l}")

print("=== repo supabase check (local source) ===")
for root, dirs, files in os.walk("/Users/traviscurnutte/cahl-dashboard"):
    dirs[:] = [d for d in dirs if d not in ("qa", ".git", "node_modules", "__pycache__")]
    for f in files:
        if f.endswith((".py", ".js", ".md", ".toml", ".txt", ".yml", ".yaml", ".json", ".html", ".css")):
            p = os.path.join(root, f)
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if re.search(r"supabase", t, re.I):
                hits = len(re.findall(r"supabase", t, re.I))
                print(f"  {p}: {hits} refs")
                for i, l in enumerate(t.splitlines()):
                    if re.search(r"supabase", l, re.I):
                        print(f"    L{i+1}: {l.strip()[:130]}")
                        if hits > 40: break

print("=== dead-team + league retry ===")
def fetch(path, timeout=45):
    t0 = time.time()
    req = urllib.request.Request("https://cahl.neural-forge.io" + path, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) JuryR10QAProbe", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            return raw, time.time() - t0, r.status
    except Exception as e:
        return None, time.time() - t0, str(e)
for p in ["/api/team/E25EA9F0-0F26-BD6A-F23ECD21D7F432C8", "/api/league/Sunday%20C%20West"]:
    raw, dt, st = fetch(p, 50)
    print(f"  {p[:60]}  {dt:.2f}s status={st} body={(raw[:200] if raw else None)!r}")
