# Release-safe notebooks

Only notebooks that support the current manuscript or its supplementary material should be released here.

Two manuscript-facing notebooks have now been prepared locally for transfer:

- `02_internal_comparison_E2A_release.ipynb`
- `03_final_paired_inference_release.ipynb`

They were output-stripped and parameterized to remove personal Google Drive paths and historical `ARTICLE2` naming. The current audit is stored in `manifests/notebook_release_audit.csv` and records zero remaining outputs, zero attachments, and no forbidden private-path/article-number tokens in either notebook.

The notebooks intentionally do not mount a personal Drive. They use repository-relative defaults and environment variables such as `MAIZE_E2_ROOT` for the frozen per-run prediction directory. They are not yet present in this directory because they are part of the pending large/binary/manual transfer package.

Historical notebooks may remain outside the release repository when their final outputs are already represented by reconciled manuscript-facing assets. Any additional notebook considered for release must be audited for credentials, private/local paths, embedded raw third-party images, obsolete article numbering, and deprecated scenario definitions.
