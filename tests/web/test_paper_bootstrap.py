"""Synthetic initial activation; no real network, credential or account data."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock,patch
from uuid import uuid4
sys.path[:0]=['/opt/ai-invest/backend','/opt/ai-invest/execution']
from ai_invest_execution import paper_bootstrap as B
from ai_invest_execution.web_store import FileVault,Refused
from ai_invest_execution.web_broker import PaperWebReader
from ai_invest_execution.alpaca_paper import PaperCredentials
from test_web import Store,Broker,KEY,VALUE,ACCOUNT


class Activation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ai-invest-stage-fixture-')
        self.path=Path(self.tmp.name);self.vault=FileVault(self.path);self.store=Store()
        self.file=self.path/B.STAGED
        self.file.write_text(json.dumps({'version':1,'mode':'PAPER','target_role':'ai_web_a','key':KEY,'secret':VALUE}))
        self.file.chmod(0o600)
    def tearDown(self): self.vault.close();self.tmp.cleanup()
    async def test_activation_actual_protected_file_fake_broker(self):
        result=await B.activate(self.store,self.vault,Broker)
        self.assertTrue(result['connected']);self.assertFalse(result['orders_reconciled'])
        self.assertFalse(result['secret_entry_authorized']);self.assertFalse(result['runtime_crash_suppression_qualified'])
        self.assertNotIn(KEY,json.dumps(result));self.assertNotIn(VALUE,json.dumps(result))
        self.assertEqual(self.store.events,['connected']);self.assertTrue(self.file.exists())
        with self.assertRaises(Refused): await B.activate(self.store,self.vault,Broker)
    async def test_rejected_credentials_never_connected(self):
        class Rejected(Broker):
            async def account(self,*args): raise Refused()
        with self.assertRaises(Refused): await B.activate(self.store,self.vault,Rejected)
        self.assertFalse(self.store.data);self.assertEqual(len(list(self.path.iterdir())),1)
    async def test_ambiguous_save_preserves_version(self):
        self.store.fail_save=True
        with self.assertRaises(Refused): await B.activate(self.store,self.vault,Broker)
        self.assertEqual(len(list(self.path.iterdir())),2)
    async def test_echoed_credential_snapshot_rejected(self):
        class Echo(Broker):
            async def dashboard(self,*args): return {'echo':VALUE}
        with self.assertRaises(Refused): await B.activate(self.store,self.vault,Echo)
        self.assertFalse(self.store.data)
    async def test_symlink_hardlink_permissions_and_bad_schema(self):
        raw=self.file.read_text()
        self.file.chmod(0o644)
        with self.assertRaises(Refused): B.staged(self.vault)
        self.file.chmod(0o600);os.link(self.file,self.path/'link')
        with self.assertRaises(Refused): B.staged(self.vault)
        (self.path/'link').unlink();self.file.rename(self.path/'real');self.file.symlink_to('real')
        with self.assertRaises(OSError): B.staged(self.vault)
        self.file.unlink();self.file.write_text(raw);self.file.chmod(0o600)
        for updates in ({'mode':'LIVE'},{'target_role':'another_role'},{'extra':'value'},{'version':True}):
            data=json.loads(raw);data.update(updates);self.file.write_text(json.dumps(data))
            with self.assertRaises(Refused): B.staged(self.vault)
    async def test_audit_actor_meets_existing_constraint(self):
        self.assertRegex(B.CONSOLE_ACTOR,r'^[a-f0-9]{64}$')
    async def test_missing_encrypted_mount_fails_before_stage(self):
        with patch.object(B.Path,'read_text',return_value=''):
            with self.assertRaises(Refused): B.protected_mounts()
    async def test_actual_reader_clock_buying_power_with_mocked_http_bytes(self):
        reader=PaperWebReader(PaperCredentials(KEY,VALUE),uuid4(),uuid4())
        async def get(path,market=False):
            if market: raise Refused()
            if path=='/v2/account':
                return json.dumps({'id':str(ACCOUNT),'currency':'USD','cash':'200','equity':'200','buying_power':'200','status':'ACTIVE','trading_blocked':False,'account_blocked':False}).encode()
            if path=='/v2/clock': return b'{"is_open":true,"timestamp":"2026-01-01T14:30:00Z","next_open":"2026-01-02T14:30:00Z","next_close":"2026-01-01T21:00:00Z"}'
            return b'[]'
        with patch.object(reader,'get',side_effect=get): result=await reader.dashboard(ACCOUNT)
        self.assertTrue(result['clock']['is_open']);self.assertEqual(result['account']['buying_power'],'200')
        self.assertIsNone(result['market'])
