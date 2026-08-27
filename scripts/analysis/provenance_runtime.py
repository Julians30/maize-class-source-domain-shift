#!/usr/bin/env python3
"""Runtime helper for losslessly archived maize provenance-analysis modules."""
from __future__ import annotations
import argparse, base64, csv, hashlib, importlib.util, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'manifests/provenance_payload_manifest.csv'
PAYLOAD_DIR = Path(__file__).resolve().parent / 'provenance_payloads'

def _rows():
    with MANIFEST.open(newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))

def _load_payload(name: str) -> str:
    path = PAYLOAD_DIR / name
    spec = importlib.util.spec_from_file_location('_maize_payload_' + path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Could not load payload: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = getattr(module, 'PAYLOAD', None)
    if not isinstance(value, str):
        raise TypeError(f'Payload module does not expose string PAYLOAD: {path}')
    return value

def source_bytes(script_path: Path) -> bytes:
    rel = script_path.resolve().relative_to(ROOT).as_posix()
    row = next((r for r in _rows() if r['release_script'] == rel), None)
    if row is None:
        raise KeyError(f'No provenance manifest row for {rel}')
    names = [x for x in row['payload_modules'].split(';') if x]
    if len(names) != int(row['payload_chunks']):
        raise RuntimeError(f'Payload chunk-count mismatch for {rel}')
    encoded = ''.join(_load_payload(name) for name in names)
    raw = zlib.decompress(base64.b85decode(encoded.encode('ascii')))
    observed = hashlib.sha256(raw).hexdigest()
    if observed != row['decoded_release_sha256']:
        raise RuntimeError(f'Provenance source SHA-256 mismatch for {rel}: {observed}')
    if len(raw) != int(row['decoded_release_bytes']):
        raise RuntimeError(f'Provenance source byte-size mismatch for {rel}')
    compile(raw.decode('utf-8'), rel, 'exec')
    return raw

def run_provenance(script_file: str) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--materialize', type=Path, help='Write reconstructed readable Python source without executing it.')
    args = parser.parse_args()
    script = Path(script_file)
    raw = source_bytes(script)
    if args.materialize:
        args.materialize.parent.mkdir(parents=True, exist_ok=True)
        args.materialize.write_bytes(raw)
        print(args.materialize)
        return
    rel = script.resolve().relative_to(ROOT).as_posix()
    exec(compile(raw.decode('utf-8'), rel, 'exec'), globals(), globals())
