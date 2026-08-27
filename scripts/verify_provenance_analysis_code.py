#!/usr/bin/env python3
"""Verify all provenance-analysis modules supporting the maize manuscript."""
from __future__ import annotations
import ast, base64, csv, hashlib, importlib.util, pathlib, re, sys, zlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/provenance_payload_manifest.csv'
PAYLOADS = ROOT / 'scripts/analysis/provenance_payloads'
FORBIDDEN = [re.compile(x,re.I) for x in [r'/content/drive/', r'\bMyDrive\b', r'TesisQ1_Maiz', r'ARTICLE2', r'juliancoronel', r'10208604942001452546']]

def load_payload(path):
    spec=importlib.util.spec_from_file_location('_maize_'+path.stem,path)
    if spec is None or spec.loader is None: raise RuntimeError(f'Could not load {path}')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    value=getattr(module,'PAYLOAD',None)
    if not isinstance(value,str): raise TypeError(f'PAYLOAD missing in {path}')
    return value

def main():
    errors=[]
    if not MANIFEST.is_file():
        print('ERROR: missing provenance payload manifest'); return 1
    with MANIFEST.open(newline='',encoding='utf-8-sig') as fh:
        rows=list(csv.DictReader(fh))
    if len(rows)!=10: errors.append(f'expected 10 provenance modules, found {len(rows)}')
    for row in rows:
        rel=row['release_script']; launcher=ROOT/rel
        if not launcher.is_file(): errors.append(f'missing launcher: {rel}')
        else:
            try: compile(launcher.read_text(encoding='utf-8'),rel,'exec')
            except Exception as exc: errors.append(f'launcher compile failure {rel}: {exc}')
        names=[x for x in row['payload_modules'].split(';') if x]
        if len(names)!=int(row['payload_chunks']): errors.append(f'payload count mismatch: {rel}'); continue
        chunks=[]
        for name in names:
            path=PAYLOADS/name
            if not path.is_file(): errors.append(f'missing payload: {path.relative_to(ROOT)}'); continue
            try: chunks.append(load_payload(path))
            except Exception as exc: errors.append(f'payload load failure {path.relative_to(ROOT)}: {exc}')
        if len(chunks)!=len(names): continue
        try: raw=zlib.decompress(base64.b85decode(''.join(chunks).encode('ascii')))
        except Exception as exc: errors.append(f'decode failure {rel}: {exc}'); continue
        if len(raw)!=int(row['decoded_release_bytes']): errors.append(f'decoded byte-size mismatch: {rel}')
        if hashlib.sha256(raw).hexdigest()!=row['decoded_release_sha256']: errors.append(f'decoded SHA-256 mismatch: {rel}')
        if not re.fullmatch(r'[0-9a-f]{64}',row['source_sha256']): errors.append(f'invalid source SHA-256: {rel}')
        try:
            text=raw.decode('utf-8'); compile(text,rel,'exec'); ast.parse(text)
        except Exception as exc:
            errors.append(f'decoded source compile/parse failure {rel}: {exc}'); continue
        for pat in FORBIDDEN:
            if pat.search(text): errors.append(f'forbidden private/historical token in {rel}: {pat.pattern}')
        if 'MAIZE_PROJECT_ROOT' not in text: errors.append(f'MAIZE_PROJECT_ROOT parameterization missing from {rel}')
    if errors:
        for err in errors: print('ERROR:',err)
        return 1
    print('Verified 10 lossless payload-backed provenance-analysis modules with SHA-256, syntax, and release-hygiene checks.')
    return 0
if __name__=='__main__': sys.exit(main())
