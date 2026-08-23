# Repository status

## Current state

**Private — pre-submission reconciliation in progress.**

The repository is aligned to the current maize manuscript and supplementary material at the level of core protocol, frozen-run registry, principal internal inference, class–source controls, external-evaluation summaries, exact internal blocked inference, architecture-ranking stability, TOM2024 classwise uncertainty, computational-cost evidence, current analytical-figure fingerprints, release-safe Grad-CAM metadata, and audited release manifests for the internal, Pandian2019, PlantVillage, and TOM2024 layers. No claim is made yet that the repository is a complete public release.

## Confirmed manuscript core

- Frozen master corpus: 13,413 images and 13,407 similarity groups.
- Six architectures and three seeds (18 frozen runs).
- Principal internal evaluation: E2-A, test n = 1,719.
- External evaluations in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.
- Frozen 18-run registry with configuration, checkpoint, and prediction SHA-256 values is stored in `manifests/e2_run_registry_v4.csv`.
- Verified E2-A execution evidence recorded in the registry: NVIDIA L4, PyTorch 2.11.0+cu128, timm 1.0.15.
- Final internal inference layer is stored under `results/final_inference/`, including strict prediction validation, per-run metrics, bootstrap intervals, Holm-adjusted pairwise contrasts, ensemble analyses, selective risk/AURC, per-run and summarized reliability, and class-level consensus difficulty.
- The internal E2-A macro-F1 architecture-effect discrepancy is resolved by exhaustive blocked randomization. With seed as the block, the observed statistic is `F(5,10)=0.8250817599851454`. Exploiting global treatment-label symmetry reduces the complete randomization space to `6!^2 = 518,400` distinct assignments; 270,135 have `F >= F_observed`, yielding `p_exact = 0.52109375`. This exact result supersedes the Monte Carlo estimates approximately 0.5198 and 0.5235495290. The result and independent verifier are stored in `results/final_inference/internal_macro_f1_blocked_exact_randomization.csv` and `scripts/verify_internal_blocked_exact.py`.
- Four-axis architecture ranking stability is now machine-readable under `results/ranking_stability/`. The descending rank matrix yields `Kendall W = 0.03571428571428571`, chi-square approximation 0.7142857142857142 with 5 df, and `p ≈ 0.9821754508742055`. EfficientNet-B0 is selected by mean internal E2-A macro-F1, but its exact external selection losses are 0.15816857440166499 in Pandian2019, 0.20719476353836469 in PlantVillage, and 0.092591070739056924 in TOM2024. `scripts/verify_ranking_stability.py` checks these outputs.
- All 18 original E2-A internal prediction files have been independently matched to the frozen registry SHA-256 values and transformed into release-safe files with private Drive paths removed; expected release hashes are in `manifests/e2a_internal_prediction_expected_sha256.csv`.
- All 18 original Pandian2019 prediction files have been independently matched to the frozen registry `external_component_predictions_sha256` values. The release-safe transformation preserves 1,922 unique samples/groups per run, nine class probabilities, and reproduces frozen rust top-1 recall. Derivation and validation are versioned under `manifests/pandian2019_prediction_release_*.csv`.
- Filtered PlantVillage release assets have been prepared from the preserved 3,852-image pHash layer: 1,330 overlap/near-overlap rows are represented in the audit, 2,522 images remain in the clean manifest, and the manuscript E3 subset contains 1,498 images (1,490 groups) across leaf blight and leaf spot. The consolidated 18-run prediction layer reproduces the stored accuracy, macro-F1, and class recalls. The preserved PlantVillage prediction artifact contains predicted labels/confidence but not nine full per-class probabilities; none are reconstructed or invented. Expected hashes are in `manifests/plantvillage_release_expected_sha256.csv`.
- TOM2024 release assets have been independently audited against the frozen manifest SHA-256. The frozen clean manifest contains 4,622 images, with zero exact SHA-256 overlap and zero pHash overlap (Hamming <=5) with the training corpus. Eighteen frozen E2-A checkpoints were evaluated without training, fine-tuning, calibration fitting, threshold fitting, or TOM2024-based model selection. The evaluated subset contains 1,833 unique images; confirmatory P1 contains 1,230 images and sensitivity P2 contains 1,833. Both release prediction layers preserve the original nine-class probabilities. Recomputed point metrics agree with the frozen per-run table to floating-point/CSV-rounding precision. Expected hashes are in `manifests/tom2024_release_expected_sha256.csv`.
- Table S18 source data are reconciled through `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`.
- Figure S5 has been finalized directly from the frozen TOM2024 classwise recall bootstrap intervals for fall-armyworm presence, healthy leaf, and rust. The PDF/PNG were rendered and visually inspected; expected hashes are registered in `manifests/supplementary_reconciliation_expected_sha256.csv`.
- Table S19 source data and a release-safe per-run audit are reconciled under `results/computational_cost/`.
- Figure S6 has been numerically and visually reconciled against the six architecture-level E2-A NVIDIA L4 timing rows and promoted from the preserved candidate without changing bytes. The final PDF therefore retains SHA-256 `791a7a2c650cebf007805dd7f791690a7199b3e32f8b4572e9933ddb2dcf66ca`.
- `scripts/verify_supplementary_reconciliation.py` checks the S5/S6 authoritative sources and, in strict mode, requires the final PDF/PNG binaries with registered hashes.
- Main analytical figure captions are catalogued, and current PDF hashes have been independently re-verified in `figures/final_pdf_fingerprints_verified.csv`.
- The older Drive fingerprint catalog is retained as provenance but is known to predate the latest saved Figures 3 and 4.
- Two release-safe notebooks have been prepared and audited: zero outputs, zero attachments, no personal Drive paths, and no historical ARTICLE2 tokens remain. Their expected hashes are in `manifests/notebook_release_audit.csv`.
- Repository scripts now audit release scope, notebook safety, manuscript-facing core claims, exact internal blocked randomization, ranking stability/selection loss, supplementary S5/S6 reconciliation, prepared large/binary assets, E2-A internal predictions, Pandian2019 predictions, PlantVillage release assets, and TOM2024 release assets.

