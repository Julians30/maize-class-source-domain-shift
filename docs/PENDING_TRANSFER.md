# Large and external release artifacts

## Current public release on 9 November 2026 UTC

The five-seed revision is published at https://doi.org/10.5281/zenodo.24064539. Its authoritative inventory is `manifests/zenodo_24064539_files.csv`, with ZIP-member hashes in `manifests/zenodo_24064539_archive_members.csv`; see `docs/CURRENT_PUBLIC_RELEASE.md` for verification scope. The current archive supplies recovered manifests, image-level prediction labels, validation outputs, analysis code and 30 separate checkpoints. Complete historical nine-output probability vectors are not claimed.

The original text below records the earlier three-seed/export preparation and recovery state. Its pending flags, unrecovered-source statements and proposed future deposit describe that historical stage. The current recovered master is `core_v7/manifests/manifest_master_clean_snapshot_v1_pre_split.csv` inside the public ZIP. No byte equivalence with historical expected exports is claimed; all six old registry layers remain historical. Original source images and private reviewer correspondence are not included in the public archive.

## Historical preparation record

The two canonical manuscript notebooks are already versioned under `notebooks/`; they are not pending.

## Pre-submission policy

Large derived artifacts are controlled by SHA-256 and may remain outside the private GitHub repository until the manuscript-submission archive is created. This is deliberate: GitHub is the code/review surface, while the persistent public archive will carry the large release payload.

See:

- `manifests/external_artifact_registry.csv`
- `docs/EXTERNAL_ARTIFACTS.md`
- layer-specific expected-SHA manifests under `manifests/`

## Revalidated sources

The preserved archive was re-audited on 2026-08-27. The E2-A split source, PlantVillage source layer, TOM2024 source layer and final main figures were re-located. The five main PDF figures matched their frozen hashes exactly. The training-time PDF also matched the final Figure S6 hash exactly.

The full source CSV for the master manifest was not re-located in the current search; its source size/hash and release derivation remain frozen in `manifests/manifest_release_derivation.csv`.

## Final public release

At manuscript submission, create the persistent archive, update the external registry with the real locator/DOI, complete rights decisions, and only then run the strict public-release gate.

Do not commit historical temporary `*_PENDING_ONLY.zip` bundles even if an old copy is located; only canonical unpacked release assets or the persistent archive should be cited.
