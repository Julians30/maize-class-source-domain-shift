"""MAIZ_14: inference-only analyses that close reviewer requests with the 30 public checkpoints.

No training, no checkpoint selection, no change to any frozen model. All outputs are new,
separately labelled sensitivity analyses. Checkpoints come from the public Zenodo record
10.5281/zenodo.24064539 and are verified by SHA-256 before use.

Blocks
  A  Recomputed nine-output probabilities on PlantVillage (1,498), Pandian2019 (1,922) and
     TOM2024 primary (1,230), gated against the archived argmax predictions.
  B  PlantVillage closed-set sensitivity (argmax restricted to blight/leaf spot).
  C  PlantVillage three-class cohort (blight, leaf spot, rust) from the verified public source.
  D  TOM2024 Helminthosporiosis-D mapped to leaf_blight (four-class sensitivity).
  E  DINOv2 candidate families and family-cluster bootstrap of architecture ranks.
  F  Grad-CAM for the six architectures (seed 17) on a fixed, outcome-blind TOM2024 rust sample.
"""
from pathlib import Path
import hashlib, io, json, os, shutil, subprocess, sys, tarfile, time, traceback
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

VERSION = '2026-11-09-maiz14'
CLASSES = ['fall_armyworm', 'grasshopper', 'healthy', 'leaf_beetle', 'leaf_blight',
           'leaf_spot', 'lethal_necrosis', 'rust', 'streak_virus']
C2I = {c: i for i, c in enumerate(CLASSES)}
KEYS = ['mobilenetv3_large', 'resnet50', 'efficientnet_b0', 'mobilevit_s',
        'vit_base_patch16_224', 'swin_tiny_patch4_window7_224']
NAMES = {'mobilenetv3_large': 'MobileNetV3-Large', 'resnet50': 'ResNet50', 'efficientnet_b0': 'EfficientNet-B0',
         'mobilevit_s': 'MobileViT-S', 'vit_base_patch16_224': 'ViT-Base/16', 'swin_tiny_patch4_window7_224': 'Swin-Tiny'}
SEEDS = [17, 42, 73, 101, 137]
RUNS = [(k, s) for k in KEYS for s in SEEDS]
ZENODO = 'https://zenodo.org/api/records/24064539/files/{}/content'
PV_COMMIT = '7f7ecc7e1eaca78107e3affe7cb5abd9427e139a'
PV_REPO = 'https://github.com/spMohanty/PlantVillage-Dataset'
TASKS = {  # target sets; argmax 'open' uses all nine outputs, 'closed' restricts to the target set
    'pv2': ['leaf_blight', 'leaf_spot'],
    'pv3': ['leaf_blight', 'leaf_spot', 'rust'],
    'tom3': ['fall_armyworm', 'healthy', 'rust'],
    'pv4': ['leaf_blight', 'leaf_spot', 'rust', 'healthy'],
    'tom4': ['fall_armyworm', 'healthy', 'rust', 'leaf_blight'],
    'tom5': ['fall_armyworm', 'healthy', 'rust', 'leaf_blight', 'leaf_spot'],
}


def utc():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(8 * 1024 ** 2), b''):
            h.update(b)
    return h.hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def atomic_json(x, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + '.tmp'); t.write_text(json.dumps(x, indent=2, ensure_ascii=False)); os.replace(t, p)


def atomic_csv(df, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + '.tmp'); df.to_csv(t, index=False); os.replace(t, p)


# ----------------------------------------------------------------------------- images
def pv_style_cache(im, exif):
    """Same cache recipe as the historical PlantVillage/TOM2024 evaluation (MAIZ_04A)."""
    if exif:
        im = ImageOps.exif_transpose(im)
    im = im.convert('RGB'); w, h = im.size
    if min(w, h) > 256:
        s = 256 / min(w, h); im = im.resize((round(w * s), round(h * s)), Image.Resampling.BILINEAR)
    buf = io.BytesIO(); im.save(buf, format='JPEG', quality=95); buf.seek(0)
    out = Image.open(buf); out.load(); return out.convert('RGB')


def extract_prepared(base, domain, dest):
    """Restore the verified MAIZ_04A cache (manifest + images.tar) for one domain."""
    d = Path(base) / 'prepared' / domain
    man = pd.read_csv(d / 'manifest.csv', dtype=str, keep_default_na=False)
    dest = Path(dest) / domain; dest.mkdir(parents=True, exist_ok=True)
    expected = dict(zip(man.cache_name, man.cache_sha256))
    if not all((dest / n).is_file() for n in expected):
        with tarfile.open(d / 'images.tar', 'r') as t:
            for m in t.getmembers():
                if m.name not in expected or not m.isfile() or Path(m.name).name != m.name:
                    raise ValueError('Miembro TAR inesperado: ' + m.name)
                with t.extractfile(m) as src, open(dest / m.name, 'wb') as f:
                    shutil.copyfileobj(src, f)
    bad = [n for n, h in expected.items() if sha_file(dest / n) != h]
    if bad:
        raise ValueError(f'{len(bad)} imágenes de caché con SHA distinto en {domain}')
    man['local_path'] = [str(dest / n) for n in man.cache_name]
    return man


