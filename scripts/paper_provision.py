#!/usr/bin/python3 -I
"""Fixed human-console PAPER staging. No network, broker operation or secret output."""
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import resource
import signal
import stat
import subprocess
import sys
import time
from types import ModuleType

INSTALLED=Path('/usr/local/sbin/ai-invest-paper-provision')
LIB=Path('/usr/local/libexec/ai-invest')
PENDING='initial-paper.json'
TEMP='.paper-input.tmp'
CLEAN={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'}
DEPENDENCIES={
 'console':(Path('/usr/local/sbin/ai-invest-operator-preflight'),'17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5'),
 'metadata':(LIB/'operator_preflight.py','e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c'),
 'terminal':(LIB/'paper-terminal.py','cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 'storage':(LIB/'paper-storage.py','e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
}


class Refused(Exception): pass
def require(value):
    if not value: raise Refused()


def checked(path):
    require(path.is_absolute() and path.resolve(strict=True)==path)
    for item in path.parents:
        s=item.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022)
    before=path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid==0 and before.st_nlink==1 and not before.st_mode&0o022 and before.st_size<=65536)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        after=os.fstat(fd);require((before.st_dev,before.st_ino)==(after.st_dev,after.st_ino))
        data=os.read(fd,65537);require(len(data)==before.st_size)
        return data
    finally: os.close(fd)


def load(name):
    path,digest=DEPENDENCIES[name];data=checked(path)
    require(hashlib.sha256(data).hexdigest()==digest)
    module=ModuleType('paper_'+name);module.__file__=str(path)
    exec(compile(data,str(path),'exec'),module.__dict__)
    return module


def scope_command():
    return ['/usr/bin/systemd-run','--scope','--quiet','--unit=ai-invest-paper-provision',
        '--expand-environment=no','-p','MemoryMax=512M','-p','MemorySwapMax=0','-p','TasksMax=32','-p','CPUQuota=50%',
        '/usr/bin/unshare','--mount','--propagation','private','/usr/bin/python3','-I','-B',str(INSTALLED),'--worker']


def protect(metadata):
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    libc=ctypes.CDLL(None)
    parent=os.getppid()
    require(parent!=1 and libc.prctl(1,signal.SIGKILL,0,0,0)==0 and os.getppid()==parent)
    require(libc.prctl(4,0,0,0,0)==0 and libc.prctl(3,0,0,0,0)==0)
    require(libc.prctl(38,1,0,0,0)==0)
    group=metadata.cgroup_directory()
    require(group.name=='ai-invest-paper-provision.scope')
    runtime(metadata,group)
    return group