## Prepared pending transfer

Five original transfer packages plus one supplementary/ranking delta package have been prepared outside GitHub. The ZIP archives themselves must **not** be committed; only their unpacked contents should be transferred while preserving repository-relative paths.

1. `maize-class-source-domain-shift_GITHUB_PENDING_ONLY.zip`
   - SHA-256: `928dc861e744135f61dd4d84165e626bf27cabd55313dd4773646f81bfdc59eb`
   - two full release-safe manifests, two release-safe notebooks, five current main analytical PDFs, one historical candidate supplementary training-time PDF, and a package SHA-256 manifest.

2. `maize-class-source-domain-shift_E2A_INTERNAL_PREDICTIONS_PENDING_ONLY.zip`
   - SHA-256: `c80f7ecd1c5619afffc762b4120cdefaf3f505deb1951c9752f45d1831e2a625`
   - 18 release-safe internal E2-A per-image prediction/probability files plus derivation/integrity metadata.

3. `maize-class-source-domain-shift_PANDIAN2019_PREDICTIONS_PENDING_ONLY.zip`
   - SHA-256: `cc4da6065d449fcb0e18217a5a4ea767587ad7f639ad2458c37a85bd4d69aa2a`
   - 18 release-safe Pandian2019 per-image prediction/probability files, derivation and validation manifests, and package SHA-256 metadata.

4. `maize-class-source-domain-shift_PLANTVILLAGE_PENDING_ONLY.zip`
   - SHA-256: `ac910295931a4da27e96c448a2fbb04c639b7b551e6bb490c4eed7355b9e40e9`
   - release-safe full/clean/evaluation manifests, overlap audit, consolidated 18-run prediction table, derivation/validation metadata, and package SHA-256 metadata.

5. `maize-class-source-domain-shift_TOM2024_PENDING_ONLY.zip`
   - SHA-256: `01a7d06211c2b45c03994b3d8de0bcb28a8fcf75ed0d576c48158d51bdd4319a`
   - release-safe frozen TOM2024 manifest and overlap-audit tables, 18-run prediction/probability layer, protocol-expanded prediction layer, checkpoint verification, mapping protocol, validation/derivation metadata, and package SHA-256 metadata. No raw TOM2024 images are included.

6. `maize-class-source-domain-shift_SUPPLEMENT_RANKING_DELTA_PENDING_ONLY.zip`
   - SHA-256: `6a836a25d8360af66ef3102210d1f9fee4651fcd16b429e2e1ddced9ae4894dd`
   - final Figure S5 PDF/PNG, final promoted Figure S6 PDF/PNG, ranking-stability outputs, S5/S6 hash manifest, reconciliation documentation, and verification scripts. Text assets are already versioned in GitHub; the binary figures remain pending manual transfer.

Development checks tolerate prepared binaries not yet manually transferred; the strict release check requires the final S5/S6 files as well as the original five prepared layers.

## Important unresolved reconciliation

The remaining supplementary scientific issue is Figure S7 redistribution: the Grad-CAM image-bearing composite contains source image content and remains outside the release package pending a source-rights decision. The current supplementary Word document also still needs its manuscript-referenced S18/S19/S5/S6/S7 sections inserted and cross-references reconciled. No public-repository or persistent-DOI statement should be inserted until the complete release audit is finished.

## Pending before release

- transfer the five original prepared pending-only package contents into their repository paths without committing ZIP archives;
- transfer the final S5/S6 PDF/PNG binaries from the supplementary/ranking delta package;
- insert formatted Table S18, Figure S5, Table S19, and Figure S6 into the supplementary Word document and resolve Figure S7 according to source-rights review;
- decide whether Figure S7 / the Grad-CAM image-bearing composite can be redistributed after source-rights review;
- locate an authoritative full software environment export if one exists; otherwise retain only the exact versions documented by the frozen run registry;
- generate the final repository-wide SHA-256 release manifest after all release assets are present;
- run the strict repository audit and resolve all remaining failures;
- only then decide public visibility / persistent archive DOI.
