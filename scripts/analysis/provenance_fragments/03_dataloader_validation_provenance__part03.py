if ESCANEO_COMPLETO_DECODIFICACION:
    muestra_decode = e3.copy()
    tipo_escaneo = 'full_E3'
else:
    muestra_decode = pd.concat([muestra_estratificada(e1, VALIDACION_RAPIDA_POR_ESTRATO), muestra_estratificada(e3, VALIDACION_RAPIDA_POR_ESTRATO), muestra_estratificada(e2a.loc[e2a['evaluation_role'].eq('external_component_test')], VALIDACION_RAPIDA_POR_ESTRATO), muestra_estratificada(e2b.loc[e2b['evaluation_role'].eq('external_component_test')], VALIDACION_RAPIDA_POR_ESTRATO)], ignore_index=True).drop_duplicates('path')
    tipo_escaneo = 'quick_stratified'

registros_decode = []

inicio = time.time()

for numero, (_, fila) in enumerate(muestra_decode.iterrows(), start=1):
    ruta = str(fila['path'])
    try:
        with Image.open(ruta) as image:
            image = ImageOps.exif_transpose(image)
            image.load()
            width, height = image.size
            mode = image.mode
        estado = 'ok'
        error = ''
    except Exception as exc:
        width = None
        height = None
        mode = ''
        estado = 'error'
        error = f'{type(exc).__name__}: {exc}'
    registros_decode.append({'scan_type': tipo_escaneo, 'path': ruta, 'class': fila.get('class', ''), 'source_operational': fila.get('source_operational', ''), 'component_clean': fila.get('component_clean', ''), 'width': width, 'height': height, 'mode': mode, 'status': estado, 'error': error})
    if numero % 1000 == 0:
        print(f'Decodificadas {numero:,}/{len(muestra_decode):,}')

validacion_decode = pd.DataFrame(registros_decode)

validacion_decode.to_csv(SALIDA_DECODIFICACION, index=False)

print('Tipo de escaneo:', tipo_escaneo)

print('Imágenes revisadas:', len(validacion_decode))

print('Errores:', int(validacion_decode['status'].ne('ok').sum()))

print('Tiempo de decodificación (minutos):', round((time.time() - inicio) / 60, 2))

if validacion_decode['status'].ne('ok').any():
    display(validacion_decode.loc[validacion_decode['status'].ne('ok')])
    raise RuntimeError('Se detectaron imágenes con errores de decodificación.')

def desnormalizar(tensor):
    mean = torch.tensor(MEDIA_IMAGENET, dtype=tensor.dtype).view(3, 1, 1)
    std = torch.tensor(STD_IMAGENET, dtype=tensor.dtype).view(3, 1, 1)
    return torch.clamp(tensor.cpu() * std + mean, 0, 1)

def guardar_muestra(loader, ruta_salida, titulo):
    images, labels, metadata = next(iter(loader))
    n = min(16, images.shape[0])
    images = torch.stack([desnormalizar(img) for img in images[:n]])
    grid = make_grid(images, nrow=4, padding=2)
    plt.figure(figsize=(12, 12))
    plt.imshow(grid.permute(1, 2, 0).numpy())
    plt.axis('off')
    plt.title(titulo)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=160, bbox_inches='tight')
    plt.show()
    plt.close()

guardar_muestra(loaders['E1_val'], SALIDA_MUESTRA_E1, 'E1 — muestra de validación con transformación determinista')

guardar_muestra(loaders['E3_val'], SALIDA_MUESTRA_E3, 'E3 — muestra de validación con transformación determinista')

print('Muestras visuales guardadas.')

