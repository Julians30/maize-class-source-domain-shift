#!/usr/bin/env python3
"""Audit release notebooks for embedded outputs, attachments and private/obsolete tokens."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
FORBIDDEN = (
    "/content/drive",
    "mydrive",
    "tesisq1_maiz",
    "article2",
    "articulo2",
    "kaggle.json",
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require", action="store_true", help="Require at least one release notebook to be present.")
    args = ap.parse_args()

    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if not notebooks:
        if args.require:
            print("ERROR: no release notebooks are present")
            return 1
        print("PENDING: no release notebooks are present yet")
        return 0

    errors: list[str] = []
    for path in notebooks:
        try:
            nb = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot parse {path.name}: {exc}")
            continue

        outputs = 0
        attachments = 0
        text_parts: list[str] = []
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                outputs += len(cell.get("outputs", []))
                if cell.get("execution_count") is not None:
                    errors.append(f"execution_count not cleared in {path.name}")
            attachments += len(cell.get("attachments", {}))
            source = cell.get("source", [])
            text_parts.append("".join(source) if isinstance(source, list) else str(source))

        if outputs:
            errors.append(f"{path.name} contains {outputs} output object(s)")
        if attachments:
            errors.append(f"{path.name} contains {attachments} attachment(s)")

        lowered = "\n".join(text_parts).lower()
        for token in FORBIDDEN:
            if token.lower() in lowered:
                errors.append(f"forbidden token {token!r} found in {path.name}")

    if errors:
        for msg in sorted(set(errors)):
            print(f"ERROR: {msg}")
        return 1

    print(f"Notebook audit passed for {len(notebooks)} release notebook(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
