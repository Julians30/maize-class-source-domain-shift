#!/usr/bin/env python3
"""Exactly verify the seed-blocked architecture effect on internal E2-A macro-F1."""
from __future__ import annotations

import csv
import itertools
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
POINTS = ROOT / "results/final_inference/02_point_metrics_by_run.csv"
RESULT = ROOT / "results/final_inference/internal_macro_f1_blocked_exact_randomization.csv"
ARCHS = (
    "EfficientNet-B0",
    "MobileNetV3-Large",
    "MobileViT-S",
    "ResNet50",
    "Swin-Tiny",
    "ViT-Base/16",
)
SEEDS = (17, 42, 73)
EXPECTED_F = 0.8250817599851454
EXPECTED_COUNT = 270135
EXPECTED_N = 518400
EXPECTED_P = 0.52109375


def read_points() -> list[list[float]]:
    with POINTS.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    lookup = {(r["architecture"], int(r["seed"])): float(r["macro_f1"]) for r in rows}
    if len(lookup) != 18:
        raise ValueError("expected 18 unique architecture-seed macro-F1 values")
    return [[lookup[(a, s)] for s in SEEDS] for a in ARCHS]


def blocked_f(y: list[list[float]]) -> float:
    t = len(y)
    b = len(y[0])
    flat = [v for row in y for v in row]
    gm = sum(flat) / len(flat)
    block_means = [sum(y[i][j] for i in range(t)) / t for j in range(b)]
    treat_means = [sum(row) / b for row in y]
    ss_total = sum((v - gm) ** 2 for v in flat)
    ss_block = t * sum((m - gm) ** 2 for m in block_means)
    ss_treat = b * sum((m - gm) ** 2 for m in treat_means)
    ss_error = ss_total - ss_block - ss_treat
    return (ss_treat / (t - 1)) / (ss_error / ((t - 1) * (b - 1)))


def exact_randomization(y: list[list[float]], f_obs: float) -> tuple[int, int]:
    # Under the randomized-complete-block null, treatment labels are permuted
    # independently within seed blocks. A common global treatment relabeling
    # leaves F invariant, so block 1 can be fixed and only blocks 2 and 3 need
    # exhaustive enumeration: 6!^2 = 518,400 distinct assignments.
    t = len(y)
    b = len(y[0])
    if (t, b) != (6, 3):
        raise ValueError("this exact verifier is defined for the frozen 6x3 design")

    gm = sum(v for row in y for v in row) / (t * b)
    ss_total = sum((v - gm) ** 2 for row in y for v in row)
    block_means = [sum(y[i][j] for i in range(t)) / t for j in range(b)]
    ss_block = t * sum((m - gm) ** 2 for m in block_means)
    col0 = [y[i][0] for i in range(t)]
    col1 = [y[i][1] for i in range(t)]
    col2 = [y[i][2] for i in range(t)]
    perms = tuple(itertools.permutations(range(t)))

    extreme = 0
    total = 0
    for p1 in perms:
        sums01 = [col0[i] + col1[p1[i]] for i in range(t)]
        for p2 in perms:
            treat_means = [(sums01[i] + col2[p2[i]]) / b for i in range(t)]
            ss_treat = b * sum((m - gm) ** 2 for m in treat_means)
            ss_error = ss_total - ss_block - ss_treat
            f = (ss_treat / (t - 1)) / (ss_error / ((t - 1) * (b - 1)))
            if f >= f_obs - 1e-13:
                extreme += 1
            total += 1
    return extreme, total


def main() -> int:
    errors: list[str] = []
    y = read_points()
    f_obs = blocked_f(y)
    if not math.isclose(f_obs, EXPECTED_F, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"observed blocked F mismatch: {f_obs}")

    extreme, total = exact_randomization(y, f_obs)
    p_exact = extreme / total
    if extreme != EXPECTED_COUNT or total != EXPECTED_N:
        errors.append(f"exact randomization count mismatch: {extreme}/{total}")
    if not math.isclose(p_exact, EXPECTED_P, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"exact randomization p mismatch: {p_exact}")

    with RESULT.open(newline="", encoding="utf-8-sig") as f:
        result_rows = list(csv.DictReader(f))
    if len(result_rows) != 1:
        errors.append("machine-readable reconciliation file must contain exactly one row")
    else:
        r = result_rows[0]
        checks = (
            (float(r["F_observed"]), f_obs, "stored F"),
            (float(r["p_exact"]), p_exact, "stored exact p"),
        )
        for actual, expected, label in checks:
            if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
                errors.append(f"{label} mismatch")
        if int(r["exact_extreme_assignments"]) != extreme or int(r["exact_unique_assignments"]) != total:
            errors.append("stored exact randomization counts mismatch")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    print(f"Exact internal blocked macro-F1 test verified: F(5,10)={f_obs:.12f}, p={p_exact:.8f} ({extreme}/{total}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
