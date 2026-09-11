#!/usr/bin/python3 -I
"""Human-only, fixed-target LUKS2 initialization. Never reads a passphrase."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import resource
import signal
import stat
import subprocess
import sys
import termios
import types

INSTALLED = Path('/usr/local/sbin/ai-invest-storage-init')
CHECKOUT = Path('/home/rob/ai-invest')
WRAPPER = Path('/usr/local/sbin/ai-invest-operator-preflight')
PREFLIGHT = Path('/usr/local/libexec/ai-invest/operator_preflight.py')
RESULT = Path('/var/tmp/ai-invest-storage-init.json')
PARENT = Path('/var/lib/ai-invest')
IMAGE = PARENT / 'qualification.luks'
MOUNT = Path('/srv/ai-invest-secure')
MAPPER = Path('/dev/mapper/ai-invest-qualification')
SIZE = 68719476736
ENV = {'PATH':'/usr/sbin:/usr/bin:/sbin:/bin', 'LANG':'C', 'LC_ALL':'C'}
HASHES = {
    str(WRAPPER): '17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5',
    str(PREFLIGHT): 'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c',
    '/usr/sbin/cryptsetup': '5400fa036759e260dfefff9e1ce3281cf03f694003a6aed8b3a9cbb45f449fca',
    '/usr/sbin/mke2fs': '07cd24ce58a410cc9cee93c55ae5ac95986df016c5907dc7a49b55389bd41ed2',
    '/usr/bin/mount': 'fde2b1540ca79ea42df942653bdfd09b9b3e3ff1d4713602bd280f754033957a',
    '/usr/bin/unshare': 'a23c8863860669003dc4660039fe642f5795c8c2195898ebc5d01afa1ac3d11c',
    '/usr/bin/systemd-run': 'dbc8b988a849d5c9d7ef2de7068a6f107021bc6c11e0d7864c73f373eef726a7',
    '/usr/bin/systemctl': 'e0d3d0e9444da1b2b58c792c3f5028b69f049b77d5ca17b3ec0d09f89117225b',
    '/usr/bin/python3.12': '1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118',
    '/usr/bin/env': '886e5fa8be716b03eeda48856e0f04493f2969fc148fb7812594ffac647fa050',
}
STAGES = {'authorization','integrity','preflight','scope','allocate','format','unlock',
          'filesystem','mount','validate','complete','interrupted'}


class Refused(Exception):
    pass


def require(value):
    if not value: raise Refused()


def checked(path, *, directory=False):
    require(path.is_absolute() and path.resolve(strict=True) == path)
    for ancestor in path.parents:
        info = ancestor.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022)
    info = path.lstat()
    require(info.st_uid == 0 and not info.st_mode & 0o022)
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1)
    return info


def integrity():
    checked(INSTALLED)
    for name,digest in HASHES.items():
        path = Path(name)
        checked(path)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest)


def module(path):
    namespace = types.ModuleType('storage_dependency')
    namespace.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), namespace.__dict__)
    return namespace


def run(args, *, timeout=30):
    # Fixed non-secret commands only; output is intentionally not published.
    result = subprocess.run(args, env=ENV, stdin=subprocess.DEVNULL, capture_output=True,
                            timeout=timeout, close_fds=True, check=False)
    require(result.returncode == 0 and len(result.stdout) <= 8192 and len(result.stderr) <= 8192)
    return result.stdout.decode('ascii')


def protection(wrapper, preflight):
    memory_headroom()
    wrapper.require_console()
    wrapper.require_host(scoped=True)
    require(preflight.operator_ok(preflight.operator_snapshot()))
    group = preflight.cgroup_directory()
    require((group/'memory.max').read_text().strip() == str(2*1024**3))
    require((group/'pids.max').read_text().strip() == '32')
    cpu = (group/'cpu.max').read_text().split()
    require(len(cpu)==2 and cpu[0].isdigit() and cpu[1].isdigit() and 0<int(cpu[0])<=int(cpu[1]))
    require((group/'memory.swap.max').read_text().strip() == '0'
            and (group/'memory.swap.current').read_text().strip() == '0')


def storage_safety(preflight, *, allocated=False):
    memory_headroom()
    snapshot = preflight.plan_snapshot()
    for field in ('local_nonrotational_block_backing','root_owned_nonwritable_ancestors','mount_parent_same_filesystem'):
        require(snapshot[field] is True)
    if not allocated:
        require(preflight.plan_ok(snapshot))
    else:
        # Allocation has already consumed SIZE; don't subtract it twice.
        require(snapshot['available_bytes'] >= 200*1024**3
                and snapshot['available_bytes']*5 >= snapshot['total_bytes'])


def memory_headroom():
    values = [line.split() for line in Path('/proc/meminfo').read_text().splitlines()
              if line.startswith('MemAvailable:')]
    require(len(values)==1 and len(values[0])==3 and values[0][2]=='kB'
            and values[0][1].isdigit() and int(values[0][1])>=4*1024**2)


def scope_idle():
    state = run(['/usr/bin/systemctl','show','ai-invest-storage-init.scope',
                 '-p','ActiveState','--value']).strip()
    if state not in ('inactive','failed'): return False
    path = Path('/sys/fs/cgroup/system.slice/ai-invest-storage-init.scope/cgroup.events')
    if path.exists():
        values = dict(line.split() for line in path.read_text().splitlines())
        return values.get('populated')=='0'
    return True


def file_identity():
    checked(PARENT, directory=True)
    info = checked(IMAGE)
    require(stat.S_IMODE(info.st_mode)==0o600 and info.st_size==SIZE and info.st_blocks*512>=SIZE)
    return (info.st_dev, info.st_ino)


def sync_directory(path):
    fd = os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try: os.fsync(fd)
    finally: os.close(fd)


def mapper_identity(expected_image):
    require(file_identity()==expected_image)
    # /dev/mapper/name is an expected udev symlink; never relax code/file checks.
    device = MAPPER.resolve(strict=True)
    require(device.parent==Path('/dev') and re.fullmatch(r'dm-[0-9]+',device.name))
    info = device.stat()
    require(stat.S_ISBLK(info.st_mode) and info.st_uid==0)
    sysdev = Path('/sys/dev/block') / f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}'
    require((sysdev/'dm/name').read_text().strip() == MAPPER.name)
    require(re.fullmatch(r'CRYPT-LUKS2-[0-9a-f]{32}-ai-invest-qualification', (sysdev/'dm/uuid').read_text().strip()))
    slaves = list((sysdev/'slaves').iterdir())
    require(len(slaves)==1 and re.fullmatch(r'loop[0-9]+',slaves[0].name))
    backing = (slaves[0]/'loop/backing_file').read_text().strip()
    require(backing == str(IMAGE))
    require(file_identity()==expected_image)
    return info.st_rdev


def terminal_command(args, wrapper, preflight):
    """Only cryptsetup receives input; Python never reads/relays terminal bytes."""
    require(args[0]=='/usr/sbin/cryptsetup')
    integrity()
    protection(wrapper, preflight)
    original = termios.tcgetattr(0)
    quiet = original.copy()
    quiet[3] &= ~(termios.ECHO | termios.ECHONL)
    child = None
    try:
        termios.tcflush(0, termios.TCIFLUSH)
        termios.tcsetattr(0, termios.TCSAFLUSH, quiet)
        require(not termios.tcgetattr(0)[3] & (termios.ECHO | termios.ECHONL))
        # Across exec: cgroup/rlimits/namespaces remain; PR_SET_DUMPABLE does not.
        # The pinned Apport private-mount/same-PID ignore branch is the defense.
        child = subprocess.Popen(args, env=ENV, close_fds=True)
        require(child.wait(timeout=300)==0)
        protection(wrapper, preflight)
    finally:
        cleanup_ok = True
        if child is not None and child.poll() is None:
            try:
                child.terminate()
                child.wait(timeout=5)
            except Exception:
                try:
                    if child.poll() is None: child.kill()
                    child.wait(timeout=5)
                except Exception: cleanup_ok = False
        # Never turn echo back on while a secret reader may survive. The outer
        # exact-scope cleanup handles this case before terminal restoration.
        require(child is None or child.poll() is not None)
        # Independent cleanup attempts; no secret is read for restoration.
        restored = True
        try: termios.tcflush(0, termios.TCIFLUSH)
        except Exception: restored = False
        try: termios.tcsetattr(0, termios.TCSAFLUSH, original)
        except Exception: restored = False
        try: restored = restored and termios.tcgetattr(0)==original
        except Exception: restored = False
        require(restored and cleanup_ok)


def report(fd, stage, ready=False, *, publish=False):
    require(stage in STAGES and type(ready) is bool)
    data = (json.dumps({'mode':'storage-init', 'storage_ready':ready, 'stage':stage,
                        'gate2_passed':False},sort_keys=True)+'\n').encode()
    os.lseek(fd,0,os.SEEK_SET)
    os.ftruncate(fd,0)
    require(os.write(fd,data)==len(data))
    os.fsync(fd)
    if publish:
        os.fchmod(fd,0o644)
        os.fsync(fd)


def worker(wrapper, preflight, fd):
    protection(wrapper,preflight)
    storage_safety(preflight)
    report(fd,'allocate')
    PARENT.mkdir(mode=0o700)
    MOUNT.mkdir(mode=0o700)
    sync_directory(PARENT.parent)
    sync_directory(MOUNT.parent)
    image_fd = os.open(IMAGE,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        os.posix_fallocate(image_fd,0,SIZE)
        os.fsync(image_fd)
        sync_directory(PARENT)
        created = os.fstat(image_fd)
        identity = (created.st_dev,created.st_ino)
        require(file_identity()==identity)
        storage_safety(preflight,allocated=True)
        require(not os.path.lexists(MAPPER) and not os.path.ismount(MOUNT))
        checked(MOUNT,directory=True)
        require(not list(MOUNT.iterdir()))
        report(fd,'format')
        print('Only the NEW dedicated 64 GiB ai-invest image will be formatted.\n'
              'At cryptsetup prompts, type YES (also hidden), then your passphrase twice.\n'
              'Do not type secrets before the passphrase prompt. No recording or redirection.',flush=True)
        terminal_command(['/usr/sbin/cryptsetup','luksFormat','--type','luks2',
            '--cipher','aes-xts-plain64','--key-size','512','--hash','sha256',
            '--pbkdf','argon2id','--pbkdf-memory','1048576','--pbkdf-parallel','1',
            '--pbkdf-force-iterations','4','--verify-passphrase','--timeout','120',str(IMAGE)],wrapper,preflight)
        require(file_identity()==identity)
        run(['/usr/sbin/cryptsetup','isLuks','--type','luks2',str(IMAGE)])
        report(fd,'unlock')
        require(not os.path.lexists(MAPPER))
        terminal_command(['/usr/sbin/cryptsetup','open','--type','luks2','--tries','1',
            '--timeout','120','--disable-external-tokens',str(IMAGE),MAPPER.name],wrapper,preflight)
        report(fd,'filesystem')
        storage_safety(preflight,allocated=True)
        device = mapper_identity(identity)
        require(not os.path.ismount(MOUNT))
        require(not list(MOUNT.iterdir()))
        # No -F; only the newly created, identity-validated mapping is formatted.
        run(['/usr/sbin/mke2fs','-t','ext4','-m','1','-L','ai-invest-secure',
             '-E','nodiscard,lazy_itable_init=0,lazy_journal_init=0',str(MAPPER)],timeout=300)
        require(mapper_identity(identity)==device)
        report(fd,'mount')
    finally:
        os.close(image_fd)


def mount_and_validate(preflight):
    identity = file_identity()
    device = mapper_identity(identity)
    storage_safety(preflight,allocated=True)
    checked(MOUNT,directory=True)
    require(not os.path.ismount(MOUNT) and not list(MOUNT.iterdir()))
    run(['/usr/bin/mount','--no-canonicalize','--internal-only','-t','ext4',
         '-o','nodev,nosuid,noexec',str(MAPPER),str(MOUNT)])
    require(os.path.ismount(MOUNT) and MOUNT.stat().st_dev==device)
    # Parse only the exact dedicated mount's metadata, not other workloads.
    rows = [line.split() for line in Path('/proc/self/mountinfo').read_text().splitlines()
            if line.split()[4]==str(MOUNT)]
    require(len(rows)==1)
    fields = rows[0]
    require({'rw','nodev','nosuid','noexec'} <= set(fields[5].split(',')))
    require(fields[fields.index('-')+1]=='ext4' and mapper_identity(identity)==device)
    os.chmod(MOUNT,0o700)
    for name in ('postgresql','openbao','runtime','financial-audit','qualification-backups','qualification-restores'):
        (MOUNT/name).mkdir(mode=0o700)
    # Non-secret marker only, kept as creation evidence. No key/header backup here.
    marker = MOUNT/'runtime/storage-created'
    output = os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        require(os.write(output,b'ai-invest-luks2-v1\n')==19)
        os.fsync(output)
    finally: os.close(output)
    require(marker.read_bytes()==b'ai-invest-luks2-v1\n')
    sync_directory(marker.parent)
    sync_directory(MOUNT)
    require(mapper_identity(identity)==device)


def scope_command(identity):
    require(re.fullmatch(r'[0-9]{1,20}:[0-9]{1,20}',identity))
    return ['/usr/bin/systemd-run','--scope','--unit=ai-invest-storage-init','--expand-environment=no',
        '-p','MemoryMax=2G','-p','MemorySwapMax=0','-p','TasksMax=32','-p','CPUQuota=100%',
        '-p','RuntimeMaxSec=900','/usr/bin/unshare','--mount','--propagation','private',
        '/usr/bin/env','-i','PATH=/usr/sbin:/usr/bin:/sbin:/bin','LANG=C','LC_ALL=C',
        '/usr/bin/python3.12','-I','-B',str(INSTALLED),'--worker',identity]


def main():
    fd = None
    scope_started = False
    terminal_state = None
    scoped = sys.argv[1:2]==['--worker']
    stage = 'authorization'
    try:
        require(os.getuid()==0 and os.geteuid()==0 and Path(__file__).absolute()==INSTALLED)
        require(sys.argv[1:]==['--initialize'] or (scoped and len(sys.argv)==3))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        os.umask(0o077)
        def interrupted(signum, frame):
            raise InterruptedError()
        for signum in (signal.SIGHUP,signal.SIGTERM,signal.SIGTSTP,signal.SIGQUIT):
            signal.signal(signum,interrupted)
        stage = 'integrity'
        integrity()
        wrapper,preflight = module(WRAPPER),module(PREFLIGHT)
        wrapper.require_console()
        terminal_state = termios.tcgetattr(0)
        if not scoped:
            require(os.environ.get('SUDO_UID')==str(wrapper.OPERATOR_UID)
                and Path('/proc/self/loginuid').read_text().strip()==str(wrapper.OPERATOR_UID)
                and os.environ.get('SUDO_USER')==pwd.getpwuid(wrapper.OPERATOR_UID).pw_name
                and os.environ.get('SUDO_COMMAND')==str(INSTALLED)+' --initialize')
            wrapper.require_operator_environment()
            wrapper.require_console_session()
        os.environ.clear(); os.environ.update(ENV)
        wrapper.require_host(scoped=scoped)
        # No private key material ever reaches this process. Drop dumpability anyway.
        require(ctypes.CDLL(None).prctl(4,0,0,0,0)==0)
        wrapper.RESULT = RESULT
        fd = wrapper.open_scoped_result(sys.argv[2]) if scoped else wrapper.create_result()
        stage = 'preflight'
        storage_safety(preflight)
        if scoped:
            worker(wrapper,preflight,fd)
        else:
            info = os.fstat(fd)
            stage = 'scope'
            report(fd,stage)
            require(scope_idle())
            scope_started = True
            result = subprocess.run(scope_command(f'{info.st_dev}:{info.st_ino}'),
                env=ENV,close_fds=True,check=False,timeout=930)
            require(scope_idle())
            scope_started = False
            termios.tcflush(0,termios.TCIFLUSH)
            termios.tcsetattr(0,termios.TCSAFLUSH,terminal_state)
            require(termios.tcgetattr(0)==terminal_state)
            os.lseek(fd,0,os.SEEK_SET)
            progress = json.loads(os.read(fd,4096))
            require(progress.get('stage') in STAGES)
            stage = progress['stage']
            require(result.returncode==0 and stage=='mount')
            stage = 'mount'
            mount_and_validate(preflight)
            stage = 'complete'
            report(fd,stage,True,publish=True)
            print('Dedicated storage mounted and validated. Share only /var/tmp/ai-invest-storage-init.json.')
        return 0
    except BaseException:
        # Preserve partial image/mapping/filesystem. Never retry formatting/delete.
        if not scoped and scope_started:
            try:
                run(['/usr/bin/systemctl','stop','ai-invest-storage-init.scope'],timeout=20)
                require(scope_idle())
                if terminal_state is not None:
                    termios.tcflush(0,termios.TCIFLUSH)
                    termios.tcsetattr(0,termios.TCSAFLUSH,terminal_state)
            except BaseException:
                print('Scope cleanup uncertain; stop typing and use the retained administration session.',file=sys.stderr)
                return 1  # Do not publish success or invite another console command.
        if fd is not None:
            try:
                if scoped:
                    pass  # worker already recorded its last destructive stage
                else: report(fd,stage,publish=True)
            except Exception: pass
        print('Storage initialization stopped. Stop typing. Preserve all targets; do not rerun initialization.',file=sys.stderr)
        return 1
    finally:
        if fd is not None: os.close(fd)


if __name__=='__main__':
    raise SystemExit(main())