def runtime(metadata,group):
    require(metadata.cgroup_directory()==group and ctypes.CDLL(None).prctl(3,0,0,0,0)==0)
    require(resource.getrlimit(resource.RLIMIT_CORE)==(0,0))
    require((group/'memory.swap.max').read_text().strip()=='0' and (group/'memory.swap.current').read_text().strip()=='0')
    require(0<int((group/'memory.max').read_text())<=536870912 and 0<int((group/'pids.max').read_text())<=32)
    quota,period=map(int,(group/'cpu.max').read_text().split());require(0<quota<=period//2)


def open_storage(storage):
    device=storage.mounted_device();fds=[]
    try:
        fd=os.open('/',storage.FLAGS);fds.append(fd)
        for name,mode in (('srv',0o755),('ai-invest-secure',0o700),('runtime',0o700)):
            fd=os.open(name,storage.FLAGS,dir_fd=fd);fds.append(fd)
            storage.directory(fd,0,mode,None if name=='srv' else device)
        try:
            os.mkdir('paper-credentials',0o700,dir_fd=fd)
            created=True
        except FileExistsError: created=False
        target=os.open('paper-credentials',storage.FLAGS,dir_fd=fd)
        try:
            if created:
                os.fchown(target,10003,26);os.fsync(target);os.fsync(fd)
            s=os.fstat(target)
            require(s.st_uid==10003 and s.st_gid==26 and stat.S_IMODE(s.st_mode)==0o700 and s.st_dev==device)
            fcntl.flock(target,fcntl.LOCK_EX|fcntl.LOCK_NB)
            # Initial provisioning only. Never replace a credential or recovery file.
            storage.empty(target)
            return target
        except BaseException: os.close(target);raise
    finally:
        for fd in reversed(fds): os.close(fd)


def read_value(terminal,fd,deadline):
    data=bytearray()
    while True:
        terminal.wait_ready(fd,deadline)
        try: part=os.read(fd,1)
        except BlockingIOError: continue
        require(part not in (b'',b'\x03',b'\x04',b'\x1a'))
        if part in (b'\r',b'\n'):
            require(16<=len(data)<=256);return data.decode('ascii')
        if part in (b'\x08',b'\x7f'):
            if data: data.pop()
            continue
        require(len(data)<256 and (part.isascii() and part.isalnum() or part in (b'_',b'-')))
        data.extend(part)


def publish(directory,key,value):
    fd=os.open(TEMP,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
    identity=os.fstat(fd)
    def same(name):
        s=os.stat(name,dir_fd=directory,follow_symlinks=False)
        return stat.S_ISREG(s.st_mode) and (s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino)
    try:
        data=json.dumps({'version':1,'mode':'PAPER','target_role':'ai_web_a','key':key,'secret':value},separators=(',',':')).encode()
        require(len(data)<=2048)
        offset=0
        while offset<len(data):
            n=os.write(fd,data[offset:]);require(n>0);offset+=n
        os.fchown(fd,10003,26);os.fsync(fd)
        require(same(TEMP) and os.fstat(fd).st_nlink==1)
        os.link(TEMP,PENDING,src_dir_fd=directory,dst_dir_fd=directory,follow_symlinks=False)
        require(same(PENDING))
    finally:
        try:
            if same(TEMP): os.unlink(TEMP,dir_fd=directory)
            os.fsync(directory)
        finally: os.close(fd)


def worker(console,metadata,terminal,storage):
    require(dict(os.environ)==CLEAN)
    console.require_console();console.require_host(scoped=True);console.require_console_session()
    require(Path('/proc/self/loginuid').read_text().strip()=='1000')
    group=protect(metadata)
    require(metadata.operator_ok(metadata.operator_snapshot()))
    directory=open_storage(storage)
    try:
        state={};deadline=time.monotonic()+180
        with terminal.interruptions():
            signal.alarm(180)
            try:
                with terminal.quiet_terminal(0,state):
                    terminal.display(1,b'PAPER-only protected setup. No SSH, recorder or real-money keys.\r\nType PAPER-CHECK to test hidden input, then Enter: ',deadline)
                    require(terminal.read_disposable(0,deadline)==b'PAPER-CHECK')
                    runtime(metadata,group)
                    terminal.display(1,b'\r\nInput checked. Alpaca PAPER API key (hidden): ',deadline)
                    key=read_value(terminal,0,deadline)
                    runtime(metadata,group)
                    terminal.display(1,b'\r\nAlpaca PAPER secret (hidden): ',deadline)
                    value=read_value(terminal,0,deadline)
                    runtime(metadata,group)
                    publish(directory,key,value)
                require(state.get('restored') is True)
                runtime(metadata,group)
            finally: signal.alarm(0)
        # No subprocess/exec/network after input. Only fixed non-secret status.
        os.write(1,b'\r\n{"mode":"paper-credential-stage","staged":true,"connected":false,"gate2_passed":false,"secret_entry_authorized":false,"runtime_crash_suppression_qualified":false}\n')
    finally: os.close(directory)


def main():
    try:
        require(os.getuid()==0 and Path(__file__).absolute()==INSTALLED and sys.argv[1:] in ([],['--worker']))
        checked(INSTALLED)
        console,metadata,terminal,storage=(load(n) for n in ('console','metadata','terminal','storage'))
        if sys.argv[1:]==['--worker']:
            worker(console,metadata,terminal,storage);return 0
        console.require_console();console.require_host();console.require_operator_environment();console.require_console_session()
        require(os.environ.get('SUDO_UID')=='1000' and Path('/proc/self/loginuid').read_text().strip()=='1000')
        require(os.environ.get('SUDO_USER')==pwd.getpwuid(1000).pw_name and os.environ.get('SUDO_COMMAND')==str(INSTALLED))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        os.umask(0o077)
        return subprocess.run(scope_command(),env=CLEAN,close_fds=True,timeout=210,check=False).returncode
    except BaseException:
        os.write(1,b'\r\n{"mode":"paper-credential-stage","staged":"UNKNOWN","connected":false,"error":"refused_or_incomplete","gate2_passed":false,"secret_entry_authorized":false,"runtime_crash_suppression_qualified":false}\n')
        return 1


if __name__=='__main__': raise SystemExit(main())
