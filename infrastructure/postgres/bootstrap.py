"""Fixed database operations, executed only inside the protected project container.

Never returns key bytes or raw command errors. Bootstrap names are public labels.
"""
import ctypes
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

PSQL='/usr/pgsql-17/bin/psql'
STAGE='preflight'


def protected():
    if ctypes.CDLL(None).ai_guard_status() != 1:
        raise RuntimeError()
    if Path('/proc/self/cgroup').read_text().strip() != '0::/':
        raise RuntimeError()


def sql(text, database='postgres'):
    result=subprocess.run([PSQL,'-X','-q','-A','-t','-v','ON_ERROR_STOP=1',
        '-h','/var/run/postgresql','-U','postgres','-d',database], input=text,
        text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40,check=False)
    if result.returncode: raise RuntimeError('sql_failed')
    return result.stdout.strip()


def keys():
    # Refuse existing provider file; never rotate, replace or print keys implicitly.
    path=Path('/var/lib/ai-invest-keys')
    s=path.lstat()
    if s.st_uid!=26 or stat.S_IMODE(s.st_mode)!=0o700 or list(path.iterdir()): raise RuntimeError()
    sql('CREATE EXTENSION pg_tde;')
    sql("""DO $$ BEGIN
      PERFORM pg_tde_add_global_key_provider_file('ai_v0_local','/var/lib/ai-invest-keys/v0.keyring');
      PERFORM pg_tde_create_key_using_global_key_provider('ai_v0_data','ai_v0_local');
      PERFORM pg_tde_set_default_key_using_global_key_provider('ai_v0_data','ai_v0_local');
      PERFORM pg_tde_create_key_using_global_key_provider('ai_v0_wal','ai_v0_local');
      PERFORM pg_tde_set_server_key_using_global_key_provider('ai_v0_wal','ai_v0_local');
    END $$;""")
    sql('CREATE DATABASE ai_invest TEMPLATE template0;')


def migrate():
    if sql('SHOW pg_tde.wal_encrypt;')!='on': raise RuntimeError()
    sql('CREATE EXTENSION IF NOT EXISTS pg_tde;', 'ai_invest')
    for name in ('0001_tenant_foundation.sql','0002_runtime_ledger.sql'):
        sql((Path('/opt/ai-invest/migrations')/name).read_text(),'ai_invest')


def runtime():
    protected()
    count=0
    for p in Path('/proc').iterdir():
        if p.name.isdecimal():
            try:
                if (p/'comm').read_text().strip()!='postgres': continue
                limits=(p/'limits').read_text()
                row=next(line.split() for line in limits.splitlines() if line.startswith('Max core file size'))
                if row[4:6]!=['0','0'] or (p/'environ').stat().st_uid!=0: raise RuntimeError()
                count+=1
            except FileNotFoundError:
                raise RuntimeError()
    if not 1<=count<=64: raise RuntimeError()
    return {'protected_postgres_processes':count}


def seed():
    # Fixed synthetic tenant identities only. No actual account identifiers.
    from uuid import UUID
    state={'version':1,'mode':'SYNTHETIC_PAPER','cash':'200','position':'0',
        'reserved':'0','stopped':True,'stop_epoch':0,'reconciled':False,
        'intents':{},'decisions':[],'orders':{},'fills':{}}
    broker={'cash':'200','position':'0','orders':{},'fills':{},'submissions':0}
    sql((Path('/opt/ai-invest/migrations')/'0003_synthetic_broker.sql').read_text(),'ai_invest')
    statements=['BEGIN; REVOKE CREATE ON SCHEMA public FROM PUBLIC; REVOKE ALL ON DATABASE ai_invest FROM PUBLIC;']
    for label,base in (('a',1),('b',11)):
        role='ai_tenant_'+label
        tenant,account,portfolio=(str(UUID(int=base+n)) for n in range(3))
        statements.append("""
          CREATE ROLE {role} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
          GRANT CONNECT ON DATABASE ai_invest TO {role};
          GRANT USAGE ON SCHEMA ai_invest TO {role};
          GRANT SELECT ON ai_invest.runtime_identity TO {role};
          GRANT SELECT,UPDATE ON ai_invest.runtime_ledger,ai_invest.synthetic_broker TO {role};
          GRANT SELECT,INSERT ON ai_invest.runtime_event TO {role};
          INSERT INTO ai_invest.tenant(id,label) VALUES ('{tenant}','SYNTHETIC {label}');
          INSERT INTO ai_invest.brokerage_account(tenant_id,id,provider,mode,currency) VALUES ('{tenant}','{account}','alpaca','PAPER','USD');
          INSERT INTO ai_invest.portfolio(tenant_id,id,account_id,mode,currency,virtual_capital) VALUES ('{tenant}','{portfolio}','{account}','PAPER','USD',200);
          INSERT INTO ai_invest.runtime_identity VALUES ('{role}','{tenant}');
          INSERT INTO ai_invest.runtime_ledger VALUES ('{tenant}','{account}','{portfolio}',0,'{state}'::jsonb);
          INSERT INTO ai_invest.synthetic_broker VALUES ('{tenant}','{account}','{broker}'::jsonb);
        """.format(role=role,label=label,tenant=tenant,account=account,portfolio=portfolio,
            state=json.dumps(state),broker=json.dumps(broker)))
    sql('\n'.join(statements)+ '\nCOMMIT;','ai_invest')


