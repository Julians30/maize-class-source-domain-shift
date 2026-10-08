# Maize Class–Source Confounding and Domain Shift Benchmark

Reproducibility repository for:

**Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**

## Scientific objective

This benchmark tests whether high internal maize disease/pest classification performance remains reliable when labels are entangled with source provenance and architectures are exposed to independent domain shift.

The manuscript addresses:

1. class–source confounding and source shortcuts;
2. leakage-safe internal architecture comparison;
3. architecture-selection instability across external domains;
4. probabilistic reliability, selective risk and uncertainty under shift.

## Frozen experimental core

- 13,413 images / 13,407 similarity groups;
- MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16 and Swin-Tiny;
- seeds 17, 42 and 73;
- 18 frozen architecture-seed runs;
- principal internal E2-A test: 1,719 images;
- external domains: Pandian2019, filtered PlantVillage and TOM2024;
- recorded execution evidence: NVIDIA L4, PyTorch `2.11.0+cu128`, timm `1.0.15`.

The run registry is `manifests/e2_run_registry_v4.csv`.

## Statistical safeguards

The repository machine-checks the manuscript-facing inferential layer, including:

- exact blocked internal macro-F1 randomization using seed as block;
- 518,400 distinct assignments and `p_exact = 0.52109375`;
- paired inference and multiplicity control;
- architecture-ranking stability and external selection loss;
- bootstrap uncertainty;
- calibration/reliability and selective-risk analyses.

## Code organization

`notebooks/` contains the two canonical reviewer-facing notebooks.

`scripts/analysis/` contains the canonical analyses plus release-safe provenance modules for the full computational chain: protocol/splits, dataloaders, training/evaluation, 18-run evaluation, consolidated analysis, class–source control, PlantVillage, TOM2024, uncertainty, Grad-CAM and computational time.

`manifests/` contains frozen SHA-256 and provenance records.

## Validation

For the pre-submission verification package:

```bash
make presubmission-check
```

For routine development:

```bash
make verify
```

The public-release gate is intentionally stricter and is reserved for submission time:

```bash
make release-check
```

## Large derived artifacts

GitHub is the code/review surface. Large derived prediction tables and manifests are tracked in `manifests/external_artifact_registry.csv` with provenance and integrity information. Public availability of individual large artifacts must be verified against the repository contents and links before claiming that they can be downloaded. GitHub is the designated project code and documentation repository; no external archive or DOI is claimed.

Original third-party maize images are not automatically redistributed.

See `docs/EXTERNAL_ARTIFACTS.md`, `DATA_RIGHTS.md`, `REPRODUCIBILITY.md` and `STATUS.md`.

## Authority rule

When a historical project artifact conflicts with the current manuscript-facing reconciled analysis, the current reconciled manuscript layer is authoritative. Historical files are retained only as provenance and do not silently redefine the reporting protocol.
