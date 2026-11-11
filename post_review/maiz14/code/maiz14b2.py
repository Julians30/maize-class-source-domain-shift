"""MAIZ_14B2: complete PlantVillage-derived healthy ablation (byte copies and mirrored copies).

Based on MAIZ_14B: healthy-component ablation (Reviewer 2, major comment 10; Academic Editor 8).

Retrains with the hash-verified original E2 source and the unchanged post-review patch
(post_review_gpu.patched_training). The only change: internal healthy images whose standard
64-bit pHash lies within 5 bits of a public PlantVillage healthy image (commit 7f7ecc7) are
removed from training and validation. Checkpoint selection stays on (reduced) validation
macro-F1. Afterwards the ablated checkpoint and the original same-seed public checkpoint are
evaluated with identical code on internal test, Pandian2019, PlantVillage and TOM2024.
"""
from pathlib import Path
import hashlib, io, json, os, subprocess, sys, tarfile
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import post_review_gpu as prg

REVISION = '2026-11-10-maiz14b2-plantvillage-healthy-full-ablation'
PLAN_NAME = 'experiment_plan_healthy_ablation_full_20261110.json'
PV_COMMIT = '7f7ecc7e1eaca78107e3affe7cb5abd9427e139a'
PV_REPO = 'https://github.com/spMohanty/PlantVillage-Dataset'
ABL_DIR = 'MAIZ14B2_healthy_ablation_full'
ANCHOR = "globals().update(load_frozen_training_metadata(_RUNTIME_PATHS['artifacts']))\n"
CLASSES = ['fall_armyworm', 'grasshopper', 'healthy', 'leaf_beetle', 'leaf_blight', 'leaf_spot',
           'lethal_necrosis', 'rust', 'streak_virus']
C2I = {c: i for i, c in enumerate(CLASSES)}
# (model, seed, lr, approximate L4 hours); EfficientNet-B0 is the validation-selected architecture.
JOBS = [('efficientnet_b0', 17, 0.0003, 5.8), ('efficientnet_b0', 42, 0.0003, 5.8), ('efficientnet_b0', 73, 0.0003, 5.8)]
ZENODO = 'https://zenodo.org/api/records/24064539/files/{}/content'


def job_id(i):
    m, s, lr, _ = JOBS[i]
    return f'healthy_ablation_full_{m}_seed{s}_lr{lr:.0e}'


def out_dir(root):
    return Path(root) / 'REVISION_POST_REVIEW_20261029'


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def phash_bits(im):
    import imagehash
    return np.array(imagehash.phash(im.convert('RGB')).hash.flatten(), dtype=np.uint8)


# --------------------------------------------------------------------------- identification
def pv_healthy(work):
    dest = Path(work) / 'PlantVillage-Dataset'
    folder = dest / 'raw' / 'color' / 'Corn_(maize)___healthy'
    if not folder.is_dir():
        subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout', '--depth', '1', PV_REPO, str(dest)], check=True)
        subprocess.run(['git', '-C', str(dest), 'fetch', '--depth', '1', 'origin', PV_COMMIT], check=True)
        subprocess.run(['git', '-C', str(dest), 'sparse-checkout', 'set', '--no-cone', 'raw/color/Corn_(maize)___healthy'], check=True)
        subprocess.run(['git', '-C', str(dest), 'checkout', PV_COMMIT], check=True)
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'})