def recovery_copies():
    protected()
    directories=[]
    source_dir=os.open('/var/lib/ai-invest-keys',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    fd=os.open('v0.keyring',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=source_dir)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=26 or s.st_nlink!=1 or s.st_mode&0o077 or not 0<s.st_size<=1048576:
            raise RuntimeError()
        for root in ('/recovery-a','/recovery-b'):
            directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            directories.append(directory)
            d=os.fstat(directory)
            if not stat.S_ISDIR(d.st_mode) or d.st_uid!=26 or stat.S_IMODE(d.st_mode)!=0o700 or d.st_dev!=s.st_dev:
                raise RuntimeError()
            if 'v0.keyring' in os.listdir(directory): raise RuntimeError()
        original=os.read(fd,1048577)
        if len(original)!=s.st_size: raise RuntimeError()
        for directory in directories:
            out=os.open('v0.keyring',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
            try:
                if os.write(out,original)!=len(original): raise RuntimeError()
                os.fsync(out)
            finally: os.close(out)
            check=os.open('v0.keyring',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
            try:
                t=os.fstat(check)
                if t.st_nlink!=1 or t.st_uid!=26 or t.st_mode&0o077 or t.st_ino==s.st_ino or os.read(check,1048577)!=original:
                    raise RuntimeError()
            finally: os.close(check)
            os.fsync(directory)
        after=os.fstat(fd)
        if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise RuntimeError()
    finally:
        os.close(fd)
        os.close(source_dir)
        for directory in directories: os.close(directory)


def validate_storage():
    global STAGE
    STAGE='encryption_configuration'
    if sql('SHOW pg_tde.wal_encrypt;')!='on': raise RuntimeError()
    # Package release 2.2.2 retains SQL extension version 2.2.
    if sql("SELECT extversion FROM pg_extension WHERE extname='pg_tde';",'ai_invest')!='2.2': raise RuntimeError()
    sql('DO $$ BEGIN PERFORM pg_tde_verify_server_key(); PERFORM pg_tde_verify_default_key(); END $$;')
    STAGE='synthetic_storage_write'
    start=sql('SELECT pg_current_wal_insert_lsn();')
    marker='AI_INVEST_PUBLIC_SYNTHETIC_STORAGE_V1'
    sql("""CREATE TABLE IF NOT EXISTS ai_invest.storage_probe(id text PRIMARY KEY,body text NOT NULL) USING tde_heap;
        ALTER TABLE ai_invest.storage_probe ENABLE ROW LEVEL SECURITY;
        ALTER TABLE ai_invest.storage_probe FORCE ROW LEVEL SECURITY;
        ALTER TABLE ai_invest.storage_probe ALTER COLUMN body SET STORAGE EXTERNAL;
        REVOKE ALL ON ai_invest.storage_probe FROM PUBLIC;
        INSERT INTO ai_invest.storage_probe VALUES ('%s','%s'||(SELECT string_agg(md5(n::text),'') FROM generate_series(1,2000)n))
        ON CONFLICT(id) DO UPDATE SET body=excluded.body;
        CHECKPOINT;"""%(marker,marker),'ai_invest')
    end=sql('SELECT pg_current_wal_insert_lsn();')
    STAGE='encrypted_relations'
    # Fixed synthetic probe includes heap, primary index, TOAST heap/index.
    relations=sql("""WITH roots AS (SELECT oid,reltoastrelid FROM pg_class WHERE oid='ai_invest.storage_probe'::regclass),
        ids AS (SELECT oid FROM roots UNION SELECT reltoastrelid FROM roots UNION SELECT indexrelid FROM pg_index
        WHERE indrelid IN (SELECT oid FROM roots UNION SELECT reltoastrelid FROM roots))
        SELECT pg_relation_filepath(oid)||'|'||pg_tde_is_encrypted(oid)::text FROM ids WHERE oid<>0;""",'ai_invest').splitlines()
    if len(relations)!=4 or any(not line.endswith('|true') for line in relations): raise RuntimeError()
    STAGE='encrypted_bytes'
    if sql("SELECT starts_with(body,'%s') FROM ai_invest.storage_probe WHERE id='%s';"%(marker,marker),'ai_invest')!='t': raise RuntimeError()
    for line in relations:
        relative=line.split('|')[0]
        import re
        if re.fullmatch(r'base/[0-9]+/[0-9]+',relative) is None: raise RuntimeError()
        path=Path('/pgdata')/relative
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            size=os.fstat(fd).st_size
            if not 0<size<=1048576: raise RuntimeError()
            if marker.encode() in os.read(fd,1048577): raise RuntimeError()
        finally: os.close(fd)
    STAGE='wal_keyed_decode'
    command=['/usr/pgsql-17/bin/pg_tde_waldump','-q','-p','/pgdata/pg_wal','-s',start,'-e',end]
    keyed=subprocess.run(command+['-k','/pgdata/pg_tde'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
    if keyed.returncode: raise RuntimeError()
    STAGE='wal_unkeyed_refusal'
    unkeyed=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
    if not unkeyed.returncode: raise RuntimeError()
    STAGE='complete'
    return {'tde_heap_index_toast':True,'plaintext_probe_absent':True,'wal_keyed_decode':True,'wal_unkeyed_refused':True}


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else 'invalid'
    try:
        protected()
        extra={}
        if mode=='keys': keys()
        elif mode=='migrate': migrate()
        elif mode=='runtime': extra=runtime()
        elif mode=='seed': seed()
        elif mode=='validate-storage': extra=validate_storage()
        elif mode=='recovery-copies': recovery_copies()
        else: raise RuntimeError()
        print(json.dumps({'mode':mode,'passed':True,**extra}))
        return 0
    except Exception:
        print(json.dumps({'mode':mode if mode in ('keys','migrate','runtime','recovery-copies','seed','validate-storage') else 'invalid','passed':False,'stage':STAGE}))
        return 1


if __name__=='__main__': raise SystemExit(main())
