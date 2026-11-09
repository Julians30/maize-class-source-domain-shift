# Repository status — 9 November 2026 (UTC)

**Public repository and published research-data record; manuscript under review at AgriEngineering.** DOI: https://doi.org/10.5281/zenodo.24064539. No editorial acceptance is claimed.

## Current revision

- Six evaluated configurations, five seeds (17/42/73/101/137), 30 selected checkpoints and 120 principal evaluations.
- Architecture selection by mean internal validation macro-F1; additional seeds and optimization checks are retrospective.
- Three external cohorts, two broad provenance families, different target class sets and metrics.
- Native comparisons completed for 1,164 strong candidate pairs, including 190 critical cross-partition pairs.
- Four exact critical RGB matches; 182 further assistant-supported pairs. The completed human record covers all 190 critical pairs: 189 same-photograph or transformation judgments and one related capture, none pending. Two contributors reviewed disjoint subsets (171 and 19); no independent double rating or agreement statistic is claimed. The four exact pairs are a subset of the 189 visual same-photograph judgments. The other 974 strong candidates were not visually adjudicated.
- Conservative exclusion sensitivities preserve the internal architecture orderings; they do not reconstruct clean training or checkpoint selection.
- Thirty checkpoint hashes verified. The data/code archive and all 30 checkpoints are published in Zenodo (31 files, 9,036,167,461 bytes). DOI resolution, DataCite registration and unauthenticated file access were verified. The complete public ZIP hash matched; checkpoint checks used public sizes/MD5 and 32-byte downloads, without downloading all model binaries in full again.

## Historical repository layer

The original three-seed/18-run registry, exact blocked internal test and canonical analysis modules remain unchanged as historical evidence. Repository CI audits this preserved layer. Passing those checks does not establish that the five-seed candidate or checkpoint binaries have been publicly released. The final repository-wide `manifests/release_sha256.csv` has not been frozen.

## Remaining work

1. Preserve the completed 190-pair critical-review record and private names/dates. Keep the remaining 974 noncritical strong candidates and biological-parent limits explicit; do not represent disjoint subsets as independent double assessment.
2. Preserve the verified public-release record and current file/member registries. The old six-layer `PENDING_AT_SUBMISSION` registry describes historical exports; those bytes are not claimed to be the current five-seed payload.
3. Retain the newly verified traceability of all 5,605 CIMMYT/Kaggle-labeled records and the recovered PlantVillage source (3,852 public binary hash matches). The current PlantVillage dataset card declares CC BY-SA 3.0. Keep the narrower unresolved upstream component terms and collecting-institution/acquisition attribution for the CIMMYT/Kaggle records explicit; see docs/SOURCE_TRACEABILITY.md.
4. Keep incomplete experiments explicit: confirmed-parent recovery/bootstrap, full closed-set/remapping analyses, and a clean training/selection reconstruction were not performed. The healthy-source prediction check is not a training ablation.
5. Freeze the final release manifest/tag only after the scientific package and public locators are final.

Use `make presubmission-check` for the historical repository checks. `make release-check` remains stricter and is not claimed to pass while the release requirements are incomplete. See `README.md`, `REPRODUCIBILITY.md`, `DATA_AVAILABILITY.md` and `DATA_RIGHTS.md`.

## Draft-upload recovery

`scripts/zenodo_draft_transfer.py` supplies recovery for an existing Colab upload session. It fetches the complete saved draft, checks the caller-specified ID and author list, accepts presentation-only title normalization, and can repair the same empty unpublished staging record with the prepared metadata. It resumes checksum-verified file transfer without creating another deposition, publishing, deleting, or storing credentials. The recovery helper passed 16 local simulated-response tests. The subsequent actual transfer completed and verified all 31 files in the draft. The record was later published and independently checked through unauthenticated public endpoints; see docs/CURRENT_PUBLIC_RELEASE.md. These are separate observations from the simulated tests.

## Draft metadata preparation

`scripts/zenodo_metadata.py` prepares readable descriptions, DOI reservation and explicit component license scope using the existing unpublished draft. It preserves authors and verified files, keeps a before/after metadata audit, and contains no publication, deletion or file-upload action. After correcting content negotiation and the numeric If-Match header, its guards and idempotence passed 18 local simulated-response tests. A subsequent actual execution updated and read back the draft metadata, retained all 31 verified files, and confirmed a reserved DOI. The user subsequently published the record; its current public status and DOI are verified. Component license declarations do not establish independent clearance of all third-party assets.

## Source evidence strengthened on 9 November 2026 UTC

All 5,605 component records reconcile across the published master, E2-A manifest and archived-extraction crosswalk, with complete filename, SHA-256, pHash, group and partition fields. Their roles are 3,923 train, 842 validation and 840 test. The original PlantVillage notebook records the clone URL and completed download; fresh public binaries match all 3,852 source hashes and support the 1,498 evaluation-file mapping and 360 healthy correspondences. No model training, inference or metric recalculation was performed. This evidence narrows the attribution limitation and corrects the earlier description of an unreconstructed PlantVillage mirror chain.
