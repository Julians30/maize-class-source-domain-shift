'
Release-safe provenance extraction from: 03_validacion_dataloaders_v1.ipynb.json

This script preserves the original notebook code-cell order. Release hygiene is
limited to removing Google Colab Drive mounting, notebook magics, execution
outputs/metadata, and replacing the private project-root literal with the
MAIZE_PROJECT_ROOT environment variable. No frozen scientific result is
recomputed during repository auditing.

Historical naming note: legacy E3 references in archival code are provenance
only; manuscript-facing E3 is the filtered PlantVillage external evaluation.
'

from __future__ import annotations

import os

import tempfile

from pathlib import Path

PROJECT_ROOT = Path(os.environ.get('MAIZE_PROJECT_ROOT', Path.cwd())).expanduser().resolve()

from pathlib import Path

from datetime import datetime

import hashlib

import json

import os

import platform

import random

import sys

import time

import warnings

import numpy as np

import pandas as pd

from PIL import Image, ImageFile, ImageOps

try:
    EN_COLAB = False
except Exception:
    EN_COLAB = False
    print('Entorno fuera de Colab. Se omite el montaje de Drive.')

import torch

from torch.utils.data import Dataset, DataLoader

from torchvision import transforms

from torchvision.transforms import InterpolationMode

from torchvision.utils import make_grid

import matplotlib.pyplot as plt

ImageFile.LOAD_TRUNCATED_IMAGES = False

warnings.filterwarnings('once')

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print('ENTORNO RECOMENDADO: GPU')

print('GPU NECESARIA PARA ESTA ETAPA: NO, PERO RECOMENDADA')

print('Dispositivo detectado:', DEVICE)

print('Python:', sys.version.split()[0])

print('PyTorch:', torch.__version__)

print('Torchvision disponible')

print('Plataforma:', platform.platform())

print('Colab:', EN_COLAB)

if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('Memoria GPU total (GB):', round(torch.cuda.get_device_properties(0).total_memory / 1024 ** 3, 2))
else:
    print('Advertencia: no se detectó GPU. La validación seguirá en CPU.')

SEMILLA = 42

VALIDACION_RAPIDA_POR_ESTRATO = 3

ESCANEO_COMPLETO_DECODIFICACION = False

BATCH_SIZE_VALIDACION = 32

NUM_WORKERS = 2

PIN_MEMORY = torch.cuda.is_available()

PERSISTENT_WORKERS = NUM_WORKERS > 0

random.seed(SEMILLA)

np.random.seed(SEMILLA)

torch.manual_seed(SEMILLA)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEMILLA)

torch.backends.cudnn.benchmark = False

torch.backends.cudnn.deterministic = True

print('Semilla:', SEMILLA)

print('Batch de validación:', BATCH_SIZE_VALIDACION)

print('Workers:', NUM_WORKERS)

print('Pin memory:', PIN_MEMORY)

print('Escaneo completo:', ESCANEO_COMPLETO_DECODIFICACION)

BASE = PROJECT_ROOT

RESULTADOS = BASE / '04_resultados/reconciliacion'

ARCHIVO_E1 = RESULTADOS / 'raw_ccmt_split_v1_manifest.csv'

ARCHIVO_E3 = RESULTADOS / 'e3_multisource_split_v1_manifest.csv'

ARCHIVO_E2A = RESULTADOS / 'e2a_adege_to_pandian_manifest_v1.csv'

ARCHIVO_E2B = RESULTADOS / 'e2b_pandian_to_adege_manifest_v1.csv'

ARCHIVO_E2A_BIN = RESULTADOS / 'e2a_pandian_external_binary_full_v1.csv'

ARCHIVO_E2B_BIN = RESULTADOS / 'e2b_adege_external_binary_full_v1.csv'

ARCHIVO_SPLITS_HASHES = RESULTADOS / 'splits_E2_E3_v1_hashes.csv'

ARCHIVO_PROTOCOLO = RESULTADOS / 'protocolo_experimental_E1_E4_v1.json'

HASH_E1_ESPERADO = '9e344878ced634dbc1a4ad1955792d3b5a35e901351cc2c432da7bdfd1b42404'

HASH_PROTOCOLO_ESPERADO = '6acccb7ee31e60a51fd1fa83cb6699b3801fdf6402631ac189b6dedd64ac912f'

HASH_ARCHIVO_SPLITS_ESPERADO = '046056b50e37acfa001b566690d769e327f7cfe8a2998e4123f9d26b9aeeeff0'

SALIDA_MAPA_E1 = RESULTADOS / 'class_mapping_E1_v1.json'

SALIDA_MAPA_E3 = RESULTADOS / 'class_mapping_E3_v1.json'

SALIDA_CONFIG = RESULTADOS / 'dataloader_config_v1.json'

SALIDA_RUTAS = RESULTADOS / 'dataloader_path_validation_v1.csv'

