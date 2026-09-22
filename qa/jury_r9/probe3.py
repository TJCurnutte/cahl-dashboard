#!/usr/bin/env python3
"""R9 juror5 part 9: dead-team live probe, players headers, leaderSection callers, lockup alpha, landing.css, censuses."""
import os, re, json, zlib, struct, urllib.request, ssl, time

OUT = os.path.expanduser("~/cahl-dashboard/qa/jury_r9/deployed")
app = open(os.path.join(OUT, "app.js"), "r", errors="replace").read()
sty = open(os.path.join(OUT, "style.css"), "r", errors="replace").read()
lnd = open(os.path.join(OUT, "landing.css"), "r", errors="replace").read()
BASE = "https://cahl.neural-forge.io"
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}

def get(path, timeout=55):
    req = urllib.request.Request(BASE + path, headers=UA)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read(), r.status, time.time() - t0, dict(r.headers)

# leaderSection callers
print("== leaderSection callers ==")
for m in re.finditer(r"leaderSection\(", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  L{ln}: {app[m.start():m.start()+110].split(chr(10))[0][:110]}")

# dead team probe (dashed-uuid stale format, like the v65 repro)
print("\n== /api/team dead-id probe ==")
try:
    body, st, dt, hd = get("/api/team/AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE", timeout=55)
    print(f"  status {st} {dt:.2f}s bytes={len(body)}")
    print("  body:", body.decode("utf-8", "replace")[:400])
except Exception as e:
    print("  ERR:", str(e)[:200])

# players headers (gzip?)
print("\n== /api/players headers (timing skipped; reuse earlier 35.4s single-shot) ==")
try:
    req = urllib.request.Request(BASE + "/api/players", headers=UA)
    with urllib.request.urlopen(req, timeout=58, context=ctx) as r:
        raw = r.read()
        print("  Content-Encoding:", r.headers.get("Content-Encoding"), "| raw wire bytes:", len(raw))
except Exception as e:
    print("  ERR:", str(e)[:200])

# upright-lockup.png fetch + alpha decode
print("\n== upright-lockup.png ==")
try:
    body, st, dt, hd = get("/static/img/upright-lockup.png")
    open(os.path.join(OUT, "upright-lockup.png"), "wb").write(body)
    print(f"  {st} {dt:.2f}s bytes={len(body)} type={hd.get('Content-Type')}")
    # PNG: parse IHDR + IDAT, unfilter, count alpha
    sig = body[:8]
    pos = 8
    w = h = bd = ct = None
    idat = b""
    while pos < len(body):
        ln = struct.unpack(">I", body[pos:pos+4])[0]
        typ = body[pos+4:pos+8]
        data = body[pos+8:pos+8+ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
        elif typ == b"IDAT":
            idat += data
        pos += 12 + ln
    print(f"  IHDR {w}x{h} bitdepth={bd} colortype={ct} (6=RGBA)")
    raw2 = zlib.decompress(idat)
    ch = 4 if ct == 6 else (3 if ct == 2 else 1)
    stride = w * ch
    # unfilter (paeth etc.)
    out = bytearray()
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw2[p]; p += 1
        line = bytearray(raw2[p:p+stride]); p += stride
        if f == 1:
            for i in range(ch, stride): line[i] = (line[i] + line[i-ch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                b = prev[i]
                c = prev[i-ch] if i >= ch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out += line
        prev = line
    if ch == 4:
        n = w * h
        alphas = out[3::4]
        transparent = sum(1 for a in alphas if a == 0)
        opaque = sum(1 for a in alphas if a == 255)
        partial = n - transparent - opaque
        print(f"  alpha: {transparent/n:.1%} transparent, {opaque/n:.1%} opaque, {partial/n:.1%} partial")
except Exception as e:
    print("  ERR:", str(e)[:200])

# landing.css structure
print("\n== landing.css census ==")
print("  bytes:", len(lnd), "lines:", lnd.count("\n")+1)
print("  backdrop-filter:", lnd.count("backdrop-filter"))
print("  @keyframes:", re.findall(r"@keyframes\s+([\w-]+)", lnd))
print("  prefers-reduced-motion blocks:", lnd.count("prefers-reduced-motion"))
print("  var(--*) uses:", len(re.findall(r"var\(--", lnd)))
print("  font-size literals:", sorted(set(re.findall(r"font-size:\s*([\d.]+)px", lnd))))
print("  @media:", re.findall(r"@media[^{]+", lnd))

# style.css standing censuses
print("\n== style.css census ==")
print("  bytes:", len(sty))
print("  @keyframes:", re.findall(r"@keyframes\s+([\w-]+)", sty))
print("  prefers-reduced-motion:", sty.count("prefers-reduced-motion"))
print("  backdrop-filter:", len(re.findall(r"backdrop-filter", sty)))
print("  hero-glow-breathe refs:", len(re.findall(r"hero-glow-breathe", sty)))
print("  font-size px literals (distinct):", sorted(set(re.findall(r"font-size:\s*([\d.]+)px", sty))))
# inline style census in app.js
inline = re.findall(r"style=\\?\"[^\"`]*\\?\"", app)
print("\n== app.js inline style= count:", len(inline))
for m in re.finditer(r"<h3[^>]*style=[^>]*>", app):
    ln = app[:m.start()].count("\n") + 1
    print(f"  inline h3 L{ln}: {m.group(0)[:120]}")
# onclick census
print("  onclick= count:", len(re.findall(r"onclick=", app)))
