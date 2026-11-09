"""Format a verified unpublished Zenodo draft; never create or publish records.

Uses the InvenioRDM draft API for mixed licenses and DOI reservation. Local
state and before/after snapshots contain metadata and checksums, never tokens.
"""
from copy import deepcopy
from datetime import datetime, timezone
from getpass import getpass
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import unicodedata


class MetadataEditError(RuntimeError):
    pass


NOTICES = 'https://github.com/Julians30/maize-class-source-domain-shift/blob/main/PRETRAINED_MODEL_NOTICES.md'
SCOPE_TITLE = 'Component-specific license scope for data, code and model checkpoints'
SCOPE_DESCRIPTION = (
    'The listed licenses apply to their respective components, not as alternative '
    'licenses for every file. CC BY 4.0 covers original derived data and documentation; '
    'MIT covers original software and applicable Swin components; Apache-2.0 applies '
    'to the identified ViT pretrained components. MobileViT components retain the '
    'Apple CVNets terms, and torchvision model assets retain applicable upstream '
    'model/data terms. Preserve the component notices documented in the archive. '
    'These declarations do not grant rights to original source photographs or '
    'establish completed clearance of every third-party asset.'
)
INVENTORY_PARAGRAPH = (
    'This record includes the data/code archive and all 30 selected model checkpoints '
    'listed in CHECKPOINT_FILES.csv, uploaded as separate files. All 31 files were '
    'verified after upload using file sizes and checksums. CC BY 4.0 applies to '
    'original derived data and documentation; original software and third-party '
    'components retain their applicable terms, as detailed in the archive\u2019s '
    'license and pretrained-model notices.'
)
COMPONENT_HTML = (
    '<p><strong>Licenses by component</strong></p><ul>'
    '<li>Original derived data and documentation: CC BY 4.0.</li>'
    '<li>Original software: MIT.</li>'
    '<li>ViT pretrained components: Apache-2.0; Swin pretrained components: MIT.</li>'
    '<li>MobileViT and torchvision components retain their applicable upstream '
    'terms. See the archive\u2019s pretrained-model notices and '
    '<a href="' + NOTICES + '">the corresponding repository notices</a>.</li>'
    '<li>Source photographs, private reviewer identities and reviewer '
    'correspondence are excluded.</li></ul>'
)


def plain(value):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]*>', ' ', str(value or '')))).strip()


def canonical(value):
    value = unicodedata.normalize('NFKC', plain(value))
    return value.translate(str.maketrans({'\u2013':'-', '\u2014':'-', '\u201c':'"', '\u201d':'"', '\u2019':"'"}))


def formatted_description(current):
    """Keep scientific paragraphs and user additions; update only old inventory."""
    if not isinstance(current, str) or not current.strip():
        raise MetadataEditError('La descripción está vacía; no se sustituye por un texto inferido.')
    result = current
    saw_inventory = False
    def rewrite(match):
        nonlocal saw_inventory
        paragraph = match.group(0)
        text = plain(paragraph)
        heading = None
        if text.startswith('Image-level prediction labels,'):
            heading = 'Study scope and design'
        elif text.startswith('The data/code archive is a release candidate.') or text.startswith('This record includes the data/code archive and all 30 selected model checkpoints'):
            heading = 'Contents and file verification'
            paragraph = '<p>' + INVENTORY_PARAGRAPH + '</p>'
            saw_inventory = True
        elif text.startswith('Human-review status on '):
            heading = 'Human-review scope'
        elif text.startswith('Attribution notices distinguish '):
            heading = 'Provenance and attribution'
        if heading and '<strong>' + heading + '</strong>' not in current:
            paragraph = '<p><strong>' + heading + '</strong></p>' + paragraph
        return paragraph
    result = re.sub(r'<p\b[^>]*>.*?</p>', rewrite, result, flags=re.I | re.S)
    if not saw_inventory:
        # Unrecognized user edits are retained instead of being overwritten.
        if 'must be uploaded separately before claiming they are available' in plain(result):
            raise MetadataEditError('El párrafo de archivos fue modificado y requiere revisión; se conserva el texto existente.')
        if INVENTORY_PARAGRAPH not in plain(result):
            result += '<p><strong>Contents and file verification</strong></p><p>' + INVENTORY_PARAGRAPH + '</p>'
    if '<strong>Licenses by component</strong>' not in result:
        result += COMPONENT_HTML
    return result


