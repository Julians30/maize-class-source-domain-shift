# Supplementary-material reconciliation

The manuscript-referenced supplementary block is now analytically reconciled. The pre-submission Word copy contains **Table S18, Figure S5, Table S19, Figure S6, and Figure S7** in the correct order. The 15-page document was rendered after the final layout correction and visually inspected page by page.

## Ranking stability and selection loss

The four manuscript-facing architecture rankings are stored in `results/ranking_stability/architecture_domain_rank_matrix.csv`. Descending ranks are:

- EfficientNet-B0: internal 1, Pandian2019 2, PlantVillage 6, TOM2024 3.
- MobileNetV3-Large: 4, 3, 5, 2.
- MobileViT-S: 2, 4, 2, 5.
- ResNet50: 3, 6, 4, 1.
- Swin-Tiny: 6, 5, 1, 4.
- ViT-Base/16: 5, 1, 3, 6.

The rank sums yield `S = 10` and **Kendall W = 0.03571428571428571**. The chi-square approximation is 0.7142857142857142 with 5 degrees of freedom, giving **p ≈ 0.9821754508742055**.

Selecting EfficientNet-B0 solely by the highest mean internal E2-A macro-F1 produces exact losses relative to the best architecture within each external domain of 0.15816857440166499 in Pandian2019, 0.20719476353836469 in PlantVillage, and 0.092591070739056924 in TOM2024. `scripts/verify_ranking_stability.py` independently checks these outputs.

## Table S18 — TOM2024 classwise uncertainty

Authoritative source:

- `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`

The source contains 10,000-replicate stratified group-bootstrap intervals and reproduces the manuscript result that ResNet50 rust recall is 0.28368794326241137 with 95% interval 0.2127659574468085–0.35815602836879434.

**Status:** formatted Table S18 is inserted into the reconciled supplementary Word copy.

## Figure S5 — TOM2024 classwise uncertainty

Final files:

- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.pdf`
- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.png`

The figure displays recall and 95% stratified group-bootstrap intervals for the six architectures across fall-armyworm presence (n=581), healthy leaf (n=555), and rust (n=94). The PDF was rendered and visually inspected after generation.

**Status:** finalized, inserted in the supplementary Word copy, and hash-registered; repository binary transfer remains pending.

## Table S19 — training time / computational cost

Authoritative sources:

- `results/computational_cost/training_time_table_for_manuscript.csv`
- `results/computational_cost/training_time_summary_by_architecture.csv`

These contain the E2-A NVIDIA L4 timing summaries cited in Section 3.9.

**Status:** formatted Table S19 is inserted into the reconciled supplementary Word copy.

## Figure S6 — training-time / cost figure

The preserved candidate `Figure_l4_training_time_vs_macro_f1.pdf` was reconciled against the six architecture-level E2-A NVIDIA L4 timing rows and promoted without changing its bytes. The final PDF retains SHA-256 `791a7a2c650cebf007805dd7f791690a7199b3e32f8b4572e9933ddb2dcf66ca`.

Final files:

- `figures/supplementary/Figure_S6_training_time_vs_macro_f1.pdf`
- `figures/supplementary/Figure_S6_training_time_vs_macro_f1.png`

The figure was rendered and visually inspected. During final Word QA, its caption was corrected so it no longer states that horizontal error bars are displayed; the between-seed timing dispersion is instead explicitly referred to Table S19.

**Status:** finalized, inserted, and hash-registered; repository binary transfer remains pending.

## Figure S7 — full Grad-CAM panel

The preserved analysis contains four correct and four incorrect TOM2024 rust cases for ResNet50 seed 17. Release-safe metadata are stored in:

- `gradcam/gradcam_selected_cases_release.csv`
- `gradcam/gradcam_validated_records_release.csv`
- `gradcam/gradcam_final_summary_release.json`

The TOM2024 Mendeley Data record (`10.17632/3d4yg89rtr.1`) is documented as **CC BY 4.0**. The final manuscript-facing Grad-CAM composite embeds source attribution, licence identification, and a statement that Grad-CAM overlays modify the source images. The rights determination is specific to TOM2024 and does not extend to other corpus sources. Full reasoning is versioned in `docs/TOM2024_RIGHTS_REVIEW.md`.

Final files:

- `figures/supplementary/Figure_S7_GradCAM_TOM2024_rust.pdf`
- `figures/supplementary/Figure_S7_GradCAM_TOM2024_rust.png`

Expected SHA-256 values are `37e1fd652bb00cfeccd0491355f4407c14739d94d6d46853e38375852b2e610d` (PDF) and `8729048bd63a367a9b48181e8ffbbb7df8367a7a8793b9464779223a5ce85585` (PNG).

**Status:** rights reviewed, attribution embedded, final figure inserted in the supplementary Word copy, and hashes registered; repository binary transfer remains pending.

## Word-package QA

The reconciled supplementary copy is `Material_suplementario_Maiz_Q1_FINAL_REVISADO.docx`, SHA-256 `d2585effd67e84552bbab645d2a5816c5439dbf87fe43d0c617cc00cb73a805d`.

During QA, an initial construction defect was found: the S5/S6/S7 image paragraphs had been appended after the references instead of appearing with their sections. The OOXML block order was corrected so that:

1. Table S18 precedes its table and Figure S5 follows the S18 note;
2. Table S19 precedes its table and Figure S6 follows the S19 note;
3. Figure S7 appears inside S16 before the source-attribution paragraph;
4. the references remain at the end of the document.

After correction, all 15 rendered pages were inspected and no clipping, overlap, broken tables, or misplaced figures remained.

## Machine-checkable reconciliation

- `manifests/supplementary_reconciliation_expected_sha256.csv` registers the final S5/S6/S7 binary fingerprints.
- `scripts/verify_supplementary_reconciliation.py` verifies the authoritative sources and, in strict mode, requires all registered final figure files.
- `scripts/verify_ranking_stability.py` verifies the manuscript-facing Kendall W and internal-selection-loss outputs.

## Remaining submission placeholders

The supplementary Word copy intentionally retains only the repository DOI/URL placeholder because no public persistent identifier has yet been finalized. Do not invent or insert that identifier before the repository passes its strict release audit.
