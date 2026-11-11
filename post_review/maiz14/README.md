# Post-review analyses MAIZ_14 (November 2026)

These analyses were run during the major revision of *AgriEngineering* manuscript agriengineering-4653844, after the reviewer reports. They use the 30 public checkpoints (Zenodo, DOI 10.5281/zenodo.24064539, each checked against its recorded SHA-256 before use) and, for the ablation, the hash-verified original training source. Nothing here replaces the five-seed principal results; each output is a sensitivity analysis reported in the Supplement.

| Notebook | Hardware | Supplement | Content |
|---|---|---|---|
| `notebooks/MAIZ_14A_Cierre_Parciales_GPU_L4.ipynb` | NVIDIA L4 | §S48–§S50, Tables S55–S59, Figures S8–S9 | Closed-set and extended-cohort scoring for PlantVillage and TOM2024; DINOv2 ViT-B/14 similarity families with class-stratified family bootstrap; Grad-CAM for all six architectures (seed 17) |
| `notebooks/MAIZ_14C_Preprocesamiento_GPU_L4.ipynb` | NVIDIA L4 | §S51, Tables S60–S62 | Every axis scored with both historical input recipes (centre crop; direct resize of the cached image) and Kendall's W under one common recipe |
| `notebooks/MAIZ_14T_Tanzania_CPU.ipynb` | CPU | §S52, Table S63 | Image-by-image comparison of the internal healthy and lethal_necrosis images with the Maize Imagery Dataset – Tanzania (Mduma and Mayo, Mendeley Data, DOI 10.17632/fkw49mz3xs.1) |
| `notebooks/MAIZ_14B2_Ablacion_Completa_3semillas_GPU_L4.ipynb` | NVIDIA L4 | §S54, Tables S65–S66 | EfficientNet-B0 retrained (seeds 17, 42, 73) without all 603 PlantVillage-derived healthy training and validation images; unchanged recipe, checkpoint selection on the reduced validation set |

The notebooks are written for Google Colab with the project folder mounted from Google Drive; they write a status file and checkpoints after each stage, so an interrupted session resumes where it stopped. Code is in `code/`; `code/inputs/` holds the evaluation manifests (file names, classes and hashes only, no images) and the archived argmax predictions used as an agreement gate.

## Main results

- **Reproduction gate.** Re-running the 30 public checkpoints with PyTorch 2.14.1 changes at most 2 of 1,498 PlantVillage and 1 of 1,230 TOM2024 argmax predictions per checkpoint relative to the archived predictions.
- **Pandian2019 lineage** (`code/pv_pandian_lineage.py`, `results/lineage/`). All 1,922 Pandian2019 rust images map to 1,146 PlantVillage rust parents at commit 7f7ecc7: 970 same-orientation copies (954 byte-identical) and 952 horizontal mirrors. Resampling parent families instead of images leaves the architecture ordering unchanged (Supplement §S47.2, Tables S51–S52).
- **Component tracing** (`results/14t_tanzania/`, `results/lineage/kaggle_healthy_paren_pv_lineage.csv`). CIMMYT_MLND (3,228 of 3,229) and Kaggle_HEALTHY_up (1,667 of 1,667) match the Tanzania dataset; Kaggle_Healthy_paren (709 of 709) matches PlantVillage as 360 byte-identical copies and 349 horizontal mirrors.
- **Input recipe** (`results/14c_input_recipe/`). On the 954 byte-identical rust images the two historical recipes change rust recall by 0.10–0.54 and change the leader. With one recipe for all axes, Kendall's W is 0.114 (centre crop) or 0.157 (direct resize), against 0.057 for the historical mix.
- **Healthy ablation** (`results/14b2_healthy_ablation/`). Removing the 603 images lowers the share of Pandian2019 rust images predicted healthy in every seed (mean 0.189 → 0.092) without a consistent rise in rust recall (+0.310, −0.090, −0.015); healthy recall falls on PlantVillage (0.999 → 0.941) and TOM2024 (0.864 → 0.751), and internal macro-F1 changes by at most 0.004.
- `results/manuscript_tables/` holds the derived tables cited in the revised manuscript (five-seed partial η², hierarchical-bootstrap raw p-values for Table S24 via `code/s24_raw_p.py`, recipe comparison and ablation summaries).

## Scope

These are retrospective sensitivity analyses on existing checkpoints, except the single-architecture ablation. They do not reconstruct a clean training and selection experiment for all architectures, do not establish plant-, field- or campaign-level independence, and do not establish causal use of source cues. Images from third-party datasets are not redistributed; Grad-CAM figures and DINOv2 contact sheets that contain source images are kept out of this repository.