def identify(root, code, work='/content/maiz14b_work'):
    """Returns the SHA-256 list of train/validation healthy images linked to PlantVillage healthy."""
    out = out_dir(root) / ABL_DIR; out.mkdir(parents=True, exist_ok=True)
    f = out / 'ablation_identification.csv'
    if f.is_file() and (out / 'ablation_sha256.json').is_file():
        return json.loads((out / 'ablation_sha256.json').read_text())
    from training_data_preflight import restore_cache, load_frozen_training_metadata
    runtime_path, cache = restore_cache(root)
    rt = json.loads(Path(runtime_path).read_text())
    meta = load_frozen_training_metadata(rt['artifacts'])
    pv = pv_healthy(work)
    def d4(p):
        im = Image.open(p).convert('RGB'); out = []
        for k in range(4):
            r = im.rotate(90 * k, expand=True); out += [phash_bits(r), phash_bits(r.transpose(Image.FLIP_LEFT_RIGHT))]
        return out
    P = np.stack([v for p in pv for v in d4(p)]); PV_NAMES = [p.name for p in pv for _ in range(8)]
    pv_sha = {sha_bytes(p.read_bytes()) for p in pv}
    rows = []
    for role in ['train_df', 'val_df']:
        d = meta[role]; d = d[d['class'] == 'healthy']
        for r in d.itertuples():
            p = rt['image_paths'][str(r.path)]
            with Image.open(p) as im:
                b = phash_bits(im)
            dist = (P != b[None]).sum(1)
            rows.append({'role': role[:-3], 'sha256': str(r.sha256).lower(), 'source_operational': r.source_operational,
                         'path': r.path, 'nearest_pv_healthy': PV_NAMES[int(dist.argmin())], 'hamming': int(dist.min())})
    te = pd.read_csv(Path(code) / 'internal_test.csv', dtype=str, keep_default_na=False)
    te = te[te['class'] == 'healthy']
    src = meta['internal_test_df'].set_index(meta['internal_test_df'].sha256.astype(str).str.lower()).source_operational
    for r in te.itertuples():
        b = np.array([int(c) for c in bin(int(r.phash, 16))[2:].zfill(64)], dtype=np.uint8)
        dist = (P != b[None]).sum(1)
        rows.append({'role': 'test', 'sha256': r.sha256.lower(), 'source_operational': src.get(r.sha256.lower(), ''),
                     'path': r.original_path, 'nearest_pv_healthy': PV_NAMES[int(dist.argmin())], 'hamming': int(dist.min())})
    df = pd.DataFrame(rows); df['linked'] = df.hamming <= 5; df['exact_sha256_in_pv'] = df.sha256.isin(pv_sha)
    df.to_csv(f, index=False)
    s = df[df.linked]
    summary = {'pv_healthy_images': len(pv), 'linked_by_role': s.role.value_counts().astype(int).to_dict(),
               'linked_by_source': s.source_operational.value_counts().astype(int).to_dict(),
               'healthy_by_role': df.role.value_counts().astype(int).to_dict(),
               'exact_sha256_by_role': df[df.exact_sha256_in_pv].role.value_counts().astype(int).to_dict(),
               'archived_reference': {'train': 496, 'val': 107, 'test': 106, 'total': 709},
               'rule': 'D4 (eight dihedral variants) 64-bit imagehash.phash, Hamming <= 5, PlantVillage commit ' + PV_COMMIT}
    summary['matches_archived_reference'] = summary['linked_by_role'] == {'train': 496, 'val': 107, 'test': 106}
    (out / 'ablation_identification_summary.json').write_text(json.dumps(summary, indent=2))
    print('Identificación:', json.dumps(summary, ensure_ascii=False), flush=True)
    sha = sorted(s[s.role.isin(['train', 'val'])].sha256)
    (out / 'ablation_sha256.json').write_text(json.dumps(sha))
    (out / 'ablation_test_linked_sha256.json').write_text(json.dumps(sorted(s[s.role == 'test'].sha256)))
    return sha


# --------------------------------------------------------------------------- training
def plan():
    return {'stage': 'post-review healthy-component ablation, after external outcomes were known',
            'revision': REVISION, 'source_sha256': prg.SOURCE_SHA,
            'jobs': [{'job_id': job_id(i), 'model_key': j[0], 'seed': j[1], 'learning_rate': j[2]} for i, j in enumerate(JOBS)],
            'change': 'remove every PlantVillage-derived healthy image (byte copies and dihedral variants, D4-pHash<=5) from train and validation; nothing else',
            'unchanged_recipe': prg.experiment_plan()['unchanged_recipe'],
            'comparison': 'same-seed original public checkpoint evaluated with identical code',
            'evaluation_policy': 'Training script ends at validation; evaluation runs afterwards on the frozen checkpoint.'}


