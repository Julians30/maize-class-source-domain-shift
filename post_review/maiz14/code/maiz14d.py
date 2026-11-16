"""MAIZ_14D (second review round): two analyses that need the internal images.

1. DINOv2 similarity between every external evaluation image and the internal training / validation
   (and test) images. MAIZ_14A searched only inside each external cohort.
2. Source classifier relabelled with the primary public sources traced in MAIZ_14T
   (Tanzania, PlantVillage, Adege, CCMT) instead of the six operational filename components.
   The recipe is the archived one (notebook 07: torchvision MobileNetV3-Large IMAGENET1K_V1, seed 17,
   up to 12 epochs, patience 3, AdamW, OneCycleLR, batch 32 x 2, label smoothing 0.10).

No disease/pest checkpoint is trained or changed. Stages are resumable.
"""
from pathlib import Path
import gc, io, json, math, os, random, re, shutil, tarfile, time, traceback, zipfile
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import maiz14_run as R
from maiz14 import (C2I, CLASSES, pv_style_cache, extract_prepared, atomic_csv, atomic_json, utc, sha_file, sha_bytes, VERSION)

OUT_REL = 'REVISION_POST_REVIEW_20261029/MAIZ14D_dino_cruzado_y_fuentes'
WORK = Path('/content/maiz14d_work')
THR = [0.90, 0.95, 0.97]
REAL = {'Adege_field_smartphone': 'Adege', 'Adege_rust_rss': 'Adege', 'CIMMYT_MLND': 'Tanzania', 'Kaggle_HEALTHY_up': 'Tanzania',
        'Kaggle_Healthy_paren': 'PlantVillage', 'raw_ccmt_clean': 'CCMT'}
EXPECT_COMPONENT = {'Adege_field_smartphone': 994, 'Adege_rust_rss': 81, 'CIMMYT_MLND': 3229, 'Kaggle_HEALTHY_up': 1667,
                    'Kaggle_Healthy_paren': 709, 'raw_ccmt_clean': 4811}
EXPECT_PART = {'train': 8043, 'validation': 1729, 'test': 1719}
SEED, EPOCHS, PATIENCE, BATCH, ACCUM, LR, WD, SMOOTH, IMG = 17, 12, 3, 32, 2, 3e-4, 1e-4, 0.10, 224
log = R.log


def device():
    import torch
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def component_of(cls, raw_path):
    """Operational component from class and file name (same rule as Supplementary Table S49)."""
    name = Path(raw_path).name; low = str(raw_path).lower()
    if 'raw_ccmt' in low:
        return 'raw_ccmt_clean'
    if cls == 'lethal_necrosis':
        return 'CIMMYT_MLND'
    if cls == 'healthy':
        if name.startswith('HEALTHY'):
            return 'Kaggle_HEALTHY_up'
        if name.lower().startswith('healthy'):
            return 'Kaggle_Healthy_paren'
    if cls == 'rust':
        return 'Adege_rust_rss' if name.lower().startswith('rss') else 'Adege_field_smartphone'
    return 'UNRESOLVED'


def find_manifest(root):
    import subprocess
    p = subprocess.run(['find', str(root), '-name', 'e2a_adege_to_pandian_manifest_v1.csv', '-not', '-path', '*/.*', '-print', '-quit'],
                       capture_output=True, text=True, timeout=1800)
    f = p.stdout.strip().splitlines()
    return Path(f[0]) if f else None


