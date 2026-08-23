#!/usr/bin/env python3
"""Verify manuscript-facing architecture-ranking stability and internal-selection loss."""
from __future__ import annotations

import csv
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RANKS = ROOT / "results/ranking_stability/architecture_domain_rank_matrix.csv"
SUMMARY = ROOT / "results/ranking_stability/kendall_w_summary.json"
LOSSES = ROOT / "results/ranking_stability/internal_selection_loss.csv"

EXPECTED_RANKS = {
    "EfficientNet-B0": (1, 2, 6, 3),
    "MobileNetV3-Large": (4, 3, 5, 2),
    "MobileViT-S": (2, 4, 2, 5),
    "ResNet50": (3, 6, 4, 1),
    "Swin-Tiny": (6, 5, 1, 4),
    "ViT-Base/16": (5, 1, 3, 6),
}
EXPECTED_W = 1.0 / 28.0
EXPECTED_P_APPROX = 0.9821754508742055
EXPECTED_SELECTED = "EfficientNet-B0"


def read_csv(path: pathlib.Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    errors: list[str] = []
    for p in (RANKS, SUMMARY, LOSSES):
        if not p.is_file():
            errors.append(f"missing ranking-stability asset: {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    rank_rows = read_csv(RANKS)
    if len(rank_rows) != 6:
        errors.append("rank matrix must contain six architectures")
    rank_by = {r["architecture"]: r for r in rank_rows}
    if set(rank_by) != set(EXPECTED_RANKS):
        errors.append("rank matrix architecture set mismatch")

    rank_cols = ("rank_internal", "rank_pandian", "rank_plantvillage", "rank_tom2024")
    for arch, expected in EXPECTED_RANKS.items():
        if arch not in rank_by:
            continue
        observed = tuple(int(rank_by[arch][c]) for c in rank_cols)
        if observed != expected:
            errors.append(f"rank mismatch for {arch}: {observed} != {expected}")

    m, n = 4, 6
    sums = [sum(int(r[c]) for c in rank_cols) for r in rank_rows]
    mean_sum = m * (n + 1) / 2
    S = sum((x - mean_sum) ** 2 for x in sums)
    W = 12 * S / (m * m * (n**3 - n))
    chi_square = m * (n - 1) * W
    if not close(W, EXPECTED_W):
        errors.append(f"Kendall W mismatch: {W}")

    with SUMMARY.open(encoding="utf-8") as f:
        summary = json.load(f)
    if not close(float(summary["kendall_W"]), W):
        errors.append("stored Kendall W does not match recomputation")
    if not close(float(summary["chi_square_approximation"]), chi_square):
        errors.append("stored chi-square approximation mismatch")
    if not close(float(summary["p_approx"]), EXPECTED_P_APPROX):
        errors.append("stored approximate p-value mismatch")

    internal_winner = max(rank_rows, key=lambda r: float(r["internal_macro_f1"]))["architecture"]
    if internal_winner != EXPECTED_SELECTED:
        errors.append(f"internal selection winner mismatch: {internal_winner}")
    metric_cols = {
        "Pandian2019": "pandian_rust_recall",
        "PlantVillage filtered": "plantvillage_macro_f1",
        "TOM2024 confirmatory": "tom2024_macro_f1",
    }
    losses = {r["external_domain"]: r for r in read_csv(LOSSES)}
    if set(losses) != set(metric_cols):
        errors.append("selection-loss domain set mismatch")
    for domain, col in metric_cols.items():
        if domain not in losses:
            continue
        best = max(rank_rows, key=lambda r: float(r[col]))
        selected = rank_by[EXPECTED_SELECTED]
        expected_loss = float(best[col]) - float(selected[col])
        expected_rel = expected_loss / float(best[col])
        row = losses[domain]
        if row["best_architecture"] != best["architecture"]:
            errors.append(f"best architecture mismatch for {domain}")
        if not close(float(row["absolute_loss"]), expected_loss):
            errors.append(f"absolute selection-loss mismatch for {domain}")
        if not close(float(row["relative_loss_fraction"]), expected_rel):
            errors.append(f"relative selection-loss mismatch for {domain}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Architecture ranking stability and internal-selection losses verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
