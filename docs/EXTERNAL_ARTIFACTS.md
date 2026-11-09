# External artifact policy

## Current public release on 9 November 2026 UTC

The five-seed revision is published at https://doi.org/10.5281/zenodo.24064539. Its authoritative inventory is `manifests/zenodo_24064539_files.csv`, with ZIP-member hashes in `manifests/zenodo_24064539_archive_members.csv`; see `docs/CURRENT_PUBLIC_RELEASE.md` for verification scope. The current archive supplies recovered manifests, image-level prediction labels, validation outputs, analysis code and 30 separate checkpoints. Complete historical nine-output probability vectors are not claimed.

The original text below records the earlier three-seed/export preparation and recovery state. Its pending flags, unrecovered-source statements and proposed future deposit describe that historical stage. The current recovered master is `core_v7/manifests/manifest_master_clean_snapshot_v1_pre_split.csv` inside the public ZIP. No byte equivalence with historical expected exports is claimed; all six old registry layers remain historical. Original source images and private reviewer correspondence are not included in the public archive.

## Historical preparation record

## Purpose

This repository separates the **reviewer-facing analytical code** from large derived artifacts. All code, canonical notebooks, statistical summaries, integrity manifests and verification scripts are versioned in GitHub. Large derived manifests and image-level prediction tables are tracked by SHA-256 records. Publication or download availability for each artifact must be confirmed independently. No external archival deposit or DOI is claimed.

This policy does **not** apply to original third-party images. Raw-image redistribution remains governed by the source-specific rights documented in `DATA_RIGHTS.md`.

## Pre-submission state

The GitHub repository is public. Entries such as `PENDING_AT_SUBMISSION` in historical registries denote artifacts whose public availability has not been confirmed; they are not valid download links or DOIs.

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

For the current public pre-submission code package:

```bash
make presubmission-check
```

This validates the scientific/code layers and requires the external registry to remain in pre-submission mode.

For the eventual public release, the registry must be updated with the real persistent archive locator. `make release-check` intentionally remains stricter and must not be made green by inserting a placeholder DOI.

## Grad-CAM boundary

Figure S7 contains image-bearing Grad-CAM material. It remains a controlled rights decision and is not automatically redistributed merely because its analytical metadata and expected hashes are available.