config = {'version': '1.0', 'date': datetime.now().isoformat(), 'recommended_runtime': 'GPU', 'gpu_strictly_required': False, 'detected_device': str(DEVICE), 'seed': SEMILLA, 'batch_size_validation': BATCH_SIZE_VALIDACION, 'num_workers': NUM_WORKERS, 'pin_memory': PIN_MEMORY, 'persistent_workers': PERSISTENT_WORKERS, 'quick_decode_per_stratum': VALIDACION_RAPIDA_POR_ESTRATO, 'full_decode_scan': ESCANEO_COMPLETO_DECODIFICACION, 'input_size': 224, 'normalization': {'mean': MEDIA_IMAGENET, 'std': STD_IMAGENET}, 'train_transforms': ['RandomResizedCrop_224_scale_0.80_1.00', 'RandomHorizontalFlip_p_0.50', 'RandomRotation_plus_minus_15', 'ColorJitter_0.20_0.20_0.20_0.05', 'ToTensor', 'ImageNetNormalize', 'RandomErasing_p_0.10'], 'eval_transforms': ['Resize_256', 'CenterCrop_224', 'ToTensor', 'ImageNetNormalize'], 'class_mapping_E1': mapa_e1, 'class_mapping_E3': mapa_e3, 'frozen_split_hash_manifest': HASH_ARCHIVO_SPLITS_ESPERADO}

with open(SALIDA_CONFIG, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

artefactos = {'class_mapping_E1': SALIDA_MAPA_E1, 'class_mapping_E3': SALIDA_MAPA_E3, 'dataloader_config': SALIDA_CONFIG, 'path_validation': SALIDA_RUTAS, 'batch_validation': SALIDA_BATCHES, 'decode_validation': SALIDA_DECODIFICACION, 'sample_E1': SALIDA_MUESTRA_E1, 'sample_E3': SALIDA_MUESTRA_E3}

registros_hash = []

for nombre, ruta in artefactos.items():
    registros_hash.append({'artifact': nombre, 'filename': ruta.name, 'n_bytes': ruta.stat().st_size, 'sha256': sha256_archivo(ruta)})

hashes_validacion = pd.DataFrame(registros_hash)

hashes_validacion.to_csv(SALIDA_HASHES, index=False)

hash_archivo_hashes = sha256_archivo(SALIDA_HASHES)

ficha = f"\nVALIDACIÓN DE DATALOADERS — V1\n==============================\nFecha: {datetime.now().isoformat()}\n\nENTORNO\n-------\nRecomendado: GPU.\nGPU estrictamente obligatoria: no.\nDispositivo detectado: {DEVICE}\n\nENTRADAS CONGELADAS\n-------------------\nE1:\n{ARCHIVO_E1.name}\nSHA-256:\n{HASH_E1_ESPERADO}\n\nArchivo de huellas E2-E3:\n{ARCHIVO_SPLITS_HASHES.name}\nSHA-256:\n{HASH_ARCHIVO_SPLITS_ESPERADO}\n\nRESULTADOS\n----------\nManifiestos con todas sus rutas existentes:\n{bool(validacion_rutas['all_paths_exist'].all())}\n\nDataloaders validados:\n{len(validacion_batches)}\n\nForma esperada:\n[batch, 3, 224, 224]\n\nErrores de decodificación:\n{int(validacion_decode['status'].ne('ok').sum())}\n\nTipo de escaneo:\n{tipo_escaneo}\n\nImágenes decodificadas:\n{len(validacion_decode)}\n\nMAPAS DE CLASES\n---------------\nE1:\n{json.dumps(mapa_e1, ensure_ascii=False)}\n\nE3:\n{json.dumps(mapa_e3, ensure_ascii=False)}\n\nARCHIVO DE HUELLAS\n------------------\n{SALIDA_HASHES.name}\n\nSHA-256:\n{hash_archivo_hashes}\n\nESTADO\n------\nLos dataloaders y transformaciones quedan validados para\ncomenzar el entrenamiento. Esta validación no modifica E1,\nE2 ni E3.\n".strip()

SALIDA_FICHA.write_text(ficha + '\n', encoding='utf-8')

print('=== DATALOADERS VALIDADOS ===')

display(hashes_validacion)

print('Archivo de huellas:', SALIDA_HASHES)

print('SHA-256 del archivo de huellas:', hash_archivo_hashes)

print('Ficha:', SALIDA_FICHA)