def build_source(source, i, out):
    m, s, lr, _ = JOBS[i]
    text = prg.patched_training(source, m, s, lr, out, job_id(i))
    if text.count(ANCHOR) != 1:
        raise ValueError('Punto de inserción no encontrado en la fuente parcheada')
    inject = ANCHOR + (
        "_ABLATION_SHA = set(json.loads(Path(os.environ['MAIZE_ABLATION_SHA']).read_text()))\n"
        "_before = (len(train_df), len(val_df))\n"
        "train_df = train_df[~train_df['sha256'].astype(str).str.lower().isin(_ABLATION_SHA)].copy()\n"
        "val_df = val_df[~val_df['sha256'].astype(str).str.lower().isin(_ABLATION_SHA)].copy()\n"
        "assert (_before[0] - len(train_df)) + (_before[1] - len(val_df)) == len(_ABLATION_SHA)\n"
        "assert set(train_df['class']) == set(val_df['class']) and len(set(train_df['class'])) == 9\n"
        "print('ABLACIÓN healthy: train', _before[0], '->', len(train_df), '| val', _before[1], '->', len(val_df), flush=True)\n")
    text = text.replace(ANCHOR, inject)
    reg_old = 'REGISTRY_PATH = Path(' + repr(str(Path(out) / 'new_runs_only.csv')) + ')'
    if text.count(reg_old) != 1:
        raise ValueError('Registro de corridas no encontrado')
    text = text.replace(reg_old, 'REGISTRY_PATH = Path(' + repr(str(Path(out) / ABL_DIR / 'healthy_ablation_runs.csv')) + ')')
    compile(text, 'maiz14b_training', 'exec')
    return text


def completed(out, i):
    jid = job_id(i); m, s, lr, _ = JOBS[i]
    receipt = Path(out) / 'execution_sources' / jid / 'TRAINING_VALIDATION_COMPLETE.json'
    if not receipt.is_file():
        return False
    r = json.loads(receipt.read_text()); state = json.loads((Path(out) / 'checkpoints' / jid / 'run_manifest.json').read_text())
    cfg = state['run_config']
    if not (cfg['model_key'] == m and cfg['seed'] == s and cfg['learning_rate'] == lr and state['evaluation_opened'] is False
            and prg.digest(Path(out) / 'checkpoints' / jid / 'checkpoint_best.pt') == r['checkpoint_sha256']):
        raise ValueError('Corrida marcada como completa pero inconsistente: ' + jid)
    print('Ya completa y verificada:', jid, flush=True)
    return True


