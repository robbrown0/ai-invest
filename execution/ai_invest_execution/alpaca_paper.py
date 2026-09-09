"""Read-only PAPER account transport. No CLI, provisioning, order or live API.

Not wired to an application. Before credential use, qualify execution process
protections, a whole-operation deadline, and encrypted tenant-bound persistence.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
import http.client
import json
import re
import ssl
from uuid import UUID

from ai_invest_core.intents import Scope, decimal_text

MAX_RESPONSE = 65536


def tls_context():
    # Avoid create_default_context's SSLKEYLOGFILE environment processing.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_verify_locations(cafile='/etc/ssl/certs/ca-certificates.crt')
    if context.keylog_filename is not None or not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
        raise PaperReadError()
    return context


class PaperReadError(RuntimeError):
    def __init__(self, reason='paper_read_failed'):
        allowed = {'paper_read_failed', 'paper_credentials_rejected', 'paper_rate_limited',
                   'paper_response_invalid'}
        self.reason = reason if reason in allowed else 'paper_read_failed'
        super().__init__(self.reason)


@dataclass(frozen=True, slots=True, repr=False)
class PaperCredentials:
    key_id: str = field(repr=False)
    secret_key: str = field(repr=False)

    def __post_init__(self):
        if any(type(value) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,256}', value) is None
               for value in (self.key_id, self.secret_key)):
            raise PaperReadError('paper_credentials_rejected')

    def __repr__(self):
        return 'PaperCredentials(<redacted>)'


@dataclass(frozen=True, slots=True, repr=False)
class AccountSnapshot:
    scope: Scope
    cash: Decimal
    equity: Decimal
    status: str
    trading_blocked: bool
    account_blocked: bool
    received_at: datetime

    def __repr__(self):
        return 'AccountSnapshot(<restricted financial data>)'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PaperReadError('paper_response_invalid')
        result[key] = value
    return result


def reject_constant(value):
    raise PaperReadError('paper_response_invalid')


def decode_account(body, scope, expected_account_id):
    try:
        if type(scope) is not Scope or type(expected_account_id) is not UUID or expected_account_id.int == 0:
            raise ValueError()
        if type(body) is not bytes or len(body) > MAX_RESPONSE:
            raise ValueError()
        value = json.loads(body, object_pairs_hook=unique_object, parse_constant=reject_constant)
        if type(value) is not dict or value.get('currency') != 'USD':
            raise ValueError()
        if value.get('id') != str(expected_account_id):
            raise ValueError()
        if any(type(value.get(name)) is not bool for name in ('trading_blocked', 'account_blocked')):
            raise ValueError()
        if type(value.get('status')) is not str:
            raise ValueError()
        # Unknown status is not silently treated as active. No order authority here.
        status = 'ACTIVE' if value['status'] == 'ACTIVE' else 'NOT_ACTIVE'
        return AccountSnapshot(scope, decimal_text(value['cash'], places=9, signed=True),
                               decimal_text(value['equity'], places=9, signed=True), status,
                               value['trading_blocked'], value['account_blocked'], datetime.now(timezone.utc))
    except Exception:
        raise PaperReadError('paper_response_invalid') from None


class AlpacaPaperAccountReader:
    """Fixed destination; callers cannot choose URLs, methods, paths or proxies."""
    __slots__ = ('_credentials', '_scope', '_expected_account_id')

    def __init__(self, credentials, scope, expected_account_id):
        if type(credentials) is not PaperCredentials:
            raise PaperReadError('paper_credentials_rejected')
        self._credentials = credentials
        if type(scope) is not Scope or type(expected_account_id) is not UUID or expected_account_id.int == 0:
            raise PaperReadError('paper_response_invalid')
        self._scope = scope
        self._expected_account_id = expected_account_id

    def __repr__(self):
        return 'AlpacaPaperAccountReader(<redacted>)'

    def read_account(self):
        return decode_account(self._get('/v2/account'), self._scope, self._expected_account_id)

    def _get(self, path, *, market_data=False):
        # Internal transport only. Public operations construct every path below.
        host = 'data.alpaca.markets' if market_data else 'paper-api.alpaca.markets'
        connection = None
        try:
            connection = http.client.HTTPSConnection(host, port=443,
                timeout=5, context=tls_context())
            connection.set_debuglevel(0)
            connection.request('GET', path, headers={
                'APCA-API-KEY-ID': self._credentials.key_id,
                'APCA-API-SECRET-KEY': self._credentials.secret_key,
                'Accept': 'application/json', 'Accept-Encoding': 'identity'})
            response = connection.getresponse()
            if response.status in (401, 403):
                raise PaperReadError('paper_credentials_rejected')
            if response.status == 429:
                raise PaperReadError('paper_rate_limited')
            if response.status != 200:
                raise PaperReadError()
            if response.getheader('Content-Encoding', 'identity') != 'identity':
                raise PaperReadError('paper_response_invalid')
            content_type = response.getheader('Content-Type', '').split(';', 1)[0].strip().lower()
            if content_type != 'application/json':
                raise PaperReadError('paper_response_invalid')
            length = response.getheader('Content-Length')
            if length is not None and (not length.isascii() or not length.isdecimal()
                                       or len(length) > 10 or int(length) > MAX_RESPONSE):
                raise PaperReadError('paper_response_invalid')
            body = response.read(MAX_RESPONSE + 1)
            if length is not None and len(body) != int(length):
                raise PaperReadError('paper_response_invalid')
            if len(body) > MAX_RESPONSE:
                raise PaperReadError('paper_response_invalid')
            return body
        except PaperReadError:
            raise
        except Exception:
            raise PaperReadError() from None
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass  # Never disclose raw transport/credential-bearing exceptions.

    def _project(self, path, kind, mapper, *, array=True, market_data=False):
        self.read_account()  # Verify expected account before any scoped projection.
        try:
            value = json.loads(self._get(path, market_data=market_data),
                object_pairs_hook=unique_object, parse_constant=reject_constant, parse_float=Decimal)
            if array:
                if type(value) is not list or len(value) >= 200:
                    raise ValueError()  # A full page is incomplete, never an absence claim.
                items = tuple(mapper(item) for item in value)
            else:
                items = (mapper(value),)
            return PaperProjection(self._scope, kind, items, datetime.now(timezone.utc))
        except Exception:
            raise PaperReadError('paper_response_invalid') from None

    def positions(self):
        return self._project('/v2/positions', 'positions', position_fields)

    def orders(self):
        # Bounded recent history, NOT complete fill history or reconciliation proof.
        return self._project('/v2/orders?status=all&limit=200&direction=desc&nested=false', 'recent_orders', order_fields)

    def latest_quote(self, symbol):
        if type(symbol) is not str or re.fullmatch(r'[A-Z]{1,5}', symbol) is None:
            raise PaperReadError('paper_response_invalid')
        def fields(value):
            if value['symbol'] != symbol: raise ValueError()
            quote = value['quote']
            return {'symbol': symbol, 'feed': 'iex', 'bid': amount(quote['bp']),
                    'ask': amount(quote['ap']), 'time': timestamp(quote['t'])}
        return self._project('/v2/stocks/' + symbol + '/quotes/latest?feed=iex', 'quote', fields, array=False, market_data=True)

    def clock(self):
        def fields(value):
            if type(value['is_open']) is not bool: raise ValueError()
            return {'is_open': value['is_open'], 'timestamp': timestamp(value['timestamp']),
                    'next_close': timestamp(value['next_close']), 'next_open': timestamp(value['next_open'])}
        return self._project('/v2/clock', 'clock', fields, array=False)


@dataclass(frozen=True, slots=True, repr=False)
class PaperProjection:
    scope: Scope
    kind: str
    items: tuple
    received_at: datetime

    def __repr__(self):
        return 'PaperProjection(<restricted account data>)'


def amount(value):
    if type(value) is Decimal:
        if (not value.is_finite() or value.as_tuple().exponent < -9
            or value.as_tuple().exponent > 9 or abs(value) > Decimal('1000000000')):
            raise ValueError()
        value = format(value, 'f')
    elif type(value) is int:
        value = str(value)
    return decimal_text(value, places=9, signed=True)


def timestamp(value):
    if type(value) is not str or len(value) > 64: raise ValueError()
    result = datetime.fromisoformat(value)
    if result.tzinfo is None: raise ValueError()
    return result.astimezone(timezone.utc)


def identifier(value):
    if type(value) is not str or len(value) != 36: raise ValueError()
    parsed = UUID(value)
    if parsed.int == 0: raise ValueError()
    return str(parsed)


def symbol_field(value):
    if type(value) is not str or re.fullmatch(r'[A-Z][A-Z0-9.\-]{0,14}', value) is None: raise ValueError()
    return value


def position_fields(value):
    if value['asset_class'] != 'us_equity' or value['side'] not in ('long', 'short'): raise ValueError()
    return {'asset_id': identifier(value['asset_id']), 'symbol': symbol_field(value['symbol']),
            'quantity': amount(value['qty']), 'side': value['side'], 'market_value': amount(value['market_value'])}


def order_fields(value):
    if type(value['client_order_id']) is not str or re.fullmatch(r'[A-Za-z0-9_\-]{1,48}', value['client_order_id']) is None:
        raise ValueError()
    if value['side'] not in ('buy', 'sell') or value['asset_class'] != 'us_equity': raise ValueError()
    if type(value['status']) is not str or re.fullmatch(r'[a-z_]{1,32}', value['status']) is None: raise ValueError()
    return {'id': identifier(value['id']), 'client_order_id': value['client_order_id'],
            'asset_id': identifier(value['asset_id']), 'symbol': symbol_field(value['symbol']),
            'side': value['side'], 'quantity': amount(value['qty']), 'filled_quantity': amount(value['filled_qty']),
            'filled_avg_price': None if value['filled_avg_price'] is None else amount(value['filled_avg_price']),
            'status': value['status'], 'submitted_at': timestamp(value['submitted_at'])}
