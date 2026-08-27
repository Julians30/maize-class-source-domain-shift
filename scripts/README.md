# Scripts

The repository separates **analysis code** from **release-verification code**.

## Manuscript analysis

`scripts/analysis/` contains manuscript-facing analytical entry points and preserved provenance code. The two canonical release analyses are:

- `02_internal_comparison_E2A_release.py`
- `03_final_paired_inference_release.py`

Their complete source is stored in sequential, syntax-valid fragments under `scripts/analysis/fragments/`. This keeps long notebook-derived analyses readable while preserving every analytical operation in version control.

`01_protocol_and_integrity_audit.py` and `02_split_generation_provenance.py` preserve historical protocol/split provenance. Historical E3 naming in the latter is explicitly non-authoritative for the current manuscript; current manuscript E3 is filtered PlantVillage external evaluation.

## Canonical-code audit

`verify_canonical_analysis_code.py` verifies:

- the two required release notebooks;
- the two canonical analytical entry scripts;
- every source-fragment SHA-256;
- Python syntax of entry scripts and fragments;
- cleared notebook outputs/execution counts;
- absence of private Drive/article-number tokens from reviewer-facing notebooks and code.

## Repository-level release checks

The remaining scripts audit release scope, manuscript-facing claims, exact blocked randomization, architecture-ranking stability, supplementary reconciliation, pending-transfer integrity, internal/Pandian/PlantVillage/TOM2024 release assets, and the final repository-wide SHA-256 manifest.

Development checks:

```bash
make audit
make verify
```

Final strict release sequence, only after every final registered asset is committed:

```bash
make release-manifest
git add manifests/release_sha256.csv
git commit -m "Freeze repository-wide release SHA-256 manifest"
make release-check
```
