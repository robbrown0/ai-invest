#!/usr/bin/python3 -I
"""Fixed synthetic crash trial, invoked only by the reviewed operator wrapper.

No standalone CLI, secret input, external command, file writer, or bootstrap.
Unobserved channels remain NOT_TESTED; this cannot authorize real secret entry.
"""
import ctypes
import errno
import faulthandler
import grp
import json
import os
from pathlib import Path
import re
import resource
import select
import signal
import stat
import struct
import time

MAX_RESULT = 4096
DEADLINE = 35
OBSERVATION_SECONDS = 10
MAX_OBSERVATION = 1024 * 1024
MAX_FIELD = 65536
SETUP_STAGES = ('setup_journal', 'setup_log_directory', 'setup_log_file', 'setup_crash_store')
JOURNAL_FIELDS = ('_BOOT_ID', '_PID', 'COREDUMP_PID', 'OBJECT_PID',
    '_SYSTEMD_UNIT', 'OBJECT_SYSTEMD_UNIT', 'UNIT', 'MESSAGE', 'COREDUMP',
    'COREDUMP_FILENAME', 'COREDUMP_CMDLINE', 'COREDUMP_ENVIRON',
    'COREDUMP_PROC_STATUS', 'COREDUMP_PROC_MAPS', 'COREDUMP_PROC_LIMITS', '_CMDLINE')
CATEGORIES = (
    'runtime_limits', 'dumpable_parent', 'dumpable_child', 'crash_signal',
    'kernel_core_flag', 'own_argv', 'own_environment', 'stdio_detached',
    'child_reaped', 'cleanup', 'bounded_result', 'collector_retention', 'journal',
    'sudo_logs', 'shell_history', 'application_logs', 'temporary_files',
    'swap_bytes', 'git_worktree', 'git_index', 'git_history', 'ci_artifacts',
    'human_input_path', 'observation_window', 'apport_log', 'crash_store',
    *SETUP_STAGES,
)
STATES = frozenset(('PASS', 'FAIL', 'NOT_TESTED', 'NOT_APPLICABLE'))
JOURNAL_STAGES = frozenset(('not_started', 'initial_change', 'cursor_restore',
    'filters', 'seek', 'iteration', 'timestamp_boot', 'field_read', 'field_shape',
    'attribution', 'final_change', 'budget', 'complete'))
JOURNAL_REASONS = frozenset(('not_started', 'api_error', 'invalidation',
    'anchor_unavailable', 'unexpected_representation', 'incomplete_field',
    'attribution_mismatch', 'time_limit', 'record_limit', 'byte_limit',
    'append_pending', 'positive_match', 'complete', 'record_boot_mismatch',
    'record_before_window', 'invalid_observation_interval', 'ordering_ambiguous'))
# PR_SET_PDEATHSIG, PR_GET_DUMPABLE, PR_SET_DUMPABLE from linux/prctl.h.
LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.prctl.restype = ctypes.c_int


class Refused(Exception):
    pass


class SetupIncomplete(Exception):
    pass


class JournalIncomplete(Refused):
    def __init__(self, reason):
        require(reason in JOURNAL_REASONS)
        self.reason = reason


def require(value):
    if not value:
        raise Refused()


def report(results=None):
    values = dict.fromkeys(CATEGORIES, 'NOT_TESTED')
    values.update(journal_stage='not_started', journal_reason='not_started')
    if results:
        require(type(results) is dict and set(results) <= set(values))
        require(all(type(value) is str and value in
                    (JOURNAL_STAGES if key == 'journal_stage' else
                     JOURNAL_REASONS if key == 'journal_reason' else STATES)
                    for key, value in results.items()))
        values.update(results)
    # Missing collector/input/leakage evidence deliberately prevents overall PASS.
    setup_failures = [name for name in SETUP_STAGES if values[name] == 'FAIL']
    return {'mode': 'crash-test', 'checks_passed': False,
            'failed_checks': setup_failures or ['crash_trial_failed' if 'FAIL' in values.values() else 'coverage_incomplete'],
            'results': values, 'secret_entry_authorized': False,
            'runtime_crash_suppression_qualified': False}


