# Reconciliation of the internal blocked macro-F1 architecture-effect test

## Scope

This note reconciles historical p-values for the architecture effect on internal E2-A macro-F1. It does not retrain models, change predictions, or reopen model selection. The authoritative inputs are the 18 frozen architecture-seed point estimates in `results/final_inference/02_point_metrics_by_run.csv` (six architectures × seeds 17, 42, and 73).

## Historical artifacts

Three numerical results must be distinguished.

1. An older development notebook computed a one-way architecture F statistic and freely permuted architecture labels across all 18 runs. It produced approximately `F = 0.6693`, `p = 0.7028`. This calculation does not implement the manuscript's seed-blocked design and is retained only as historical provenance; it must not be used for the manuscript-facing blocked test.
2. The later blocked analysis uses seed as a block and gives `F(5,10) = 0.8250817599851454`. A 50,000-draw restricted Monte Carlo permutation artifact reports `p = 0.5235495290094198`.
3. The manuscript draft reports approximately `p = 0.5198` for the same blocked architecture-effect question. The difference from the 50,000-draw value is compatible with ordinary Monte Carlo variation and does not represent a change in the observed F statistic or scientific conclusion.

## Exact resolution

Because the design is a randomized complete block with six architecture labels and three seed blocks, the null randomization permutes architecture assignments within each seed block. A common global relabeling of the six architecture labels leaves the treatment F statistic unchanged. Therefore one block can be fixed without loss of generality and the complete distinct randomization space has

`6!^(3-1) = 720^2 = 518,400`

assignments.

Enumerating all 518,400 distinct assignments gives 270,135 assignments with `F >= F_observed`. Thus the exact restricted-randomization p-value is

`p_exact = 270135 / 518400 = 0.52109375`.

No Monte Carlo correction is required because the reduced randomization space is exhaustively enumerated.

## Manuscript-facing decision

Use the exact blocked result `F(5,10) = 0.8251, p_exact = 0.5211` when a permutation/randomization p-value for internal macro-F1 is reported. The conclusion is unchanged: there is no evidence of an overall architecture effect on internal macro-F1 at alpha = 0.05. The historical Monte Carlo values `~0.5198` and `0.52355` should not be mixed across tables or text; they are superseded by the exact enumeration for the manuscript-facing result.

The machine-readable result is stored in `results/final_inference/internal_macro_f1_blocked_exact_randomization.csv`, and `scripts/verify_internal_blocked_exact.py` independently recomputes the statistic and exact p-value from the frozen 18-run table.
