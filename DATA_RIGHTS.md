# Data rights and redistribution boundary

This repository separates **analytical reproducibility** from **rights to redistribute original image files**.

## Rule for original images

The manuscript is based on a reconciled multi-source corpus. Inclusion in the analytical corpus does not imply that the manuscript authors own, created, or may redistribute every underlying image. Therefore, original image files are excluded from the repository release unless source-specific reuse and redistribution rights have been verified.

## Sources represented in the manuscript-facing analysis

The preserved audit uses operational source labels, including `raw_ccmt_clean`, `CIMMYT_MLND`, `Kaggle_HEALTHY_up`, `Kaggle_Healthy_paren`, `Adege_field_smartphone`, `Adege_rust_rss`, and `Pandian2019`. External evaluation additionally uses a filtered PlantVillage subset and TOM2024.

Reference-level provenance recorded by the manuscript includes:

- Adege (2026), *Maize Crop Disease (Leaf)*, Mendeley Data, V1, DOI: `10.17632/6w6gsvghfw.1`;
- Arun Pandian & Geetharamani (2019), plant-leaf-disease data, Mendeley Data, V1, DOI: `10.17632/tywbtsjrjv.1`;
- PlantVillage as described by Mohanty et al. (2016), used only after an overlap audit and restricted to two retained maize disease classes;
- TOM2024 as described by Appiah et al. (2025), *Data in Brief* 59, 111357, DOI: `10.1016/j.dib.2025.111357`;
- additional operational components preserved in the local audit, including CIMMYT-derived and Kaggle-derived components, for which redistribution rights must be reviewed independently.

These references document provenance at the level supported by the manuscript. They do **not** constitute a repository-wide licensing determination.

## Components excluded during audit

The release must not reintroduce components that the analytical audit excluded, including:

- `CCMT_augmented`: excluded because pre-generated augmentation creates pseudoreplication risk;
- `CCMT_raw_id8`: excluded because of provenance/licensing/visual heterogeneity concerns;
- `Otras`: excluded because of overlap, provenance, and label-traceability concerns;
- source-specific files excluded because of exact/perceptual duplication or unresolved label conflicts.

## Derived assets intended for release

Subject to final privacy and rights review, the repository may release:

- source/provenance inventories;
- analytical identifiers and operational labels;
- SHA-256 and perceptual-hash metadata;
- frozen split assignments;
- exclusion and audit decisions;
- model configuration and checkpoint hashes;
- per-image predictions and class probabilities when they do not reproduce restricted image content;
- statistical outputs, tables, figures, and reproducibility scripts;
- release-safe notebooks with outputs removed when needed.

## Licensing

No blanket data license is asserted for third-party image content. Any future code license or license for author-generated derived data must be scoped explicitly and must not be interpreted as relicensing third-party images.
