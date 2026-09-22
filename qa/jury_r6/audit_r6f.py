#!/usr/bin/env python3
"""R6-3 final weighted math with interaction held at 8.9."""
scores = {
    'identity': (8.9, 0.12), 'type': (7.6, 0.12), 'color': (8.4, 0.10),
    'layout': (8.9, 0.12), 'density': (8.8, 0.12), 'interaction': (8.9, 0.10),
    'motion': (9.0, 0.08), 'depth': (9.1, 0.08), 'consistency': (8.3, 0.08),
    'mobile': (8.9, 0.08),
}
total = sum(s*w for s, w in scores.values())
print('parts:', ' + '.join(f'{s}x{w}={s*w:.3f}' for s, w in scores.values()))
print(f'TOTAL = {total:.3f} -> {total:.1f}')
proj = dict(scores)
proj['type'] = (8.6, 0.12); proj['color'] = (9.1, 0.10)
proj['consistency'] = (8.9, 0.08); proj['mobile'] = (9.3, 0.08)
t2 = sum(s*w for s, w in proj.values())
print(f'projected post-3-fixes = {t2:.3f} -> {t2:.1f}')
print(f'fix1 delta (type+consistency): {(8.6-7.6)*0.12 + (8.9-8.3)*0.08:.3f}')
print(f'fix2 delta (color): {(9.1-8.4)*0.10:.3f}')
print(f'fix3 delta (mobile): {(9.3-8.9)*0.08:.3f}')
