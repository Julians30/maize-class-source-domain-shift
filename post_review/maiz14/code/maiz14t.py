"""MAIZ_14T: compare the public Tanzania maize dataset (Mduma & Mayo 2023, Mendeley 10.17632/fkw49mz3xs.1)
with the internal healthy / lethal_necrosis / streak_virus images (exact SHA-256 and 64-bit pHash <= 5).

Source order: (1) Mendeley public API file links; (2) manual links given by the user;
(3) the Hugging Face mirror Project-AgML/maize_disease_classification, which cites the same DOI.
CPU only. Results go to MAIZ14_cierre_parciales/tanzania_* and MAIZ_14T_Tanzania.zip.
"""
from pathlib import Path
import io, json, os, time, zipfile, hashlib
import numpy as np
import pandas as pd
from PIL import Image

DATASET = 'fkw49mz3xs'
WANT = ['MLN', 'HEALTHY', 'MSV']
IMG = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')
HF_REPO = 'Project-AgML/maize_disease_classification'
WORK = Path('/content/maiz14t_work')


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def phash_hex(b):
    import imagehash
    try:
        with Image.open(io.BytesIO(b)) as im:
            return str(imagehash.phash(im.convert('RGB')))
    except Exception:
        return ''


def _walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values():
            yield from _walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk(v)


def mendeley_links():
    """Best-effort discovery of the three ZIP links through the public API."""
    import requests
    urls = [f'https://data.mendeley.com/public-api/datasets/{DATASET}/files?folder_id=root&version=1',
            f'https://data.mendeley.com/public-api/datasets/{DATASET}?version=1',
            f'https://data.mendeley.com/public-api/datasets/{DATASET}/files?version=1']
    found = {}
    for u in urls:
        try:
            r = requests.get(u, timeout=60, headers={'Accept': 'application/json'})
            if r.status_code != 200:
                log('  API', r.status_code, u); continue
            for d in _walk(r.json()):
                name = d.get('filename') or d.get('name')
                if not name or not str(name).upper().endswith('.ZIP'):
                    continue
                key = str(name).upper().replace('.ZIP', '')
                link = next((v.get('download_url') for v in _walk(d) if isinstance(v, dict) and v.get('download_url')), None)
                sha = next((v.get('sha256_hash') for v in _walk(d) if isinstance(v, dict) and v.get('sha256_hash')), None)
                if key in WANT and link:
                    found[key] = {'url': link, 'sha256': sha}
            if found:
                break
        except Exception as e:
            log('  API no disponible:', u, repr(e)[:150])
    return found


def download(url, dest):
    import requests
    h = hashlib.sha256()
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for b in r.iter_content(16 * 1024 ** 2):
                f.write(b); h.update(b)
    return h.hexdigest()


def rows_from_zip(zp, cls):
    rows = []
    with zipfile.ZipFile(zp) as z:
        names = [n for n in z.namelist() if n.lower().endswith(IMG)]
        log(f'  {cls}: {len(names)} imágenes en el ZIP')
        for i, n in enumerate(names, 1):
            b = z.read(n)
            rows.append({'source': 'mendeley', 'tz_class': cls, 'member': n, 'file': Path(n).name,
                         'sha256': hashlib.sha256(b).hexdigest(), 'phash': phash_hex(b)})
            if i % 500 == 0:
                log(f'    {cls} {i}/{len(names)}')
    return rows


def rows_from_hf():
    from huggingface_hub import list_repo_files, hf_hub_download
    import pyarrow.parquet as pq
    files = [f for f in list_repo_files(HF_REPO, repo_type='dataset') if f.endswith('.parquet')]
    log('  Hugging Face parquet:', len(files))
    rows = []; names = None
    for f in sorted(files):
        p = hf_hub_download(HF_REPO, f, repo_type='dataset', local_dir=str(WORK / 'hf'))
        t = pq.ParquetFile(p)
        if names is None:
            meta = t.schema_arrow.metadata or {}
            try:
                feats = json.loads(meta[b'huggingface'])['info']['features']
                lab = next(v for k, v in feats.items() if isinstance(v, dict) and v.get('_type') == 'ClassLabel')
                names = lab['names']
            except Exception:
                names = None
        cols = t.schema_arrow.names
        img_col = next(c for c in cols if c in ('image', 'img'))
        lab_col = next((c for c in cols if c in ('label', 'labels', 'class')), None)
        for batch in t.iter_batches(batch_size=256):
            d = batch.to_pydict()
            for k, im in enumerate(d[img_col]):
                b = im['bytes'] if isinstance(im, dict) else im
                lab = d[lab_col][k] if lab_col else ''
                cls = names[lab] if (names and isinstance(lab, int)) else str(lab)
                path = im.get('path') if isinstance(im, dict) else ''
                rows.append({'source': 'huggingface', 'tz_class': str(cls).upper(), 'member': path or '',
                             'file': Path(path).name if path else '', 'sha256': hashlib.sha256(b).hexdigest(), 'phash': phash_hex(b)})
            log(f'    HF {len(rows)} imágenes')
        os.remove(p)
    return rows


