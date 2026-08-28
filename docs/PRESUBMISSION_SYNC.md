# Pre-submission manuscript–supplement–repository synchronization

Status: pre-submission synchronization for the Agriculture (MDPI) manuscript.

This note records manuscript-facing additions that were derived exclusively from already frozen analytical outputs. No model was retrained, no checkpoint was changed, and no primary scientific result was regenerated during this synchronization.

## Newly synchronized derived artifacts

- `results/variance_decomposition/architecture_seed_ss_by_axis.csv`: descriptive, within-axis partition of sums of squares into architecture, seed and residual/unresolved components for Internal E2-A, Pandian2019, PlantVillage and TOM2024. The residual includes any non-estimable architecture×seed interaction because there is one observation per cell. The rows are not pooled into one cross-domain ANOVA because the evaluation axes use heterogeneous response scales and class spaces.
- `manifests/source_license_audit.csv`: source-level rights/license status and conservative redistribution decision used for the supplementary license audit.

These correspond to manuscript-facing Supplementary Tables S20 and S21.

## Submission-facing bibliography state

The submission-ready manuscript contains 54 bibliographic entries. MDPI numeric citations are ordered by first appearance. DOI strings are included only where an assigned identifier could be verified; conference proceedings, JMLR/PMLR papers and books without an assigned DOI are not given invented identifiers.

Specific corrections made during the final audit include:

- Appiah et al. (2025): `10.1016/j.dib.2025.111357`.
- Geirhos et al. (2020): `10.1038/s42256-020-00257-z`.
- Hu et al. (2026): `10.3389/fpls.2026.1807927`.
- Xiang et al. (2026): `10.3389/fpls.2026.1826962`.
- Mensah et al. (2023), CCMT: `10.1016/j.dib.2023.109306`.

## Release boundary

GitHub remains the code/notebook/manifest/reproducibility layer. Large release-safe prediction files and final public archive assets remain governed by the external-artifact registry and are intended for the persistent public deposit (for example Zenodo) at submission/release time. This note does not replace the strict release check or invent a DOI before one exists.