def validate(value):
    require(type(value) is dict and set(value) == set(report()))
    require(value['checks_passed'] is False and value['secret_entry_authorized'] is False
            and value['runtime_crash_suppression_qualified'] is False)
    require(value == report(value.get('results')))
    require(type(value['results']) is dict and set(value['results']) == set(report()['results']))
    return value


def prctl(option, value=0):
    answer = LIBC.prctl(ctypes.c_int(option), ctypes.c_ulong(value),
                        ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0))
    require(answer >= 0)
    return answer


def protect(parent_pid):
    # No canary exists at this point. A dead supervisor cannot leave an orphan.
    require(prctl(1, signal.SIGKILL) == 0)
    require(os.getppid() == parent_pid)
    require(prctl(4, 0) == 0 and prctl(3) == 0)
    faulthandler.disable()
    require(not faulthandler.is_enabled())
    require(resource.getrlimit(resource.RLIMIT_CORE) == (0, 0))


def runtime_group():
    rows = Path('/proc/self/cgroup').read_text().splitlines()
    require(len(rows) == 1 and rows[0].startswith('0::/'))
    root = Path('/sys/fs/cgroup').resolve(strict=True)
    group = (root / rows[0][3:].lstrip('/')).resolve(strict=True)
    require(group != root and group.is_relative_to(root))
    return group


def runtime_limits(expected=None):
    group = runtime_group()
    if expected is not None:
        require(group == expected)
    def number(name):
        value = (group / name).read_text().strip()
        require(value.isascii() and value.isdecimal())
        return int(value)
    require(0 < number('memory.max') <= 2 * 1024 ** 3)
    require(number('memory.swap.max') == 0 and number('memory.swap.current') == 0)
    require(0 < number('pids.max') <= 32)
    cpu = (group / 'cpu.max').read_text().split()
    require(len(cpu) == 2 and all(value.isascii() and value.isdecimal() for value in cpu))
    require(0 < int(cpu[0]) <= int(cpu[1]) and int(cpu[1]) > 0)
    require(resource.getrlimit(resource.RLIMIT_CORE) == (0, 0))
    require(os.stat('/proc/self/ns/mnt').st_ino != os.stat('/proc/1/ns/mnt').st_ino)
    require(os.stat('/proc/self/ns/pid').st_ino == os.stat('/proc/1/ns/pid').st_ino)
    require(len(list(Path('/proc/self/task').iterdir())) == 1)
    return group


def detach(keep):
    # Only this worker's descriptor table. No unrelated process inspection.
    for name in os.listdir('/proc/self/fd'):
        fd = int(name)
        if fd != keep:
            try:
                os.close(fd)
            except OSError:
                pass  # Directory enumeration's already-closed internal descriptor.
    null = os.open('/dev/null', os.O_RDWR | os.O_CLOEXEC)
    for fd in (0, 1, 2):
        os.dup2(null, fd)
    if null > 2 and null != keep:
        os.close(null)
    expected = os.stat('/dev/null').st_rdev
    require(all(stat.S_ISCHR(os.fstat(fd).st_mode) and os.fstat(fd).st_rdev == expected
                for fd in (0, 1, 2)))


def contains(canary, data):
    # Local comparisons only; no stable digest or reversible representation returned.
    return canary in data or canary.hex().encode('ascii') in data


def bounded_read(path, maximum=65536):
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        data = os.read(fd, maximum + 1)
        require(len(data) <= maximum)
        return data
    finally:
        os.close(fd)


def wait_child(pid, deadline):
    while time.monotonic() < deadline:
        found, status = os.waitpid(pid, os.WNOHANG)
        if found == pid:
            return status
        time.sleep(0.02)
    raise Refused()


def wait_exit(pid, deadline):
    # Keep the zombie/PID identity through observation, then reap normally.
    while time.monotonic() < deadline:
        result = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        if result is not None:
            require(result.si_pid == pid)
            return
        time.sleep(0.02)
    raise Refused()


