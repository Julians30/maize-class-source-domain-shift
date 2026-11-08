# Maize Class–Source Confounding and Domain Shift Benchmark

[![Repository audit](https://github.com/Julians30/maize-class-source-domain-shift/actions/workflows/repository-audit.yml/badge.svg?branch=main)](https://github.com/Julians30/maize-class-source-domain-shift/actions/workflows/repository-audit.yml) [![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

Reproducibility repository for **Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**.

**Revision status, 8 November 2026:** under review at *AgriEngineering*. No acceptance, journal DOI, published Zenodo record or archive DOI is claimed.

## Current scientific reporting

The revised analysis evaluates six configurations: MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16 and Swin-Tiny. Five seeds (17, 42, 73, 101, 137) yield 30 selected checkpoints and 120 principal evaluation records. Architecture selection uses mean internal validation macro-F1. The two added seeds and optimization checks were retrospective, after earlier external results were known.

The provenance inventory contains 13,413 images, including 11,491 internal images and 1,922 Pandian2019 images recorded for bookkeeping. The original internal split has 1,729 validation and 1,719 test images. Three external cohorts (Pandian2019, filtered PlantVillage and TOM2024) represent two broad provenance families and different class sets/metrics. Scores across these tasks are not interchangeable, and ranking changes do not isolate a causal source effect.

## Overlap audit and limits

Historical SHA-256/perceptual-hash controls and exclusion of pregenerated augmentation did not detect every transformed copy. The later native-pixel audit completed 1,164 strong candidate-pair comparisons, including 190 critical cross-partition pairs. Four critical pairs have exact native-RGB equality under a rotation/reflection; assistant visual support for 182 additional pairs remains distinct from human adjudication.

A supplied human record dated 8 November covers the four previously unresolved critical pairs: three same-photograph transformations and one related capture. Human ratification remains pending for the other 186. These are pair counts, not distinct-image or biological-parent counts. Private reviewer identities and image galleries are not published here.

Conservative post hoc exclusions retain 1,656 validation and 1,631 test images and preserve the internal architecture orderings. This sensitivity uses existing selected checkpoints; it does not remove training exposure or reconstruct clean stopping/selection. External candidate-family weighting is a point-estimate sensitivity, not a confirmed-parent bootstrap correction. Biological leaf/plant/field/campaign identities remain incomplete.

## Historical code and current release candidate

The original three-seed/18-run scripts and registries are retained as historical evidence, including `manifests/e2_run_registry_v4.csv`. The historical blocked internal test (`p_exact = 0.52109375`) is not relabeled as a five-seed result. Current five-seed manifests, predictions, recovered validation outputs, statistical tables and sensitivity code have been prepared in a separate release candidate; their preparation does not establish public download availability.

The revised inference uses five observed seeds and a paired group/seed bootstrap with 5,000 resamples, raw and Holm-adjusted contrasts. Its groups remain the recorded historical groups; later audit dependencies are not silently treated as corrected. Selective-risk analysis, a complete closed-set/remapping sensitivity, embedding-based parent recovery, and clean retraining/selection are not claimed as completed. Historical calibration/Grad-CAM material is identified by its original scope.

## Rights and availability

Original software is [MIT-licensed](LICENSE); see [LICENSE_SCOPE.md](LICENSE_SCOPE.md). MIT does not license third-party images or scientific data/figures. Exact upstream terms for 5,605 internal CIMMYT/Kaggle-derived images and the historical PlantVillage mirror chain remain unresolved; see `manifests/source_license_audit.csv` and [DATA_RIGHTS.md](DATA_RIGHTS.md). No source photograph collection is redistributed by the prepared data/code archive.

The 30 checkpoint files were verified against their recorded SHA-256 values and total 9,013,090,475 bytes. They are separate from the data/code ZIP and still require an actual deposit and public-download verification. Existing `PENDING_AT_SUBMISSION` locators remain pending. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md), [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [STATUS.md](STATUS.md).

## Repository checks

Run `make presubmission-check` for the repository's historical code/integrity checks. Those checks do not by themselves validate the separate five-seed release candidate. `make release-check` is stricter and remains incomplete while release locators, rights decisions and the final release manifest are outstanding. An audit badge is not proof of public data availability or biological independence.
