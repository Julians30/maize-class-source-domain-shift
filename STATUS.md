# Repository status

## Current state

**Private — pre-submission reconciliation in progress.**

The repository is aligned to the current maize manuscript and supplementary material at the level of core protocol, frozen-run registry, principal internal inference, class–source controls, external-evaluation summaries, TOM2024 uncertainty, computational-cost evidence, current analytical-figure fingerprints, and release-safe Grad-CAM metadata. No claim is made yet that the repository is a complete public release.

## Confirmed manuscript core

- Frozen master corpus: 13,413 images and 13,407 similarity groups.
- Six architectures and three seeds (18 frozen runs).
- Principal internal evaluation: E2-A, test n = 1,719.
- External evaluations in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.
- Frozen 18-run registry with configuration, checkpoint, and prediction SHA-256 values is stored in `manifests/e2_run_registry_v4.csv`.
- Verified E2-A execution evidence recorded in the registry: NVIDIA L4, PyTorch 2.11.0+cu128, timm 1.0.15.
- Final internal inference layer is stored under `results/final_inference/`, including strict prediction validation, per-run metrics, bootstrap intervals, Holm-adjusted pairwise contrasts, ensemble analyses, selective risk/AURC, per-run and summarized reliability, and class-level consensus difficulty.
- Table S18 source data are reconciled through the TOM2024 classwise bootstrap file.
- Table S19 source data and a release-safe per-run audit are reconciled under `results/computational_cost/`.
- Main analytical figure captions are catalogued, and current PDF hashes have been independently re-verified in `figures/final_pdf_fingerprints_verified.csv`.
- The older Drive fingerprint catalog is retained as provenance but is known to predate the latest saved Figures 3 and 4.
- Two release-safe notebooks have been prepared and audited: zero outputs, zero attachments, no personal Drive paths, and no historical ARTICLE2 tokens remain. Their expected hashes are in `manifests/notebook_release_audit.csv`.
- Repository scripts now audit release scope, notebook safety, manuscript-facing core claims, and hashes for prepared pending-transfer assets.

## Prepared pending transfer

A first pending-only large/binary transfer package has been prepared outside GitHub:

- package: `maize-class-source-domain-shift_GITHUB_PENDING_ONLY.zip`
- SHA-256: `928dc861e744135f61dd4d84165e626bf27cabd55313dd4773646f81bfdc59eb`
- contents: two full release-safe manifests, two release-safe notebooks, five current main analytical PDFs, one explicitly named candidate supplementary training-time PDF, and a package SHA-256 manifest.

Expected target hashes are versioned in `manifests/pending_transfer_expected_sha256.csv`; `scripts/verify_pending_transfer.py` verifies transferred files without requiring them during ordinary development checks and requires all of them during the strict release check.

## Important unresolved reconciliation

The manuscript-facing internal blocked macro-F1 permutation p-value remains under reconciliation: the manuscript reports approximately 0.5198, while a preserved 50,000-permutation development artifact reports 0.5235495290 with the same F statistic. The repository does not silently substitute one value for the other.

The candidate training-time PDF is not yet promoted to final Figure S6. Figure S5 still requires final manuscript-facing construction/reconciliation. The Grad-CAM image-bearing composite remains outside the release package pending source-rights review.

## Pending before release

- transfer the prepared pending-only package contents into their repository paths without committing the ZIP itself;
- package/transfer the 18 E2-A per-image prediction-probability outputs and external-domain prediction files;
- package filtered PlantVillage and TOM2024 release-safe manifests/audits;
- finalize Figure S5 and reconcile/promote Figure S6;
- decide whether Figure S7 / the Grad-CAM image-bearing composite can be redistributed after source-rights review;
- locate an authoritative full software environment export if one exists; otherwise retain only the exact versions documented by the frozen run registry;
- generate the final repository-wide SHA-256 release manifest after all release assets are present;
- resolve the internal permutation-p discrepancy or document the regenerated authoritative analysis;
- run the strict repository audit and resolve all remaining failures;
- only then decide public visibility / persistent archive DOI.
