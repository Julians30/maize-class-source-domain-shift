"""MAIZ_14A driver: stages are resumable; every stage writes a DONE receipt in OUT."""
from pathlib import Path
import gc, glob, io, json, os, re, shutil, sys, tarfile, time, traceback, zipfile
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from maiz14 import *

CODE = Path(__file__).resolve().parent
OUT_REL = 'REVISION_POST_REVIEW_20261029/MAIZ14_cierre_parciales'
PREP_REL = 'REVISION_POST_REVIEW_20261029/evaluation_5seeds/prepared'
TOM_REL = '01_datasets/TOM2024/CategoryA_English/CATA-English'
SPLIT_REL = '01_datasets/split_v3'
WORK = Path('/content/maiz14_work')
IMG_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff'}
DINO = 'vit_base_patch14_dinov2.lvd142m'
THRESHOLDS = [0.90, 0.95, 0.97]
MAIN_THR = 0.95


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def done(out, stage):
    return (Path(out) / 'receipts' / f'{stage}.json').is_file()


def mark(out, stage, info):
    atomic_json({'stage': stage, 'completed_utc': utc(), 'version': VERSION, **info}, Path(out) / 'receipts' / f'{stage}.json')


def phash_hex(im):
    import imagehash
    return str(imagehash.phash(im.convert('RGB')))


def hamming_matrix(a_hex, b_hex):
    A = np.array([[int(c) for c in bin(int(h, 16))[2:].zfill(64)] for h in a_hex], dtype=np.uint8)
    B = np.array([[int(c) for c in bin(int(h, 16))[2:].zfill(64)] for h in b_hex], dtype=np.uint8)
    out = np.zeros((len(A), len(B)), dtype=np.uint8)
    for i in range(0, len(A), 512):
        out[i:i + 512] = (A[i:i + 512, None, :] != B[None]).sum(2)
    return out


# ============================================================================ 1. environment
def stage_env(out):
    import torch, torchvision, timm
    if not torch.cuda.is_available():
        raise RuntimeError('Active GPU: Entorno de ejecución > Cambiar tipo > GPU L4')
    info = {'torch': torch.__version__, 'torchvision': torchvision.__version__, 'timm': timm.__version__,
            'gpu': torch.cuda.get_device_name(0), 'python': sys.version.split()[0],
            'training_versions': {'torch': '2.11.0+cu128', 'torchvision': '0.26.0+cu128', 'timm': '1.0.15'}}
    info['same_as_training'] = (info['torch'], info['torchvision'], info['timm']) == ('2.11.0+cu128', '0.26.0+cu128', '1.0.15')
    if 'L4' not in info['gpu']:
        log('AVISO: GPU distinta de L4:', info['gpu'], '(se permite; la compuerta de concordancia decide)')
    if not info['same_as_training']:
        log('AVISO: versiones distintas a las de entrenamiento; la compuerta de concordancia lo documentará', info)
    torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    atomic_json(info, Path(out) / 'environment.json'); log('Entorno:', info)
    return info


# ============================================================================ 2. internal index (Drive)
def stage_internal_index(root, out):
    """SHA-256 and pHash of internal healthy / lethal_necrosis / streak_virus images.

    Train and validation come from the verified E2-A training cache (training_data_preflight.json and its
    TAR); test comes from the frozen internal-test manifest. Falls back to 01_datasets/split_v3 only if the
    training cache record is missing.
    """
    f = Path(out) / 'internal_index_healthy_mln_msv.csv'
    if done(out, 'internal_index'):
        return pd.read_csv(f, dtype=str)
    target = {'healthy', 'lethal_necrosis', 'streak_virus'}
    rep = Path(root) / 'REVISION_POST_REVIEW_20261029' / 'training_data_preflight.json'
    rows = []
    if rep.is_file():
        r = json.loads(rep.read_text())
        val = set(pd.read_csv(CODE / 'validation.csv', dtype=str).sha256.str.lower())
        need = {}
        for raw, name in r['path_to_cache_name'].items():
            cls = next((p for p in reversed(Path(raw).parts) if p in C2I), None)
            if cls in target:
                need[name] = (cls, raw)
        local = WORK / r['archive_name']
        if not (local.is_file() and local.stat().st_size == r['archive_bytes']):
            log('Copiando caché de entrenamiento verificada (', round(r['archive_bytes'] / 1e9, 2), 'GB )')
            shutil.copyfile(Path(root) / 'REVISION_POST_REVIEW_20261029' / 'training_data_cache' / r['archive_name'], local)
        if sha_file(local) != r['archive_sha256']:
            raise ValueError('La caché de entrenamiento cambió de huella')
        with tarfile.open(local, 'r:') as t:
            for m in t:
                if m.name in need:
                    b = t.extractfile(m).read(); sha = sha_bytes(b)
                    if sha + '.img' != m.name:
                        raise ValueError('SHA de caché incorrecto: ' + m.name)
                    with Image.open(io.BytesIO(b)) as im:
                        ph = phash_hex(im)
                    cls, raw = need[m.name]
                    rows.append({'partition': 'validation' if sha in val else 'train', 'class': cls, 'file': Path(raw).name,
                                 'sha256': sha, 'phash': ph, 'source_record': 'E2-A training cache'})
        local.unlink(missing_ok=True)
        if len(rows) != len(need):
            raise ValueError(f'Faltan imágenes en la caché: {len(rows)} de {len(need)}')
        te = pd.read_csv(CODE / 'internal_test.csv', dtype=str, keep_default_na=False)
        te = te[te['class'].isin(target)]
        rows += [{'partition': 'test', 'class': x['class'], 'file': Path(x.original_path).name, 'sha256': x.sha256.lower(),
                  'phash': x.phash.lower(), 'source_record': 'frozen internal-test manifest'} for _, x in te.iterrows()]
    else:
        base = Path(root) / SPLIT_REL
        files = [p for c in sorted(target) for p in sorted(base.glob(f'*/{c}/*')) if p.suffix.lower() in IMG_EXT]
        log('AVISO: sin registro de caché; se indexa split_v3:', len(files))
        for p in files:
            b = p.read_bytes()
            with Image.open(io.BytesIO(b)) as im:
                ph = phash_hex(im)
            rows.append({'partition': p.parent.parent.name, 'class': p.parent.name, 'file': p.name, 'sha256': sha_bytes(b),
                         'phash': ph, 'source_record': 'split_v3 folder'})
    df = pd.DataFrame(rows); atomic_csv(df, f)
    counts = df.groupby(['partition', 'class']).size()
    mark(out, 'internal_index', {'files': len(df), 'by_partition_class': {f'{a}|{b}': int(v) for (a, b), v in counts.items()}})
    log('Índice interno:', counts.to_dict())
    return df


