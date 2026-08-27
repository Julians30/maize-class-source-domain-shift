#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, pathlib, py_compile, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
M=ROOT/'manifests/canonical_code_provenance.csv'; F=ROOT/'manifests/canonical_fragment_sha256.csv'
FORBIDDEN=('/content/drive','mydrive','tesisq1_maiz','kaggle.json','article2','articulo2')
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def main():
 errors=[]; rows=list(csv.DictReader(M.open(encoding='utf-8-sig')))
 if len(rows)!=2:errors.append('canonical provenance manifest must contain exactly two analyses')
 for r in rows:
  for key,hkey in [('release_notebook','release_notebook_sha256'),('release_script','release_script_sha256')]:
   p=ROOT/r[key]
   if not p.is_file():errors.append(f'missing {r[key]}');continue
   if sha(p)!=r[hkey]:errors.append(f'hash mismatch {r[key]}')
  p=ROOT/r['release_script']
  if p.is_file():
   try:py_compile.compile(str(p),doraise=True)
   except Exception as e:errors.append(f'syntax error {p}: {e}')
 fr=list(csv.DictReader(F.open(encoding='utf-8-sig')))
 for r in fr:
  p=ROOT/r['fragment']
  if not p.is_file():errors.append(f'missing {r["fragment"]}');continue
  if sha(p)!=r['sha256']:errors.append(f'hash mismatch {r["fragment"]}')
  try:py_compile.compile(str(p),doraise=True)
  except Exception as e:errors.append(f'syntax error {p}: {e}')
  low=p.read_text(encoding='utf-8',errors='replace').lower()
  for tok in FORBIDDEN[:4]:
   if tok in low:errors.append(f'private path token {tok} in {r["fragment"]}')
 for nbname in ['02_internal_comparison_E2A_release.ipynb','03_final_paired_inference_release.ipynb']:
  p=ROOT/'notebooks'/nbname; nb=json.loads(p.read_text(encoding='utf-8')); text=[]
  for c in nb.get('cells',[]):
   if c.get('cell_type')=='code' and (c.get('outputs') or c.get('execution_count') is not None):errors.append(f'uncleared outputs/count in {nbname}')
   s=c.get('source',[]);text.append(''.join(s) if isinstance(s,list) else str(s))
  low='\n'.join(text).lower()
  for tok in FORBIDDEN:
   if tok in low:errors.append(f'forbidden token {tok} in {nbname}')
 if errors:
  print('\n'.join('ERROR: '+e for e in sorted(set(errors))));return 1
 print(f'Canonical analysis code audit passed: 2 notebooks, 2 entry scripts, {len(fr)} source fragments.')
 return 0
if __name__=='__main__':sys.exit(main())