def mixed_rights(existing):
    """Preserve custom licenses; standard vocabulary entries need only their ID."""
    if not isinstance(existing, list):
        raise MetadataEditError('El formato de licencias no es el esperado.')
    result = []
    seen = set()
    for row in existing:
        if not isinstance(row, dict):
            raise MetadataEditError('Hay una licencia con formato no reconocido.')
        if row.get('id'):
            if row['id'] not in seen:
                result.append({'id': row['id']});seen.add(row['id'])
        else:
            cleaned = {key:deepcopy(row[key]) for key in ['title','description','link'] if key in row}
            if not cleaned.get('title'):
                raise MetadataEditError('Una licencia personalizada carece de título.')
            result.append(cleaned)
    for identifier in ['cc-by-4.0', 'mit', 'apache-2.0']:
        if identifier not in seen:
            result.append({'id':identifier});seen.add(identifier)
    if not any(row.get('title', {}).get('en') == SCOPE_TITLE for row in result):
        result.append({'title':{'en':SCOPE_TITLE},'description':{'en':SCOPE_DESCRIPTION},'link':NOTICES})
    return result


def _save(path, data):
    path = Path(path);temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2));temporary.replace(path)


def _call(session, method, url, **kwargs):
    parts = urlsplit(url)
    route = parts.path
    legal = parts.scheme == 'https' and parts.netloc == 'zenodo.org' and not parts.query and not parts.fragment
    legal = legal and (
        (method == 'GET' and re.fullmatch(r'/api/deposit/depositions/\d+(?:/files)?', route))
        or (method in {'GET','PUT'} and re.fullmatch(r'/api/records/\d+/draft', route))
        or (method == 'POST' and re.fullmatch(r'/api/records/\d+/draft/pids/doi', route))
    )
    if not legal:
        raise MetadataEditError('Solicitud bloqueada: esta celda solo edita metadatos de un borrador existente.')
    headers = dict(kwargs.pop('headers', {}) or {})
    # Zenodo overrides application/json with its legacy output serializer even
    # on modern /records routes. Explicit content negotiation is required to
    # receive metadata.rights, native creators and pids without losing fields.
    headers['Accept'] = ('application/vnd.inveniordm.v1+json'
                         if route.startswith('/api/records/') else 'application/json')
    if method == 'PUT':
        headers.setdefault('Content-Type', 'application/json')
    try:
        response = session.request(method, url, allow_redirects=False, timeout=(30,120), headers=headers, **kwargs)
    except Exception:
        raise MetadataEditError('La conexión se interrumpió. No se creó ni publicó otro depósito; conserva el estado y vuelve a comprobarlo.') from None
    if response.status_code not in {200,201,202}:
        fields = []
        try:
            errors = response.json().get('errors', [])
            if isinstance(errors, list):
                fields = [row.get('field') for row in errors if isinstance(row, dict)
                          and isinstance(row.get('field'), str)
                          and re.fullmatch(r'[A-Za-z0-9_.\[\]-]{1,160}', row['field'])]
        except Exception:
            pass
        detail = (' Campos señalados por la API: ' + ', '.join(fields[:8]) + '.') if fields else ''
        raise MetadataEditError(f'Zenodo respondió HTTP {response.status_code} durante la edición.' + detail + ' No se imprimieron credenciales ni se publicaron archivos.')
    try:
        return response.json(), response.headers.get('ETag')
    except Exception:
        raise MetadataEditError('La respuesta de Zenodo no tiene el formato JSON esperado.') from None


def _unpublished(record, identifier):
    if str(record.get('id')) != str(identifier):
        raise MetadataEditError('El ID devuelto no corresponde al borrador solicitado.')
    if record.get('submitted') or record.get('is_published') or record.get('state') in {'done','published','error'} or record.get('is_draft') is False:
        raise MetadataEditError('El registro no es un borrador editable; no se modificó.')


