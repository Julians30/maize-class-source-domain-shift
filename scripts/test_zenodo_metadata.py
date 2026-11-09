import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('editor',Path(__file__).with_name('zenodo_metadata.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Reply:
    status_code=200
    headers={'ETag':'"7"'}
    def __init__(self,data):self.data=data
    def json(self):return copy.deepcopy(self.data)

class Session:
    def __init__(self,record,files,legacy):
        self.record=copy.deepcopy(record);self.files=copy.deepcopy(files);self.legacy=copy.deepcopy(legacy);self.headers={};self.calls=[];self.closed=False;self.fail=False
        self.native_requests=0
    def request(self,method,url,**kwargs):
        self.calls.append((method,url,kwargs))
        if self.fail:
            r=Reply({});r.status_code=403;return r
        if '/api/records/' in url:
            self.native_requests+=1
            # Match Zenodo's real default serializer: without explicit Accept,
            # modern URLs still return the legacy schema lacking rights/pids.
            if kwargs.get('headers',{}).get('Accept')!='application/vnd.inveniordm.v1+json':
                return Reply(self.legacy)
        if url.endswith('/pids/doi'):
            assert method=='POST';self.record['pids']={'doi':{'identifier':'10.5072/test.123','provider':'datacite'}};return Reply(self.record)
        if '/deposit/' in url:return Reply(self.files if url.endswith('/files') else self.legacy)
        if method=='PUT':
            assert kwargs['headers'].get('If-Match')=='"7"'
            self.record.update(copy.deepcopy(kwargs['json']))
        return Reply(self.record)
    def close(self):self.closed=True

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'upload_state.json'
        self.creators=[{'name':f'Family{i}, Given'} for i in range(4)]
        self.prepared={'title':'A “Class–Source” benchmark','creators':self.creators}
        self.state={'deposition_id':123,'all_expected_files_verified':True,'published':False,'uploaded':{f'file{i}':{'md5':f'md5value{i}','bytes':i+1,'status':'uploaded_verified'} for i in range(31)}}
        self.path.write_text(json.dumps(self.state))
        self.files=[{'filename':k,'size':v['bytes'],'checksum':'md5:'+v['md5']} for k,v in self.state['uploaded'].items()]
        description='<p>Image-level prediction labels, preserving scientific scope.</p><p>The data/code archive is a release candidate. The 30 checkpoint binaries listed in CHECKPOINT_FILES.csv must be uploaded separately before claiming they are available.</p><p>Human-review status on 8 November 2026: 190 critical, 189 same, 1 related, 974 unreviewed.</p><p>Attribution notices distinguish component terms.</p><p>Author-added detail retained.</p>'
        self.record={'id':'123','is_published':False,'is_draft':True,'metadata':{'title':self.prepared['title'],'creators':[{'person_or_org':{'type':'personal','name':x['name']}} for x in self.creators],'description':description,'rights':[{'id':'cc-by-4.0','title':{'en':'CC BY 4.0'}}],'resource_type':{'id':'dataset','title':{'en':'Dataset'}},'publication_date':'2026-11-09','version':'1.0.0-rc4'},'pids':{},'access':{'record':'public','files':'public'},'custom_fields':{},'links':{'self_html':'https://zenodo.org/uploads/123'}}
        self.legacy={'id':123,'state':'inprogress','submitted':False,'metadata':copy.deepcopy(self.prepared)}
        self.session=Session(self.record,self.files,self.legacy)
        self.ns={'STATE_FILE':self.path,'METADATA':self.prepared}
        self.prompts=0
    def tearDown(self):self.tmp.cleanup()
    def prompt(self,message):self.prompts+=1;return 'test-only-placeholder'
    def run_editor(self):
        with contextlib.redirect_stdout(io.StringIO()):return m.edit_metadata(self.ns,123,session_factory=lambda:self.session,prompt=self.prompt)
    def test_complete_edit_and_doi(self):
        result=self.run_editor();self.assertFalse(result['published']);self.assertEqual(result['files_verified'],31);self.assertEqual(result['reserved_doi'],'10.5072/test.123')
        state=json.loads(self.path.read_text());self.assertTrue(state['metadata_updated']);self.assertTrue(state['mixed_license_scope_verified']);self.assertEqual(len(state['uploaded']),31)
        self.assertTrue(self.session.closed);self.assertNotIn('Authorization',self.session.headers)
        md=self.session.record['metadata'];self.assertIn('Author-added detail retained.',md['description']);self.assertIn('189 same',md['description']);self.assertNotIn('must be uploaded separately',md['description']);self.assertEqual(md['publication_date'],'2026-11-09');self.assertEqual(md['version'],'1.0.0-rc4')
        audit=json.loads((self.path.parent/'metadata_editor_123.json').read_text());self.assertTrue(audit['events'][0]['verified']);self.assertNotIn('test-only-placeholder',json.dumps(audit))
    def test_zenodo_legacy_default_requires_native_accept(self):
        reply=self.session.request('GET','https://zenodo.org/api/records/123/draft')
        self.assertNotIn('rights',reply.json()['metadata'])
        self.session.calls.clear()
        self.run_editor()
        self.assertGreater(self.session.native_requests,0)
        for method,url,kwargs in self.session.calls:
            expected='application/vnd.inveniordm.v1+json' if '/api/records/' in url else 'application/json'
            self.assertEqual(kwargs['headers']['Accept'],expected)
            if method=='PUT':self.assertEqual(kwargs['headers']['Content-Type'],'application/json')
    def test_no_put_before_native_rights_are_verified(self):
        self.session.record['metadata'].pop('rights')
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertTrue(all(method=='GET' for method,url,kwargs in self.session.calls))
    def test_second_run_no_duplicate_doi_or_headings(self):
        self.run_editor();first=self.session.record['metadata']['description'];self.session.closed=False;self.run_editor()
        self.assertEqual(first,self.session.record['metadata']['description']);self.assertEqual(sum(method=='POST' for method,url,kw in self.session.calls),1);self.assertEqual(len(json.loads((self.path.parent/'metadata_editor_123.json').read_text())['events']),2)
    def test_existing_doi_preserved(self):
        self.session.record['pids']={'doi':{'identifier':'10.5072/existing.999'}};r=self.run_editor();self.assertEqual(r['reserved_doi'],'10.5072/existing.999');self.assertFalse(any(method=='POST' for method,url,kw in self.session.calls))
    def test_wrong_state_id_no_token(self):
        self.state['deposition_id']=456;self.path.write_text(json.dumps(self.state))
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertEqual(self.prompts,0);self.assertEqual(self.session.calls,[])
    def test_incomplete_upload_no_token(self):
        self.state['all_expected_files_verified']=False;self.path.write_text(json.dumps(self.state))
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertEqual(self.prompts,0)
    def test_wrong_remote_hash_no_writes(self):
        self.session.files[0]['checksum']='md5:different'
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertTrue(all(method=='GET' for method,url,kw in self.session.calls))
    def test_wrong_authors_no_writes(self):
        self.session.legacy['metadata']['creators'][0]['name']='Different, Person'
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertTrue(all(method=='GET' for method,url,kw in self.session.calls))
    def test_published_remote_no_writes(self):
        self.session.legacy['submitted']=True
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertTrue(all(method=='GET' for method,url,kw in self.session.calls))
    def test_auth_failure_scrubs_header(self):
        self.session.fail=True
        with self.assertRaises(m.MetadataEditError):self.run_editor()
        self.assertNotIn('Authorization',self.session.headers);self.assertTrue(self.session.closed)
    def test_only_metadata_put_and_doi_post(self):
        self.run_editor()
        for method,url,kwargs in self.session.calls:
            if method=='PUT':self.assertEqual(url,'https://zenodo.org/api/records/123/draft')
            if method=='POST':self.assertEqual(url,'https://zenodo.org/api/records/123/draft/pids/doi')
    def test_disallowed_routes_never_sent(self):
        for method,url in [('POST','https://zenodo.org/api/deposit/depositions'),('POST','https://zenodo.org/api/records/123/draft/actions/publish'),('DELETE','https://zenodo.org/api/records/123/draft'),('PUT','https://zenodo.org/api/files/bucket/file.pt'),('GET','https://other.example/api/records/123/draft')]:
            with self.assertRaises(m.MetadataEditError):m._call(self.session,method,url)
        self.assertEqual(self.session.calls,[])
    def test_preserves_custom_rights_and_removes_expanded_fields(self):
        rights=m.mixed_rights([{'id':'mit','title':{'en':'MIT'}},{'title':{'en':'Author custom condition'},'description':{'en':'Keep this'}}]);self.assertIn({'id':'mit'},rights);self.assertIn({'title':{'en':'Author custom condition'},'description':{'en':'Keep this'}},rights)
        self.assertEqual(len([x for x in rights if x.get('id')=='mit']),1)
    def test_unrecognized_edited_stale_inventory_stops(self):
        with self.assertRaises(m.MetadataEditError):m.formatted_description('<div>The models must be uploaded separately before claiming they are available.</div>')
    def test_description_idempotence(self):
        s=m.formatted_description(self.record['metadata']['description']);self.assertEqual(s,m.formatted_description(s))

if __name__=='__main__':unittest.main(verbosity=2)
