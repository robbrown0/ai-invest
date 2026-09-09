#!/usr/bin/python3 -I
"""Private local control surface. Demo is disconnected; PAPER reports blockers."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import subprocess
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from ai_invest_core.intents import TradeIntent, Mode, Side, decimal_text
from ai_invest_core.synthetic import SyntheticStore, SyntheticBroker, SCOPES, initialize
from ai_invest_core.workflow import Workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    paper = modes.add_parser('paper-readiness', help='non-secret fixed-target readiness, no credentials')
    demo = modes.add_parser('demo', help='SYNTHETIC ONLY: no network, credentials or actual account data')
    demo.add_argument('--state-dir', required=True, type=Path)
    demo.add_argument('--tenant', choices=('a', 'b'), default='a')
    actions = demo.add_subparsers(dest='action', required=True)
    for command in ('init', 'exercise', 'status', 'reconcile', 'resume', 'stop', 'audit', 'complete-fill'):
        actions.add_parser(command)
    propose = actions.add_parser('propose')
    propose.add_argument('--quantity', default='0.5')
    propose.add_argument('--limit', default='20.01')
    submit = actions.add_parser('submit')
    submit.add_argument('intent', type=UUID)
    submit.add_argument('--fault', choices=('none', 'timeout', 'crash-after-accept', 'partial'), default='none')
    args = parser.parse_args()
    if args.mode == 'paper-readiness':
        print(json.dumps({'mode': 'PAPER', 'ready': False,
            'blocked_by': ['encrypted_database_not_provisioned', 'runtime_tenant_access_not_qualified',
                           'protected_credential_provisioning_not_ready', 'paper_execution_not_connected'],
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}))
        return 2
    store = broker = None
    try:
        if args.action in ('init', 'exercise'):
            initialize(args.state_dir)
        store, broker = SyntheticStore(args.state_dir), SyntheticBroker(args.state_dir)
        scope = SCOPES[args.tenant == 'b']
        app = Workflow(store, broker, scope)
        detail = None
        if args.action == 'exercise':
            # Fresh synthetic directory only. Child stdout contains no real data.
            app.reconcile()
            app.resume()
            now = datetime.now(timezone.utc)
            value = TradeIntent(scope, uuid4(), broker.security_id, Mode.PAPER, Side.BUY,
                decimal_text('0.5'), decimal_text('20.01'), now, now + timedelta(minutes=15))
            identifier = app.record(value)
            command = ['/usr/bin/python3', '-I', '-B', str(ROOT/'scripts/v0.py'), 'demo',
                '--state-dir', str(args.state_dir), '--tenant', args.tenant]
            crashed = subprocess.run(command + ['submit', identifier, '--fault', 'crash-after-accept'],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if crashed.returncode != 75 or app.status()['orders'][identifier]['status'] != 'UNKNOWN':
                raise ValueError()
            recovered = subprocess.run(command + ['reconcile'], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if recovered.returncode != 0 or app.dispatch(identifier) != 'FILLED': raise ValueError()
            if broker.snapshot(scope)['submissions'] != 1: raise ValueError()
            detail = 'process_crash_reconciled_without_resubmission'
        elif args.action == 'propose':
            now = datetime.now(timezone.utc)
            value = TradeIntent(scope, uuid4(), broker.security_id, Mode.PAPER, Side.BUY,
                decimal_text(args.quantity), decimal_text(args.limit), now, now + timedelta(minutes=15))
            detail = app.record(value)
        elif args.action == 'submit':
            broker.timeout = args.fault == 'timeout'
            broker.partial = args.fault == 'partial'
            detail = app.dispatch(str(args.intent), crash_after_accept=args.fault == 'crash-after-accept')
        elif args.action in ('reconcile', 'resume', 'stop'):
            getattr(app, args.action)()
        elif args.action == 'complete-fill':
            for order in app.status()['orders'].values():
                broker.complete(scope, order['client_id'])
            app.reconcile()
        state = app.status()
        print(json.dumps({'mode': 'DISCONNECTED_SYNTHETIC_ONLY', 'result': detail,
            'cash': state['cash'], 'position': state['position'], 'reserved': state['reserved'],
            'stopped': state['stopped'], 'reconciled': state['reconciled'],
            'orders': {k: v['status'] for k,v in state['orders'].items()},
            'last_risk': state['decisions'][-1] if state['decisions'] else None,
            'fill_count': len(state['fills']), 'broker_submissions': broker.snapshot(scope)['submissions'],
            'audit': store.events(scope) if args.action == 'audit' else len(store.events(scope)),
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}, sort_keys=True))
        return 0
    except Exception:
        print(json.dumps({'mode': 'DISCONNECTED_SYNTHETIC_ONLY', 'error': 'operation_refused',
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}))
        return 1
    finally:
        if store is not None: store.close()
        if broker is not None: broker.close()


if __name__ == '__main__':
    raise SystemExit(main())