def fetch_pv_public(dest):
    """Sparse checkout of the four maize folders at the verified public commit."""
    dest = Path(dest)
    color = dest / 'raw' / 'color'
    if not color.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout', '--depth', '1', PV_REPO, str(dest)], check=True)
        subprocess.run(['git', '-C', str(dest), 'fetch', '--depth', '1', 'origin', PV_COMMIT], check=True)
        subprocess.run(['git', '-C', str(dest), 'sparse-checkout', 'set', '--no-cone', 'raw/color/Corn_*'], check=True)
        subprocess.run(['git', '-C', str(dest), 'checkout', PV_COMMIT], check=True)
    folders = sorted(p for p in color.iterdir() if p.is_dir() and p.name.startswith('Corn'))
    return {p.name: sorted(q for q in p.iterdir() if q.suffix.lower() in {'.jpg', '.jpeg', '.png'}) for p in folders}


# ----------------------------------------------------------------------------- models
def build_model(key):
    import torch.nn as nn
    import torchvision.models as tv
    import timm
    if key == 'mobilenetv3_large':
        m = tv.mobilenet_v3_large(weights=None); m.classifier[3] = nn.Linear(m.classifier[3].in_features, 9)
    elif key == 'resnet50':
        m = tv.resnet50(weights=None); m.fc = nn.Linear(m.fc.in_features, 9)
    elif key == 'efficientnet_b0':
        m = tv.efficientnet_b0(weights=None); m.classifier[1] = nn.Linear(m.classifier[1].in_features, 9)
    else:
        names = {'mobilevit_s': 'mobilevit_s', 'vit_base_patch16_224': 'vit_base_patch16_224.augreg_in1k',
                 'swin_tiny_patch4_window7_224': 'swin_tiny_patch4_window7_224.ms_in1k'}
        m = timm.create_model(names[key], pretrained=False, num_classes=9)
    return m


def load_checkpoint(model, path):
    import torch
    obj = torch.load(path, map_location='cpu', weights_only=False)
    if isinstance(obj, dict):
        for k in ('model_state_dict', 'state_dict', 'model'):
            if k in obj and isinstance(obj[k], dict):
                if 'class_to_idx' in obj and obj['class_to_idx'] != C2I:
                    raise ValueError('Orden de clases distinto en el checkpoint')
                obj = obj[k]; break
    sd = {k[7:] if k.startswith('module.') else k: v for k, v in obj.items()}
    model.load_state_dict(sd, strict=True)
    return model


def download_checkpoint(fname, sha, dest):
    import requests
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and sha_file(dest) == sha:
        return dest
    for attempt in range(4):
        try:
            tmp = dest.with_name(dest.name + '.part'); h = hashlib.sha256()
            with requests.get(ZENODO.format(fname), stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp, 'wb') as f:
                    for b in r.iter_content(16 * 1024 ** 2):
                        f.write(b); h.update(b)
            if h.hexdigest() != sha:
                raise ValueError('SHA-256 distinto: ' + fname)
            os.replace(tmp, dest); return dest
        except Exception as e:
            print('  reintento de descarga', attempt + 1, fname, e, flush=True); time.sleep(10)
    raise RuntimeError('No se pudo descargar ' + fname)


def make_loader(items, mode, batch=64):
    """items: list of PIL-producing callables. mode 'squash' (PV/TOM) or 'crop' (Pandian)."""
    import torch
    from torchvision import transforms as T
    norm = [T.ToTensor(), T.Normalize([.485, .456, .406], [.229, .224, .225])]
    if mode == 'squash':
        tf = T.Compose([T.Resize((224, 224), interpolation=T.InterpolationMode.BILINEAR)] + norm)
    else:
        tf = T.Compose([T.Resize(256, interpolation=T.InterpolationMode.BICUBIC), T.CenterCrop(224)] + norm)

    class DS(torch.utils.data.Dataset):
        def __len__(self): return len(items)
        def __getitem__(self, i): return tf(items[i]()), i
    return torch.utils.data.DataLoader(DS(), batch_size=batch, shuffle=False, num_workers=2, pin_memory=True)


