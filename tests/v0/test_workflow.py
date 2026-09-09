"""Actual durable CLI/process tests use isolated synthetic data, never Alpaca."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from ai_invest_core.intents import TradeIntent, Mode, Side
from ai_invest_core.synthetic import initialize, SCOPES, SyntheticStore, SyntheticBroker
from ai_invest_core.workflow import Workflow, WorkflowError


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ai-invest-workflow-')
        self.directory = Path(self.tmp.name) / 'state'
        initialize(self.directory)
        self.store, self.broker = SyntheticStore(self.directory), SyntheticBroker(self.directory)
        self.app = Workflow(self.store, self.broker, SCOPES[0])
        self.app.reconcile()
        self.app.resume()

    def tearDown(self):
        self.store.close()
        self.broker.close()
        self.tmp.cleanup()

    def intent(self, **changes):
        now = datetime.now(timezone.utc)
        values = dict(scope=SCOPES[0], intent_id=uuid4(), security_id=self.broker.security_id,
            mode=Mode.PAPER, side=Side.BUY, quantity=Decimal('0.5'), limit_price=Decimal('20.01'),
            created_at=now, expires_at=now+timedelta(minutes=5))
        values.update(changes)
        return TradeIntent(**values)

    def cli(self, *args, expected=0):
        result = subprocess.run(['/usr/bin/python3', '-I', '-B', str(ROOT/'scripts/v0.py'), 'demo',
            '--state-dir', str(self.directory), *args], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(result.stderr, '')
        return json.loads(result.stdout) if result.stdout else None

    def test_cli_actual_process_crash_restart_lookup_not_resubmit(self):
        proposed = self.cli('propose')['result']
        self.cli('submit', proposed, '--fault', 'crash-after-accept', expected=75)
        state = self.cli('status')
        self.assertEqual(state['orders'][proposed], 'UNKNOWN')
        self.assertEqual(state['broker_submissions'], 1)
        self.assertEqual(self.cli('submit', proposed)['result'], 'UNKNOWN')
        recovered = self.cli('reconcile')
        self.assertEqual(recovered['orders'][proposed], 'FILLED')
        self.assertEqual((recovered['cash'], recovered['position'], recovered['reserved']), ('189.995', '0.5', '0'))
        self.assertEqual(self.cli('submit', proposed)['broker_submissions'], 1)
        self.assertEqual(len(self.cli('audit')['audit']), 5)
        self.assertFalse(recovered['secret_entry_authorized'])
        self.assertFalse(recovered['runtime_crash_suppression_qualified'])

    def test_timeout_is_unknown_and_not_found_never_releases(self):
        key = self.app.record(self.intent())
        with patch.object(self.broker, 'submit', side_effect=TimeoutError):
            self.assertEqual(self.app.dispatch(key), 'UNKNOWN')
        self.app.reconcile()
        self.assertEqual(self.app.status()['reserved'], '10.005')
        self.assertFalse(self.app.status()['reconciled'])
        self.assertEqual(self.app.dispatch(key), 'UNKNOWN')
        self.assertEqual(self.broker.snapshot(SCOPES[0])['submissions'], 0)

    def test_durable_admission_before_broker_and_rollback_blocks_send(self):
        key = self.app.record(self.intent())
        @contextmanager
        def fail(*args):
            yield self.store.read(SCOPES[0])
            raise OSError('synthetic_storage_failure')
        with patch.object(self.store, 'transaction', fail), patch.object(self.broker, 'submit') as send:
            with self.assertRaises(OSError): self.app.dispatch(key)
            send.assert_not_called()

    def test_partial_fill_and_duplicate_reconciliation(self):
        key = self.app.record(self.intent())
        self.broker.partial = True
        self.assertEqual(self.app.dispatch(key), 'PARTIAL')
        self.assertEqual(self.app.status()['reserved'], '5.0025')
        self.app.reconcile()
        self.assertEqual(len(self.app.status()['fills']), 1)
        self.broker.complete(SCOPES[0], self.app.status()['orders'][key]['client_id'])
        self.app.reconcile()
        self.app.reconcile()
        self.assertEqual((self.app.status()['position'],len(self.app.status()['fills'])), ('0.5',2))

    def test_stop_precedes_admission_and_blocks_buy(self):
        key = self.app.record(self.intent())
        self.app.stop()
        self.assertEqual(self.app.dispatch(key), 'REJECT')
        self.assertIn('stopped', self.app.status()['decisions'][-1]['reasons'])
        self.assertEqual(self.broker.snapshot(SCOPES[0])['submissions'], 0)

    def test_stop_after_admission_does_not_promise_no_fill(self):
        key = self.app.record(self.intent())
        original = self.broker.submit
        def send(scope, order):
            self.app.stop()
            original(scope, order)
        with patch.object(self.broker, 'submit', send):
            self.assertEqual(self.app.dispatch(key), 'FILLED')
        self.assertTrue(self.app.status()['stopped'])

    def test_policy_rejects_oversize_sell_wrong_mode_asset_and_expiry(self):
        for changes, reason in (({'quantity': Decimal('2')},'order_cap'), ({'side': Side.SELL},'buy_paper_only'),
            ({'mode': Mode.SHADOW},'buy_paper_only'), ({'security_id': uuid4()},'unsupported_asset'),
            ({'created_at': datetime(2025,1,1,tzinfo=timezone.utc),
              'expires_at': datetime(2025,1,2,tzinfo=timezone.utc)},'intent_expired')):
            key = self.app.record(self.intent(**changes))
            self.assertEqual(self.app.dispatch(key), 'REJECT')
            self.assertIn(reason, self.app.status()['decisions'][-1]['reasons'])
        self.assertEqual(self.broker.snapshot(SCOPES[0])['submissions'], 0)

    def test_stale_market_and_external_cash_changes_reject(self):
        market = self.broker.market()
        market['time'] -= timedelta(seconds=30)
        key = self.app.record(self.intent())
        with patch.object(self.broker, 'market', return_value=market):
            self.assertEqual(self.app.dispatch(key), 'REJECT')
        with self.broker._change(SCOPES[0]) as state: state['cash'] = '0'
        self.assertEqual(self.app.dispatch(key), 'REJECT')
        self.assertIn('account_changed', self.app.status()['decisions'][-1]['reasons'])

    def test_tenant_scope_and_synthetic_provider_boundary(self):
        with self.assertRaises(WorkflowError): self.app.record(self.intent(scope=SCOPES[1]))
        with self.assertRaises(WorkflowError): Workflow(self.store, object(), SCOPES[0])
        self.app.record(self.intent())
        self.assertEqual(self.store.read(SCOPES[1])['intents'], {})

    def test_stored_intent_mutation_refused_before_send(self):
        key = self.app.record(self.intent())
        with self.store.transaction(SCOPES[0], 'synthetic_corruption') as state:
            state['intents'][key]['payload']['quantity'] = '1'
        with self.assertRaises(WorkflowError): self.app.dispatch(key)
        self.assertEqual(self.broker.snapshot(SCOPES[0])['submissions'], 0)

    def test_missing_fill_is_not_successful_reconciliation(self):
        key = self.app.record(self.intent())
        self.broker.timeout = True
        self.app.dispatch(key)
        with self.broker._change(SCOPES[0]) as state: state['fills'] = {}
        with self.assertRaises(WorkflowError): self.app.reconcile()
        self.assertTrue(self.app.status()['stopped'])

    def test_client_identity_and_unexpected_update_fields_refused_reg_rv02(self):
        key = self.app.record(self.intent())
        with patch.object(self.broker,'submit',side_effect=TimeoutError): self.app.dispatch(key)
        original = self.app.status()['orders'][key]
        for change in ({'client_id':'different-client'}, {'approval_consumed':False}):
            with self.broker._change(SCOPES[0]) as state:
                state['orders'][original['client_id']] = {
                    **{n:original[n] for n in ('client_id','digest','quantity','limit_price','filled_quantity','filled_value')},
                    'status':'REJECTED', **change}
            with self.assertRaises(WorkflowError): self.app.reconcile()
            actual=self.app.status()['orders'][key]
            self.assertEqual(actual['client_id'],original['client_id'])
            self.assertTrue(actual['approval_consumed'])
            self.assertEqual(actual['status'],'UNKNOWN')
            self.assertTrue(self.app.status()['stopped'])

    def test_quote_evaluation_occurs_after_observation_reg_rv03(self):
        key=self.app.record(self.intent())
        self.assertEqual(self.app.dispatch(key),'FILLED')
        decision=self.app.status()['decisions'][-1]
        self.assertGreaterEqual(decision['time'],decision['quote']['time'])

    def test_missing_demo_database_never_silently_reinitialized(self):
        missing=Path(self.tmp.name)/'empty'
        missing.mkdir(mode=0o700)
        with self.assertRaises(FileNotFoundError): SyntheticStore(missing)
        self.assertEqual(list(missing.iterdir()),[])

    def test_reconciliation_bad_digest_and_cash_fail_closed(self):
        key = self.app.record(self.intent())
        self.broker.timeout = True
        self.app.dispatch(key)
        with self.broker._change(SCOPES[0]) as state:
            state['orders'][self.app.status()['orders'][key]['client_id']]['digest'] = 'wrong'
        with self.assertRaises(WorkflowError): self.app.reconcile()
        self.assertTrue(self.app.status()['stopped'])
        self.assertFalse(self.app.status()['reconciled'])

    def test_concurrent_process_duplicate_submits_one_broker_order(self):
        key = self.app.record(self.intent())
        command = ['/usr/bin/python3','-I','-B',str(ROOT/'scripts/v0.py'),'demo','--state-dir',str(self.directory),'submit',key]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr+stdout)
        self.app.reconcile()
        self.assertEqual(self.broker.snapshot(SCOPES[0])['submissions'], 1)

    def test_sqlite_event_mutation_rejected(self):
        with self.assertRaises(Exception): self.store.db.execute("UPDATE event SET kind='modified'")

    def test_safe_demo_files_refuse_symlink_hardlink_permissions(self):
        self.store.close()
        path = self.directory/'synthetic-ledger.sqlite'
        original = self.directory/'saved.sqlite'
        path.rename(original)
        try:
            path.symlink_to(original)
            with self.assertRaises(Exception): SyntheticStore(self.directory)
            path.unlink()
            os.link(original, path)
            with self.assertRaises(Exception): SyntheticStore(self.directory)
            path.unlink()
            original.rename(path)
            path.chmod(0o666)
            with self.assertRaises(Exception): SyntheticStore(self.directory)
        finally:
            path.chmod(0o600)
            self.store = SyntheticStore(self.directory)


if __name__ == '__main__':
    unittest.main()
