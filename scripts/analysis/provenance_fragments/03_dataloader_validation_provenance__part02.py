validacion_rutas = pd.DataFrame(registros_rutas)

display(validacion_rutas)

validacion_rutas.to_csv(SALIDA_RUTAS, index=False)

if not validacion_rutas['all_paths_exist'].all():
    raise FileNotFoundError('Existen rutas faltantes. No se debe iniciar el entrenamiento.')

print('Todas las rutas existen.')

MEDIA_IMAGENET = [0.485, 0.456, 0.406]

STD_IMAGENET = [0.229, 0.224, 0.225]

transform_train = transforms.Compose([transforms.RandomResizedCrop(224, scale=(0.8, 1.0), interpolation=InterpolationMode.BICUBIC), transforms.RandomHorizontalFlip(p=0.5), transforms.RandomRotation(degrees=15, interpolation=InterpolationMode.BILINEAR, fill=0), transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05), transforms.ToTensor(), transforms.Normalize(mean=MEDIA_IMAGENET, std=STD_IMAGENET), transforms.RandomErasing(p=0.1, scale=(0.02, 0.1), ratio=(0.3, 3.3), value=0)])

transform_eval = transforms.Compose([transforms.Resize(256, interpolation=InterpolationMode.BICUBIC), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean=MEDIA_IMAGENET, std=STD_IMAGENET)])

print('Transformaciones de entrenamiento y evaluación definidas.')

class MaizeManifestDataset(Dataset):

    def __init__(self, dataframe, class_to_idx, transform=None, label_column='class', return_metadata=True):
        self.df = dataframe.reset_index(drop=True).copy()
        self.class_to_idx = dict(class_to_idx)
        self.transform = transform
        self.label_column = label_column
        self.return_metadata = return_metadata
        required = {'path', self.label_column}
        missing = required - set(self.df.columns)
        if missing:
            raise KeyError(f'Faltan columnas requeridas: {sorted(missing)}')
        unknown = sorted(set(self.df[self.label_column].astype(str)) - set(self.class_to_idx))
        if unknown:
            raise ValueError(f'Etiquetas sin índice: {unknown}')

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        row = self.df.iloc[index]
        path = str(row['path'])
        label_name = str(row[self.label_column])
        label = int(self.class_to_idx[label_name])
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image)
                image = image.convert('RGB')
                image_size_original = image.size
                if self.transform is not None:
                    image = self.transform(image)
        except Exception as exc:
            raise RuntimeError(f'Error al abrir o transformar la imagen:\n{path}') from exc
        if not self.return_metadata:
            return (image, label)
        metadata = {'path': path, 'label_name': label_name, 'original_width': int(image_size_original[0]), 'original_height': int(image_size_original[1])}
        for columna in ['split', 'evaluation_role', 'component_clean', 'source_operational', 'global_group_id']:
            if columna in self.df.columns:
                metadata[columna] = str(row[columna])
        return (image, label, metadata)

print('Clase Dataset creada.')

def seleccionar(df, columna, valor):
    if columna not in df.columns:
        raise KeyError(f'Falta la columna {columna}.')
    return df.loc[df[columna].astype(str).eq(str(valor))].copy()

datasets = {'E1_train': MaizeManifestDataset(seleccionar(e1, 'split', 'train'), mapa_e1, transform=transform_train), 'E1_val': MaizeManifestDataset(seleccionar(e1, 'split', 'val'), mapa_e1, transform=transform_eval), 'E1_test': MaizeManifestDataset(seleccionar(e1, 'split', 'test'), mapa_e1, transform=transform_eval), 'E3_train': MaizeManifestDataset(seleccionar(e3, 'split', 'train'), mapa_e3, transform=transform_train), 'E3_val': MaizeManifestDataset(seleccionar(e3, 'split', 'val'), mapa_e3, transform=transform_eval), 'E3_test': MaizeManifestDataset(seleccionar(e3, 'split', 'test'), mapa_e3, transform=transform_eval), 'E2A_external': MaizeManifestDataset(seleccionar(e2a, 'evaluation_role', 'external_component_test'), mapa_e3, transform=transform_eval), 'E2B_external': MaizeManifestDataset(seleccionar(e2b, 'evaluation_role', 'external_component_test'), mapa_e3, transform=transform_eval)}

def worker_init_fn(worker_id):
    worker_seed = SEMILLA + worker_id
    random.seed(worker_seed)
    np.random.seed(worker_seed)
    torch.manual_seed(worker_seed)

generador = torch.Generator()

generador.manual_seed(SEMILLA)

loaders = {}

for nombre, dataset in datasets.items():
    es_train = nombre.endswith('_train')
    loaders[nombre] = DataLoader(dataset, batch_size=BATCH_SIZE_VALIDACION, shuffle=es_train, num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY, persistent_workers=PERSISTENT_WORKERS, worker_init_fn=worker_init_fn, generator=generador if es_train else None, drop_last=False)

print('Datasets y dataloaders construidos:')

for nombre, dataset in datasets.items():
    print(f'{nombre}: {len(dataset):,} imágenes')

registros_batch = []

for nombre, loader in loaders.items():
    inicio = time.time()
    images, labels, metadata = next(iter(loader))
    tiempo_carga = time.time() - inicio
    if images.ndim != 4:
        raise ValueError(f'{nombre}: tensor con dimensión inesperada {images.shape}.')
    if tuple(images.shape[1:]) != (3, 224, 224):
        raise ValueError(f'{nombre}: se esperaba [3,224,224] y se obtuvo {tuple(images.shape[1:])}.')
    if not torch.isfinite(images).all():
        raise ValueError(f'{nombre}: el lote contiene NaN o infinito.')
    images_device = images.to(DEVICE, non_blocking=PIN_MEMORY)
    labels_device = labels.to(DEVICE, non_blocking=PIN_MEMORY)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    registros_batch.append({'loader': nombre, 'dataset_size': len(loader.dataset), 'batch_size_observed': int(images.shape[0]), 'channels': int(images.shape[1]), 'height': int(images.shape[2]), 'width': int(images.shape[3]), 'label_min': int(labels.min().item()), 'label_max': int(labels.max().item()), 'tensor_min': float(images.min().item()), 'tensor_max': float(images.max().item()), 'tensor_mean': float(images.mean().item()), 'tensor_std': float(images.std().item()), 'all_finite': bool(torch.isfinite(images).all().item()), 'device_transfer': str(images_device.device), 'load_seconds_first_batch': round(tiempo_carga, 4)})
    del images_device, labels_device

validacion_batches = pd.DataFrame(registros_batch)

display(validacion_batches)

validacion_batches.to_csv(SALIDA_BATCHES, index=False)

assert validacion_batches['all_finite'].all()

assert validacion_batches['channels'].eq(3).all()

assert validacion_batches['height'].eq(224).all()

assert validacion_batches['width'].eq(224).all()

print('Todos los lotes fueron validados.')

def muestra_estratificada(df, n_por_estrato=3):
    columnas = ['class']
    if 'source_operational' in df.columns:
        columnas.append('source_operational')
    if 'split' in df.columns:
        columnas.append('split')
    elif 'evaluation_role' in df.columns:
        columnas.append('evaluation_role')
    partes = []
    for clave, bloque in df.groupby(columnas, dropna=False, sort=True):
        bloque = bloque.sort_values('path', kind='mergesort')
        partes.append(bloque.head(min(n_por_estrato, len(bloque))))
    return pd.concat(partes, ignore_index=True).drop_duplicates('path')
