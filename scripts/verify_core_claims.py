#!/usr/bin/env python3
"""Verify machine-checkable manuscript-facing invariants from released CSV assets."""
from __future__ import annotations

import csv
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def rows(rel: str):
    with (ROOT / rel).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def fail(msg: str, errors: list[str]):
    errors.append(msg)


def main() -> int:
    errors: list[str] = []

    # Master-corpus summary.
    master = rows("data/manifests/manifest_master_clean_snapshot_v1_resumen.csv")
    if sum(int(r["n_images"]) for r in master) != 13413:
        fail("master summary does not sum to 13,413 images", errors)
    if sum(int(r["n_groups"]) for r in master) != 13407:
        fail("master summary does not sum to 13,407 groups", errors)

    # Principal E2-A split.
    split = {r["evaluation_role"]: r for r in rows("splits/e2a_split_summary.csv")}
    expected = {"train": 8043, "val": 1729, "test": 1719, "external_component_test": 1922}
    for role, n in expected.items():
        if role not in split or int(split[role]["n_images"]) != n:
            fail(f"E2-A split mismatch for {role}: expected {n}", errors)

    # Six architectures x three seeds.
    ck = rows("manifests/checkpoints_tom2024_verified_release.csv")
    pairs = {(r["architecture"], int(r["seed"])) for r in ck}
    if len(ck) != 18 or len(pairs) != 18:
        fail("checkpoint manifest must contain 18 unique architecture-seed runs", errors)
    if {int(r["seed"]) for r in ck} != {17, 42, 73}:
        fail("checkpoint manifest seeds are not exactly 17, 42, 73", errors)
    if len({r["architecture"] for r in ck}) != 6:
        fail("checkpoint manifest must contain six architectures", errors)

    # Internal architecture means supporting Table 6.
    internal = {r["architecture"]: r for r in rows("results/internal/05_global_summary_by_architecture.csv")}
    expected_internal = {
        "MobileNetV3-Large": 0.9565656641138238,
        "ResNet50": 0.9584699286425599,
        "EfficientNet-B0": 0.960112231951685,
        "MobileViT-S": 0.9599592546303608,
        "ViT-Base/16": 0.9558814704679198,
        "Swin-Tiny": 0.9529690433407598,
    }
    for arch, value in expected_internal.items():
        if arch not in internal or not close(float(internal[arch]["macro_f1_mean"]), value):
            fail(f"internal macro-F1 mismatch for {arch}", errors)

    # Class-source controls.
    assoc = rows("results/class_source/A_asociacion_clase_fuente.csv")[0]
    if not close(float(assoc["cramer_v"]), 0.759264595505191):
        fail("Cramer's V mismatch", errors)
    if not close(float(assoc["nmi"]), 0.7208605726365822):
        fail("normalized mutual information mismatch", errors)
    base = {r["predictor"]: r for r in rows("results/class_source/A_baselines_solo_fuente.csv")}
    if not close(float(base["solo_fuente_mayoritaria"]["mcc"]), 0.657142474017696):
        fail("source-majority baseline MCC mismatch", errors)

    # TOM2024 confirmatory architecture effect.
    tom = rows("results/external/tom2024/D_estadistica_bloqueada_TOM2024.csv")
    t = [r for r in tom if r["response"] == "macro_f1" and r["confirmatory"] == "True"]
    if len(t) != 1:
        fail("expected one confirmatory TOM2024 macro-F1 blocked-test row", errors)
    else:
        r = t[0]
        if not close(float(r["f_observed"]), 11.425900290765714):
            fail("TOM2024 confirmatory F mismatch", errors)
        if not close(float(r["p_permutation_restricted"]), 0.004199580041995801):
            fail("TOM2024 restricted-permutation p mismatch", errors)
        if not close(float(r["eta_squared"]), 0.6830122230031969):
            fail("TOM2024 eta-squared mismatch", errors)

    # Classwise rust result cited in manuscript.
    ci = rows("results/external/tom2024/tom2024_classwise_bootstrap_ci.csv")
    rr = [r for r in ci if r["architecture"] == "ResNet50" and r["class_name"] == "rust" and r["metric"] == "recall"]
    if len(rr) != 1:
        fail("ResNet50 rust recall CI row missing", errors)
    else:
        r = rr[0]
        if int(r["support"]) != 94:
            fail("TOM2024 rust support must be 94", errors)
        if not close(float(r["point_estimate_mean_over_seeds"]), 0.28368794326241137):
            fail("ResNet50 rust recall point estimate mismatch", errors)
        if not close(float(r["ci_lower"]), 0.2127659574468085) or not close(float(r["ci_upper"]), 0.35815602836879434):
            fail("ResNet50 rust recall CI mismatch", errors)
        if int(r["bootstrap_replicates"]) != 10000:
            fail("classwise bootstrap replicate count must be 10,000", errors)

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Core manuscript-facing claims verified from released assets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
