# Reconciliation notes

This file records discrepancies discovered while aligning preserved project artifacts with the current manuscript. The purpose is to prevent historical development outputs from silently overriding the reporting layer.

## 1. Scenario label `E3`

A historical protocol used `E3` for a nine-class multisource split. The current manuscript/supplement uses `E3` for the filtered PlantVillage external evaluation. The repository therefore treats the current manuscript definition as authoritative and labels the older meaning as historical only.

## 2. Internal blocked macro-F1 permutation p-value

The current manuscript reports the internal E2-A architecture effect for macro-F1 as approximately:

- F(5,10) = 0.8251
- restricted-permutation p = 0.5198

A preserved development artifact named `07_blocked_permutation_tests.csv` reproduces F = 0.8250817599851454 but reports restricted-permutation p = 0.5235495290094198 from 50,000 permutations.

Because these p-values are close but not identical, that historical CSV is **not currently promoted as the manuscript-authoritative inferential asset**. The discrepancy must be resolved by locating the exact final analysis/run or by regenerating the test from the frozen run-level metrics under the manuscript protocol. No value has been silently replaced in this repository.

## 3. Final-figure fingerprint reconciliation

The preserved Drive file `_figure_fingerprints.csv` predates the latest saved versions of the Pandian2019 and PlantVillage error-destination figures. Its entries for the older `Figure_3a_error_destinations_pandian.*` and `Figure_3b_error_destinations_plantvillage.*` files therefore must not be used as hashes for the current manuscript-facing PDFs `Figure_3_error_destinations_pandian.pdf` and `Figure_4_error_destinations_plantvillage.pdf`.

The current PDFs were downloaded directly from the final-figures folder and re-hashed. Their verified SHA-256 values are stored in `figures/final_pdf_fingerprints_verified.csv`. Figures 1, 2, and 5 agree with the preserved fingerprint catalog; the current Figures 3 and 4 have new verified hashes corresponding to their later saved files.

The candidate supplementary training-time figure is also fingerprinted there but remains explicitly marked as a candidate until its visual/content alignment with the manuscript-facing Table S19 is confirmed.

## 4. Grad-CAM release scope

The preserved full Grad-CAM composite embeds TOM2024 source-image content. Release-safe metadata have been deposited, but the image-bearing composite remains pending source-specific redistribution review.

## 5. Historical `ARTICLE2` naming

Folders and files with `ARTICLE2` in their historical names are not interpreted as a second publication. They are development artifacts from the same research project. Assets are included only when they substantively support the current manuscript and pass reconciliation checks. Release-safe notebooks remove this historical naming and replace private Drive paths with environment-variable/repository-relative configuration.
