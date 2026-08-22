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

## Local commands

```bash
make audit
make verify
make release-check
```

`make release-check` is intentionally expected to fail until the large frozen manifests, release-safe notebooks, and final release SHA-256 manifest have been transferred.
