#!/usr/local/bin/python3 -I
"""Real encrypted PostgreSQL, disconnected synthetic broker. No credentials."""
import argparse
import ctypes
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID, uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from ai_invest_core.intents import TradeIntent, Mode, Side, decimal_text
from ai_invest_core.postgres import PostgresLedger
from ai_invest_core.postgres_synthetic import PostgresSyntheticBroker
from ai_invest_core.synthetic import SCOPES
from ai_invest_core.workflow import Workflow


def connect():
    import psycopg
    uid=os.getuid()
    if uid not in (10001,10002) or ctypes.CDLL(None).ai_guard_status()!=1: raise ValueError()
    return psycopg.connect(host='/var/run/postgresql',dbname='ai_invest',
        user='ai_tenant_a' if uid==10001 else 'ai_tenant_b',connect_timeout=5,autocommit=True,
        options='-c statement_timeout=5000 -c lock_timeout=5000')


def isolation(connection,scope):
    other=SCOPES[scope==SCOPES[0]]
    for table in ('runtime_ledger','runtime_event','synthetic_broker'):
        if connection.execute('SELECT count(*) FROM ai_invest.'+table+' WHERE tenant_id=%s',(other.tenant_id,)).fetchone()!=(0,):
            raise ValueError()
    for table in ('runtime_ledger','synthetic_broker'):
        if connection.execute('UPDATE ai_invest.'+table+' SET body=body WHERE tenant_id=%s',(other.tenant_id,)).rowcount!=0:
            raise ValueError()
    for query in ('SET ROLE '+('ai_tenant_b' if scope==SCOPES[0] else 'ai_tenant_a'),
        'UPDATE ai_invest.runtime_identity SET tenant_id=tenant_id',
        'DELETE FROM ai_invest.runtime_event'):
        try: connection.execute(query)
        except Exception as error:
            if getattr(error,'sqlstate',None)!='42501': raise
        else: raise ValueError()
    try:
        connection.execute('INSERT INTO ai_invest.runtime_event (tenant_id,account_id,revision,kind,body) VALUES (%s,%s,99999,%s,%s::jsonb)',
            (other.tenant_id,other.account_id,'cross_tenant','{}'))
    except Exception as error:
        if getattr(error,'sqlstate',None)!='42501': raise
    else: raise ValueError()
    connection.execute("SET app.tenant_id='00000000-0000-0000-0000-00000000000b'")
    if connection.execute('SELECT tenant_id FROM ai_invest.runtime_identity').fetchall()!=[(scope.tenant_id,)]: raise ValueError()
    return 'PASS'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('status','exercise','recover','reconcile','stop','isolation','submit-fault'))
    parser.add_argument('--intent',type=UUID)
    args=parser.parse_args()
    connections=[]
    try:
        connections=[connect(),connect()]
        scope=SCOPES[os.getuid()==10002]
        store=PostgresLedger(connections[0],scope)
        broker=PostgresSyntheticBroker(connections[1],scope)
        app=Workflow(store,broker,scope)
        detail=None
        if args.action=='exercise':
            if app.status()['intents'] or broker.snapshot(scope)['submissions']: raise ValueError()
            app.reconcile()
            app.resume()
            now=datetime.now(timezone.utc)
            intent=TradeIntent(scope,uuid4(),broker.security_id,Mode.PAPER,Side.BUY,
                decimal_text('0.5'),decimal_text('20.01'),now,now+timedelta(minutes=15))
            identifier=app.record(intent)
            result=subprocess.run(['/usr/local/bin/python3','-I','-B',str(Path(__file__).resolve()),
                'submit-fault','--intent',identifier],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,timeout=20,env={'LD_PRELOAD':'/usr/local/lib/ai-invest/runtime_guard.so'})
            if result.returncode!=75 or app.status()['orders'][identifier]['status']!='UNKNOWN' or broker.snapshot(scope)['submissions']!=1:
                raise ValueError()
            detail='accepted_then_process_exit_unknown_persisted'
        elif args.action=='submit-fault':
            if args.intent is None: raise ValueError()
            app.dispatch(str(args.intent),crash_after_accept=True)
            raise ValueError()
        elif args.action=='recover':
            before=broker.snapshot(scope)['submissions']
            if before!=1 or len(app.status()['orders'])!=1: raise ValueError()
            app.reconcile()
            identifier=next(iter(app.status()['orders']))
            if app.dispatch(identifier)!='FILLED' or broker.snapshot(scope)['submissions']!=before: raise ValueError()
            app.reconcile()
            detail='reconciled_without_resubmission'
        elif args.action=='isolation': detail=isolation(connections[0],scope)
        elif args.action in ('reconcile','stop'): getattr(app,args.action)()
        state=app.status()
        print(json.dumps({'mode':'POSTGRES_DISCONNECTED_SYNTHETIC','action':args.action,'passed':True,'result':detail,
            'cash':state['cash'],'position':state['position'],'reserved':state['reserved'],
            'orders':[v['status'] for v in state['orders'].values()],
            'intents':len(state['intents']),'risk_decisions':len(state['decisions']),
            'fills':len(state['fills']),'audit_events':len(store.events(scope)),
            'broker_submissions':broker.snapshot(scope)['submissions'],
            'gate2_passed':False,'secret_entry_authorized':False,'runtime_crash_suppression_qualified':False}))
        return 0
    except Exception:
        print(json.dumps({'mode':'POSTGRES_DISCONNECTED_SYNTHETIC','passed':False,'error':'operation_refused',
            'secret_entry_authorized':False,'runtime_crash_suppression_qualified':False}))
        return 1
    finally:
        for connection in connections: connection.close()


if __name__=='__main__': raise SystemExit(main())
