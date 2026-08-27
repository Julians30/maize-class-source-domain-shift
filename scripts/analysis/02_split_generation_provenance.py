"""Frozen split-generation provenance; historical E3 label is not manuscript E3

Release-safe Python export derived from: 02_generacion_splits_E2_E3_v1.ipynb.json
Notebook outputs and Colab identity metadata are intentionally excluded.
"""
try:
    from IPython.display import display
except ImportError:

    def display(obj):
        print(obj)
from pathlib import Path
from datetime import datetime
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
try:
    EN_COLAB = True
except Exception:
    EN_COLAB = False
    print('Entorno fuera de Colab. Se omite el montaje de Drive.')
print('ENTORNO RECOMENDADO: CPU')
print('GPU NECESARIA: NO')
print('Python:', sys.version.split()[0])
print('NumPy:', np.__version__)
print('Pandas:', pd.__version__)
print('Plataforma:', platform.platform())
print('Colab:', EN_COLAB)
import os
BASE = Path(os.environ.get('MAIZE_PROJECT_ROOT', '.')).resolve()
RESULTADOS = BASE / '04_resultados/reconciliacion'
ARCHIVO_MASTER = RESULTADOS / 'manifest_master_clean_snapshot_v1_pre_split.csv'
ARCHIVO_PROTOCOLO = RESULTADOS / 'protocolo_experimental_E1_E4_v1.json'
HASH_MASTER_ESPERADO = '19c902a8bd95b64d3594fa48a0a628a1357dbc48518f91e34e9fb502f27ac0e8'
HASH_PROTOCOLO_ESPERADO = '6acccb7ee31e60a51fd1fa83cb6699b3801fdf6402631ac189b6dedd64ac912f'
SALIDA_E3 = RESULTADOS / 'e3_multisource_split_v1_manifest.csv'
SALIDA_E3_RESUMEN = RESULTADOS / 'e3_multisource_split_v1_resumen.csv'
SALIDA_E3_ESTRATOS = RESULTADOS / 'e3_multisource_split_v1_estratos.csv'
SALIDA_E2A = RESULTADOS / 'e2a_adege_to_pandian_manifest_v1.csv'
SALIDA_E2A_BINARIO = RESULTADOS / 'e2a_pandian_external_binary_full_v1.csv'
SALIDA_E2A_BALANCEADO = RESULTADOS / 'e2a_pandian_external_binary_balanced_v1.csv'
SALIDA_E2B = RESULTADOS / 'e2b_pandian_to_adege_manifest_v1.csv'
SALIDA_E2B_BINARIO = RESULTADOS / 'e2b_adege_external_binary_full_v1.csv'
SALIDA_E2B_BALANCEADO = RESULTADOS / 'e2b_adege_external_binary_balanced_v1.csv'
SALIDA_E2_RESUMEN = RESULTADOS / 'e2_splits_v1_resumen.csv'
SALIDA_HASHES = RESULTADOS / 'splits_E2_E3_v1_hashes.csv'
SALIDA_FICHA = RESULTADOS / 'splits_E2_E3_v1_ficha_reproducibilidad.txt'
for archivo in [ARCHIVO_MASTER, ARCHIVO_PROTOCOLO]:
    if not archivo.exists():
        raise FileNotFoundError(f'No se encontró:\n{archivo}')
RESULTADOS.mkdir(parents=True, exist_ok=True)

def sha256_archivo(ruta, block_size=1024 * 1024):
    h = hashlib.sha256()
    with open(ruta, 'rb') as archivo:
        for bloque in iter(lambda: archivo.read(block_size), b''):
            h.update(bloque)
    return h.hexdigest()
hash_master = sha256_archivo(ARCHIVO_MASTER)
hash_protocolo = sha256_archivo(ARCHIVO_PROTOCOLO)
print('SHA master:', hash_master)
print('SHA protocolo:', hash_protocolo)
if hash_master != HASH_MASTER_ESPERADO:
    raise ValueError('La huella del snapshot maestro no coincide.')
