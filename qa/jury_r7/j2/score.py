import json

d = json.load(open('today.json'))
games = d.get('games') or d.get('today') or []
print('top-level keys:', list(d.keys()))
print('n games:', len(games))
for x in games[:14]:
    print(x.get('time'), '|', x.get('home'), 'vs', x.get('away'), '|',
          x.get('facility'), '| played:', x.get('played'),
          '| hs:', x.get('home_score'), x.get('away_score'))

# ---- WCAG contrast checks for tokens I need to re-score ----
def lum(hexc):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    def f(c):
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126*r + 0.7152*g + 0.0722*b

def ratio(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi+0.05)/(lo+0.05)

def blend(fg, alpha, bg):
    f = [int(fg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    out = [round(a*alpha + c*(1-alpha)) for a, c in zip(f, b)]
    return '#%02x%02x%02x' % tuple(out)

dark_bg = '070b12'
panel = '0d1522'
checks = {
    'accent #ef3d54 on #070b12': ratio('ef3d54', dark_bg),
    'accent #ef3d54 on panel': ratio('ef3d54', panel),
    'muted #5d6f88 on bg': ratio('5d6f88', dark_bg),
    'faint #5d6b80 on bg': ratio('5d6b80', dark_bg),
    'scored-nums accent 20px on inset': ratio('ef3d54', '0a1018'),
    'rink-head union #2a7fd4 on bg': ratio('2a7fd4', dark_bg),
    'tonight-label (per css px/alpha)': None,
}
for k, v in checks.items():
    if v is not None:
        print(f'{k}: {v:.2f}:1')

# smallest label colors blended over panel
print('muted@1.0 over panel:', round(ratio('5d6f88', panel), 2))
print('text-2 blended 0.8 over panel:', round(ratio(blend('e8eef8', 0.8, panel), panel), 2))
