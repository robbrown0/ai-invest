"""Actual isolated mTLS/HTTP, protected file fixtures, fake broker/database.

No shared journal, real account, production TLS key or host runtime secret access.
"""
import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch,AsyncMock
from uuid import UUID,uuid4

sys.path[:0]=['/opt/ai-invest/backend','/opt/ai-invest/execution']
from aiohttp import web,ClientSession,ClientTimeout,TCPConnector
from multidict import CIMultiDict
from ai_invest_execution.web_gateway import Gateway,application,server_tls,policy,encrypted_mounts
from ai_invest_execution.web_store import FileVault,WebStore,Refused
from ai_invest_execution.web_broker import PaperWebReader
from ai_invest_execution.alpaca_paper import PaperCredentials

KEY='PUBLIC_SYNTHETIC_PAPER_KEY'
VALUE='PUBLIC_SYNTHETIC_PAPER_VALUE'
OTHER='PUBLIC_SYNTHETIC_REPLACEMENT'
ACCOUNT=UUID(int=400)


class Store:
    tenant=UUID(int=100)
    def __init__(self): self.data={};self.events=[];self.fail_save=False
    async def rows(self): return list(deepcopy(self.data).values())
    async def get(self,identifier):
        if identifier not in self.data: raise Refused()
        return deepcopy(self.data[identifier])
    async def save(self,identifier,account,version,snapshot,actor,kind):
        if self.fail_save: raise Refused()
        self.data[identifier]={'id':identifier,'broker_account_id':account,'credential_version':version,
            'snapshot':snapshot,'state':'CONNECTED','updated_at':datetime.now(timezone.utc)}
        self.events.append(kind)
    async def disconnect(self,identifier,actor):
        self.data[identifier].update(state='DISCONNECTED',credential_version=None,snapshot={})
        self.events.append('disconnected')
    async def refreshed(self,identifier,snapshot,actor):
        self.data[identifier]['snapshot']=snapshot
        self.events.append('refreshed')


class Broker:
    def __init__(self,credentials,*scope): self.credentials=credentials
    async def account(self,expected=None):
        if self.credentials.secret_key not in (VALUE,OTHER) or expected not in (None,ACCOUNT): raise Refused()
        return ACCOUNT,{'account_id':str(ACCOUNT),'cash':'200','equity':'201','observed_at':'2026-01-01T00:00:00+00:00'}
    async def dashboard(self,expected):
        _,value=await self.account(expected)
        return {'account':value,'positions':[],'orders':[],'market_status':'UNAVAILABLE'}