if hash_protocolo != HASH_PROTOCOLO_ESPERADO:
    raise ValueError('La huella del protocolo congelado no coincide.')
print('Entradas congeladas verificadas correctamente.')
with open(ARCHIVO_PROTOCOLO, 'r', encoding='utf-8') as f:
    protocolo = json.load(f)
master = pd.read_csv(ARCHIVO_MASTER)
columnas_obligatorias = ['component_clean', 'source_operational', 'class', 'path', 'sha256', 'phash_standard', 'global_group_id']
faltantes = [columna for columna in columnas_obligatorias if columna not in master.columns]
if faltantes:
    raise KeyError(f'Faltan columnas en el snapshot maestro: {faltantes}')
assert len(master) == 13413
assert master['global_group_id'].nunique() == 13407
assert master['class'].nunique() == 9
assert master['component_clean'].nunique() == 4
assert master['source_operational'].nunique() == 7
assert int(master['path'].duplicated().sum()) == 0
assert len(master) - master['sha256'].nunique() == 0
assert len(master) - master['phash_standard'].nunique() == 0
print('Snapshot validado.')
print('Imágenes:', len(master))
print('Grupos:', master['global_group_id'].nunique())
print('Clases:', master['class'].nunique())
print('Componentes:', master['component_clean'].nunique())
print('Fuentes operacionales:', master['source_operational'].nunique())
display(master['class'].value_counts().sort_index().rename_axis('class').reset_index(name='n_images'))
SPLITS = ['train', 'val', 'test']
PROPORCIONES = np.array([0.7, 0.15, 0.15], dtype=float)
SEMILLA_E3 = 42

def semilla_estable(texto, semilla_base=42):
    contenido = f'{semilla_base}|{texto}'.encode('utf-8')
    digest = hashlib.sha256(contenido).digest()
    return int.from_bytes(digest[:8], 'big') % 2 ** 32

def asignar_conteos(n, proporciones=PROPORCIONES):
    if n <= 0:
        return np.array([0, 0, 0], dtype=int)
    valores = proporciones * n
    base = np.floor(valores).astype(int)
    faltan = int(n - base.sum())
    fracciones = valores - base
    orden = np.argsort(-fracciones, kind='mergesort')
    for indice in orden[:faltan]:
        base[indice] += 1
    if n >= 3:
        for indice in range(3):
            if base[indice] == 0:
                donante = int(np.argmax(base))
                if base[donante] <= 1:
                    raise RuntimeError('No fue posible asegurar presencia en los tres splits.')
                base[donante] -= 1
                base[indice] += 1
    if int(base.sum()) != int(n):
        raise RuntimeError('La asignación de conteos no suma n.')
    return base

def construir_split_grupos(df, semilla=42):
    chequeo_grupos = df.groupby('global_group_id').agg(n_classes=('class', 'nunique'), n_sources=('source_operational', 'nunique'), n_components=('component_clean', 'nunique'), n_images=('path', 'size'), class_name=('class', 'first'), source_name=('source_operational', 'first'), component_name=('component_clean', 'first')).reset_index()
    if int((chequeo_grupos['n_classes'] > 1).sum()) != 0:
        raise ValueError('Existen grupos multiclase.')
    if int((chequeo_grupos['n_sources'] > 1).sum()) != 0:
        raise ValueError('Existen grupos con más de una fuente operacional.')
    if int((chequeo_grupos['n_components'] > 1).sum()) != 0:
        raise ValueError('Existen grupos con más de un componente.')
    chequeo_grupos['stratum'] = chequeo_grupos['class_name'].astype(str) + '||' + chequeo_grupos['source_name'].astype(str)
    asignaciones = []
    for estrato, bloque in chequeo_grupos.groupby('stratum', sort=True):
        bloque = bloque.sort_values('global_group_id', kind='mergesort').reset_index(drop=True)
        rng = np.random.default_rng(semilla_estable(estrato, semilla))
        orden = rng.permutation(len(bloque))
        bloque = bloque.iloc[orden].reset_index(drop=True)
        conteos = asignar_conteos(len(bloque))
        inicio = 0
        for split, cantidad in zip(SPLITS, conteos):
            fin = inicio + int(cantidad)
            parte = bloque.iloc[inicio:fin].copy()
            parte['split'] = split
            asignaciones.append(parte)
            inicio = fin
        if inicio != len(bloque):
            raise RuntimeError(f'Asignación incompleta en el estrato {estrato}.')
    grupos_split = pd.concat(asignaciones, ignore_index=True)
    if grupos_split['global_group_id'].duplicated().any():
        raise ValueError('Un grupo fue asignado más de una vez.')
    salida = df.merge(grupos_split[['global_group_id', 'stratum', 'split']], on='global_group_id', how='left', validate='many_to_one')
    if salida['split'].isna().any():
        raise ValueError('Hay imágenes sin split asignado.')
    return (salida, grupos_split)

