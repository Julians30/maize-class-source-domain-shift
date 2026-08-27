"""Historical protocol and frozen-input integrity audit

Release-safe Python export derived from: 01_protocolo_experimental_E1_E4_v1.ipynb.json
Notebook outputs and Colab identity metadata are intentionally excluded.
"""
try:
    from IPython.display import display
except ImportError:

    def display(obj):
        print(obj)
from pathlib import Path
import os
import sys
import json
import hashlib
import platform
import pandas as pd
import numpy as np
try:
    EN_COLAB = True
except Exception:
    EN_COLAB = False
    print('Entorno fuera de Google Colab. Se omite el montaje de Drive.')
print('Python:', sys.version.split()[0])
print('Plataforma:', platform.platform())
print('Colab:', EN_COLAB)
import os
BASE = Path(os.environ.get('MAIZE_PROJECT_ROOT', '.')).resolve()
RESULTADOS = BASE / '04_resultados/reconciliacion'
ARCHIVOS = {'raw_ccmt_pre_split': RESULTADOS / 'raw_ccmt_manifest_final_pre_split.csv', 'raw_ccmt_split_v1': RESULTADOS / 'raw_ccmt_split_v1_manifest.csv', 'adege_clean': RESULTADOS / 'adege_manifest_final_pre_split.csv', 'cimmyt_mlnd_clean': RESULTADOS / 'cimmyt_mlnd_manifest_final_pre_split.csv', 'pandian2019_clean': RESULTADOS / 'pandian2019_manifest_final_pre_split.csv', 'master_snapshot_v1': RESULTADOS / 'manifest_master_clean_snapshot_v1_pre_split.csv', 'inventario_fuentes_final': RESULTADOS / 'inventario_fuentes_estado_auditoria_final.csv', 'cierre_auditoria': RESULTADOS / 'cierre_auditoria_fuentes_y_corpus_v1.txt'}
HASHES_ESPERADOS = {'raw_ccmt_split_v1': '9e344878ced634dbc1a4ad1955792d3b5a35e901351cc2c432da7bdfd1b42404', 'adege_clean': '2f91f31cd10520669d4cb88f4f32eb503d7442182a41ee5f8ad06e2ff245e382', 'cimmyt_mlnd_clean': 'b17f9265adcd048e23bb952bada972721e13cbfacb1f589be07c042496224b1d', 'pandian2019_clean': '7672b1f7716b8d738ac8d7e9542ce5ecd2c2152d91fd241dd7a5fe804d4001c8', 'master_snapshot_v1': '19c902a8bd95b64d3594fa48a0a628a1357dbc48518f91e34e9fb502f27ac0e8', 'inventario_fuentes_final': '142ca054b38fc998d58879b1b9f866132de760ab06bca88afb5945a2f9963d92'}
faltantes = [str(ruta) for ruta in ARCHIVOS.values() if not ruta.exists()]
if faltantes:
    raise FileNotFoundError('No se encontraron los siguientes archivos:\n' + '\n'.join(faltantes))
print('Archivos congelados encontrados:', len(ARCHIVOS))

def sha256_archivo(ruta, bloque=1024 * 1024):
    h = hashlib.sha256()
    with open(ruta, 'rb') as archivo:
        for fragmento in iter(lambda: archivo.read(bloque), b''):
            h.update(fragmento)
    return h.hexdigest()
registros_hash = []
for nombre, hash_esperado in HASHES_ESPERADOS.items():
    ruta = ARCHIVOS[nombre]
    hash_obtenido = sha256_archivo(ruta)
    registros_hash.append({'archivo_logico': nombre, 'archivo': ruta.name, 'sha256_esperado': hash_esperado, 'sha256_obtenido': hash_obtenido, 'coincide': hash_obtenido == hash_esperado})
verificacion_hash = pd.DataFrame(registros_hash)
display(verificacion_hash)
if not verificacion_hash['coincide'].all():
    problemáticos = verificacion_hash.loc[~verificacion_hash['coincide'], ['archivo_logico', 'sha256_esperado', 'sha256_obtenido']]
    raise ValueError('Una o más huellas no coinciden con los archivos congelados:\n' + problemáticos.to_string(index=False))
print('Todas las huellas verificadas correctamente.')
raw_split = pd.read_csv(ARCHIVOS['raw_ccmt_split_v1'])
master = pd.read_csv(ARCHIVOS['master_snapshot_v1'])
columnas_split = {'split', 'class', 'path'}
faltantes_split = columnas_split - set(raw_split.columns)
if faltantes_split:
    raise KeyError(f'Faltan columnas en E1: {sorted(faltantes_split)}')
