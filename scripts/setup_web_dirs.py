#!/usr/bin/python3 -I
"""Fixed NON-SECRET web-directory setup. No certificate/credential generation."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys


def leaf(fd,uid,mode,device):
    s=os.fstat(fd)
    if (not stat.S_ISDIR(s.st_mode) or s.st_uid!=uid or s.st_gid!=26
        or stat.S_IMODE(s.st_mode)!=mode or s.st_dev!=device): raise RuntimeError()


def setup():
    if os.geteuid()!=0 or len(sys.argv)!=1: raise RuntimeError()
    helper=Path(__file__).resolve().with_name('setup_postgres_dirs.py')
    for path in (Path(__file__),helper):
        s=path.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_mode&0o022: raise RuntimeError()
    spec=importlib.util.spec_from_file_location('fixed_storage_checks',helper)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    device=module.mounted_device()
    fds=[]
    try:
        fd=os.open('/',module.FLAGS);fds.append(fd)
        for name,mode in (('srv',0o755),('ai-invest-secure',0o700),('runtime',0o700)):
            fd=os.open(name,module.FLAGS,dir_fd=fd);fds.append(fd)
            module.directory(fd,0,mode,None if name=='srv' else device)
        targets=(('paper-credentials',10003,0o700),('web-tls',10003,0o700),('web-policy',0,0o750))
        for name,uid,mode in targets:
            try: current=os.open(name,module.FLAGS,dir_fd=fd)
            except FileNotFoundError: continue
            try:
                leaf(current,uid,mode,device)
                module.empty(current)
            finally: os.close(current)
        for name,uid,mode in targets:
            try:
                os.mkdir(name,0o700,dir_fd=fd)
                created=True
            except FileExistsError: created=False
            current=os.open(name,module.FLAGS,dir_fd=fd)
            try:
                module.empty(current)
                if created:
                    os.fchown(current,uid,26)
                    os.fchmod(current,mode)
                leaf(current,uid,mode,device)
            finally: os.close(current)
        if module.mounted_device()!=device: raise RuntimeError()
    finally:
        for fd in reversed(fds): os.close(fd)


def main():
    try: setup();ready=True
    except Exception: ready=False
    print(json.dumps({'mode':'web-directory-setup','directories_ready':ready,
        'credentials_created':False,'tls_created':False,'web_started':False,'gate2_passed':False}))
    return 0 if ready else 1


if __name__=='__main__': raise SystemExit(main())