def muestreo_estratificado_determinista(df, n, columna_estrato='class', semilla=42):
    if n >= len(df):
        return df.copy()
    conteos = df[columna_estrato].value_counts().sort_index()
    proporciones = conteos / conteos.sum()
    deseados = proporciones * n
    asignados = np.floor(deseados).astype(int)
    restantes = int(n - asignados.sum())
    fracciones = (deseados - asignados).sort_values(ascending=False, kind='mergesort')
    for estrato in fracciones.index:
        if restantes <= 0:
            break
        if asignados.loc[estrato] < conteos.loc[estrato]:
            asignados.loc[estrato] += 1
            restantes -= 1
    while restantes > 0:
        progreso = False
        for estrato in conteos.index:
            if asignados.loc[estrato] < conteos.loc[estrato]:
                asignados.loc[estrato] += 1
                restantes -= 1
                progreso = True
                if restantes == 0:
                    break
        if not progreso:
            raise RuntimeError('No fue posible completar el muestreo.')
    partes = []
    for estrato, cantidad in asignados.items():
        bloque = df.loc[df[columna_estrato].eq(estrato)].sort_values('path', kind='mergesort').reset_index(drop=True)
        rng = np.random.default_rng(semilla_estable(f'{columna_estrato}|{estrato}', semilla))
        indices = rng.permutation(len(bloque))[:int(cantidad)]
        partes.append(bloque.iloc[indices].copy())
    salida = pd.concat(partes, ignore_index=True)
    if len(salida) != n:
        raise RuntimeError(f'El muestreo produjo {len(salida)} filas y se esperaban {n}.')
    return salida
print('Funciones deterministas definidas.')
e3, grupos_e3 = construir_split_grupos(master, semilla=SEMILLA_E3)
orden_split = pd.CategoricalDtype(categories=['train', 'val', 'test'], ordered=True)
e3['split'] = e3['split'].astype(orden_split)
e3 = e3.sort_values(['split', 'class', 'source_operational', 'path'], kind='mergesort').reset_index(drop=True)
fuga_grupos = int(e3.groupby('global_group_id')['split'].nunique().gt(1).sum())
fuga_sha = int(e3.groupby('sha256')['split'].nunique().gt(1).sum())
fuga_phash = int(e3.groupby('phash_standard')['split'].nunique().gt(1).sum())
resumen_e3 = e3.groupby('split', observed=True).agg(n_images=('path', 'size'), n_groups=('global_group_id', 'nunique'), n_classes=('class', 'nunique'), n_sources=('source_operational', 'nunique'), n_components=('component_clean', 'nunique')).reset_index()
estratos_e3 = e3.groupby(['class', 'source_operational', 'split'], observed=True).agg(n_images=('path', 'size'), n_groups=('global_group_id', 'nunique')).reset_index()
print('=== E3 MULTIFUENTE ===')
display(resumen_e3)
print('Fuga por grupo:', fuga_grupos)
print('Fuga por SHA:', fuga_sha)
print('Fuga por pHash exacto:', fuga_phash)
assert len(e3) == 13413
assert e3['global_group_id'].nunique() == 13407
assert fuga_grupos == 0
assert fuga_sha == 0
assert fuga_phash == 0
assert e3.groupby('split', observed=True)['class'].nunique().eq(9).all()
e3.to_csv(SALIDA_E3, index=False)
resumen_e3.to_csv(SALIDA_E3_RESUMEN, index=False)
estratos_e3.to_csv(SALIDA_E3_ESTRATOS, index=False)
print('E3 guardado:', SALIDA_E3)

