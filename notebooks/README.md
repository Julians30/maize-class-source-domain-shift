# Release-safe notebooks

This directory contains the two canonical reviewer-facing notebooks for the current maize manuscript:

- `02_internal_comparison_E2A_release.ipynb`
- `03_final_paired_inference_release.ipynb`

Both notebooks are intentionally lightweight launchers. The complete auditable Python source is versioned under `scripts/analysis/`, with long sources split only at top-level syntax boundaries into sequential files under `scripts/analysis/fragments/`.

The release notebooks contain zero execution outputs, zero attachments, no personal Google Drive paths, no credentials, and no historical manuscript-number tokens. Their byte counts and SHA-256 values are recorded in `manifests/notebook_release_audit.csv` and `manifests/canonical_code_provenance.csv`.

The transformation from the executed project notebooks was limited to repository hygiene: execution outputs and Colab identity metadata were removed, personal Drive mounting was eliminated, and runtime paths were parameterized. No model was retrained and no frozen statistical result was altered.

Audit with:

```bash
python scripts/audit_notebooks.py --require
python scripts/verify_canonical_analysis_code.py
```

Historical development notebooks are not automatically manuscript-facing. In particular, the historical split named `E3` is not the manuscript-facing E3 analysis; the current manuscript uses E3 for filtered PlantVillage external evaluation.
