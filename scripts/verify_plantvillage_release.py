#!/usr/bin/env python3
"""Verify the release-safe filtered PlantVillage external-evaluation layer."""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "manifests/plantvillage_release_expected_sha256.csv"
LOCAL_PATTERNS = (
    re.compile(r"/content/drive/", re.I),
    re.compile(r"\bMyDrive\b", re.I),
    re.compile(r"TesisQ1_Maiz", re.I),
    re.compile(r"[A-Za-z]:\\\\Users\\\\", re.I),
    re.compile(r"/home/", re.I),
)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_csv(path: pathlib.Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not EXPECTED.is_file():
        print(f"ERROR: missing expected manifest: {EXPECTED.relative_to(ROOT)}")
        return 1
    with EXPECTED.open(newline="", encoding="utf-8-sig") as f:
        expected = list(csv.DictReader(f))

    errors: list[str] = []
    parsed: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    present = 0
    for item in expected:
        rel = item["path"]
        path = ROOT / rel
        if not path.is_file():
            if args.strict:
                errors.append(f"missing PlantVillage release asset: {rel}")
            continue
        present += 1
        if path.stat().st_size != int(item["bytes"]):
            errors.append(f"byte-size mismatch: {rel}")
        if sha256(path) != item["sha256"]:
            errors.append(f"SHA-256 mismatch: {rel}")
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if any(p.search(text) for p in LOCAL_PATTERNS):
            errors.append(f"private/local path remains in {rel}")
        fields, rows = parse_csv(path)
        parsed[rel] = (fields, rows)
        if len(rows) != int(item["rows"]):
            errors.append(f"row-count mismatch: {rel}")
        if len(fields) != int(item["columns"]):
            errors.append(f"column-count mismatch: {rel}")

    full_rel = "data/plantvillage/plantvillage_phash_full_release.csv"
    clean_rel = "data/plantvillage/plantvillage_clean_manifest_release.csv"
    overlap_rel = "data/plantvillage/plantvillage_overlap_audit_release.csv"
    eval_rel = "data/plantvillage/plantvillage_evaluation_manifest_release.csv"
    pred_rel = "predictions/plantvillage/plantvillage_filtered_predictions_release.csv"
    val_rel = "manifests/plantvillage_release_validation.csv"

    if full_rel in parsed:
        fields, rows = parsed[full_rel]
        if "logical_path" not in fields or any("absolute" in c.lower() for c in fields):
            errors.append("PlantVillage full pHash layer has unsafe/incorrect path schema")
        if len({r.get('logical_path') for r in rows}) != 3852:
            errors.append("PlantVillage full pHash layer does not contain 3,852 unique images")

    if clean_rel in parsed:
        fields, rows = parsed[clean_rel]
        if "logical_path" not in fields or "group_id" not in fields:
            errors.append("PlantVillage clean manifest schema is incomplete")
        if len({r.get('logical_path') for r in rows}) != 2522:
            errors.append("PlantVillage clean manifest does not contain 2,522 unique images")

    if overlap_rel in parsed:
        fields, rows = parsed[overlap_rel]
        if len(rows) != 1330:
            errors.append("PlantVillage overlap audit does not contain 1,330 rows")
        if "pv_logical_path" not in fields or any(c in fields for c in ("pv_path", "corpus_path")):
            errors.append("PlantVillage overlap audit has unsafe/incorrect path schema")

    if eval_rel in parsed:
        fields, rows = parsed[eval_rel]
        ids = {r.get('logical_path') for r in rows}
        groups = {r.get('group_id') for r in rows}
        classes = {r.get('true_class') for r in rows}
        if len(ids) != 1498 or len(groups) != 1490:
            errors.append("PlantVillage evaluation manifest does not match 1,498 images / 1,490 groups")
        if classes != {"leaf_blight", "leaf_spot"}:
            errors.append("PlantVillage evaluation manifest is not restricted to leaf_blight/leaf_spot")

    if pred_rel in parsed:
        fields, rows = parsed[pred_rel]
        if "logical_path" not in fields or "group_id" not in fields or "confidence" not in fields:
            errors.append("PlantVillage prediction release schema is incomplete")
        if any(c.startswith("prob_") for c in fields):
            errors.append("unexpected probability columns in PlantVillage release; preserved source did not contain full class-probability vectors")
        combos = {(r.get('arquitectura'), r.get('semilla')) for r in rows}
        ids = {r.get('logical_path') for r in rows}
        groups = {r.get('group_id') for r in rows}
        keys = {(r.get('arquitectura'), r.get('semilla'), r.get('logical_path')) for r in rows}
        if len(combos) != 18 or len(ids) != 1498 or len(groups) != 1490:
            errors.append("PlantVillage predictions do not match 18 runs / 1,498 images / 1,490 groups")
        if len(keys) != len(rows):
            errors.append("duplicate run-image rows in PlantVillage prediction release")

    if val_rel in parsed:
        fields, rows = parsed[val_rel]
        if len(rows) != 18:
            errors.append("PlantVillage validation table does not contain 18 runs")
        for r in rows:
            if int(float(r.get('private_path_occurrences','1'))) != 0:
                errors.append("PlantVillage validation reports a private path occurrence")
            for c in ('accuracy_abs_difference','macro_f1_abs_difference'):
                if float(r.get(c,'1')) > 1e-12:
                    errors.append(f"PlantVillage metric reconciliation exceeds tolerance in {c}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    if present == 0 and not args.strict:
        print("PlantVillage release assets not transferred yet; expected hashes are registered.")
    else:
        print(f"Verified {present}/{len(expected)} PlantVillage release assets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