def construir_e2(e3_df, codigo, componente_externo, componente_roya_entrenamiento):
    salida = e3_df.copy()
    salida['evaluation_role'] = salida['split'].astype(str)
    mascara_externa = salida['component_clean'].eq(componente_externo)
    salida.loc[mascara_externa, 'evaluation_role'] = 'external_component_test'
    if salida.loc[mascara_externa, 'evaluation_role'].ne('external_component_test').any():
        raise RuntimeError(f'{codigo}: el componente externo no quedó totalmente aislado.')
    roya_train = salida.loc[salida['evaluation_role'].eq('train') & salida['class'].eq('rust'), 'component_clean'].value_counts()
    if set(roya_train.index) != {componente_roya_entrenamiento}:
        raise ValueError(f'{codigo}: la roya de entrenamiento no proviene exclusivamente de {componente_roya_entrenamiento}. Se obtuvo: {roya_train.to_dict()}')
    salida['e2_scenario'] = codigo
    salida = salida.sort_values(['evaluation_role', 'class', 'source_operational', 'path'], kind='mergesort').reset_index(drop=True)
    fuga = int(salida.groupby('global_group_id')['evaluation_role'].nunique().gt(1).sum())
    if fuga != 0:
        raise ValueError(f'{codigo}: se detectó fuga de {fuga} grupos.')
    return salida
e2a = construir_e2(e3, codigo='E2_A_Adege_to_Pandian', componente_externo='pandian2019_clean', componente_roya_entrenamiento='adege_clean')
e2b = construir_e2(e3, codigo='E2_B_Pandian_to_Adege', componente_externo='adege_clean', componente_roya_entrenamiento='pandian2019_clean')
e2a.to_csv(SALIDA_E2A, index=False)
e2b.to_csv(SALIDA_E2B, index=False)
print('E2-A guardado:', SALIDA_E2A)
print('E2-B guardado:', SALIDA_E2B)
positivos_e2a = e2a.loc[e2a['evaluation_role'].eq('external_component_test') & e2a['class'].eq('rust')].copy()
negativos_e2a = e2a.loc[e2a['evaluation_role'].eq('test') & e2a['class'].ne('rust')].copy()
e2a_binario = pd.concat([positivos_e2a.assign(binary_label=1, binary_class='rust_external_positive', binary_negative_origin='not_applicable'), negativos_e2a.assign(binary_label=0, binary_class='reference_non_rust_negative', binary_negative_origin='E3_internal_test')], ignore_index=True)
e2a_binario['binary_evaluation_design'] = 'external_rust_vs_internal_reference_negatives'
n_balance_e2a = min(len(positivos_e2a), len(negativos_e2a))
positivos_e2a_bal = positivos_e2a.sort_values('path', kind='mergesort').head(n_balance_e2a).copy()
negativos_e2a_bal = muestreo_estratificado_determinista(negativos_e2a, n=n_balance_e2a, columna_estrato='class', semilla=42)
e2a_balanceado = pd.concat([positivos_e2a_bal.assign(binary_label=1, binary_class='rust_external_positive', binary_negative_origin='not_applicable'), negativos_e2a_bal.assign(binary_label=0, binary_class='reference_non_rust_negative', binary_negative_origin='E3_internal_test')], ignore_index=True)
e2a_balanceado['binary_evaluation_design'] = 'balanced_external_rust_vs_internal_reference_negatives'
externos_e2b = e2b.loc[e2b['evaluation_role'].eq('external_component_test')].copy()
clases_externas_e2b = set(externos_e2b['class'].astype(str).unique())
if clases_externas_e2b != {'healthy', 'rust'}:
    raise ValueError(f'E2-B esperaba únicamente healthy y rust en Adege, pero encontró {clases_externas_e2b}.')
