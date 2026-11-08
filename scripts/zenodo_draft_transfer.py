"""Resume a known, unpublished Zenodo draft from an existing Colab runtime.

No credentials, study-private file paths or draft identifiers are stored here.
The caller must explicitly supply the already recorded deposition identifier.
This module never creates, publishes, deletes or discards a deposition.
"""
from pathlib import Path
from urllib.parse import urlsplit, quote
import hashlib
import html
import json
import re
import unicodedata


class DraftRecoveryError(RuntimeError):
    pass


def canonical_title(value):
    """Allow only HTML, Unicode, quotation and whitespace presentation changes."""
    value = unicodedata.normalize('NFKC', html.unescape(str(value or '')))
    value = value.translate(str.maketrans({
        '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2013': '-',
        '\u2014': '-', '\u2212': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u00a0': ' ',
    }))
    return re.sub(r'\s+', ' ', value).strip()


def _api(session, method, url, **kwargs):
    parts = urlsplit(url)
    permitted = (
        parts.scheme == 'https' and parts.netloc == 'zenodo.org'
        and not parts.query and not parts.fragment
        and (re.fullmatch(r'/api/deposit/depositions/\d+(?:/files)?', parts.path)
             or re.fullmatch(r'/api/files/[A-Za-z0-9-]+(?:/[^/]+)?', parts.path))
    )
    if not permitted or method not in {'GET', 'PUT'}:
        raise DraftRecoveryError('Solicitud bloqueada: solo se permite leer o cargar en el borrador guardado.')
    try:
        response = session.request(method, url, allow_redirects=False, timeout=(30, 900), **kwargs)
    except Exception:
        raise DraftRecoveryError('La conexión se interrumpió. Reejecuta esta recuperación para comprobar lo ya recibido; no se creó otro borrador.') from None
    if response.status_code not in {200, 201, 202}:
        raise DraftRecoveryError(f'Zenodo respondió HTTP {response.status_code}. Se detuvo sin imprimir credenciales.')
    try:
        return response.json()
    except Exception:
        raise DraftRecoveryError('Zenodo no devolvió una respuesta JSON válida.') from None


def _save(path, data):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    temporary.replace(path)


def _assert_draft(record, expected_id):
    if not isinstance(record, dict) or str(record.get('id')) != str(expected_id):
        raise DraftRecoveryError('El identificador devuelto no coincide con el borrador guardado.')
    if record.get('submitted') or record.get('state') in {'done', 'published', 'error'} or record.get('is_published'):
        raise DraftRecoveryError('El registro no es un borrador editable. No se modificó.')


def _files(session, record_id):
    rows = _api(session, 'GET', f'https://zenodo.org/api/deposit/depositions/{record_id}/files')
    if not isinstance(rows, list):
        raise DraftRecoveryError('El listado de archivos no tiene el formato esperado.')
    result = {}
    for row in rows:
        name = row.get('filename') or row.get('key') or row.get('name')
        if not isinstance(name, str) or name in result:
            raise DraftRecoveryError('El listado remoto contiene nombres ausentes o repetidos.')
        result[name] = row
    return result


def _md5(row):
    return str(row.get('checksum', '')).lower().removeprefix('md5:')


def _size(row):
    try:
        return int(row.get('filesize', row.get('size', -1)))
    except (ValueError, TypeError):
        return -1


def _creator_names(metadata):
    rows = metadata.get('creators', [])
    if not isinstance(rows, list):
        return None
    return [canonical_title(row.get('name', '')) for row in rows if isinstance(row, dict)]


def prepare_existing_draft(session, state, metadata, state_file, expected_id):
    """Read the full saved draft, repair only its verified empty staging record.

    POST responses may be partial and title presentation can be normalized by
    the service. A substantive mismatch is never silently accepted. Repair is
    limited to the caller-pinned unpublished ID, no remote files, no recorded
    uploads, and matching creators (or a genuinely empty title/creator record).
    A before/after metadata snapshot is retained locally without credentials.
    """
    if str(state.get('deposition_id')) != str(expected_id):
        raise DraftRecoveryError('El ID solicitado difiere del estado guardado. No se creó ni modificó ningún depósito.')
    if state.get('creation_attempt_started'):
        raise DraftRecoveryError('La creación previa tiene estado incierto; no se hará otra creación ni una reparación automática.')
    if not isinstance(metadata, dict) or not metadata.get('title') or not _creator_names(metadata):
        raise DraftRecoveryError('Faltan el título o los autores preparados.')
    url = f'https://zenodo.org/api/deposit/depositions/{int(expected_id)}'
    record = _api(session, 'GET', url)
    _assert_draft(record, expected_id)
    remote_metadata = record.get('metadata') or {}
    if not isinstance(remote_metadata, dict):
        raise DraftRecoveryError('El formato de metadatos devuelto no es válido.')
    current_title = remote_metadata.get('title') or record.get('title') or ''
    files = _files(session, expected_id)
    expected_canonical = canonical_title(metadata['title'])
    if canonical_title(current_title) != expected_canonical:
        remote_names = _creator_names(remote_metadata)
        expected_names = _creator_names(metadata)
        empty_record = not canonical_title(current_title) and remote_names == []
        known_creators = remote_names == expected_names
        if files or state.get('uploaded') or not (empty_record or known_creators):
            print('Título esperado:', metadata['title'])
            print('Título devuelto:', current_title or '(vacío)')
            raise DraftRecoveryError('La discrepancia requiere revisión: no se sobrescribió un borrador con archivos o autores diferentes.')
        snapshot_path = Path(state_file).parent / f'metadata_recovery_{int(expected_id)}.json'
        if not snapshot_path.exists():
            _save(snapshot_path, {'deposition_id': int(expected_id), 'before': remote_metadata, 'prepared': metadata})
        state['metadata_repair_attempted'] = True
        _save(state_file, state)
        _api(session, 'PUT', url, json={'metadata': metadata})
        record = _api(session, 'GET', url)
        _assert_draft(record, expected_id)
        after = record.get('metadata') or {}
        current_title = after.get('title') or record.get('title') or ''
        if canonical_title(current_title) != expected_canonical or _creator_names(after) != expected_names:
            print('Título esperado:', metadata['title'])
            print('Título devuelto:', current_title or '(vacío)')
            raise DraftRecoveryError('La lectura posterior no confirma el título y los autores; no se inició la transferencia.')
        snapshot = json.loads(snapshot_path.read_text())
        snapshot['after'] = after
        _save(snapshot_path, snapshot)
        state['metadata_repair_verified'] = True
    elif _creator_names(remote_metadata) != _creator_names(metadata):
        raise DraftRecoveryError('El título coincide, pero los autores difieren. No se inició la transferencia.')
    bucket = record.get('links', {}).get('bucket')
    if not isinstance(bucket, str):
        raise DraftRecoveryError('El borrador no devolvió un bucket de subida.')
    parts = urlsplit(bucket)
    if parts.scheme != 'https' or parts.netloc != 'zenodo.org' or parts.query or parts.fragment or not re.fullmatch(r'/api/files/[A-Za-z0-9-]+', parts.path):
        raise DraftRecoveryError('El destino de subida no es un bucket válido de Zenodo.')
    state['metadata_verified'] = True
    _save(state_file, state)
    print('Borrador verificado:', expected_id)
    print('Título y autores comprobados; se conserva el mismo depósito.')
    return record, bucket, files


