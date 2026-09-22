#!/Users/traviscurnutte/.hermes/hermes-agent/venv/bin/python3
weights = {
    'identity': 0.12, 'type': 0.12, 'color': 0.10, 'layout': 0.12,
    'density': 0.12, 'interaction': 0.10, 'motion': 0.08, 'depth': 0.08,
    'consistency': 0.08, 'mobile': 0.08,
}
scores = {
    'identity': 9.0, 'type': 9.0, 'color': 8.0, 'layout': 8.5,
    'density': 8.5, 'interaction': 7.5, 'motion': 8.5, 'depth': 8.5,
    'consistency': 7.8, 'mobile': 8.6,
}
total = sum(weights[k] * scores[k] for k in weights)
for k in weights:
    print(f"{k:12s} {scores[k]:4.1f} x {weights[k]:.2f} = {scores[k]*weights[k]:.4f}")
print(f"WEIGHTED TOTAL = {total:.4f} -> {round(total,1)}")
