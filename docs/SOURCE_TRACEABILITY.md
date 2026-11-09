# Image traceability and recovered PlantVillage source

Verified 9 November 2026 (UTC), using the existing public research record https://doi.org/10.5281/zenodo.24064539 and original project records. No training, inference or score recalculation was performed.

## All 5,605 component images are accounted for

| Operational component | Retained | Training | Validation | Test | Exact links to archived extraction |
|---|---:|---:|---:|---:|---:|
| CIMMYT_MLND | 3,229 | 2,260 | 485 | 484 | 3,229 |
| Kaggle_HEALTHY_up | 1,667 | 1,167 | 250 | 250 | 1,667 |
| Kaggle_Healthy_paren | 709 | 496 | 107 | 106 | 709 |
| Total | 5,605 | 3,923 | 842 | 840 | 5,605 |

The master manifest, experimental E2-A manifest and extraction-membership crosswalk agree on SHA-256 identity, filename, operational source, class, pHash and recorded group for every row. Each of the 5,605 has complete identity fields and an exact-content link to the archived extraction. The experimental partition is defined by evaluation_role, rather than inferred from historical local path strings. These are not missing or unaccounted observations.

The original 20 July component sheets record 3,231 initial MLN images, two exclusions and 3,229 retained images. The Adege-clean sheet records 4,443 initial and 3,451 retained images, including 2,376 healthy records in the two Kaggle-labeled components and 1,075 rust records in the two Adege-labeled components. The historical source closure separately documents exclusion of pregenerated augmentation. Those counts describe local component decisions and do not certify collecting institution or original mirror rights.

## Recovered PlantVillage acquisition evidence

The original notebook 13_plantvillage_segundo_dominio_externo.ipynb, SHA-256 5a128327b43c8a4a5d3b468644c5bd56b4289dd36697fde6a071633f1fb7559a, contains the clone command in cell index 3 and its completed output. It identifies https://github.com/spMohanty/PlantVillage-Dataset, selecting raw/color maize folders. Output counts are 513 leaf-spot, 1,192 rust, 985 blight and 1,162 healthy images: 3,852 total. The release-safe GitHub Python transcription had removed this shell command; its absence from that transcription did not establish absence from the original notebook.

A fresh binary comparison against public commit 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a matched every one of the 3,852 source SHA-256 values in the published archive. Relative paths join all 1,498 evaluation records to these verified source hashes. The historical evaluation manifest had empty SHA-256 fields; they were not treated as hashes. All 360 previously identified healthy correspondences also match the verified public source. The original checkout commit was not logged, so the new check documents present content identity at the stated commit rather than inventing that historical commit.

At that public commit, README_HF.md declares license: cc-by-sa-3.0. The source card is https://github.com/spMohanty/PlantVillage-Dataset/blob/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/README_HF.md. Preserve the source attribution and its applicable terms. This declaration is separate from CC BY 4.0 for the authors' original derived study data; source photographs were not added to the study archive. The earlier blanket statement that the PlantVillage mirror chain was unreconstructed is superseded by this recovered acquisition and content evidence.

## Remaining scope

The operational CIMMYT_MLND label was assigned from filename prefixes. Complete local identity tracing does not independently prove collecting institution, country, biological parent or the exact original component/mirror-license terms for the three historical components. The public multi-source collection cited by the study (Adege, DOI 10.17632/6w6gsvghfw.1) declares CC BY 4.0, but its metadata describe eight classes whereas the preserved local extraction has nine. Its declared license is therefore not automatically assigned to every earlier component or attributed creator. No unsupported institutional attribution, country, source version or license is substituted.

The 190 critical-pair human review, dependency sensitivities and existing prediction checks keep their previously reported scope. This reconciliation neither reconstructs clean training/selection nor supplies the unperformed causal healthy-training ablation or confirmed biological-parent bootstrap.

## Reproduce the reconciliation

Run:

```bash
python scripts/verify_source_traceability.py --output-dir source_evidence
```

The script downloads the exact public study ZIP, verifies SHA-256 4f4efbc585728442982f5784f07fd7b817383d89757393faed868443a652ca91 and writes the focused 5,605-row ledger, three-row summary and PlantVillage 1,498-row source mapping. To repeat the physical public-image comparison, supply --plantvillage-root pointing to raw/color from the checked public upstream commit. No original project Drive access is needed for the archived identity reconciliation. The recorded successful physical comparison is in PV_PUBLIC_SOURCE_VERIFICATION.json; the source/split checks are in SOURCE_TRACEABILITY_VERIFICATION.json. These reports distinguish stored identity reconciliation from a fresh raw-image check.