class TLSFlow(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)
        cls.temp=tempfile.TemporaryDirectory(prefix='ai-invest-web-fixture-')
        cls.root=Path(cls.temp.name)
        def run(*args):
            subprocess.run(['/usr/bin/openssl',*args],cwd=cls.root,stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10,check=True)
        run('req','-x509','-newkey','ec','-pkeyopt','ec_paramgen_curve:P-256','-nodes','-keyout','ca.key',
            '-out','client-ca.crt','-days','1','-subj','/CN=SYNTHETIC_TEST_CA','-addext','basicConstraints=critical,CA:TRUE')
        for name,usage,serial in (('server','serverAuth','2'),('client','clientAuth','3')):
            run('req','-new','-newkey','ec','-pkeyopt','ec_paramgen_curve:P-256','-nodes','-keyout',name+'.key',
                '-out',name+'.csr','-subj','/CN=localhost')
            (cls.root/(name+'.ext')).write_text('subjectAltName=DNS:localhost,IP:127.0.0.1\nextendedKeyUsage='+usage+'\n')
            run('x509','-req','-in',name+'.csr','-CA','client-ca.crt','-CAkey','ca.key','-set_serial',serial,
                '-out',name+'.crt','-days','1','-extfile',name+'.ext')
        for path in cls.root.iterdir(): path.chmod(0o600)
        cert=ssl.PEM_cert_to_DER_cert((cls.root/'client.crt').read_text())
        cls.fingerprint=hashlib.sha256(cert).hexdigest()

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    async def asyncSetUp(self):
        self.files=tempfile.TemporaryDirectory(prefix='ai-invest-web-vault-')
        self.vault=FileVault(self.files.name)
        self.store=Store()
        self.gateway=Gateway(self.store,self.vault,'https://localhost:8443',frozenset([self.fingerprint]),reader=Broker)
        self.runner=web.AppRunner(application(self.gateway),access_log=None)
        await self.runner.setup()
        site=web.TCPSite(self.runner,'127.0.0.1',0,ssl_context=server_tls(self.root))
        await site.start()
        port=site._server.sockets[0].getsockname()[1]
        self.origin='https://localhost:'+str(port)
        self.gateway.origin=self.origin
        self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.minimum_version=ssl.TLSVersion.TLSv1_3
        self.context.load_verify_locations(cafile=self.root/'client-ca.crt')
        self.context.load_cert_chain(self.root/'client.crt',self.root/'client.key')
        self.client=ClientSession(connector=TCPConnector(ssl=self.context),timeout=ClientTimeout(total=5))

    async def asyncTearDown(self):
        await self.client.close()
        await self.runner.cleanup()
        self.vault.close();self.files.cleanup()

    async def post(self,path,data,headers=None):
        async with self.client.get(self.origin+'/api/session') as response: session=await response.json()
        self.gateway.last_write.clear() # Isolate tests from real1s rate limit.
        auth={'Origin':self.origin,'X-CSRF-Token':session['csrf']}
        auth.update(headers or {})
        async with self.client.post(self.origin+path,json=data,headers=auth) as response:
            body=await response.text()
            for value in (KEY,VALUE,OTHER): self.assertNotIn(value,body)
            self.assertEqual(response.headers['Cache-Control'],'no-store')
            return response.status,json.loads(body)

    async def connected(self):
        status,result=await self.post('/api/connections',{'key':KEY,'secret':VALUE})
        self.assertEqual(status,200)
        return UUID(result['id'])

    async def test_connect_refresh_replace_disconnect_actual_tls(self):
        identifier=await self.connected()
        original=self.store.data[identifier]['credential_version']
        self.assertEqual(self.vault.get(self.store.tenant,identifier,original).secret_key,VALUE)
        status,_=await self.post('/api/connections/'+str(identifier)+'/refresh',{})
        self.assertEqual(status,200)
        status,_=await self.post('/api/connections/'+str(identifier)+'/credentials',{'key':KEY,'secret':OTHER})
        self.assertEqual(status,200)
        self.assertFalse((Path(self.files.name)/self.vault.name(original)).exists())
        async with self.client.get(self.origin+'/api/connections') as response:
            result=await response.text()
            for value in (KEY,VALUE,OTHER): self.assertNotIn(value,result)
            self.assertIn('200',result)
        status,result=await self.post('/api/connections/'+str(identifier)+'/disconnect',{})
        self.assertEqual(status,200);self.assertFalse(result['broker_revoked'])
        self.assertEqual(list(Path(self.files.name).iterdir()),[])
        self.assertEqual(self.store.events,['connected','refreshed','replaced','disconnected'])

    async def test_failed_rotation_preserves_active_file(self):
        identifier=await self.connected();before=self.store.data[identifier]['credential_version']
        status,_=await self.post('/api/connections/'+str(identifier)+'/credentials',{'key':KEY,'secret':'PUBLIC_INVALID_CREDENTIAL'})
        self.assertEqual(status,400)
        self.assertEqual(self.store.data[identifier]['credential_version'],before)
        self.assertEqual(len(list(Path(self.files.name).iterdir())),1)

    async def test_wrong_account_rotation_refused(self):
        identifier=await self.connected()
        self.store.data[identifier]['broker_account_id']=UUID(int=401)
        status,_=await self.post('/api/connections/'+str(identifier)+'/credentials',{'key':KEY,'secret':OTHER})
        self.assertEqual(status,400)

    async def test_csrf_host_origin_and_unknown_account_refused(self):
        for headers in ({'Origin':'https://invalid.example'},{'X-CSRF-Token':'bad'},{'Host':'invalid.example'},
            {'X-Forwarded-Host':'localhost'},{'X-Client-Cert':'pretend'}):
            status,_=await self.post('/api/connections',{'key':KEY,'secret':VALUE},headers)
            self.assertEqual(status,400)
        status,_=await self.post('/api/connections/'+str(uuid4())+'/disconnect',{})
        self.assertEqual(status,400)
        self.assertEqual(list(Path(self.files.name).iterdir()),[])

    async def test_client_cert_required_and_unknown_fingerprint_refused(self):
        no_cert=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);no_cert.load_verify_locations(cafile=self.root/'client-ca.crt')
        async with ClientSession(connector=TCPConnector(ssl=no_cert),timeout=ClientTimeout(total=3)) as client:
            with self.assertRaises(Exception):
                async with client.get(self.origin+'/api/session') as response: await response.read()
        self.gateway.clients=frozenset()
        async with self.client.get(self.origin+'/api/session') as response: self.assertEqual(response.status,400)

    async def test_replay_and_expiry_refused(self):
        challenge=self.gateway.csrf(self.fingerprint)
        class Request:
            headers=CIMultiDict({'Origin':self.origin,'X-CSRF-Token':challenge})
        self.gateway.consume(Request(),self.fingerprint)
        with self.assertRaises(Refused): self.gateway.consume(Request(),self.fingerprint)
        self.gateway.tokens[self.fingerprint]=(challenge,0)
        with self.assertRaises(Refused): self.gateway.consume(Request(),self.fingerprint)

    async def test_encrypted_tls_key_never_prompts(self):
        with patch('ai_invest_execution.web_gateway.ssl.SSLContext') as factory,patch('builtins.input') as prompt:
            context=factory.return_value
            context.options=0
            context.keylog_filename=None
            def load_chain(*args,**kwargs):
                self.assertEqual(set(kwargs),{'password'})
                kwargs['password']()
            context.load_cert_chain.side_effect=load_chain
            with self.assertRaises(Refused): server_tls(self.root)
            context.load_cert_chain.assert_called_once()
            context.load_verify_locations.assert_not_called()
            prompt.assert_not_called()

    async def test_no_order_or_live_route_and_oversized_input(self):
        for path,data in (('/api/orders',{}),('/api/live',{}),('/api/connections',{'key':KEY,'secret':VALUE,'tenant':'other'}),
            ('/api/connections',{'key':'x'*3000,'secret':VALUE})):
            status,_=await self.post(path,data);self.assertEqual(status,400)

    async def test_unknown_commit_not_reported_connected(self):
        self.store.fail_save=True
        status,_=await self.post('/api/connections',{'key':KEY,'secret':VALUE})
        self.assertEqual(status,400);self.assertFalse(self.store.data)
        self.assertEqual(len(list(Path(self.files.name).iterdir())),1) # Protected ambiguous candidate retained.

    async def test_timeout_cancels_and_removes_unvalidated_candidate(self):
        async def stalled(*args): await asyncio.Event().wait()
        with patch('ai_invest_execution.web_gateway.OPERATION_TIMEOUT',0.05),patch.object(Broker,'account',new=stalled):
            status,_=await self.post('/api/connections',{'key':KEY,'secret':VALUE})
        self.assertEqual(status,400)
        self.assertFalse(self.store.data)
        self.assertEqual(list(Path(self.files.name).iterdir()),[])

    async def test_simultaneous_mutation_is_refused(self):
        async with self.gateway.lock:
            status,_=await self.post('/api/connections',{'key':KEY,'secret':VALUE})
        self.assertEqual(status,400)
        self.assertEqual(list(Path(self.files.name).iterdir()),[])

    async def test_credential_echo_from_broker_refused(self):
        with patch.object(Broker,'account',new=AsyncMock(return_value=(ACCOUNT,{'cash':VALUE}))):
            status,_=await self.post('/api/connections',{'key':KEY,'secret':VALUE})
        self.assertEqual(status,400);self.assertFalse(self.store.data)

    async def test_static_shell_no_persistence_or_injection_sinks(self):
        for path,fragment in (('/','Connect Alpaca PAPER'),('/app.js','textContent'),('/app.css','max-width:600px')):
            async with self.client.get(self.origin+path) as response:
                text=await response.text();self.assertIn(fragment,text)
                self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])
                for forbidden in ('localStorage','sessionStorage','innerHTML','document.cookie','serviceWorker','console.log'):
                    self.assertNotIn(forbidden,text)