# ============================================================================ 1. internal images
def stage_internal(root, out):
    """Frame of the 11,491 internal images + 224x224 array (DINOv2) + short-side-256 JPEG cache (classifier)."""
    root = Path(root); out = Path(out); f = out / 'internal_frame.csv'
    arr = WORK / 'internal_224.npy'; cdir = WORK / 'cache256'; cdir.mkdir(parents=True, exist_ok=True)
    if f.is_file() and arr.is_file():
        fr = pd.read_csv(f, dtype=str)
        if all((cdir / f'{s}.jpg').is_file() for s in fr.sha256):
            return fr
    code = R.CODE
    vf = pd.read_csv(code / 'validation.csv', dtype=str); val = dict(zip(vf.sha256.str.lower(), vf['class']))
    te = pd.read_csv(code / 'internal_test.csv', dtype=str, keep_default_na=False)
    test = dict(zip(te.sha256.str.lower(), zip(te['class'], te.original_path)))
    rev = root / 'REVISION_POST_REVIEW_20261029'
    pre = json.loads((rev / 'training_data_preflight.json').read_text())
    need = {}
    for raw, name in pre['path_to_cache_name'].items():
        cls = next((p for p in reversed(Path(raw).parts) if p in C2I), None)
        if cls is None:
            parts = [p.lower().replace(' ', '_') for p in Path(raw).parts]
            cls = next((c for c in CLASSES if c in parts or c.replace('grasshopper', 'grasshoper') in parts), None)
        need[name] = (cls, raw)
    local = WORK / pre['archive_name']
    if not (local.is_file() and local.stat().st_size == pre['archive_bytes']):
        log('Copiando la caché de entrenamiento verificada (', round(pre['archive_bytes'] / 1e9, 2), 'GB )')
        shutil.copyfile(rev / 'training_data_cache' / pre['archive_name'], local)
    if sha_file(local) != pre['archive_sha256']:
        raise ValueError('La caché de entrenamiento cambió de huella')
    rows = []; imgs = []

    def add(b, sha, cls, raw, part):
        with Image.open(io.BytesIO(b)) as im:
            im.load()
            c = im.convert('RGB'); w, h = c.size      # archived classifier cache: no EXIF transpose
            if min(w, h) > 256:
                s = 256 / min(w, h); c = c.resize((max(1, round(w * s)), max(1, round(h * s))), Image.BILINEAR)
            c.save(cdir / f'{sha}.jpg', format='JPEG', quality=95)
            imgs.append(R.to_array(pv_style_cache(im, exif=True)))
        rows.append({'sha256': sha, 'class': cls, 'partition': part, 'file': Path(raw).name, 'component': component_of(cls, raw)})

    with tarfile.open(local, 'r:') as t:
        for n, m in enumerate(t):
            if m.name not in need:
                continue
            b = t.extractfile(m).read(); sha = sha_bytes(b)
            if sha + '.img' != m.name:
                raise ValueError('SHA de caché incorrecto: ' + m.name)
            cls, raw = need[m.name]
            if sha in test:
                continue
            cls = val.get(sha, cls)
            if cls not in C2I:
                raise ValueError(f'Clase no reconocida para {raw}')
            add(b, sha, cls, raw, 'validation' if sha in val else 'train')
            if len(rows) % 1000 == 0:
                log('  internas leídas:', len(rows))
    local.unlink(missing_ok=True)
    have = {r['sha256'] for r in rows}
    prep = extract_prepared(root / R.PREP_REL.rsplit('/', 1)[0], 'internal_test', WORK / 'prepared')
    for x in prep.itertuples():
        sha = str(x.sample_id).lower()
        if sha in have:
            continue
        b = Path(x.local_path).read_bytes()
        cls, raw = test.get(sha, (x._asdict().get('class'), x.local_path))
        add(b, sha, cls, raw, 'test')
    fr = pd.DataFrame(rows)
    fr['source'] = fr.component.map(REAL)
    counts = fr.partition.value_counts().to_dict(); comp = fr.component.value_counts().to_dict()
    log('Particiones:', counts, '| componentes:', comp)
    if counts != EXPECT_PART or comp != EXPECT_COMPONENT:
        man = find_manifest(root)
        if man is not None:
            mf = pd.read_csv(man, dtype=str); mf['sha256'] = mf.sha256.str.lower()
            fr = fr.drop(columns=['component', 'source']).merge(mf[['sha256', 'source_operational']].drop_duplicates('sha256'), on='sha256', how='left')
            fr = fr.rename(columns={'source_operational': 'component'}); fr['source'] = fr.component.map(REAL)
            comp = fr.component.value_counts().to_dict(); log('Componentes tomados del manifiesto:', comp)
        if counts != EXPECT_PART or comp != EXPECT_COMPONENT:
            raise ValueError(f'Conteos internos inesperados: {counts} {comp}')
    np.save(arr, np.stack(imgs)); atomic_csv(fr, f)
    R.mark(out, 'internal', {'images': len(fr), 'partitions': counts, 'components': comp,
                             'source_by_class': {f'{a}|{b}': int(v) for (a, b), v in fr.groupby(['source', 'class']).size().items()}})
    return fr


