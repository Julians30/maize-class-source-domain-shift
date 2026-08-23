#!/usr/bin/env python3
"""Build the canonical repository-wide SHA-256 release manifest.

The manifest is computed from Git index blobs rather than working-tree bytes so
line-ending conversion and local checkout settings cannot change the recorded
hashes. The manifest intentionally excludes itself to avoid a circular hash.

Release workflow:
  1. Transfer and commit all final release assets.
  2. Ensure the working tree is clean.
  3. Run: python scripts/build_release_manifest.py
  4. Review and commit manifests/release_sha256.csv.
  5. Run: python scripts/verify_release_manifest.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "manifests/release_sha256.csv"
OUTPUT_REL = OUTPUT.relative_to(ROOT).as_posix()


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )


def tracked_paths() -> list[str]:
    result = git("ls-files", "-z", text=False)
    paths = [p.decode("utf-8") for p in result.stdout.split(b"\0") if p]
    return sorted(p for p in paths if p != OUTPUT_REL)


def blob_digest(path: str) -> tuple[int, str]:
    proc = subprocess.Popen(
        ["git", "cat-file", "blob", f":{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    h = hashlib.sha256()
    n_bytes = 0
    for chunk in iter(lambda: proc.stdout.read(1024 * 1024), b""):
        n_bytes += len(chunk)
        h.update(chunk)
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"git cat-file failed for {path}: {stderr.strip()}")
    return n_bytes, h.hexdigest()


def require_clean_tree() -> None:
    status = git("status", "--porcelain=v1", "--untracked-files=all").stdout.strip()
    if status:
        raise RuntimeError(
            "working tree is not clean; commit or remove pending changes before "
            "building the canonical release manifest:\n" + status
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Development-only override; canonical release generation should use a clean tree.",
    )
    args = ap.parse_args()

    try:
        git("rev-parse", "--is-inside-work-tree")
        if not args.allow_dirty:
            require_clean_tree()
        paths = tracked_paths()
        if not paths:
            raise RuntimeError("no tracked repository files found")

        rows: list[dict[str, str | int]] = []
        for rel in paths:
            n_bytes, digest = blob_digest(rel)
            rows.append({"path": rel, "n_bytes": n_bytes, "sha256": digest})

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "n_bytes", "sha256"], lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        print(f"Wrote {OUTPUT_REL} with {len(rows)} tracked-file hashes.")
        print("The manifest excludes itself by design; review and commit it before strict verification.")
        return 0
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
