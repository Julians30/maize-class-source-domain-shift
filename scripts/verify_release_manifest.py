#!/usr/bin/env python3
"""Verify the canonical repository-wide SHA-256 release manifest.

Verification is performed against Git index blobs so results are independent of
checkout line-ending conversion. The manifest must cover every tracked file
except itself, with exact byte counts and SHA-256 digests.
"""
from __future__ import annotations

import csv
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/release_sha256.csv"
MANIFEST_REL = MANIFEST.relative_to(ROOT).as_posix()


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
    return sorted(p for p in paths if p != MANIFEST_REL)


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
            "working tree is not clean; strict release verification requires a stable checkout:\n" + status
        )


def main() -> int:
    try:
        git("rev-parse", "--is-inside-work-tree")
        require_clean_tree()
        if not MANIFEST.is_file():
            raise RuntimeError(f"missing release manifest: {MANIFEST_REL}")

        with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["path", "n_bytes", "sha256"]:
                raise RuntimeError(
                    "release manifest columns must be exactly: path,n_bytes,sha256"
                )
            rows = list(reader)

        manifest_paths = [r["path"] for r in rows]
        duplicates = sorted({p for p in manifest_paths if manifest_paths.count(p) > 1})
        if duplicates:
            raise RuntimeError("duplicate manifest paths: " + ", ".join(duplicates))

        tracked = tracked_paths()
        tracked_set = set(tracked)
        manifest_set = set(manifest_paths)

        errors: list[str] = []
        for rel in sorted(tracked_set - manifest_set):
            errors.append(f"tracked file missing from manifest: {rel}")
        for rel in sorted(manifest_set - tracked_set):
            errors.append(f"manifest contains non-tracked or excluded file: {rel}")

        for row in rows:
            rel = row["path"]
            if rel not in tracked_set:
                continue
            try:
                expected_size = int(row["n_bytes"])
            except ValueError:
                errors.append(f"invalid n_bytes for {rel}: {row['n_bytes']!r}")
                continue
            expected_hash = row["sha256"].lower()
            if len(expected_hash) != 64 or any(c not in "0123456789abcdef" for c in expected_hash):
                errors.append(f"invalid SHA-256 for {rel}: {row['sha256']!r}")
                continue
            actual_size, actual_hash = blob_digest(rel)
            if actual_size != expected_size:
                errors.append(
                    f"size mismatch for {rel}: expected {expected_size}, got {actual_size}"
                )
            if actual_hash != expected_hash:
                errors.append(f"SHA-256 mismatch for {rel}")

        if errors:
            for msg in errors:
                print(f"ERROR: {msg}")
            return 1

        print(
            f"Release manifest verification passed for {len(rows)} tracked files "
            f"(excluding {MANIFEST_REL})."
        )
        return 0
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