# ============================================================================ 3. cohorts
def to_array(im):
    return np.asarray(im.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR), dtype=np.uint8)


def stage_cohorts(root, out):
    """Builds every cohort as a frame plus a uint8 224x224 array with the historical squash recipe."""
    arrdir = WORK / 'arrays'; arrdir.mkdir(parents=True, exist_ok=True)
    meta_f = Path(out) / 'cohorts.csv'
    if done(out, 'cohorts') and all((arrdir / f'{c}.npy').is_file() for c in pd.read_csv(meta_f).cohort.unique()):
        return pd.read_csv(meta_f, dtype={'sample_id': str})
    root = Path(root); frames = []; report = {}
    # --- PlantVillage public source at the verified commit
    pv = fetch_pv_public(WORK / 'PlantVillage-Dataset')
    report['pv_public_folder_counts'] = {k: len(v) for k, v in pv.items()}
    pub = pd.read_csv(CODE / 'plantvillage_public_source_1498.csv', dtype=str)
    hist = pd.read_csv(CODE / 'plantvillage.csv', dtype=str, keep_default_na=False)
    if pub.sample_id.tolist() != hist.sample_id.tolist():
        raise ValueError('Orden PlantVillage distinto del archivo')
    prep = root / PREP_REL / 'plantvillage'
    prepared = None
    if (prep / 'manifest.csv').is_file() and (prep / 'images.tar').is_file():
        prepared = extract_prepared(root / PREP_REL.rsplit('/', 1)[0], 'plantvillage', WORK / 'prepared')
        prepared = prepared.set_index('sample_id').loc[hist.sample_id]
    pv_root = WORK / 'PlantVillage-Dataset'
    arr = np.zeros((len(pub), 224, 224, 3), np.uint8); same_cache = 0
    for i, r in enumerate(pub.itertuples()):
        raw = (pv_root / r.public_relative_path).read_bytes()
        if sha_bytes(raw) != r.sha256:
            raise ValueError('SHA público distinto: ' + r.sample_id)
        im = pv_style_cache(Image.open(io.BytesIO(raw)), exif=False)
        if prepared is not None:
            cached = Image.open(prepared.iloc[i].local_path); cached.load()
            same_cache += int(np.array_equal(np.asarray(cached.convert('RGB')), np.asarray(im)))
            im = cached
        arr[i] = to_array(im)
    np.save(arrdir / 'pv_bs.npy', arr)
    report['pv_bs_input'] = 'prepared historical cache' if prepared is not None else 'public commit + historical cache recipe'
    report['pv_bs_public_recipe_pixel_identical_to_prepared_cache'] = int(same_cache) if prepared is not None else None
    frames.append(pd.DataFrame({'cohort': 'pv_bs', 'sample_id': hist.sample_id, 'class': hist['class'],
                                'group': hist.global_group_id, 'sha256': pub.sha256}))
    for folder, cls, name in [('Corn_(maize)___Common_rust_', 'rust', 'pv_rust'), ('Corn_(maize)___healthy', 'healthy', 'pv_healthy')]:
        files = pv[folder]; arr = np.zeros((len(files), 224, 224, 3), np.uint8); sh = []; ph = []
        for i, p in enumerate(files):
            raw = p.read_bytes(); sh.append(sha_bytes(raw))
            im0 = Image.open(io.BytesIO(raw)); ph.append(phash_hex(im0))
            arr[i] = to_array(pv_style_cache(im0, exif=False))
        np.save(arrdir / f'{name}.npy', arr)
        frames.append(pd.DataFrame({'cohort': name, 'sample_id': ['PV::' + folder + '/' + p.name for p in files],
                                    'class': cls, 'group': ['pvsha_' + s[:16] for s in sh], 'sha256': sh, 'phash': ph}))
    # --- TOM2024 primary (prepared historical cache)
    tom_hist = pd.read_csv(CODE / 'tom2024_primary.csv', dtype=str, keep_default_na=False)
    tp = extract_prepared(root / PREP_REL.rsplit('/', 1)[0], 'tom2024_primary', WORK / 'prepared')
    tp = tp.set_index('sample_id').loc[tom_hist.sample_id]
    arr = np.zeros((len(tp), 224, 224, 3), np.uint8)
    for i, p in enumerate(tp.local_path):
        with Image.open(p) as im:
            arr[i] = to_array(im)
    np.save(arrdir / 'tom_p.npy', arr)
    frames.append(pd.DataFrame({'cohort': 'tom_p', 'sample_id': tom_hist.sample_id, 'class': tom_hist['class'],
                                'group': tom_hist.global_group_id, 'sha256': tom_hist.sha256}))
    # --- TOM2024 Helminthosporiosis-D / Curvularia-D with the documented exclusion rules
    tom_idx = tom_index(root, out)
    report['tom_index_files'] = int(len(tom_idx))
    for pattern, cls, name in [('helminth', 'leaf_blight', 'tom_helm'), ('curvularia', 'leaf_spot', 'tom_curv')]:
        sel = tom_idx[tom_idx.folder.str.lower().str.contains(pattern)]
        if sel.empty:
            log('AVISO: no se encontró carpeta TOM2024 para', pattern); report[name] = 'folder not found'; continue
        folder = sel.folder.iloc[0]
        n0 = len(sel)
        sha_folders = tom_idx.groupby('sha256').folder.nunique()
        conflict = sel.sha256.map(sha_folders) > 1
        sel = sel[~conflict]; n1 = len(sel)
        sel = sel.sort_values('relpath').drop_duplicates('sha256'); n2 = len(sel)
        in_primary = sel.sha256.isin(set(tom_hist.sha256)); sel = sel[~in_primary]
        unreadable = []; arr = np.zeros((len(sel), 224, 224, 3), np.uint8); keep = []
        for r in sel.itertuples():
            try:
                with Image.open(Path(root) / TOM_REL / r.relpath) as im:
                    arr[len(keep)] = to_array(pv_style_cache(im, exif=True)); keep.append(r.Index)
            except Exception:
                unreadable.append(r.relpath)
        sel = sel.loc[keep]; arr = arr[:len(keep)]
        np.save(arrdir / f'{name}.npy', arr)
        report[name] = {'folder': folder, 'files': int(n0), 'conflicting_label_files_removed': int(n0 - n1),
                        'exact_redundant_copies_removed': int(n1 - n2), 'already_in_primary': int(in_primary.sum()),
                        'unreadable': unreadable, 'retained': int(len(sel)),
                        'mapping': f'{folder} -> {cls} (taxonomic sensitivity mapping; no image-level label review)'}
        frames.append(pd.DataFrame({'cohort': name, 'sample_id': ['TOM2024::' + p for p in sel.relpath], 'class': cls,
                                    'group': ['tomsha_' + s[:16] for s in sel.sha256], 'sha256': sel.sha256.values}))
    meta = pd.concat(frames, ignore_index=True)
    atomic_csv(meta, meta_f); atomic_json(report, Path(out) / 'cohort_report.json')
    mark(out, 'cohorts', {'counts': meta.groupby('cohort').size().astype(int).to_dict()})
    log('Cohortes:', meta.groupby(['cohort', 'class']).size().to_dict())
    return meta


