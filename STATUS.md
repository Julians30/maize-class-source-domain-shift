# Repository status

## Current state

**Private — pre-submission reconciliation in progress.**

The repository is aligned to the current maize manuscript and supplementary material at the level of core protocol, frozen-run registry, principal internal inference, class–source controls, external-evaluation summaries, TOM2024 uncertainty, computational-cost evidence, and release-safe Grad-CAM metadata. No claim is made yet that the repository is a complete public release.

## Confirmed manuscript core

- Frozen master corpus: 13,413 images and 13,407 similarity groups.
- Six architectures and three seeds (18 frozen runs).
- Principal internal evaluation: E2-A, test n = 1,719.
- External evaluations in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.
- Frozen 18-run registry with configuration, checkpoint, and prediction SHA-256 values is now stored in `manifests/e2_run_registry_v4.csv`.
- Verified E2-A execution evidence recorded in the registry: NVIDIA L4, PyTorch 2.11.0+cu128, timm 1.0.15.
- Final internal inference layer is stored under `results/final_inference/`, including strict prediction validation, per-run metrics, bootstrap intervals, Holm-adjusted pairwise contrasts, ensemble analyses, selective risk/AURC, reliability summaries, and class-level consensus difficulty.
- Table S18 source data are reconciled through the TOM2024 classwise bootstrap file.
- Table S19 source data are reconciled through the training-time tables.
- Main analytical figure captions and SHA-256 fingerprints are catalogued under `figures/`.
- Main statistical components include blocked/permutation analysis, paired bootstrap, Holm correction, ranking stability, classwise uncertainty, source-confounding controls, Grad-CAM exploration, and computational-cost analysis.

## Important unresolved reconciliation

The manuscript-facing internal blocked macro-F1 permutation p-value remains under reconciliation: the manuscript reports approximately 0.5198, while a preserved 50,000-permutation development artifact reports 0.5235495290 with the same F statistic. The repository does not silently substitute one value for the other.

## Pending before release

- transfer the prepared release-safe full master-corpus and E2-A split manifests;
- package/transfer the 18 E2-A per-image prediction-probability outputs and external-domain prediction files;
- package filtered PlantVillage and TOM2024 release-safe manifests/audits;
- transfer the final analytical figure binaries after hash verification;
- finalize manuscript-facing Figure S5 and reconcile the candidate training-time Figure S6;
- decide whether Figure S7 / the Grad-CAM image-bearing composite can be redistributed after source-rights review;
- prepare and audit release-safe notebooks, removing outputs, credentials/private paths, and obsolete scenario labels;
- locate an authoritative full software environment export if one exists; otherwise retain only the exact versions documented by the frozen run registry;
- generate the final package-level SHA-256 manifest after all large assets are transferred;
- run the strict repository audit and resolve any remaining failures;
- only then decide public visibility / persistent archive DOI.
