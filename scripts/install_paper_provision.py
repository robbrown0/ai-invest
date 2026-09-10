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
SUDOERS=Path('/etc/sudoers')
SUDOERS_DIR=Path('/etc/sudoers.d')
CLEAN={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'}
FILES=(
 ('scripts/paper_provision.py',Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'f05af8d246885d5469ac405fbe9b286f98c9b5b902dec9e9068841d340da967a'),
 ('scripts/qualification/terminal_exchange.py',LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 ('scripts/setup_postgres_dirs.py',LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 ('infrastructure/web/ai-invest-paper-provision.sudoers',POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'82f91e8f370442a6aeeedff3552c7c295516c5eb2760a1875b6c3fa8c8887d79'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'4e5eb0c4132a9d6d01900e52450661a354fec60cf01b4d5acdb243477e2d2ee5'),
)
SSH_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'559a059870ff73e83afecd397d1dac32304d1aad1ec2d0b6555c40c6eaa53659'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'8562e5d48f623825c5d707548b66a5e40918f8ba9f93877d258346e2523b866e'),
)
SCOPE_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'44d620a2c41822e73d8cd931b1b357e8919e350fd41c8e5a238483efff3df737'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'ac4dfccb27bb4d7a274f4ab613792a116a4d0d9b7dcfeb1e5e123ec092281d70'),
)
DIAGNOSTIC_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'d5829e80d0b9fd4dca994e1ecfad3d524d3cff30074530c29955b2b5dabb8ab6'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'939c802cf6e0908858d504c383fcb6323be51dfa86db0f968710f162a21537fb'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V5_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'a65158bb67af7291e61d153d7ad90326af21945ddcef7f2c83f84565c60bd097'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V6_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'e5158d558a4c0b1162665ee671f83cb5c487976a56a0d79f923b4bce1c49b34b'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V7_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'cd64856e9c6d8c97396d74cb3325fa788fc3062f64b2ce793118a117cbdd350a'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V8_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'44fa2a4ba8e0af3f9dbd6b684e8ab478d7afbc74c2f53cffc378299fc8894ea2'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V9_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'18fb88910ce0018ac086cd3c46ec9c30871181b6d4bcda10459b2d4017129a5f'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V10_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'e618bcec89b8a7128de6cbff0b16df3c1e5f0c571d09295913f7c176f25d00dd'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V11_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'75cac45431155c00e9cd361b0b0897d77303140bdc0affc417b4dfd5731999ce'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V12_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'884e91739473ecfca58850d7e44bfc14b3cbe36f822d0e339ef2c96a6da4ccbe'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
SESSION_V13_OLD_FILES=(
 (Path('/usr/local/sbin/ai-invest-paper-provision'),0o755,'5592b8585ebd78bd2d8bfbaa43a152a87fab205ad57c38a6a2ddb71ec18e6f11'),
 (LIB/'paper-terminal.py',0o644,'cc065a0790e18eadc62038effb79c66f7990cdd121da6a8c2930b51975f1cf04'),
 (LIB/'paper-storage.py',0o644,'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706'),
 (POLICY,0o440,'84c3bdd92fe2582122871c031e970b37ef8ab6c0c11175a66d91f575c6258cc0'),
)
APPROVED_OLD_VERSIONS=(('physical-console-v1',OLD_FILES),('ssh-v1',SSH_OLD_FILES),('ssh-scope-v2',SCOPE_OLD_FILES),('ssh-diagnostic-v3',DIAGNOSTIC_OLD_FILES),('ssh-session-v4',SESSION_OLD_FILES),('ssh-session-v5',SESSION_V5_OLD_FILES),('ssh-session-v6',SESSION_V6_OLD_FILES),('ssh-session-v7',SESSION_V7_OLD_FILES),('ssh-session-v8',SESSION_V8_OLD_FILES),('ssh-session-v9',SESSION_V9_OLD_FILES),('ssh-session-v10',SESSION_V10_OLD_FILES),('ssh-session-v11',SESSION_V11_OLD_FILES),('ssh-session-v12',SESSION_V12_OLD_FILES),('ssh-session-v13',SESSION_V13_OLD_FILES))
CURRENT_VERSION='ssh-session-v14'
MANIFEST_MODE=0o400
DEPENDENCIES=(
 (Path('/usr/local/sbin/ai-invest-operator-preflight'),'17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5'),
 (LIB/'operator_preflight.py','e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c'),
)
FAILURE_STAGES=frozenset(('precheck','old_artifact_validation','new_source_validation',
                          'candidate_policy_validation','backup_creation','replacement',
                          'aggregate_sudo_validation','new_artifact_validation','rollback'))