def root_path(path, directory=False, sticky=False):
    target = Path(path)
    require(target.resolve(strict=True) == target)
    for item in (target, *target.parents):
        info = item.lstat()
        require(info.st_uid == 0 and (not info.st_mode & 0o022 or
                item == target == Path('/var/crash') and sticky
                and bool(info.st_mode & stat.S_ISVTX)))
    info = target.lstat()
    require(stat.S_ISDIR(info.st_mode) if directory else
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1)
    return info


def fingerprint(info):
    # Reading may update atime; mutation checks use identity/size/mtime/ctime.
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def log_directory_policy(info, syslog_gid, root_gid):
    # Observation source ONLY. Never used for executable/helper/policy paths.
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0)
    require((info.st_gid, stat.S_IMODE(info.st_mode)) in
            ((root_gid, 0o755), (syslog_gid, 0o755), (syslog_gid, 0o775)))


def log_file_policy(info):
    require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and info.st_nlink == 1)
    require(stat.S_IMODE(info.st_mode) in (0o600, 0o640, 0o644))


def log_acl_policy(fd):
    # Mode 0775 can hide additional named-user write grants in a POSIX ACL.
    # Inspect only presence on the held directory; never publish ACL contents.
    try:
        os.getxattr(fd, 'system.posix_acl_access')
    except OSError as error:
        require(error.errno == errno.ENODATA)
        return
    raise Refused()


