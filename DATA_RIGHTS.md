# Data rights and redistribution boundary

This repository separates **analytical reproducibility** from **rights to redistribute original image files**.

## Rule for original images

The manuscript is based on a reconciled multi-source corpus. Inclusion in the analytical corpus does not imply that the manuscript authors own, created, or may redistribute every underlying image. Therefore, original image files are excluded from the repository release unless source-specific reuse and redistribution rights have been verified.

## Sources represented in the manuscript-facing analysis

The preserved audit uses operational source labels, including `raw_ccmt_clean`, `CIMMYT_MLND`, `Kaggle_HEALTHY_up`, `Kaggle_Healthy_paren`, `Adege_field_smartphone`, `Adege_rust_rss`, and `Pandian2019`. External evaluation additionally uses a filtered PlantVillage subset and TOM2024.

Reference-level provenance recorded by the manuscript includes:

- Adege (2026), *Maize Crop Disease (Leaf)*, Mendeley Data, V1, DOI: `10.17632/6w6gsvghfw.1`;
- Arun Pandian & Geetharamani (2019), plant-leaf-disease data, Mendeley Data, V1, DOI: `10.17632/tywbtsjrjv.1`;
- PlantVillage as described by Mohanty et al. (2016), downloaded from https://github.com/spMohanty/PlantVillage-Dataset as documented in the original notebook; the current upstream dataset card declares CC BY-SA 3.0. All 3,852 archived maize-source hashes match public commit 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a; the 1,498-image evaluation subset remains limited to blight/leaf spot after the recorded overlap audit;
- TOM2024 as described by Appiah et al. (2025), *Data in Brief* 59, 111357, DOI: `10.1016/j.dib.2025.111357`, with the underlying Mendeley Data record DOI `10.17632/3d4yg89rtr.1`;
- the operational components `CIMMYT_MLND`, `Kaggle_HEALTHY_up` and `Kaggle_Healthy_paren`, which are filename-pattern labels for images obtained within the Adege (2026) download above (CC BY 4.0 as declared by that aggregated collection); the record does not report their original contributors, so raw redistribution remains excluded.

These references document provenance at the level supported by the manuscript. They do **not** constitute a repository-wide licensing determination.

## TOM2024 rights review for Figure S7

The Mendeley Data record for TOM2024 (`10.17632/3d4yg89rtr.1`) explicitly identifies the dataset licence as **Creative Commons Attribution 4.0 International (CC BY 4.0)**. CC BY 4.0 permits sharing and adaptation provided appropriate attribution is given, a link to the licence is supplied, and changes are indicated.

Accordingly, the TOM2024 source images embedded in the manuscript-facing Grad-CAM composite may be redistributed as part of that derived figure under the licence conditions. The final repository figure is prepared as `figures/supplementary/Figure_S7_GradCAM_TOM2024_rust.pdf` (and PNG counterpart) and includes an in-figure attribution stating the TOM2024 source, dataset DOI, CC BY 4.0 status, and that the source images were modified by the displayed Grad-CAM overlays. This determination is **specific to the TOM2024 material used in Figure S7** and must not be generalized to the other third-party sources in the corpus.

Reference licence: `https://creativecommons.org/licenses/by/4.0/`.

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

No blanket data license is asserted for third-party image content. The original research **software code and associated software documentation** in this repository are published under the [MIT License](LICENSE), subject to the specific exclusions and conditions in [LICENSE_SCOPE.md](LICENSE_SCOPE.md). That license does **not** cover third-party image content, frozen data/splits/manifests, predictions, figures, or other scientific output. Any license for author-generated derived data must be established separately. The verified CC BY 4.0 status of TOM2024 applies only to the corresponding source material and derivative uses that comply with its attribution terms.

## Verified image traceability on 9 November 2026 UTC

The 5,605 CIMMYT/Kaggle-labeled images are not missing observations. All have complete local identity metadata and exact-content correspondence to the archived extraction; their experimental partition roles are 3,923 training, 842 validation and 840 test. The public Zenodo record contains the controlling manifests and extraction-membership crosswalk. See docs/SOURCE_TRACEABILITY.md, manifests/traceability_5605_summary.csv and docs/SOURCE_TRACEABILITY_VERIFICATION.json.

The original PlantVillage notebook contains the exact public clone URL and its completed output. A fresh comparison verified all 3,852 source-image hashes, all 1,498 evaluation images through their relative-path/source-hash mapping, and the 360 healthy correspondences. The current public dataset card declares CC BY-SA 3.0. That source attribution/license is distinct from the study authors' CC BY 4.0 scope for original derived data and does not grant a blanket license to other upstream image collections. No original photographs were added to the study archive during this verification.

The remaining limitation is the exact upstream component/mirror terms and collecting-institution/acquisition attribution for the historical CIMMYT/Kaggle components. A filename-derived label is not proof of collecting institution or country. The full local image and split traceability should not be described as absent merely because these upstream fields remain unresolved.