def _check_files(rows, state):
    if not isinstance(rows, list) or len(rows) != 31:
        raise MetadataEditError('El borrador no contiene exactamente los 31 archivos verificados.')
    found = {}
    for row in rows:
        name = row.get('filename') or row.get('key') or row.get('name')
        if name in found:
            raise MetadataEditError('El listado remoto repite un nombre de archivo.')
        found[name] = row
    if set(found) != set(state['uploaded']):
        raise MetadataEditError('Los nombres remotos difieren del registro verificado.')
    for name, expected in state['uploaded'].items():
        row = found[name]
        checksum = str(row.get('checksum','')).lower().removeprefix('md5:')
        if checksum != expected['md5'] or int(row.get('filesize',row.get('size',-1))) != int(expected['bytes']):
            raise MetadataEditError('La comprobación remota difiere para un archivo; no se editaron sus bytes: ' + name)


def _clean_vocabularies(metadata):
    """Strip expanded vocabulary display fields from write payloads."""
    for key in ['resource_type', 'languages']:
        value = metadata.get(key)
        if isinstance(value,dict) and value.get('id'):metadata[key]={'id':value['id']}
        elif isinstance(value,list):metadata[key]=[{'id':row['id']} if row.get('id') else row for row in value]
    for row in metadata.get('related_identifiers',[]):
        for key in ['relation_type','resource_type']:
            if isinstance(row.get(key),dict) and row[key].get('id'):row[key]={'id':row[key]['id']}
    for row in metadata.get('dates',[]):
        if isinstance(row.get('type'),dict) and row['type'].get('id'):row['type']={'id':row['type']['id']}
    return metadata


def _doi(record):
    value = record.get('pids',{}).get('doi',{}).get('identifier')
    return value.strip() if isinstance(value,str) else ''


def _revision_header(record, etag):
    """Invenio returns a quoted ETag but parses request If-Match as an int."""
    revision = record.get('revision_id')
    if revision is not None:
        if isinstance(revision, bool) or not re.fullmatch(r'[0-9]+', str(revision)):
            raise MetadataEditError('La revisión del borrador no tiene el formato numérico esperado.')
        revision = str(int(revision))
    from_etag = None
    if etag:
        match = re.fullmatch(r'(?:W/)?"([0-9]+)"|([0-9]+)', str(etag).strip())
        if not match:
            raise MetadataEditError('La cabecera de versión no tiene un formato reconocido; no se guarda sin control de concurrencia.')
        from_etag = str(int(match.group(1) or match.group(2)))
    if revision is not None and from_etag is not None and revision != from_etag:
        raise MetadataEditError('La revisión y la cabecera de versión no coinciden; vuelve a leer el borrador antes de guardar.')
    version = revision if revision is not None else from_etag
    if version is None:
        raise MetadataEditError('Zenodo no devolvió una revisión que permita guardar con control de concurrencia.')
    return {'If-Match': version}