def tom_index(root, out):
    """SHA-256 of the maize Category A files only (maize_* folders), read in parallel from Drive."""
    import concurrent.futures as cf
    f = Path(out) / 'tom2024_categoryA_index.csv'
    if f.is_file():
        return pd.read_csv(f, dtype=str)
    base = Path(root) / TOM_REL
    tops = [d for d in base.iterdir() if d.is_dir() and d.name.lower().startswith('maize')] or [base]
    files = sorted(p for d in tops for p in d.rglob('*') if p.is_file() and p.suffix.lower() in IMG_EXT)
    log('Índice TOM2024 (carpetas de maíz):', [d.name for d in tops], '| archivos', len(files))

    def h(p):
        return {'relpath': str(p.relative_to(base)), 'folder': p.parent.name, 'sha256': sha_file(p)}
    rows = []
    with cf.ThreadPoolExecutor(16) as ex:
        for i, r in enumerate(ex.map(h, files), 1):
            rows.append(r)
            if i % 500 == 0:
                log('  TOM', i, '/', len(files))
    df = pd.DataFrame(rows); atomic_csv(df, f); return df


def pv_healthy_overlap(meta, internal, out):
    """PlantVillage healthy images whose standard pHash is within 5 bits of an internal healthy image."""
    h = meta[meta.cohort == 'pv_healthy'].reset_index(drop=True)
    ih = internal[(internal['class'] == 'healthy') & (internal.phash.str.len() == 16)].reset_index(drop=True)
    d = hamming_matrix(h.phash, ih.phash)
    best = d.argmin(1); dist = d.min(1)
    res = h[['sample_id', 'sha256', 'phash']].copy()
    res['nearest_internal_file'] = ih.file.values[best]; res['nearest_internal_partition'] = ih.partition.values[best]
    res['hamming'] = dist; res['exact_sha256'] = res.sha256.isin(set(internal.sha256)); res['matched_le5'] = dist <= 5
    atomic_csv(res, Path(out) / 'pv_healthy_internal_overlap.csv')
    summ = {'pv_healthy': int(len(res)), 'matched_hamming_le5': int(res.matched_le5.sum()), 'exact_sha256': int(res.exact_sha256.sum()),
            'matched_by_internal_partition': res[res.matched_le5].nearest_internal_partition.value_counts().astype(int).to_dict(),
            'distinct_internal_images_matched': int(res[res.matched_le5].nearest_internal_file.nunique())}
    atomic_json(summ, Path(out) / 'pv_healthy_internal_overlap_summary.json'); log('PV healthy ↔ interno:', summ)
    return res


