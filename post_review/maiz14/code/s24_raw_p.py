import numpy as np, pandas as pd, sys, itertools
sys.path.insert(0, sys.argv[1]); import maiz14 as M
E = np.load(sys.argv[2]); runs = [str(r) for r in E['runs']]; A = E['pandian2019']
seeds = [17, 42, 73]; K = M.KEYS
hit = {k: np.stack([(A[runs.index(f'{k}|{s}')] == 7) for s in seeds]).astype(float) for k in K}   # 3 x 1922
n = hit[K[0]].shape[1]; B = int(sys.argv[3]); rng = np.random.default_rng(int(sys.argv[4]))
S = rng.integers(0, 3, (B, 3)); I = rng.integers(0, n, (B, n))
# per-replicate recall for each arch: mean over resampled seeds of recall on resampled images
rec = {}
cnt = {k: np.stack([np.bincount(I[b], minlength=n) for b in range(1)]) for k in K[:0]}
W = np.zeros((B, n))
for b in range(B):
    W[b] = np.bincount(I[b], minlength=n)
for k in K:
    per_seed = hit[k] @ W.T / n            # 3 x B
    rec[k] = per_seed[S, np.arange(B)[:, None]].mean(1)   # B
obs = {k: hit[k].mean() for k in K}
rows = []
for a, b in itertools.combinations(K, 2):
    d = rec[a] - rec[b]; o = obs[a] - obs[b]
    lo, hi = np.percentile(d, [2.5, 97.5])
    p = min(1.0, 2 * min(((d <= 0).sum() + 1) / (B + 1), ((d >= 0).sum() + 1) / (B + 1)))
    rows.append({'A': M.NAMES[a], 'B': M.NAMES[b], 'diff': o, 'ci_low': lo, 'ci_high': hi, 'raw_p': p})
r = pd.DataFrame(rows).sort_values('raw_p').reset_index(drop=True); m = len(r)
adj = np.maximum.accumulate([min(1, (m - i) * p) for i, p in enumerate(r.raw_p)]); r['holm_p'] = np.minimum(adj, 1)
print(r.round(4).to_string())
r.to_csv(sys.argv[5], index=False)