class StageFailure(RuntimeError):
    """Sanitized installer failure; never carries host/exception details."""
    def __init__(self,stage):
        if stage not in FAILURE_STAGES: stage='precheck'
        self.stage=stage
        super().__init__(stage)


def phase(stage, operation):
    try:
        return operation()
    except StageFailure:
        raise
    except BaseException:
        raise StageFailure(stage)


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


def artifact(path,digest,mode):
    data=read(path,digest)
    info=path.lstat()
    require(stat.S_IMODE(info.st_mode)==mode and info.st_uid==0 and info.st_gid==0 and info.st_nlink==1)
    return data


def backup_path(path,version=None):
    suffix='.paper-provision.previous' if version is None else '.paper-provision.previous.'+version
    return path.parent / ('.'+path.name+suffix)


def manifest_path():
    return LIB/'paper-provision.manifest'


def manifest_bytes(version_name, version_files):
    artifacts=[{'name':target.name,'mode':mode,'sha256':digest}
               for target,mode,digest in version_files]
    return (json.dumps({'format':1,'version':version_name,'artifacts':artifacts},
                       sort_keys=True,separators=(',',':'))+'\n').encode()


def manifest_digest(version_name, version_files):
    return hashlib.sha256(manifest_bytes(version_name,version_files)).hexdigest()


def validate_manifest(version_name, version_files, allow_missing=False):
    path=manifest_path()
    if allow_missing and not path.exists() and not path.is_symlink(): return None
    return artifact(path,manifest_digest(version_name,version_files),MANIFEST_MODE)


def replace_file(path,data,mode):
    fd,name=tempfile.mkstemp(prefix='paper-provision.',dir=path.parent)
    temporary=Path(name)
    try:
        os.fchmod(fd,mode);os.fchown(fd,0,0)
        require(os.write(fd,data)==len(data));os.fsync(fd)
    finally: os.close(fd)
    try:
        os.replace(temporary,path);sync_parent(path)
    finally:
        if temporary.exists(): temporary.unlink()


def validate_existing_backups():
    # Every rollback generation is an all-or-nothing set for the four
    # installed artifacts.  The manifest backup is optional only for legacy
    # generations created before manifests existed.
    targets=[target for _,target,_,_ in FILES]
    marker=manifest_path()
    known={backup_path(target) for target in targets}|{backup_path(target,name) for target in targets for name,_ in APPROVED_OLD_VERSIONS}
    known.add(backup_path(marker))
    known.update(backup_path(marker,name) for name,_ in APPROVED_OLD_VERSIONS)
    for target in targets+[marker]:
        prefix='.'+target.name+'.paper-provision.previous'
        for entry in target.parent.iterdir():
            if entry.name.startswith(prefix): require(entry in known)
    legacy=[backup_path(target) for target in targets]
    require(not backup_path(marker).exists() and not backup_path(marker).is_symlink())
    legacy_state=[path.exists() or path.is_symlink() for path in legacy]
    require(all(state==legacy_state[0] for state in legacy_state))
    if all(legacy_state):
        matches=[]
        for name,version_files in APPROVED_OLD_VERSIONS:
            try:
                for (target,mode,digest),backup in zip(version_files,legacy): artifact(backup,digest,mode)
                matches.append(name)
            except BaseException: pass
        require(len(matches)==1)
    for name,version_files in APPROVED_OLD_VERSIONS:
        paths=[backup_path(target,name) for target,_,_ in version_files]
        present=[path.exists() or path.is_symlink() for path in paths]
        require(not any(present) or all(present))
        marker_backup=backup_path(marker,name)
        marker_present=marker_backup.exists() or marker_backup.is_symlink()
        require(not marker_present or all(present))
        if all(present):
            for (target,mode,digest),path in zip(version_files,paths): artifact(path,digest,mode)
            if marker_present:
                artifact(marker_backup,manifest_digest(name,version_files),MANIFEST_MODE)


