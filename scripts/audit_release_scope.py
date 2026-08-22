#!/usr/bin/env python3
"""Audit repository release scope without requiring raw images or model checkpoints."""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

FORBIDDEN_DIR_NAMES = {
    "raw",
    "raw_images",
    "images_raw",
    "original_images",
    "datasets_raw",
    "restricted_images",
}
MODEL_EXTENSIONS = {".pt", ".pth", ".ckpt", ".onnx", ".safetensors"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json", ".yml", ".yaml", ".py", ".toml", ".cff", ".ipynb"}
LOCAL_PATH_PATTERNS = [
    re.compile(r"/content/drive/", re.I),
    re.compile(r"[A-Za-z]:\\\\Users\\\\", re.I),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="Also require final release-safe transfer assets.")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        lower_parts = {p.lower() for p in rel.parts}

        if lower_parts & FORBIDDEN_DIR_NAMES:
            errors.append(f"forbidden raw/restricted directory content: {rel}")
        if path.suffix.lower() in MODEL_EXTENSIONS:
            errors.append(f"model checkpoint/binary committed to repository: {rel}")
        if path.suffix.lower() in IMAGE_EXTENSIONS and rel.parts and rel.parts[0] in {"data", "splits", "predictions"}:
            errors.append(f"image file found in analytical-data path: {rel}")

        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(text):
                    # Reconciliation notes may mention historical local-path patterns descriptively.
                    if rel.as_posix() not in {"docs/RECONCILIATION_NOTES.md"}:
                        warnings.append(f"local machine/Drive path reference in {rel}")
                    break

    required_now = [
        "README.md",
        "DATA_RIGHTS.md",
        "DATA_AVAILABILITY.md",
        "REPRODUCIBILITY.md",
        "protocol/manuscript_aligned_protocol_v1.json",
        "splits/e2a_split_summary.csv",
        "manifests/e2a_split_integrity.csv",
        "manifests/e2_run_registry_v4.csv",
        "results/final_inference/01_strict_prediction_validation.csv",
        "results/final_inference/03_point_summary_by_architecture.csv",
        "results/final_inference/05_pairwise_macro_f1_bootstrap_holm.csv",
        "results/final_inference/07_ensemble_bootstrap_intervals.csv",
        "results/internal/05_global_summary_by_architecture.csv",
        "results/external/tom2024/D_estadistica_bloqueada_TOM2024.csv",
        "results/external/tom2024/tom2024_classwise_bootstrap_ci.csv",
        "figures/final_pdf_fingerprints_verified.csv",
        "manifests/notebook_release_audit.csv",
        "docs/MANUSCRIPT_ASSET_CROSSWALK.md",
        "docs/SUPPLEMENT_RECONCILIATION.md",
    ]
    for rel in required_now:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required current-stage file: {rel}")

    if args.strict:
        strict_required = [
            "data/manifests/manifest_master_clean_snapshot_v1_release.csv",
            "splits/e2a_adege_to_pandian_manifest_v1_release.csv",
            "notebooks/02_internal_comparison_E2A_release.ipynb",
            "notebooks/03_final_paired_inference_release.ipynb",
            "figures/main/Figure_1_three_axes_independence.pdf",
            "figures/main/Figure_2_external_performance_and_rank_reversal.pdf",
            "figures/main/Figure_3_error_destinations_pandian.pdf",
            "figures/main/Figure_4_error_destinations_plantvillage.pdf",
            "figures/main/Figure_5_reliability_diagram.pdf",
            "manifests/release_sha256.csv",
        ]
        for rel in strict_required:
            if not (ROOT / rel).is_file():
                errors.append(f"strict release requirement missing: {rel}")

    for msg in sorted(set(warnings)):
        print(f"WARNING: {msg}")
    if errors:
        for msg in sorted(set(errors)):
            print(f"ERROR: {msg}")
        return 1

    print("Release-scope audit passed" + (" (strict)." if args.strict else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
