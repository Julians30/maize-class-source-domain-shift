# Software license and research-data rights

This repository supports **Class–Source Confounding and Architecture-Selection Instability under Domain Shift: A Multi-Source Benchmark for Maize Disease and Pest Image Classification**, prepared for *AgriEngineering* (MDPI).

## MIT-licensed software

The [MIT License](LICENSE) applies to original software code and associated software documentation authored by the project contributors to the extent they hold the relevant rights. This includes the original analytical and verification Python code in `scripts/`, executable code in `notebooks/`, and repository automation scripts under `.github/workflows/`. Third-party code or bundled components, if any, remain subject to their own license terms. Preserve the MIT copyright and permission notice when redistributing the covered software.

## Materials NOT licensed under MIT

The MIT software license does **not** grant rights to original or derivative third-party maize images or to other non-software scientific assets, including:

- image data used from CCMT/CIMMYT, Kaggle, Adege, Pandian2019, PlantVillage and TOM2024; image reuse is governed by the corresponding providers and dataset licenses;
- frozen analytical identifiers, source and class labels, split assignments, data and integrity manifests under `data/`, `splits/`, and `manifests/`;
- numeric experimental outputs, predictions, statistical tables, figures and image-bearing Grad-CAM material under `results/`, `predictions/`, `tables/`, `figures/`, and `gradcam/`;
- scientific manuscript text and supplementary research material, unless separately licensed by their rights holders.

Original third-party images are not made reusable by the public visibility of this repository. The specific TOM2024 image/Grad-CAM rights determination in [DATA_RIGHTS.md](DATA_RIGHTS.md) remains subject to that source's **CC BY 4.0** terms, including attribution; it is not MIT-licensed.

## Data availability versus software licensing

The public GitHub repository provides software and documentation for review and computational reproducibility. Some large derived analytical assets may remain pending or may be available only subject to separate review; neither the presence of a manifest nor this MIT license should be understood as a downloadable data release. See [DATA_RIGHTS.md](DATA_RIGHTS.md), [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md), and [docs/EXTERNAL_ARTIFACTS.md](docs/EXTERNAL_ARTIFACTS.md).

No external archive or DOI is claimed. Scientific citation of the corresponding article and sources is appreciated, but is not an additional condition imposed by the MIT software license.
