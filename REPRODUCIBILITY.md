# Reproducibility — current revision and historical records

Updated 9 November 2026 (UTC). The current manuscript/supplement define reporting targets; historical notebook/folder names or old registries do not silently redefine the revised experiment.

## Current reporting targets

- Six configurations, five seeds (17, 42, 73, 101, 137), 30 selected checkpoints, 120 principal evaluations.
- Mean internal validation macro-F1 selects the architecture. The original validation/test counts are 1,729/1,719. Added seeds and optimization checks were retrospective.
- Three external cohorts (Pandian2019, filtered PlantVillage, TOM2024) represent two broad provenance families and different tasks/metrics.
- Paired group/seed bootstrap with 5,000 resamples, raw and Holm-adjusted contrasts, classwise errors and seed-specific ranks. Uncertainty is conditional on the observed five seeds and recorded groups.
- Native-pixel verification of 1,164 strong pairs; prediction-only internal exclusions and external candidate-family weighting. Neither reconstructs clean training/selection or supplies confirmed-parent bootstrap intervals.
- Human review covers all 190 critical pairs (189 same-photograph or transformation judgments, one related capture), with none pending. Two contributors reviewed disjoint subsets of 171 and 19, so no independent double rating of every pair or inter-rater agreement is claimed. The four computationally exact critical pairs are included in the 189 visual same-photograph judgments. The other 974 strong candidates were not visually adjudicated. The anonymous 94-image rust assessment is separate.

## Public scientific package

The public archive contains manifests, five-seed prediction labels, recovered validation outputs, run records, statistics, native-pixel results/masks and executable verification/sensitivity code. It also supplies the healthy-source-stratified and TOM2024 probability checks. All 30 checkpoint binaries (9,013,090,475 bytes) are separate public files. Public research record: [https://doi.org/10.5281/zenodo.24064539](https://doi.org/10.5281/zenodo.24064539). It contains the data/code ZIP and all 30 selected checkpoints (31 files; 9,036,167,461 bytes). See [current file registry](manifests/zenodo_24064539_files.csv), [archive-member inventory](manifests/zenodo_24064539_archive_members.csv) and [verification scope](docs/CURRENT_PUBLIC_RELEASE.md).

The source-stratified healthy check does not remove the 261 linked training images and is not an ablation. Complete historical nine-output vectors and all requested closed-set/remapping analyses are not supplied. Embedding-based biological-parent recovery and a clean retraining/selection experiment were not performed. Selective-risk analyses are not claimed as executed.

## Historical code layer

The repository preserves the original three-seed/18-run code and registries, including the historical internal exact blocked test and earlier bootstrap choices. Their original counts, seeds and resampling definitions are not relabeled as the five-seed analysis. Repository CI verifies this historical integrity layer; its results do not by themselves audit every artifact in the separate current candidate.

## Integrity and release

Use SHA-256 manifests to verify source and output identities. Keep original and reconciled records, plus their mapping and explanation, whenever they differ. Do not alter prediction bytes to match revised narrative claims.

Run `make presubmission-check` for existing repository checks. The final repository-wide `manifests/release_sha256.csv` is generated only after final release assets are committed, from Git index blobs, excluding itself. Then run `make release-check`. Publication of the current Zenodo record is verified independently; it does not imply that this stricter historical repository-wide gate passes, that every historical export is released byte-for-byte, or that unresolved rights have been cleared.

Release notebooks must exclude credentials, bulky execution outputs, private identities and unauthorized raw images. Original source photographs are not included in the prepared derived-data archive. See `LICENSE_SCOPE.md` and `DATA_RIGHTS.md` for rights distinct from the MIT software license.
