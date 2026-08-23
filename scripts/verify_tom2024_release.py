#!/usr/bin/env python3
"""Verify release-safe TOM2024 manifest, protocol, checkpoint and prediction assets."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "manifests/tom2024_release_expected_sha256.csv"
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


def read_text(path: pathlib.Path, kind: str) -> str:
    if kind == "csv.gz":
        with gzip.open(path, "rt", encoding="utf-8-sig", errors="replace") as f:
            return f.read()
    return path.read_text(encoding="utf-8-sig", errors="replace")


def csv_schema(path: pathlib.Path, kind: str) -> tuple[list[str], list[dict[str, str]]]:
    if kind == "csv.gz":
        fh = gzip.open(path, "rt", newline="", encoding="utf-8-sig")
    else:
        fh = path.open(newline="", encoding="utf-8-sig")
    with fh:
        reader = csv.DictReader(fh)
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
    present = 0
    parsed: dict[str, tuple[list[str], list[dict[str, str]]]] = {}

    for item in expected:
        rel = item["path"]
        kind = item["kind"]
        path = ROOT / rel
        if not path.is_file():
            if args.strict:
                errors.append(f"missing TOM2024 release asset: {rel}")
            continue
        present += 1
        if path.stat().st_size != int(item["bytes"]):
            errors.append(f"byte-size mismatch: {rel}")
        if sha256(path) != item["sha256"]:
            errors.append(f"SHA-256 mismatch: {rel}")
        text = read_text(path, kind)
        if any(p.search(text) for p in LOCAL_PATTERNS):
            errors.append(f"private/local path remains in {rel}")
        if kind.startswith("csv"):
            fields, rows = csv_schema(path, kind)
            parsed[rel] = (fields, rows)
            if item["rows"] and len(rows) != int(item["rows"]):
                errors.append(f"row-count mismatch: {rel}")
            if item["columns"] and len(fields) != int(item["columns"]):
                errors.append(f"column-count mismatch: {rel}")
        elif kind == "json":
            try:
                json.loads(text)
            except json.JSONDecodeError:
                errors.append(f"invalid JSON: {rel}")

    manifest_rel = "data/external/tom2024/tom2024_maize_external_clean_frozen_v2_release.csv"
    if manifest_rel in parsed:
        fields, rows = parsed[manifest_rel]
        if "absolute_path" in fields or "zip_member" not in fields:
            errors.append("TOM2024 frozen release manifest has unsafe/incorrect path schema")
        if len({r.get("tom2024_external_id", "") for r in rows}) != 4622:
            errors.append("TOM2024 frozen release manifest does not contain 4,622 unique external IDs")
        if any(r.get("keep_external_v2", "").lower() not in {"true", "1"} for r in rows):
            errors.append("TOM2024 frozen release manifest contains non-retained rows")
        if any(r.get("exact_overlap_with_corpus", "").lower() in {"true", "1"} for r in rows):
            errors.append("TOM2024 frozen release manifest contains exact corpus overlap")
        if any(r.get("phash_overlap_with_corpus", "").lower() in {"true", "1"} for r in rows):
            errors.append("TOM2024 frozen release manifest contains pHash corpus overlap")

    raw_rel = "predictions/tom2024/tom2024_predictions_18_runs_release.csv.gz"
    if raw_rel in parsed:
        fields, rows = parsed[raw_rel]
        if "absolute_path" in fields or "zip_member" not in fields:
            errors.append("TOM2024 raw prediction release has unsafe/incorrect path schema")
        prob = [c for c in fields if c.startswith("prob_")]
        if len(prob) != 9:
            errors.append("TOM2024 raw prediction release must preserve nine probability columns")
        runs = {(r.get("model_key"), r.get("seed")) for r in rows}
        ids = {r.get("tom2024_external_id") for r in rows}
        if len(runs) != 18:
            errors.append("TOM2024 raw prediction release does not contain 18 runs")
        if len(ids) != 1833:
            errors.append("TOM2024 raw prediction release does not contain 1,833 unique images")
        keys = {(r.get("model_key"), r.get("seed"), r.get("tom2024_external_id")) for r in rows}
        if len(keys) != len(rows):
            errors.append("duplicate run-image rows in TOM2024 raw prediction release")

    protocol_pred_rel = "predictions/tom2024/tom2024_predictions_by_protocol_release.csv.gz"
    if protocol_pred_rel in parsed:
        fields, rows = parsed[protocol_pred_rel]
        if "absolute_path" in fields or "zip_member" not in fields or "true_class" not in fields:
            errors.append("TOM2024 protocol prediction release has unsafe/incorrect schema")
        prob = [c for c in fields if c.startswith("prob_")]
        if len(prob) != 9:
            errors.append("TOM2024 protocol prediction release must preserve nine probability columns")
        p1 = {r.get("tom2024_external_id") for r in rows if r.get("protocol") == "P1_directo_3_clases"}
        p2 = {r.get("tom2024_external_id") for r in rows if r.get("protocol") == "P2_directo_mas_actividad"}
        combos = {(r.get("protocol"), r.get("model_key"), r.get("seed")) for r in rows}
        if len(p1) != 1230 or len(p2) != 1833:
            errors.append("TOM2024 protocol image counts do not match frozen P1/P2 scope")
        if len(combos) != 36:
            errors.append("TOM2024 protocol prediction release does not contain 36 protocol-run combinations")
        keys = {(r.get("protocol"), r.get("model_key"), r.get("seed"), r.get("tom2024_external_id")) for r in rows}
        if len(keys) != len(rows):
            errors.append("duplicate protocol-run-image rows in TOM2024 prediction release")

    ck_rel = "manifests/tom2024_checkpoint_verification_release.csv"
    if ck_rel in parsed:
        fields, rows = parsed[ck_rel]
        if "checkpoint_path" in fields or "checkpoint_id" not in fields or "checkpoint_sha256" not in fields:
            errors.append("TOM2024 checkpoint release has unsafe/incorrect schema")
        if len(rows) != 18 or len({(r.get('model_key'), r.get('seed')) for r in rows}) != 18:
            errors.append("TOM2024 checkpoint verification does not contain 18 unique runs")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    if present == 0 and not args.strict:
        print("TOM2024 release assets not transferred yet; expected hashes are registered.")
    else:
        print(f"Verified {present}/{len(expected)} TOM2024 release assets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