class LogSource:
    """Fixed /var/log/apport.log reader, never a code-loading trust policy.

    Root and approved syslog-directory writers remain trusted. Descriptor
    anchoring detects observed substitutions, not malicious pre-baseline erasure.
    """
    def __init__(self):
        self.chain = []
        self.fd = None
        self.info = None
        self.watch_fd = None
        self.watch_changed = False

    def setup_directory(self):
        self.syslog_gid = grp.getgrnam('syslog').gr_gid
        self.root_gid = grp.getgrnam('root').gr_gid
        require(type(self.syslog_gid) is int and type(self.root_gid) is int
                and self.syslog_gid >= 0 and self.root_gid >= 0
                and self.syslog_gid != self.root_gid)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        for name in ('/', 'var', 'log'):
            parent = self.chain[-1][0] if self.chain else None
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if name == 'log':
                log_directory_policy(before, self.syslog_gid, self.root_gid)
            else:
                require(stat.S_ISDIR(before.st_mode) and before.st_uid == 0
                        and not before.st_mode & 0o022)
            fd = os.open(name, flags, dir_fd=parent)
            # Register immediately, including a subsequently rejected descriptor.
            self.chain.append((fd, parent, name, before))
            require(fingerprint(os.fstat(fd)) == fingerprint(before))
            require(fingerprint(os.stat(name, dir_fd=parent, follow_symlinks=False)) == fingerprint(before))
        self.watch_fd = LIBC.inotify_init1(os.O_CLOEXEC | os.O_NONBLOCK)
        require(self.watch_fd >= 0)
        # Kernel-provided link to this process's retained directory FD only.
        # Unlike a mutable /var/log pathname, it cannot select another inode.
        self.watch_id = LIBC.inotify_add_watch(self.watch_fd,
            ('/proc/self/fd/' + str(self.chain[-1][0])).encode('ascii'), 0x01000FCE)
        require(self.watch_id >= 0)  # IN_ONLYDIR plus reviewed mutation events.
        self.verify_directory()

    def verify_events(self):
        require(not self.watch_changed and self.watch_fd is not None)
        try:
            for _ in range(4):
                try:
                    data = os.read(self.watch_fd, 65536)
                except BlockingIOError:
                    return
                require(data and len(data) <= 65536)
                offset = 0
                while offset < len(data):
                    require(len(data) - offset >= 16)
                    wd, mask, _, size = struct.unpack_from('iIII', data, offset)
                    require(wd == self.watch_id and not mask & 0xEC00)
                    require(mask and not mask & ~0x40000FCE)
                    require(0 < size <= 4096 and size % 4 == 0 and offset + 16 + size <= len(data))
                    padded = data[offset + 16:offset + 16 + size]
                    name, separator, padding = padded.partition(b'\0')
                    require(separator and name and b'/' not in name and not padding.strip(b'\0'))
                    require(name != b'apport.log')
                    offset += 16 + size
            raise Refused()  # Queue not proven drained within the fixed budget.
        except BaseException:
            self.watch_changed = True  # Never clear a consumed mutation/error.
            raise

    def verify_directory(self):
        require(len(self.chain) == 3)
        for fd, parent, name, old in self.chain:
            held = os.fstat(fd)
            named = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(held.st_mode) and stat.S_ISDIR(named.st_mode))
            require((held.st_dev, held.st_ino) == (old.st_dev, old.st_ino)
                    == (named.st_dev, named.st_ino))
            if name == 'log':
                log_directory_policy(held, self.syslog_gid, self.root_gid)
                log_directory_policy(named, self.syslog_gid, self.root_gid)
                log_acl_policy(fd)
                # Detect entry changes, including rename-away-and-back or an
                # initially absent file created then removed during observation.
                require(fingerprint(held) == fingerprint(old) == fingerprint(named))
            else:
                require(held.st_uid == named.st_uid == 0
                        and not (held.st_mode | named.st_mode) & 0o022)
        self.verify_events()

    def named_file(self):
        try:
            return os.stat('apport.log', dir_fd=self.chain[-1][0], follow_symlinks=False)
        except FileNotFoundError:
            return None

    def setup_file(self):
        self.verify_directory()
        before = self.named_file()
        if before is not None:
            log_file_policy(before)
            self.fd = os.open('apport.log', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                              dir_fd=self.chain[-1][0])
            held = os.fstat(self.fd)
            log_file_policy(held)
            require(fingerprint(held) == fingerprint(before))
            self.info = held
            self.verify_file()
        else:
            require(self.named_file() is None)
        self.verify_directory()

    def verify_file(self):
        named = self.named_file()
        require(named is not None and self.fd is not None)
        held = os.fstat(self.fd)
        log_file_policy(named)
        log_file_policy(held)
        require((held.st_dev, held.st_ino) == (self.info.st_dev, self.info.st_ino))
        require(fingerprint(held) == fingerprint(named))
        return held

    def observe(self, child, canary):
        stable = True
        try:
            self.verify_directory()
            if self.info is None:
                require(self.named_file() is None)
                self.verify_directory()
                return 'PASS', False
            self.verify_file()
        except Exception:
            stable = False
        require(self.info is not None and self.fd is not None)
        # Read only appended bytes of the already anchored original file, even
        # after rotation, to avoid erasing a known positive. Never open a replacement.
        now = os.fstat(self.fd)
        require(stat.S_ISREG(now.st_mode) and now.st_uid == 0
                and (now.st_dev, now.st_ino) == (self.info.st_dev, self.info.st_ino))
        require(self.info.st_size <= now.st_size <= self.info.st_size + MAX_OBSERVATION)
        data = os.pread(self.fd, now.st_size - self.info.st_size, self.info.st_size)
        leaked, complete = apport_records(data, child, canary)
        if leaked:
            return 'FAIL', True
        require(len(data) == now.st_size - self.info.st_size)
        self.verify_directory()
        after = self.verify_file()
        require(stable and fingerprint(after) == fingerprint(now))
        if fingerprint(now) == fingerprint(self.info):
            return 'PASS', False
        # Any append/metadata rewrite prevents a no-invocation conclusion.
        return ('PASS' if complete and data else 'NOT_TESTED'), True

    def close(self):
        failed = False
        owned = ([self.fd] if self.fd is not None else [])
        if self.watch_fd is not None and self.watch_fd >= 0:
            owned.append(self.watch_fd)
        owned += [item[0] for item in reversed(self.chain)]
        self.fd, self.watch_fd, self.chain = None, None, []
        for fd in owned:
            try:
                os.close(fd)
            except BaseException:
                failed = True
        require(not failed)


def journal_groups(boot, parent, child):
    scope = 'ai-invest-operator-preflight.scope'
    return [(('_BOOT_ID', boot), (key, value)) for key, value in (
        ('_PID', str(parent)), ('_PID', str(child)), ('COREDUMP_PID', str(child)),
        ('OBJECT_PID', str(child)), ('_SYSTEMD_UNIT', scope),
        ('OBJECT_SYSTEMD_UNIT', scope), ('UNIT', scope))]


