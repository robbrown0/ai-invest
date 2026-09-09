"""Small durable workflow exercised by the disconnected V0 CLI.

This first policy is deliberately synthetic-only. No real broker dispatch is
exposed until PostgreSQL, identity, credentials and financial inputs qualify.
"""
from datetime import datetime, timezone
from decimal import Context, Decimal, localcontext
import json

from .intents import TradeIntent, Mode, Side, canonical_decimal as dec

TERMINAL = {'FILLED', 'CANCELED', 'REJECTED', 'EXPIRED'}
POLICY = 'SYNTHETIC_V0_1'


class WorkflowError(RuntimeError):
    def __init__(self, code='workflow_refused'):
        super().__init__(code if code in {'workflow_refused', 'intent_conflict',
            'reconciliation_required', 'not_found', 'state_inconsistent', 'synthetic_only'} else 'workflow_refused')


def initial_state():
    return {'version': 1, 'mode': 'SYNTHETIC_PAPER', 'cash': '200', 'position': '0',
            'reserved': '0', 'stopped': True, 'stop_epoch': 0, 'reconciled': False,
            'intents': {}, 'decisions': [], 'orders': {}, 'fills': {}}


class Workflow:
    def __init__(self, store, broker, scope, clock=None):
        # No configuration switch can attach this demonstration to Alpaca.
        from .synthetic import SyntheticBroker, SyntheticStore
        if type(store) is not SyntheticStore or type(broker) is not SyntheticBroker:
            raise WorkflowError('synthetic_only')
        self.store, self.broker, self.scope = store, broker, scope
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def status(self):
        return self.store.read(self.scope)

    def record(self, intent):
        if type(intent) is not TradeIntent or intent.scope != self.scope:
            raise WorkflowError()
        with self.store.transaction(self.scope, 'intent_recorded') as state:
            key = str(intent.intent_id)
            value = {'payload': json.loads(intent.canonical_bytes()), 'digest': intent.digest()}
            if key in state['intents'] and state['intents'][key] != value:
                raise WorkflowError('intent_conflict')
            if len(state['intents']) >= 100 and key not in state['intents']:
                raise WorkflowError()
            state['intents'][key] = value
        return key

    def stop(self):
        with self.store.transaction(self.scope, 'stop') as state:
            state['stopped'] = True
            state['stop_epoch'] += 1

    def resume(self):
        with self.store.transaction(self.scope, 'human_resume') as state:
            if not state['reconciled'] or any(o['status'] not in TERMINAL for o in state['orders'].values()):
                raise WorkflowError('reconciliation_required')
            state['stopped'] = False

    def _intent(self, state, key):
        try:
            saved = state['intents'][key]
            payload = saved['payload']
            names = ('intent_id', 'security_id', 'mode', 'side', 'quantity', 'limit_price', 'created_at', 'expires_at')
            intent = TradeIntent.from_advisory(self.scope, {n: payload[n] for n in names})
            if json.loads(intent.canonical_bytes()) != payload or intent.digest() != saved['digest']:
                raise ValueError()
            return intent
        except Exception:
            raise WorkflowError('state_inconsistent') from None

    def dispatch(self, key, *, crash_after_accept=False):
        """Human-triggered; commit UNKNOWN before the sole outbound attempt.

        Account admission serializes with stop. Stop cannot undo an admitted
        request. A timeout, crash or missing lookup NEVER causes another send.
        """
        with localcontext(Context(prec=60)):
            with self.store.transaction(self.scope, 'risk_and_dispatch_admission') as state:
                if key in state['orders']:
                    return state['orders'][key]['status']
                intent = self._intent(state, key)
                market = self.broker.market()
                now = self.clock()
                reasons = []
                if state['stopped']: reasons.append('stopped')
                if not state['reconciled']: reasons.append('reconciliation_required')
                current = self.broker.snapshot(self.scope)
                if current['cash'] != state['cash'] or current['position'] != state['position']:
                    reasons.append('account_changed')
                if set(current['orders']) != {o['client_id'] for o in state['orders'].values()}:
                    reasons.append('unmatched_orders')
                if any(o['status'] not in TERMINAL for o in state['orders'].values()): reasons.append('pending_order')
                if intent.mode is not Mode.PAPER or intent.side is not Side.BUY: reasons.append('buy_paper_only')
                if intent.security_id != self.broker.security_id: reasons.append('unsupported_asset')
                if not intent.created_at <= now < intent.expires_at: reasons.append('intent_expired')
                if not market['open']: reasons.append('market_closed')
                if not 0 <= (now - market['time']).total_seconds() <= 10: reasons.append('stale_quote')
                if not Decimal('5') <= market['bid'] <= market['ask']: reasons.append('invalid_quote')
                if market['ask'] - market['bid'] > market['bid'] * Decimal('0.005'): reasons.append('spread')
                if not market['ask'] <= intent.limit_price <= market['ask'] * Decimal('1.01'): reasons.append('price_limit')
                if intent.notional > Decimal('25'): reasons.append('order_cap')
                turnover = sum((Decimal(o['filled_value']) for o in state['orders'].values()), Decimal(0))
                if turnover + intent.notional > Decimal('80'): reasons.append('demo_turnover_cap')
                if intent.notional > Decimal(state['cash']) - Decimal(state['reserved']): reasons.append('cash')
                if (Decimal(state['position']) + intent.quantity) * intent.limit_price > Decimal('120'): reasons.append('position_cap')
                if len(state['decisions']) >= 200: raise WorkflowError()
                state['decisions'].append({'intent': key, 'digest': intent.digest(), 'policy': POLICY,
                    'result': 'REJECT' if reasons else 'ALLOW', 'reasons': reasons,
                    'time': now.isoformat(), 'stop_epoch': state['stop_epoch'],
                    'cash': state['cash'], 'position': state['position'],
                    'quote': {'bid': dec(market['bid']), 'ask': dec(market['ask']), 'time': market['time'].isoformat()}})
                if reasons:
                    return 'REJECT'
                client = 'ai-' + intent.intent_id.hex
                order = {'client_id': client, 'digest': intent.digest(), 'status': 'UNKNOWN',
                         'quantity': dec(intent.quantity), 'limit_price': dec(intent.limit_price),
                         'filled_quantity': '0', 'filled_value': '0', 'admitted_at': now.isoformat(),
                         'stop_epoch': state['stop_epoch'], 'approval_consumed': True}
                state['orders'][key] = order
                state['reserved'] = dec(intent.notional)
                state['reconciled'] = False
            # Crash here is conservatively UNKNOWN even if no network call began.
            try:
                self.broker.submit(self.scope, order)
                if crash_after_accept:
                    import os
                    os._exit(75)  # Explicit synthetic CLI fault, never a real broker.
            except Exception:
                return 'UNKNOWN'
            self.reconcile()
            return self.status()['orders'][key]['status']

    def reconcile(self):
        """Recompute cumulative accounting; duplicates never add fills twice."""
        bad = False
        with localcontext(Context(prec=60)):
            with self.store.transaction(self.scope, 'reconciliation') as state:
                snapshot = self.broker.snapshot(self.scope)
                managed = {o['client_id'] for o in state['orders'].values()}
                if set(snapshot['orders']) - managed:
                    bad = True
                for key, order in state['orders'].items():
                    found = snapshot['orders'].get(order['client_id'])
                    if found is None:
                        if order['status'] in TERMINAL: bad = True
                        continue  # Not-found is not permission to resend/release.
                    if (type(found) is not dict or set(found) != {'client_id','digest','quantity',
                            'limit_price','filled_quantity','filled_value','status'}
                        or found['client_id'] != order['client_id']):
                        bad = True
                        continue
                    quantity, value = Decimal(found['filled_quantity']), Decimal(found['filled_value'])
                    if (found['digest'] != order['digest'] or found['quantity'] != order['quantity']
                        or found['limit_price'] != order['limit_price']
                        or found['status'] not in TERMINAL | {'ACCEPTED', 'PARTIAL'}
                        or not Decimal(order['filled_quantity']) <= quantity <= Decimal(order['quantity'])
                        or not Decimal(order['filled_value']) <= value <= quantity * Decimal(order['limit_price'])
                        or (quantity > 0 and value <= 0)
                        or (found['status'] == 'FILLED' and quantity != Decimal(order['quantity']))
                        or (order['status'] in TERMINAL and found != {n: order[n] for n in found})):
                        bad = True
                        continue
                    order.update(found)
                # A cumulative order update is not itself a fill audit trail.
                for order in state['orders'].values():
                    fills = [fill for fill in snapshot['fills'].values() if fill['client_id'] == order['client_id']]
                    if (any(Decimal(f['quantity']) <= 0 or Decimal(f['value']) <= 0 for f in fills)
                        or sum((Decimal(f['quantity']) for f in fills), Decimal(0)) != Decimal(order['filled_quantity'])
                        or sum((Decimal(f['value']) for f in fills), Decimal(0)) != Decimal(order['filled_value'])):
                        bad = True
                if any(fill['client_id'] not in managed for fill in snapshot['fills'].values()):
                    bad = True
                if not set(state['fills']).issubset(snapshot['fills']):
                    bad = True
                if not bad:
                    filled = sum((Decimal(o['filled_quantity']) for o in state['orders'].values()), Decimal(0))
                    cost = sum((Decimal(o['filled_value']) for o in state['orders'].values()), Decimal(0))
                    if Decimal(snapshot['cash']) != Decimal('200') - cost or Decimal(snapshot['position']) != filled:
                        bad = True
                    else:
                        state['cash'], state['position'] = dec(Decimal('200') - cost), dec(filled)
                        state['reserved'] = dec(sum(((Decimal(o['quantity']) - Decimal(o['filled_quantity'])) *
                            Decimal(o['limit_price']) for o in state['orders'].values() if o['status'] not in TERMINAL), Decimal(0)))
                        # Broker supplies immutable fill IDs; exact duplicates are benign.
                        for identifier, fill in snapshot['fills'].items():
                            if identifier in state['fills'] and state['fills'][identifier] != fill:
                                bad = True
                            else:
                                state['fills'][identifier] = fill
                state['reconciled'] = not bad and all(o['status'] in TERMINAL for o in state['orders'].values())
                if bad:
                    state['stopped'] = True
                    state['stop_epoch'] += 1
        if bad:
            raise WorkflowError('state_inconsistent')
        return self.status()
