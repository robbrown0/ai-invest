"""Offline V0 regressions. No credentials, HTTP request or database is used."""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import importlib
import json
from pathlib import Path
import re
import ssl
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
sys.path.insert(0, str(ROOT / 'execution'))
D = importlib.import_module('ai_invest_core.intents')
A = importlib.import_module('ai_invest_execution.alpaca_paper')


def uuid(number):
    return UUID(int=number)


def scope():
    return D.Scope(uuid(1), uuid(2), uuid(3))


def decode(body):
    return A.decode_account(body, scope(), uuid(91))


def intent():
    return D.TradeIntent(D.Scope(uuid(1), uuid(2), uuid(3)), uuid(4), uuid(5),
        D.Mode.PAPER, D.Side.BUY, Decimal('0.125'), Decimal('20.05'),
        datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc))


def account_body(**changes):
    value = {'id': str(uuid(91)), 'cash': '250.00', 'equity': '251.25', 'currency': 'USD', 'status': 'ACTIVE',
             'trading_blocked': False, 'account_blocked': False}
    value.update(changes)
    return json.dumps(value).encode()


class IntentTests(unittest.TestCase):
    def test_exact_notional_independent_of_ambient_decimal_precision(self):
        with localcontext() as context:
            context.prec = 2
            self.assertEqual(intent().notional, Decimal('2.50625'))

    def test_immutable_and_redacted_repr(self):
        value = intent()
        with self.assertRaises(FrozenInstanceError):
            value.quantity = Decimal('1')
        self.assertNotIn('20.05', repr(value))
        self.assertNotIn(str(value.scope.tenant_id), repr(value.scope))

    def test_canonical_equivalent_decimals_and_timezone(self):
        first = intent()
        second = replace(first, quantity=Decimal('0.125000'), limit_price=Decimal('20.050'),
            created_at=first.created_at.astimezone(timezone(timedelta(hours=2))))
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())

    def test_digest_binds_every_scope_and_financial_field(self):
        value = intent()
        changes = {'scope': [D.Scope(uuid(8), uuid(2), uuid(3)), D.Scope(uuid(1), uuid(8), uuid(3)),
                             D.Scope(uuid(1), uuid(2), uuid(8))],
            'intent_id': [uuid(9)], 'security_id': [uuid(9)], 'mode': [D.Mode.SHADOW],
            'side': [D.Side.SELL], 'quantity': [Decimal('1')], 'limit_price': [Decimal('21')],
            'created_at': [value.created_at + timedelta(seconds=1)],
            'expires_at': [value.expires_at + timedelta(seconds=1)]}
        for name, choices in changes.items():
            for choice in choices:
                self.assertNotEqual(value.digest(), replace(value, **{name: choice}).digest())

    def test_forbidden_and_ambiguous_numeric_input(self):
        for value in ('NaN', 'Infinity', '-1', '1e2', ' 1', '+1', '01', '1.',
                      '.1', '1.1234567891', '1000000001', '1' * 100, '١', 1, 1.0, True, None):
            with self.assertRaises(D.InvalidIntent):
                D.decimal_text(value)

    def test_constructor_rejects_nonfinite_float_zero_and_precision(self):
        for value in (Decimal('NaN'), Decimal('sNaN'), Decimal('Infinity'), Decimal('-Infinity'),
                      Decimal('0'), Decimal('-1'), Decimal('1000000001'), Decimal('1E-10'), 1.5, True):
            with self.assertRaises(D.InvalidIntent):
                replace(intent(), quantity=value)

    def test_strict_identity_and_modes(self):
        for scope in (None, {'tenant_id': str(uuid(1))}):
            with self.assertRaises(D.InvalidIntent):
                replace(intent(), scope=scope)
        with self.assertRaises(D.InvalidIntent):
            D.Scope(uuid(0), uuid(2), uuid(3))
        for mode in ('LIVE', 'LIVE_LIMITED', 'PAPER', None):
            with self.assertRaises(D.InvalidIntent):
                replace(intent(), mode=mode)
        self.assertEqual({x.value for x in D.Mode}, {'BACKTEST', 'PAPER', 'SHADOW'})

    def test_naive_reversed_and_empty_interval_refused(self):
        value = intent()
        for changes in ({'created_at': datetime(2026, 1, 1)},
                        {'expires_at': value.created_at}, {'expires_at': value.created_at - timedelta(seconds=1)}):
            with self.assertRaises(D.InvalidIntent):
                replace(value, **changes)

    def test_utc_underflow_overflow_rejected_at_intake_reg_vf01(self):
        for created, expires in (('0001-01-01T00:00:00+14:00', '0001-01-02T00:00:00+14:00'),
                                 ('9999-12-30T23:59:59-14:00', '9999-12-31T23:59:59-14:00')):
            with self.assertRaises(D.InvalidIntent) as error:
                D.TradeIntent.from_advisory(scope(), {**self.payload(), 'created_at': created, 'expires_at': expires})
            self.assertEqual(str(error.exception), 'invalid_trade_intent')

    def payload(self):
        value = intent()
        return {'intent_id': str(value.intent_id), 'security_id': str(value.security_id),
                'mode': 'PAPER', 'side': 'BUY', 'quantity': '0.125', 'limit_price': '20.05',
                'created_at': value.created_at.isoformat(), 'expires_at': value.expires_at.isoformat()}

    def test_advisory_cannot_select_scope_or_extra_execution_fields(self):
        for name in ('tenant_id', 'account_id', 'portfolio_id', 'endpoint', 'approval', 'extended_hours'):
            with self.assertRaises(D.InvalidIntent):
                D.TradeIntent.from_advisory(intent().scope, {**self.payload(), name: 'UNTRUSTED'})
        self.assertEqual(D.TradeIntent.from_advisory(intent().scope, self.payload()).digest(), intent().digest())

    def test_advisory_errors_are_bounded(self):
        for field, bad in (('mode', 'LIVE'), ('side', 'BUY;UNTRUSTED'), ('quantity', 'NaN'),
                           ('created_at', 'x' * 10000), ('intent_id', 'UNTRUSTED'), ('quantity', 1)):
            with self.assertRaises(D.InvalidIntent) as error:
                D.TradeIntent.from_advisory(intent().scope, {**self.payload(), field: bad})
            self.assertEqual(str(error.exception), 'invalid_trade_intent')

    def test_intent_has_no_permission_or_submission_method(self):
        self.assertFalse(any(hasattr(intent(), name) for name in ('submit', 'approve', 'credential', 'execute')))
        value = json.loads(intent().canonical_bytes())
        self.assertEqual((value['order_type'], value['time_in_force'], value['extended_hours']), ('limit', 'day', False))