def resume_upload(namespace, expected_deposition_id):
    """Resume after the original Colab metadata check without another token."""
    required = ['SESSION', 'METADATA', 'STATE_FILE', 'ITEMS', 'DIGESTS']
    missing = [key for key in required if key not in namespace]
    if missing:
        raise DraftRecoveryError('La sesión original no conserva sus variables. No reinicies el entorno ni crees otro depósito; informa de este mensaje.')
    session = namespace['SESSION']
    state_file = Path(namespace['STATE_FILE'])
    if not state_file.is_file():
        raise DraftRecoveryError('No está el estado guardado; esta recuperación no crea depósitos.')
    state = json.loads(state_file.read_text())
    metadata = namespace['METADATA']
    items, digests = namespace['ITEMS'], namespace['DIGESTS']
    if not isinstance(items, list) or len(items) != 31 or len({item['name'] for item in items}) != 31:
        raise DraftRecoveryError('El plan debe contener exactamente el ZIP y los 30 checkpoints, sin nombres repetidos.')
    for item in items:
        path = Path(item['path'])
        digest = digests.get(item['name'])
        if not path.is_file() or path.stat().st_size != int(item['bytes']) or not isinstance(digest, (list, tuple)) or len(digest) != 2 or digest[0] != item['sha256']:
            raise DraftRecoveryError('Falta una comprobación local válida. No se cambió el plan ni se ejecutó entrenamiento.')
    record, bucket, existing = prepare_existing_draft(session, state, metadata, state_file, int(expected_deposition_id))
    namespace.update(STATE=state, RECORD=record, BUCKET=bucket)
    for i, item in enumerate(items, 1):
        name = item['name']
        digest = digests[name]
        print(f'{i}/31: {name}', flush=True)
        if name in existing:
            row = existing[name]
            if _md5(row) != digest[1] or _size(row) != int(item['bytes']):
                raise DraftRecoveryError('Hay un archivo remoto incompleto o diferente. Se detuvo sin eliminarlo: ' + name)
            status = 'already_verified'
        else:
            with Path(item['path']).open('rb') as file:
                row = _api(session, 'PUT', bucket.rstrip('/') + '/' + quote(name, safe=''), data=file, headers={'Content-Type': 'application/octet-stream'})
            if _md5(row) != digest[1] or _size(row) != int(item['bytes']):
                raise DraftRecoveryError('No coincide la verificación remota del archivo: ' + name)
            existing[name] = row
            status = 'uploaded_verified'
        state.setdefault('uploaded', {})[name] = {'status': status, 'sha256': digest[0], 'md5': digest[1], 'bytes': int(item['bytes'])}
        _save(state_file, state)
        print('  ' + status, flush=True)
    final_files = _files(session, int(expected_deposition_id))
    for item in items:
        row = final_files.get(item['name'], {})
        if _md5(row) != digests[item['name']][1] or _size(row) != int(item['bytes']):
            raise DraftRecoveryError('La comprobación final está incompleta: ' + item['name'])
    final_record = _api(session, 'GET', f'https://zenodo.org/api/deposit/depositions/{int(expected_deposition_id)}')
    _assert_draft(final_record, int(expected_deposition_id))
    final_metadata = final_record.get('metadata') or {}
    if canonical_title(final_metadata.get('title') or final_record.get('title')) != canonical_title(metadata['title']) or _creator_names(final_metadata) != _creator_names(metadata):
        raise DraftRecoveryError('El título o los autores cambiaron durante la transferencia. No se publica el depósito.')
    state.update(all_expected_files_verified=True, published=False, extra_remote_files=sorted(set(final_files) - {x['name'] for x in items}))
    _save(state_file, state)
    namespace.update(STATE=state, FINAL_RECORD=final_record)
    session.close()
    session.headers.pop('Authorization', None)
    print('BORRADOR COMPLETO: los 31 archivos esperados están verificados. NO PUBLICADO.')
    print('Revisión:', final_record.get('links', {}).get('html', 'Abre My dashboard en Zenodo'))
    return state
