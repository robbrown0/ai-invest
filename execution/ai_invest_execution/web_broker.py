"""Bounded asynchronous PAPER-only reads. No broker mutation operation exists."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import json
from uuid import UUID

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from ai_invest_core.intents import Scope
from .alpaca_paper import (PaperCredentials, decode_account, unique_object,reject_constant,
    position_fields,order_fields,tls_context,amount,timestamp)
from .web_store import Refused


def plain(value):
    if isinstance(value,dict): return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [plain(v) for v in value]
    if isinstance(value,(Decimal,UUID)): return str(value)
    if isinstance(value,datetime): return value.isoformat()
    if value is None or type(value) in (str,int,bool): return value
    raise Refused()


class PaperWebReader:
    def __init__(self,credentials,tenant,connection):
        if type(credentials) is not PaperCredentials: raise Refused()
        self.credentials,self.scope=credentials,Scope(tenant,connection,connection)

    async def get(self,path,market=False):
        # All callers below are fixed operations; no supplied URL, proxy or redirect.
        host='https://data.alpaca.markets' if market else 'https://paper-api.alpaca.markets'
        allowed=('/v2/stocks/SPY/quotes/latest?feed=iex',) if market else (
            '/v2/account','/v2/positions','/v2/orders?status=all&limit=200&direction=desc&nested=false','/v2/clock')
        if path not in allowed: raise Refused()
        headers={'APCA-API-KEY-ID':self.credentials.key_id,'APCA-API-SECRET-KEY':self.credentials.secret_key,
                 'Accept':'application/json','Accept-Encoding':'identity'}
        async with ClientSession(timeout=ClientTimeout(total=8,connect=4,sock_read=4),
            connector=TCPConnector(ssl=tls_context(),limit=1),trust_env=False,auto_decompress=False) as client:
            async with client.get(host+path,headers=headers,allow_redirects=False) as response:
                if response.status!=200 or response.content_type!='application/json' or response.headers.get('Content-Encoding','identity')!='identity': raise Refused()
                body=bytearray()
                async for chunk in response.content.iter_chunked(4096):
                    body.extend(chunk)
                    if len(body)>65536: raise Refused()
                return bytes(body)

    async def account(self,expected=None):
        raw=await self.get('/v2/account')
        data=json.loads(raw,object_pairs_hook=unique_object,parse_constant=reject_constant)
        account=UUID(data['id'])
        if expected is not None and account!=expected: raise Refused()
        parsed=decode_account(raw,self.scope,account)
        return account,{'account_id':str(account),'cash':str(parsed.cash),'equity':str(parsed.equity),
            'status':parsed.status,'trading_blocked':parsed.trading_blocked,
            'account_blocked':parsed.account_blocked,'observed_at':parsed.received_at.isoformat()}

    async def dashboard(self,expected):
        async with asyncio.timeout(25):
            account,summary=await self.account(expected)
            result={'account':summary,'positions':[],'orders':[],'market':None,
                    'market_status':'UNAVAILABLE','orders_scope':'Recent orders only; not complete fill reconciliation'}
            for path,key,mapper in (('/v2/positions','positions',position_fields),
                ('/v2/orders?status=all&limit=200&direction=desc&nested=false','orders',order_fields)):
                values=json.loads(await self.get(path),object_pairs_hook=unique_object,parse_constant=reject_constant,parse_float=Decimal)
                if type(values) is not list or len(values)>=200: raise Refused()
                result[key]=plain([mapper(value) for value in values])
            try:
                value=json.loads(await self.get('/v2/stocks/SPY/quotes/latest?feed=iex',True),
                    object_pairs_hook=unique_object,parse_constant=reject_constant,parse_float=Decimal)
                if value['symbol']!='SPY': raise Refused()
                quote=value['quote']
                result['market']=plain({'symbol':'SPY','feed':'IEX','bid':amount(quote['bp']),
                    'ask':amount(quote['ap']),'observed_at':timestamp(quote['t'])})
                result['market_status']='OBSERVED_NOT_EXECUTION_VALIDATED'
            except Exception: pass  # Account reads can work without quote entitlement.
            await self.account(expected)  # Account identity checked again before publication.
            return result
