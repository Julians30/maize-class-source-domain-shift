# Manuscript-to-repository asset crosswalk

This document maps the current manuscript to repository assets. The current manuscript and supplementary material are the reporting authority. Historical project folder names such as `ARTICLE2_*` are development provenance only.

## Core design

| Manuscript element | Repository asset | Status |
|---|---|---|
| Frozen corpus: 13,413 images / 13,407 groups | `data/manifests/manifest_master_clean_snapshot_v1_resumen.csv` | available summary; full release-safe manifest prepared, pending large-file transfer |
| Source inclusion/exclusion audit | `data/provenance/inventario_fuentes_estado_auditoria_final.csv` | available |
| E2-A: 8,043 train / 1,729 validation / 1,719 test | `splits/e2a_split_summary.csv` | available summary; full release-safe manifest prepared, pending large-file transfer |
| E2-A manifest hashes | `manifests/e2a_split_integrity.csv`, `manifests/manifest_release_derivation.csv` | available |
| Frozen 18-run registry and output hashes | `manifests/e2_run_registry_v4.csv` | available |
| Six architectures | `protocol/model_architectures.csv` | available |
| Manuscript-facing protocol | `protocol/manuscript_aligned_protocol_v1.json` | available |
| TOM2024 label mapping and no-tuning rules | `protocol/tom2024_mapping_protocol_release.json` | available |
| 18 frozen checkpoint hashes | `manifests/checkpoints_tom2024_verified_release.csv` | available |
| Verified E2-A runtime evidence | `environment/README.md`, `manifests/e2_run_registry_v4.csv` | available: NVIDIA L4, PyTorch 2.11.0+cu128, timm 1.0.15 |

## Main results

| Manuscript result | Repository asset | Status |
|---|---|---|
| Strict integrity of all 18 internal prediction files | `results/final_inference/01_strict_prediction_validation.csv` | available |
| Per-run internal point metrics | `results/final_inference/02_point_metrics_by_run.csv` | available |
| Internal E2-A architecture means | `results/final_inference/03_point_summary_by_architecture.csv`, `results/internal/05_global_summary_by_architecture.csv` | available |
| Architecture macro-F1 bootstrap intervals | `results/final_inference/04_macro_f1_architecture_bootstrap_intervals.csv` | available |
| Paired architecture contrasts with Holm correction | `results/final_inference/05_pairwise_macro_f1_bootstrap_holm.csv` | available; no pair significant after Holm |
| Classwise internal F1 uncertainty | `results/final_inference/06_classwise_f1_bootstrap_intervals.csv` | available |
| Soft-voting ensemble intervals/comparisons | `results/final_inference/07_ensemble_bootstrap_intervals.csv`, `08_ensemble_vs_architectures_bootstrap.csv` | available |
| Selective-risk / AURC summaries | `results/final_inference/09_exact_aurc_and_risk_by_run.csv`, `10_exact_aurc_summary.csv` | available |
| Equal-frequency reliability summary | `results/final_inference/13_equal_frequency_reliability_summary.csv` | available |
| Class-level consensus difficulty | `results/final_inference/14_consensus_difficulty_by_class.csv` | available |
| Compact final-inference claim register | `results/final_inference/article2_final_inference_summary.json` | available |
| Class-source association and source-only baseline | `results/class_source/A_asociacion_clase_fuente.csv`, `A_baselines_solo_fuente.csv` | available |
| Global source-classification control | `results/class_source/B_metricas_fuente_sin_pesos.csv` | available |
| Fixed-label source-classification controls | `results/class_source/C_fuente_dentro_de_clase.csv` | available |
| Filtered PlantVillage external results | `results/external/plantvillage/B_resultados_plantvillage.csv` | available |
| Internal/Pandian/PlantVillage rank comparison | `results/external/plantvillage/C_comparacion_tres_ejes.csv` | available |
| PlantVillage error destinations | `results/external/plantvillage/C_destino_dominante_por_clase.csv` | available |
| TOM2024 blocked architecture effect | `results/external/tom2024/D_estadistica_bloqueada_TOM2024.csv` | available |
| TOM2024 classwise bootstrap uncertainty / Table S18 source | `results/external/tom2024/tom2024_classwise_bootstrap_ci.csv` | available |
| Training-time / Table S19 source | `results/computational_cost/training_time_table_for_manuscript.csv`, `training_time_summary_by_architecture.csv` | available |
| Main analytical figure captions and hashes | `figures/figure_captions.csv`, `figures/figure_fingerprints.csv` | available; binaries pending transfer |
| Grad-CAM selected cases and frozen/recomputed agreement | `gradcam/gradcam_selected_cases_release.csv`, `gradcam_validated_records_release.csv`, `gradcam_final_summary_release.json` | metadata available; image-bearing composite pending rights review |

## Large authoritative assets still pending transfer

The following preserved files are known or have release-safe versions prepared but are not yet stored in GitHub because they require large/binary transfer rather than the text-side connector:

- `manifest_master_clean_snapshot_v1_release.csv` — release-safe full frozen master corpus manifest;
- `e2a_adege_to_pandian_manifest_v1_release.csv` — release-safe full E2-A split manifest;
- E2-A per-image prediction/probability outputs for 18 runs;
- Pandian2019 per-image predictions;
- filtered PlantVillage manifest, overlap audit, and per-image predictions;
- TOM2024 frozen clean manifest and per-image prediction outputs;
- analytical figure PDF/PNG binaries whose SHA-256 values are already catalogued;
- release-safe notebooks.

These assets should be added through a dedicated pending-only transfer package after notebook and release-scope auditing. The Grad-CAM image-bearing composite is a separate rights decision and must not be bundled automatically.

## Important reconciliation rule

An older experimental protocol used the label `E3` for a different nine-class multisource split. In the current manuscript and supplement, `E3` is the filtered PlantVillage external evaluation. Historical E3 artifacts must never be presented as the manuscript-facing E3 analysis.
