"""Execution-owned TLS gateway. Browser credentials terminate here, not in research."""
import asyncio
import ctypes
import hashlib
import ipaddress
import json
import logging
import os
from pathlib import Path
import re
import secrets
import ssl
import stat
import time
from urllib.parse import urlsplit
from uuid import UUID,uuid4

from aiohttp import web
from .alpaca_paper import PaperCredentials,unique_object,reject_constant
from .web_broker import PaperWebReader,plain
from .web_store import FileVault,WebStore,Refused

STATIC=Path('/opt/ai-invest/frontend')
APP=web.AppKey('service',object)
OPERATION_TIMEOUT=30
SECURITY={
    'Cache-Control':'no-store','Pragma':'no-cache','X-Content-Type-Options':'nosniff',
    'Referrer-Policy':'no-referrer','X-Frame-Options':'DENY',
    'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'",
    'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
    'Strict-Transport-Security':'max-age=31536000',
}


def policy(data):
    if type(data) is not dict or set(data)!={'origin','clients'}: raise Refused()
    origin=urlsplit(data['origin'])
    if (origin.scheme!='https' or origin.username or origin.password or origin.path or origin.query or origin.fragment
        or not origin.hostname or origin.port!=8443 or re.fullmatch(r'[a-zA-Z0-9.-]+',origin.hostname) is None): raise Refused()
    clients=data['clients']
    if type(clients) is not list or not 1<=len(clients)<=16 or len(set(clients))!=len(clients): raise Refused()
    if any(type(value) is not str or re.fullmatch('[a-f0-9]{64}',value) is None for value in clients): raise Refused()
    return data['origin'],frozenset(clients)


def authenticated(request,origin,clients):
    transport=request.transport
    channel=transport.get_extra_info('ssl_object') if transport else None
    if channel is None or request.scheme!='https' or channel.session_reused: raise Refused()
    cert=channel.getpeercert(binary_form=True)
    if not cert or len(cert)>8192: raise Refused()
    actor=hashlib.sha256(cert).hexdigest()
    if actor not in clients: raise Refused()
    if request.headers.getall('Host',[])!=[urlsplit(origin).netloc]: raise Refused()
    if any(key.lower() in ('forwarded','x-forwarded-host','x-forwarded-proto','x-client-cert') for key in request.headers): raise Refused()
    remote=ipaddress.ip_address(request.remote)
    networks=('127.0.0.0/8','10.0.0.0/8','172.16.0.0/12','192.168.0.0/16','::1/128','fc00::/7')
    if not any(remote in ipaddress.ip_network(net) for net in networks): raise Refused()
    if request.query_string: raise Refused()
    return actor


class Gateway:
    def __init__(self,store,vault,origin,clients,reader=PaperWebReader,static=STATIC):
        self.store,self.vault,self.origin,self.clients=store,vault,origin,clients
        self.reader,self.static=reader,static
        self.lock=asyncio.Lock()
        self.tokens={}
        self.last_write={}

    def csrf(self,actor):
        challenge=secrets.token_urlsafe(32)
        self.tokens[actor]=(challenge,time.monotonic()+300)
        return challenge

    def consume(self,request,actor):
        if request.headers.getall('Origin',[])!=[self.origin]: raise Refused()
        token,expiry=self.tokens.pop(actor,('',0))
        supplied=request.headers.get('X-CSRF-Token','')
        if not token or len(supplied)>64 or expiry<time.monotonic() or not secrets.compare_digest(token,supplied): raise Refused()
        previous=self.last_write.get(actor,0)
        if time.monotonic()-previous<1: raise Refused()
        self.last_write[actor]=time.monotonic()

    async def handle(self,request,actor):
        if request.method=='GET' and request.path in ('/','/app.js','/app.css'):
            name={'/':'index.html','/app.js':'app.js','/app.css':'app.css'}[request.path]
            content={'/':'text/html','/app.js':'application/javascript','/app.css':'text/css'}[request.path]
            return web.Response(body=(self.static/name).read_bytes(),content_type=content)
        if request.method=='GET' and request.path=='/api/session':
            return web.json_response({'mode':'PAPER','csrf':self.csrf(actor),'execution_enabled':False})
        async with asyncio.timeout(OPERATION_TIMEOUT):
            if self.lock.locked(): raise Refused()
            async with self.lock:
                if request.method=='GET' and request.path=='/api/connections':
                    rows=await self.store.rows()
                    return web.json_response({'connections':[{'id':str(row['id']),'account_id':str(row['broker_account_id']),
                        'state':row['state'],'snapshot':row['snapshot'],'updated_at':plain(row['updated_at'])} for row in rows]})
                if request.method!='POST': raise Refused()
                self.consume(request,actor)
                if request.content_type!='application/json' or request.headers.get('Content-Encoding','identity')!='identity': raise Refused()
                # Fixed schema/size; no form parser, uploads, temp files or request logging.
                data=json.loads(await request.read(),object_pairs_hook=unique_object,parse_constant=reject_constant)
                if type(data) is not dict: raise Refused()
                parts=request.path.split('/')
                if parts==['','api','connections']:
                    if len(await self.store.rows())>=8: raise Refused()
                    return await self.provision(uuid4(),None,data,actor)
                if len(parts)!=5 or parts[1:3]!=['api','connections']: raise Refused()
                identifier=UUID(parts[3])
                row=await self.store.get(identifier)  # Never trust a browser tenant/account claim.
                if parts[4]=='credentials': return await self.provision(identifier,row,data,actor)
                if data!={}: raise Refused()
                if parts[4]=='disconnect':
                    await self.store.disconnect(identifier,actor)  # Durable removal of authority FIRST.
                    if row['credential_version'] is not None: self.vault.remove(row['credential_version'])
                    return web.json_response({'state':'DISCONNECTED','broker_revoked':False})
                if parts[4]=='refresh' and row['state']=='CONNECTED':
                    credentials=self.vault.get(self.store.tenant,identifier,row['credential_version'])
                    snapshot=await self.reader(credentials,self.store.tenant,identifier).dashboard(row['broker_account_id'])
                    self.no_secret_response(snapshot,credentials)
                    await self.store.refreshed(identifier,snapshot,actor)
                    return web.json_response({'refreshed':True})
                raise Refused()

    @staticmethod
    def no_secret_response(value,credentials):
        encoded=json.dumps(value)
        if credentials.key_id in encoded or credentials.secret_key in encoded: raise Refused()

    async def provision(self,identifier,old,data,actor):
        if set(data)!={'key','secret'} or any(type(data[k]) is not str or not 16<=len(data[k])<=256 for k in data): raise Refused()
        credentials=PaperCredentials(data.pop('key'),data.pop('secret'))
        version=self.vault.put(self.store.tenant,identifier,credentials) # Protected storage before API use.
        try:
            account,summary=await self.reader(credentials,self.store.tenant,identifier).account(None if old is None else old['broker_account_id'])
            snapshot={'account':summary}
            self.no_secret_response(snapshot,credentials)
        except BaseException:
            self.vault.remove(version)
            raise
        # An ambiguous DB commit preserves the protected candidate; never delete a
        # possibly active version or advertise success after an exception.
        await self.store.save(identifier,account,version,snapshot,actor,'connected' if old is None else 'replaced')
        if old is not None and old['credential_version'] is not None: self.vault.remove(old['credential_version'])
        return web.json_response({'state':'CONNECTED','id':str(identifier)})


