# Predictions

## Current public release on 9 November 2026 UTC

The five-seed revision is published at https://doi.org/10.5281/zenodo.24064539. Its authoritative inventory is `manifests/zenodo_24064539_files.csv`, with ZIP-member hashes in `manifests/zenodo_24064539_archive_members.csv`; see `docs/CURRENT_PUBLIC_RELEASE.md` for verification scope. The current archive supplies recovered manifests, image-level prediction labels, validation outputs, analysis code and 30 separate checkpoints. Complete historical nine-output probability vectors are not claimed.

The original text below records the earlier three-seed/export preparation and recovery state. Its pending flags, unrecovered-source statements and proposed future deposit describe that historical stage. The current recovered master is `core_v7/manifests/manifest_master_clean_snapshot_v1_pre_split.csv` inside the public ZIP. No byte equivalence with historical expected exports is claimed; all six old registry layers remain historical. Original source images and private reviewer correspondence are not included in the public archive.

## Historical preparation record

This directory is reserved for release-safe per-image prediction/probability outputs supporting the frozen E2-A runs and external evaluations.

## Target substructure

- `internal_E2A/` — 18 frozen internal-test prediction files (six architectures × seeds 17, 42, 73; n = 1,719 each).
- `pandian2019/` — 18 frozen external rust prediction files (n = 1,922 each).
- `plantvillage/` — filtered external PlantVillage predictions, pending packaging/release audit.
- `tom2024/` — TOM2024 confirmatory/sensitivity predictions, pending packaging/release audit.

## Release-safe schema rule

Prediction files preserve architecture/run identity through the file name and retain image SHA-256, similarity-group identifier, source label, class label, sample identifier, predicted class, confidence, and class probabilities. Private absolute paths are removed and replaced with a portable logical path where needed. No raw image bytes belong here.

For E2-A internal predictions, expected file sizes/hashes are registered in `manifests/e2a_internal_prediction_expected_sha256.csv` and checked by `scripts/verify_internal_predictions.py`.

For Pandian2019, source-to-release derivation and expected release hashes are registered in `manifests/pandian2019_prediction_release_derivation.csv`; validation against the frozen run registry is recorded in `manifests/pandian2019_prediction_release_validation.csv` and checked by `scripts/verify_pandian_predictions.py`.
