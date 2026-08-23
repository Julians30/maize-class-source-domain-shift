#!/usr/bin/env python3
"""Verify manuscript-facing S5/S6 reconciliation and their authoritative source tables."""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "manifests/supplementary_reconciliation_expected_sha256.csv"
S5_SOURCE = ROOT / "results/external/tom2024/tom2024_classwise_bootstrap_ci.csv"
S6_SOURCE = ROOT / "results/computational_cost/training_time_summary_by_architecture.csv"


def read_csv(path: pathlib.Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    errors: list[str] = []

    if not S5_SOURCE.is_file():
        errors.append(f"missing S5 source: {S5_SOURCE.relative_to(ROOT)}")
    else:
        rows = read_csv(S5_SOURCE)
        recall = [r for r in rows if r.get("metric") == "recall"]
        architectures = {r["architecture"] for r in recall}
        classes = {r["class_name"] for r in recall}
        expected_arch = {"MobileNetV3-Large","ResNet50","EfficientNet-B0","MobileViT-S","ViT-Base/16","Swin-Tiny"}
        expected_classes = {"fall_armyworm","healthy","rust"}
        if len(rows) != 54 or len(recall) != 18:
            errors.append("S5 source must contain 54 metric rows and 18 recall rows")
        if architectures != expected_arch or classes != expected_classes:
            errors.append("S5 source architecture/class set mismatch")
        support = {r["class_name"]: int(r["support"]) for r in recall}
        if support != {"fall_armyworm":581,"healthy":555,"rust":94}:
            errors.append("S5 source support mismatch")
        if {int(r["bootstrap_replicates"]) for r in recall} != {10000}:
            errors.append("S5 source must use 10,000 bootstrap replicates")
        if {float(r["confidence_level"]) for r in recall} != {0.95}:
            errors.append("S5 source confidence level mismatch")
        rr = [r for r in recall if r["architecture"]=="ResNet50" and r["class_name"]=="rust"]
        if len(rr) != 1:
            errors.append("ResNet50 rust recall row missing from S5 source")
        else:
            r=rr[0]
            if not close(float(r["point_estimate_mean_over_seeds"]),0.28368794326241137):
                errors.append("ResNet50 rust recall point estimate mismatch")
            if not close(float(r["ci_lower"]),0.2127659574468085) or not close(float(r["ci_upper"]),0.35815602836879434):
                errors.append("ResNet50 rust recall interval mismatch")

    if not S6_SOURCE.is_file():
        errors.append(f"missing S6 source: {S6_SOURCE.relative_to(ROOT)}")
    else:
        rows = [r for r in read_csv(S6_SOURCE) if r.get("experiment") == "E2_A"]
        if len(rows) != 6:
            errors.append("S6 source must contain six E2-A architecture rows")
        if {r.get("hardware_hint") for r in rows} != {"NVIDIA L4"}:
            errors.append("S6 source hardware must be NVIDIA L4")
        expected_minutes = {
            "efficientnet_b0": 201.48980962617773,
            "mobilenetv3_large": 228.60128537269995,
            "mobilevit_s": 223.54290244925002,
            "resnet50": 263.3947771545113,
            "swin_tiny_patch4_window7_224": 305.75622057602226,
            "vit_base_patch16_224": 333.09498665006663,
        }
        by = {r["architecture"]: r for r in rows}
        if set(by) != set(expected_minutes):
            errors.append("S6 source architecture set mismatch")
        else:
            for arch, expected in expected_minutes.items():
                if not close(float(by[arch]["mean_total_minutes"]), expected):
                    errors.append(f"S6 mean training-time mismatch for {arch}")

    if not EXPECTED.is_file():
        errors.append(f"missing S5/S6 expected-hash manifest: {EXPECTED.relative_to(ROOT)}")
    else:
        expected = read_csv(EXPECTED)
        present = 0
        for item in expected:
            p = ROOT / item["path"]
            if not p.is_file():
                if args.strict:
                    errors.append(f"missing reconciled supplementary figure: {item['path']}")
                continue
            present += 1
            if p.stat().st_size != int(item["bytes"]):
                errors.append(f"byte-size mismatch: {item['path']}")
            if sha256(p) != item["sha256"]:
                errors.append(f"SHA-256 mismatch: {item['path']}")
        if not args.strict and present == 0:
            print("Reconciled Figure S5/S6 binaries are prepared but not transferred yet.")
        elif present:
            print(f"Verified {present}/{len(expected)} reconciled S5/S6 figure binaries.")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Supplementary S5/S6 source reconciliation verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
