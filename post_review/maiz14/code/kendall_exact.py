"""Exact null distribution of Kendall's W for m = 4 rankings of n = 6 architectures.

The null assumes independent, uniformly relabeled untied rankings. Because W is invariant to a common
relabeling of the architectures, the first ranking is fixed and all 720**3 relative assignments of the
other three are enumerated. Prints exact lower- and upper-tail probabilities for the observed W values
reported in the manuscript (Section 3.3) and Supplement Table S62.
"""
import itertools
from collections import Counter
import numpy as np

N, M = 6, 4
OBSERVED = {'historical mix': 2 / 35, 'all axes crop': 4 / 35, 'all axes resize': 11 / 70}


def w_from_s(s):
    return 12 * s / (M ** 2 * (N ** 3 - N))


def null_counts():
    perms = np.array(list(itertools.permutations(range(1, N + 1))), dtype=np.int32)
    first_two = np.arange(1, N + 1, dtype=np.int32) + perms
    mean = M * (N + 1) / 2
    counts = Counter()
    for k in range(len(perms)):
        sums = first_two[:, None, :] + perms[None, :, :] + perms[k][None, None, :]
        s = ((sums - mean) ** 2).sum(axis=2)
        values, freq = np.unique(s, return_counts=True)
        counts.update(dict(zip(values.tolist(), freq.tolist())))
    return counts


if __name__ == '__main__':
    counts = null_counts(); total = sum(counts.values())
    print('recipe_set,W,exact_lower_tail_p,exact_upper_tail_p')
    for name, w in OBSERVED.items():
        lo = sum(c for s, c in counts.items() if w_from_s(s) <= w + 1e-12) / total
        hi = sum(c for s, c in counts.items() if w_from_s(s) >= w - 1e-12) / total
        print(f'{name},{w:.6f},{lo:.6f},{hi:.6f}')
