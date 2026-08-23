# Repository status

## Current state

**Private — pre-submission reconciliation in progress.**

The repository is aligned to the current maize manuscript and supplementary material at the level of core protocol, frozen-run registry, principal internal inference, class–source controls, external-evaluation summaries, exact internal blocked inference, architecture-ranking stability, TOM2024 classwise uncertainty, computational-cost evidence, current analytical-figure fingerprints, release-safe Grad-CAM metadata, audited release manifests for the internal, Pandian2019, PlantVillage, and TOM2024 layers, and canonical repository-wide SHA-256 release-manifest tooling. No claim is made yet that the repository is a complete public release.

## Confirmed manuscript core

- Frozen master corpus: 13,413 images and 13,407 similarity groups.
- Six architectures and three seeds (18 frozen runs).
- Principal internal evaluation: E2-A, test n = 1,719.
- External evaluations in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.
- Frozen 18-run registry with configuration, checkpoint, and prediction SHA-256 values is stored in `manifests/e2_run_registry_v4.csv`.
- Verified E2-A execution evidence recorded in the registry: NVIDIA L4, PyTorch 2.11.0+cu128, timm 1.0.15.
- Final internal inference layer is stored under `results/final_inference/`, including strict prediction validation, per-run metrics, bootstrap intervals, Holm-adjusted pairwise contrasts, ensemble analyses, selective risk/AURC, per-run and summarized reliability, and class-level consensus difficulty.
- The internal E2-A macro-F1 architecture-effect discrepancy is resolved by exhaustive blocked randomization. With seed as the block, the observed statistic is `F(5,10)=0.8250817599851454`. Exploiting global treatment-label symmetry reduces the complete randomization space to `6!^2 = 518,400` distinct assignments; 270,135 have `F >= F_observed`, yielding `p_exact = 0.52109375`. This exact result supersedes the Monte Carlo estimates approximately 0.5198 and 0.5235495290. The manuscript-facing Word copy has been reconciled to report `p = 0.5211` and the exhaustive randomization denominator/numerator.
- Four-axis architecture ranking stability is machine-readable under `results/ranking_stability/`. The descending rank matrix yields `Kendall W = 0.03571428571428571`, chi-square approximation 0.7142857142857142 with 5 df, and `p ≈ 0.9821754508742055`. EfficientNet-B0 is selected by mean internal E2-A macro-F1, but its exact external selection losses are 0.15816857440166499 in Pandian2019, 0.20719476353836469 in PlantVillage, and 0.092591070739056924 in TOM2024.
- All 18 original E2-A internal prediction files have been independently matched to the frozen registry SHA-256 values and transformed into release-safe files with private Drive paths removed; expected release hashes are in `manifests/e2a_internal_prediction_expected_sha256.csv`.
- All 18 original Pandian2019 prediction files have been independently matched to the frozen registry `external_component_predictions_sha256` values. The release-safe transformation preserves 1,922 unique samples/groups per run, nine class probabilities, and reproduces frozen rust top-1 recall.
- Filtered PlantVillage release assets have been prepared from the preserved 3,852-image pHash layer: 1,330 overlap/near-overlap rows are represented in the audit, 2,522 images remain in the clean manifest, and the manuscript E3 subset contains 1,498 images (1,490 groups) across leaf blight and leaf spot. The preserved PlantVillage prediction artifact contains predicted labels/confidence but not nine full per-class probabilities; none are reconstructed or invented.
- TOM2024 release assets have been independently audited against the frozen manifest SHA-256. The frozen clean manifest contains 4,622 images, with zero exact SHA-256 overlap and zero pHash overlap (Hamming <=5) with the training corpus. Eighteen frozen E2-A checkpoints were evaluated without training, fine-tuning, calibration fitting, threshold fitting, or TOM2024-based model selection. The evaluated subset contains 1,833 unique images; confirmatory P1 contains 1,230 images and sensitivity P2 contains 1,833.
- Table S18 source data are reconciled through `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`.
- Figure S5 has been finalized directly from the frozen TOM2024 classwise recall bootstrap intervals and inserted into the reconciled supplementary Word copy.
- Table S19 source data and a release-safe per-run audit are reconciled under `results/computational_cost/`.
- Figure S6 has been numerically and visually reconciled against the six architecture-level E2-A NVIDIA L4 timing rows, promoted to the final supplementary filename, and inserted into the reconciled supplementary Word copy. Its caption was corrected so it no longer claims error bars that are not displayed.
- Figure S7 has passed a source-rights review specific to TOM2024. The Mendeley Data record is documented as CC BY 4.0; the final Grad-CAM composite embeds attribution, licence identification, and an indication that overlays modify the source images. This determination does not extend to other image sources.
- The supplementary Word copy now contains Table S18, Figure S5, Table S19, Figure S6, and Figure S7 in the correct order. A 15-page headless render was visually inspected page by page after final layout correction.
- The manuscript-facing Word copy and supplementary Word copy retain explicit placeholders only for information that has not yet been legitimately finalized: the public repository DOI/URL and author-confirmed CRediT roles.
- Two release-safe notebooks have been prepared and audited: zero outputs, zero attachments, no personal Drive paths, and no historical ARTICLE2 tokens remain.
- Repository scripts audit release scope, notebook safety, manuscript-facing core claims, exact internal blocked randomization, ranking stability/selection loss, supplementary S5/S6/S7 reconciliation, prepared large/binary assets, E2-A internal predictions, Pandian2019 predictions, PlantVillage release assets, and TOM2024 release assets.
- The final repository-wide integrity procedure is now implemented through `scripts/build_release_manifest.py` and `scripts/verify_release_manifest.py`. The canonical manifest is generated from Git index blobs after all final assets are committed, excludes itself to avoid circular hashing, and is enforced by `make release-check`.
- The search for a fuller maize software-environment export is closed without version inference: no authoritative E2-A lock file or `pip freeze` was found, so the release reports only the exact environment evidence preserved by the frozen run registry.

