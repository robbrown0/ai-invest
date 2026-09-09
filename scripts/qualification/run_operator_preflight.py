#!/usr/bin/python3 -I
"""Human-console metadata wrapper. No secret input or bootstrap operations."""
import configparser
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import re
import resource
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
CHECKOUT = Path('/home/rob/ai-invest')
INSTALLED = Path('/usr/local/sbin/ai-invest-operator-preflight')
LIB = Path('/usr/local/libexec/ai-invest')
HELPER = LIB / 'operator_preflight.py'
HOST_ID = LIB / 'host-id'
RESULT = Path('/var/tmp/ai-invest-operator-preflight.json')
HELPER_COMMIT = 'ff75739e4bd420cd17104e34e1eb2b1cdcd54e22'
HELPER_SHA256 = 'a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd'
CLEAN_ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
PLAN_BOOL = {'local_nonrotational_block_backing', 'capacity_margin_pass',
             'root_owned_nonwritable_ancestors', 'targets_absent', 'mount_parent_same_filesystem'}
PLAN_INT = {'total_bytes', 'available_bytes', 'proposed_volume_bytes', 'remaining_bytes'}
OP_BOOL = {'root_operator', 'direct_virtual_console', 'cpu_limit_bounded', 'core_soft_zero',
           'core_hard_zero', 'mount_namespace_differs_from_visible_pid1',
           'pid_namespace_matches_visible_pid1', 'reviewed_apport_handler', 'reviewed_core_pattern'}
OP_LIMIT = {'memory_max', 'memory_swap_max', 'memory_swap_current', 'pids_max'}


class Rejected(Exception):
    """Only fixed diagnostics may be emitted by the caller."""


def require(condition):
    if not condition:
        raise Rejected()


def checked_path(path, *, root_owned=True, directory=False):
    """No symlinks at any component; root-owned immutable installed ancestry."""
    require(path.is_absolute() and path.resolve(strict=True) == path)
    for ancestor in reversed(path.parents):
        info = ancestor.lstat()
        require(stat.S_ISDIR(info.st_mode) and not info.st_mode & 0o022)
        if root_owned:
            require(info.st_uid == 0)
    info = path.lstat()
    require((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)))
    require(not info.st_mode & 0o022)
    if root_owned:
        require(info.st_uid == 0)
    return info


def checked_bytes(path, *, root_owned=True, maximum=65536):
    before = checked_path(path, root_owned=root_owned)
    require(before.st_size <= maximum and before.st_nlink == 1)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        actual = os.fstat(fd)
        require((actual.st_dev, actual.st_ino) == (before.st_dev, before.st_ino))
        value = os.read(fd, maximum + 1)
        require(len(value) <= maximum)
        return value
    finally:
        os.close(fd)


def trusted_helper():
    require(Path(__file__).absolute() == INSTALLED)
    installed = checked_bytes(INSTALLED)
    checked_path(CHECKOUT, root_owned=False, directory=True)
    checked_path(CHECKOUT / '.git', root_owned=False, directory=True)
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(checked_bytes(CHECKOUT / '.git/config', root_owned=False).decode())
    require(config.get('remote "origin"', 'url') == 'https://github.com/robbrown0/ai-invest.git')
    require(checked_bytes(CHECKOUT / '.git/HEAD', root_owned=False).strip()
            == b'ref: refs/heads/phase3/synthetic-qualification')
    source = checked_bytes(CHECKOUT / 'scripts/qualification/run_operator_preflight.py', root_owned=False)
    require(hmac.compare_digest(installed, source))
    helper = checked_bytes(HELPER)
    require(hashlib.sha256(helper).hexdigest() == HELPER_SHA256)
    require(hmac.compare_digest(helper, checked_bytes(
        CHECKOUT / 'scripts/qualification/operator_preflight.py', root_owned=False)))
    return helper


def console_ok(names, devices, environment):
    forbidden = ('SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY', 'DISPLAY', 'WAYLAND_DISPLAY',
                 'TMUX', 'STY')
    return (not any(environment.get(key) for key in forbidden)
            and len(names) == 3 and len(set(names)) == 1
            and re.fullmatch(r'/dev/tty[1-9][0-9]*', names[0]) is not None
            and len(devices) == 3 and all(stat.S_ISCHR(mode) and major == 4
                                        and 1 <= minor <= 63
                                        and minor == int(names[0].removeprefix('/dev/tty'))
                                        for mode, major, minor in devices))


