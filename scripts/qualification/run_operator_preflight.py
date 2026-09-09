#!/usr/bin/python3 -I
"""Human-console metadata wrapper. No secret input or bootstrap operations."""
import configparser
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import hmac
import io
import json
import os
import pwd
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
CRASH_HELPER = LIB / 'crash_canary.py'
CRASH_SHA256 = 'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3'
CRASH_RESULT = Path('/var/tmp/ai-invest-crash-journal.json')
JOURNAL_STAGES = frozenset(('not_started', 'initial_change', 'cursor_restore',
    'filters', 'seek', 'iteration', 'timestamp_boot', 'field_read', 'field_shape',
    'attribution', 'final_change', 'budget', 'complete'))
JOURNAL_REASONS = frozenset(('not_started', 'api_error', 'invalidation',
    'anchor_unavailable', 'unexpected_representation', 'incomplete_field',
    'attribution_mismatch', 'time_limit', 'record_limit', 'byte_limit',
    'append_pending', 'positive_match', 'complete'))
CRASH_SETUP_STAGES = ('setup_journal', 'setup_log_directory', 'setup_log_file', 'setup_crash_store')
CRASH_CATEGORIES = frozenset({
    'runtime_limits', 'dumpable_parent', 'dumpable_child', 'crash_signal',
    'kernel_core_flag', 'own_argv', 'own_environment', 'stdio_detached',
    'child_reaped', 'cleanup', 'bounded_result', 'collector_retention', 'journal',
    'sudo_logs', 'shell_history', 'application_logs', 'temporary_files',
    'swap_bytes', 'git_worktree', 'git_index', 'git_history', 'ci_artifacts',
    'human_input_path', 'observation_window', 'apport_log', 'crash_store',
    *CRASH_SETUP_STAGES,
})
HOST_ID = LIB / 'host-id'
ORDINARY_RESULT = Path('/var/tmp/ai-invest-operator-preflight.json')
RESULT = ORDINARY_RESULT
DIAGNOSTIC_RESULT = Path('/var/tmp/ai-invest-operator-diagnostic.json')
HELPER_BASELINE_COMMIT = 'ff75739e4bd420cd17104e34e1eb2b1cdcd54e22'
HELPER_BASELINE_SHA256 = 'a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd'
HELPER_SHA256 = 'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c'
CLEAN_ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
# Host-specific qualification policy, not application identity configuration.
OPERATOR_UID = 1000
SESSION_EXPECTED = {'Active': 'yes', 'Remote': 'no', 'Type': 'tty', 'Class': 'user',
                    'User': str(OPERATOR_UID), 'LockedHint': 'no', 'State': 'active',
                    'Service': 'login'}
PLAN_BOOL = {'local_nonrotational_block_backing', 'capacity_margin_pass',
             'root_owned_nonwritable_ancestors', 'targets_absent', 'mount_parent_same_filesystem'}
PLAN_INT = {'total_bytes', 'available_bytes', 'proposed_volume_bytes', 'remaining_bytes'}
OP_BOOL = {'root_operator', 'direct_virtual_console', 'cpu_limit_bounded', 'core_soft_zero',
           'core_hard_zero', 'mount_namespace_differs_from_visible_pid1',
           'pid_namespace_matches_visible_pid1', 'reviewed_apport_handler', 'reviewed_core_pattern'}
OP_LIMIT = {'memory_max', 'memory_swap_max', 'memory_swap_current', 'pids_max'}
ENVIRONMENT_CHECKS = frozenset({
    'environment_keyset', 'environment_locale', 'environment_term',
    'environment_home', 'environment_user', 'environment_logname', 'environment_mail',
    'environment_shell', 'environment_sudo_gid',
})
DIAGNOSTIC_CHECKS = frozenset({
    'cgroup_membership', 'memory_max', 'memory_swap_max', 'memory_swap_current',
    'pids_max', 'cpu_max', 'rlimit_core', 'tty_identity', 'mount_namespace',
    'pid_namespace', 'apport_handler', 'core_pattern', 'root_operator',
    'operator_evaluation', 'arguments', 'result_file', 'helper_integrity',
    'host_context', 'plan_preflight', 'scope_launch', 'report_validation', 'result_publication',
    'operator_identity', 'operator_environment', 'console_session',
    'crash_harness',
    'environment_path',  # Historical report compatibility; no active PATH predicate.
}) | ENVIRONMENT_CHECKS


class Rejected(Exception):
    """Only fixed diagnostics may be emitted by the caller."""


class EnvironmentRejected(Rejected):
    """Carries one validated symbolic predicate, never environment data."""

    def __init__(self, check):
        if type(check) is not str or check not in ENVIRONMENT_CHECKS:
            raise Rejected()
        super().__init__()
        self.check = check


def environment_require(check, predicate):
    try:
        passed = predicate()
    except Exception:
        raise EnvironmentRejected(check) from None
    if not passed:
        raise EnvironmentRejected(check)


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


