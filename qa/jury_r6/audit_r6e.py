#!/usr/bin/env python3
"""R6-3: weighted total verify + light faint candidate math."""
def lum(hx):
    r, g, b = (int(hx[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb)+0.05)/(min(la, lb)+0.05)

print('=== LIGHT FAINT CANDIDATES (need >=3:1 large-only, stay subordinate to muted 5.13:1) ===')
for cand in ['76879c', '7b8ba0', '80909f', '7e8ea2']:
    r = ratio(cand, 'ffffff')
    print(f'#{cand} / panel #ffffff: {r:.2f}:1')

print('\n=== WEIGHTED TOTAL (R6-3 scores) ===')
scores = {
    'identity': (8.9, 0.12), 'type': (7.6, 0.12), 'color': (8.4, 0.10),
    'layout': (8.9, 0.12), 'density': (8.8, 0.12), 'interaction': (9.0, 0.10),
    'motion': (9.0, 0.08), 'depth': (9.1, 0.08), 'consistency': (8.3, 0.08),
    'mobile': (8.9, 0.08),
}
total = 0.0
parts = []
for k, (s, w) in scores.items():
    contrib = s * w
    total += contrib
    parts.append(f'{k} {s}x{w}={contrib:.3f}')
print(' + '.join(parts))
print(f'TOTAL = {total:.3f} -> rounds to {total:.1f}')

# projected post-fix
proj = scores.copy()
proj['type'] = (8.6, 0.12); proj['color'] = (9.1, 0.10); proj['consistency'] = (8.9, 0.08)
proj['mobile'] = (9.3, 0.08)
t2 = sum(s*w for s, w in proj.values())
print(f'projected after 3 fixes = {t2:.3f} -> {t2:.1f}')