def journal_entry(entry, groups, canary):
    require(type(entry) is dict and 0 < len(entry) <= 256)
    require(all(type(key) is str and type(value) is bytes
                and len(key.encode('ascii')) + 1 + len(value) < MAX_FIELD
                for key, value in entry.items()))
    require(sum(len(value) for value in entry.values()) <= MAX_OBSERVATION)
    require(any(all(entry.get(key) == value.encode('ascii') for key, value in group)
                for group in groups))
    leaked = any(contains(canary, value) for value in entry.values())
    collector = any(key in entry for key in ('COREDUMP_PID', 'COREDUMP', 'COREDUMP_FILENAME'))
    return leaked, collector


def apport_records(data, child, canary):
    # Only new interval bytes. Parse attribution before examining payloads.
    require(len(data) <= MAX_OBSERVATION)
    rows, valid = [], not data or data.endswith(b'\n')
    # A trailing partial record makes coverage incomplete but cannot erase a
    # positive match in an earlier complete attributable record.
    for line in data.split(b'\n')[:-1]:
        match = re.fullmatch(rb'(?:ERROR|WARNING|INFO|DEBUG|CRITICAL): apport \(pid ([0-9]{1,10})\) [^\r\n]{1,80}?: (.*)', line)
        if match is None:
            valid = False
        else:
            rows.append(match.groups())
    markers = (b'host pid ' + str(child).encode() + b' crashed in a separate mount namespace, ignoring',
               b'called for global pid ' + str(child).encode() + b', signal ')
    # Do not attribute other lines by collector PID: that PID is not pinned.
    targeted = [message for _, message in rows if any(message.startswith(marker) for marker in markers)]
    leaked = any(contains(canary, message) for message in targeted)
    return leaked, valid and not rows  # Any collector activity stays incomplete.


