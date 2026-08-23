# Maize Class–Source Confounding and Domain Shift Benchmark

Reproducibility repository for the manuscript:

**Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**

## Scientific objective

This project evaluates whether high internal image-classification performance in maize disease and pest recognition remains reliable when class labels are entangled with source provenance and models are exposed to external domain shift.

The benchmark is designed around three connected questions:

1. **Class–source confounding:** how strongly are labels associated with image source/provenance, and can models exploit source-specific cues?
2. **Leakage-safe internal performance:** how stable are architecture comparisons after duplicate/similarity controls and frozen evaluation protocols?
3. **Architecture-selection stability under domain shift:** does the architecture selected from internal performance remain the best choice across independent external domains?

## Frozen experimental core

- **Master corpus:** 13,413 images in 13,407 similarity groups.
- **Architectures:** MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16, and Swin-Tiny.
- **Seeds:** 17, 42, and 73.
- **Frozen runs:** 18 architecture-seed combinations.
- **Principal internal evaluation:** E2-A, test `n = 1,719`.
- **External domains:** Pandian2019, filtered PlantVillage, and TOM2024.
- **Verified execution evidence:** NVIDIA L4, PyTorch `2.11.0+cu128`, timm `1.0.15`.

The frozen run registry is stored in `manifests/e2_run_registry_v4.csv` and records configuration hashes, checkpoint hashes, prediction hashes, parameter counts, best epochs, metrics, and execution metadata.

## Main reproducibility layers

The repository contains or is being finalized to contain:

- audited provenance and class–source control tables;
- frozen split and protocol metadata;
- release-safe notebooks with outputs and private paths removed;
- internal E2-A inference summaries and paired statistical analyses;
- exact blocked randomization for the internal architecture effect;
- paired bootstrap and Holm-adjusted architecture contrasts;
- calibration, selective-risk/AURC, and class-difficulty analyses;
- architecture-ranking stability and external selection-loss summaries;
- release-safe Pandian2019, PlantVillage, and TOM2024 evaluation layers;
- classwise TOM2024 uncertainty estimates;
- computational-cost evidence;
- analytical figures and release-safe Grad-CAM metadata;
- SHA-256 integrity manifests and release verification scripts.

## Manuscript-facing statistical checks

The internal E2-A macro-F1 architecture effect was reconciled with exhaustive blocked randomization using seed as the block. The observed statistic is `F(5,10) = 0.8250817599851454`. After exploiting global treatment-label symmetry, the complete assignment space contains `6!^2 = 518,400` distinct assignments; 270,135 are at least as extreme as observed, giving `p_exact = 0.52109375` (`p = 0.5211` in the manuscript).

Architecture ranking is not stable across the four evaluation axes. The descending rank matrix yields `Kendall W = 0.03571428571428571` with `p ≈ 0.9821754508742055`. EfficientNet-B0 is selected by mean internal E2-A macro-F1, but its external selection losses are approximately `0.1582` on Pandian2019, `0.2072` on PlantVillage, and `0.0926` on TOM2024. These results motivate reporting domain-specific robustness rather than declaring a single architecture universally best.

## Reproducibility commands

Development-stage checks:

```bash
make audit
make verify
```

After all final release assets are committed and the working tree is clean, freeze the canonical repository-wide SHA-256 manifest:

```bash
make release-manifest
git add manifests/release_sha256.csv
git commit -m "Freeze repository-wide release SHA-256 manifest"
make release-check
```

`manifests/release_sha256.csv` is generated from Git index blobs rather than working-tree bytes, so the integrity record is independent of local CRLF/LF conversion. The manifest excludes itself to avoid circular hashing.

## Data redistribution boundary

The repository does **not** automatically redistribute original third-party maize images. Image-level redistribution depends on the licensing and reuse terms of each source. Derived manifests, hashes, code, predictions, statistical outputs, and reproducibility metadata are handled separately from raw-image rights.

The TOM2024 source-rights review supporting the final Grad-CAM composite is documented separately and should not be generalized to other image sources.

## Software-environment boundary

No authoritative full E2-A `pip freeze` or lock file was preserved. The repository therefore reports only software/hardware versions directly evidenced by the frozen run registry and does not reconstruct unrecorded package versions.

## Repository status

**Private — pre-submission reconciliation in progress.**

The scientific core, statistical reconciliation, external-evaluation summaries, manuscript/supplement crosswalks, release-safe metadata, and integrity tooling are already versioned. Large release-safe manifests, prediction tables, notebooks, and final binary figures are being transferred in controlled layers before the strict release audit is allowed to pass.

See `STATUS.md` for the current release checklist, `REPRODUCIBILITY.md` for the reproducibility boundary, `DATA_RIGHTS.md` for redistribution constraints, and `DATA_AVAILABILITY.md` for the planned data-availability statement.

## Manuscript authority

When historical project artifacts conflict with the current manuscript or supplementary material, the current manuscript-facing reconciled analysis is the authoritative reporting layer. Historical files are retained outside the release package unless required for traceability.