def infer(model, loader, n):
    import torch
    out = np.zeros((n, 9), dtype=np.float32); seen = 0
    with torch.inference_mode():
        for x, idx in loader:
            with torch.autocast('cuda', dtype=torch.float16):
                lg = model(x.to('cuda', non_blocking=True))
            out[idx.numpy()] = torch.softmax(lg.float(), 1).cpu().numpy(); seen += len(idx)
    if seen != n:
        raise ValueError('Inferencia incompleta')
    return out


# ----------------------------------------------------------------------------- metrics
def macro_f1(y, yp, labels, w=None):
    """Weighted (bootstrap) macro-F1 over `labels`; out-of-set predictions are FN only."""
    w = np.ones(len(y)) if w is None else w
    f = []
    for c in labels:
        tp = (w * ((y == c) & (yp == c))).sum(); fn = (w * ((y == c) & (yp != c))).sum(); fp = (w * ((y != c) & (yp == c))).sum()
        d = 2 * tp + fp + fn; f.append(2 * tp / d if d > 0 else 0.0)
    return float(np.mean(f))


def predict(probs, labels=None):
    if labels is None:
        return probs.argmax(1)
    idx = np.array([C2I[c] for c in labels]); return idx[probs[:, idx].argmax(1)]


def task_metrics(y, probs, task):
    labels = [C2I[c] for c in TASKS[task]]
    yo = predict(probs); yc = predict(probs, TASKS[task])
    r = {'task': task, 'n': int(len(y)),
         'macro_f1_open_9way': macro_f1(y, yo, labels), 'macro_f1_closed': macro_f1(y, yc, labels),
         'out_of_set_fraction_open': float((~np.isin(yo, labels)).mean())}
    for c in TASKS[task]:
        i = C2I[c]; m = y == i
        r[f'recall_open_{c}'] = float((yo[m] == i).mean()) if m.any() else np.nan
        r[f'precision_open_{c}'] = float((y[yo == i] == i).mean()) if (yo == i).any() else np.nan
    return r


def components(emb, thr):
    """Connected components of the cosine-similarity graph (edge if sim >= thr)."""
    n = len(emb); parent = np.arange(n)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    sims = emb @ emb.T
    ii, jj = np.where(np.triu(sims >= thr, 1))
    for a, b in zip(ii, jj):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    roots = np.array([find(i) for i in range(n)])
    _, fam = np.unique(roots, return_inverse=True)
    return fam


def union_groups(*labelings):
    """Merge several image groupings (any shared label in any grouping joins two images)."""
    n = len(labelings[0]); parent = np.arange(n)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for lab in labelings:
        first = {}
        for i, g in enumerate(pd.Series(lab).astype(str)):
            if g in first:
                ra, rb = find(first[g]), find(i)
                if ra != rb:
                    parent[rb] = ra
            else:
                first[g] = i
    return np.unique([find(i) for i in range(n)], return_inverse=True)[1]


def family_bootstrap(fam, y, per_run_metric, B=2000, seed=20261109):
    """Class-stratified family-cluster bootstrap of the five-seed architecture means.

    fam: family index per image; y: class per image (a family is stratified by its majority class);
    per_run_metric(w) -> array (30,) ordered KEYS x SEEDS for image weights w.
    """
    rng = np.random.default_rng(seed); fam = np.asarray(fam); nf = fam.max() + 1
    fam_class = pd.Series(y).groupby(fam).agg(lambda s: s.value_counts().index[0]).reindex(range(nf)).to_numpy()
    strata = [np.where(fam_class == c)[0] for c in np.unique(fam_class)]
    obs = per_run_metric(np.ones(len(fam))).reshape(6, 5).mean(1); best = int(obs.argmax())
    boots = np.zeros((B, 6))
    for b in range(B):
        draw = np.zeros(nf)
        for s in strata:
            draw += np.bincount(s[rng.integers(0, len(s), len(s))], minlength=nf)
        boots[b] = per_run_metric(draw[fam]).reshape(6, 5).mean(1)
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    diff = boots - boots[:, [best]]; dlo, dhi = np.percentile(diff, [2.5, 97.5], axis=0)
    ranks = (-boots).argsort(1).argsort(1) + 1
    return pd.DataFrame({'architecture': [NAMES[k] for k in KEYS], 'observed_mean': obs, 'ci95_low': lo, 'ci95_high': hi,
                         'observed_rank': (-obs).argsort().argsort() + 1, 'p_rank1': np.bincount(boots.argmax(1), minlength=6) / B,
                         'median_rank': np.median(ranks, 0), 'diff_vs_observed_best': obs - obs[best],
                         'diff_ci95_low': dlo, 'diff_ci95_high': dhi, 'families': int(nf), 'images': int(len(fam)),
                         'largest_family': int(np.bincount(fam).max()), 'bootstrap_replicates': B})
