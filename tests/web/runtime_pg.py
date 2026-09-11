"""Opt-in real PostgreSQL web-role transaction/RLS test; synthetic and rolled back."""
import asyncio
import json
import sys
from uuid import UUID,uuid4
sys.path[:0]=['/opt/ai-invest/backend','/opt/ai-invest/execution']
from ai_invest_execution.web_store import WebStore


async def main():
    store=await WebStore.open()
    try:
        if await store.rows(): raise RuntimeError() # Never exercise over owner account data.
        class RollbackTest(Exception): pass
        try:
            async with store.db.transaction():
                identifier=uuid4()
                await store.save(identifier,UUID(int=900),uuid4(),{'public_synthetic_fixture':True},'a'*64,'connected')
                if (await store.get(identifier))['state']!='CONNECTED': raise RuntimeError()
                await store.refreshed(identifier,{'public_synthetic_fixture':'updated'},'a'*64)
                await store.disconnect(identifier,'a'*64)
                if (await store.get(identifier))['credential_version'] is not None: raise RuntimeError()
                other=UUID(int=1)
                row=await (await store.db.execute('SELECT count(*) FROM ai_invest.web_connection WHERE tenant_id=%s',(other,))).fetchone()
                if row!=(0,): raise RuntimeError()
                for sql,args in (("INSERT INTO ai_invest.web_connection (tenant_id,id,broker_account_id,state) VALUES (%s,%s,%s,'DISCONNECTED')",(other,uuid4(),uuid4())),
                    ('DELETE FROM ai_invest.web_event',()),('SET ROLE ai_tenant_a',()),('UPDATE ai_invest.runtime_identity SET tenant_id=tenant_id',())):
                    try:
                        async with store.db.transaction(): await store.db.execute(sql,args)
                    except Exception as error:
                        if getattr(error,'sqlstate',None)!='42501': raise
                    else: raise RuntimeError()
                count=await (await store.db.execute('SELECT count(*) FROM ai_invest.web_event WHERE connection_id=%s',(identifier,))).fetchone()
                if count!=(3,): raise RuntimeError()
                raise RollbackTest()
        except RollbackTest: pass
        if await store.rows(): raise RuntimeError()
        print(json.dumps({'web_postgres_transactions':'PASS','cross_tenant_insert_denied':'PASS','foreign_row_read':'NOT_TESTED','audit_mutation_denied':'PASS',
            'synthetic_rows_rolled_back':True,'broker_connected':False,'gate2_passed':False}))
    finally: await store.db.close()


try: asyncio.run(main())
except Exception:
    print('{"web_postgres_test":"FAIL"}')
    raise SystemExit(1)
