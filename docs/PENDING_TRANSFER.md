# Large and external release artifacts

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