def require_console():
    names, devices = [], []
    for fd in (0, 1, 2):
        require(os.isatty(fd))
        name = os.ttyname(fd)
        info = os.fstat(fd)
        target = os.lstat(name)
        require(stat.S_ISCHR(target.st_mode) and info.st_rdev == target.st_rdev)
        names.append(name)
        devices.append((info.st_mode, os.major(info.st_rdev), os.minor(info.st_rdev)))
    require(console_ok(names, devices, os.environ))
    # A redirected VT descriptor must not disguise a different controlling PTY.
    terminal = int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[4])
    require(terminal == os.makedev(4, devices[0][2]))


def require_host(scoped=False):
    require(sys.platform == 'linux' and Path('/proc/1/comm').read_text().strip() == 'systemd')
    enrolled = checked_bytes(HOST_ID, maximum=64)
    require(stat.S_IMODE(HOST_ID.stat().st_mode) == 0o600)
    current = checked_bytes(Path('/etc/machine-id'), maximum=64)
    require(re.fullmatch(rb'[0-9a-f]{32}\n?', enrolled) is not None)
    require(hmac.compare_digest(enrolled, current))
    require(os.stat('/').st_dev == os.stat('/proc/1/root').st_dev
            and os.stat('/').st_ino == os.stat('/proc/1/root').st_ino)
    for kind in ('pid', 'user', 'mnt'):
        same = os.stat('/proc/self/ns/' + kind).st_ino == os.stat('/proc/1/ns/' + kind).st_ino
        require(same if kind != 'mnt' or not scoped else not same)
    detected = subprocess.run(['/usr/bin/systemd-detect-virt', '--container', '--quiet'],
                              env=CLEAN_ENV, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=10, check=False)
    require(detected.returncode == 1)
    if scoped:
        # Private propagation must be observed, not inferred from unshare syntax.
        for line in Path('/proc/self/mountinfo').read_text().splitlines():
            fields = line.split()
            require('-' in fields)
            require(not any(field.startswith(('shared:', 'master:', 'propagate_from:'))
                            for field in fields[6:fields.index('-')]))


def failure():
    return {'mode': 'operator', 'checks_passed': False, 'error': 'metadata_unavailable',
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}


def validate_report(report):
    require(type(report) is dict)
    base = {'mode', 'checks_passed', 'secret_entry_authorized', 'runtime_crash_suppression_qualified'}
    require(report.get('mode') in ('plan', 'operator') and type(report.get('checks_passed')) is bool)
    require(report.get('secret_entry_authorized') is False
            and report.get('runtime_crash_suppression_qualified') is False)
    if 'error' in report:
        require(set(report) == base | {'error'} and report['error'] == 'metadata_unavailable'
                and report['checks_passed'] is False)
        return report
    require(set(report) == base | {'observations'} and type(report.get('observations')) is dict)
    observation = report['observations']
    bools = PLAN_BOOL if report['mode'] == 'plan' else OP_BOOL
    others = PLAN_INT | {'filesystem_type'} if report['mode'] == 'plan' else OP_LIMIT
    require(set(observation) == bools | others)
    require(all(type(observation[key]) is bool for key in bools))
    if report['mode'] == 'plan':
        require(all(type(observation[key]) is int and abs(observation[key]) < 2 ** 64 for key in PLAN_INT))
        # Approved source uses a filesystem label; do not return arbitrary strings.
        require(observation['filesystem_type'] in ('ext4', 'nfs', 'nfs4', 'cifs', 'overlay', 'tmpfs'))
    else:
        require(all(type(observation[key]) is str
                    and re.fullmatch(r'(?:max|[0-9]{1,20})', observation[key]) for key in OP_LIMIT))
    return report


def invoke_helper(source, mode):
    # Execute only checked bytes from the root-owned, pinned committed helper.
    # Python-level capture preserves real fds 0/1/2 for its existing TTY checks.
    namespace = {'__name__': 'qualification_operator_helper', '__file__': str(HELPER)}
    output, errors = io.StringIO(), io.StringIO()
    previous = sys.argv
    try:
        with redirect_stdout(output), redirect_stderr(errors):
            exec(compile(source, str(HELPER), 'exec'), namespace)
            sys.argv = [str(HELPER), mode]
            status = namespace['main']()
        require(not errors.getvalue() and len(output.getvalue()) <= 8192)
        report = validate_report(json.loads(output.getvalue()))
        require(report['mode'] == mode and status == (0 if report['checks_passed'] else 1))
        return report
    finally:
        sys.argv = previous


