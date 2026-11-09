#!/usr/bin/env python3
"""Reconcile archived image identities; performs no training or inference.

Usage: python scripts/verify_source_traceability.py --archive /path/to/public.zip
       --output-dir /path/to/evidence [--plantvillage-root /path/to/PV/raw/color]
Without --archive, downloads the exact published scientific ZIP from Zenodo.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, io, json, re, urllib.request, zipfile
from pathlib import Path

DOI = '10.5281/zenodo.24064539'
ARCHIVE_URL = 'https://zenodo.org/api/records/24064539/files/MAIZ_ZENODO_DATOS_Y_CODIGO_CANDIDATO.zip/content'
ARCHIVE_SHA256 = '4f4efbc585728442982f5784f07fd7b817383d89757393faed868443a652ca91'
SOURCES = {'CIMMYT_MLND': (3229, 2260, 485, 484),
           'Kaggle_HEALTHY_up': (1667, 1167, 250, 250),
           'Kaggle_Healthy_paren': (709, 496, 107, 106)}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def reconcile(archive, output_dir, plantvillage_root=None):
    raw = archive.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == ARCHIVE_SHA256, 'Public ZIP SHA-256 differs')
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        def read_csv(name):
            return list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig'))))
        master_name = 'core_v7/manifests/manifest_master_clean_snapshot_v1_pre_split.csv'
        split_name = 'core_v7/manifests/e2a_adege_to_pandian_manifest_v1.csv'
        crosswalk_name = 'core_v7/recovery/master_13413_exact_extraction_membership.csv'
        master, split, crosswalk = [read_csv(n) for n in [master_name, split_name, crosswalk_name]]
        require(len(master) == len(split) == len(crosswalk) == 13413, 'Master row counts differ')
        require(len({r['sha256'] for r in master}) == 13413, 'Master SHA-256 is not unique')
        m = {r['sha256']: r for r in master}
        s = {r['sha256']: r for r in split}
        c = {r['sha256']: r for r in crosswalk}
        require(len(s) == len(c) == 13413 and m.keys() == s.keys() == c.keys(), 'Identity sets differ')
        fields = ['filename', 'source_operational', 'class', 'phash_standard', 'global_group_id']
        for h, row in m.items():
            require(all(row[k] == s[h][k] == c[h][k] for k in fields), 'Metadata mismatch for ' + h)
        internal = [r for r in split if r['evaluation_role'] in ['train', 'val', 'test']]
        require(collections.Counter(r['evaluation_role'] for r in internal) ==
                {'train': 8043, 'val': 1729, 'test': 1719}, 'Internal split totals differ')
        summary, ledger = [], []
        for source, expected in SOURCES.items():
            selected = [r for r in split if r['source_operational'] == source]
            counts = collections.Counter(r['evaluation_role'] for r in selected)
            actual = (len(selected), counts['train'], counts['val'], counts['test'])
            require(actual == expected, 'Source split counts differ: ' + source)
            require(all(c[r['sha256']]['exact_aggregate_match'].lower() == 'true' for r in selected),
                    'Archived extraction correspondence missing: ' + source)
            for row in selected:
                require(re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None, 'Invalid SHA-256')
                require(re.fullmatch('[0-9a-fA-F]{16}', row['phash_standard']) is not None, 'Invalid pHash')
                require(all(row[k] for k in fields), 'Required identity metadata missing')
                ledger.append({k: row[k] for k in ['source_operational', 'class', 'filename', 'sha256',
                                                 'phash_standard', 'group_id', 'global_group_id', 'evaluation_role']}
                              | {'archived_extraction_exact_match': True})
            summary.append({'source_operational': source, 'retained': len(selected),
                            'train': counts['train'], 'validation': counts['val'], 'test': counts['test'],
                            'complete_identity_records': len(selected), 'archived_extraction_exact_matches': len(selected)})
        ledger.sort(key=lambda r: (r['source_operational'], r['evaluation_role'], r['sha256']))
        write_csv(output_dir/'traceability_5605_summary.csv', summary)
        write_csv(output_dir/'traceability_5605_ledger.csv', ledger)
        pv_name = 'additional_checks_v9/inputs/PlantVillage_source_SHA256.csv'
        pv_rows = read_csv(pv_name)
        pv_sources = {r['path'].split('PlantVillage_maize/', 1)[1]: r['sha256_recomputed'] for r in pv_rows}
        require(len(pv_sources) == 3852, 'PlantVillage source count differs')
        pv_eval = read_csv('core_v7/manifests/plantvillage.csv')
        healthy = read_csv('additional_checks_v9/360_HEALTHY_VINCULOS_SHA256.csv')
        require(len(pv_eval) == 1498 and len(healthy) == 360, 'PlantVillage subset counts differ')
        require(all(r['sha256'] in set(pv_sources.values()) for r in healthy), 'Healthy source link missing')
        require(collections.Counter(r['evaluation_role'] for r in healthy) ==
                {'train': 261, 'val': 50, 'test': 49}, 'Healthy split counts differ')
        pv_ledger = []
        for row in pv_eval:
            relative = row['original_path'].split('PlantVillage_maize/', 1)[1]
            require(relative in pv_sources, 'Evaluation/source path correspondence missing')
            pv_ledger.append({'sample_id': row['sample_id'], 'class': row['class'],
                              'global_group_id': row['global_group_id'], 'public_relative_path': 'raw/color/'+relative,
                              'sha256': pv_sources[relative]})
        write_csv(output_dir/'plantvillage_public_source_1498.csv', pv_ledger)
        physical = {'performed': False}
        if plantvillage_root:
            paths = [p for p in plantvillage_root.rglob('*') if p.is_file() and p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
            observed = {p.relative_to(plantvillage_root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            require(observed == pv_sources, 'Current public PlantVillage binaries differ from archived source hashes')
            physical = {'performed': True, 'public_source_images': 3852, 'matching_archived_source_hashes': 3852,
                        'evaluation_images_joined_to_verified_source': 1498, 'healthy_images_matching_source': 360}
        inputs = {name: hashlib.sha256(z.read(name)).hexdigest() for name in [master_name, split_name, crosswalk_name, pv_name]}
    report = {'doi': DOI, 'archive_sha256': ARCHIVE_SHA256, 'master_records': 13413,
              'internal_records': 11491, 'target_records': 5605,
              'target_records_with_complete_identity_fields': 5605,
              'target_records_in_archived_extraction': 5605,
              'canonical_split_field': 'evaluation_role', 'source_summary': summary,
              'plantvillage_public_binary_check': physical, 'input_sha256': inputs,
              'training_performed': False, 'model_inference_performed': False,
              'interpretation': 'Reconciles existing archived identities. Archived extraction identity is not independent proof of original collecting institution, biological parent or upstream component-license clearance.'}
    (output_dir/'SOURCE_TRACEABILITY_VERIFICATION.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--plantvillage-root', type=Path)
    args = parser.parse_args()
    archive = args.archive
    if archive is None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        archive = args.output_dir/'MAIZ_ZENODO_DATOS_Y_CODIGO_CANDIDATO.zip'
        request = urllib.request.Request(ARCHIVE_URL, headers={'User-Agent': 'Maize source traceability verification'})
        with urllib.request.urlopen(request, timeout=120) as response:
            archive.write_bytes(response.read())
    report = reconcile(archive, args.output_dir, args.plantvillage_root)
    print(json.dumps({'verified_target_records': report['target_records'],
                      'public_plantvillage_check': report['plantvillage_public_binary_check'],
                      'training_performed': False, 'model_inference_performed': False}))

if __name__ == '__main__':
    main()
