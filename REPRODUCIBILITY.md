# Reproducibility plan

## Authoritative reporting layer

The current manuscript and current supplementary material define the reporting targets. Historical notebook/folder names such as `ARTICLE2`, legacy E3 split artifacts, or deprecated project branches are not treated as authoritative merely because they exist in the archive.

## Frozen experimental core

- 6 architectures: MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16, Swin-Tiny.
- 3 seeds: 17, 42, 73.
- 18 frozen E2-A runs.
- Internal E2-A test: 1,719 images.
- External domains used in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.

## Statistical reproducibility targets

The release package should support, where applicable:

1. internal/external metric reconstruction;
2. blocked architecture comparisons with seed as block;
3. restricted permutation inference;
4. paired bootstrap with 10,000 resamples for TOM2024;
5. Holm-adjusted pairwise contrasts;
6. architecture-ranking stability and selection-loss summaries;
7. classwise recall/F1/error-destination analyses;
8. class–source controls and source-classifier results;
9. calibration diagnostics;
10. Grad-CAM reproduction for the frozen exploratory analysis;
11. computational-cost summaries.

## Integrity requirements

Release assets should be accompanied by SHA-256 manifests. Frozen split and prediction files should not be regenerated after final statistical reconciliation. Where a historical artifact and a manuscript-facing reconciled asset differ, both the mapping and the reason for the difference must be documented.

The final repository-wide integrity layer is `manifests/release_sha256.csv`. It is generated only after all final release assets are committed, from Git index blobs rather than working-tree bytes. The manifest excludes itself to avoid circular hashing. `scripts/verify_release_manifest.py` then verifies exact coverage, byte counts, and SHA-256 values against the committed repository state.

Canonical sequence:

```bash
make verify
# transfer and commit every final release asset
make release-manifest
git add manifests/release_sha256.csv
git commit -m "Freeze repository-wide release SHA-256 manifest"
make release-check
```

## Release-safe notebooks

Notebooks intended for repository release should preserve code and Markdown while removing bulky execution outputs, embedded image outputs, credentials, local/private paths where avoidable, and any raw third-party image content not cleared for redistribution.
