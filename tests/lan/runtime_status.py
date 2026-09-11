"""Real health-role deny tests: never selects account row values."""
import asyncio
import json
import sys
sys.path.insert(0,'/opt/ai-invest/backend')
import psycopg
from ai_invest_core.lan_app import database_status

async def main():
    if await database_status()!='READY_WAL_ENCRYPTION_ON': raise RuntimeError()
    async with await psycopg.AsyncConnection.connect(host='/var/run/postgresql',dbname='ai_invest',user='ai_lan_status',autocommit=True) as db:
        for query in ('SELECT 1 FROM ai_invest.web_connection LIMIT 0','SELECT 1 FROM ai_invest.runtime_identity LIMIT 0',
                      'SELECT 1 FROM ai_invest.runtime_ledger LIMIT 0','SET ROLE ai_web_a','SET ROLE ai_tenant_a'):
            try: await db.execute(query)
            except Exception as error:
                if getattr(error,'sqlstate',None)!='42501': raise
            else: raise RuntimeError()
    print(json.dumps({'database_health':'PASS','application_access_denied':'PASS','role_switch_denied':'PASS','broker_connected':False}))

try: asyncio.run(main())
except Exception:
    print('{"health_role_test":"FAIL"}')
    raise SystemExit(1)
