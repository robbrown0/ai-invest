#!/usr/bin/python3 -I
import json, os, stat
from pathlib import Path
BASE=Path("/srv/ai-invest-secure/runtime/paper-credentials")
PENDING=BASE/"initial-paper.json"
def main():
    if os.geteuid()!=0 or BASE.is_symlink() or not BASE.is_dir(): return 1
    s=BASE.stat()
    if s.st_uid!=10003 or stat.S_IMODE(s.st_mode)!=0o700 or s.st_nlink<2: return 1
    entries=list(BASE.iterdir())
    if len(entries)!=1 or entries[0].name!=PENDING.name or entries[0].is_symlink(): return 1
    f=PENDING.lstat()
    if not stat.S_ISREG(f.st_mode) or f.st_uid!=10003 or f.st_nlink!=1 or stat.S_IMODE(f.st_mode)!=0o600: return 1
    PENDING.unlink(); os.sync()
    print(json.dumps({"mode":"paper-stage-reset","reset":True,"credentials_accessed":False}))
    return 0
if __name__=="__main__": raise SystemExit(main())