# ============================================================================ 4. inference
def stage_inference(root, out, meta):
    import torch
    zen = pd.read_csv(CODE / 'zenodo_files.csv').set_index('filename')
    cohorts = list(meta.cohort.unique()); arrays = {c: np.load(WORK / 'arrays' / f'{c}.npy', mmap_mode='r') for c in cohorts}
    pdir = Path(out) / 'probabilities'; pdir.mkdir(parents=True, exist_ok=True)
    ck = WORK / 'checkpoints'; ck.mkdir(parents=True, exist_ok=True)
    mean = torch.tensor([.485, .456, .406], device='cuda').view(1, 3, 1, 1); std = torch.tensor([.229, .224, .225], device='cuda').view(1, 3, 1, 1)
    for n, (key, seed) in enumerate(RUNS, 1):
        f = pdir / f'{key}_seed{seed}.npz'
        if f.is_file() and set(np.load(f).files) >= set(cohorts):
            log(f'[{n}/30] ya existe:', f.name)
        else:
            name = f'{key}_seed{seed}.pt'
            log(f'[{n}/30] descarga verificada:', name)
            path = download_checkpoint(name, zen.loc[name, 'sha256'], ck / name)
            model = load_checkpoint(build_model(key), path).to('cuda').eval()
            res = {}
            for c in cohorts:
                a = arrays[c]; o = np.zeros((len(a), 9), np.float32)
                with torch.inference_mode():
                    for i in range(0, len(a), 64):
                        x = torch.from_numpy(np.ascontiguousarray(a[i:i + 64])).to('cuda').permute(0, 3, 1, 2).float().div_(255)
                        x = (x - mean) / std
                        with torch.autocast('cuda', dtype=torch.float16):
                            lg = model(x)
                        o[i:i + 64] = torch.softmax(lg.float(), 1).cpu().numpy()
                res[c] = o
            np.savez_compressed(f, **res)
            del model; gc.collect(); torch.cuda.empty_cache()
            if seed != 17:
                path.unlink(missing_ok=True)   # seed-17 checkpoints are reused by Grad-CAM
        q = gate_check(out, meta, runs=[(key, seed)], write=False)
        log('   concordancia con lo archivado:', dict(zip(q.dataset, q.argmax_disagreements)), '| Δ métrica', q.abs_difference.round(5).tolist())
        if (q.argmax_disagreements > 0.05 * q.n).any():
            raise RuntimeError(f'{key} semilla {seed}: más de 5% de predicciones distintas a las archivadas. '
                               'Se detiene para revisar preprocesamiento/versiones; no se usan estos resultados.')
    g = gate_check(out, meta)
    mark(out, 'inference', {'runs': 30, 'gate_pass': int((g.gate == 'PASS').sum()), 'gate_total': int(len(g)),
                            'max_disagreements': int(g.argmax_disagreements.max())})
    return g


def gate_check(out, meta, runs=None, write=True):
    """Recomputed argmax and primary metric against the archived predictions of every run."""
    exp = np.load(CODE / 'expected_argmax.npz', allow_pickle=False)
    exp_runs = [str(r) for r in exp['runs']]; expm = pd.read_csv(CODE / 'expected_metrics.csv'); gates = []
    for key, seed in (runs or RUNS):
        z = np.load(Path(out) / 'probabilities' / f'{key}_seed{seed}.npz'); j = exp_runs.index(f'{key}|{seed}')
        for cohort, ds in [('pv_bs', 'plantvillage'), ('tom_p', 'tom2024_primary')]:
            p = z[cohort]; y = meta[meta.cohort == cohort]['class'].map(C2I).to_numpy()
            dis = int((p.argmax(1) != exp[ds][j]).sum())
            labels = [C2I[c] for c in (TASKS['pv2'] if ds == 'plantvillage' else TASKS['tom3'])]
            val = macro_f1(y, p.argmax(1), labels)
            ref = expm[(expm.dataset == ds) & (expm.model_key == key) & (expm.seed == seed)].primary_value.iloc[0]
            gates.append({'model_key': key, 'seed': seed, 'dataset': ds, 'n': len(y), 'argmax_disagreements': dis,
                          'recomputed_primary': val, 'archived_primary': ref, 'abs_difference': abs(val - ref),
                          'gate': 'PASS' if dis <= 0.01 * len(y) and abs(val - ref) <= 0.01 else 'FLAG'})
    g = pd.DataFrame(gates)
    if not write:
        return g
    atomic_csv(g, Path(out) / 'agreement_gate.csv')
    log('Compuerta de concordancia: PASS', int((g.gate == 'PASS').sum()), 'de', len(g), '| máx. discrepancias', int(g.argmax_disagreements.max()))
    return g


def load_probs(out, cohort):
    return np.stack([np.load(Path(out) / 'probabilities' / f'{k}_seed{s}.npz')[cohort] for k, s in RUNS])  # (30,n,9)