## Manuscript-package reconciliation

The current local pre-submission copies are:

- `Manuscrito_Maiz_ES_Q1_RECONCILIADO.docx` — SHA-256 `77e3dcc4a58950f1114f8ddb3b4fccde7a28cbc615c9adc828e6b1844c4b7354`.
- `Material_suplementario_Maiz_Q1_FINAL_REVISADO.docx` — SHA-256 `d2585effd67e84552bbab645d2a5816c5439dbf87fe43d0c617cc00cb73a805d`.

These manuscript binaries are not treated as repository source-of-truth files; the repository stores the machine-readable evidence and reconciliation notes that support them.

## Prepared pending transfer

Five original transfer packages plus the supplementary/ranking delta package have been prepared outside GitHub. The ZIP archives themselves must **not** be committed; only their unpacked contents should be transferred while preserving repository-relative paths.

1. `maize-class-source-domain-shift_GITHUB_PENDING_ONLY.zip`
   - SHA-256: `928dc861e744135f61dd4d84165e626bf27cabd55313dd4773646f81bfdc59eb`

2. `maize-class-source-domain-shift_E2A_INTERNAL_PREDICTIONS_PENDING_ONLY.zip`
   - SHA-256: `c80f7ecd1c5619afffc762b4120cdefaf3f505deb1951c9752f45d1831e2a625`

3. `maize-class-source-domain-shift_PANDIAN2019_PREDICTIONS_PENDING_ONLY.zip`
   - SHA-256: `cc4da6065d449fcb0e18217a5a4ea767587ad7f639ad2458c37a85bd4d69aa2a`

4. `maize-class-source-domain-shift_PLANTVILLAGE_PENDING_ONLY.zip`
   - SHA-256: `ac910295931a4da27e96c448a2fbb04c639b7b551e6bb490c4eed7355b9e40e9`

5. `maize-class-source-domain-shift_TOM2024_PENDING_ONLY.zip`
   - SHA-256: `01a7d06211c2b45c03994b3d8de0bcb28a8fcf75ed0d576c48158d51bdd4319a`

6. `maize-class-source-domain-shift_SUPPLEMENT_RANKING_DELTA_PENDING_ONLY.zip`
   - SHA-256: `6a836a25d8360af66ef3102210d1f9fee4651fcd16b429e2e1ddced9ae4894dd`
   - final S5/S6/S7 figures, ranking-stability outputs, reconciliation metadata, and verification scripts. Text assets are already versioned in GitHub; binary figures remain pending transfer.

Development checks tolerate prepared binaries not yet manually transferred; the strict release check requires all registered final assets.

## Pending before release

- transfer the prepared pending-only package contents into their repository paths without committing ZIP archives;
- transfer the final S5/S6/S7 PDF/PNG binaries;
- after all final assets are committed and the tree is clean, run `make release-manifest`, review and commit `manifests/release_sha256.csv`;
- run `make release-check` and resolve all remaining strict-audit failures;
- obtain author-confirmed CRediT roles;
- only after the repository passes the release audit, decide public visibility / persistent archive DOI and replace the DOI/URL placeholders in manuscript and supplement.