class Files(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='ai-invest-file-fixture-');self.vault=FileVault(self.temp.name)
        self.tenant,self.connection=uuid4(),uuid4();self.credentials=PaperCredentials(KEY,VALUE)
    def tearDown(self): self.vault.close();self.temp.cleanup()
    def test_scope_modes_links_and_symlink_rejection(self):
        version=self.vault.put(self.tenant,self.connection,self.credentials)
        path=Path(self.temp.name)/self.vault.name(version)
        with self.assertRaises(Refused): self.vault.get(uuid4(),self.connection,version)
        path.chmod(0o644)
        with self.assertRaises(Refused): self.vault.get(self.tenant,self.connection,version)
        path.chmod(0o600);os.link(path,path.with_suffix('.other'))
        with self.assertRaises(Refused): self.vault.get(self.tenant,self.connection,version)
        path.unlink();path.symlink_to(path.with_suffix('.other'))
        with self.assertRaises(OSError): self.vault.get(self.tenant,self.connection,version)
    def test_partial_write_cleanup_reg_web01(self):
        with patch('ai_invest_execution.web_store.os.write',return_value=1):
            with self.assertRaises(Refused): self.vault.put(self.tenant,self.connection,self.credentials)
        self.assertEqual(list(Path(self.temp.name).iterdir()),[])
    def test_fsync_failure_cleanup(self):
        with patch('ai_invest_execution.web_store.os.fsync',side_effect=OSError('PRIVATE_TEST_DETAIL')):
            with self.assertRaises(OSError): self.vault.put(self.tenant,self.connection,self.credentials)
        self.assertEqual(list(Path(self.temp.name).iterdir()),[])
    def test_path_traversal_and_orphan_capacity(self):
        with self.assertRaises(Refused): self.vault.get(self.tenant,self.connection,'../../anything')
        for _ in range(32): self.vault.put(self.tenant,self.connection,self.credentials)
        with self.assertRaises(Refused): self.vault.put(self.tenant,self.connection,self.credentials)


