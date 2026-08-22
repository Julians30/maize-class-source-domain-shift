# Predictions

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