SALIDA_BATCHES = RESULTADOS / 'dataloader_batch_validation_v1.csv'

SALIDA_DECODIFICACION = RESULTADOS / 'dataloader_decode_validation_v1.csv'

SALIDA_MUESTRA_E1 = RESULTADOS / 'dataloader_sample_E1_v1.png'

SALIDA_MUESTRA_E3 = RESULTADOS / 'dataloader_sample_E3_v1.png'

SALIDA_HASHES = RESULTADOS / 'dataloader_validation_artifacts_v1_hashes.csv'

SALIDA_FICHA = RESULTADOS / 'dataloader_validation_v1_ficha.txt'

entradas = [ARCHIVO_E1, ARCHIVO_E3, ARCHIVO_E2A, ARCHIVO_E2B, ARCHIVO_E2A_BIN, ARCHIVO_E2B_BIN, ARCHIVO_SPLITS_HASHES, ARCHIVO_PROTOCOLO]

faltantes = [str(ruta) for ruta in entradas if not ruta.exists()]

if faltantes:
    raise FileNotFoundError('No se encontraron los siguientes archivos:\n' + '\n'.join(faltantes))

def sha256_archivo(ruta, block_size=1024 * 1024):
    h = hashlib.sha256()
    with open(ruta, 'rb') as archivo:
        for bloque in iter(lambda: archivo.read(block_size), b''):
            h.update(bloque)
    return h.hexdigest()

assert sha256_archivo(ARCHIVO_E1) == HASH_E1_ESPERADO

assert sha256_archivo(ARCHIVO_PROTOCOLO) == HASH_PROTOCOLO_ESPERADO

assert sha256_archivo(ARCHIVO_SPLITS_HASHES) == HASH_ARCHIVO_SPLITS_ESPERADO

print('Huellas principales verificadas.')

hashes_splits = pd.read_csv(ARCHIVO_SPLITS_HASHES)

if not {'artifact', 'filename', 'sha256'}.issubset(hashes_splits.columns):
    raise KeyError('El archivo de huellas de E2-E3 no contiene las columnas esperadas.')

verificaciones = []

for _, fila in hashes_splits.iterrows():
    ruta = RESULTADOS / str(fila['filename'])
    existe = ruta.exists()
    hash_obtenido = sha256_archivo(ruta) if existe else ''
    hash_esperado = str(fila['sha256'])
    verificaciones.append({'artifact': fila['artifact'], 'filename': fila['filename'], 'exists': existe, 'sha256_expected': hash_esperado, 'sha256_observed': hash_obtenido, 'matches': existe and hash_obtenido == hash_esperado})

verificacion_splits = pd.DataFrame(verificaciones)

display(verificacion_splits)

if not verificacion_splits['matches'].all():
    raise ValueError('Una o más salidas congeladas de E2-E3 no coinciden.')

print('Todas las huellas E2-E3 coinciden.')

e1 = pd.read_csv(ARCHIVO_E1)

e3 = pd.read_csv(ARCHIVO_E3)

e2a = pd.read_csv(ARCHIVO_E2A)

e2b = pd.read_csv(ARCHIVO_E2B)

e2a_bin = pd.read_csv(ARCHIVO_E2A_BIN)

e2b_bin = pd.read_csv(ARCHIVO_E2B_BIN)

clases_e1 = sorted(e1['class'].dropna().astype(str).unique())

clases_e3 = sorted(e3['class'].dropna().astype(str).unique())

mapa_e1 = {clase: indice for indice, clase in enumerate(clases_e1)}

mapa_e3 = {clase: indice for indice, clase in enumerate(clases_e3)}

assert len(mapa_e1) == 7

assert len(mapa_e3) == 9

with open(SALIDA_MAPA_E1, 'w', encoding='utf-8') as f:
    json.dump(mapa_e1, f, ensure_ascii=False, indent=2)

with open(SALIDA_MAPA_E3, 'w', encoding='utf-8') as f:
    json.dump(mapa_e3, f, ensure_ascii=False, indent=2)

print('Mapa E1:')

print(json.dumps(mapa_e1, ensure_ascii=False, indent=2))

print('\nMapa E3:')

print(json.dumps(mapa_e3, ensure_ascii=False, indent=2))

manifiestos = {'E1': e1, 'E3': e3, 'E2A': e2a, 'E2B': e2b, 'E2A_BINARY': e2a_bin, 'E2B_BINARY': e2b_bin}

registros_rutas = []

for nombre, df in manifiestos.items():
    if 'path' not in df.columns:
        raise KeyError(f'{nombre} no contiene la columna path.')
    existe = df['path'].astype(str).map(lambda p: Path(p).exists())
    registros_rutas.append({'manifest': nombre, 'n_rows': len(df), 'n_existing_paths': int(existe.sum()), 'n_missing_paths': int((~existe).sum()), 'all_paths_exist': bool(existe.all())})
