"""Immutable tenant-bound trade data. An intent is NEVER an execution permit."""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Context, Decimal, localcontext
from enum import Enum
import hashlib
import json
import re
from uuid import UUID


class InvalidIntent(ValueError):
    def __init__(self):
        super().__init__('invalid_trade_intent')


class Mode(str, Enum):
    BACKTEST = 'BACKTEST'
    PAPER = 'PAPER'
    SHADOW = 'SHADOW'


class Side(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'


def require(condition):
    if not condition:
        raise InvalidIntent()


def decimal_text(value, *, places=9, maximum=Decimal('1000000000'), signed=False):
    """Parse bounded plain decimals; no floats, scientific notation or rounding."""
    require(type(value) is str and 0 < len(value) <= 40)
    sign = '-?' if signed else ''
    require(re.fullmatch(sign + r'(?:0|[1-9][0-9]*)(?:\.[0-9]{1,' + str(places) + r'})?', value) is not None)
    number = Decimal(value)
    require(number.is_finite() and -maximum <= number <= maximum)
    return number


def canonical_decimal(value):
    text = format(value, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return '0' if text == '-0' else text


@dataclass(frozen=True, slots=True, repr=False)
class Scope:
    tenant_id: UUID
    account_id: UUID
    portfolio_id: UUID

    def __post_init__(self):
        require(all(type(item) is UUID and item.int != 0 for item in
                    (self.tenant_id, self.account_id, self.portfolio_id)))

    def __repr__(self):
        return 'Scope(<internal identifiers>)'


@dataclass(frozen=True, slots=True, repr=False)
class TradeIntent:
    scope: Scope
    intent_id: UUID
    security_id: UUID
    mode: Mode
    side: Side
    quantity: Decimal
    limit_price: Decimal
    created_at: datetime
    expires_at: datetime

    def __post_init__(self):
        require(type(self.scope) is Scope)
        require(all(type(item) is UUID and item.int != 0 for item in (self.intent_id, self.security_id)))
        require(type(self.mode) is Mode and type(self.side) is Side)
        for value in (self.quantity, self.limit_price):
            require(type(value) is Decimal and value.is_finite())
            require(Decimal('0') < value <= Decimal('1000000000'))
            require(value.as_tuple().exponent >= -9)
        require(all(type(value) is datetime and type(value.tzinfo) is timezone
                    for value in (self.created_at, self.expires_at)))
        try:
            created = self.created_at.astimezone(timezone.utc)
            expires = self.expires_at.astimezone(timezone.utc)
        except (ValueError, OverflowError):
            raise InvalidIntent() from None
        require(created < expires)
        object.__setattr__(self, 'created_at', created)
        object.__setattr__(self, 'expires_at', expires)

    def __repr__(self):
        return 'TradeIntent(<restricted financial data; no authority>)'

    @classmethod
    def from_advisory(cls, scope, payload):
        # Scope comes from authenticated application context, never model fields.
        names = {'intent_id', 'security_id', 'mode', 'side', 'quantity', 'limit_price',
                 'created_at', 'expires_at'}
        require(type(payload) is dict and set(payload) == names)
        require(all(type(value) is str and len(value) <= 128 for value in payload.values()))
        try:
            return cls(scope, UUID(payload['intent_id']), UUID(payload['security_id']),
                       Mode(payload['mode']), Side(payload['side']),
                       decimal_text(payload['quantity']), decimal_text(payload['limit_price']),
                       datetime.fromisoformat(payload['created_at']),
                       datetime.fromisoformat(payload['expires_at']))
        except (ValueError, TypeError, OverflowError):
            raise InvalidIntent() from None

    @property
    def notional(self):
        # Independent of caller/thread Decimal context; never round authoritative values.
        with localcontext(Context(prec=60)):
            return self.quantity * self.limit_price

    def canonical_bytes(self):
        value = {'version': 1, 'tenant_id': str(self.scope.tenant_id),
                 'account_id': str(self.scope.account_id), 'portfolio_id': str(self.scope.portfolio_id),
                 'intent_id': str(self.intent_id), 'security_id': str(self.security_id),
                 'mode': self.mode.value, 'side': self.side.value,
                 'quantity': canonical_decimal(self.quantity), 'limit_price': canonical_decimal(self.limit_price),
                 'currency': 'USD', 'order_type': 'limit', 'time_in_force': 'day', 'extended_hours': False,
                 'created_at': self.created_at.astimezone(timezone.utc).isoformat(timespec='microseconds'),
                 'expires_at': self.expires_at.astimezone(timezone.utc).isoformat(timespec='microseconds')}
        return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')

    def digest(self):
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