def rollback_candidates():
    for _,target,mode,digest in FILES: artifact(target,digest,mode)
    current_files=tuple((target,mode,digest) for _,target,mode,digest in FILES)
    validate_manifest(CURRENT_VERSION,current_files)
    versioned=[]
    marker=manifest_path()
    for name,version_files in APPROVED_OLD_VERSIONS:
        paths=[backup_path(target,name) for target,_,_ in version_files]
        present=[path.exists() or path.is_symlink() for path in paths]
        require(not any(present) or all(present))
        if all(present):
            data=[artifact(path,digest,mode) for (target,mode,digest),path in zip(version_files,paths)]
            marker_backup=backup_path(marker,name)
            marker_data=None
            if marker_backup.exists() or marker_backup.is_symlink():
                marker_data=artifact(marker_backup,manifest_digest(name,version_files),MANIFEST_MODE)
            versioned.append((name,version_files,data,paths,marker_backup if marker_data is not None else None,marker_data))
    if versioned:
        return versioned[-1]
    legacy=[backup_path(target) for _,target,_,_ in FILES]
    require(all(path.exists() and not path.is_symlink() for path in legacy))
    matches=[]
    for name,version_files in APPROVED_OLD_VERSIONS:
        try:
            data=[artifact(path,digest,mode) for (target,mode,digest),path in zip(version_files,legacy)]
            matches.append((name,version_files,data,legacy,None,None))
        except BaseException: pass
    require(len(matches)==1);return matches[0]


def replacement_aggregate(candidate):
    """Build post-upgrade sudoers with this policy substituted exactly once."""
    fd=os.open(SUDOERS,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1 and not info.st_mode&0o022 and 0<info.st_size<=1048576)
        base=os.read(fd,1048577)
        require(len(base)==info.st_size)
    finally: os.close(fd)
    try: lines=base.decode('utf-8').splitlines(keepends=True)
    except BaseException: raise RuntimeError('sudoers_encoding')
    entries=[]
    with os.scandir(SUDOERS_DIR) as scan:
        for entry in scan:
            name=entry.name
            if name==POLICY.name or '.' in name or name.endswith('~'): continue
            require(entry.is_file(follow_symlinks=True))
            entries.append((name,Path(entry.path)))
    entries.append((POLICY.name,candidate))
    entries.sort(key=lambda item:item[0])
    includes=['@include '+str(path)+'\n' for _,path in entries]
    output=[];replaced=0
    for line in lines:
        if line.strip() in ('@includedir /etc/sudoers.d','@includedir /etc/sudoers.d/'):
            output.extend(includes);replaced+=1
        else: output.append(line)
    require(replaced==1)
    return ''.join(output).encode('utf-8')


def upgrade():
    phase('precheck',lambda: (require(os.getuid()==0 and sys.argv[1:]==['--upgrade']),
                              validate(),
                              [read(path,digest) for path,digest in DEPENDENCIES],
                              require(stat.S_IMODE(LIB.stat().st_mode)==0o700)))
    old=[];new=[];backups=[];old_version=None;old_marker=None;marker_backup=None
    def inspect_old():
        nonlocal old,backups,old_version,old_marker,marker_backup
        validate_existing_backups()
        matches=[]
        for version_name,version_files in APPROVED_OLD_VERSIONS:
            candidate_old=[];candidate_backups=[]
            try:
                for (source,target,mode,digest),(old_target,old_mode,old_digest) in zip(FILES,version_files):
                    require(target==old_target and mode==old_mode and not target.is_symlink())
                    candidate_old.append(artifact(target,old_digest,old_mode))
                    backup=backup_path(target,version_name);require(not backup.exists() and not backup.is_symlink())
                    candidate_backups.append(backup)
                marker=manifest_path()
                marker_present=marker.exists() or marker.is_symlink()
                if marker_present: validate_manifest(version_name,tuple((target,mode,digest) for target,mode,digest in version_files))
                candidate_marker_backup=backup_path(marker,version_name)
                if marker_present: require(not candidate_marker_backup.exists() and not candidate_marker_backup.is_symlink())
                matches.append((version_name,candidate_old,candidate_backups,marker_present,candidate_marker_backup))
            except BaseException:
                continue
        require(len(matches)==1)
        old_version,old,backups,old_marker,marker_backup=matches[0]
    phase('old_artifact_validation',inspect_old)
    def inspect_new():
        for source,target,mode,digest in FILES:
            new.append((read(ROOT/source,digest,True),mode,digest))
    phase('new_source_validation',inspect_new)
    with tempfile.TemporaryDirectory(prefix='paper-provision-upgrade-',dir=LIB) as directory:
        work=Path(directory);candidate=work/'policy'
        phase('candidate_policy_validation',lambda: (write(candidate,new[-1][0],0o440),validate(candidate)))
        aggregate=work/'aggregate'
        phase('aggregate_sudo_validation',lambda: (write(aggregate,replacement_aggregate(candidate),0o600),validate(aggregate)))
    made=[]
    def make_backups():
        for (source,target,mode,digest),backup,data in zip(FILES,backups,new):
            os.link(target,backup,follow_symlinks=False);sync_parent(backup)
            require(backup.lstat().st_nlink==2);made.append(backup)
        if old_marker:
            os.link(manifest_path(),marker_backup,follow_symlinks=False);sync_parent(marker_backup)
            require(marker_backup.lstat().st_nlink==2);made.append(marker_backup)
    def restore():
        for (source,target,mode,digest),backup,original in zip(FILES,backups,old):
            if backup.exists() and target.exists(): replace_file(target,original,mode)
        if old_marker:
            if marker_backup.exists():
                old_files=next(files for name,files in APPROVED_OLD_VERSIONS if name==old_version)
                replace_file(manifest_path(),manifest_bytes(old_version,old_files),MANIFEST_MODE)
        elif manifest_path().exists() and not manifest_path().is_symlink(): manifest_path().unlink();sync_parent(manifest_path())
        for backup in made:
            if backup.exists(): backup.unlink();sync_parent(backup)
    try:
        phase('backup_creation',make_backups)
        phase('replacement',lambda: ([replace_file(target,data,mode) for (_,target,mode,digest),(data,_,_) in zip(FILES,new)], replace_file(manifest_path(),manifest_bytes(CURRENT_VERSION,tuple((target,mode,digest) for _,target,mode,digest in FILES)),MANIFEST_MODE)))
        phase('aggregate_sudo_validation',validate)
        phase('new_artifact_validation',lambda: ([artifact(target,digest,mode) for (_,target,mode,digest),(data,_,_) in zip(FILES,new)], validate_manifest(CURRENT_VERSION,tuple((target,mode,digest) for _,target,mode,digest in FILES))))
    except StageFailure:
        phase('rollback',restore)
        raise
    except BaseException:
        phase('rollback',restore)
        raise StageFailure('replacement')
    return 'upgraded_not_provisioned'