columna_grupo_e1 = next((c for c in ['global_group_id', 'group_id', 'group_unit'] if c in raw_split.columns), None)
if columna_grupo_e1 is None:
    raise KeyError('No se encontró una columna de agrupación en E1.')
columnas_master = {'component_clean', 'source_operational', 'class', 'path', 'sha256', 'phash_standard', 'global_group_id'}
faltantes_master = columnas_master - set(master.columns)
if faltantes_master:
    raise KeyError(f'Faltan columnas en el snapshot maestro: {sorted(faltantes_master)}')
resumen_e1 = raw_split.groupby('split').agg(n_images=('path', 'size'), n_groups=(columna_grupo_e1, 'nunique'), n_classes=('class', 'nunique')).reset_index()
print('=== E1 CONGELADO ===')
display(resumen_e1)
assert len(raw_split) == 4811
assert raw_split['class'].nunique() == 7
assert raw_split.loc[raw_split['split'].eq('train')].shape[0] == 3367
assert raw_split.loc[raw_split['split'].eq('val')].shape[0] == 723
assert raw_split.loc[raw_split['split'].eq('test')].shape[0] == 721
grupos_por_split = raw_split.groupby(columna_grupo_e1)['split'].nunique()
assert int((grupos_por_split > 1).sum()) == 0
print('\n=== SNAPSHOT MAESTRO V1 ===')
print('Imágenes:', len(master))
print('Grupos:', master['global_group_id'].nunique())
print('Clases:', master['class'].nunique())
print('Componentes:', master['component_clean'].nunique())
print('Fuentes operativas:', master['source_operational'].nunique())
print('Rutas repetidas:', int(master['path'].duplicated().sum()))
print('SHA repetidos:', len(master) - master['sha256'].nunique())
print('pHash exactos repetidos:', len(master) - master['phash_standard'].nunique())
assert len(master) == 13413
assert master['global_group_id'].nunique() == 13407
assert master['class'].nunique() == 9
assert master['component_clean'].nunique() == 4
assert int(master['path'].duplicated().sum()) == 0
assert len(master) - master['sha256'].nunique() == 0
assert len(master) - master['phash_standard'].nunique() == 0
display(master['class'].value_counts().sort_index().rename_axis('class').reset_index(name='n_images'))
PROTOCOLO = {'project': 'Convoluciones locales vs. atención global: benchmark CNN–ViT para enfermedades y plagas del maíz', 'protocol_version': '1.0', 'dataset_snapshot': {'master_manifest': ARCHIVOS['master_snapshot_v1'].name, 'master_sha256': HASHES_ESPERADOS['master_snapshot_v1'], 'n_images': 13413, 'n_groups': 13407, 'n_classes': 9, 'n_clean_components': 4, 'n_operational_sources': 7}, 'scenarios': {'E1': {'name': 'Intra-CCMT benchmark', 'manifest': ARCHIVOS['raw_ccmt_split_v1'].name, 'manifest_sha256': HASHES_ESPERADOS['raw_ccmt_split_v1'], 'classes': 7, 'train_images': 3367, 'val_images': 723, 'test_images': 721, 'split_policy': 'frozen_group_stratified_70_15_15', 'primary_endpoint': 'macro_f1'}, 'E2_A': {'name': 'External rust transfer Adege_to_Pandian', 'training_rust_source': 'Adege', 'external_rust_source': 'Pandian2019', 'interpretation': 'External-source stress test for rust embedded in a multiclass classifier; not a fully source-independent nine-class test.', 'rust_endpoints': ['rust_recall', 'rust_f1', 'rust_ovr_auroc', 'mean_rust_probability', 'ece', 'brier_score']}, 'E2_B': {'name': 'External rust transfer Pandian_to_Adege', 'training_rust_source': 'Pandian2019', 'external_rust_source': 'Adege', 'interpretation': 'External-source stress test for rust embedded in a multiclass classifier; not a fully source-independent nine-class test.', 'rust_endpoints': ['rust_recall', 'rust_f1', 'rust_ovr_auroc', 'mean_rust_probability', 'ece', 'brier_score']}, 'E3': {'name': 'Nine-class multisource classification', 'manifest': ARCHIVOS['master_snapshot_v1'].name, 'split_seed': 42, 'target_proportions': {'train': 0.7, 'val': 0.15, 'test': 0.15}, 'split_unit': 'global_group_id', 'stratification_priority': ['class', 'source_operational'], 'interpretation': 'Multisource classification. Single-source classes remain confounded with source and must be discussed explicitly.', 'primary_endpoint': 'macro_f1'}, 'E4': {'name': 'Controlled robustness evaluation', 'test_sets': ['E1_test', 'E3_test'], 'degradations': {'gaussian_blur_sigma': [1.0, 2.0, 3.0], 'gaussian_noise_std_0_1': [0.02, 0.05, 0.1], 'brightness_factor': [0.6, 0.8, 1.2, 1.4], 'jpeg_quality': [70, 50, 30], 'central_occlusion_fraction': [0.1, 0.2, 0.3]}, 'selection_use': 'forbidden'}}, 'architectures': [{'family': 'CNN', 'name': 'MobileNetV3-Large', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}, {'family': 'CNN', 'name': 'ResNet50', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}, {'family': 'CNN', 'name': 'EfficientNet-B0', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}, {'family': 'Hybrid', 'name': 'MobileViT-S', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}, {'family': 'Transformer', 'name': 'ViT-Base/16', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}, {'family': 'Transformer', 'name': 'Swin-Tiny', 'input_size': 224, 'initialization': 'ImageNet_pretrained'}], 'random_seeds': [17, 42, 73], 'training': {'max_epochs': 40, 'early_stopping_patience': 8, 'early_stopping_metric': 'validation_macro_f1', 'optimizer': 'AdamW', 'base_learning_rate': 0.0003, 'weight_decay': 0.0001, 'scheduler': 'cosine_decay_with_5_percent_warmup', 'loss': 'class_weighted_cross_entropy', 'class_weights': 'computed_from_training_partition_only_and_normalized_to_mean_1', 'label_smoothing': 0.1, 'effective_batch_size': 64, 'gradient_accumulation': 'allowed_to_reach_effective_batch_size', 'mixed_precision': True, 'fine_tuning': 'all_layers', 'checkpoint_rule': 'best_validation_macro_f1; tie_breaker_validation_MCC; second_tie_breaker_lower_validation_ECE'}, 'preprocessing': {'train': ['RandomResizedCrop_224_scale_0.80_1.00', 'RandomHorizontalFlip_p_0.50', 'RandomRotation_plus_minus_15_degrees', 'ColorJitter_brightness_0.20_contrast_0.20_saturation_0.20_hue_0.05', 'RandomErasing_p_0.10_scale_0.02_0.10', 'ImageNet_normalization'], 'validation_test': ['Resize_short_side_256', 'CenterCrop_224', 'ImageNet_normalization'], 'pregenerated_augmentation': 'forbidden', 'online_augmentation_after_split_only': True}, 'metrics': {'primary': 'macro_f1', 'secondary': ['balanced_accuracy', 'matthews_correlation_coefficient', 'per_class_recall', 'per_class_f1', 'macro_ovr_auroc_when_estimable', 'confusion_matrix'], 'calibration': ['ece_15_equal_width_bins', 'multiclass_brier_score', 'temperature_scaling_fitted_on_validation_only', 'coverage_risk_curve'], 'efficiency': ['trainable_parameters', 'model_file_size_mb', 'flops_or_macs', 'single_image_latency_ms_same_gpu', 'throughput_images_per_second_same_gpu', 'peak_gpu_memory_mb']}, 'statistics': {'confidence_intervals': 'paired_bootstrap_10000_resamples', 'paired_score_test': 'paired_permutation_test', 'correctness_comparison': 'McNemar_test', 'multiple_testing': 'Holm_correction', 'alpha': 0.05, 'unit_of_resampling': 'group_id_when_groups_have_multiple_images_otherwise_image'}, 'interpretability': {'cnn': 'Grad-CAM', 'transformers': 'attention_rollout', 'all_models': 'occlusion_sensitivity', 'equivalence_claim_between_methods': False, 'case_sampling': 'predefined_correct_incorrect_and_low_confidence_cases'}, 'test_set_policy': {'hyperparameter_tuning_on_test': False, 'model_selection_on_test': False, 'temperature_scaling_on_test': False, 'threshold_selection_on_test': False, 'single_final_evaluation_after_protocol_freeze': True}, 'reporting': {'per_seed_results_required': True, 'mean_and_standard_deviation_required': True, 'confidence_intervals_required': True, 'limitations_required': ['source_class_confounding', 'single_source_classes', 'operational_source_labels_not_equal_independent_sources', 'web_application_is_server_side_not_native_mobile']}}
print('Protocolo definido.')
print('Arquitecturas:', len(PROTOCOLO['architectures']))
print('Semillas:', PROTOCOLO['random_seeds'])
print('Escenarios:', list(PROTOCOLO['scenarios'].keys()))
assert len(PROTOCOLO['architectures']) == 6
assert len(PROTOCOLO['random_seeds']) == 3
assert PROTOCOLO['metrics']['primary'] == 'macro_f1'
assert PROTOCOLO['test_set_policy']['model_selection_on_test'] is False
assert PROTOCOLO['preprocessing']['pregenerated_augmentation'] == 'forbidden'
assert PROTOCOLO['scenarios']['E3']['split_unit'] == 'global_group_id'
rust_por_componente = master.loc[master['class'].eq('rust')].groupby(['component_clean', 'source_operational']).size().rename('n_images').reset_index().sort_values(['component_clean', 'source_operational'])
print('=== ROYA DISPONIBLE PARA E2 ===')
display(rust_por_componente)
assert int(master.loc[master['component_clean'].eq('adege_clean') & master['class'].eq('rust')].shape[0]) == 1075
assert int(master.loc[master['component_clean'].eq('pandian2019_clean') & master['class'].eq('rust')].shape[0]) == 1922
print('Validaciones lógicas completadas.')
SALIDA_JSON = RESULTADOS / 'protocolo_experimental_E1_E4_v1.json'
SALIDA_TXT = RESULTADOS / 'protocolo_experimental_E1_E4_v1.txt'
SALIDA_MODELOS = RESULTADOS / 'protocolo_modelos_v1.csv'
SALIDA_ESCENARIOS = RESULTADOS / 'protocolo_escenarios_v1.csv'
SALIDA_HASHES = RESULTADOS / 'protocolo_archivos_congelados_hashes_v1.csv'
SALIDA_FICHA = RESULTADOS / 'protocolo_experimental_E1_E4_v1_ficha.txt'
with open(SALIDA_JSON, 'w', encoding='utf-8') as f:
    json.dump(PROTOCOLO, f, ensure_ascii=False, indent=2)