def require_operator_identity():
    # SUDO_* is sudo-managed context, not proof against an already privileged root.
    # /proc loginuid and logind below independently bind the local login origin.
    require(os.getuid() == 0 and os.environ.get('SUDO_UID') == str(OPERATOR_UID))
    require(Path('/proc/self/loginuid').read_text().strip() == str(OPERATOR_UID))
    require(os.environ.get('SUDO_USER') == pwd.getpwuid(OPERATOR_UID).pw_name)
    expected = '--crash-test' if sys.argv[1:] == ['--crash-test'] else '--diagnostic'
    require(os.environ.get('SUDO_COMMAND') == str(INSTALLED) + ' ' + expected)


def require_operator_environment():
    allowed = set(CLEAN_ENV) | {'TERM', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'MAIL',
                                'SUDO_UID', 'SUDO_GID', 'SUDO_USER', 'SUDO_COMMAND'}
    environment_require('environment_keyset', lambda: set(os.environ) <= allowed)
    # Inherited PATH is unused incidental state, never an executable selector.
    # Absolute executables and explicit CLEAN_ENV protect child work instead.
    for key in ('LANG', 'LC_ALL', 'TERM'):
        environment_require('environment_term' if key == 'TERM' else 'environment_locale',
                            lambda: re.fullmatch(r'[A-Za-z0-9_.@+-]{0,64}', os.environ.get(key, '')) is not None)
    for key, value in {'HOME': '/root', 'USER': 'root', 'LOGNAME': 'root',
                       'MAIL': '/var/mail/root'}.items():
        environment_require('environment_' + key.lower(),
                            lambda: key not in os.environ or os.environ[key] == value)
    environment_require('environment_shell',
                        lambda: os.environ.get('SHELL', '/bin/bash') in ('/bin/bash', '/usr/bin/bash'))
    environment_require('environment_sudo_gid',
                        lambda: os.environ.get('SUDO_GID') == str(pwd.getpwuid(OPERATOR_UID).pw_gid))


def session_ok(output, tty):
    # Fixed bounded properties only. Never publish loginctl output/session values.
    if len(output) > 2048:
        return False
    expected = {**SESSION_EXPECTED, 'TTY': tty.removeprefix('/dev/')}
    rows = output.splitlines()
    if len(rows) != len(expected) or any('=' not in line for line in rows):
        return False
    values = dict(line.split('=', 1) for line in rows)
    return values == expected


def require_console_session():
    # "self", never "auto": no fallback to another graphical/login session.
    command = ['/usr/bin/loginctl', '--no-pager', '--no-ask-password', 'show-session', 'self']
    command += ['--property=' + key for key in (*SESSION_EXPECTED, 'TTY')]
    result = subprocess.run(command, env=CLEAN_ENV, capture_output=True, text=True,
                            timeout=10, check=False, close_fds=True)
    require(result.returncode == 0 and not result.stderr
            and session_ok(result.stdout, os.ttyname(0)))


