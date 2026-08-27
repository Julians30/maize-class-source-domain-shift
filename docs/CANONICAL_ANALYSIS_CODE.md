# Canonical manuscript analysis code

This layer contains the two reviewer-facing analyses that were previously listed as pending transfer.

- `02_internal_comparison_E2A_release.ipynb` → architecture-centered internal E2-A comparison.
- `03_final_paired_inference_release.ipynb` → final paired inference, bootstrap uncertainty, Holm-adjusted contrasts, reliability and selective-risk outputs.

The notebooks are lightweight launchers. Their complete Python source is retained under `scripts/analysis/`. Long code is split only at top-level Python syntax boundaries into sequential fragments so every fragment remains readable, syntax-valid and SHA-256 auditable.

The transformation from the executed project notebooks was limited to repository hygiene: outputs, execution counts, Colab identity metadata, Drive mounting and private absolute paths were removed or parameterized. No model was retrained and no frozen statistical result was altered.

Integrity files:

- `manifests/canonical_code_provenance.csv`
- `manifests/canonical_fragment_sha256.csv`

Audit command:

```bash
python scripts/verify_canonical_analysis_code.py
```