def train(root, source_path, i, sha):
    root = Path(root).resolve(); source_path = Path(source_path).resolve()
    if prg.digest(source_path) != prg.SOURCE_SHA:
        raise ValueError('La fuente original no coincide con su huella SHA-256')
    out = out_dir(root); plan_path = out / PLAN_NAME; blob = json.dumps(plan(), sort_keys=True, indent=2)
    if plan_path.exists() and plan_path.read_text() != blob:
        raise RuntimeError('Ya existe un plan MAIZ_14B distinto; no se sobrescribe')
    if not plan_path.exists():
        plan_path.write_text(blob)
    if completed(out, i):
        return
    jid = job_id(i); m, s, lr, _ = JOBS[i]
    job_dir = out / 'execution_sources' / jid; job_dir.mkdir(parents=True, exist_ok=True)
    sha_file = out / ABL_DIR / 'ablation_sha256.json'
    if json.loads(sha_file.read_text()) != sha:
        raise ValueError('Lista de ablación distinta')
    code = build_source(source_path.read_text(), i, out)
    script = job_dir / 'training_derived_from_original.py'; prg.versioned_text(script, code)
    run_file = job_dir / 'execute_training.py'; prg.versioned_text(run_file, prg.executable_training(code))
    info = prg.preflight_versions(job_dir / 'environment_preflight.json')
    from training_data_preflight import restore_cache
    runtime_path, cache = restore_cache(root)
    prov = {'job_id': jid, 'model_key': m, 'seed': s, 'learning_rate': lr, 'removed_images': len(sha),
            'ablation_list_sha256': prg.digest(sha_file), 'original_source_sha256': prg.SOURCE_SHA,
            'derived_source_sha256': prg.digest(script), 'executed_source_sha256': prg.digest(run_file),
            'plan_sha256': prg.digest(plan_path), 'environment': info, 'infrastructure_revision': REVISION}
    prg.versioned_text(job_dir / 'post_review_provenance.json', json.dumps(prov, indent=2))
    env = {**os.environ, 'MAIZE_PROJECT_ROOT': str(root), 'PYTHONUNBUFFERED': '1', 'PYTHONHASHSEED': str(s),
           'PYTHONPATH': str(Path(prg.__file__).resolve().parent) + os.pathsep + os.environ.get('PYTHONPATH', ''),
           'MAIZE_RUNTIME_PATHS': str(runtime_path), 'MAIZE_CACHE_ROOT': str(cache), 'MAIZE_ABLATION_SHA': str(sha_file)}
    print(f'Inicio/reanudación: {jid}', flush=True)
    log = job_dir / 'training_stdout.log'
    with log.open('a') as stream:
        stream.write('\n--- ' + REVISION + ' ---\n'); stream.flush()
        child = subprocess.Popen([sys.executable, '-u', str(run_file)], env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in child.stdout:
                print(line, end='', flush=True); stream.write(line); stream.flush()
            rc = child.wait()
        except BaseException:
            child.terminate()
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill(); child.wait()
            raise
    if rc:
        raise RuntimeError(f'La corrida terminó con código {rc}; log: {log}. Los checkpoints quedan para reanudar.')
    state = json.loads((out / 'checkpoints' / jid / 'run_manifest.json').read_text())
    (job_dir / 'TRAINING_VALIDATION_COMPLETE.json').write_text(json.dumps({
        'job_id': jid, 'best_epoch': state['best_epoch'], 'validation_macro_f1_reduced_validation': state['best_val_macro_f1'],
        'checkpoint_sha256': state['checkpoint_best_sha256'], 'test_external_evaluated': False}, indent=2))
    print('Corrida congelada por validación:', jid, flush=True)


# --------------------------------------------------------------------------- evaluation
def build_model(key):
    import torch.nn as nn
    import torchvision.models as tv
    if key == 'resnet50':
        m = tv.resnet50(weights=None); m.fc = nn.Linear(m.fc.in_features, 9)
    elif key == 'efficientnet_b0':
        m = tv.efficientnet_b0(weights=None); m.classifier[1] = nn.Linear(m.classifier[1].in_features, 9)
    else:
        raise ValueError(key)
    return m


def load_model(key, path):
    import torch
    obj = torch.load(path, map_location='cpu', weights_only=False)
    sd = obj['model_state_dict'] if isinstance(obj, dict) and 'model_state_dict' in obj else obj
    if isinstance(obj, dict) and obj.get('class_to_idx') not in (None, C2I):
        raise ValueError('Orden de clases distinto')
    m = build_model(key); m.load_state_dict({k[7:] if k.startswith('module.') else k: v for k, v in sd.items()}, strict=True)
    return m.to('cuda').eval()


def domain_images(root, work):
    """Prepared historical caches (same recipe as MAIZ_04B) plus PlantVillage rust/healthy from the public commit."""
    base = out_dir(root) / 'evaluation_5seeds' / 'prepared'; res = {}
    for d in ['internal_test', 'pandian2019', 'plantvillage', 'tom2024_primary']:
        man = pd.read_csv(base / d / 'manifest.csv', dtype=str, keep_default_na=False)
        dest = Path(work) / 'prepared' / d; dest.mkdir(parents=True, exist_ok=True)
        expected = dict(zip(man.cache_name, man.cache_sha256))
        if not all((dest / n).is_file() for n in expected):
            with tarfile.open(base / d / 'images.tar') as t:
                for m in t.getmembers():
                    if m.name not in expected or Path(m.name).name != m.name:
                        raise ValueError('Miembro TAR inesperado')
                    (dest / m.name).write_bytes(t.extractfile(m).read())
        for n, h in expected.items():
            if hashlib.sha256((dest / n).read_bytes()).hexdigest() != h:
                raise ValueError('Caché alterada: ' + d)
        res[d] = (man.assign(local=[str(dest / n) for n in man.cache_name]), 'squash' if d in {'plantvillage', 'tom2024_primary'} else 'crop')
    pv = Path(work) / 'PlantVillage-Dataset'
    if not (pv / 'raw/color/Corn_(maize)___Common_rust_').is_dir():
        subprocess.run(['git', '-C', str(pv), 'sparse-checkout', 'set', '--no-cone', 'raw/color/Corn_*'], check=True)
        subprocess.run(['git', '-C', str(pv), 'checkout', PV_COMMIT], check=True)
    for folder, cls, name in [('Corn_(maize)___Common_rust_', 'rust', 'pv_rust'), ('Corn_(maize)___healthy', 'healthy', 'pv_healthy')]:
        files = sorted((pv / 'raw/color' / folder).iterdir())
        res[name] = (pd.DataFrame({'sample_id': [p.name for p in files], 'class': cls, 'local': [str(p) for p in files]}), 'pvraw')
    return res


def predict(model, frame, mode):
    import torch
    from torchvision import transforms as T
    norm = [T.ToTensor(), T.Normalize([.485, .456, .406], [.229, .224, .225])]
    sq = T.Compose([T.Resize((224, 224), interpolation=T.InterpolationMode.BILINEAR)] + norm)
    cr = T.Compose([T.Resize(256, interpolation=T.InterpolationMode.BICUBIC), T.CenterCrop(224)] + norm)
    out = []
    for i in range(0, len(frame), 64):
        xs = []
        for p in frame.local.iloc[i:i + 64]:
            with Image.open(p) as im:
                if mode == 'crop':
                    xs.append(cr(ImageOps.exif_transpose(im).convert('RGB')))
                elif mode == 'squash':
                    xs.append(sq(im.convert('RGB')))
                else:   # PlantVillage public file -> historical cache recipe -> squash
                    im = im.convert('RGB'); w, h = im.size
                    if min(w, h) > 256:
                        s = 256 / min(w, h); im = im.resize((round(w * s), round(h * s)), Image.Resampling.BILINEAR)
                    b = io.BytesIO(); im.save(b, format='JPEG', quality=95); b.seek(0)
                    xs.append(sq(Image.open(b).convert('RGB')))
        with torch.inference_mode(), torch.autocast('cuda', dtype=torch.float16):
            out.append(torch.softmax(model(torch.stack(xs).cuda()).float(), 1).cpu().numpy())
    return np.concatenate(out)


def f1(y, p, labels):
    r = []
    for c in labels:
        tp = ((y == c) & (p == c)).sum(); fp = ((y != c) & (p == c)).sum(); fn = ((y == c) & (p != c)).sum()
        r.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
    return float(np.mean(r))


def evaluate(root, code, work='/content/maiz14b_work'):
    import requests
    out = out_dir(root); ab = out / ABL_DIR; ab.mkdir(parents=True, exist_ok=True)
    data = domain_images(root, work)
    linked_test = set(json.loads((ab / 'ablation_test_linked_sha256.json').read_text()))
    zen = pd.read_csv(Path(code) / 'zenodo_files.csv').set_index('filename')
    expm = pd.read_csv(Path(code) / 'expected_metrics.csv')
    rows = []
    for i in range(len(JOBS)):
        m, s, lr, _ = JOBS[i]; jid = job_id(i)
        ck_new = out / 'checkpoints' / jid / 'checkpoint_best.pt'
        if not (out / 'execution_sources' / jid / 'TRAINING_VALIDATION_COMPLETE.json').is_file():
            print('Sin entrenar todavía; se omite la evaluación de', jid, flush=True); continue
        name = f'{m}_seed{s}.pt'; ck_old = Path(work) / name
        if not (ck_old.is_file() and hashlib.sha256(ck_old.read_bytes()).hexdigest() == zen.loc[name, 'sha256']):
            with requests.get(ZENODO.format(name), stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(ck_old, 'wb') as f:
                    for b in r.iter_content(16 * 1024 ** 2):
                        f.write(b)
            if hashlib.sha256(ck_old.read_bytes()).hexdigest() != zen.loc[name, 'sha256']:
                raise ValueError('SHA distinto: ' + name)
        for variant, path in [('original_public_checkpoint', ck_old), ('healthy_ablation', ck_new)]:
            model = load_model(m, path); P = {}
            for d, (fr, mode) in data.items():
                P[d] = predict(model, fr, mode)
            np.savez_compressed(ab / f'probs_{m}_seed{s}_{variant}.npz', **P)
            del model
            y = {d: data[d][0]['class'].map(C2I).to_numpy() for d in data}; a = {d: P[d].argmax(1) for d in P}
            it = data['internal_test'][0]; keep = ~it.sha256.str.lower().isin(linked_test).to_numpy()
            r = {'model_key': m, 'seed': s, 'variant': variant, 'checkpoint_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                 'internal_macro_f1_9': f1(y['internal_test'], a['internal_test'], range(9)),
                 'internal_macro_f1_9_without_linked_test': f1(y['internal_test'][keep], a['internal_test'][keep], range(9)),
                 'internal_healthy_f1': f1(y['internal_test'], a['internal_test'], [C2I['healthy']]),
                 'internal_healthy_recall_linked_test': float((a['internal_test'][~keep] == C2I['healthy']).mean()) if (~keep).any() else np.nan,
                 'pandian_rust_recall': float((a['pandian2019'] == C2I['rust']).mean()),
                 'pandian_pred_healthy_fraction': float((a['pandian2019'] == C2I['healthy']).mean()),
                 'pv_macro_f1_blight_spot_open': f1(y['plantvillage'], a['plantvillage'], [C2I['leaf_blight'], C2I['leaf_spot']]),
                 'pv_rust_recall': float((a['pv_rust'] == C2I['rust']).mean()),
                 'pv_rust_pred_healthy_fraction': float((a['pv_rust'] == C2I['healthy']).mean()),
                 'pv_healthy_recall_all_1162': float((a['pv_healthy'] == C2I['healthy']).mean()),
                 'tom_macro_f1_3_open': f1(y['tom2024_primary'], a['tom2024_primary'], [C2I['fall_armyworm'], C2I['healthy'], C2I['rust']]),
                 'tom_healthy_recall': float((a['tom2024_primary'][y['tom2024_primary'] == C2I['healthy']] == C2I['healthy']).mean()),
                 'tom_rust_recall': float((a['tom2024_primary'][y['tom2024_primary'] == C2I['rust']] == C2I['rust']).mean())}
            rows.append(r); print(variant, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}), flush=True)
    res = pd.DataFrame(rows); res.to_csv(ab / 'healthy_ablation_paired_evaluation.csv', index=False)
    # seed-to-seed range of the original five seeds, for scale
    ref = expm[expm.model_key.isin([j[0] for j in JOBS])].groupby(['dataset', 'model_key']).primary_value.agg(['mean', 'std', 'min', 'max']).reset_index()
    ref.to_csv(ab / 'original_five_seed_range_for_scale.csv', index=False)
    return res


def export(root):
    import zipfile
    out = out_dir(root); z = out / 'MAIZ_14B2_Ablacion_Completa_Registros.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        for p in sorted((out / ABL_DIR).rglob('*')):
            if p.is_file() and p.stat().st_size < 100 * 1024 ** 2:
                f.write(p, str(p.relative_to(out)))
        for i in range(len(JOBS)):
            for sub in ['execution_sources', 'checkpoints']:
                d = out / sub / job_id(i)
                if d.is_dir():
                    for p in sorted(d.rglob('*')):
                        if p.is_file() and p.suffix in {'.json', '.csv', '.log', '.py'} and p.stat().st_size < 20 * 1024 ** 2:
                            f.write(p, str(p.relative_to(out)))
        if (out / PLAN_NAME).is_file():
            f.write(out / PLAN_NAME, PLAN_NAME)
    return z