def failure(diagnostic=False, check='report_validation'):
    if diagnostic:
        require(type(check) is str and check in DIAGNOSTIC_CHECKS)
        return {'mode': 'diagnostic', 'checks_passed': False, 'failed_checks': [check],
                'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}
    return {'mode': 'operator', 'checks_passed': False, 'error': 'metadata_unavailable',
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}


def validate_report(report):
    require(type(report) is dict)
    base = {'mode', 'checks_passed', 'secret_entry_authorized', 'runtime_crash_suppression_qualified'}
    if report.get('mode') == 'crash-test':
        require(set(report) == base | {'failed_checks', 'results'})
        require(report['checks_passed'] is False and report['secret_entry_authorized'] is False
                and report['runtime_crash_suppression_qualified'] is False)
        results = report['results']
        require(type(results) is dict and set(results) == CRASH_CATEGORIES | {'journal_stage', 'journal_reason'})
        require(all(type(value) is str and value in
                    (JOURNAL_STAGES if key == 'journal_stage' else JOURNAL_REASONS
                     if key == 'journal_reason' else ('PASS', 'FAIL', 'NOT_TESTED', 'NOT_APPLICABLE'))
                    for key, value in results.items()))
        expected = 'crash_trial_failed' if 'FAIL' in results.values() else 'coverage_incomplete'
        setup_failures = [name for name in CRASH_SETUP_STAGES if results[name] == 'FAIL']
        require(report['failed_checks'] == (setup_failures or [expected]))
        return report
    if report.get('mode') == 'diagnostic':
        require(set(report) == base | {'failed_checks'})
        failures = report.get('failed_checks')
        require(type(failures) is list and len(failures) <= 1)
        require(all(type(check) is str and check in DIAGNOSTIC_CHECKS for check in failures))
        require(type(report.get('checks_passed')) is bool and report['checks_passed'] == (not failures))
        require(report.get('secret_entry_authorized') is False
                and report.get('runtime_crash_suppression_qualified') is False)
        return report
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
        if RESULT == CRASH_RESULT:
            print('A new bounded synthetic crash-trial result is ready.')
        elif report['mode'] == 'diagnostic':
            print('A new sanitized diagnostic result is ready.')
        else:
            print('A new sanitized result is ready at /var/tmp/ai-invest-operator-preflight.json.')


def invoke_crash():
    source = checked_bytes(CRASH_HELPER)
    require(hashlib.sha256(source).hexdigest() == CRASH_SHA256)
    require(hmac.compare_digest(source, checked_bytes(
        CHECKOUT / 'scripts/qualification/crash_canary.py', root_owned=False)))
    namespace = {'__name__': 'qualification_crash_helper', '__file__': str(CRASH_HELPER)}
    # Only pinned source is executed; no argument, path or arbitrary code is accepted.
    exec(compile(source, str(CRASH_HELPER), 'exec'), namespace)
    return validate_report(namespace['run']())


def scope_command(identity, diagnostic=False, crash=False):
    require(re.fullmatch(r'[0-9]{1,20}:[0-9]{1,20}', identity) is not None)
    mode = '--scoped-crash-test' if crash else '--scoped-diagnostic' if diagnostic else '--scoped'
    command = ['/usr/bin/systemd-run', '--scope', '--unit=ai-invest-operator-preflight',
            '--expand-environment=no',
            '-p', 'MemoryMax=2G', '-p', 'MemorySwapMax=0', '-p', 'TasksMax=32', '-p', 'CPUQuota=100%',
            '/usr/bin/unshare', '--mount', '--propagation', 'private',
            '/usr/bin/env', '-i', 'PATH=/usr/sbin:/usr/bin:/sbin:/bin', 'LANG=C', 'LC_ALL=C',
            '/usr/bin/python3', '-I', '-B', str(INSTALLED), mode, identity]
    # Both core limits are zero in the root parent, inherited across exec and
    # set again at scoped startup. No shell or variable-looking text is needed.
    return command


def main():
    global RESULT
    fd = None
    scoped = False
    crash = len(sys.argv) > 1 and sys.argv[1] in ('--crash-test', '--scoped-crash-test')
    diagnostic = crash or (len(sys.argv) > 1 and sys.argv[1] in ('--diagnostic', '--scoped-diagnostic'))
    RESULT = CRASH_RESULT if crash else DIAGNOSTIC_RESULT if diagnostic else ORDINARY_RESULT
    stage = 'root_operator'
    report = failure()
    try:
        require(os.geteuid() == 0)
        stage = 'arguments'
        require(sys.argv[1:] in ([], ['--diagnostic'], ['--crash-test']) or
                (len(sys.argv) == 3 and sys.argv[1] in ('--scoped', '--scoped-diagnostic', '--scoped-crash-test')))
        scoped = len(sys.argv) == 3
        stage = 'rlimit_core'
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        os.umask(0o077)
        stage = 'result_file'
        fd = open_scoped_result(sys.argv[2]) if scoped else create_result()
        stage = 'tty_identity'
        require_console()
        stage = 'helper_integrity'
        source = trusted_helper()
        if diagnostic and not scoped:
            stage = 'operator_identity'
            require_operator_identity()
            stage = 'operator_environment'
            require_operator_environment()
            stage = 'console_session'
            require_console_session()
        os.environ.clear()
        os.environ.update(CLEAN_ENV)
        stage = 'host_context'
        require_host(scoped)
        stage = 'plan_preflight'
        if scoped:
            require(invoke_helper(source, 'plan')['checks_passed'])
            stage = 'report_validation'
            report = invoke_helper(source, 'diagnostic' if diagnostic else 'operator')
            if crash and report['checks_passed']:
                stage = 'crash_harness'
                report = invoke_crash()
        else:
            report = invoke_helper(source, 'plan')
            if report['checks_passed']:
                info = os.fstat(fd)
                stage = 'scope_launch'
                save_result(fd, failure(diagnostic, stage))
                completed = subprocess.run(scope_command(f'{info.st_dev}:{info.st_ino}', diagnostic, crash),
                                           env=CLEAN_ENV, check=False, close_fds=True)
                stage = 'report_validation'
                os.lseek(fd, 0, os.SEEK_SET)
                report = validate_report(json.loads(os.read(fd, 8193)))
                expected_modes = ('diagnostic', 'crash-test') if crash else ('diagnostic',) if diagnostic else ('operator',)
                require(report['mode'] in expected_modes
                        and completed.returncode == (0 if report['checks_passed'] else 1))
            elif diagnostic:
                report = failure(True, 'plan_preflight')
        stage = 'result_publication'
        save_result(fd, report, publish=not scoped)
        return 0 if report['checks_passed'] else 1
    except Exception as error:
        if diagnostic and stage == 'operator_environment' and isinstance(error, EnvironmentRejected):
            # Only a fixed predicate can refine this one boundary. No exception text.
            if type(error.check) is str and error.check in ENVIRONMENT_CHECKS:
                stage = error.check
        saved = False
        if fd is not None:
            try:
                save_result(fd, failure(diagnostic, stage), publish=not scoped)
                saved = True
            except Exception:
                pass  # An incomplete/private file is not a published result.
        if diagnostic and not saved:
            try:
                print(json.dumps(failure(True, stage), sort_keys=True))
            except OSError:
                pass
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
