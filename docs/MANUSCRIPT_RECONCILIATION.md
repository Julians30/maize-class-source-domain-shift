# Manuscript reconciliation

This note records the manuscript-facing changes made after the reproducibility audit. It is not a substitute for the manuscript; it documents how the reporting layer was aligned with the frozen analytical evidence.

## Internal E2-A architecture-effect p-value

The preserved development artifacts contained two nearby Monte Carlo restricted-permutation p-values for the same observed statistic: approximately 0.5198 and 0.5235495290. The observed blocked statistic itself was identical.

The complete blocked randomization space was therefore enumerated exactly. With six architectures and three seed blocks, global treatment-label symmetry yields `6!^2 = 518,400` distinct assignments. Of these, 270,135 produced `F >= F_observed`, with:

- `F(5,10) = 0.8250817599851454`
- `p_exact = 270135 / 518400 = 0.52109375`

The manuscript-facing Word copy now reports the rounded value `p = 0.5211` and explicitly identifies it as an exact restricted-randomization result. The conclusion is unchanged: no global architecture effect is detected for internal E2-A macro-F1.

Machine-readable source and verifier:

- `results/final_inference/internal_macro_f1_blocked_exact_randomization.csv`
- `scripts/verify_internal_blocked_exact.py`

## Supplementary cross-references

The manuscript references Table S18, Figure S5, Table S19, Figure S6, and Figure S7. These assets are now present in the reconciled supplementary Word copy and their analytical sources/hashes are documented in `docs/SUPPLEMENT_RECONCILIATION.md`.

## Unconfirmed metadata deliberately left pending

Two submission-time fields are intentionally not fabricated:

1. **Public repository DOI/URL.** The manuscript and supplement retain an explicit placeholder until the private repository passes the strict release audit and a public/persistent identifier is actually created.
2. **CRediT contributions.** Generic provisional author-role assignments were removed from the working manuscript. The current copy contains only a transparent pending marker until the authors confirm real roles.

## Current local Word fingerprints

- `Manuscrito_Maiz_ES_Q1_RECONCILIADO.docx`: SHA-256 `77e3dcc4a58950f1114f8ddb3b4fccde7a28cbc615c9adc828e6b1844c4b7354`.
- `Material_suplementario_Maiz_Q1_FINAL_REVISADO.docx`: SHA-256 `d2585effd67e84552bbab645d2a5816c5439dbf87fe43d0c617cc00cb73a805d`.

Both documents were rendered after their final edit batches. The manuscript contains 15 rendered pages; the supplement contains 15 rendered pages. All pages were visually inspected for clipping, overlap, broken tables, missing figures, and page-order defects.