# ============================================================================ 5. DINOv2 families
def stage_dino(out, meta):
    import torch, timm
    f = Path(out) / 'dinov2_embeddings.npz'
    if not f.is_file():
        m = timm.create_model(DINO, pretrained=True, num_classes=0, img_size=224).to('cuda').eval()
        mean = torch.tensor([.485, .456, .406], device='cuda').view(1, 3, 1, 1); std = torch.tensor([.229, .224, .225], device='cuda').view(1, 3, 1, 1)
        res = {}
        for c in meta.cohort.unique():
            a = np.load(WORK / 'arrays' / f'{c}.npy', mmap_mode='r'); e = []
            with torch.inference_mode():
                for i in range(0, len(a), 128):
                    x = torch.from_numpy(np.ascontiguousarray(a[i:i + 128])).to('cuda').permute(0, 3, 1, 2).float().div_(255)
                    v = m((x - mean) / std).float(); e.append(torch.nn.functional.normalize(v, dim=1).cpu().numpy())
            res[c] = np.concatenate(e).astype(np.float32)
        np.savez_compressed(f, **res); del m; torch.cuda.empty_cache()
    mark(out, 'dino', {'model': DINO, 'input': '224x224 historical squash recipe, ImageNet normalization', 'embedding': 'CLS token, L2-normalized'})


def families_for(out, meta, cohorts, thr):
    sub = meta[meta.cohort.isin(cohorts)].reset_index(drop=True)
    rec = sub.cohort + '::' + sub.group.astype(str)
    if thr is None:
        return union_groups(rec.to_numpy())
    z = np.load(Path(out) / 'dinov2_embeddings.npz'); emb = np.concatenate([z[c] for c in cohorts])
    return union_groups(rec.to_numpy(), components(emb, thr))


