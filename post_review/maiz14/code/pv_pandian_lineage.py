"""Pandian2019 rust lineage against the public PlantVillage maize rust folder.

Inputs: pandian2019 evaluation manifest (stores the historical 64-bit imagehash.phash of
every retained Pandian2019 image) and a checkout of spMohanty/PlantVillage-Dataset at
commit 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a. For each PlantVillage rust image the
pHash of its eight dihedral (D4) variants is computed; each Pandian2019 image is assigned
to the PlantVillage image and transform with the smallest Hamming distance.

Outputs: per-image lineage CSV, per-parent family CSV and a JSON summary.
"""
import argparse, glob, hashlib, json, os
import numpy as np, pandas as pd, imagehash
from PIL import Image

TRANSFORMS = ['identity', 'flip_lr', 'rot90', 'rot90_flip_lr', 'rot180', 'rot180_flip_lr', 'rot270', 'rot270_flip_lr']


def bits(h):
    return np.array(h.hash.flatten(), dtype=np.uint8)


def hexbits(x):
    return np.array([int(b) for b in bin(int(x, 16))[2:].zfill(64)], dtype=np.uint8)


def main(manifest, pv_root, out, threshold=5):
    pan = pd.read_csv(manifest, dtype=str, keep_default_na=False)
    P = np.stack([hexbits(h) for h in pan.phash])
    files = sorted(glob.glob(os.path.join(pv_root, 'raw', 'color', 'Corn_(maize)___Common_rust_', '*')))
    H, S, names = [], [], []
    for f in files:
        b = open(f, 'rb').read(); S.append(hashlib.sha256(b).hexdigest()); names.append(os.path.basename(f))
        im = Image.open(f).convert('RGB'); vs = []
        for k in range(4):
            r = im.rotate(90 * k, expand=True); vs += [r, r.transpose(Image.FLIP_LEFT_RIGHT)]
        H.append(np.stack([bits(imagehash.phash(v)) for v in vs]))
    H = np.stack(H)
    d = (H[:, :, None, :] != P[None, None]).sum(3)            # parent, transform, pandian
    flat = d.reshape(-1, len(pan))
    arg = flat.argmin(0); parent = arg // 8; transform = arg % 8; dist = flat.min(0)
    second = np.sort(d.min(1), 0)[1]                           # distance to the second-closest parent
    lin = pd.DataFrame({'pandian_sample_id': pan.sample_id, 'pandian_sha256': pan.sha256,
                        'pv_parent_file': [names[i] for i in parent], 'pv_parent_sha256': [S[i] for i in parent],
                        'transform': [TRANSFORMS[t] for t in transform], 'hamming': dist,
                        'second_parent_hamming': second, 'exact_sha256_copy': pan.sha256.isin(set(S)).to_numpy(),
                        'matched': dist <= threshold})
    lin['family_id'] = 'PVRUST_' + pd.Series(parent).astype(str).str.zfill(4)
    lin.loc[~lin.matched, 'family_id'] = 'UNMATCHED_' + lin.loc[~lin.matched, 'pandian_sample_id'].str[:12]
    os.makedirs(out, exist_ok=True)
    lin.to_csv(os.path.join(out, 'pandian2019_pv_lineage.csv'), index=False)
    fam = lin[lin.matched].groupby(['family_id', 'pv_parent_file']).agg(
        children=('pandian_sample_id', 'size'), transforms=('transform', lambda x: '+'.join(sorted(x)))).reset_index()
    fam.to_csv(os.path.join(out, 'pandian2019_pv_families.csv'), index=False)
    pv_children = np.bincount(parent[dist <= threshold], minlength=len(files))
    summary = {'pandian_images': int(len(pan)), 'pv_rust_images': int(len(files)), 'threshold_hamming': threshold,
               'pandian_matched': int(lin.matched.sum()), 'pandian_unmatched': int((~lin.matched).sum()),
               'pandian_exact_sha256_copies': int(lin.exact_sha256_copy.sum()),
               'matched_by_transform': lin[lin.matched]['transform'].value_counts().to_dict(),
               'hamming_distribution_matched': lin[lin.matched].hamming.value_counts().sort_index().astype(int).to_dict(),
               'second_parent_hamming_min': int(second.min()),
               'distinct_pv_parents': int((pv_children > 0).sum()),
               'pv_parents_by_children': {int(k): int(v) for k, v in pd.Series(pv_children[pv_children > 0]).value_counts().sort_index().items()},
               'pv_rust_without_pandian_child': int((pv_children == 0).sum()),
               'identity_orientation_matches_at_threshold': int((d[:, 0].min(0) <= threshold).sum()),
               'pv_commit': '7f7ecc7e1eaca78107e3affe7cb5abd9427e139a', 'hash': 'imagehash.phash 64-bit, RGB'}
    json.dump(summary, open(os.path.join(out, 'pandian2019_pv_lineage_summary.json'), 'w'), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('--manifest', required=True); a.add_argument('--pv-root', required=True)
    a.add_argument('--out', required=True); a.add_argument('--threshold', type=int, default=5)
    x = a.parse_args(); main(x.manifest, x.pv_root, x.out, x.threshold)