# ============================================================================ 2. DINOv2 cross-cohort search
def embed(a):
    import torch, timm
    dev = device()
    m = timm.create_model(R.DINO, pretrained=True, num_classes=0, img_size=224).to(dev).eval()
    mean = torch.tensor([.485, .456, .406], device=dev).view(1, 3, 1, 1); std = torch.tensor([.229, .224, .225], device=dev).view(1, 3, 1, 1)
    e = []
    with torch.inference_mode():
        for i in range(0, len(a), 128):
            x = torch.from_numpy(np.ascontiguousarray(a[i:i + 128])).to(dev).permute(0, 3, 1, 2).float().div_(255)
            e.append(torch.nn.functional.normalize(m((x - mean) / std).float(), dim=1).cpu().numpy())
    del m; gc.collect()
    if dev.type == 'cuda':
        torch.cuda.empty_cache()
    return np.concatenate(e).astype(np.float32)


def stage_external(root, out_a):
    """External cohorts of MAIZ_14A (arrays rebuilt if this is a new session) plus Pandian2019."""
    meta = R.stage_cohorts(root, out_a)
    arrays = {c: np.load(R.WORK / 'arrays' / f'{c}.npy', mmap_mode='r') for c in meta.cohort.unique()}
    f = WORK / 'pandian_224.npy'
    pan = extract_prepared(Path(root) / R.PREP_REL.rsplit('/', 1)[0], 'pandian2019', WORK / 'prepared')
    if not f.is_file():
        a = np.zeros((len(pan), 224, 224, 3), np.uint8)
        for i, p in enumerate(pan.local_path):
            with Image.open(p) as im:
                im.load(); a[i] = R.to_array(pv_style_cache(im, exif=True))
        np.save(f, a)
    arrays['pandian2019'] = np.load(f, mmap_mode='r')
    pm = pd.DataFrame({'cohort': 'pandian2019', 'sample_id': pan.sample_id.astype(str), 'class': 'rust'})
    meta = pd.concat([meta[['cohort', 'sample_id', 'class']], pm], ignore_index=True)
    return meta, arrays


