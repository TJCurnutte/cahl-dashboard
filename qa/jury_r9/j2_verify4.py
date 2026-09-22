#!/usr/bin/env python3
"""Jury R9 juror2 — part 4: proper census, dark contrast, today payload, ledger tails."""
import os, re, json, time, urllib.request, ssl

J2 = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/j2")
sty = open(os.path.join(J2, "style.css"), errors="replace").read()
app = open(os.path.join(J2, "app.js"), errors="replace").read()

print("== Q. API timing ==")
ctx2 = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
def timed(path, tmo=50):
    req = urllib.request.Request("https://cahl.neural-forge.io" + path, headers=UA)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=tmo, context=ctx2) as r:
            return time.time()-t0, r.read(), r.status
    except Exception as e:
        return time.time()-t0, b"", str(e)[:50]
d1, b1, s1 = timed("/api/today")
print(f"  /api/today: {d1:.2f}s, {len(b1)}B, {s1}")
d2, b2, s2 = timed("/api/players")
print(f"  /api/players: {d2:.2f}s, {len(b2)}B ({len(b2)/1e6:.2f}MB), {s2}")
open(os.path.join(J2, "j2_today.json"), "wb").write(b1)
open(os.path.join(J2, "j2_players_head.json"), "wb").write(b2[:2000])
try:
    tj = json.loads(b1)
    games = tj.get("games") or tj.get("today") or []
    print("  today keys:", list(tj.keys())[:8])
    for g in (games if isinstance(games, list) else [])[:6]:
        print("   game:", json.dumps(g)[:200])
    leagues = tj.get("leagues") or []
    print("  leagues:", len(leagues) if isinstance(leagues, list) else type(leagues).__name__)
except Exception as e:
    print("  today parse:", e)

print("\n== R. dark :root tokens (first definitions) ==")
root = sty[:sty.find("[data-theme")]
tokd = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", root))
for k in ["--bg", "--panel", "--panel-2", "--panel-3", "--inset", "--muted", "--faint",
          "--text-2", "--union", "--union-cta", "--sponsor-gold", "--accent", "--win", "--border"]:
    print(f"  {k}: {tokd.get(k)}")

def lum(hx):
    hx = hx.lstrip("#"); r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b); return 0.2126*r + 0.7152*g + 0.0722*b
def cr(a, b):
    l1, l2 = sorted((lum(a), lum(b)), reverse=True); return (l1+0.05)/(l2+0.05)
print("  DARK contrast:")
for fg, bg, label in [(tokd.get("--muted"), tokd.get("--panel"), "muted/panel"),
                      (tokd.get("--muted"), tokd.get("--panel-3"), "muted/panel-3"),
                      (tokd.get("--faint"), tokd.get("--panel"), "faint/panel"),
                      (tokd.get("--faint"), tokd.get("--bg"), "faint/bg"),
                      (tokd.get("--accent"), tokd.get("--panel"), "accent/panel"),
                      (tokd.get("--accent"), tokd.get("--bg"), "accent/bg"),
                      (tokd.get("--sponsor-gold"), tokd.get("--inset"), "gold/inset"),
                      ("#4a9ae6", tokd.get("--panel"), "rinkhead/panel")]:
    if fg and bg:
        print(f"    {label}: {cr(fg, bg):.2f}")

print("\n== S. token-aware hex census ==")
# allowed = every hex that appears in a --token: #hex definition (any theme)
allowed = set(re.findall(r"--[a-z0-9-]+\s*:\s*(#[0-9a-fA-F]{3,8})\b", sty))
allowed |= set(re.findall(r"--[a-z0-9-]+\s*:\s*(#[0-9a-fA-F]{3,8})\b", open(os.path.join(J2, "landing.css"), errors="replace").read()))
raw_uses = {}
for i, line in enumerate(sty.split("\n"), 1):
    if re.search(r"--[a-z0-9-]+\s*:\s*#", line):
        continue  # token definition line
    for m in re.finditer(r"#[0-9a-fA-F]{6}\b", line):
        h = m.group(0).lower()
        if h not in allowed:
            raw_uses.setdefault(h, []).append(i)
print("  off-token raw uses in style.css:", {k: v[:6] for k, v in raw_uses.items()} or "NONE")

print("\n== T. font-size literal census ==")
sizes = {}
for m in re.finditer(r"font-size:\s*([\d.]+)px", sty):
    sizes[m.group(1)] = sizes.get(m.group(1), 0) + 1
print("  style.css px sizes:", dict(sorted(sizes.items(), key=lambda x: float(x[0]))))
lnd = open(os.path.join(J2, "landing.css"), errors="replace").read()
sizes_l = {}
for m in re.finditer(r"font-size:\s*([\d.]+)px", lnd):
    sizes_l[m.group(1)] = sizes_l.get(m.group(1), 0) + 1
print("  landing.css px sizes:", dict(sorted(sizes_l.items(), key=lambda x: float(x[0]))))
print("  mono tokens:", {k: tokd.get(k) for k in ("--mono-xs", "--mono-sm", "--mono-md")})

print("\n== U. ledger tails ==")
def show(pat, txt, label, cap=6, ctx=130):
    hits = [(txt[:m.start()].count("\n")+1, txt[max(0,m.start()-40):m.start()+ctx].replace("\n", " ")) for m in re.finditer(pat, txt)]
    print(f"[{label}] {len(hits)}")
    for ln, s in hits[:cap]:
        print(f"  L{ln}: …{s!r}")
show(r"recent_result", app, "hasOpp-site", cap=4)
show(r"focus-visible", sty, "focus-visible-parity", cap=8)
show(r"hover:\s*none|pointer:\s*coarse", sty, "coarse-blocks", cap=6)
show(r"R8-2|R9-", sty, "new-block-markers", cap=8)
show(r"R8-2|R9-", app, "new-js-markers", cap=6)
show(r"dataStamp", app, "datastamp-site", cap=2, ctx=400)
show(r"\$\{e\.message\}|\$\{err", app, "raw-msg-census", cap=8)
show(r"min-height:\s*44px", sty, "44px-floors", cap=10)
