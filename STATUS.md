# Repository status

## Current state

**Private — pre-submission reproducibility package.**

The scientific results are frozen. No model was retrained and no frozen result was regenerated during repository hardening.

## Pre-submission code status

- 2 canonical release-safe manuscript notebooks are versioned.
- Canonical internal comparison and final paired-inference source are SHA-256 audited.
- 10 provenance modules cover protocol/splits, dataloaders, E2 training/evaluation, 18-checkpoint evaluation, consolidated E2-A analysis, class–source shortcut control, PlantVillage, TOM2024, classwise uncertainty, Grad-CAM and computational time.
- Repository CI verifies canonical code, provenance code, core claims, exact blocked randomization, ranking stability, supplementary reconciliation and external-layer controlling manifests.

## Frozen scientific core

- master corpus: 13,413 images / 13,407 similarity groups;
- 6 architectures × 3 seeds = 18 frozen runs;
- principal internal E2-A test: 1,719 images;
- external manuscript domains: Pandian2019, filtered PlantVillage and TOM2024;
- exact blocked internal macro-F1 test: 518,400 distinct assignments, `p_exact = 0.52109375`.

## Large-artifact policy

Large release-safe prediction tables and manifests are **not required to be duplicated in GitHub during private pre-submission hardening**. Their exact release filenames, byte counts and SHA-256 values are controlled by repository manifests and mapped by `manifests/external_artifact_registry.csv`.

They are planned for a persistent Zenodo archive at manuscript submission. Until such a deposit exists, the registry must say `PENDING_AT_SUBMISSION`; no DOI is fabricated.

The five main PDF figures have been re-located and their frozen hashes revalidated. Figure S6 has also been reconciled by exact SHA-256. Figure S7 remains rights-controlled because it contains image-bearing Grad-CAM material.

## Commands

Current private pre-submission gate:

```bash
make presubmission-check
```

Normal development validation:

```bash
make verify
```

Final public-release gate, reserved for submission time:

```bash
make release-check
```

The final gate intentionally remains red until all final release requirements, public archive locators and rights decisions are satisfied.

## Remaining submission-time decisions

- select/confirm the software licence;
- confirm final author CRediT roles;
- create the persistent archive and record its actual DOI/locator;
- finalize the rights decision for image-bearing Figure S7;
- freeze the final repository-wide `manifests/release_sha256.csv`;
- create the release tag only when the manuscript submission package is final.