class PaperReaderTests(unittest.TestCase):
    def credentials(self):
        return A.PaperCredentials('SYNTHETIC_KEY_ID', 'SYNTHETIC_SECRET_VALUE')

    def reader(self):
        return A.AlpacaPaperAccountReader(self.credentials(), scope(), uuid(91))

    def read(self, body=None, status=200, headers=None, error=None):
        body = account_body() if body is None else body
        fields = {'Content-Type': 'application/json', **(headers or {})}
        response = Mock(status=status)
        response.read.return_value = body
        response.getheader.side_effect = lambda name, default=None: fields.get(name, default)
        connection = Mock()
        connection.getresponse.side_effect = error
        connection.getresponse.return_value = response
        with patch.object(A.http.client, 'HTTPSConnection', return_value=connection) as factory:
            try:
                result = self.reader().read_account()
                return result, factory, connection, response
            finally:
                connection.close.assert_called_once()

    def test_fixed_paper_endpoint_tls_get_and_no_debug(self):
        result, factory, connection, response = self.read()
        self.assertEqual(factory.call_args.args, ('paper-api.alpaca.markets',))
        self.assertEqual(factory.call_args.kwargs['port'], 443)
        self.assertEqual(factory.call_args.kwargs['timeout'], 5)
        context = factory.call_args.kwargs['context']
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        connection.set_debuglevel.assert_called_once_with(0)
        self.assertEqual(connection.request.call_args.args, ('GET', '/v2/account'))
        response.read.assert_called_once_with(A.MAX_RESPONSE + 1)
        self.assertEqual((result.cash, result.equity), (Decimal('250.00'), Decimal('251.25')))

    def test_sensitive_objects_redact_representation(self):
        for value in (self.credentials(), self.reader(), decode(account_body())):
            self.assertNotIn('SYNTHETIC_SECRET_VALUE', repr(value))
            self.assertNotIn('250.00', repr(value))

    def test_credential_header_injection_and_wrong_types_refused(self):
        for value in ('x\r\nX-Evil: yes', '', 'x' * 257, None, 123, 'secret value'):
            with self.assertRaises(A.PaperReadError):
                A.PaperCredentials(value, 'SYNTHETIC_SECRET_VALUE')
        with self.assertRaises(A.PaperReadError):
            A.AlpacaPaperAccountReader({'key_id': 'SYNTHETIC'}, scope(), uuid(91))

    def test_redirects_errors_and_rate_limits_never_retried(self):
        for status, reason in ((301, 'paper_read_failed'), (302, 'paper_read_failed'),
                (307, 'paper_read_failed'), (308, 'paper_read_failed'), (500, 'paper_read_failed'),
                (401, 'paper_credentials_rejected'), (403, 'paper_credentials_rejected'),
                (429, 'paper_rate_limited')):
            with self.assertRaises(A.PaperReadError) as error:
                self.read(status=status, headers={'Location': 'https://untrusted.invalid'})
            self.assertEqual(str(error.exception), reason)

    def test_transport_error_details_suppressed(self):
        with self.assertRaises(A.PaperReadError) as error:
            self.read(error=OSError('SYNTHETIC_SECRET_VALUE'))
        self.assertEqual(str(error.exception), 'paper_read_failed')
        self.assertTrue(error.exception.__suppress_context__)

    def test_response_bounds_compression_and_content_type(self):
        for headers in ({'Content-Length': '65537'}, {'Content-Length': '-1'},
                        {'Content-Length': '1'}, {'Content-Length': '9' * 20},
                        {'Content-Encoding': 'gzip'}, {'Content-Type': 'text/html'}):
            with self.assertRaises(A.PaperReadError):
                self.read(headers=headers)
        with self.assertRaises(A.PaperReadError):
            self.read(body=b' ' * (A.MAX_RESPONSE + 1))

    def test_duplicate_json_fields_and_nonfinite_constants_refused(self):
        for body in (b'{"cash":"1","cash":"2"}', b'{"unexpected":NaN}',
                     b'{"unexpected":Infinity}', b'not json', b'[]'):
            with self.assertRaises(A.PaperReadError):
                decode(body)

    def test_required_fields_and_numeric_type_checks(self):
        for field, value in (('cash', 100), ('cash', True), ('equity', 'NaN'), ('cash', '1e2'),
                ('currency', 'EUR'), ('trading_blocked', 'false'), ('account_blocked', 0), ('status', None)):
            with self.assertRaises(A.PaperReadError):
                decode(account_body(**{field: value}))

    def test_unknown_status_stays_inactive_negative_cash_visible(self):
        value = decode(account_body(status='NEW_UNKNOWN_STATUS', cash='-1.25'))
        self.assertEqual(value.status, 'NOT_ACTIVE')
        self.assertEqual(value.cash, Decimal('-1.25'))

    def test_broker_ids_and_buying_power_not_in_account_projection(self):
        value = decode(account_body(account_number='SYNTHETIC', buying_power='999999'))
        self.assertFalse(any(hasattr(value, name) for name in ('id', 'account_number', 'buying_power', 'credentials')))
        self.assertFalse(hasattr(A.AlpacaPaperAccountReader, 'submit_order'))

    def test_proxy_and_endpoint_environment_cannot_redirect(self):
        with patch.dict('os.environ', {'HTTPS_PROXY': 'http://untrusted.invalid',
                'APCA_API_BASE_URL': 'https://untrusted.invalid',
                'SSL_CERT_FILE': '/nonexistent-untrusted-ca', 'SSL_CERT_DIR': '/nonexistent-untrusted-dir'}):
            _, factory, _, _ = self.read()
        self.assertEqual(factory.call_args.args, ('paper-api.alpaca.markets',))

    def test_tls_keylog_environment_cannot_create_sink_reg_vf06(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-v0-tls-') as directory:
            target = Path(directory) / 'forbidden-key-log'
            with patch.dict('os.environ', {'SSLKEYLOGFILE': str(target)}):
                _, factory, _, _ = self.read()
            self.assertIsNone(factory.call_args.kwargs['context'].keylog_filename)
            self.assertFalse(target.exists())

    def test_provider_account_mismatch_never_associated_with_scope(self):
        for identifier in (str(uuid(92)), 'UNTRUSTED', None):
            with self.assertRaises(A.PaperReadError):
                self.read(body=account_body(id=identifier))
        self.assertEqual(self.read()[0].scope, scope())

    def test_missing_or_wrong_trusted_binding_refused(self):
        for scoped, account in ((None, uuid(91)), (scope(), uuid(0)), (scope(), 'UNTRUSTED')):
            with self.assertRaises(A.PaperReadError):
                A.AlpacaPaperAccountReader(self.credentials(), scoped, account)
            with self.assertRaises(A.PaperReadError):
                A.decode_account(account_body(), scoped, account)


class MigrationStructureTests(unittest.TestCase):
    """Source checks only, NOT SQL execution, TDE proof or RLS qualification."""
    def setUp(self):
        self.sql = (ROOT / 'backend/migrations/0001_tenant_foundation.sql').read_text()
        self.tables = ('tenant', 'brokerage_account', 'portfolio', 'trade_proposal', 'audit_event')

    def test_all_tables_request_tde_and_force_default_deny(self):
        self.assertEqual(self.sql.count(') USING tde_heap;'), len(self.tables))
        for table in self.tables:
            self.assertIn('ALTER TABLE ai_invest.' + table + ' ENABLE ROW LEVEL SECURITY;', self.sql)
            self.assertIn('ALTER TABLE ai_invest.' + table + ' FORCE ROW LEVEL SECURITY;', self.sql)
        self.assertNotIn('CREATE POLICY', self.sql)
        self.assertNotIn('GRANT ', self.sql)
        self.assertIn("RAISE EXCEPTION 'qualified_pg_tde_required'", self.sql)

    def test_source_migration_not_ignored_but_dumps_still_ignored_reg_vf02(self):
        import subprocess
        migration = subprocess.run(['/usr/bin/git', 'check-ignore', '--quiet',
            'backend/migrations/0001_tenant_foundation.sql'], cwd=ROOT, check=False)
        self.assertEqual(migration.returncode, 1)
        dump = subprocess.run(['/usr/bin/git', 'check-ignore', '--quiet', 'sensitive-dump.sql'],
                              cwd=ROOT, check=False)
        self.assertEqual(dump.returncode, 0)

    def test_complete_ownership_reference_and_one_active_binding(self):
        self.assertIn('FOREIGN KEY (tenant_id, portfolio_id, account_id)', self.sql)
        self.assertIn('REFERENCES ai_invest.portfolio (tenant_id, id, account_id)', self.sql)
        self.assertIn('WHERE active AND mode = \'PAPER\'', self.sql)
        self.assertIn('stopped boolean NOT NULL DEFAULT true', self.sql)

    def test_decimal_precision_checked_without_typmod_rounding(self):
        self.assertNotRegex(self.sql, r'\bnumeric\s*\(')
        for name in ('quantity', 'limit_price', 'virtual_capital'):
            self.assertIn('scale(' + name + ') <= 9', self.sql)

    def test_append_only_and_no_credentials_or_live_bootstrap(self):
        self.assertIn('immutable_proposal BEFORE UPDATE OR DELETE', self.sql)
        self.assertIn('immutable_audit BEFORE UPDATE OR DELETE', self.sql)
        for fragment in ('CREATE EXTENSION', 'CREATE ROLE', 'PASSWORD ', 'LIVE', 'pg_tde_set_key', 'api_secret'):
            self.assertNotIn(fragment, self.sql)
        self.assertTrue(self.sql.rstrip().endswith('COMMIT;'))


if __name__ == '__main__':
    unittest.main()
