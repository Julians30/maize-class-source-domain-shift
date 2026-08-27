# Pending large/binary transfer

The two canonical manuscript notebooks are **no longer pending**: they are versioned under `notebooks/` and independently audited through `manifests/notebook_release_audit.csv` and `scripts/verify_canonical_analysis_code.py`.

The original pending-only ZIP archives must **not** be committed. Only release-safe unpacked contents should be transferred while preserving repository-relative paths.

The first registered transfer layer still contains these remaining large/binary assets:

- `data/manifests/manifest_master_clean_snapshot_v1_release.csv`;
- `splits/e2a_adege_to_pandian_manifest_v1_release.csv`;
- five current main analytical PDF figures;
- one candidate supplementary training-time PDF, subject to final reconciliation.

Additional registered prediction layers for E2-A, Pandian2019, PlantVillage and TOM2024 remain governed by their dedicated expected-SHA manifests and verifier scripts.

The Grad-CAM image-bearing composite remains a separate source-rights/release decision and must not be bundled automatically merely because its analytical metadata are present.

Use:

```bash
python scripts/verify_pending_transfer.py
```

Development mode reports missing large assets as pending. Final strict release requires every final registered asset that remains in scope.
