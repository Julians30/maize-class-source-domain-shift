# Supplementary-material reconciliation

The current supplementary Word document ends at **Table S17** and **Figure S4**, while the main manuscript cites additional assets in Sections 3.8–3.9 and in the Grad-CAM description. The analyses themselves are preserved and reconciled; the Word supplement still needs the final S18/S19/S5/S6/S7 insertion before submission.

## Ranking stability and selection loss

The four manuscript-facing architecture rankings are now stored in `results/ranking_stability/architecture_domain_rank_matrix.csv`. Descending ranks are:

- EfficientNet-B0: internal 1, Pandian2019 2, PlantVillage 6, TOM2024 3.
- MobileNetV3-Large: 4, 3, 5, 2.
- MobileViT-S: 2, 4, 2, 5.
- ResNet50: 3, 6, 4, 1.
- Swin-Tiny: 6, 5, 1, 4.
- ViT-Base/16: 5, 1, 3, 6.

The rank sums yield `S = 10` and **Kendall W = 0.03571428571428571**. The chi-square approximation is 0.7142857142857142 with 5 degrees of freedom, giving **p ≈ 0.9821754508742055**. This reproduces the manuscript's near-zero cross-domain rank concordance.

Selecting EfficientNet-B0 solely by the highest mean internal E2-A macro-F1 produces the following exact losses relative to the best architecture within each external domain: Pandian2019 0.15816857440166499 (19.0875%), PlantVillage 0.20719476353836469 (64.0314%), and TOM2024 0.092591070739056924 (12.1881%). These are stored in `results/ranking_stability/internal_selection_loss.csv`. `scripts/verify_ranking_stability.py` independently recomputes the rank concordance and selection losses from the machine-readable rank matrix.

## Missing manuscript-referenced assets

### Table S18 — TOM2024 classwise uncertainty

**Purpose in manuscript:** bootstrap 95% intervals for precision, recall, and F1 by confirmatory TOM2024 class and architecture.

**Authoritative source:**

- `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`

This source contains 10,000-replicate stratified group-bootstrap intervals. It reproduces the manuscript statement that ResNet50 rust recall is 0.28368794326241137 with 95% interval 0.2127659574468085–0.35815602836879434.

**Status:** source data located and versioned; formatted Table S18 still needs to be inserted into the supplementary Word document.

### Figure S5 — TOM2024 classwise uncertainty

A final manuscript-facing figure has now been generated directly from the authoritative classwise bootstrap table. It displays recall and 95% stratified group-bootstrap intervals for the six architectures across the three confirmatory categories: fall-armyworm presence (n=581), healthy leaf (n=555), and rust (n=94).

Prepared final files:

- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.pdf`
- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.png`

The PDF was rendered and visually inspected after generation. Its expected SHA-256 is `b9e5d25a957afa1f156e29d200be50a045debf1d4c7af2c53f12168b4a5a854a`.

**Status:** finalized and hash-registered; binary transfer to GitHub is pending.

### Table S19 — training time / computational cost

**Authoritative sources:**

- `results/computational_cost/training_time_table_for_manuscript.csv`
- `results/computational_cost/training_time_summary_by_architecture.csv`

These contain the E2-A NVIDIA L4 training-time summaries cited in Section 3.9.

**Status:** source data located and versioned; formatted Table S19 still needs to be inserted into the supplementary Word document.

### Figure S6 — training-time / cost figure

The preserved candidate `Figure_l4_training_time_vs_macro_f1.pdf` was reconciled against the six architecture-level E2-A NVIDIA L4 timing rows. The plotted x-axis is mean E2-A training time in minutes and the y-axis is mean internal macro-F1. The six source means are 201.4898, 228.6013, 223.5429, 263.3948, 305.7562, and 333.0950 minutes for EfficientNet-B0, MobileNetV3-Large, MobileViT-S, ResNet50, Swin-Tiny, and ViT-Base/16, respectively. The reconstructed total across 18 runs is approximately 77.794 GPU-hours.

The reconciled candidate is promoted under the final manuscript-facing filename **without changing its bytes**, so the final PDF retains SHA-256 `791a7a2c650cebf007805dd7f791690a7199b3e32f8b4572e9933ddb2dcf66ca`.

Prepared final files:

- `figures/supplementary/Figure_S6_training_time_vs_macro_f1.pdf`
- `figures/supplementary/Figure_S6_training_time_vs_macro_f1.png`

The final PDF was rendered and visually inspected after promotion.

**Status:** reconciled, promoted, and hash-registered; binary transfer to GitHub is pending.

### Figure S7 — full Grad-CAM panel

The preserved Grad-CAM analysis contains four correct and four incorrect TOM2024 rust cases for ResNet50 seed 17. Release-safe metadata are stored in:

- `gradcam/gradcam_selected_cases_release.csv`
- `gradcam/gradcam_validated_records_release.csv`
- `gradcam/gradcam_final_summary_release.json`

The composite PNG/PDF includes source image content and is therefore held pending source-rights review before a public release.

**Status:** analysis and metadata reconciled; figure-rights/release decision pending.

## Machine-checkable reconciliation

- `manifests/supplementary_reconciliation_expected_sha256.csv` registers the final S5/S6 binary fingerprints.
- `scripts/verify_supplementary_reconciliation.py` verifies the authoritative S5/S6 source tables and, when binaries are present, their byte sizes and SHA-256 values. Normal verification tolerates pending binary transfer; strict release mode requires all four final figure files.
- `scripts/verify_ranking_stability.py` verifies the manuscript-facing Kendall W and internal-selection-loss outputs.

## Submission rule

Do not submit the supplement with references to S18/S19/S5/S6/S7 unresolved. S5 and S6 are now analytically finalized, but their binaries and the formatted S18/S19 sections still need to be inserted into the final supplementary package. Figure S7 remains contingent on source-rights review. The repository must remain private until the complete release audit and the manuscript's data-sharing decision are finalized.
