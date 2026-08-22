# Predictions

This directory is reserved for release-safe per-image prediction/probability outputs supporting the frozen E2-A runs and external evaluations.

Recommended substructure:

- `internal_E2A/`
- `pandian2019/`
- `plantvillage/`
- `tom2024/`

Prediction files should preserve architecture, seed, sample/group identifier, true label, predicted label, class probabilities, and integrity metadata where available. No raw image bytes belong here.
