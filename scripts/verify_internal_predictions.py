#!/usr/bin/env python3
"""Verify release-safe per-image E2-A internal prediction files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "manifests/e2a_internal_prediction_expected_sha256.csv"
LOCAL_PATTERNS = (re.compile(r"/content/drive/", re.I), re.compile(r"[A-Za-z]:\\\\Users\\\\", re.I))


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    with EXPECTED.open(newline="", encoding="utf-8-sig") as f:
        expected = list(csv.DictReader(f))

    errors: list[str] = []
    present = 0
    for item in expected:
        path = ROOT / item["release_file"]
        if not path.is_file():
            if args.strict:
                errors.append(f"missing prediction file: {item['release_file']}")
            continue
        present += 1
        if path.stat().st_size != int(item["release_bytes"]):
            errors.append(f"byte-size mismatch: {item['release_file']}")
        if sha256(path) != item["release_sha256"]:
            errors.append(f"SHA-256 mismatch: {item['release_file']}")
        text = path.read_text(encoding="utf-8-sig")
        if any(p.search(text) for p in LOCAL_PATTERNS):
            errors.append(f"private/local path remains in {item['release_file']}")
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            rows = list(reader)
        if len(rows) != int(item["rows"]):
            errors.append(f"row-count mismatch: {item['release_file']}")
        if len(fields) != int(item["columns"]):
            errors.append(f"column-count mismatch: {item['release_file']}")
        if "path" in fields or "resolved_image_path" in fields or "logical_path" not in fields:
            errors.append(f"release-safe path schema mismatch: {item['release_file']}")
        prob = [c for c in fields if c.startswith("prob_")]
        if len(prob) != 9:
            errors.append(f"expected nine probability columns: {item['release_file']}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    if present == 0 and not args.strict:
        print("E2-A internal predictions not transferred yet; expected hashes are registered.")
    else:
        print(f"Verified {present}/{len(expected)} release-safe E2-A internal prediction files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
