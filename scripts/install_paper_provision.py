#!/usr/bin/python3 -I
"""Human-run fixed installer. Public code/policy only; never reads credentials."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ROOT=Path('/home/rob/ai-invest')
LIB=Path('/usr/local/libexec/ai-invest')
POLICY=Path('/etc/sudoers.d/ai-invest-paper-provision')
CLEAN={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'}
FILES=(
 ('scripts/paper_provision.py',Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'82f91e8f370442a6aeeedff3552c7c295516c5eb2760a1875b6c3fa8c8887d79'),
 ('scripts/qualification/terminal_exchange.py',LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 ('scripts/setup_postgres_dirs.py',LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 ('infrastructure/web/ai-invest-paper-provision.sudoers',POLICY,0o440,'4e5eb0c4132a9d6d01900e52450661a354fec60cf01b4d5acdb243477e2d2ee5'),
)
DEPENDENCIES=(
 (Path('/usr/local/sbin/ai-invest-operator-preflight'),'17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5'),
 (LIB/'operator_preflight.py','e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c'),
)


def require(value):
    if not value: raise RuntimeError('installation_refused')


def parents(path,source=False):
    require(path.is_absolute() and path.parent.resolve(strict=True)==path.parent)
    for parent in path.parents:
        info=parent.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid in ((0,1000) if source else (0,)) and not info.st_mode&0o022)


def read(path,digest,source=False):
    parents(path,source)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    try:
        info=os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid in ((0,1000) if source else (0,)) and info.st_nlink==1 and not info.st_mode&0o022 and 0<info.st_size<=65536)
        data=os.read(fd,65537)
        require(len(data)==info.st_size and hashlib.sha256(data).hexdigest()==digest)
        return data
    finally: os.close(fd)


def validate(path=None):
    command=['/usr/sbin/visudo','-c','-s']
    if path is not None: command+=['-f',str(path)]
    subprocess.run(command,env=CLEAN,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL,close_fds=True,timeout=10,check=True)


def write(path,data,mode):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
    try:
        require(os.write(fd,data)==len(data));os.fchmod(fd,mode);os.fsync(fd)
    finally: os.close(fd)


def sync_parent(path):
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try: os.fsync(fd)
    finally: os.close(fd)


def install():
    require(os.getuid()==0 and sys.argv[1:] in ([],['--rollback']))
    os.umask(0o077)
    validate()
    if sys.argv[1:]==['--rollback']:
        # Remove only this exact policy. Public helper copies remain inert evidence.
        read(POLICY,FILES[-1][3]);POLICY.unlink();sync_parent(POLICY);validate()
        return 'policy_removed_helpers_preserved'
    for path,digest in DEPENDENCIES: read(path,digest)
    require(stat.S_IMODE(LIB.stat().st_mode)==0o700)
    data=[]
    for source,target,mode,digest in FILES:
        parents(target)
        require(not target.exists() and not target.is_symlink())
        data.append(read(ROOT/source,digest,True))
    created=[]
    # Staging is root-only, fixed public artifacts; no credential path is touched.
    with tempfile.TemporaryDirectory(prefix='paper-install-',dir=LIB) as directory:
        work=Path(directory)
        candidate=work/'policy';write(candidate,data[-1],0o440);validate(candidate)
        aggregate=work/'aggregate'
        write(aggregate,('@include /etc/sudoers\n@include '+str(candidate)+'\n').encode(),0o600)
        validate(aggregate)
        try:
            for index,(_,target,mode,digest) in enumerate(FILES):
                staged=work/('artifact-'+str(index));write(staged,data[index],mode)
                os.link(staged,target,follow_symlinks=False) # Atomic, exclusive, no overwrite.
                created.append((target,staged.stat().st_ino))
                staged.unlink();sync_parent(target);read(target,digest)
            validate()
        except BaseException:
            # Fixed created files only; never remove replaced files or earlier evidence.
            for target,inode in reversed(created):
                info=target.lstat()
                if stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_ino==inode:
                    target.unlink();sync_parent(target)
            validate()
            raise
    return 'installed_not_provisioned'


def main():
    try: state=install();status=0
    except BaseException: state='refused_or_incomplete';status=1
    print(json.dumps({'mode':'paper-provision-install','state':state,'credentials_entered':False,'connected':False},separators=(',',':')))
    return status


if __name__=='__main__': raise SystemExit(main())
