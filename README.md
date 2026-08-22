# Maize Class–Source Confounding and Domain Shift Benchmark

Reproducibility repository for the manuscript:

**Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**

## Scope

This repository is being prepared to support a multi-source maize image-classification benchmark focused on class–source confounding, provenance auditing, leakage control, architecture-selection stability, and external domain shift.

The manuscript-level analysis uses six architectures (MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16, and Swin-Tiny), three training seeds (17, 42, and 73), and 18 frozen runs. The principal internal evaluation is E2-A. External evaluations include Pandian2019, a filtered PlantVillage subset, and TOM2024.

## Repository status

**Private / pre-submission preparation.** Files are being reconciled against the manuscript and supplementary material before release. Historical project folders and deprecated experiments are intentionally excluded unless they support a manuscript claim or reproducibility requirement.

## Planned reproducibility assets

- audited source/provenance manifests;
- frozen split manifests and protocol metadata;
- release-safe notebooks and scripts;
- per-image predictions and probabilities where redistribution is permitted;
- statistical outputs for blocked/permutation analyses, paired bootstrap, Holm-adjusted comparisons, ranking stability, classwise uncertainty, and calibration diagnostics;
- main and supplementary tables/figures;
- Grad-CAM reproducibility artifacts;
- SHA-256 integrity manifests and environment metadata.

## Data redistribution boundary

The repository will not automatically redistribute original third-party maize images. Image-level redistribution depends on the licensing and reuse terms of each source. Derived manifests, hashes, code, predictions, statistical outputs, and reproducibility metadata will be handled separately from raw image rights.

## Manuscript authority

When historical project artifacts conflict with the current manuscript or supplementary material, the current manuscript-facing analysis is treated as the authoritative reporting layer. Historical files are retained outside the release package unless needed for traceability.