def rollback_upgrade():
    require(os.getuid()==0 and sys.argv[1:]==['--rollback-upgrade'])
    validate()
    version_name,version_files,old,backups,marker_backup,marker_data=rollback_candidates()
    try:
        for (target,mode,digest),data in zip(version_files,old): replace_file(target,data,mode)
        if marker_data is not None: replace_file(manifest_path(),marker_data,MANIFEST_MODE)
        elif manifest_path().exists() and not manifest_path().is_symlink(): manifest_path().unlink();sync_parent(manifest_path())
        validate()
        for target,mode,digest in version_files: artifact(target,digest,mode)
        if marker_data is not None: artifact(manifest_path(),manifest_digest(version_name,version_files),MANIFEST_MODE)
    except BaseException:
        # Leave rollback copies intact for a guarded human recovery; no deletion on ambiguity.
        raise
    for backup in backups: backup.unlink();sync_parent(backup)
    if marker_backup is not None and marker_backup.exists(): marker_backup.unlink();sync_parent(marker_backup)
    return 'rolled_back_previous_version'


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
    require(os.getuid()==0 and sys.argv[1:] in ([],['--rollback'],['--upgrade'],['--rollback-upgrade']))
    os.umask(0o077)
    if sys.argv[1:]==['--upgrade']: return upgrade()
    if sys.argv[1:]==['--rollback-upgrade']: return rollback_upgrade()
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
    require(not manifest_path().exists() and not manifest_path().is_symlink())
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
            staged=work/'manifest';write(staged,manifest_bytes(CURRENT_VERSION,tuple((target,mode,digest) for _,target,mode,digest in FILES)),MANIFEST_MODE)
            os.link(staged,manifest_path(),follow_symlinks=False)
            created.append((manifest_path(),staged.stat().st_ino))
            staged.unlink();sync_parent(manifest_path())
            validate_manifest(CURRENT_VERSION,tuple((target,mode,digest) for _,target,mode,digest in FILES))
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
    except StageFailure as caught: failure_stage=caught.stage;state='refused_or_incomplete';status=1
    except BaseException: failure_stage='precheck';state='refused_or_incomplete';status=1
    result={'mode':'paper-provision-install','state':state,'credentials_entered':False,'connected':False}
    if status: result['failure_stage']=failure_stage
    print(json.dumps(result,separators=(',',':')))
    return status


if __name__=='__main__': raise SystemExit(main())
