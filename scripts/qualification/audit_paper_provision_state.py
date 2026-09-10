#!/usr/bin/env python3 -I
"""Read-only, exhaustive PAPER provisioner state audit; never reads credentials."""
import hashlib, json, os, stat
from pathlib import Path

ROOT=Path('/home/rob/ai-invest'); LIB=Path('/usr/local/libexec/ai-invest')
POLICY=Path('/etc/sudoers.d/ai-invest-paper-provision'); MANIFEST=LIB/'paper-provision.manifest'
CURRENT=(
 ('paper_provision',Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'1762fbfe82a6ccb22adc502ac0c0e39aa8d51ce623ec4d0882fdf831742ac4c4'),
 ('paper_terminal',LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 ('paper_storage',LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 ('sudo_policy',POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
VERSIONS=(
 ('v1','82f91e8f370442a6aeeedff3552c7c295516c5eb2760a1875b6c3fa8c8887d79','4e5eb0c4132a9d6d01900e52450661a354fec60cf01b4d5acdb243477e2d2ee5'),
 ('ssh-v1','559a059870ff73e83afecd397d1dac32304d1aad1ec2d0b6555c40c6eaa53659','8562e5d48f623825c5d707548b66a5e40918f8ba9f93877d258346e2523b866e'),
 ('v24','480d5bc00b0cc01858d78925014ac4ef769607978fff86403d9b9363248d2b2d','84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
 ('v25','142963a65f48c52441a8b93c41d6a564ddb5c617869584bdc995f37c4c7dc130','84c3bdd92fe2582122871c031e970b37ef8ab8c0c11175a66d91f575c6258cc0'),
)
# Current expected marker is derived from the repository installer; this audit deliberately reports marker shape/content separately.

def meta(path):
    try:
        s=path.lstat(); return {'exists':True,'symlink':stat.S_ISLNK(s.st_mode),'regular':stat.S_ISREG(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'nlink':s.st_nlink,'size':s.st_size}
    except Exception: return {'exists':False}

def file_check(path,expected,mode):
    m=meta(path); out={'path_key':path.name,'metadata':m,'expected_mode':oct(mode),'hash_match':False,'actual_hash_present':False}
    if m.get('regular') and not m.get('symlink') and m.get('size',0)<=65536:
        try:
            data=path.read_bytes(); actual=hashlib.sha256(data).hexdigest(); out['actual_hash_present']=True; out['actual_hash']=actual; out['hash_match']=actual==expected
        except Exception: pass
    out['expected_hash_present']=bool(expected); return out

def main():
    artifacts={name:file_check(path,digest,mode) for name,path,mode,digest in CURRENT}
    backups=[]
    for name,path,mode,digest in CURRENT:
        parent=path.parent; prefix='.'+path.name+'.paper-provision.previous'
        try: entries=sorted(x for x in parent.iterdir() if x.name.startswith(prefix))
        except Exception: entries=[]
        backups += [{'artifact':name,'filename_class':'known_prefix','metadata':meta(x)} for x in entries]
    marker={'metadata':meta(MANIFEST),'readable':False,'json_shape':'unavailable'}
    if marker['metadata'].get('regular') and not marker['metadata'].get('symlink'):
        try:
            obj=json.loads(MANIFEST.read_text()); marker['readable']=True
            marker['json_shape']={'format':obj.get('format'),'version_type':type(obj.get('version')).__name__,'version':obj.get('version') if isinstance(obj.get('version'),str) and len(obj.get('version'))<=64 else None,'artifact_count':len(obj.get('artifacts',[])) if isinstance(obj.get('artifacts'),list) else -1}
        except Exception: marker['json_shape']='invalid_or_unreadable'
    print(json.dumps({'audit':'ai-invest-paper-provision-state-v1','read_only':True,'credentials_accessed':False,'current_artifacts':artifacts,'manifest':marker,'rollback_candidates':backups,'known_version_count':len(VERSIONS)},sort_keys=True,separators=(',',':')))
if __name__=='__main__': main()
