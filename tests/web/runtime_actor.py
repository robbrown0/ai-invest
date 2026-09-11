"""Explicit real-PostgreSQL synthetic rollback test; never a brokerage request."""
import asyncio
import json
import logging
import sys
from uuid import uuid4
sys.path[:0]=['/opt/ai-invest/backend','/opt/ai-invest/execution']
import psycopg
from ai_invest_execution.paper_bootstrap import CONSOLE_ACTOR
from ai_invest_execution.web_store import WebStore


async def check():
    store=await WebStore.open()
    try:
        identifier=uuid4()
        async with store.db.transaction():
            await store.save(identifier,uuid4(),uuid4(),{'synthetic':True},CONSOLE_ACTOR,'connected')
            row=await (await store.db.execute('SELECT count(*) FROM ai_invest.web_event WHERE tenant_id=%s AND connection_id=%s AND actor=%s',(store.tenant,identifier,CONSOLE_ACTOR))).fetchone()
            assert row==(1,)
            try:
                async with store.db.transaction():
                    await store.event(identifier,'physical-console','connected')
            except psycopg.errors.CheckViolation: pass
            else: raise RuntimeError('constraint_missing')
            raise psycopg.Rollback()
        row=await (await store.db.execute('SELECT count(*) FROM ai_invest.web_connection WHERE tenant_id=%s AND id=%s',(store.tenant,identifier))).fetchone()
        assert row==(0,)
    finally: await store.db.close()


logging.disable(logging.CRITICAL)
try: asyncio.run(check());passed=True
except BaseException: passed=False
print(json.dumps({'test':'paper_actor_real_postgresql','passed':passed,'synthetic_rolled_back':passed,'broker_contacted':False}))
raise SystemExit(0 if passed else 1)
