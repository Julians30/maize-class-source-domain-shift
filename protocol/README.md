# Protocol authority

The current manuscript and supplementary material are the reporting authority for this repository. Historical project protocol files are retained only for provenance and must not override manuscript-facing scenario definitions.

## Principal analysis

- E2-A: 9 classes; 8,043 train, 1,729 validation, 1,719 internal test images.
- Six architectures: MobileNetV3-Large, ResNet50, EfficientNet-B0, MobileViT-S, ViT-Base/16, Swin-Tiny.
- Seeds: 17, 42, 73.
- Checkpoint selection: highest validation macro-F1.
- External evaluations use the frozen E2-A checkpoints without retraining or fine-tuning.

## External domains in the current manuscript

- Pandian2019: 1,922 rust images.
- PlantVillage filtered: 1,498 images / 1,490 similarity groups, limited to Northern Corn Leaf Blight and Gray Leaf Spot after overlap auditing.
- TOM2024 confirmatory: 1,230 images from Healthy_leaf, Rust-D, and Spodoptera_frugiperda-P.
- TOM2024 sensitivity: 603 additional Spodotera_frugiperda-A images, reported separately as activity/damage sensitivity.

## Historical nomenclature warning

An older project protocol used the label E3 for a nine-class multisource split. In the current manuscript and supplement, E3 denotes the filtered PlantVillage external evaluation. Historical E3 files must therefore remain explicitly labeled as historical and are not the manuscript-facing E3 definition.

## Training recipe

The preserved protocol records ImageNet initialization, AdamW, learning rate 3e-4, weight decay 1e-4, a maximum of 40 epochs, 5% warm-up with cosine scheduling, effective batch size 64, class-weighted cross-entropy, label smoothing 0.10, and early stopping patience 8.

## Statistical design

The manuscript reports macro-F1 as the primary metric, architecture effects with seed as a block and restricted permutations, Kendall's W for ranking stability, paired bootstrap inference on TOM2024 with 10,000 resamples and Holm correction, classwise bootstrap intervals, and class-source association controls.