def result_parent_ok():
    checked_path(Path('/var'), directory=True)
    info = RESULT.parent.lstat()
    require(RESULT.parent.resolve(strict=True) == RESULT.parent and stat.S_ISDIR(info.st_mode)
            and info.st_uid == 0 and stat.S_IMODE(info.st_mode) == 0o1777)


def create_result():
    result_parent_ok()
    fd = os.open(RESULT, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    os.fchmod(fd, 0o600)
    return fd


def open_scoped_result(identity):
    require(re.fullmatch(r'[0-9]{1,20}:[0-9]{1,20}', identity) is not None)
    result_parent_ok()
    fd = os.open(RESULT, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == 0o600
                and identity == f'{info.st_dev}:{info.st_ino}')
        return fd
    except BaseException:
        os.close(fd)
        raise


def save_result(fd, report, publish=False):
    data = (json.dumps(validate_report(report), sort_keys=True) + '\n').encode()
    require(len(data) <= 8192)
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    with os.fdopen(os.dup(fd), 'wb', closefd=True) as stream:
        stream.write(data)
        stream.flush()
    os.fsync(fd)
    if publish:
        os.fchmod(fd, 0o644)  # Only allowlisted non-secret JSON is now readable over SSH.
        os.fsync(fd)
        print('A new sanitized result is ready at /var/tmp/ai-invest-operator-preflight.json.')


def scope_command(identity):
    return ['/usr/bin/systemd-run', '--scope', '--unit=ai-invest-operator-preflight',
            '-p', 'MemoryMax=2G', '-p', 'MemorySwapMax=0', '-p', 'TasksMax=32', '-p', 'CPUQuota=100%',
            '/usr/bin/unshare', '--mount', '--propagation', 'private',
            '/usr/bin/env', '-i', 'PATH=/usr/sbin:/usr/bin:/sbin:/bin', 'LANG=C', 'LC_ALL=C',
            '/bin/bash', '--noprofile', '--norc', '-c',
            'set -eu; ulimit -Sc 0; ulimit -Hc 0; exec /usr/bin/python3 -I -B "$1" --scoped "$2"',
            'ai-invest-preflight', str(INSTALLED), identity]


def main():
    fd = None
    scoped = False
    report = failure()
    try:
        require(os.geteuid() == 0)
        require(sys.argv[1:] == [] or (len(sys.argv) == 3 and sys.argv[1] == '--scoped'))
        scoped = len(sys.argv) == 3
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        os.umask(0o077)
        fd = open_scoped_result(sys.argv[2]) if scoped else create_result()
        require_console()
        source = trusted_helper()
        os.environ.clear()
        os.environ.update(CLEAN_ENV)
        require_host(scoped)
        if scoped:
            require(invoke_helper(source, 'plan')['checks_passed'])
            report = invoke_helper(source, 'operator')
        else:
            report = invoke_helper(source, 'plan')
            if report['checks_passed']:
                info = os.fstat(fd)
                save_result(fd, failure())
                completed = subprocess.run(scope_command(f'{info.st_dev}:{info.st_ino}'),
                                           env=CLEAN_ENV, check=False)
                os.lseek(fd, 0, os.SEEK_SET)
                report = validate_report(json.loads(os.read(fd, 8193)))
                require(report['mode'] == 'operator'
                        and completed.returncode == (0 if report['checks_passed'] else 1))
        save_result(fd, report, publish=not scoped)
        return 0 if report['checks_passed'] else 1
    except Exception:
        if fd is not None:
            try:
                save_result(fd, failure(), publish=not scoped)
            except Exception:
                pass  # An incomplete/private file is not a published result.
        print('Preflight refused. No secret entry authorized. Existing result files are never replaced.', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Do not publish a result while an interrupted scope might still be exiting.
        print('Preflight interrupted; no completed result or secret entry authorization.', file=sys.stderr)
        return 130
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


if __name__ == '__main__':
    raise SystemExit(main())
