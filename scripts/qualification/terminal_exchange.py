"""UNWIRED synthetic terminal candidate: no CLI, launcher, or sudo grant.

Only a future reviewed protected worker may call exercise(). Do not run it from
an operator shell. The current wrapper does not import this module. Controls
must be the existing pinned crash helper, never caller-supplied configuration.
"""
from contextlib import contextmanager
import fcntl
import hmac
import json
import os
import select
import signal
import stat
import termios
import time

SECONDS = 90
MAX_INPUT = 48
MAX_RESULT = 2048
CLEAN_ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
CATCH_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP,
                 signal.SIGQUIT, signal.SIGTSTP, signal.SIGALRM)
REASONS = frozenset(('coverage_incomplete', 'protected_context', 'terminal_identity',
    'terminal_prepare', 'terminal_restore', 'input_timeout', 'input_eof',
    'input_cancelled', 'input_invalid', 'input_mismatch', 'interrupted',
    'output_failed', 'containment', 'internal_error'))
CATEGORIES = ('protection_before', 'echo_disabled', 'recovery_display',
    'input_roundtrip', 'own_argv', 'own_environment', 'protection_after',
    'terminal_restored', 'bounded_result')


class Refused(Exception):
    def __init__(self, reason):
        # Never retain arbitrary exception data or supplied input.
        self.reason = reason if type(reason) is str and reason in REASONS else 'internal_error'
        super().__init__()


def require(value, reason):
    if not value:
        raise Refused(reason)


def result(values=None, reason='coverage_incomplete'):
    require(type(reason) is str and reason in REASONS, 'internal_error')
    states = dict.fromkeys(CATEGORIES, 'NOT_TESTED')
    if values is not None:
        require(type(values) is dict and set(values) <= set(states), 'internal_error')
        require(all(type(v) is str and v in ('PASS', 'FAIL', 'NOT_TESTED')
                    for v in values.values()), 'internal_error')
        states.update(values)
    return {'mode': 'synthetic-io-candidate', 'checks_passed': False,
            'failed_checks': [reason], 'results': states,
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}


def encode(value, materials):
    require(type(value) is dict and set(value) == set(result()), 'internal_error')
    require(all(value[name] is False for name in ('checks_passed',
            'secret_entry_authorized', 'runtime_crash_suppression_qualified')), 'internal_error')
    failed = value['failed_checks']
    require(type(failed) is list and len(failed) == 1, 'internal_error')
    require(type(value['results']) is dict and set(value['results']) == set(CATEGORIES), 'internal_error')
    require(value == result(value['results'], failed[0]), 'internal_error')
    data = json.dumps(value, sort_keys=True).encode('ascii') + b'\n'
    require(len(data) <= MAX_RESULT, 'containment')
    require(all(not item or (item not in data and item.hex().encode('ascii') not in data)
                for item in materials), 'containment')
    return data


def interrupted(signum, frame):
    raise Refused('interrupted')


@contextmanager
def interruptions():
    old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, CATCH_SIGNALS)
    previous = {}
    try:
        for number in CATCH_SIGNALS:
            previous[number] = signal.signal(number, interrupted)
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_BLOCK, CATCH_SIGNALS)
        for number, handler in previous.items():
            signal.signal(number, handler)
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


def no_echo(attributes):
    mask = termios.ECHO | termios.ECHONL | termios.ICANON | termios.ISIG | termios.IEXTEN
    for name in ('ECHOCTL', 'ECHOPRT', 'ECHOKE', 'ECHOE', 'ECHOK'):
        mask |= getattr(termios, name, 0)
    return not attributes[3] & mask


@contextmanager
def quiet_terminal(fd, state):
    original = None
    original_flags = None
    try:
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, CATCH_SIGNALS)
        try:
            original = termios.tcgetattr(fd)
            original_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, original_flags | os.O_NONBLOCK)
            require(fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_NONBLOCK, 'terminal_prepare')
            changed = [*original[:6], list(original[6])]
            for name in ('ECHO', 'ECHONL', 'ECHOCTL', 'ECHOPRT', 'ECHOKE',
                         'ECHOE', 'ECHOK', 'ICANON', 'ISIG', 'IEXTEN'):
                changed[3] &= ~getattr(termios, name, 0)
            for name in ('IGNBRK', 'BRKINT', 'PARMRK', 'ISTRIP', 'INLCR',
                         'IGNCR', 'ICRNL', 'IXON', 'IXOFF'):
                changed[0] &= ~getattr(termios, name, 0)
            changed[6][termios.VMIN] = 0
            changed[6][termios.VTIME] = 0
            termios.tcflush(fd, termios.TCIFLUSH)
            termios.tcsetattr(fd, termios.TCSANOW, changed)
            require(no_echo(termios.tcgetattr(fd)), 'terminal_prepare')
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)
        yield
    finally:
        if original is not None:
            mask = signal.pthread_sigmask(signal.SIG_BLOCK, CATCH_SIGNALS)
            try:
                # Do not leave partially typed input for a subsequent shell read.
                # No guarantee covers late input after restore or SIGKILL.
                failures = False
                try:
                    termios.tcflush(fd, termios.TCIFLUSH)
                except BaseException:
                    failures = True
                try:
                    termios.tcsetattr(fd, termios.TCSANOW, original)
                    require(termios.tcgetattr(fd) == original, 'terminal_restore')
                except BaseException:
                    failures = True
                if original_flags is not None:
                    try:
                        fcntl.fcntl(fd, fcntl.F_SETFL, original_flags)
                        require(fcntl.fcntl(fd, fcntl.F_GETFL) == original_flags, 'terminal_restore')
                    except BaseException:
                        failures = True
                require(not failures, 'terminal_restore')
                state['restored'] = True
            except BaseException:
                raise Refused('terminal_restore') from None
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, mask)


