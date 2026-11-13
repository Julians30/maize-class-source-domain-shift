# Maize Class–Source Confounding and Domain Shift Benchmark

[![Repository audit](https://github.com/Julians30/maize-class-source-domain-shift/actions/workflows/repository-audit.yml/badge.svg?branch=main)](https://github.com/Julians30/maize-class-source-domain-shift/actions/workflows/repository-audit.yml) [![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

Reproducibility repository for **Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**.

**Editorial status (13 November 2026):** Accepted for publication in *AgriEngineering* (MDPI), as reported by the author. The post-review analyses MAIZ_14A–14T are documented in [post_review/maiz14](post_review/maiz14/README.md). A journal publication DOI has not been supplied; the separate, published Zenodo research archive is [10.5281/zenodo.24064539](https://doi.org/10.5281/zenodo.24064539). Acceptance is not presented as online publication.

## Current scientific reporting

The revised analysis evaluates six configurations: MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16 and Swin-Tiny. Five seeds (17, 42, 73, 101, 137) yield 30 selected checkpoints and 120 principal evaluation records. Architecture selection uses mean internal validation macro-F1. The two added seeds and optimization checks were retrospective, after earlier external results were known.

The provenance inventory contains 13,413 images, including 11,491 internal images and 1,922 Pandian2019 images recorded for bookkeeping. The original internal split has 1,729 validation and 1,719 test images. Three external cohorts (Pandian2019, filtered PlantVillage and TOM2024) represent two broad provenance families and different class sets/metrics. Scores across these tasks are not interchangeable, and ranking changes do not isolate a causal source effect.

## Overlap audit and limits

Historical SHA-256/perceptual-hash controls and exclusion of pregenerated augmentation did not detect every transformed copy. The later native-pixel audit completed 1,164 strong candidate-pair comparisons, including 190 critical cross-partition pairs. Four critical pairs have exact native-RGB equality under a rotation/reflection; assistant visual support for 182 additional pairs remains distinct from human adjudication.

The completed human record dated 8 November covers all 190 critical pairs: 189 same-photograph or transformation judgments and one related capture, with none pending. Two contributors reviewed disjoint subsets of 171 and 19 pairs; independent double rating of every pair and inter-rater agreement are not claimed. The four computationally exact critical pairs are included in the 189 visual same-photograph judgments. These are pair counts, not distinct-image or biological-parent counts. The other 974 strong candidates were not visually adjudicated. Private reviewer identities, notes and image galleries are not published here.

Conservative post hoc exclusions retain 1,656 validation and 1,631 test images and preserve the internal architecture orderings. This sensitivity uses existing selected checkpoints; it does not remove training exposure or reconstruct clean stopping/selection. External candidate-family weighting is a point-estimate sensitivity, not a confirmed-parent bootstrap correction. Biological leaf/plant/field/campaign identities remain incomplete.

## Historical code and current public release

The original three-seed/18-run scripts and registries are retained as historical evidence, including `manifests/e2_run_registry_v4.csv`. The historical blocked internal test (`p_exact = 0.52109375`) is not relabeled as a five-seed result. Current five-seed manifests, prediction labels, recovered validation outputs, statistical tables and sensitivity code are publicly archived at https://doi.org/10.5281/zenodo.24064539. The archive filename and its preparation README retain release-candidate wording; the Zenodo record is published.

The revised inference uses five observed seeds and a paired group/seed bootstrap with 5,000 resamples, raw and Holm-adjusted contrasts. Its groups remain the recorded historical groups; later audit dependencies are not silently treated as corrected. Closed-set and extended-cohort scoring, DINOv2 similarity families, a common-input-recipe sensitivity, the Pandian2019 parent lineage in PlantVillage and a three-seed retraining ablation of the PlantVillage-derived healthy component were added after review ([post_review/maiz14](post_review/maiz14/README.md)). Selective-risk analysis and a clean retraining/selection of all architectures are not claimed. Historical calibration/Grad-CAM material is identified by its original scope.

## Rights and availability

Original software is [MIT-licensed](LICENSE); see [LICENSE_SCOPE.md](LICENSE_SCOPE.md). MIT does not license third-party images or scientific data/figures. All 5,605 CIMMYT/Kaggle-labeled image identities and partition roles are reconciled with the archived extraction. Image-by-image comparison traces CIMMYT_MLND (3,228 of 3,229) and Kaggle_HEALTHY_up (1,667 of 1,667) to the Maize Imagery Dataset – Tanzania (Mduma and Mayo, Mendeley Data, DOI 10.17632/fkw49mz3xs.1, CC BY 4.0) and Kaggle_Healthy_paren (709 of 709) to PlantVillage (360 byte-identical copies, 349 horizontal mirrors); per-image acquisition metadata beyond those records remain unavailable. The PlantVillage download repository is recovered and all 3,852 source hashes match its public files; its current dataset card declares CC BY-SA 3.0. See [source traceability evidence](docs/SOURCE_TRACEABILITY.md); see `manifests/source_license_audit.csv` and [DATA_RIGHTS.md](DATA_RIGHTS.md). No source photograph collection is redistributed by the prepared data/code archive.

The 30 checkpoint files were verified against their recorded SHA-256 values and total 9,013,090,475 bytes. They are publicly deposited as separate files alongside the data/code ZIP. Public research record: [https://doi.org/10.5281/zenodo.24064539](https://doi.org/10.5281/zenodo.24064539). It contains the data/code ZIP and all 30 selected checkpoints (31 files; 9,036,167,461 bytes). See [current file registry](manifests/zenodo_24064539_files.csv), [archive-member inventory](manifests/zenodo_24064539_archive_members.csv) and [verification scope](docs/CURRENT_PUBLIC_RELEASE.md). The six-layer `external_artifact_registry.csv` is historical: its expected exports are not asserted to be byte-identical to the current five-seed files. Its old pending flags do not describe the current public release. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md), [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [STATUS.md](STATUS.md).

## Repository checks

Run `make presubmission-check` for the repository's historical code/integrity checks. Those checks do not by themselves validate the separate five-seed release candidate. `make release-check` is stricter and remains incomplete while release locators, rights decisions and the final repository-wide release manifest/tag are outstanding. An audit badge is not proof of public data availability or biological independence.
