"""MAIZ_14C: harmonized-preprocessing sensitivity for every evaluation axis.

The historical evaluation used two input recipes:
  crop   : EXIF transpose -> RGB -> Resize(short side 256, bicubic) -> CenterCrop(224)
           (internal test and Pandian2019; identical to the training-time validation transform)
  squash : cache recipe (EXIF for TOM2024, RGB, short side capped at 256 bilinear, JPEG q95)
           -> Resize((224, 224), bilinear) (PlantVillage and TOM2024)
This module scores all 30 public checkpoints on every axis with both recipes, so that each axis is
available under one common recipe. Inference only; checkpoints are SHA-256 verified.
"""
from pathlib import Path
import io, json, time, gc
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import maiz14_run as R
from maiz14 import (KEYS, NAMES, SEEDS, RUNS, C2I, CLASSES, macro_f1, pv_style_cache, extract_prepared,
                    build_model, load_checkpoint, download_checkpoint, atomic_csv, atomic_json, utc, sha_bytes)

OUT_REL = 'REVISION_POST_REVIEW_20261029/MAIZ14C_preprocesamiento'
DOMAINS = ['internal_test', 'pandian2019', 'plantvillage', 'tom2024_primary', 'pv_rust']
HISTORICAL = {'internal_test': 'crop', 'pandian2019': 'crop', 'plantvillage': 'squash', 'tom2024_primary': 'squash', 'pv_rust': None}
TARGETS = {'internal_test': CLASSES, 'pandian2019': ['rust'], 'plantvillage': ['leaf_blight', 'leaf_spot'],
           'tom2024_primary': ['fall_armyworm', 'healthy', 'rust'], 'pv_rust': ['rust']}
METRIC = {'internal_test': 'nine-class macro-F1', 'pandian2019': 'rust recall', 'plantvillage': 'blight/leaf-spot macro-F1',
          'tom2024_primary': 'three-class macro-F1', 'pv_rust': 'rust recall (public PlantVillage rust, 1,192)'}


def crop_array(im):
    from torchvision import transforms as T
    tf = T.Compose([T.Resize(256, interpolation=T.InterpolationMode.BICUBIC), T.CenterCrop(224)])
    return np.asarray(tf(ImageOps.exif_transpose(im).convert('RGB')), dtype=np.uint8)


def squash_array(im, cached):
    if not cached:
        im = pv_style_cache(im, exif=True)
    return np.asarray(im.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR), dtype=np.uint8)


def stage_arrays(root, out):
    """Two uint8 arrays per domain (crop, squash) built from the verified historical caches."""
    work = R.WORK / 'arrays14c'; work.mkdir(parents=True, exist_ok=True)
    base = Path(root) / R.PREP_REL.rsplit('/', 1)[0]
    meta = {}
    for d in DOMAINS:
        if d == 'pv_rust':
            files = R.fetch_pv_public(R.WORK / 'PlantVillage-Dataset')['Corn_(maize)___Common_rust_']
            frame = pd.DataFrame({'sample_id': [p.name for p in files], 'class': 'rust', 'local_path': [str(p) for p in files]})
            cached = False
        else:
            frame = extract_prepared(base, d, R.WORK / 'prepared')
            cached = d in {'plantvillage', 'tom2024_primary'}
        meta[d] = frame[['sample_id', 'class']].copy()
        fc, fs = work / f'{d}_crop.npy', work / f'{d}_squash.npy'
        if fc.is_file() and fs.is_file():
            continue
        ac = np.zeros((len(frame), 224, 224, 3), np.uint8); as_ = np.zeros_like(ac)
        for i, p in enumerate(frame.local_path):
            with Image.open(p) as im:
                im.load()
                ac[i] = crop_array(im)
                as_[i] = squash_array(im, cached)
        np.save(fc, ac); np.save(fs, as_)
        R.log('Arreglos', d, len(frame))
    return meta