def wait_ready(fd, deadline, writing=False):
    left = deadline - time.monotonic()
    require(left > 0, 'output_failed' if writing else 'input_timeout')
    ready = select.select([] if writing else [fd], [fd] if writing else [], [], left)
    require(bool(ready[1 if writing else 0]), 'output_failed' if writing else 'input_timeout')


def display(fd, data, deadline):
    require(type(data) is bytes and len(data) <= 512, 'output_failed')
    offset = 0
    while offset < len(data):
        wait_ready(fd, deadline, writing=True)
        try:
            count = os.write(fd, data[offset:])
        except BlockingIOError:
            continue
        require(0 < count <= len(data) - offset, 'output_failed')
        offset += count


def read_disposable(fd, deadline):
    value = bytearray()
    while True:
        wait_ready(fd, deadline)
        try:
            part = os.read(fd, 1)
        except BlockingIOError:
            continue
        require(part not in (b'', b'\x04'), 'input_eof')
        require(part not in (b'\x03', b'\x1a'), 'input_cancelled')
        if part in (b'\r', b'\n'):
            require(bool(value), 'input_invalid')
            return bytes(value)
        if part in (b'\x08', b'\x7f'):
            if value:
                value.pop()
            continue
        require(part.isascii() and (part.isalnum() or part == b'-'), 'input_invalid')
        require(len(value) < MAX_INPUT, 'input_invalid')
        value.extend(part)


def require_vt(fd):
    info = os.fstat(fd)
    require(os.geteuid() == 0 and stat.S_ISCHR(info.st_mode)
            and os.major(info.st_rdev) == 4 and 1 <= os.minor(info.st_rdev) <= 63,
            'terminal_identity')
    require(os.isatty(fd) and os.tcgetpgrp(fd) == os.getpgrp(), 'terminal_identity')
    # The established wrapper must also bind this descriptor to its verified VT.
    require(dict(os.environ) == CLEAN_ENV, 'protected_context')


def exercise(fd, controls):
    """Candidate only; returns bounded bytes, never entered/displayed material.

    Integration still needs reviewed fd closure, a fixed supervisor/deadline,
    installed digest checks, console provenance and exclusive result publication.
    No process/exec/credential transition is allowed after protection below.
    """
    values = {}
    terminal_state = {}
    material = entered = None
    reason = 'protected_context'
    try:
        controls.protect(os.getppid())
        group = controls.runtime_limits()
        require_vt(fd)
        values['protection_before'] = 'PASS'
        with interruptions():
            try:
                with quiet_terminal(fd, terminal_state):
                    values['echo_disabled'] = 'PASS'
                    controls.runtime_limits(group)
                    require(controls.prctl(3) == 0, 'protected_context')
                    deadline = time.monotonic() + SECONDS
                    # Random disposable challenge, never an encryption key/share.
                    random = os.getrandom(16)
                    require(len(random) == 16, 'protected_context')
                    material = b'SYNTHETIC-' + random.hex().encode('ascii')
                    display(fd, b'\nSYNTHETIC I/O TEST ONLY. NEVER ENTER A REAL SECRET.\n'
                            b'Disposable recovery-display fixture: ' + material +
                            b'\nRetype ONLY that fixture; echo is OFF. Ctrl-C cancels.\n', deadline)
                    values['recovery_display'] = 'PASS'  # write completion, not human custody
                    entered = read_disposable(fd, deadline)
                    require(hmac.compare_digest(entered, material), 'input_mismatch')
                    values['input_roundtrip'] = 'PASS'
                    for name, path in (('own_argv', '/proc/self/cmdline'),
                                       ('own_environment', '/proc/self/environ')):
                        data = controls.bounded_read(path)
                        values[name] = 'FAIL' if any(controls.contains(v, data)
                            for v in (material, entered)) else 'PASS'
                    require('FAIL' not in values.values(), 'containment')
                    controls.runtime_limits(group)
                    require(controls.prctl(3) == 0, 'protected_context')
                    values['protection_after'] = 'PASS'
                    reason = 'coverage_incomplete'
            finally:
                if terminal_state.get('restored') is True:
                    values['terminal_restored'] = 'PASS'
    except Refused as error:
        reason = error.reason
    except BaseException:
        reason = 'internal_error'
    # Failure paths receive the same fixed schema and containment check.
    values['bounded_result'] = 'PASS'
    return encode(result(values, reason), (material, entered))
