#!/usr/bin/env python3
"""Fetch gate HD logo; verify crown PNG alpha; inspect header SVG."""
import urllib.request, struct, pathlib, zlib

Q = pathlib.Path.home() / "cahl-dashboard/qa/jury_r8"

def fetch(name, path):
    with urllib.request.urlopen("https://cahl.neural-forge.io" + path, timeout=30) as r:
        b = r.read()
    (Q / name).write_bytes(b)
    print(name, r.status, f"{len(b):,}B")

fetch("cahl-logo-hd.png", "/static/img/cahl-logo-hd.png")

def png_info(path):
    data = (Q / path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a png"
    pos, idat, w = 8, b"", None
    color_type = bit_depth = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos+4])[0]
        typ = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]
        if typ == b"IHDR":
            w, h, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"PLTE":
            pass
        pos += 12 + ln
    print(f"{path}: {w}x{h} depth={bit_depth} colortype={color_type} (6=RGBA,2=RGB,3=palette)")
    if color_type == 6:
        raw = zlib.decompress(idat)
        stride = w * 4 + 1
        # unfilter enough rows to sample alpha stats (sample every 40th px)
        import collections
        prev = bytearray(w * 4)
        alpha_hist = collections.Counter()
        out = bytearray()
        pos2 = 0
        rows = h
        cur = bytearray(w * 4)
        for y in range(rows):
            f = raw[pos2]; pos2 += 1
            line = bytearray(raw[pos2:pos2 + w * 4]); pos2 += w * 4
            bpp = 4
            if f == 0: pass
            elif f == 1:
                for i in range(bpp, len(line)): line[i] = (line[i] + line[i - bpp]) & 255
            elif f == 2:
                for i in range(len(line)): line[i] = (line[i] + prev[i]) & 255
            elif f == 3:
                for i in range(len(line)):
                    a = line[i - bpp] if i >= bpp else 0
                    line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
            elif f == 4:
                for i in range(len(line)):
                    a = line[i - bpp] if i >= bpp else 0
                    b_ = prev[i]; c = prev[i - bpp] if i >= bpp else 0
                    p = a + b_ - c
                    pa, pb, pc = abs(p - a), abs(p - b_), abs(p - c)
                    pr = a if (pa <= pb and pa <= pc) else (b_ if pb <= pc else c)
                    line[i] = (line[i] + pr) & 255
            prev = line
            if y % 13 == 0:
                for x in range(0, w * 4, 4 * 7):
                    alpha_hist[line[x + 3]] += 1
        opaque = sum(v for k, v in alpha_hist.items() if k == 255)
        transparent = sum(v for k, v in alpha_hist.items() if k == 0)
        total = sum(alpha_hist.values())
        print(f"  alpha sample: {opaque/total:.1%} fully opaque, {transparent/total:.1%} fully transparent, rest={total-opaque-transparent}")
        return w, h, color_type
    return w, h, color_type

png_info("upright-crown.png")
png_info("cahl-logo-hd.png")
png_info("cahl-icon-192.png")

svg = (Q / "cahl-logo.svg").read_text(encoding="utf-8", errors="replace")
print("\ncahl-logo.svg head:", svg[:600].replace("\n", " | "))
print("svg has <text>:", "<text" in svg, "| viewBox:", svg[svg.find("viewBox"):svg.find("viewBox")+30])
