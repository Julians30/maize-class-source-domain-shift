# Repository status — 8 November 2026

**Public repository; manuscript under review at AgriEngineering; current persistent research-data release pending.** No acceptance or DOI is claimed.

## Current revision

- Six evaluated configurations, five seeds (17/42/73/101/137), 30 selected checkpoints and 120 principal evaluations.
- Architecture selection by mean internal validation macro-F1; additional seeds and optimization checks are retrospective.
- Three external cohorts, two broad provenance families, different target class sets and metrics.
- Native comparisons completed for 1,164 strong candidate pairs, including 190 critical cross-partition pairs.
- Four exact critical RGB matches; 182 further assistant-supported pairs. The completed human record covers all 190 critical pairs: 189 same-photograph or transformation judgments and one related capture, none pending. Two contributors reviewed disjoint subsets (171 and 19); no independent double rating or agreement statistic is claimed. The four exact pairs are a subset of the 189 visual same-photograph judgments. The other 974 strong candidates were not visually adjudicated.
- Conservative exclusion sensitivities preserve the internal architecture orderings; they do not reconstruct clean training or checkpoint selection.
- Thirty checkpoint hashes verified; approximately 9 GB still require deposit and public-download verification.

## Historical repository layer

The original three-seed/18-run registry, exact blocked internal test and canonical analysis modules remain unchanged as historical evidence. Repository CI audits this preserved layer. Passing those checks does not establish that the five-seed candidate or checkpoint binaries have been publicly released. The final repository-wide `manifests/release_sha256.csv` has not been frozen.

## Remaining work

1. Preserve the completed 190-pair critical-review record and private names/dates. Keep the remaining 974 noncritical strong candidates and biological-parent limits explicit; do not represent disjoint subsets as independent double assessment.
2. Deposit the current scientific archive and 30 models, review rights/metadata, publish and verify real DOI/download links. Existing `PENDING_AT_SUBMISSION` entries remain accurate until then.
3. Verify or explicitly justify unresolved upstream terms for 5,605 internal CIMMYT/Kaggle-derived images and the historical PlantVillage mirror chain.
4. Keep incomplete experiments explicit: confirmed-parent recovery/bootstrap, full closed-set/remapping analyses, and a clean training/selection reconstruction were not performed. The healthy-source prediction check is not a training ablation.
5. Freeze the final release manifest/tag only after the scientific package and public locators are final.

Use `make presubmission-check` for the historical repository checks. `make release-check` remains stricter and is not claimed to pass while the release requirements are incomplete. See `README.md`, `REPRODUCIBILITY.md`, `DATA_AVAILABILITY.md` and `DATA_RIGHTS.md`.

## Draft-upload recovery

`scripts/zenodo_draft_transfer.py` supplies recovery for an existing Colab upload session. It fetches the complete saved draft, checks the caller-specified ID and author list, accepts presentation-only title normalization, and can repair the same empty unpublished staging record with the prepared metadata. It resumes checksum-verified file transfer without creating another deposition, publishing, deleting, or storing credentials. The helper was checked with 16 local simulated-response tests; this does not establish that the actual transfer or public release has completed. Public archive and checkpoint download verification remain pending.
