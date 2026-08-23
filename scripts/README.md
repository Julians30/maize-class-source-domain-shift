# Scripts

Repository-level release and reproducibility checks operate on released manifests and derived analytical assets. They do not require access to unpublished raw-image folders.

## `audit_release_scope.py`

Checks that restricted/raw-image directory patterns and model checkpoint binaries are not accidentally committed, flags local-machine/Drive path references in release text, and verifies the current-stage core repository structure. With `--strict`, it additionally requires the full frozen master manifest, full E2-A manifest, notebook release audit, and final SHA-256 release manifest.

## `verify_core_claims.py`

Verifies machine-checkable manuscript-facing invariants from CSV files, including:

- 13,413 frozen images and 13,407 similarity groups;
- E2-A counts of 8,043 train / 1,729 validation / 1,719 test and 1,922 Pandian2019 external images;
- 18 unique architecture-seed checkpoint records using seeds 17, 42, and 73;
- internal architecture macro-F1 means;
- class-source association controls;
- TOM2024 confirmatory blocked-test statistics;
- ResNet50 TOM2024 rust-recall point estimate and 95% classwise bootstrap interval.

## Canonical release SHA-256 manifest

`build_release_manifest.py` creates `manifests/release_sha256.csv` only from Git-tracked index blobs, excluding the manifest itself. This makes the recorded byte counts and SHA-256 values independent of local checkout line-ending conversion. Canonical generation requires a clean working tree.

`verify_release_manifest.py` requires a clean working tree and checks that the committed manifest covers every tracked repository file except itself, contains no extra paths, and matches the exact Git-blob byte count and SHA-256 digest for each path.

Final release sequence:

```bash
# after all final release assets have been transferred and committed
make release-manifest
git add manifests/release_sha256.csv
git commit -m "Freeze repository-wide release SHA-256 manifest"
make release-check
```

## Local commands

```bash
make audit
make verify
make release-manifest
make verify-release-manifest
make release-check
```

`make release-check` is intentionally expected to fail until the large frozen manifests, release-safe notebooks, final analytical figures/predictions, and `manifests/release_sha256.csv` have all been transferred or generated as appropriate.