@web.middleware
async def boundary(request,handler):
    try:
        gateway=request.app[APP]
        actor=authenticated(request,gateway.origin,gateway.clients)
        response=await gateway.handle(request,actor)
    except Exception:
        response=web.json_response({'error':'Request refused. Check your connection or retry.'},status=400)
    response.headers.update(SECURITY)
    response.force_close() # Fresh mTLS handshake; no HTTP session/auth cookies.
    return response


def application(gateway):
    app=web.Application(middlewares=[boundary],client_max_size=2048)
    app[APP]=gateway
    async def unused(request): raise Refused()
    app.router.add_route('*','/{tail:.*}',unused)
    return app


def server_tls(directory=Path('/run/ai-invest/tls')):
    d=directory.lstat()
    if not stat.S_ISDIR(d.st_mode) or d.st_uid!=10003 or stat.S_IMODE(d.st_mode)!=0o700: raise Refused()
    for name in ('server.crt','server.key','client-ca.crt'):
        s=(directory/name).lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=10003 or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600 or not 0<s.st_size<=65536: raise Refused()
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version=ssl.TLSVersion.TLSv1_3
    context.verify_mode=ssl.CERT_REQUIRED
    context.options|=ssl.OP_NO_TICKET
    context.num_tickets=0
    def no_interactive_password():
        raise Refused()  # Never let OpenSSL prompt on stdin for an encrypted PEM.
    context.load_cert_chain(directory/'server.crt',directory/'server.key',password=no_interactive_password)
    context.load_verify_locations(cafile=directory/'client-ca.crt')
    if context.keylog_filename is not None: raise Refused()
    return context


def encrypted_mounts():
    expected={'/run/ai-invest/paper','/run/ai-invest/tls','/run/ai-invest/policy','/var/run/postgresql'}
    devices=set()
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        parts=line.split()
        if len(parts)<10 or parts[4] not in expected: continue
        separator=parts.index('-')
        if parts[separator+1]!='ext4' or parts[separator+2]!='/dev/mapper/ai-invest-qualification': raise Refused()
        if not {'nosuid','nodev','noexec'}<=set(parts[5].split(',')): raise Refused()
        devices.add(parts[2])
        expected.remove(parts[4])
    if expected or len(devices)!=1: raise Refused()


async def serve():
    if os.getuid()!=10003 or ctypes.CDLL(None).ai_guard_status()!=1: raise Refused()
    if Path('/proc/self/cgroup').read_text().strip()!='0::/': raise Refused()
    encrypted_mounts()
    config=Path('/run/ai-invest/policy/web.json')
    s=config.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_nlink!=1 or s.st_mode&0o022 or s.st_size>4096: raise Refused()
    origin,clients=policy(json.loads(config.read_text(),object_pairs_hook=unique_object))
    tls=server_tls()  # Keys read only after guard and encrypted-mount validation.
    store=await WebStore.open()
    vault=FileVault('/run/ai-invest/paper',10003)
    runner=web.AppRunner(application(Gateway(store,vault,origin,clients)),access_log=None,
        keepalive_timeout=5,shutdown_timeout=5,max_line_size=4096,max_field_size=4096)
    try:
        await runner.setup()
        site=web.TCPSite(runner,'0.0.0.0',8443,ssl_context=tls,backlog=16)
        await site.start()
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        vault.close()
        await store.db.close()


def main():
    logging.disable(logging.CRITICAL)
    try:
        asyncio.run(serve())
    except BaseException:
        # No traceback, raw request, transport, environment or secret diagnostics.
        return 1
    return 0
