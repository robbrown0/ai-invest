"""Mocked PAPER/PG contracts; explicitly not brokerage or PostgreSQL runtime proof."""
from contextlib import contextmanager
from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'backend'))
sys.path.insert(0, str(ROOT/'execution'))
from ai_invest_core.synthetic import SCOPES
from ai_invest_core.postgres import PostgresLedger, DatabaseRefused
from ai_invest_execution.alpaca_paper import AlpacaPaperAccountReader, PaperCredentials, PaperReadError
from ai_invest_execution.alpaca_paper import amount


class Reads(unittest.TestCase):
    def setUp(self):
        self.reader = AlpacaPaperAccountReader(PaperCredentials('SYNTHETIC', 'SYNTHETIC'), SCOPES[0], UUID(int=91))
        self.account = json.dumps({'id': str(UUID(int=91)), 'cash':'200','equity':'200','currency':'USD',
            'status':'ACTIVE','trading_blocked':False,'account_blocked':False}).encode()

    def read(self, method, value, *args):
        with patch.object(AlpacaPaperAccountReader, '_get', side_effect=[self.account, json.dumps(value).encode()]) as get:
            result = getattr(self.reader, method)(*args)
            return result,get

    def test_positions_scope_projection(self):
        result,get = self.read('positions',[{'asset_id':str(UUID(int=5)), 'asset_class':'us_equity',
            'symbol':'SPY','qty':'0.5','side':'long','market_value':'10'}])
        self.assertEqual(result.scope, SCOPES[0])
        self.assertEqual(result.items[0]['quantity'],Decimal('0.5'))
        self.assertEqual(get.call_args.args, ('/v2/positions',))
        self.assertNotIn('SPY',repr(result))

    def test_recent_order_fields_and_full_page_refusal(self):
        order = {'id': str(UUID(int=50)), 'client_order_id':'ai-test','asset_id':str(UUID(int=5)),
            'asset_class':'us_equity','symbol':'SPY','side':'buy','qty':'0.5','filled_qty':'0.25',
            'filled_avg_price':'20.01','status':'partially_filled','submitted_at':'2026-09-09T12:00:00Z'}
        result,get = self.read('orders',[order])
        self.assertEqual(result.items[0]['filled_quantity'],Decimal('0.25'))
        self.assertEqual(get.call_args.args, ('/v2/orders?status=all&limit=200&direction=desc&nested=false',))
        with self.assertRaises(PaperReadError): self.read('orders',[order]*200)
        with self.assertRaises(PaperReadError): self.read('orders',[{**order,'submitted_at':None}])

    def test_iex_quotes_exact_decimal_and_fixed_data_destination(self):
        result,get = self.read('latest_quote',{'symbol':'SPY','quote':{'bp':20.0,'ap':20.01,'t':'2026-09-09T12:00:00Z'}},'SPY')
        self.assertEqual(result.items[0]['ask'],Decimal('20.01'))
        self.assertEqual(get.call_args.kwargs, {'market_data':True})
        self.assertEqual(get.call_args.args, ('/v2/stocks/SPY/quotes/latest?feed=iex',))
        for symbol in ('../account','SPY?feed=sip','https://bad.invalid','spy','SPY\n'):
            with self.assertRaises(PaperReadError): self.reader.latest_quote(symbol)

    def test_clock_type_and_timestamp_validation(self):
        value = {'is_open':True,'timestamp':'2026-09-09T12:00:00Z',
            'next_close':'2026-09-09T20:00:00Z','next_open':'2026-09-10T13:30:00Z'}
        self.assertTrue(self.read('clock',value)[0].items[0]['is_open'])
        with self.assertRaises(PaperReadError): self.read('clock',{**value,'is_open':'true'})

    def test_expected_account_checked_before_data_projection(self):
        with patch.object(AlpacaPaperAccountReader,'_get',return_value=self.account.replace(str(UUID(int=91)).encode(),str(UUID(int=92)).encode())) as get:
            with self.assertRaises(PaperReadError): self.reader.positions()
            self.assertEqual(get.call_count,1)

    def test_compact_decimal_expansion_refused_before_format_reg_rv01(self):
        for value in ('1e100000', '1e-100000', '0e100000', 'NaN', 'Infinity'):
            with patch('ai_invest_execution.alpaca_paper.format', create=True) as formatter:
                with self.assertRaises(ValueError): amount(Decimal(value))
                formatter.assert_not_called()


class FakePG:
    autocommit = True
    def __init__(self):
        self.calls=[]
        self.rollbacks=0
        self.commits=0
        self.changed=1
    def execute(self, query, params=None):
        self.calls.append((query,params))
        result=Mock(rowcount=self.changed)
        if 'SELECT rolsuper' in query: result.fetchone.return_value=(False,False,True)
        elif 'pg_auth_members' in query: result.fetchone.return_value=(False,)
        elif 'SELECT tenant_id' in query: result.fetchall.return_value=[(SCOPES[0].tenant_id,)]
        elif 'SELECT c.relname' in query: result.fetchall.return_value=[(n,'tde_heap',True,True,False) for n in ('runtime_identity','runtime_ledger','runtime_event')]
        elif 'SELECT revision,body' in query: result.fetchone.return_value=(0,{'cash':'200'})
        elif 'SELECT body' in query: result.fetchone.return_value=({'cash':'200'},)
        return result
    @contextmanager
    def transaction(self):
        try:
            yield
            self.commits+=1
        except BaseException:
            self.rollbacks+=1
            raise


class PGContract(unittest.TestCase):
    def test_transaction_lock_cas_and_event_same_commit(self):
        connection=FakePG()
        ledger=PostgresLedger(connection,SCOPES[0])
        with ledger.transaction(SCOPES[0],'risk_decision') as state: state['cash']='190'
        self.assertEqual(connection.commits,1)
        queries=[q for q,p in connection.calls]
        self.assertTrue(any('FOR UPDATE' in q for q in queries))
        self.assertTrue(any('AND revision=%s' in q for q in queries))
        self.assertTrue(any('INSERT INTO ai_invest.runtime_event' in q for q in queries))

    def test_failed_cas_rolls_back_no_event(self):
        connection=FakePG(); connection.changed=0
        ledger=PostgresLedger(connection,SCOPES[0])
        with self.assertRaises(DatabaseRefused):
            with ledger.transaction(SCOPES[0],'risk_decision') as state: state['cash']='190'
        self.assertEqual(connection.rollbacks,1)
        self.assertFalse(any('INSERT INTO' in q for q,p in connection.calls))

    def test_cross_tenant_access_refused_without_query(self):
        connection=FakePG(); ledger=PostgresLedger(connection,SCOPES[0]); count=len(connection.calls)
        with self.assertRaises(DatabaseRefused): ledger.read(SCOPES[1])
        self.assertEqual(len(connection.calls),count)

    def test_migration_no_grants_force_rls_session_user_not_guc(self):
        text=(ROOT/'backend/migrations/0002_runtime_ledger.sql').read_text()
        self.assertEqual(text.count(') USING tde_heap;'),3)
        self.assertEqual(text.count('FORCE ROW LEVEL SECURITY;'),3)
        self.assertIn('database_role = session_user',text)
        self.assertNotIn('current_setting',text)
        self.assertNotIn('GRANT ',text)


if __name__=='__main__': unittest.main()