class Observation:
    """Fixed read-only sinks inside the protected worker; no external canary receiver."""
    def __init__(self):
        self.reader = None
        self.watch_fd = None
        self.log = LogSource()
        self.ready = False
        self.setup = dict.fromkeys(SETUP_STAGES, 'NOT_TESTED')
        # Four fixed stages, not a caller-selected diagnostic/command framework.
        # Journal and store probes remain independent of the log-directory policy.
        for name, operation in (('setup_journal', self.setup_journal),
                                ('setup_log_directory', self.log.setup_directory),
                                ('setup_log_file', self.log.setup_file),
                                ('setup_crash_store', self.setup_store)):
            if name == 'setup_log_file' and self.setup['setup_log_directory'] != 'PASS':
                continue
            try:
                operation()
                self.setup[name] = 'PASS'
            except BaseException:
                self.setup[name] = 'FAIL'
        self.ready = all(value == 'PASS' for value in self.setup.values())
        if self.ready:
            self.start, self.wall = time.monotonic(), time.time()

    def setup_journal(self):
        # Import installed standard binding BEFORE random material exists.
        from systemd import _reader
        self.boot = bounded_read('/proc/sys/kernel/random/boot_id', 64).strip().decode('ascii').replace('-', '')
        require(re.fullmatch('[0-9a-f]{32}', self.boot) is not None)
        self.reader = _reader._Reader(flags=_reader.LOCAL_ONLY | _reader.SYSTEM)
        require(self.reader.fileno() >= 0)
        self.reader.data_threshold = MAX_FIELD
        self.reader.seek_tail()
        require(self.reader._previous())
        _, boot = self.reader._get_monotonic()
        require(boot.hex() == self.boot)
        self.anchor = self.reader._get_cursor()  # No historical entry body.

    def setup_store(self):
        self.watch_fd = LIBC.inotify_init1(os.O_CLOEXEC | os.O_NONBLOCK)
        require(self.watch_fd >= 0)
        self.stores = []
        for path in ('/var/crash', '/var/lib/systemd/coredump'):
            target = Path(path)
            if not target.exists():
                require(not target.is_symlink())
                target = target.parent
            info = root_path(target, directory=True, sticky=target == Path('/var/crash'))
            require(LIBC.inotify_add_watch(self.watch_fd, os.fsencode(target), 0xFCE) >= 0)
            self.stores.append((target, info.st_dev, info.st_ino))

    def close(self):
        failed = False
        if self.reader is not None:
            try:
                self.reader.close()
            except BaseException:
                failed = True
            self.reader = None
        try:
            self.log.close()
        except BaseException:
            failed = True
        fd, self.watch_fd = self.watch_fd, None
        if fd is not None and fd >= 0:
            try:
                os.close(fd)
            except BaseException:
                failed = True
        require(not failed)

    def journal(self, child, canary, end):
        reader = self.reader
        stage = 'initial_change'
        self.journal_diagnostic = {'journal_stage': stage, 'journal_reason': 'api_error'}
        deadline = time.monotonic() + 2

        def check(condition, reason):
            if not condition:
                raise JournalIncomplete(reason)

        def change(final=False):
            state = reader.process()
            check(type(state) is int and state in (0, 1, 2), 'unexpected_representation')
            check(state != 2, 'invalidation')
            check(not final or state == 0, 'append_pending')

        try:
            change()
            stage = 'cursor_restore'
            reader.seek_cursor(self.anchor)
            check(reader._next() and reader.test_cursor(self.anchor), 'anchor_unavailable')
            stage = 'filters'
            groups = journal_groups(self.boot, os.getpid(), child)
            for index, group in enumerate(groups):
                if index:
                    reader.add_disjunction()
                for key, value in group:
                    reader.add_match(key + '=' + value)
            stage = 'seek'
            lower, upper = int(self.start * 1000000), int(end * 1000000)
            check(0 <= self.start <= end and lower <= upper, 'invalid_observation_interval')
            reader.seek_monotonic(lower, self.boot)
            size, collector = 0, False
            last_stamp = None
            for _ in range(256):
                stage = 'budget'
                check(time.monotonic() < deadline, 'time_limit')
                stage = 'iteration'
                if not reader._next():
                    break
                stage = 'timestamp_boot'
                timestamp = reader._get_monotonic()
                check(isinstance(timestamp, tuple) and len(timestamp) == 2, 'unexpected_representation')
                stamp, boot = timestamp
                check(type(stamp) is int and type(boot) is bytes and len(boot) == 16,
                      'unexpected_representation')
                check(boot.hex() == self.boot, 'record_boot_mismatch')
                check(stamp >= 0 and (last_stamp is None or stamp >= last_stamp),
                      'ordering_ambiguous')
                last_stamp = stamp
                if stamp < lower or stamp > upper:
                    # v255 may position before lower. Never read excluded payloads.
                    # Spend the same iteration/time budget and advance ONCE. Do
                    # not infer EOF from an upper-bound crossing across files.
                    continue
                entry = {}
                # Raw v235 _get returns bytes, NOT high-level Reader conversions.
                # Only KeyError means missing; never suppress other API errors.
                for key in JOURNAL_FIELDS:
                    stage = 'budget'
                    check(time.monotonic() < deadline, 'time_limit')
                    stage = 'field_read'
                    try:
                        value = reader._get(key)
                    except KeyError:
                        continue
                    stage = 'field_shape'
                    check(type(value) is bytes, 'unexpected_representation')
                    # A bounded observed positive dominates later incompleteness.
                    # This is conservative detection, not proof of attribution.
                    if contains(canary, value[:MAX_FIELD]):
                        self.journal_diagnostic = {'journal_stage': stage,
                                                   'journal_reason': 'positive_match'}
                        return 'FAIL', True
                    check(len(key) + 1 + len(value) < MAX_FIELD, 'incomplete_field')
                    entry[key] = value
                    size += len(value)
                    stage = 'budget'
                    check(size <= MAX_OBSERVATION, 'byte_limit')
                stage = 'attribution'
                check('_BOOT_ID' in entry, 'incomplete_field')
                check(any(all(entry.get(key) == value.encode('ascii') for key, value in group)
                          for group in groups), 'attribution_mismatch')
                collector |= any(key in entry for key in ('COREDUMP_PID', 'COREDUMP', 'COREDUMP_FILENAME'))
            else:
                stage = 'budget'
                raise JournalIncomplete('record_limit')
            stage = 'final_change'
            change(final=True)
            stage = 'budget'
            check(time.monotonic() < deadline, 'time_limit')
            self.journal_diagnostic = {'journal_stage': 'complete', 'journal_reason': 'complete'}
            return 'PASS', collector
        except BaseException as error:
            reason = error.reason if type(error) is JournalIncomplete else 'api_error'
            self.journal_diagnostic = {'journal_stage': stage, 'journal_reason': reason}
            raise JournalIncomplete(reason) from None

    def apport(self, child, canary):
        return self.log.observe(child, canary)

    def store_events(self):
        for target, device, inode in self.stores:
            info = root_path(target, directory=True, sticky=target == Path('/var/crash'))
            require((info.st_dev, info.st_ino) == (device, inode))
        try:
            events = os.read(self.watch_fd, 65536)
        except BlockingIOError:
            return 'PASS'
        require(events)
        return 'NOT_TESTED'

    def finish(self, child, canary):
        values = dict.fromkeys(('observation_window', 'journal', 'apport_log',
                                'crash_store', 'collector_retention'), 'NOT_TESTED')
        if not self.ready:
            return values
        until = time.monotonic() + OBSERVATION_SECONDS
        while time.monotonic() < until:
            time.sleep(min(0.05, max(0, until - time.monotonic())))
        end = time.monotonic()
        require(end - until < 2 and abs((time.time() - self.wall) - (end - self.start)) < 0.25)
        values['observation_window'] = 'PASS'
        collector = changed = True
        try:
            values['journal'], collector = self.journal(child, canary, end)
        except BaseException:
            pass
        values.update(getattr(self, 'journal_diagnostic',
                              {'journal_stage': 'not_started', 'journal_reason': 'not_started'}))
        try:
            values['apport_log'], changed = self.apport(child, canary)
        except BaseException:
            pass
        try:
            values['crash_store'] = self.store_events()
        except BaseException:
            pass
        if 'FAIL' in values.values():
            values['collector_retention'] = 'FAIL'
        elif not collector and not changed and all(values[key] == 'PASS' for key in
                                                  ('journal', 'apport_log', 'crash_store')):
            # Finite reviewed window/sinks, NOT universal non-retention.
            values['collector_retention'] = 'PASS'
        return values


