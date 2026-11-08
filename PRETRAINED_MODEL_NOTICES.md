# Pretrained-model attribution and scope

Prepared 8 November 2026. These notices describe upstream records for release-resolved initialization identifiers. They do not assert that the original downloaded initialization binaries were independently hash-logged, and they do not relicense third-party weights or training images.

| Evaluated configuration | Release-resolved initialization | Upstream record / terms |
|---|---|---|
| MobileNetV3-Large | MobileNet_V3_Large_Weights.IMAGENET1K_V2 | Torchvision pretrained-weight terms; see the general pretrained-model notice below. |
| ResNet50 | ResNet50_Weights.IMAGENET1K_V2 | Torchvision pretrained-weight terms; see the general pretrained-model notice below. |
| EfficientNet-B0 | EfficientNet_B0_Weights.IMAGENET1K_V1 | Torchvision pretrained-weight terms; see the general pretrained-model notice below. |
| MobileViT-S | mobilevit_s.cvnets_in1k | The timm model card identifies a custom license and points to Apple's CVNets license. Preserve the applicable upstream notice and component terms. |
| ViT-Base/16 | vit_base_patch16_224.augreg2_in21k_ft_in1k | The timm model card identifies Apache-2.0. Preserve applicable notices and attribution. |
| Swin-Tiny | swin_tiny_patch4_window7_224.ms_in1k | The timm model card identifies MIT. Preserve applicable notices and attribution. |

The three torchvision identifiers were resolved from torchvision 0.26.0 defaults; timm identifiers were resolved from timm 1.0.15 defaults. These release-based resolutions are documented in the scientific recovery table, separately from the verified SHA-256 of each final fine-tuned checkpoint.

Torchvision's documentation distinguishes pretrained weights from library code and states that models may carry terms associated with their training data. A software-library license alone is therefore not a blanket license for all model assets. See [Torchvision pretrained-model documentation](https://docs.pytorch.org/vision/stable/models.html).

The [MobileViT model card](https://huggingface.co/timm/mobilevit_s.cvnets_in1k) refers to the [CVNets license](https://github.com/apple-aiml-research/ml-cvnets/blob/main/LICENSE). Its text permits use, modification and redistribution under its stated conditions, preserves applicable notices/disclaimers, and identifies separately licensed components. The short model-card label "other" is not a CC BY declaration. See also [ViT's model card](https://huggingface.co/timm/vit_base_patch16_224.augreg2_in21k_ft_in1k) and [Swin's model card](https://huggingface.co/timm/swin_tiny_patch4_window7_224.ms_in1k).

The proposed CC BY 4.0 license for the authors' original derived data/documentation must not be represented as replacing upstream licenses for pretrained or fine-tuned model components. The authors' original software remains within its stated MIT scope. Original maize photographs are not redistributed in the scientific data/code archive. Exact image-source terms and checkpoint redistribution conditions remain separate review items before publication.

These notices add attribution and clarify scope; they do not establish a completed legal clearance of every asset or a public checkpoint deposit.
