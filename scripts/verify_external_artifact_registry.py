#!/usr/bin/env python3
"""Verify the public-safe registry for large/external reproducibility artifacts."""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "manifests/external_artifact_registry.csv"

FORBIDDEN = (
    re.compile(r"drive\.google\.com", re.I),
    re.compile(r"/content/drive/", re.I),
    re.compile(r"\bMyDrive\b", re.I),
    re.compile(r"TesisQ1_Maiz", re.I),
    re.compile(r"sediment://", re.I),
    re.compile(r"private-user-images", re.I),
)
EXPECTED_LAYERS = {
    "core_registered_assets": 10,
    "internal_e2a_predictions": 18,
    "pandian2019_predictions": 18,
    "plantvillage_release": 7,
    "tom2024_release": 11,
    "supplementary_figures": 6,
}
HASH_LAYOUTS = (("path", "sha256"), ("release_file", "release_sha256"))


def read_csv(path: pathlib.Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--presubmission", action="store_true")
    mode.add_argument("--release", action="store_true")
    args = ap.parse_args()

    errors: list[str] = []
    if not REGISTRY.is_file():
        print("ERROR: missing manifests/external_artifact_registry.csv")
        return 1

    fields, rows = read_csv(REGISTRY)
    required = {
        "layer", "controlling_manifest", "expected_asset_count", "archive_policy",
        "presubmission_status", "planned_public_destination", "public_locator",
    }
    if not required.issubset(fields):
        errors.append("external artifact registry schema is incomplete")

    if {r.get("layer") for r in rows} != set(EXPECTED_LAYERS):
        errors.append("external artifact registry layer set mismatch")

    for row in rows:
        layer = row.get("layer", "")
        manifest_rel = row.get("controlling_manifest", "")
        manifest = ROOT / manifest_rel
        try:
            expected_count = int(row.get("expected_asset_count", "-1"))
        except ValueError:
            expected_count = -1
            errors.append(f"invalid expected_asset_count for {layer}")

        if expected_count != EXPECTED_LAYERS.get(layer):
            errors.append(f"registered asset count mismatch for {layer}")

        public_text = ",".join(str(v) for v in row.values())
        if any(pattern.search(public_text) for pattern in FORBIDDEN):
            errors.append(f"private/local locator leaked into registry row {layer}")

        if not manifest.is_file():
            errors.append(f"missing controlling manifest for {layer}: {manifest_rel}")
            continue

        manifest_fields, assets = read_csv(manifest)
        if len(assets) != expected_count:
            errors.append(
                f"{layer}: controlling manifest has {len(assets)} rows, expected {expected_count}"
            )

        layout = None
        for path_col, hash_col in HASH_LAYOUTS:
            if path_col in manifest_fields and hash_col in manifest_fields:
                layout = (path_col, hash_col)
                break
        if layout is None:
            errors.append(f"{layer}: controlling manifest lacks recognized path/hash columns")
        else:
            path_col, hash_col = layout
            rels = [asset.get(path_col, "") for asset in assets]
            hashes = [asset.get(hash_col, "") for asset in assets]
            if len(set(rels)) != len(rels) or any(not rel for rel in rels):
                errors.append(f"{layer}: empty or duplicate release paths")
            if any(not re.fullmatch(r"[0-9a-f]{64}", value or "") for value in hashes):
                errors.append(f"{layer}: malformed SHA-256 value")

        if row.get("planned_public_destination") != "Zenodo":
            errors.append(f"{layer}: planned public destination must be Zenodo")

        locator = row.get("public_locator", "")
        if args.presubmission and locator != "PENDING_AT_SUBMISSION":
            errors.append(f"{layer}: pre-submission locator must remain PENDING_AT_SUBMISSION")
        if args.release:
            if locator == "PENDING_AT_SUBMISSION" or not locator:
                errors.append(f"{layer}: public locator still pending at release")
            elif not (
                locator.lower().startswith("doi:")
                or locator.lower().startswith("https://doi.org/")
                or locator.lower().startswith("https://zenodo.org/")
            ):
                errors.append(f"{layer}: unrecognized public archive locator")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    mode_name = "release" if args.release else "pre-submission" if args.presubmission else "structural"
    print(
        f"External artifact registry verified in {mode_name} mode: "
        f"{len(rows)} layers / {sum(EXPECTED_LAYERS.values())} registered assets."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