e2b_binario = externos_e2b.copy()
e2b_binario['binary_label'] = e2b_binario['class'].eq('rust').astype(int)
e2b_binario['binary_class'] = np.where(e2b_binario['binary_label'].eq(1), 'rust_external_positive', 'source_pure_healthy_negative')
e2b_binario['binary_negative_origin'] = 'Adege_external_component'
e2b_binario['binary_evaluation_design'] = 'source_pure_Adege_rust_vs_healthy'
positivos_e2b = e2b_binario.loc[e2b_binario['binary_label'].eq(1)].copy()
negativos_e2b = e2b_binario.loc[e2b_binario['binary_label'].eq(0)].copy()
n_balance_e2b = min(len(positivos_e2b), len(negativos_e2b))
positivos_e2b_bal = positivos_e2b.sort_values('path', kind='mergesort').head(n_balance_e2b).copy()
negativos_e2b_bal = muestreo_estratificado_determinista(negativos_e2b, n=n_balance_e2b, columna_estrato='class', semilla=42)
e2b_balanceado = pd.concat([positivos_e2b_bal, negativos_e2b_bal], ignore_index=True)
e2b_balanceado['binary_evaluation_design'] = 'balanced_source_pure_Adege_rust_vs_healthy'
for frame in [e2a_binario, e2a_balanceado, e2b_binario, e2b_balanceado]:
    frame.sort_values(['binary_label', 'class', 'path'], kind='mergesort', inplace=True)
    frame.reset_index(drop=True, inplace=True)
e2a_binario.to_csv(SALIDA_E2A_BINARIO, index=False)
e2a_balanceado.to_csv(SALIDA_E2A_BALANCEADO, index=False)
e2b_binario.to_csv(SALIDA_E2B_BINARIO, index=False)
e2b_balanceado.to_csv(SALIDA_E2B_BALANCEADO, index=False)
print('=== EVALUACIONES BINARIAS E2 ===')
print('E2-A full:', e2a_binario['binary_label'].value_counts().sort_index().to_dict())
print('E2-A balanced:', e2a_balanceado['binary_label'].value_counts().sort_index().to_dict())
print('E2-B full:', e2b_binario['binary_label'].value_counts().sort_index().to_dict())
print('E2-B balanced:', e2b_balanceado['binary_label'].value_counts().sort_index().to_dict())
assert len(positivos_e2a) == 1922
assert len(positivos_e2b) == 1075
assert len(negativos_e2b) == 2376
assert e2a_balanceado['binary_label'].value_counts().nunique() == 1
assert e2b_balanceado['binary_label'].value_counts().nunique() == 1
resumenes = []
for codigo, df in [('E2_A_Adege_to_Pandian', e2a), ('E2_B_Pandian_to_Adege', e2b)]:
    bloque = df.groupby('evaluation_role').agg(n_images=('path', 'size'), n_groups=('global_group_id', 'nunique'), n_classes=('class', 'nunique'), n_sources=('source_operational', 'nunique'), n_components=('component_clean', 'nunique')).reset_index()
    bloque.insert(0, 'scenario', codigo)
    resumenes.append(bloque)
