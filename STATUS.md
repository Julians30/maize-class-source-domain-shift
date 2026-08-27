# Repository status

## Current state

**Private — pre-submission reproducibility hardening.**

The scientific results remain frozen. The repository now contains the canonical reviewer-facing internal E2-A comparison and final paired-inference code, together with machine-checkable provenance and SHA-256 integrity records. No model was retrained and no frozen result was regenerated during this repository hardening.

## Confirmed scientific core

- Frozen master corpus: 13,413 images / 13,407 similarity groups.
- Six architectures × three seeds = 18 frozen runs.
- Principal internal E2-A test: 1,719 images.
- External manuscript domains: Pandian2019, filtered PlantVillage, and TOM2024.
- Recorded E2-A execution evidence: NVIDIA L4, PyTorch `2.11.0+cu128`, timm `1.0.15`.
- Exact blocked internal macro-F1 architecture test: `F(5,10)=0.8250817599851454`, `p_exact=0.52109375` from 518,400 distinct assignments.
- Four-axis architecture-ranking stability and external selection-loss analyses are stored under `results/ranking_stability/`.

## Canonical code layer — versioned

Two release-safe notebooks are present:

- `notebooks/02_internal_comparison_E2A_release.ipynb`
- `notebooks/03_final_paired_inference_release.ipynb`

Their complete analytical source is stored under `scripts/analysis/` and `scripts/analysis/fragments/`. Integrity is recorded by:

- `manifests/canonical_code_provenance.csv`
- `manifests/canonical_fragment_sha256.csv`
- `manifests/notebook_release_audit.csv`

Run:

```bash
python scripts/verify_canonical_analysis_code.py
```

The historical protocol/split provenance code is also being consolidated under `scripts/analysis/`. Historical E3 split terminology is explicitly not the reporting authority: current manuscript E3 is the filtered PlantVillage external evaluation.

## Release-verification layer

Repository tooling checks release scope, notebook safety, canonical code integrity, manuscript-facing core claims, exhaustive blocked randomization, ranking stability, supplementary reconciliation, pending assets, internal E2-A predictions, Pandian2019, PlantVillage and TOM2024 layers, plus final repository-wide SHA-256 integrity.

The earlier TOM2024 CI failure was an integrity-manifest mismatch for `protocol/tom2024_mapping_protocol_release.json`; the expected byte count/SHA-256 record has been synchronized with the current audited release-safe protocol file. This correction changes repository integrity metadata, not statistical results.

## Remaining before final public release

- transfer remaining registered large release-safe manifests and final figure binaries;
- transfer registered per-image prediction layers that are still outside GitHub;
- finish consolidation/audit of the remaining historical analysis modules that support external-domain and interpretability provenance;
- run the full strict audit;
- generate and commit `manifests/release_sha256.csv` only after the final repository tree is stable;
- obtain author-confirmed CRediT roles and select a software licence;
- create the final release / persistent archive DOI only at manuscript-submission time.

No claim is made yet that the repository is a complete public release.