def hamming_min(a_hex, b_hex):
    A = np.array([[int(c) for c in bin(int(h, 16))[2:].zfill(64)] for h in a_hex], dtype=np.uint8)
    B = np.array([[int(c) for c in bin(int(h, 16))[2:].zfill(64)] for h in b_hex], dtype=np.uint8)
    dmin = np.zeros(len(A), np.uint8); arg = np.zeros(len(A), int)
    for i in range(0, len(A), 256):
        d = (A[i:i + 256, None, :] != B[None]).sum(2)
        dmin[i:i + 256] = d.min(1); arg[i:i + 256] = d.argmin(1)
    return dmin, arg


def run(root, out_rel, manual_urls=None, classes=('MLN', 'HEALTHY')):
    root = Path(root); out = root / out_rel; WORK.mkdir(parents=True, exist_ok=True)
    internal = pd.read_csv(out / 'internal_index_healthy_mln_msv.csv', dtype=str)
    log('Índice interno:', internal.groupby(['partition', 'class']).size().to_dict())
    cache = out / 'tanzania_image_index.csv'
    if cache.is_file():
        tz = pd.read_csv(cache, dtype=str); log('Índice Tanzania ya calculado:', len(tz))
        how = 'cached'
    else:
        links = {k: {'url': v, 'sha256': None} for k, v in (manual_urls or {}).items() if v and 'PEGUE' not in v}
        if not links:
            log('Buscando enlaces en la API pública de Mendeley...'); links = mendeley_links()
        rows = []; how = None
        if all(c in links for c in classes):
            how = 'mendeley'
            for c in classes:
                zp = WORK / f'{c}.zip'
                log('Descargando', c); sha = download(links[c]['url'], zp)
                if links[c].get('sha256') and links[c]['sha256'] != sha:
                    raise ValueError(f'SHA-256 de {c}.zip no coincide con el publicado')
                rows += rows_from_zip(zp, c); zp.unlink()
        else:
            log('Mendeley no dio enlaces directos; se usa el espejo de Hugging Face (misma cita DOI).')
            how = 'huggingface'; rows = [r for r in rows_from_hf() if r['tz_class'] in classes or not classes]
        tz = pd.DataFrame(rows); tz.to_csv(cache, index=False)
    ok = tz.phash.fillna('').str.len() == 16; ii = internal[internal.phash.str.len() == 16].reset_index(drop=True)
    tz['exact_internal'] = tz.sha256.isin(set(internal.sha256))
    tz['hamming_min'] = 99; tz['nearest_internal_class'] = ''; tz['nearest_internal_partition'] = ''; tz['nearest_internal_file'] = ''
    if ok.any():
        dmin, arg = hamming_min(tz.loc[ok, 'phash'], ii.phash)
        tz.loc[ok, 'hamming_min'] = dmin
        tz.loc[ok, 'nearest_internal_class'] = ii['class'].values[arg]
        tz.loc[ok, 'nearest_internal_partition'] = ii.partition.values[arg]
        tz.loc[ok, 'nearest_internal_file'] = ii.file.values[arg]
    tz['phash_le5_internal'] = tz.hamming_min.astype(int) <= 5
    tz['same_filename_internal'] = tz.file.isin(set(internal.file))
    tz.to_csv(out / 'tanzania_vs_internal.csv', index=False)
    hit = internal.sha256.isin(set(tz.sha256))
    m = tz[tz.exact_internal | tz.phash_le5_internal]
    summ = {'status': 'done', 'source_used': how, 'dataset_doi': '10.17632/fkw49mz3xs.1', 'classes_compared': list(classes),
            'tanzania_images_by_class': tz.tz_class.value_counts().astype(int).to_dict(),
            'exact_sha256_in_internal_by_class': tz[tz.exact_internal].tz_class.value_counts().astype(int).to_dict(),
            'phash_le5_in_internal_by_class': tz[tz.phash_le5_internal].tz_class.value_counts().astype(int).to_dict(),
            'same_filename_in_internal_by_class': tz[tz.same_filename_internal].tz_class.value_counts().astype(int).to_dict(),
            'matches_by_tz_class_and_internal_class': {f'{a}->{b}': int(v) for (a, b), v in m.groupby(['tz_class', 'nearest_internal_class']).size().items()},
            'internal_indexed_by_class': internal['class'].value_counts().astype(int).to_dict(),
            'internal_with_exact_tanzania_copy_by_class': internal[hit]['class'].value_counts().astype(int).to_dict(),
            'internal_with_exact_tanzania_copy_by_partition_class': {f'{a}|{b}': int(v) for (a, b), v in internal[hit].groupby(['partition', 'class']).size().items()}}
    (out / 'tanzania_check.json').write_text(json.dumps(summ, indent=2, ensure_ascii=False))
    log('RESULTADO Tanzania:', json.dumps(summ, ensure_ascii=False))
    z = out.parent / 'MAIZ_14T_Tanzania.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for p in ['tanzania_check.json', 'tanzania_vs_internal.csv']:
            f.write(out / p, p)
    import shutil; shutil.copy(z, '/content/MAIZ_14T_Tanzania.zip') if Path('/content').is_dir() else None
    log('ZIP:', z)
    return summ
