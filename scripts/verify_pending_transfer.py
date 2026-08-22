#!/usr/bin/env python3
"""Verify size and SHA-256 of prepared pending-transfer assets when present."""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/pending_transfer_expected_sha256.csv"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-all", action="store_true", help="Fail when a pending-transfer asset is still missing.")
    args = ap.parse_args()

    with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        expected = list(csv.DictReader(f))

    errors: list[str] = []
    missing: list[str] = []
    verified = 0

    for r in expected:
        rel = r["path"]
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual_size = path.stat().st_size
        expected_size = int(r["n_bytes"])
        if actual_size != expected_size:
            errors.append(f"size mismatch for {rel}: expected {expected_size}, got {actual_size}")
            continue
        actual_hash = sha256(path)
        if actual_hash != r["sha256"]:
            errors.append(f"SHA-256 mismatch for {rel}")
            continue
        verified += 1

    for rel in missing:
        print(f"PENDING: {rel}")
    if args.require_all and missing:
        errors.append(f"{len(missing)} pending-transfer asset(s) are still missing")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}")
        return 1

    print(f"Pending-transfer verification passed for {verified}/{len(expected)} present asset(s).")
    if missing:
        print(f"{len(missing)} asset(s) remain pending; use --require-all for strict transfer validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
