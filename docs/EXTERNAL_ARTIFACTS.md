# External artifact policy

## Purpose

This repository separates the **reviewer-facing analytical code** from large derived artifacts. All code, canonical notebooks, statistical summaries, integrity manifests and verification scripts are versioned in GitHub. Large release-safe manifests and image-level prediction tables are controlled by SHA-256 manifests and are planned for a persistent Zenodo archive at manuscript submission.

This policy does **not** apply to original third-party images. Raw-image redistribution remains governed by the source-specific rights documented in `DATA_RIGHTS.md`.

## Pre-submission state

The repository is currently private. The public archive locator is intentionally recorded as `PENDING_AT_SUBMISSION`; no DOI is invented before a deposit exists.

`manifests/external_artifact_registry.csv` maps six controlled layers to their authoritative hash manifests:

1. core registered manifests / figures;
2. internal E2-A image-level predictions;
3. Pandian2019 image-level predictions;
4. filtered PlantVillage release layer;
5. TOM2024 release layer;
6. supplementary figure layer.

The registry contains **no private Drive URLs, account paths or local mount points**.

## Source revalidation performed on 2026-08-27

- the original E2-A split manifest was re-located in the preserved reconciliation archive;
- the source transformation for the 13,413-row master manifest remains frozen by `manifests/manifest_release_derivation.csv`;
- PlantVillage source manifests, pHash audit and 18-run prediction table were re-located;
- TOM2024 frozen evaluation sources and prediction layers were re-located;
- the five main PDF figures were re-located and matched their frozen SHA-256 values exactly;
- the training-time PDF matches the frozen final Figure S6 SHA-256 exactly.

The full source CSV corresponding to the master-manifest source hash was not re-located in the current Drive search. Its source byte count and SHA-256 remain frozen in `manifests/manifest_release_derivation.csv`; no replacement is fabricated.

## Checks

For the current private pre-submission package:

```bash
make presubmission-check
```

This validates the scientific/code layers and requires the external registry to remain in pre-submission mode.

For the eventual public release, the registry must be updated with the real persistent archive locator. `make release-check` intentionally remains stricter and must not be made green by inserting a placeholder DOI.

## Grad-CAM boundary

Figure S7 contains image-bearing Grad-CAM material. It remains a controlled rights decision and is not automatically redistributed merely because its analytical metadata and expected hashes are available.
