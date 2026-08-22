# Recorded execution environment

This file records only environment details that are directly preserved in the frozen E2-A run registry. It is not a reconstructed full `pip freeze` and does not infer versions that were not recorded.

## Verified common environment across the 18 frozen E2-A runs

- GPU: NVIDIA L4
- Reported GPU memory: 22.0343 GiB
- PyTorch: 2.11.0+cu128
- timm: 1.0.15
- Training seeds: 17, 42, 73
- Frozen internal split sizes: train 8,043; validation 1,729; internal test 1,719
- External Pandian2019 component used by the registry: 1,922 images
- Balanced binary external subset recorded by the registry: 3,116 images

The authoritative machine-readable source is `manifests/e2_run_registry_v4.csv`, which also stores run-configuration hashes, checkpoint hashes, prediction-output hashes, parameter counts, best epochs, internal metrics, external rust metrics, and completion timestamps for all 18 runs.

## Parameter counts recorded in the registry

| Architecture | Parameters |
|---|---:|
| EfficientNet-B0 | 4,019,077 |
| MobileNetV3-Large | 4,213,561 |
| MobileViT-S | 4,943,401 |
| ResNet50 | 23,526,473 |
| Swin-Tiny | 27,526,275 |
| ViT-Base/16 | 85,805,577 |

## Reproducibility boundary

A complete package lock file should only be added if an authoritative preserved environment export is located. Until then, the versions above are the exact environment evidence available from the frozen run registry and should not be expanded by inference.
