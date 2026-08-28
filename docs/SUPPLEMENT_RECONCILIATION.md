# Supplementary-material reconciliation

The current pre-submission Supplementary Material is analytically reconciled with the English main manuscript. It contains **Table S1–Table S21** and **Figure S1–Figure S7**. Reference numbers in the supplement reuse the numbered reference list of the main manuscript; no supplementary-only bibliography is introduced.

## Ranking stability and selection loss

The four manuscript-facing architecture rankings are stored in `results/ranking_stability/architecture_domain_rank_matrix.csv`. Descending ranks are:

- EfficientNet-B0: internal 1, Pandian2019 2, PlantVillage 6, TOM2024 3.
- MobileNetV3-Large: 4, 3, 5, 2.
- MobileViT-S: 2, 4, 2, 5.
- ResNet50: 3, 6, 4, 1.
- Swin-Tiny: 6, 5, 1, 4.
- ViT-Base/16: 5, 1, 3, 6.

The rank sums yield `S = 10` and **Kendall W = 0.03571428571428571**. The chi-square approximation is 0.7142857142857142 with 5 degrees of freedom, giving **p ≈ 0.9821754508742055**. The manuscript treats W as descriptive; the primary evidence of instability is the concrete architecture rank reversals.

Selecting EfficientNet-B0 solely by the highest mean internal E2-A macro-F1 produces exact losses relative to the best architecture within each external domain of 0.15816857440166499 in Pandian2019, 0.20719476353836469 in PlantVillage, and 0.092591070739056924 in TOM2024. `scripts/verify_ranking_stability.py` independently checks these outputs.

## Table S18 — TOM2024 classwise uncertainty

Authoritative source:

- `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv`

The source contains 10,000-replicate stratified group-bootstrap intervals and reproduces the manuscript result that ResNet50 rust recall is 0.28368794326241137 with 95% interval 0.2127659574468085–0.35815602836879434.

## Figure S5 — TOM2024 classwise uncertainty

Final files:

- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.pdf`
- `figures/supplementary/Figure_S5_TOM2024_classwise_recall_uncertainty.png`

The figure displays recall and 95% stratified group-bootstrap intervals for the six architectures across fall-armyworm presence (n=581), healthy leaf (n=555), and rust (n=94).

## Table S19 and Figure S6 — computational cost

Authoritative sources:

- `results/computational_cost/training_time_table_for_manuscript.csv`
- `results/computational_cost/training_time_summary_by_architecture.csv`

The preserved Figure S6 was reconciled against the six architecture-level E2-A NVIDIA L4 timing rows. Its final PDF SHA-256 is `791a7a2c650cebf007805dd7f791690a7199b3e32f8b4572e9933ddb2dcf66ca`.

## Figure S7 — full Grad-CAM panel

The preserved analysis contains four correct and four incorrect TOM2024 rust cases for ResNet50 seed 17. Release-safe metadata are stored in:

- `gradcam/gradcam_selected_cases_release.csv`
- `gradcam/gradcam_validated_records_release.csv`
- `gradcam/gradcam_final_summary_release.json`

The TOM2024 Mendeley Data record (`10.17632/3d4yg89rtr.1`) is documented as **CC BY 4.0**. The manuscript-facing composite embeds source attribution, license identification, and a statement that the Grad-CAM overlays modify the source images. Full reasoning is versioned in `docs/TOM2024_RIGHTS_REVIEW.md`.

Expected SHA-256 values remain `37e1fd652bb00cfeccd0491355f4407c14739d94d6d46853e38375852b2e610d` (PDF) and `8729048bd63a367a9b48181e8ffbbb7df8367a7a8793b9464779223a5ce85585` (PNG).

## Table S20 — source-license and redistribution audit

Table S20 explicitly separates **analytical inclusion** from **redistribution rights**. Verified public licenses are stated only when the source record could be confirmed. Historical local mirrors whose exact upstream chain could not be reconstructed remain under a conservative no-redistribution policy.

Important final reconciliation:

- CCMT is cited through Mensah et al. (2023), *Data in Brief* 49, 109306, DOI `10.1016/j.dib.2023.109306`.
- An unverified local CCMT Mendeley DOI is **not** asserted in the final supplement.
- Adege, Pandian2019, TOM2024, and Rahman dataset records remain identified by their verified public dataset DOI where applicable.
- PlantVillage local-mirror redistribution rights are not inferred beyond what can be traced.

## Table S21 — descriptive architecture–seed decomposition

Table S21 partitions sums of squares separately within each evaluation axis, using the frozen 6×3 architecture–seed grid:

| Axis | Architecture share | Seed share | Residual / unresolved |
|---|---:|---:|---:|
| Internal E2-A macro-F1 | 21.8% | 25.3% | 52.9% |
| Pandian2019 rust recall | 66.1% | 0.8% | 33.2% |
| PlantVillage macro-F1 | 34.7% | 9.0% | 56.3% |
| TOM2024 macro-F1 | 68.3% | 19.7% | 12.0% |

Authoritative inputs:

- `results/final_inference/02_point_metrics_by_run.csv`
- `results/external/plantvillage/B_resultados_plantvillage.csv`
- `results/external/tom2024/D_estadistica_bloqueada_TOM2024.csv`

The decomposition is descriptive and is not a substitute for additional seeds. Because there is one observation per architecture–seed cell, the residual also contains any non-estimable architecture×seed interaction.

## Final Word-package QA

The final English pre-submission package was checked after reference and language alignment:

- Main manuscript: 54 references, numbered by first appearance; abstract 193 words.
- Supplement: 17 rendered pages, Table S1–S21 and Figure S1–S7.
- Main and supplement were rendered page by page after the final edits.
- Accessibility audit: 0 high / 0 medium / 0 low findings in both final Word files.
- No scientific result, frozen checkpoint, split, or prediction output was modified during language/reference finalization.

## Machine-checkable reconciliation

- `manifests/supplementary_reconciliation_expected_sha256.csv` registers the S5/S6/S7 binary fingerprints.
- `scripts/verify_supplementary_reconciliation.py` verifies the authoritative sources and, in strict mode, requires all registered final figure files.
- `scripts/verify_ranking_stability.py` verifies the manuscript-facing Kendall W and internal-selection-loss outputs.

## Remaining submission placeholders

The project repository remains private during preparation. Reviewer access should be supplied through the journal-appropriate confidential mechanism at submission. The public persistent identifier must not be invented; it should be added only after the final public repository/Zenodo release has been created and passed the strict release audit.