def stage_inference(root, out, meta):
    import torch
    zen = pd.read_csv(R.CODE / 'zenodo_files.csv').set_index('filename')
    work = R.WORK / 'arrays14c'; pdir = Path(out) / 'probabilities'; pdir.mkdir(parents=True, exist_ok=True)
    arrays = {(d, p): np.load(work / f'{d}_{p}.npy', mmap_mode='r') for d in DOMAINS for p in ['crop', 'squash']}
    mean = torch.tensor([.485, .456, .406], device='cuda').view(1, 3, 1, 1); std = torch.tensor([.229, .224, .225], device='cuda').view(1, 3, 1, 1)
    exp = np.load(R.CODE / 'expected_argmax.npz'); runs = [str(r) for r in exp['runs']]
    gates = []
    for n, (key, seed) in enumerate(RUNS, 1):
        f = pdir / f'{key}_seed{seed}.npz'
        if not f.is_file():
            name = f'{key}_seed{seed}.pt'
            path = download_checkpoint(name, zen.loc[name, 'sha256'], R.WORK / 'checkpoints' / name)
            model = load_checkpoint(build_model(key), path).to('cuda').eval(); res = {}
            for (d, p), a in arrays.items():
                o = np.zeros((len(a), 9), np.float32)
                with torch.inference_mode():
                    for i in range(0, len(a), 64):
                        x = torch.from_numpy(np.array(a[i:i + 64])).to('cuda').permute(0, 3, 1, 2).float().div_(255)
                        with torch.autocast('cuda', dtype=torch.float16):
                            o[i:i + 64] = torch.softmax(model((x - mean) / std).float(), 1).cpu().numpy()
                res[f'{d}__{p}'] = o
            np.savez_compressed(f, **res); del model; gc.collect(); torch.cuda.empty_cache()
            path.unlink(missing_ok=True)
        z = np.load(f); j = runs.index(f'{key}|{seed}'); row = {'model_key': key, 'seed': seed}
        for d in ['internal_test', 'pandian2019', 'plantvillage', 'tom2024_primary']:
            row[f'{d}_disagreements'] = int((z[f'{d}__{HISTORICAL[d]}'].argmax(1) != exp[d][j]).sum())
        gates.append(row)
        R.log(f'[{n}/30] {key} s{seed} discrepancias con lo archivado (receta histórica):',
              {k.replace('_disagreements', ''): v for k, v in row.items() if k.endswith('disagreements')})
        if any(row[f'{d}_disagreements'] > 0.05 * len(meta[d]) for d in ['internal_test', 'pandian2019', 'plantvillage', 'tom2024_primary']):
            raise RuntimeError('Discrepancia >5% con las predicciones archivadas; se detiene.')
    g = pd.DataFrame(gates); atomic_csv(g, Path(out) / 'agreement_gate_14c.csv')
    return g


def kendall_w(ranks):
    """ranks: (m axes, n architectures)."""
    m, n = ranks.shape; R_ = ranks.sum(0); S = ((R_ - R_.mean()) ** 2).sum()
    return 12 * S / (m ** 2 * (n ** 3 - n))


def stage_analysis(out, meta):
    rows = []
    for key, seed in RUNS:
        z = np.load(Path(out) / 'probabilities' / f'{key}_seed{seed}.npz')
        for d in DOMAINS:
            y = meta[d]['class'].map(C2I).to_numpy(); labels = [C2I[c] for c in TARGETS[d]]
            for p in ['crop', 'squash']:
                yp = z[f'{d}__{p}'].argmax(1)
                v = float((yp == C2I['rust']).mean()) if d in {'pandian2019', 'pv_rust'} else macro_f1(y, yp, labels)
                rows.append({'domain': d, 'protocol': p, 'model_key': key, 'architecture': NAMES[key], 'seed': seed, 'value': v,
                             'pred_healthy_fraction': float((yp == C2I['healthy']).mean())})
    pr = pd.DataFrame(rows); atomic_csv(pr, Path(out) / 'per_run_by_protocol.csv')
    sm = pr.groupby(['domain', 'protocol', 'architecture'], sort=False).agg(mean=('value', 'mean'), sd=('value', 'std'),
                                                                             pred_healthy=('pred_healthy_fraction', 'mean')).reset_index()
    sm['rank'] = sm.groupby(['domain', 'protocol'])['mean'].rank(ascending=False, method='min').astype(int)
    atomic_csv(sm, Path(out) / 'architecture_means_by_protocol.csv')
    # concordance of the four principal axes under each single protocol and under the historical mix
    order = [NAMES[k] for k in KEYS]; conc = []
    axes = ['internal_test', 'pandian2019', 'plantvillage', 'tom2024_primary']
    for label, prot in [('historical mix', HISTORICAL), ('all crop', {a: 'crop' for a in axes}), ('all squash', {a: 'squash' for a in axes})]:
        rk = np.stack([sm[(sm.domain == a) & (sm.protocol == prot[a])].set_index('architecture').loc[order, 'rank'].to_numpy() for a in axes])
        ext = rk[1:]
        leaders = {a: sm[(sm.domain == a) & (sm.protocol == prot[a])].sort_values('mean', ascending=False).architecture.iloc[0] for a in axes}
        conc.append({'protocol_set': label, 'kendall_W_four_axes': kendall_w(rk), 'kendall_W_external': kendall_w(ext), **{f'leader_{a}': v for a, v in leaders.items()}})
    atomic_csv(pd.DataFrame(conc), Path(out) / 'ranking_concordance_by_protocol.csv')
    R.log('Concordancia:\n' + pd.DataFrame(conc).to_string(index=False))
    piv = sm.pivot_table(index=['domain', 'architecture'], columns='protocol', values='mean').reset_index()
    R.log('Medias por protocolo:\n' + piv.round(4).to_string(index=False))
    return sm


def run_all(root):
    root = Path(root); out = root / OUT_REL; out.mkdir(parents=True, exist_ok=True)
    R.stage_env(out)
    meta = stage_arrays(root, out)
    stage_inference(root, out, meta)
    stage_analysis(out, meta)
    atomic_json({'status': 'COMPLETE', 'utc': utc()}, out / 'MAIZ14C_STATUS.json')
    import zipfile, shutil
    z = out.parent / 'MAIZ_14C_Resultados.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                f.write(p, str(p.relative_to(out)))
    shutil.copy(z, '/content/MAIZ_14C_Resultados.zip'); R.log('ZIP:', z)