def reap_owned(pid, pidfd):
    """Bounded cleanup through a pinned process identity, never a recycled PID."""
    if pid is None:
        if pidfd is not None:
            os.close(pidfd)
        return True
    if pidfd is None:
        # Never fall back to numeric kill. PDEATHSIG/parent-death check is backup.
        return False
    try:
        try:
            signal.pidfd_send_signal(pidfd, signal.SIGKILL, None, 0)
        except ProcessLookupError:
            pass
        try:
            wait_child(pid, time.monotonic() + 2)
        except ChildProcessError:
            pass  # Already reaped before an interrupt; pidfd could not hit reuse.
        return True
    except BaseException:
        return False
    finally:
        os.close(pidfd)


def encode_result(values, canary):
    value = json.dumps(report(values), sort_keys=True).encode('ascii') + b'\n'
    require(len(value) <= MAX_RESULT)
    require(canary is None or not contains(canary, value))
    return value


def trial(output_fd, supervisor_pid):
    values = {}
    child = child_fd = canary = observation = None
    try:
        protect(supervisor_pid)
        detach(output_fd)
        group = runtime_limits()
        values.update(runtime_limits='PASS', dumpable_parent='PASS', stdio_detached='PASS')
        observation = Observation()
        values.update(observation.setup)
        runtime_limits(group)  # Library loading cannot silently add workers.
        if not observation.ready or any(values[name] != 'PASS' for name in SETUP_STAGES):
            raise SetupIncomplete()
        # Generation is AFTER protections, inside the worker, never in wrapper/model.
        canary = os.getrandom(32)
        require(len(canary) == 32)
        values['own_argv'] = 'FAIL' if contains(canary, bounded_read('/proc/self/cmdline')) else 'PASS'
        values['own_environment'] = 'FAIL' if contains(canary, bounded_read('/proc/self/environ')) else 'PASS'
        require('FAIL' not in values.values())
        parent = os.getpid()
        child = os.fork()
        if child == 0:
            try:
                protect(parent)
                os.close(output_fd)
                # Do not use the parent's process-origin-bound journal object.
                # Raw close leaves its parent's watches intact; no child exec or
                # Python destructor runs on SIGABRT / the os._exit fallback.
                detach(-1)
                runtime_limits(group)
                require(len(canary) == 32 and prctl(3) == 0)
                signal.signal(signal.SIGABRT, signal.SIG_DFL)
                signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGABRT})
                os.kill(os.getpid(), signal.SIGABRT)
            except BaseException:
                pass  # Never format an exception or write child memory to any FD.
            os._exit(71)
        child_fd = os.pidfd_open(child, 0)
        wait_exit(child, time.monotonic() + 5)
        values.update(observation.finish(child, canary))
        status = wait_child(child, time.monotonic() + 5)
        child = None
        values['child_reaped'] = 'PASS'
        signaled = os.WIFSIGNALED(status) and os.WTERMSIG(status) == signal.SIGABRT
        values['crash_signal'] = 'PASS' if signaled else 'FAIL'
        # SIGABRT is reachable only after child's protection checks in this graph.
        values['dumpable_child'] = 'PASS' if signaled else 'FAIL'
        values['kernel_core_flag'] = 'PASS' if signaled and not os.WCOREDUMP(status) else 'FAIL'
        runtime_limits(group)
        require(prctl(3) == 0 and not faulthandler.is_enabled())
        values['runtime_limits'] = 'PASS'
        if 'FAIL' not in values.values():
            # Reviewed data-flow exclusions, not searches of uninvolved systems.
            for key in ('sudo_logs', 'shell_history', 'application_logs', 'temporary_files',
                        'git_worktree', 'git_index', 'git_history', 'ci_artifacts'):
                values[key] = 'NOT_APPLICABLE'
    except SetupIncomplete:
        pass  # Publish setup stages; no new canary and no deliberate crash.
    except BaseException:
        values['runtime_limits'] = 'FAIL'
    finally:
        values['cleanup'] = 'PASS' if reap_owned(child, child_fd) else 'FAIL'
        if observation is not None:
            try:
                observation.close()
            except BaseException:
                values['cleanup'] = 'FAIL'
    try:
        values['bounded_result'] = 'PASS'
        candidate = encode_result(values, canary)
        # The only write is a bounded fixed-enum result, never raw memory.
        require(os.write(output_fd, candidate) == len(candidate))
    except BaseException:
        pass  # Missing/incomplete output fails supervisor validation.
    os._exit(0)


