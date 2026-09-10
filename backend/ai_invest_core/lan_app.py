"""Unauthenticated LAN research shell: no financial data or execution authority."""
import asyncio
import ctypes
from datetime import datetime, timezone
import ipaddress
import json
import logging
import os
from pathlib import Path
import time

from aiohttp import web, ClientSession, ClientTimeout
import psycopg

def lan_address(value):
    address=ipaddress.IPv4Address(value)
    if not any(address in ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16')):
        raise ValueError('private_lan_address_required')
    return str(address)

ADDRESS=lan_address(os.environ.get('AI_INVEST_LAN_ADDRESS',''))
ORIGIN='http://'+ADDRESS+':8443'
SUBNET=ipaddress.ip_network(ADDRESS+'/24',strict=False)
SYMBOLS=('SPY','AAPL','MSFT','NVDA')
MODEL='qwen3-0.6b-q8_0'
MODEL_HASH='9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031'
STATIC=Path('/opt/ai-invest/frontend/lan')
SERVICE=web.AppKey('lan_service',object)
HEADERS={'Cache-Control':'no-store','Pragma':'no-cache','X-Content-Type-Options':'nosniff',
 'Referrer-Policy':'no-referrer','X-Frame-Options':'DENY',
 'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'"}


class Refused(Exception): pass


def unique_object(pairs):
    value={}
    for key,item in pairs:
        if key in value: raise Refused()
        value[key]=item
    return value


def source_allowed(request):
    if request.headers.getall('Host',[])!=[ADDRESS+':8443'] or request.query_string: raise Refused()
    if any(k.lower().startswith('x-forwarded-') or k.lower() in ('forwarded','x-client-cert','authorization','cookie') for k in request.headers): raise Refused()
    peer=ipaddress.ip_address(request.remote)
    if peer not in SUBNET: raise Refused()
    if request.method=='POST' and request.headers.getall('Origin',[])!=[ORIGIN]: raise Refused()


async def database_status():
    """Literal health query only; role has no application-schema/table grant."""
    try:
        async with asyncio.timeout(3):
            async with await psycopg.AsyncConnection.connect(host='/var/run/postgresql',dbname='ai_invest',
                user='ai_lan_status',connect_timeout=2,autocommit=True) as db:
                row=await (await db.execute("SELECT current_user='ai_lan_status', NOT pg_is_in_recovery(), current_setting('pg_tde.wal_encrypt')='on'" )).fetchone()
                return 'READY_WAL_ENCRYPTION_ON' if row==(True,True,True) else 'NOT_READY'
    except Exception: return 'UNAVAILABLE'


class LocalModel:
    async def exchange(self,path,payload=None):
        if path not in ('/health','/v1/chat/completions'): raise Refused()
        async with ClientSession(timeout=ClientTimeout(total=90 if payload else 2),trust_env=False,
            auto_decompress=False) as client:
            async with client.request('POST' if payload else 'GET','http://research-model:8080'+path,
                json=payload,allow_redirects=False,headers={'Accept-Encoding':'identity'}) as response:
                if response.status!=200 or response.content_type!='application/json': raise Refused()
                if response.headers.get('Content-Encoding','identity')!='identity': raise Refused()
                body=bytearray()
                async for chunk in response.content.iter_chunked(4096):
                    body.extend(chunk)
                    if len(body)>16384: raise Refused()
                return json.loads(body,object_pairs_hook=unique_object)

    async def health(self):
        try: return 'READY' if (await self.exchange('/health')).get('status')=='ok' else 'UNAVAILABLE'
        except Exception: return 'UNAVAILABLE'

    async def research(self,symbol):
        if symbol not in SYMBOLS: raise Refused()
        schema={'type':'object','properties':{key:{'type':'string'} for key in ('bull_question','bear_question','evidence_needed')},
            'required':['bull_question','bear_question','evidence_needed'],'additionalProperties':False}
        payload={'model':MODEL,'stream':False,'max_tokens':256,'temperature':0.2,
            'chat_template_kwargs':{'enable_thinking':False},
            'response_format':{'type':'json_schema','json_schema':{'name':'research_questions','strict':True,'schema':schema}},
            'messages':[{'role':'system','content':'Generate research QUESTIONS, not facts or investment advice. No live market evidence or portfolio is available. Return three short strings in JSON: bull_question, bear_question, evidence_needed. Never assert a current price, return, catalyst or trading recommendation. Maximum 25 words per string. /no_think'},
                        {'role':'user','content':'Public security to investigate: '+symbol}]}
        result=await self.exchange('/v1/chat/completions',payload)
        choices=result.get('choices')
        if type(choices) is not list or len(choices)!=1 or choices[0].get('finish_reason')!='stop': raise Refused()
        content=choices[0]['message']['content']
        if type(content) is not str or len(content)>2048: raise Refused()
        value=json.loads(content,object_pairs_hook=unique_object)
        if type(value) is not dict or set(value)!=set(schema['required']): raise Refused()
        if any(type(x) is not str or not 1<=len(x)<=400 or any(ord(c)<32 for c in x) for x in value.values()): raise Refused()
        return value


class Service:
    def __init__(self,model=None,status=database_status,static=STATIC):
        self.model=model or LocalModel();self.status=status;self.static=static
        self.lock=asyncio.Lock();self.next_research=0
        self.cached_status=None;self.status_until=0;self.status_lock=asyncio.Lock()

    async def handle(self,request):
        source_allowed(request)
        if request.method=='GET' and request.path in ('/','/app.js','/app.css'):
            name={'/':'index.html','/app.js':'app.js','/app.css':'app.css'}[request.path]
            kind={'/':'text/html','/app.js':'application/javascript','/app.css':'text/css'}[request.path]
            return web.Response(body=(self.static/name).read_bytes(),content_type=kind)
        if request.method=='GET' and request.path=='/api/status':
            async with self.status_lock:
                if self.cached_status is None or time.monotonic()>=self.status_until:
                    db,model=await asyncio.gather(self.status(),self.model.health())
                    self.cached_status={'application':'RUNNING','transport':'HTTP_PUBLIC_TO_LAN','database':db,'local_model':model,
                        'model':MODEL,'mode':'PAPER_ONLY','credential_entry':False,'account_data':'NOT_CONNECTED',
                        'execution_enabled':False,'gate2_passed':False,'observed_at':datetime.now(timezone.utc).isoformat()}
                    self.status_until=time.monotonic()+5
                return web.json_response(self.cached_status)
        # Reject credential/order/unknown endpoints without parsing any body.
        if request.method!='POST' or request.path!='/api/research': raise Refused()
        if request.content_type!='application/json' or request.headers.get('Content-Encoding','identity')!='identity': raise Refused()
        async with asyncio.timeout(3):
            data=json.loads(await request.read(),object_pairs_hook=unique_object)
        if type(data) is not dict or set(data)!={'symbol'} or data['symbol'] not in SYMBOLS: raise Refused()
        if self.lock.locked() or time.monotonic()<self.next_research: raise Refused()
        async with self.lock:
            self.next_research=time.monotonic()+15
            try:
                async with asyncio.timeout(92): questions=await self.model.research(data['symbol'])
                return web.json_response({'symbol':data['symbol'],'questions':questions,'model':MODEL,'model_sha256':MODEL_HASH,
                    'prompt_version':'PUBLIC_QUESTIONS_1','generated_at':datetime.now(timezone.utc).isoformat(),
                    'action':'WATCH_ONLY','evidence_status':'NO_CURRENT_MARKET_SOURCES','confidence':'UNCALIBRATED',
                    'risk_result':'BLOCKED','risk_reasons':['NO_AUTHENTICATED_APPROVAL','NO_CONNECTED_ACCOUNT','NO_FRESH_MARKET_EVIDENCE'],
                    'execution_enabled':False})
            finally: self.next_research=time.monotonic()+15


@web.middleware
async def boundary(request,handler):
    try: result=await request.app[SERVICE].handle(request)
    except Exception: result=web.json_response({'error':'unavailable_or_refused','execution_enabled':False},status=400)
    result.headers.update(HEADERS);result.force_close()
    return result


def application(service=None):
    app=web.Application(middlewares=[boundary],client_max_size=128)
    app[SERVICE]=service or Service()
    async def unavailable(request): raise web.HTTPNotFound()
    app.router.add_route('*','/{path:.*}',unavailable)
    return app


def main():
    logging.disable(logging.CRITICAL)
    try:
        if os.getuid()!=10004 or ctypes.CDLL(None).ai_guard_status()!=1: raise Refused()
        web.run_app(application(),host='0.0.0.0',port=8080,print=None,access_log=None,
            handler_args={'max_line_size':2048,'max_field_size':2048,'keepalive_timeout':5},shutdown_timeout=5)
    except BaseException: return 1
    return 0
