# Manuscript-to-repository asset crosswalk

This document maps the current manuscript to repository assets. The current manuscript and supplementary material are the reporting authority. Historical project folder names such as `ARTICLE2_*` are development provenance only.

## Core design

| Manuscript element | Repository asset | Status |
|---|---|---|
| Frozen corpus: 13,413 images / 13,407 groups | `data/manifests/manifest_master_clean_snapshot_v1_resumen.csv` | available summary; full manifest pending transfer |
| Source inclusion/exclusion audit | `data/provenance/inventario_fuentes_estado_auditoria_final.csv` | available |
| E2-A: 8,043 train / 1,729 validation / 1,719 test | `splits/e2a_split_summary.csv` | available summary; full manifest pending transfer |
| E2-A manifest hashes | `manifests/e2a_split_integrity.csv` | available |
| Six architectures | `protocol/model_architectures.csv` | available |
| Manuscript-facing protocol | `protocol/manuscript_aligned_protocol_v1.json` | available |
| TOM2024 label mapping and no-tuning rules | `protocol/tom2024_mapping_protocol_release.json` | available |
| 18 frozen checkpoint hashes | `manifests/checkpoints_tom2024_verified_release.csv` | available |

## Main results

| Manuscript result | Repository asset | Status |
|---|---|---|
| Internal E2-A architecture means (Table 6 internal column) | `results/internal/05_global_summary_by_architecture.csv` | available |
| Class-source association and source-only baseline (Section 3.2 / Table 4) | `results/class_source/A_asociacion_clase_fuente.csv`, `A_baselines_solo_fuente.csv` | available |
| Global source-classification control | `results/class_source/B_metricas_fuente_sin_pesos.csv` | available |
| Fixed-label source-classification controls | `results/class_source/C_fuente_dentro_de_clase.csv` | available |
| Filtered PlantVillage external results | `results/external/plantvillage/B_resultados_plantvillage.csv` | available |
| Internal/Pandian/PlantVillage rank comparison | `results/external/plantvillage/C_comparacion_tres_ejes.csv` | available |
| PlantVillage error destinations | `results/external/plantvillage/C_destino_dominante_por_clase.csv` | available |
| TOM2024 blocked architecture effect | `results/external/tom2024/D_estadistica_bloqueada_TOM2024.csv` | available |
| TOM2024 classwise bootstrap uncertainty | `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv` | available |
| Training-time summary | `results/computational_cost/training_time_table_for_manuscript.csv`, `training_time_summary_by_architecture.csv` | available |
| Grad-CAM selected cases and frozen/recomputed agreement | `gradcam/gradcam_selected_cases_release.csv`, `gradcam_validated_records_release.csv`, `gradcam_final_summary_release.json` | metadata available; image-bearing composite pending rights review |

## Large authoritative assets still pending transfer

The following preserved files are known but are not yet stored in GitHub because they are substantially larger than the text-side assets transferred through the connector:

- `manifest_master_clean_snapshot_v1_pre_split.csv` — frozen full master corpus manifest;
- `e2a_adege_to_pandian_manifest_v1.csv` — full E2-A split manifest;
- E2-A per-image prediction/probability outputs for 18 runs;
- Pandian2019 per-image predictions;
- filtered PlantVillage manifest, overlap audit, and per-image predictions;
- TOM2024 frozen clean manifest and per-image prediction outputs;
- release-safe notebooks.

These will be added through a dedicated pending-only transfer package after notebook and release-scope auditing.

## Important reconciliation rule

An older experimental protocol used the label `E3` for a different nine-class multisource split. In the current manuscript and supplement, `E3` is the filtered PlantVillage external evaluation. Historical E3 artifacts must never be presented as the manuscript-facing E3 analysis.
