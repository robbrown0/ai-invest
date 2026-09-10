"""Fixed initial PAPER activation from protected staging; never a credential CLI."""
import asyncio
import ctypes
import hashlib
import json
import logging
import os
from pathlib import Path
import stat
from uuid import uuid4

from .alpaca_paper import PaperCredentials, unique_object, reject_constant
from .web_broker import PaperWebReader
from .web_store import FileVault, WebStore, Refused

STAGED='initial-paper.json'
# Fixed actor namespace, not a client certificate or user-controlled identity.
CONSOLE_ACTOR=hashlib.sha256(b'ai-invest:authenticated-operator:uid1000:paper-initial:v2').hexdigest()


class ActivationFailure(Refused):
    def __init__(self,stage):
        self.stage=stage
        super().__init__()


def staged(vault):
    fd=os.open(STAGED,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=vault.fd)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=vault.uid or before.st_nlink!=1 or stat.S_IMODE(before.st_mode)!=0o600 or not 0<before.st_size<=2048:
            raise Refused()
        raw=os.read(fd,2049)
        after=os.fstat(fd)
        named=os.stat(STAGED,dir_fd=vault.fd,follow_symlinks=False)
        identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink)
        if len(raw)!=before.st_size or identity(before)!=identity(after) or identity(after)!=identity(named): raise Refused()
        data=json.loads(raw,object_pairs_hook=unique_object,parse_constant=reject_constant)
        if type(data) is not dict or set(data)!={'version','mode','target_role','key','secret'} or type(data['version']) is not int or data['version']!=1 or data['mode']!='PAPER' or data['target_role']!='ai_web_a': raise Refused()
        return PaperCredentials(data['key'],data['secret'])
    finally: os.close(fd)


def protected_mounts():
    expected={'/run/ai-invest/paper','/run/postgresql'};devices=set()
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        parts=line.split()
        if len(parts)<10 or parts[4] not in expected: continue
        separator=parts.index('-')
        if parts[separator+1]!='ext4' or parts[separator+2]!='/dev/mapper/ai-invest-qualification' or not {'nosuid','nodev','noexec'}<=set(parts[5].split(',')): raise Refused()
        devices.add(parts[2]);expected.remove(parts[4])
    if expected or len(devices)!=1: raise Refused()


async def activate(store,vault,reader=PaperWebReader):
    # Peer DB identity, TDE/RLS and advisory ownership are validated by WebStore.open.
    # Never guess an account or replace a current connection on repeated invocation.
    if await store.rows(): raise Refused()
    try:
        credentials=staged(vault)
    except BaseException:
        raise ActivationFailure('credential_read') from None
    identifier=uuid4()
    broker=reader(credentials,store.tenant,identifier)
    try:
        async with asyncio.timeout(45):
            account,_=await broker.account()
            snapshot=await broker.dashboard(account)
    except BaseException:
        raise ActivationFailure('paper_api_validation') from None
    encoded=json.dumps(snapshot)
    if credentials.key_id in encoded or credentials.secret_key in encoded: raise ActivationFailure('paper_api_validation')
    try:
        version=vault.put(store.tenant,identifier,credentials)
    except BaseException:
        raise ActivationFailure('credential_publish') from None
    # After save begins, an ambiguous database response must preserve the immutable
    # credential version. Never delete/retry a possibly committed connection.
    try:
        await store.save(identifier,account,version,snapshot,CONSOLE_ACTOR,'connected')
    except BaseException:
        raise ActivationFailure('database_record') from None
    # Preserve staging as protected recovery evidence; no secret returns to caller.
    return {'mode':'paper-activation','connected':True,'account_read':True,
            'positions_read':True,'orders_read':True,
            'clock_read':snapshot.get('clock') is not None,
            'market_read':snapshot.get('market') is not None,
            'orders_reconciled':False,'gate2_passed':False,
            'secret_entry_authorized':False,'runtime_crash_suppression_qualified':False}


async def run():
    if os.getuid()!=10003 or ctypes.CDLL(None).ai_guard_status()!=1 or Path('/proc/self/cgroup').read_text().strip()!='0::/': raise Refused()
    protected_mounts()
    store=await WebStore.open()
    vault=None
    try:
        vault=FileVault('/run/ai-invest/paper',10003)
        return await activate(store,vault)
    finally:
        if vault is not None: vault.close()
        await store.db.close()


def main():
    logging.disable(logging.CRITICAL)
    try: result=asyncio.run(run());status=0
    except ActivationFailure as failure:
        result={'mode':'paper-activation','connected':'UNKNOWN','error':'refused_or_incomplete','failure_stage':failure.stage,
                'gate2_passed':False,'secret_entry_authorized':False,'runtime_crash_suppression_qualified':False};status=1
    print(json.dumps(result,separators=(',',':')))
    return status
