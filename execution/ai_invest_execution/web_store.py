"""Execution-only protected credential files and PostgreSQL metadata.

No credential value reaches SQL, configuration, repr or an error response.
"""
import json
import os
import stat
from uuid import UUID, uuid4

from .alpaca_paper import PaperCredentials


class Refused(RuntimeError):
    def __init__(self): super().__init__('request_refused')


class FileVault:
    def __init__(self,path,uid=None):
        self.uid=os.geteuid() if uid is None else uid
        self.fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        s=os.fstat(self.fd)
        if s.st_uid!=self.uid or stat.S_IMODE(s.st_mode)!=0o700:
            os.close(self.fd)
            raise Refused()

    @staticmethod
    def name(version):
        if type(version) is not UUID: raise Refused()
        return version.hex+'.json'

    def put(self,tenant,connection,credentials):
        if type(tenant) is not UUID or type(connection) is not UUID or type(credentials) is not PaperCredentials: raise Refused()
        with os.scandir(self.fd) as entries:
            for count,_ in enumerate(entries,1):
                if count>=32: raise Refused() # Bound protected orphan growth after ambiguous commits.
        version=uuid4()
        fd=os.open(self.name(version),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        try:
            data=json.dumps({'tenant':str(tenant),'connection':str(connection),
                'key':credentials.key_id,'secret':credentials.secret_key},separators=(',',':')).encode()
            if os.write(fd,data)!=len(data): raise Refused()
            os.fsync(fd)
            os.fsync(self.fd)
        except BaseException:
            os.unlink(self.name(version),dir_fd=self.fd) # Definitely not published to DB yet.
            raise
        finally: os.close(fd)
        return version

    def get(self,tenant,connection,version):
        fd=os.open(self.name(version),os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=self.fd)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid!=self.uid or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600 or not 0<s.st_size<=2048: raise Refused()
            raw=os.read(fd,2049)
            after=os.fstat(fd)
            if len(raw)!=s.st_size or (s.st_ino,s.st_size,s.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns): raise Refused()
            data=json.loads(raw)
            if set(data)!={'tenant','connection','key','secret'} or data['tenant']!=str(tenant) or data['connection']!=str(connection): raise Refused()
            return PaperCredentials(data['key'],data['secret'])
        finally: os.close(fd)

    def remove(self,version):
        # Only known, no-longer-referenced immutable versions. No recursive cleanup.
        os.unlink(self.name(version),dir_fd=self.fd)
        os.fsync(self.fd)

    def close(self): os.close(self.fd)


class WebStore:
    def __init__(self,connection,tenant): self.db,self.tenant=connection,tenant

    @classmethod
    async def open(cls):
        import psycopg
        db=await psycopg.AsyncConnection.connect(host='/var/run/postgresql',dbname='ai_invest',
            user='ai_web_a',autocommit=True,connect_timeout=5,
            options='-c statement_timeout=5000 -c lock_timeout=5000')
        try:
            row=await (await db.execute('SELECT rolsuper,rolbypassrls,rolcreaterole,rolcreatedb,current_user=session_user FROM pg_roles WHERE rolname=session_user')).fetchone()
            if row!=(False,False,False,False,True): raise Refused()
            memberships=await (await db.execute('SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=session_user)')).fetchone()
            if memberships!=(0,): raise Refused()
            ids=await (await db.execute('SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user')).fetchall()
            if len(ids)!=1: raise Refused()
            tables=await (await db.execute("SELECT a.amname,c.relrowsecurity,c.relforcerowsecurity,pg_get_userbyid(c.relowner)=session_user FROM pg_class c JOIN pg_am a ON a.oid=c.relam WHERE c.oid IN ('ai_invest.web_connection'::regclass,'ai_invest.web_event'::regclass)")).fetchall()
            if len(tables)!=2 or any(row!=('tde_heap',True,True,False) for row in tables): raise Refused()
            # One process owns this tenant's operations; no cross-process rotation race.
            locked=await (await db.execute('SELECT pg_try_advisory_lock(hashtextextended(session_user,0))')).fetchone()
            if locked!=(True,): raise Refused()
            return cls(db,ids[0][0])
        except BaseException:
            await db.close()
            raise

    async def rows(self):
        from psycopg.rows import dict_row
        async with self.db.cursor(row_factory=dict_row) as cur:
            await cur.execute('SELECT id,broker_account_id,state,credential_version,snapshot,updated_at FROM ai_invest.web_connection WHERE tenant_id=%s ORDER BY updated_at DESC LIMIT 9',(self.tenant,))
            rows=await cur.fetchall()
        if len(rows)>8: raise Refused()
        return rows

    async def get(self,identifier):
        rows=await self.rows()
        for row in rows:
            if row['id']==identifier: return row
        raise Refused()

    async def save(self,identifier,account,version,snapshot,actor,kind):
        async with self.db.transaction():
            changed=await self.db.execute("INSERT INTO ai_invest.web_connection (tenant_id,id,broker_account_id,state,credential_version,snapshot) VALUES (%s,%s,%s,'CONNECTED',%s,%s::jsonb) ON CONFLICT(tenant_id,id) DO UPDATE SET state='CONNECTED',credential_version=excluded.credential_version,snapshot=excluded.snapshot,updated_at=CURRENT_TIMESTAMP WHERE ai_invest.web_connection.broker_account_id=excluded.broker_account_id",
                (self.tenant,identifier,account,version,json.dumps(snapshot)))
            if changed.rowcount!=1: raise Refused()
            await self.event(identifier,actor,kind)

    async def event(self,identifier,actor,kind):
        await self.db.execute('INSERT INTO ai_invest.web_event(tenant_id,connection_id,actor,kind) VALUES (%s,%s,%s,%s)',(self.tenant,identifier,actor,kind))

    async def disconnect(self,identifier,actor):
        async with self.db.transaction():
            changed=await self.db.execute("UPDATE ai_invest.web_connection SET state='DISCONNECTED',credential_version=NULL,snapshot='{}',updated_at=CURRENT_TIMESTAMP WHERE tenant_id=%s AND id=%s",(self.tenant,identifier))
            if changed.rowcount!=1: raise Refused()
            await self.event(identifier,actor,'disconnected')

    async def refreshed(self,identifier,snapshot,actor):
        async with self.db.transaction():
            changed=await self.db.execute('UPDATE ai_invest.web_connection SET snapshot=%s::jsonb,updated_at=CURRENT_TIMESTAMP WHERE tenant_id=%s AND id=%s',(json.dumps(snapshot),self.tenant,identifier))
            if changed.rowcount!=1: raise Refused()
            await self.event(identifier,actor,'refreshed')