def edit_metadata(namespace, expected_id, session_factory=None, prompt=getpass):
    """One Colab call: authorize, format, reserve DOI, verify, save audit."""
    if 'STATE_FILE' not in namespace:
        raise MetadataEditError('Abre esta celda en el mismo notebook de Colab que completó la subida; falta su ruta de progreso.')
    state_file = Path(namespace['STATE_FILE'])
    if not state_file.is_file():raise MetadataEditError('No se encuentra el registro de subida.')
    state = json.loads(state_file.read_text())
    if str(state.get('deposition_id')) != str(expected_id) or not state.get('all_expected_files_verified') or len(state.get('uploaded',{})) != 31 or state.get('published'):
        raise MetadataEditError('El estado no confirma este borrador completo de 31 archivos; no se solicita el token ni se escribe en Zenodo.')
    prepared = namespace.get('METADATA',{})
    if not prepared.get('title') or len(prepared.get('creators',[])) != 4:
        raise MetadataEditError('Faltan los metadatos preparados con los cuatro autores.')
    if session_factory is None:
        import requests
        session_factory = requests.Session
    session = session_factory()
    session.headers.update({'User-Agent':'MaizeDraftMetadata/1.0 (+https://github.com/Julians30/maize-class-source-domain-shift)'})
    token = prompt('Pega el token de Zenodo aquí (entrada oculta): ').strip()
    if not token:
        session.close()
        raise MetadataEditError('No se proporcionó token; no se modificó el borrador.')
    session.headers['Authorization']='Bearer '+token
    del token
    legacy = f'https://zenodo.org/api/deposit/depositions/{int(expected_id)}'
    native = f'https://zenodo.org/api/records/{int(expected_id)}/draft'
    try:
        legacy_record,_ = _call(session,'GET',legacy);_unpublished(legacy_record,expected_id)
        lm=legacy_record.get('metadata',{})
        if canonical(lm.get('title')) != canonical(prepared['title']) or [canonical(x.get('name')) for x in lm.get('creators',[])] != [canonical(x.get('name')) for x in prepared['creators']]:
            raise MetadataEditError('El título o los autores no coinciden con el depósito preparado; no se modificó.')
        files,_ = _call(session,'GET',legacy+'/files');_check_files(files,state)
        before,etag = _call(session,'GET',native);_unpublished(before,expected_id)
        if not isinstance(before.get('metadata',{}).get('rights'),list):
            raise MetadataEditError('La API no devuelve la lista de licencias mixtas esperada; no se escribió una licencia inferida.')
        audit_path=state_file.parent/f'metadata_editor_{int(expected_id)}.json'
        audit=json.loads(audit_path.read_text()) if audit_path.exists() else {'deposition_id':int(expected_id),'events':[]}
        event={'before':{key:deepcopy(before[key]) for key in ['metadata','pids','access','custom_fields'] if key in before},'files_verified':31,'started_at':datetime.now(timezone.utc).isoformat()}
        audit['events'].append(event);_save(audit_path,audit)
        if not _doi(before):
            _call(session,'POST',native+'/pids/doi')
            before,etag=_call(session,'GET',native);_unpublished(before,expected_id)
        reserved=_doi(before)
        if not re.fullmatch(r'10\.\d{4,9}/[^\s?#]+',reserved):
            raise MetadataEditError('La respuesta no confirma un DOI reservado; no se inventó ningún identificador.')
        metadata=_clean_vocabularies(deepcopy(before['metadata']))
        metadata['description']=formatted_description(metadata.get('description'))
        metadata['rights']=mixed_rights(metadata.get('rights',[]))
        payload={'metadata':metadata}
        for key in ['pids','access','custom_fields']:
            if key in before:payload[key]=deepcopy(before[key])
        headers=_revision_header(before,etag)
        _call(session,'PUT',native,json=payload,headers=headers)
        after,_=_call(session,'GET',native);_unpublished(after,expected_id)
        final=after.get('metadata',{})
        if canonical(final.get('title')) != canonical(before['metadata'].get('title')) or final.get('creators') != before['metadata'].get('creators'):
            raise MetadataEditError('La lectura posterior no conserva título y autores; revisa el registro de cambios antes de continuar.')
        if canonical(final.get('description')) != canonical(metadata['description']):
            raise MetadataEditError('La descripción devuelta difiere del texto preparado; se guardó la evidencia para revisarla.')
        ids={x.get('id') for x in final.get('rights',[]) if x.get('id')}
        if not {'cc-by-4.0','mit','apache-2.0'}.issubset(ids) or not any(x.get('title',{}).get('en')==SCOPE_TITLE for x in final.get('rights',[])):
            raise MetadataEditError('La lectura posterior no confirma las licencias por componente.')
        if _doi(after)!=reserved:raise MetadataEditError('El DOI cambió durante la edición; se detuvo sin publicar.')
        final_files,_=_call(session,'GET',legacy+'/files');_check_files(final_files,state)
        event.update(after={key:deepcopy(after[key]) for key in ['metadata','pids','access','custom_fields'] if key in after},verified=True,reserved_doi=reserved,finished_at=datetime.now(timezone.utc).isoformat());_save(audit_path,audit)
        state.update(metadata_updated=True,reserved_doi=reserved,doi_status='reserved_unpublished',license_ids=sorted(ids),mixed_license_scope_verified=True,published=False)
        _save(state_file,state);namespace['FINAL_RECORD_METADATA']=after
        print('METADATOS ACTUALIZADOS Y VERIFICADOS.')
        print('31/31 archivos conservados; no se repitió la subida.')
        print('Descripción organizada, autores conservados y licencias por componente declaradas.')
        print('DOI reservado:',reserved,'(todavía no registrado públicamente).')
        print('Revisión:',after.get('links',{}).get('self_html','Abre el mismo borrador en Zenodo.'))
        print('BORRADOR SIN PUBLICAR. La declaración de licencias no sustituye la revisión de derechos de terceros.')
        return {'deposition_id':int(expected_id),'reserved_doi':reserved,'metadata_verified':True,'files_verified':31,'published':False}
    finally:
        session.headers.pop('Authorization',None);session.close()
