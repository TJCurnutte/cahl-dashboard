# J10-1 static census: type scale, tokens, ledger, contrast math for v70
import re, os

D = "/Users/traviscurnutte/cahl-dashboard/qa/jury_r10/deployed"
style = open(os.path.join(D, "style.css")).read()
land = open(os.path.join(D, "landing.css")).read()
app = open(os.path.join(D, "app.js")).read()
idx = open(os.path.join(D, "index.html")).read()

def lines(s): return s.split("\n")

def find_line(s, pat):
    for i, l in enumerate(lines(s), 1):
        if re.search(pat, l): yield i, l.strip()

print("=== 1. LANDING.CSS FONT-SIZE CENSUS ===")
fs = re.findall(r'font-size:\s*([^;]+);', land)
from collections import Counter
c = Counter(fs)
for v, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"  {n}x  font-size: {v}")
offscale = [v for v in c if 'var(' not in v and re.search(r'\b(11|12|12\.5|13\.5|15|17|19|22|24|27|32|44)px', v)]
print("  off-scale (brief says only 13/14/16/20/26/30/34 allowed):", offscale or "NONE")

print("\n=== 2. LANDING.CSS RAW-HEX VAR FALLBACKS ===")
fb = re.findall(r'var\(--[a-z0-9-]+,\s*#[0-9a-fA-F]{3,8}\)', land)
print(" ", fb or "NONE — all fallbacks dropped")

print("\n=== 3. LANDING.CSS backdrop-filter census ===")
print("  landing:", len(re.findall(r'backdrop-filter', land)))
print("  style.css:", len(re.findall(r'backdrop-filter', style)))

print("\n=== 4. STYLE.CSS font-size literal census (px only) ===")
fs2 = re.findall(r'font-size:\s*([\d.]+)px', style)
c2 = Counter(fs2)
print("  ", dict(sorted(c2.items(), key=lambda kv: float(kv[0]))))
print("   total literals:", sum(c2.values()), " distinct:", len(c2))
pt = re.findall(r'font-size:\s*([\d.]+)pt', style)
print("   pt rules:", pt)

print("\n=== 5. TOKENS: union-hover / union-cta / mono scale / sponsor-gold / union ===")
for tok in ['--union-hover', '--union-cta', '--mono-xs', '--mono-sm', '--mono-md', '--sponsor-gold', '--union:', '--union-deep']:
    for i, l in find_line(style, re.escape(tok)):
        print(f"  style.css:{i}: {l[:110]}")

print("\n=== 6. palette focus-within cue + context ===")
for i, l in find_line(style, r'focus-within'):
    print(f"  style.css:{i}: {l[:130]}")

print("\n=== 7. rink-head rules (dup check) ===")
for i, l in find_line(style, r'rink-head'):
    print(f"  style.css:{i}: {l[:120]}")

print("\n=== 8. STANDING LEDGER greps ===")
print("  tnum count style.css:", len(re.findall(r'font-variant-numeric:\s*tabular-nums', style)))
print("  zebra (nth-child) count:", len(re.findall(r'nth-child', style)))
print("  position:sticky count:", len(re.findall(r'position:\s*sticky', style)))
print("  prefers-reduced-motion blocks:", len(re.findall(r'prefers-reduced-motion', style)), "style /", len(re.findall(r'prefers-reduced-motion', land)), "landing")
print("  min-height:\\s*0 inside any @media (release gate):",
      len(re.findall(r'@media[^{]*\{[^@]*?min-height:\s*0', style)))
print("  min-width:\\s*0 inside any @media:",
      len(re.findall(r'@media[^{]*\{[^@]*?min-width:\s*0', style)))
print("  44px floors:", len(re.findall(r'min-height:\s*4[48]px', style)))
print("  app.js font-size literals:", len(re.findall(r'font-size:\s*[\d.]+px', app)))
print("  app.js esc( uses:", len(re.findall(r'esc\(', app)))
print("  app.js RAW ${data.error}:", len(re.findall(r'\$\{data\.error\}', app)), " RAW ${e.message}:", len(re.findall(r'\$\{e\.message\}', app)))
print("  concat(finals):", 'concat(finals)' in app)
print("  upright-crown refs (app+idx+css):", (app+idx+style+land).count('upright-crown'))
print("  upright-lockup refs (app+idx):", (app+idx).count('upright-lockup'))
print("  AbortController:", 'AbortController' in app, " JS_VERSION:", re.findall(r'const JS_VERSION = (\d+)', app))
print("  index.html ?v= refs:", re.findall(r'\?v=(\d+)', idx))
print("  Saira weights in font href:", re.findall(r'family=Saira[^&\'"]*', idx))
print("  union-hover uses in css (should consume new token):", len(re.findall(r'var\(--union-hover\)', style+land)))

print("\n=== 9. WCAG CONTRAST ===")
def lum(hx):
    hx = hx.lstrip('#')
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)

pairs = [
    ("NEW hover #2b71c4 vs white label", "2b71c4", "ffffff"),
    ("idle CTA #1f6cb8 vs white", "1f6cb8", "ffffff"),
    ("old hover #3a8fe0 vs white (dead)", "3a8fe0", "ffffff"),
    ("sponsor-gold dark #b8925e vs panel #0e1420", "b8925e", "0e1420"),
    ("sponsor-gold light #7a5c2e vs white", "7a5c2e", "ffffff"),
    ("accent dark #ef3d54 vs panel #0e1420", "ef3d54", "0e1420"),
    ("faint dark #7d92ad vs panel #0e1420", "7d92ad", "0e1420"),
    ("faint light #5d6b80 vs white", "5d6b80", "ffffff"),
    ("muted dark vs panel", "9fb0c7", "0e1420"),
    ("union dark #2a7fd4 vs panel (focus ring)", "2a7fd4", "0e1420"),
    ("union light #002654 vs white (focus ring)", "002654", "ffffff"),
    ("text dark vs bg", "e8eef7", "070b12"),
]
for name, a, b in pairs:
    print(f"  {name}: {cr(a,b):.2f}:1")

print("\n=== 10. app.js leader-row gate census (dead-link class) ===")
for i, l in find_line(app, r'p\.player_id \? `onclick|p\.token \? `onclick|selectPlayer\(|selectPlayerToken\('):
    print(f"  app.js:{i}: {l.strip()[:130]}")