def stage_dino(root, out, fr, meta, arrays, out_a):
    out = Path(out); f = out / 'dinov2_embeddings_14d.npz'
    if not f.is_file():
        res = {'internal': embed(np.load(WORK / 'internal_224.npy', mmap_mode='r')), 'pandian2019': embed(arrays['pandian2019'])}
        old = Path(out_a) / 'dinov2_embeddings.npz'
        z = np.load(old) if old.is_file() else {}
        for c in meta.cohort.unique():
            if c in res:
                continue
            n = int((meta.cohort == c).sum())
            res[c] = z[c] if (c in getattr(z, 'files', []) and len(z[c]) == n) else embed(arrays[c])
        np.savez_compressed(f, **res)
    z = np.load(f); E = z['internal']
    parts = {'train': (fr.partition == 'train').to_numpy(), 'validation': (fr.partition == 'validation').to_numpy(), 'test': (fr.partition == 'test').to_numpy()}
    near = []; summ = []; pairs = []
    for c in meta.cohort.unique():
        sub = meta[meta.cohort == c].reset_index(drop=True); S = z[c] @ E.T
        row = {'cohort': c, 'images': len(sub)}
        best = {}
        for p, mask in parts.items():
            idx = np.where(mask)[0]; s = S[:, idx]; j = s.argmax(1); v = s[np.arange(len(sub)), j]
            best[p] = (v, idx[j])
            for t in THR:
                row[f'images_with_{p}_neighbour_ge_{t:.2f}'] = int((v >= t).sum())
            row[f'max_cosine_{p}'] = float(v.max()); row[f'median_nearest_{p}'] = float(np.median(v))
        tv = np.maximum(best['train'][0], best['validation'][0])
        for t in THR:
            row[f'images_with_train_or_validation_neighbour_ge_{t:.2f}'] = int((tv >= t).sum())
        summ.append(row)
        d = sub.copy()
        for p in parts:
            v, j = best[p]
            d[f'cosine_{p}'] = v; d[f'nearest_{p}_sha256'] = fr.sha256.to_numpy()[j]; d[f'nearest_{p}_class'] = fr['class'].to_numpy()[j]
            d[f'nearest_{p}_source'] = fr.source.to_numpy()[j]; d[f'nearest_{p}_file'] = fr.file.to_numpy()[j]
        d['cosine_train_or_validation'] = tv; d['ext_index'] = np.arange(len(sub))
        d['int_index'] = np.where(best['train'][0] >= best['validation'][0], best['train'][1], best['validation'][1])
        near.append(d)
        ii, jj = np.where(S >= 0.95)
        if len(ii):
            pp = pd.DataFrame({'cohort': c, 'external_sample': sub.sample_id.to_numpy()[ii], 'external_class': sub['class'].to_numpy()[ii],
                               'internal_sha256': fr.sha256.to_numpy()[jj], 'internal_class': fr['class'].to_numpy()[jj],
                               'internal_partition': fr.partition.to_numpy()[jj], 'internal_source': fr.source.to_numpy()[jj], 'cosine': S[ii, jj]})
            pairs.append(pp.sort_values('cosine', ascending=False).head(20000))
    near = pd.concat(near, ignore_index=True)
    atomic_csv(near.drop(columns=['ext_index', 'int_index']), out / 'dino_external_nearest_internal.csv')
    atomic_csv(pd.DataFrame(summ), out / 'dino_external_vs_internal_summary.csv')
    atomic_csv(pd.concat(pairs, ignore_index=True) if pairs else pd.DataFrame(columns=['cohort']), out / 'dino_external_internal_pairs_ge095.csv')
    bc = near.assign(ge95=near.cosine_train_or_validation >= 0.95, ge97=near.cosine_train_or_validation >= 0.97).groupby(['cohort', 'class']).agg(
        images=('ge95', 'size'), ge_0_95=('ge95', 'sum'), ge_0_97=('ge97', 'sum'), max_cosine=('cosine_train_or_validation', 'max')).reset_index()
    atomic_csv(bc, out / 'dino_external_vs_internal_by_class.csv')
    # internal reference: nearest training neighbour of each validation / test image
    Et = E[parts['train']]
    ref = []
    for p in ['validation', 'test']:
        v = (E[parts[p]] @ Et.T).max(1)
        ref.append({'partition': p, 'images': int(parts[p].sum()), **{f'with_train_neighbour_ge_{t:.2f}': int((v >= t).sum()) for t in THR}, 'median_nearest': float(np.median(v))})
    atomic_csv(pd.DataFrame(ref), out / 'dino_internal_reference.csv')
    sheets(out, near, arrays, fr)
    R.mark(out, 'dino_cross', {'model': R.DINO, 'thresholds': THR, 'cohorts': list(meta.cohort.unique())})
    log('Resumen DINOv2 externas vs internas:\n' + pd.DataFrame(summ)[['cohort', 'images'] + [f'images_with_train_or_validation_neighbour_ge_{t:.2f}' for t in THR] + ['max_cosine_train', 'max_cosine_validation']].to_string(index=False))
    return near