class Boundaries(unittest.IsolatedAsyncioTestCase):
    async def test_database_zero_update_never_success_reg_web02(self):
        class DB:
            @asynccontextmanager
            async def transaction(self): yield
            execute=AsyncMock(return_value=SimpleNamespace(rowcount=0))
        store=WebStore(DB(),uuid4())
        for action in (store.save(uuid4(),uuid4(),uuid4(),{},'a'*64,'connected'),store.disconnect(uuid4(),'a'*64),store.refreshed(uuid4(),{},'a'*64)):
            with self.assertRaises(Refused): await action
    async def test_transport_refuses_arbitrary_url_before_network(self):
        reader=PaperWebReader(PaperCredentials(KEY,VALUE),uuid4(),uuid4())
        for path in ('https://bad.invalid','/v2/orders','/v2/account?key=value'):
            with self.assertRaises(Refused): await reader.get(path)
    async def test_account_discovery_and_binding(self):
        reader=PaperWebReader(PaperCredentials(KEY,VALUE),uuid4(),uuid4())
        data={'id':str(ACCOUNT),'currency':'USD','cash':'200','equity':'200','status':'ACTIVE','trading_blocked':False,'account_blocked':False}
        with patch.object(reader,'get',new=AsyncMock(return_value=json.dumps(data).encode())):
            self.assertEqual((await reader.account())[0],ACCOUNT)
            with self.assertRaises(Refused): await reader.account(uuid4())
    async def test_policy_no_insecure_origin_or_open_client_access(self):
        self.assertEqual(policy({'origin':'https://invest.local:8443','clients':['a'*64]})[0],'https://invest.local:8443')
        for data in ({'origin':'http://invest.local:8443','clients':['a'*64]},
            {'origin':'https://invest.local:8443','clients':[]},{'origin':'https://user@invest.local:8443','clients':['a'*64]}):
            with self.assertRaises(Refused): policy(data)
    async def test_missing_encrypted_mount_refused(self):
        with patch.object(Path,'read_text',return_value=''):
            with self.assertRaises(Refused): encrypted_mounts()


if __name__=='__main__': unittest.main()