def near_pair_sheet(out, meta, cohort, path, k=24):
    """Contact sheet of the pairs closest to the main threshold for human checking."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    z = np.load(Path(out) / 'dinov2_embeddings.npz'); e = z[cohort]; s = e @ e.T; np.fill_diagonal(s, -1)
    iu = np.triu_indices(len(e), 1); v = s[iu]
    order = np.argsort(np.abs(v - MAIN_THR))[:k]
    a = np.load(WORK / 'arrays' / f'{cohort}.npy', mmap_mode='r'); sub = meta[meta.cohort == cohort].reset_index(drop=True)
    fig, ax = plt.subplots(k // 4, 8, figsize=(16, 2.2 * k // 4))
    rows = []
    for n, o in enumerate(sorted(order, key=lambda o: -v[o])):
        i, j = iu[0][o], iu[1][o]; r, c = divmod(n, 4)
        for t, idx in enumerate([i, j]):
            axx = ax[r, 2 * c + t]; axx.imshow(a[idx]); axx.set_xticks([]); axx.set_yticks([])
        ax[r, 2 * c].set_title(f'cos={v[o]:.3f}', fontsize=8, loc='left')
        rows.append({'cohort': cohort, 'cosine': float(v[o]), 'a': sub.sample_id[i], 'b': sub.sample_id[j],
                     'class_a': sub['class'][i], 'class_b': sub['class'][j], 'human_judgement': ''})
    plt.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return pd.DataFrame(rows)


# ============================================================================ 6. Grad-CAM
def target_layer(key, m):
    if key == 'mobilenetv3_large': return m.features[-1]
    if key == 'resnet50': return m.layer4[-1]
    if key == 'efficientnet_b0': return m.features[-1]
    if key == 'mobilevit_s': return m.final_conv
    if key == 'vit_base_patch16_224': return m.blocks[-1].norm1
    return m.layers[-1].blocks[-1].norm1


def reshape_for(key, m):
    import torch
    def rt(t):
        if t.ndim == 3:
            npt = getattr(m, 'num_prefix_tokens', 0) if key == 'vit_base_patch16_224' else 0
            t = t[:, npt:, :]; s = int(round(t.shape[1] ** 0.5)); t = t.reshape(t.shape[0], s, s, t.shape[2])
            return t.permute(0, 3, 1, 2)
        if t.ndim == 4 and t.shape[-1] > t.shape[1]:
            return t.permute(0, 3, 1, 2)
        return t
    return None if key in {'mobilenetv3_large', 'resnet50', 'efficientnet_b0', 'mobilevit_s'} else rt


def stage_gradcam(out, meta):
    import torch
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    gdir = Path(out) / 'gradcam'; gdir.mkdir(parents=True, exist_ok=True)
    tom = meta[meta.cohort == 'tom_p'].reset_index(drop=True)
    arch_cases = pd.read_csv(CODE / 'gradcam_archived_cases.csv').tom2024_external_id.tolist()
    rust_ids = tom[tom['class'] == 'rust'].sample_id.tolist()
    rest = sorted(set(rust_ids) - set(arch_cases))
    rnd = sorted(np.random.default_rng(20261109).choice(rest, 8, replace=False).tolist())
    cases = pd.DataFrame({'sample_id': arch_cases + rnd, 'selection': ['archived_ResNet50_confidence_panel'] * 8 + ['outcome_blind_random_rng20261109'] * 8})
    idx = [tom.index[tom.sample_id == s][0] for s in cases.sample_id]
    a = np.load(WORK / 'arrays' / 'tom_p.npy', mmap_mode='r'); imgs = np.stack([a[i] for i in idx])
    x = torch.from_numpy(imgs).permute(0, 3, 1, 2).float().div(255)
    x = (x - torch.tensor([.485, .456, .406]).view(1, 3, 1, 1)) / torch.tensor([.229, .224, .225]).view(1, 3, 1, 1)
    zen = pd.read_csv(CODE / 'zenodo_files.csv').set_index('filename')
    maps = {}; rows = []; status = {}
    for key in KEYS:
        name = f'{key}_seed17.pt'
        try:
            path = download_checkpoint(name, zen.loc[name, 'sha256'], WORK / 'checkpoints' / name)
            m = load_checkpoint(build_model(key), path).to(dev).eval()
            for p in m.parameters():
                p.requires_grad_(True)
            with torch.no_grad():
                prob = torch.softmax(m(x.to(dev)).float(), 1).cpu().numpy()
            cam = GradCAM(model=m, target_layers=[target_layer(key, m)], reshape_transform=reshape_for(key, m))
            g = cam(input_tensor=x.to(dev), targets=[ClassifierOutputTarget(C2I['rust'])] * len(x))
            maps[key] = g.astype(np.float32); status[key] = 'ok'
            band = np.ones((224, 224), bool); band[28:196, 28:196] = False
            for i in range(len(x)):
                mm = g[i] / (g[i].sum() + 1e-12)
                rows.append({'sample_id': cases.sample_id[i], 'selection': cases.selection[i], 'architecture': NAMES[key],
                             'pred_class': CLASSES[int(prob[i].argmax())], 'prob_rust': float(prob[i, C2I['rust']]),
                             'cam_mass_outer_band': float(mm[band].sum()), 'uniform_expectation_outer_band': float(band.mean())})
            del cam, m; torch.cuda.empty_cache()
        except Exception as e:
            status[key] = 'error: ' + repr(e)[:300]; log('Grad-CAM falló para', key, e); traceback.print_exc()
    np.savez_compressed(gdir / 'gradcam_maps_rust_target.npz', **maps, sample_ids=cases.sample_id.to_numpy())
    df = pd.DataFrame(rows); atomic_csv(df, gdir / 'gradcam_cases_by_architecture.csv'); atomic_csv(cases, gdir / 'gradcam_case_list.csv')
    # cross-architecture agreement of maps (Spearman over 28x28 downsampled maps)
    from scipy.stats import spearmanr
    ok = [k for k in KEYS if k in maps]; agree = []
    for i in range(len(cases)):
        for a1 in range(len(ok)):
            for a2 in range(a1 + 1, len(ok)):
                m1 = maps[ok[a1]][i].reshape(28, 8, 28, 8).mean((1, 3)).ravel(); m2 = maps[ok[a2]][i].reshape(28, 8, 28, 8).mean((1, 3)).ravel()
                agree.append({'sample_id': cases.sample_id[i], 'a': NAMES[ok[a1]], 'b': NAMES[ok[a2]], 'spearman': float(spearmanr(m1, m2)[0])})
    atomic_csv(pd.DataFrame(agree), gdir / 'gradcam_cross_architecture_spearman.csv')
    for part, sl in [('A_archived_cases', slice(0, 8)), ('B_random_cases', slice(8, 16))]:
        fig, ax = plt.subplots(8, len(ok) + 1, figsize=(2.1 * (len(ok) + 1), 17))
        for r, i in enumerate(range(sl.start, sl.stop)):
            ax[r, 0].imshow(imgs[i]); ax[r, 0].set_ylabel(cases.sample_id[i].replace('TOM2024_MAIZE_', ''), fontsize=8)
            for cidx, key in enumerate(ok, 1):
                ax[r, cidx].imshow(imgs[i]); ax[r, cidx].imshow(maps[key][i], cmap='jet', alpha=0.45, vmin=0, vmax=1)
                q = df[(df.sample_id == cases.sample_id[i]) & (df.architecture == NAMES[key])].iloc[0]
                ax[r, cidx].set_title(f'{q.pred_class} | p(rust)={q.prob_rust:.2f}', fontsize=7)
                if r == 0:
                    ax[r, cidx].text(0.5, 1.25, NAMES[key], transform=ax[r, cidx].transAxes, ha='center', fontsize=9, weight='bold')
            for cc in range(len(ok) + 1):
                ax[r, cc].set_xticks([]); ax[r, cc].set_yticks([])
        ax[0, 0].text(0.5, 1.25, 'TOM2024 Rust-D', transform=ax[0, 0].transAxes, ha='center', fontsize=9, weight='bold')
        plt.tight_layout(); fig.savefig(gdir / f'Figure_gradcam_six_architectures_{part}.png', dpi=130); plt.close(fig)
    mark(out, 'gradcam', {'status': status, 'cases': len(cases), 'target': 'rust logit', 'seed': 17})


# ============================================================================ 7. analysis
def task_frame(meta, task):
    spec = {'pv2': ['pv_bs'], 'pv3': ['pv_bs', 'pv_rust'], 'pv4': ['pv_bs', 'pv_rust', 'pv_healthy_clean'],
            'tom3': ['tom_p'], 'tom4': ['tom_p', 'tom_helm'], 'tom5': ['tom_p', 'tom_helm', 'tom_curv']}[task]
    return spec


def metric_factory(y, preds, labels):
    """Vectorized weighted macro-F1 for 30 runs: returns f(w) -> (30,)."""
    ind = []
    for c in labels:
        tp = ((y == c)[None] & (preds == c)).astype(np.float32); fn = ((y == c)[None] & (preds != c)).astype(np.float32)
        fp = ((y != c)[None] & (preds == c)).astype(np.float32); ind.append((tp, fn, fp))

    def f(w):
        out = np.zeros(preds.shape[0])
        for tp, fn, fp in ind:
            a, b, c = tp @ w, fn @ w, fp @ w; d = 2 * a + b + c
            out += np.divide(2 * a, d, out=np.zeros_like(d), where=d > 0)
        return out / len(ind)
    return f


def stage_analysis(out, meta, B=2000):
    out = Path(out); ana = out / 'analysis'; ana.mkdir(parents=True, exist_ok=True)
    overlap = pd.read_csv(out / 'pv_healthy_internal_overlap.csv')
    clean = set(overlap[~overlap.matched_le5].sample_id)
    meta = meta.copy()
    probs = {c: load_probs(out, c) for c in meta.cohort.unique()}
    zemb = np.load(out / 'dinov2_embeddings.npz')
    if 'pv_healthy' in probs:
        keep = meta[meta.cohort == 'pv_healthy'].sample_id.isin(clean).to_numpy()
        probs['pv_healthy_clean'] = probs['pv_healthy'][:, keep]
        meta = pd.concat([meta[meta.cohort != 'pv_healthy'], meta[(meta.cohort == 'pv_healthy') & meta.sample_id.isin(clean)].assign(cohort='pv_healthy_clean')], ignore_index=True)
        emb_clean = zemb['pv_healthy'][keep]
    per_run, summary, boots = [], [], []
    for task in ['pv2', 'pv3', 'pv4', 'tom3', 'tom4', 'tom5']:
        cohorts = task_frame(meta, task)
        if not all(c in probs for c in cohorts):
            log('Tarea omitida (cohorte ausente):', task); continue
        sub = pd.concat([meta[meta.cohort == c] for c in cohorts], ignore_index=True)
        y = sub['class'].map(C2I).to_numpy(); P = np.concatenate([probs[c] for c in cohorts], axis=1)
        labels = [C2I[c] for c in TASKS[task]]
        for j, (k, s) in enumerate(RUNS):
            r = task_metrics(y, P[j], task); r.update({'architecture': NAMES[k], 'model_key': k, 'seed': s}); per_run.append(r)
        emb = np.concatenate([emb_clean if c == 'pv_healthy_clean' else zemb[c] for c in cohorts])
        rec = (sub.cohort + '::' + sub.group.astype(str)).to_numpy()
        for rule in ['open_9way', 'closed']:
            preds = np.stack([predict(P[j]) if rule == 'open_9way' else predict(P[j], TASKS[task]) for j in range(30)])
            f = metric_factory(y, preds, labels)
            for fam_name, thr in [('recorded_groups', None)] + [(f'recorded+dinov2_cos{t:.2f}', t) for t in THRESHOLDS]:
                fam = union_groups(rec) if thr is None else union_groups(rec, components(emb, thr))
                bt = family_bootstrap(fam, y, f, B=B); bt.insert(0, 'family_definition', fam_name); bt.insert(0, 'rule', rule); bt.insert(0, 'task', task)
                boots.append(bt)
    pr = pd.DataFrame(per_run); atomic_csv(pr, ana / 'per_run_metrics_open_closed.csv')
    cols = [c for c in pr.columns if c.startswith(('macro_f1', 'out_of_set', 'recall_', 'precision_'))]
    sm = pr.groupby(['task', 'architecture'], sort=False)[cols].agg(['mean', 'std'])
    sm.columns = ['_'.join(c) for c in sm.columns]; sm = sm.reset_index()
    for rule in ['open_9way', 'closed']:
        sm[f'rank_{rule}'] = sm.groupby('task')[f'macro_f1_{rule}_mean'].rank(ascending=False, method='min').astype(int)
    atomic_csv(sm, ana / 'architecture_means_open_closed.csv')
    bt = pd.concat(boots, ignore_index=True); atomic_csv(bt, ana / 'family_bootstrap_rank_stability.csv')
    sel = []
    for (task, rule, fam), g in bt.groupby(['task', 'rule', 'family_definition'], sort=False):
        b = g.sort_values('observed_mean', ascending=False)
        sel.append({'task': task, 'rule': rule, 'family_definition': fam, 'families': int(g.families.iloc[0]), 'images': int(g.images.iloc[0]),
                    'largest_family': int(g.largest_family.iloc[0]), 'selected': b.architecture.iloc[0], 'selected_mean': b.observed_mean.iloc[0],
                    'p_rank1_selected': b.p_rank1.iloc[0], 'runner_up': b.architecture.iloc[1],
                    'gap_ci95': f'[{-b.diff_ci95_high.iloc[1]:.4f}, {-b.diff_ci95_low.iloc[1]:.4f}]'})
    atomic_csv(pd.DataFrame(sel), ana / 'selection_summary.csv')
    # family counts at each threshold, per cohort
    fc = []
    for c in [c for c in zemb.files]:
        e = zemb[c]
        for t in THRESHOLDS:
            fam = components(e, t); cnt = np.bincount(fam)
            fc.append({'cohort': c, 'cosine_threshold': t, 'images': len(e), 'families': int(len(cnt)), 'multi_image_families': int((cnt > 1).sum()),
                       'images_in_multi_image_families': int(cnt[cnt > 1].sum()), 'largest_family': int(cnt.max())})
    atomic_csv(pd.DataFrame(fc), ana / 'dinov2_family_counts.csv')
    sheets = []
    for c in ['pv_bs', 'pv_rust', 'tom_p']:
        if c in zemb.files:
            sheets.append(near_pair_sheet(out, meta, c, ana / f'dinov2_pairs_near_threshold_{c}.png'))
    if sheets:
        atomic_csv(pd.concat(sheets), ana / 'dinov2_pairs_near_threshold_for_human_review.csv')
    mark(out, 'analysis', {'tasks': sorted(pr.task.unique().tolist()), 'bootstrap_replicates': B})
    log('Resumen de selección:\n' + pd.DataFrame(sel).to_string(index=False))
    return sm


# ============================================================================ 8. Tanzania (optional)
def stage_tanzania(out, internal):
    import requests
    tz = WORK / 'tanzania'; tz.mkdir(parents=True, exist_ok=True); zp = tz / 'fkw49mz3xs-1.zip'
    urls = ['https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/fkw49mz3xs-1.zip']
    got = zp.is_file() and zipfile.is_zipfile(zp)
    for u in urls:
        if got:
            break
        try:
            log('Descargando Tanzania:', u)
            with requests.get(u, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(zp, 'wb') as f:
                    for b in r.iter_content(16 * 1024 ** 2):
                        f.write(b)
            got = zipfile.is_zipfile(zp)
        except Exception as e:
            log('  no disponible:', e)
    if not got:
        atomic_json({'status': 'download_unavailable', 'urls_tried': urls,
                     'next_step': 'Descargar manualmente "Download All" de doi:10.17632/fkw49mz3xs.1 a ' + str(zp)}, Path(out) / 'tanzania_check.json')
        return
    rows = []
    with zipfile.ZipFile(zp) as z:
        names = [n for n in z.namelist() if Path(n).suffix.lower() in IMG_EXT]
        log('Tanzania imágenes en ZIP:', len(names))
        for i, n in enumerate(names, 1):
            b = z.read(n)
            try:
                with Image.open(io.BytesIO(b)) as im:
                    ph = phash_hex(im)
            except Exception:
                ph = ''
            rows.append({'zip_member': n, 'folder': str(Path(n).parent), 'sha256': sha_bytes(b), 'phash': ph})
            if i % 1000 == 0:
                log('  Tanzania', i, '/', len(names))
    t = pd.DataFrame(rows)
    t['exact_internal'] = t.sha256.isin(set(internal.sha256))
    ok = t.phash.str.len() == 16; ii = internal[internal.phash.str.len() == 16].reset_index(drop=True)
    t['phash_le5_internal'] = False; t['nearest_internal_class'] = ''; t['nearest_internal_partition'] = ''
    if ok.any():
        d = hamming_matrix(t.loc[ok, 'phash'], ii.phash)
        t.loc[ok, 'phash_le5_internal'] = d.min(1) <= 5
        t.loc[ok, 'nearest_internal_class'] = ii['class'].values[d.argmin(1)]; t.loc[ok, 'nearest_internal_partition'] = ii.partition.values[d.argmin(1)]
    atomic_csv(t, Path(out) / 'tanzania_vs_internal.csv')
    m = t[t.exact_internal | t.phash_le5_internal]
    internal_hit = internal[internal.sha256.isin(set(t.sha256))]
    summ = {'status': 'done', 'zip_bytes': zp.stat().st_size, 'zip_sha256': sha_file(zp), 'tanzania_images': int(len(t)),
            'by_folder': t.folder.value_counts().astype(int).to_dict(),
            'exact_sha256_in_internal': int(t.exact_internal.sum()), 'phash_le5_in_internal': int(t.phash_le5_internal.sum()),
            'matches_by_folder_and_internal_class': m.groupby(['folder', 'nearest_internal_class']).size().astype(int).to_dict().__repr__(),
            'internal_images_with_exact_tanzania_copy_by_class': internal_hit['class'].value_counts().astype(int).to_dict(),
            'internal_images_indexed_by_class': internal['class'].value_counts().astype(int).to_dict()}
    atomic_json(summ, Path(out) / 'tanzania_check.json'); log('Tanzania:', summ)


# ============================================================================ main
def export(out):
    out = Path(out); z = out.parent / 'MAIZ_14A_Resultados.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for p in sorted(out.rglob('*')):
            if p.is_file() and p.stat().st_size < 200 * 1024 ** 2:
                f.write(p, str(p.relative_to(out)))
    shutil.copy(z, '/content/MAIZ_14A_Resultados.zip'); log('ZIP de resultados:', z)
    return z


def run_all(root, tanzania=True):
    root = Path(root); out = root / OUT_REL; out.mkdir(parents=True, exist_ok=True); WORK.mkdir(parents=True, exist_ok=True)
    try:
        stage_env(out)
        internal = stage_internal_index(root, out)
        meta = stage_cohorts(root, out)
        pv_healthy_overlap(meta, internal, out)
        stage_inference(root, out, meta)
        stage_dino(out, meta)
        if not done(out, 'gradcam'):
            stage_gradcam(out, meta)
        stage_analysis(out, meta)
        if tanzania and not (out / 'tanzania_check.json').is_file():
            try:
                stage_tanzania(out, internal)
            except Exception as e:
                atomic_json({'status': 'error', 'error': repr(e)}, out / 'tanzania_check.json')
        atomic_json({'status': 'COMPLETE', 'completed_utc': utc(), 'version': VERSION}, out / 'MAIZ14A_STATUS.json')
        log('MAIZ_14A COMPLETO')
    except Exception as e:
        atomic_json({'status': 'ERROR', 'error': repr(e), 'traceback': traceback.format_exc(), 'utc': utc()}, out / 'MAIZ14A_last_error.json')
        raise
    finally:
        export(out)