with open(SALIDA_TXT, 'w', encoding='utf-8') as f:
    f.write(json.dumps(PROTOCOLO, ensure_ascii=False, indent=2))
    f.write('\n')
pd.DataFrame(PROTOCOLO['architectures']).to_csv(SALIDA_MODELOS, index=False)
escenarios_planos = []
for codigo, contenido in PROTOCOLO['scenarios'].items():
    escenarios_planos.append({'scenario_code': codigo, 'name': contenido.get('name', ''), 'primary_endpoint': contenido.get('primary_endpoint', ''), 'split_policy': contenido.get('split_policy', ''), 'interpretation': contenido.get('interpretation', '')})
pd.DataFrame(escenarios_planos).to_csv(SALIDA_ESCENARIOS, index=False)
verificacion_hash.to_csv(SALIDA_HASHES, index=False)
hash_protocolo = sha256_archivo(SALIDA_JSON)
ficha = f"\nPROTOCOLO EXPERIMENTAL CONGELADO E1–E4\n=======================================\nVersión: {PROTOCOLO['protocol_version']}\n\nSnapshot maestro:\n{ARCHIVOS['master_snapshot_v1'].name}\n\nSHA-256 del snapshot:\n{HASHES_ESPERADOS['master_snapshot_v1']}\n\nSplit E1:\n{ARCHIVOS['raw_ccmt_split_v1'].name}\n\nSHA-256 del split E1:\n{HASHES_ESPERADOS['raw_ccmt_split_v1']}\n\nArquitecturas:\n{len(PROTOCOLO['architectures'])}\n\nSemillas:\n{PROTOCOLO['random_seeds']}\n\nEscenarios:\n{list(PROTOCOLO['scenarios'].keys())}\n\nMétrica primaria:\n{PROTOCOLO['metrics']['primary']}\n\nArchivo de protocolo:\n{SALIDA_JSON.name}\n\nSHA-256 del protocolo:\n{hash_protocolo}\n\nEstado:\nProtocolo congelado antes de generar los splits E2 y E3 y antes\nde ejecutar cualquier entrenamiento.\n".strip()
SALIDA_FICHA.write_text(ficha + '\n', encoding='utf-8')
print('=== PROTOCOLO CONGELADO ===')
print('JSON:', SALIDA_JSON)
print('TXT:', SALIDA_TXT)
print('Modelos:', SALIDA_MODELOS)
print('Escenarios:', SALIDA_ESCENARIOS)
print('Verificación de hashes:', SALIDA_HASHES)
print('Ficha:', SALIDA_FICHA)
print('SHA-256 del protocolo:', hash_protocolo)
