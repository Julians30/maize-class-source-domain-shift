# Repository status

## Current state

**Private — pre-submission reconciliation in progress.**

The repository has been initialized and aligned to the current maize manuscript and supplementary material. No claim is made yet that the repository is a complete public release.

## Confirmed manuscript core

- Frozen master corpus: 13,413 images and 13,407 similarity groups.
- Six architectures and three seeds (18 frozen runs).
- Principal internal evaluation: E2-A, test n = 1,719.
- External evaluations in the manuscript: Pandian2019, filtered PlantVillage, and TOM2024.
- Main statistical components: blocked/permutation analysis, paired bootstrap, Holm correction, ranking stability, classwise uncertainty, source-confounding controls, Grad-CAM exploration, and computational-cost analysis.

## Pending before release

- reconcile authoritative Drive assets against manuscript tables/figures;
- identify and package frozen E2-A manifests and prediction outputs;
- package external-domain prediction files and audit/exclusion manifests;
- package final statistical tables and figures;
- locate/reconcile supplementary Table S18, Table S19, Figure S5, Figure S6, and Figure S7 referenced by the manuscript;
- record runtime environment and package versions from preserved artifacts;
- generate SHA-256 release manifests;
- audit notebooks for release safety;
- verify data-rights boundaries source by source;
- run repository integrity checks;
- only then decide public visibility / persistent archive DOI.