def sheets(out, near, arrays, fr, k=24):
    """Contact sheets: for each cohort, the k external images with the closest training/validation neighbour."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    I = np.load(WORK / 'internal_224.npy', mmap_mode='r'); rows = []
    sd = Path(out) / 'contact_sheets'; sd.mkdir(exist_ok=True)
    for c, d in near.groupby('cohort', sort=False):
        d = d.sort_values('cosine_train_or_validation', ascending=False).head(k)
        fig, ax = plt.subplots(math.ceil(len(d) / 4), 8, figsize=(16, 2.3 * math.ceil(len(d) / 4)), squeeze=False)
        for a_ in ax.ravel():
            a_.set_xticks([]); a_.set_yticks([])
        for n, x in enumerate(d.itertuples()):
            r, q = divmod(n, 4)
            ax[r, 2 * q].imshow(arrays[c][x.ext_index]); ax[r, 2 * q + 1].imshow(I[x.int_index])
            ax[r, 2 * q].set_title(f'{n + 1}. cos={x.cosine_train_or_validation:.3f} ext:{x[3]}', fontsize=7, loc='left')
            ax[r, 2 * q + 1].set_title(f"int:{fr['class'].iloc[x.int_index]} ({fr.partition.iloc[x.int_index]})", fontsize=7, loc='left')
            rows.append({'cohort': c, 'pair': n + 1, 'cosine': float(x.cosine_train_or_validation), 'external_sample': x.sample_id, 'external_class': x[3],
                         'internal_sha256': fr.sha256.iloc[x.int_index], 'internal_class': fr['class'].iloc[x.int_index],
                         'internal_partition': fr.partition.iloc[x.int_index], 'internal_source': fr.source.iloc[x.int_index],
                         'human_judgement': '', 'reviewer_initials': ''})
        plt.tight_layout(); fig.savefig(sd / f'closest_external_internal_{c}.png', dpi=110); plt.close(fig)
    atomic_csv(pd.DataFrame(rows), Path(out) / 'closest_pairs_for_human_review.csv')


# ============================================================================ 3. source controls with primary sources
def set_seed(s):
    import torch
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s); os.environ['PYTHONHASHSEED'] = str(s)
    torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False


def train_eval(tr, va, te, col, labels, tag, out, use_weights, pretrained=True, epochs=EPOCHS):
    """Archived notebook-07 recipe with a different label column."""
    import torch, torch.nn as nn, torch.nn.functional as F, torchvision
    from torch.utils.data import Dataset, DataLoader
    from torchvision import transforms
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, matthews_corrcoef, roc_auc_score, confusion_matrix
    dev = device(); res_f = Path(out) / f'source_classifier_{tag}.json'
    if res_f.is_file():
        return json.loads(res_f.read_text())
    MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
    tf_train = transforms.Compose([transforms.Resize((IMG + 32, IMG + 32)), transforms.RandomCrop(IMG), transforms.RandomHorizontalFlip(), transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    tf_eval = transforms.Compose([transforms.Resize((IMG, IMG)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    mapping = {c: k for k, c in enumerate(labels)}; cdir = WORK / 'cache256'

    class DS(Dataset):
        def __init__(self, frame, train):
            self.sha = frame.sha256.to_numpy(); self.y = frame[col].map(mapping).astype(int).to_numpy(); self.tf = tf_train if train else tf_eval
        def __len__(self):
            return len(self.sha)
        def __getitem__(self, k):
            with Image.open(cdir / f'{self.sha[k]}.jpg') as im:
                return self.tf(im.convert('RGB')), self.y[k], self.sha[k]
    nw = 4 if dev.type == 'cuda' else 0
    ltr = DataLoader(DS(tr, True), batch_size=BATCH, shuffle=True, num_workers=nw, pin_memory=dev.type == 'cuda', drop_last=False)
    lva = DataLoader(DS(va, False), batch_size=64, shuffle=False, num_workers=nw); lte = DataLoader(DS(te, False), batch_size=64, shuffle=False, num_workers=nw)

    @torch.inference_mode()
    def infer(model, loader):
        model.eval(); ys, ps, ids = [], [], []
        for x, y, sid in loader:
            with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == 'cuda'):
                lg = model(x.to(dev, non_blocking=True))
            ys.append(y.numpy()); ps.append(F.softmax(lg.float(), 1).cpu().numpy()); ids.extend(sid)
        return np.concatenate(ys), np.concatenate(ps), ids

    set_seed(SEED)
    model = torchvision.models.mobilenet_v3_large(weights='IMAGENET1K_V1' if pretrained else None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(labels)); model = model.to(dev)
    w = None
    if use_weights:
        n_c = np.array([max(1, int((tr[col] == c).sum())) for c in labels], dtype=float); w_np = len(tr) / n_c
        w = torch.tensor(np.clip(w_np / w_np.mean(), 0.2, 5.0), dtype=torch.float, device=dev)
    crit = nn.CrossEntropyLoss(weight=w, label_smoothing=SMOOTH)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    steps = max(1, math.ceil(len(ltr) / ACCUM)) * epochs
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=LR, total_steps=steps, pct_start=0.05, anneal_strategy='cos')
    scaler = torch.amp.GradScaler('cuda', enabled=dev.type == 'cuda')
    best, best_state, best_ep, bad, hist = -1, None, 0, 0, []
    for ep in range(1, epochs + 1):
        model.train(); opt.zero_grad(set_to_none=True); acum = 0.0; t0 = time.time()
        for k, (x, y, _) in enumerate(ltr):
            x = x.to(dev, non_blocking=True); y = y.to(dev, non_blocking=True)
            with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == 'cuda'):
                loss = crit(model(x), y) / ACCUM
            scaler.scale(loss).backward(); acum += loss.detach().item() * ACCUM
            if (k + 1) % ACCUM == 0 or k + 1 == len(ltr):
                scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True)
                if sch.last_epoch < steps - 1:
                    sch.step()
        yv, pv, _ = infer(model, lva)
        f1v = f1_score(yv, pv.argmax(1), average='macro', labels=list(range(len(labels))), zero_division=0)
        hist.append({'epoch': ep, 'train_loss': acum / max(1, len(ltr)), 'val_macro_f1': f1v, 'minutes': (time.time() - t0) / 60})
        log(f'  [{tag}] época {ep:02d}/{epochs} | pérdida {hist[-1]["train_loss"]:.4f} | macro-F1 de validación {f1v:.6f}')
        if f1v > best:
            best, best_ep, bad = f1v, ep, 0; best_state = {k_: v.detach().cpu().clone() for k_, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    model.load_state_dict(best_state); yt, pt, ids = infer(model, lte); pred = pt.argmax(1)
    res = {'tag': tag, 'weighted': bool(use_weights), 'labels': labels, 'n_train': len(tr), 'n_val': len(va), 'n_test': int(len(yt)), 'best_epoch': best_ep,
           'epochs_run': len(hist), 'val_macro_f1_best': float(best), 'test_accuracy': float(accuracy_score(yt, pred)),
           'test_balanced_accuracy': float(balanced_accuracy_score(yt, pred)),
           'test_macro_f1': float(f1_score(yt, pred, average='macro', labels=list(range(len(labels))), zero_division=0)),
           'test_mcc': float(matthews_corrcoef(yt, pred)), 'chance_majority': float(pd.Series(yt).value_counts(normalize=True).max())}
    try:
        res['test_roc_auc_ovr'] = float(roc_auc_score(yt, pt, multi_class='ovr', average='macro') if len(labels) > 2 else roc_auc_score(yt, pt[:, 1]))
    except Exception:
        res['test_roc_auc_ovr'] = None
    cm = pd.DataFrame(confusion_matrix(yt, pred, labels=list(range(len(labels)))), index=[f'true_{c}' for c in labels], columns=[f'pred_{c}' for c in labels])
    cm.to_csv(Path(out) / f'source_classifier_{tag}_confusion.csv')
    pd.DataFrame(hist).to_csv(Path(out) / f'source_classifier_{tag}_history.csv', index=False)
    pdf = pd.DataFrame({'sha256': ids, 'true': [labels[i] for i in yt], 'pred': [labels[i] for i in pred], 'confidence': pt.max(1)})
    pdf.to_csv(Path(out) / f'source_classifier_{tag}_predictions.csv', index=False)
    atomic_json(res, res_f)
    del model; gc.collect()
    if dev.type == 'cuda':
        torch.cuda.empty_cache()
    return res


def source_only(fr, col):
    """Association and image-free rules, same definitions as the archived notebook 07."""
    from scipy import stats
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, matthews_corrcoef
    ct = pd.crosstab(fr['class'], fr[col]); chi2, p, dof, _ = stats.chi2_contingency(ct.values); n = ct.values.sum()
    v = math.sqrt(chi2 / n / (min(ct.shape) - 1))
    pj = ct.values / n; pc = pj.sum(1, keepdims=True); ps = pj.sum(0, keepdims=True); nz = pj > 0
    mi = float((pj[nz] * np.log(pj[nz] / (pc @ ps)[nz])).sum()); H = lambda q: float(-(q[q > 0] * np.log(q[q > 0])).sum())
    nmi = mi / math.sqrt(H(pc.ravel()) * H(ps.ravel()))
    tr = fr[fr.partition == 'train']; te = fr[fr.partition == 'test']; classes = sorted(fr['class'].unique()); c2i = {c: k for k, c in enumerate(classes)}
    cond = tr.groupby([col, 'class']).size().unstack(fill_value=0).reindex(columns=classes, fill_value=0); cond = (cond.T / cond.sum(1)).T
    det = cond.max(1); single = det[det >= 0.999].index.tolist(); y = te['class'].map(c2i).to_numpy(); src = te[col].to_numpy()
    pm = pd.Series(src).map(cond.idxmax(1)).map(c2i).to_numpy()
    rng = np.random.default_rng(SEED); cdf = np.cumsum(cond.values, axis=1); si = pd.Series(src).map({s: k for k, s in enumerate(cond.index)}).to_numpy()
    acc, f1s, mcc = [], [], []
    for _ in range(200):
        u = rng.random(len(y)); pr = np.array([int(np.searchsorted(cdf[si[k]], u[k])) for k in range(len(y))])
        pr = np.minimum(pr, len(classes) - 1)
        acc.append(accuracy_score(y, pr)); f1s.append(f1_score(y, pr, average='macro', labels=list(range(len(classes))), zero_division=0)); mcc.append(matthews_corrcoef(y, pr))
    return {'label_set': col, 'sources': int(ct.shape[1]), 'chi2': float(chi2), 'dof': int(dof), 'cramers_v': v, 'nmi': nmi,
            'single_source_classes': int((ct.gt(0).sum(1) == 1).sum()), 'single_class_sources': len(single),
            'test_images_class_determined_by_source': int(te[col].isin(single).sum()), 'test_images': int(len(te)),
            'majority_rule_accuracy': float(accuracy_score(y, pm)), 'majority_rule_balanced_accuracy': float(balanced_accuracy_score(y, pm)),
            'majority_rule_macro_f1': float(f1_score(y, pm, average='macro', labels=list(range(len(classes))), zero_division=0)),
            'majority_rule_mcc': float(matthews_corrcoef(y, pm)), 'stochastic_accuracy': float(np.mean(acc)), 'stochastic_macro_f1': float(np.mean(f1s)),
            'stochastic_mcc': float(np.mean(mcc)), 'stochastic_mcc_sd': float(np.std(mcc, ddof=1))}


def stage_sources(out, fr, pretrained=True):
    out = Path(out)
    atomic_csv(pd.DataFrame([source_only(fr, 'component'), source_only(fr, 'source')]), out / 'source_only_controls_components_vs_primary_sources.csv')
    pd.crosstab(fr['class'], fr.source).to_csv(out / 'class_by_primary_source.csv')
    part = {p: fr[fr.partition == p] for p in ['train', 'validation', 'test']}
    res = []
    order = ['Adege', 'CCMT', 'PlantVillage', 'Tanzania']
    for wts in [False, True]:
        res.append(train_eval(part['train'], part['validation'], part['test'], 'source', order, f'primary4_{"weighted" if wts else "unweighted"}', out, wts, pretrained))
    h = {p: d[d['class'] == 'healthy'] for p, d in part.items()}
    labs = [s for s in order if s in set(h['train'].source)]
    res.append(train_eval(h['train'], h['validation'], h['test'], 'source', labs, 'primary_within_healthy_unweighted', out, False, pretrained))
    df = pd.DataFrame(res); df['labels'] = df['labels'].map('|'.join); atomic_csv(df, out / 'source_classifier_primary_sources.csv')
    R.mark(out, 'sources', {'recipe': 'archived notebook 07: MobileNetV3-Large IMAGENET1K_V1, seed 17, <=12 epochs, patience 3'})
    log('Clasificador de fuente (fuentes primarias):\n' + df[['tag', 'n_test', 'best_epoch', 'test_accuracy', 'test_macro_f1', 'test_mcc', 'test_roc_auc_ovr']].to_string(index=False))
    return df


def export(out):
    out = Path(out); z = out.parent / 'MAIZ_14D_Resultados.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for p in sorted(out.rglob('*')):
            if p.is_file() and p.suffix != '.npz':
                f.write(p, str(p.relative_to(out)))
    if Path('/content').is_dir():
        shutil.copy(z, '/content/MAIZ_14D_Resultados.zip')
    log('ZIP de resultados:', z); return z


def run_all(root):
    root = Path(root); out = root / OUT_REL; out_a = root / R.OUT_REL; out.mkdir(parents=True, exist_ok=True); WORK.mkdir(parents=True, exist_ok=True); R.WORK.mkdir(parents=True, exist_ok=True)
    try:
        fr = stage_internal(root, out)
        if not R.done(out, 'sources'):
            stage_sources(out, fr)
        if not R.done(out, 'dino_cross'):
            meta, arrays = stage_external(root, out_a)
            stage_dino(root, out, fr, meta, arrays, out_a)
        atomic_json({'status': 'COMPLETE', 'completed_utc': utc(), 'version': VERSION + '+14d'}, out / 'MAIZ14D_STATUS.json')
        log('MAIZ_14D COMPLETO')
    except Exception as e:
        atomic_json({'status': 'ERROR', 'error': repr(e), 'traceback': traceback.format_exc(), 'utc': utc()}, out / 'MAIZ14D_last_error.json')
        raise
    finally:
        export(out)
