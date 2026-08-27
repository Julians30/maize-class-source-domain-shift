#!/usr/bin/env python3
"""Verify historical/provenance analysis code supporting the maize manuscript."""
from __future__ import annotations
import ast, base64, csv, hashlib, importlib.util, pathlib, re, sys, zlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/provenance_payload_manifest.csv'
ANALYSIS = ROOT / 'scripts/analysis'
FRAGMENTS = ANALYSIS / 'provenance_fragments'
PAYLOADS = ANALYSIS / 'provenance_payloads'
DATALOADER_ENTRY = ANALYSIS / '03_dataloader_validation_provenance.py'
DATALOADER_FRAGMENTS = [FRAGMENTS / f'03_dataloader_validation_provenance__part0{i}.py' for i in (1,2,3)]
FORBIDDEN = [re.compile(x,re.I) for x in [r'/content/drive/', r'\bMyDrive\b', r'TesisQ1_Maiz', r'ARTICLE2', r'juliancoronel', r'10208604942001452546']]

def load_payload(path):
    spec=importlib.util.spec_from_file_location('_maize_'+path.stem,path)
    if spec is None or spec.loader is None: raise RuntimeError(f'Could not load {path}')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    value=getattr(m,'PAYLOAD',None)
    if not isinstance(value,str): raise TypeError(f'PAYLOAD missing in {path}')
    return value

def hygiene(text,rel,errors):
    for pat in FORBIDDEN:
        if pat.search(text): errors.append(f'forbidden private/historical token in {rel}: {pat.pattern}')
    if 'MAIZE_PROJECT_ROOT' not in text: errors.append(f'MAIZE_PROJECT_ROOT parameterization missing from {rel}')

def main():
    errors=[]
    if not DATALOADER_ENTRY.is_file(): errors.append('missing dataloader provenance launcher')
    else:
        try: compile(DATALOADER_ENTRY.read_text(encoding='utf-8'),str(DATALOADER_ENTRY),'exec')
        except Exception as exc: errors.append(f'dataloader launcher compile failure: {exc}')
    if any(not p.is_file() for p in DATALOADER_FRAGMENTS): errors.append('one or more dataloader provenance fragments are missing')
    else:
        text='\n\n'.join(p.read_text(encoding='utf-8') for p in DATALOADER_FRAGMENTS)
        try: compile(text,'dataloader_provenance.py','exec'); ast.parse(text)
        except Exception as exc: errors.append(f'dataloader reconstruction failure: {exc}')
        hygiene(text,'dataloader provenance',errors)
    if not MANIFEST.is_file(): errors.append('missing provenance payload manifest'); rows=[]
    else:
        with MANIFEST.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    if len(rows)!=9: errors.append(f'expected 9 payload-backed provenance modules, found {len(rows)}')
    for row in rows:
        rel=row['release_script']; launcher=ROOT/rel
        if not launcher.is_file(): errors.append(f'missing launcher: {rel}')
        else:
            try: compile(launcher.read_text(encoding='utf-8'),rel,'exec')
            except Exception as exc: errors.append(f'launcher compile failure {rel}: {exc}')
        names=[x for x in row['payload_modules'].split(';') if x]
        if len(names)!=int(row['payload_chunks']): errors.append(f'payload count mismatch: {rel}'); continue
        parts=[]
        for name in names:
            p=PAYLOADS/name
            if not p.is_file(): errors.append(f'missing payload: {p.relative_to(ROOT)}'); continue
            try: parts.append(load_payload(p))
            except Exception as exc: errors.append(f'payload load failure {p.relative_to(ROOT)}: {exc}')
        if len(parts)!=len(names): continue
        try: raw=zlib.decompress(base64.b85decode(''.join(parts).encode('ascii')))
        except Exception as exc: errors.append(f'decode failure {rel}: {exc}'); continue
        if len(raw)!=int(row['decoded_release_bytes']): errors.append(f'decoded byte-size mismatch: {rel}')
        if hashlib.sha256(raw).hexdigest()!=row['decoded_release_sha256']: errors.append(f'decoded SHA-256 mismatch: {rel}')
        if not re.fullmatch(r'[0-9a-f]{64}',row['source_sha256']): errors.append(f'invalid source SHA-256: {rel}')
        try: text=raw.decode('utf-8'); compile(text,rel,'exec'); ast.parse(text)
        except Exception as exc: errors.append(f'decoded source compile/parse failure {rel}: {exc}'); continue
        hygiene(text,rel,errors)
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print('Verified 10 provenance-analysis modules: dataloader + nine lossless payload-backed modules with SHA-256 and hygiene checks.')
    return 0
if __name__=='__main__': sys.exit(main())