def run():
    """Called by verified wrapper only after metadata/host/plan checks pass."""
    worker = worker_fd = None
    reader, writer = os.pipe2(os.O_CLOEXEC)
    answer = report({'runtime_limits': 'FAIL'})
    try:
        require(os.geteuid() == 0 and resource.getrlimit(resource.RLIMIT_CORE) == (0, 0))
        runtime_limits()
        supervisor = os.getpid()
        worker = os.fork()
        if worker == 0:
            os.close(reader)
            trial(writer, supervisor)
            os._exit(72)
        worker_fd = os.pidfd_open(worker, 0)
        os.close(writer)
        writer = None
        deadline = time.monotonic() + DEADLINE
        value = bytearray()
        while True:
            require(time.monotonic() < deadline)
            ready, _, _ = select.select([reader], [], [], max(0, deadline - time.monotonic()))
            require(ready)
            block = os.read(reader, MAX_RESULT + 1 - len(value))
            if not block:
                break
            value.extend(block)
            require(len(value) <= MAX_RESULT)
        status = wait_child(worker, deadline)
        worker = None
        require(os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0)
        answer = validate(json.loads(value))
    except BaseException:
        answer = report({'runtime_limits': 'FAIL'})
    finally:
        if not reap_owned(worker, worker_fd):
            answer = report({**answer['results'], 'cleanup': 'FAIL'})
        os.close(reader)
        if writer is not None:
            os.close(writer)
    return answer