resumen_e2 = pd.concat(resumenes, ignore_index=True)
resumen_e2.to_csv(SALIDA_E2_RESUMEN, index=False)
print('=== RESUMEN E2 ===')
display(resumen_e2)
assert e2a.loc[e2a['component_clean'].eq('pandian2019_clean'), 'evaluation_role'].eq('external_component_test').all()
assert e2b.loc[e2b['component_clean'].eq('adege_clean'), 'evaluation_role'].eq('external_component_test').all()
assert not (e2a['evaluation_role'].eq('train') & e2a['component_clean'].eq('pandian2019_clean')).any()
assert not (e2b['evaluation_role'].eq('train') & e2b['component_clean'].eq('adege_clean')).any()
print('Verificaciones E2 completadas.')
archivos_salida = {'e3_manifest': SALIDA_E3, 'e3_resumen': SALIDA_E3_RESUMEN, 'e3_estratos': SALIDA_E3_ESTRATOS, 'e2a_manifest': SALIDA_E2A, 'e2a_binary_full': SALIDA_E2A_BINARIO, 'e2a_binary_balanced': SALIDA_E2A_BALANCEADO, 'e2b_manifest': SALIDA_E2B, 'e2b_binary_full': SALIDA_E2B_BINARIO, 'e2b_binary_balanced': SALIDA_E2B_BALANCEADO, 'e2_resumen': SALIDA_E2_RESUMEN}
registros_hash = []
for nombre, ruta in archivos_salida.items():
    registros_hash.append({'artifact': nombre, 'filename': ruta.name, 'n_bytes': ruta.stat().st_size, 'sha256': sha256_archivo(ruta)})
hashes = pd.DataFrame(registros_hash)
hashes.to_csv(SALIDA_HASHES, index=False)
hash_archivo_hashes = sha256_archivo(SALIDA_HASHES)
ficha = f"\nSPLITS E2–E3 CONGELADOS — V1\n=============================\nFecha: {datetime.now().isoformat()}\n\nENTORNO\n-------\nCPU.\nGPU no requerida.\n\nENTRADAS\n--------\nSnapshot maestro:\n{ARCHIVO_MASTER.name}\nSHA-256:\n{HASH_MASTER_ESPERADO}\n\nProtocolo:\n{ARCHIVO_PROTOCOLO.name}\nSHA-256:\n{HASH_PROTOCOLO_ESPERADO}\n\nE3\n--\nUnidad de partición:\nglobal_group_id\n\nEstratificación:\nclass + source_operational\n\nSemilla:\n{SEMILLA_E3}\n\nImágenes:\n{len(e3)}\n\nGrupos:\n{e3['global_group_id'].nunique()}\n\nFuga por grupo:\n0\n\nFuga por SHA:\n0\n\nFuga por pHash exacto:\n0\n\nE2-A\n----\nEntrenamiento de roya:\nadege_clean\n\nComponente externo:\npandian2019_clean\n\nPositivos externos de roya:\n{len(positivos_e2a)}\n\nNota:\nComo Pandian solo contiene roya, su evaluación binaria completa\nutiliza negativos de referencia procedentes del internal_test\nno-roya. No debe presentarse como evaluación source-pure.\n\nE2-B\n----\nEntrenamiento de roya:\npandian2019_clean\n\nComponente externo:\nadege_clean\n\nPositivos externos de roya:\n{len(positivos_e2b)}\n\nNegativos externos saludables:\n{len(negativos_e2b)}\n\nNota:\nE2-B permite evaluación binaria source-pure dentro de Adege.\n\nARCHIVO DE HUELLAS\n------------------\n{SALIDA_HASHES.name}\n\nSHA-256 del archivo de huellas:\n{hash_archivo_hashes}\n\nESTADO\n------\nLos splits E2 y E3 quedan congelados. No deben regenerarse\ndespués de iniciar el entrenamiento ni después de observar\nresultados experimentales.\n".strip()
SALIDA_FICHA.write_text(ficha + '\n', encoding='utf-8')
print('=== SPLITS E2–E3 CONGELADOS ===')
display(hashes)
print('Archivo de huellas:', SALIDA_HASHES)
print('SHA-256 del archivo de huellas:', hash_archivo_hashes)
print('Ficha:', SALIDA_FICHA)
