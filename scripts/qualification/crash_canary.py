#!/usr/bin/python3 -I
"""Fixed synthetic crash trial, invoked only by the reviewed operator wrapper.

No standalone CLI, secret input, external command, file writer, or bootstrap.
Unobserved channels remain NOT_TESTED; this cannot authorize real secret entry.
"""
import ctypes
import faulthandler
import json
import os
from pathlib import Path
import resource
import select
import signal
import stat
import time

MAX_RESULT = 4096
DEADLINE = 20
CATEGORIES = (
    'runtime_limits', 'dumpable_parent', 'dumpable_child', 'crash_signal',
    'kernel_core_flag', 'own_argv', 'own_environment', 'stdio_detached',
    'child_reaped', 'cleanup', 'bounded_result', 'collector_retention', 'journal',
    'sudo_logs', 'shell_history', 'application_logs', 'temporary_files',
    'swap_bytes', 'git_worktree', 'git_index', 'git_history', 'ci_artifacts',
    'human_input_path',
)
STATES = frozenset(('PASS', 'FAIL', 'NOT_TESTED', 'NOT_APPLICABLE'))
# PR_SET_PDEATHSIG, PR_GET_DUMPABLE, PR_SET_DUMPABLE from linux/prctl.h.
LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.prctl.restype = ctypes.c_int


class Refused(Exception):
    pass


def require(value):
    if not value:
        raise Refused()


def report(results=None):
    values = dict.fromkeys(CATEGORIES, 'NOT_TESTED')
    if results:
        require(type(results) is dict and set(results) <= set(CATEGORIES))
        require(all(type(value) is str and value in STATES for value in results.values()))
        values.update(results)
    # Missing collector/input/leakage evidence deliberately prevents overall PASS.
    return {'mode': 'crash-test', 'checks_passed': False,
            'failed_checks': ['crash_trial_failed' if 'FAIL' in values.values() else 'coverage_incomplete'],
            'results': values, 'secret_entry_authorized': False,
            'runtime_crash_suppression_qualified': False}


def validate(value):
    require(type(value) is dict and set(value) == set(report()))
    require(value['checks_passed'] is False and value['secret_entry_authorized'] is False
            and value['runtime_crash_suppression_qualified'] is False)
    require(value == report(value.get('results')))
    require(type(value['results']) is dict and set(value['results']) == set(CATEGORIES))
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
    child = child_fd = canary = None
    try:
        protect(supervisor_pid)
        detach(output_fd)
        group = runtime_limits()
        values.update(runtime_limits='PASS', dumpable_parent='PASS', stdio_detached='PASS')
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
                runtime_limits(group)
                require(len(canary) == 32 and prctl(3) == 0)
                signal.signal(signal.SIGABRT, signal.SIG_DFL)
                signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGABRT})
                os.kill(os.getpid(), signal.SIGABRT)
            except BaseException:
                pass  # Never format an exception or write child memory to any FD.
            os._exit(71)
        child_fd = os.pidfd_open(child, 0)
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
    except BaseException:
        values['runtime_limits'] = 'FAIL'
    finally:
        values['cleanup'] = 'PASS' if reap_owned(child, child_fd) else 'FAIL'
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
