# Supplementary-material reconciliation

The current supplementary Word document ends at **Table S17** and **Figure S4**, while the main manuscript cites additional assets in Sections 3.8–3.9 and in the Grad-CAM description. The analyses themselves are preserved in Drive; the Word supplement must be completed before submission.

## Missing manuscript-referenced assets

### Table S18 — TOM2024 classwise uncertainty

**Purpose in manuscript:** bootstrap 95% intervals for precision, recall, and F1 by confirmatory TOM2024 class and architecture.

**Authoritative source now identified:**

- `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`

This source contains 10,000-replicate stratified group-bootstrap intervals. It reproduces the manuscript statement that ResNet50 rust recall is approximately 0.2837 with 95% interval 0.2128–0.3582.

**Status:** source data located and transferred; formatted Table S18 still needs to be inserted into the supplementary Word document.

### Figure S5 — TOM2024 classwise uncertainty

**Purpose in manuscript:** visual counterpart to Table S18.

**Status:** underlying classwise bootstrap data are available. The manuscript-facing figure file must still be identified or regenerated from the authoritative CSV before release.

### Table S19 — training time / computational cost

**Authoritative sources now identified:**

- `results/computational_cost/training_time_table_for_manuscript.csv`
- `results/computational_cost/training_time_summary_by_architecture.csv`

These contain the E2-A NVIDIA L4 training-time summaries cited in Section 3.9.

**Status:** source data located and transferred; formatted Table S19 still needs to be inserted into the supplementary Word document.

### Figure S6 — training-time / cost figure

A preserved Drive figure named `Figure_l4_training_time_vs_macro_f1.pdf` has been located and is a candidate source for manuscript Figure S6. It should not be relabeled automatically until its plotted values and caption are checked against the current manuscript-facing training-time table.

**Status:** candidate identified; visual/content reconciliation pending.

### Figure S7 — full Grad-CAM panel

The preserved Grad-CAM analysis contains four correct and four incorrect TOM2024 rust cases for ResNet50 seed 17. Release-safe metadata are stored in:

- `gradcam/gradcam_selected_cases_release.csv`
- `gradcam/gradcam_validated_records_release.csv`
- `gradcam/gradcam_final_summary_release.json`

The composite PNG/PDF includes source image content and is therefore held pending source-rights review before a public release.

**Status:** analysis and metadata reconciled; figure-rights/release decision pending.

## Submission rule

Do not submit the supplement with references to S18/S19/S5/S6/S7 unresolved. Either add the final assets with matching numbering/captions or revise the main-manuscript cross-references consistently. The preferred route is to add the already-computed analyses, because the main manuscript currently relies on them.
