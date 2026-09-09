"""Synthetic trust-boundary regressions; never install policy or use sudo."""
from contextlib import redirect_stdout
import io
import hashlib
import os
import re
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_operator_wrapper as base

W, ROOT = base.WRAPPER, base.ROOT


POLICY = ROOT / 'infrastructure/qualification/ai-invest-operator.sudoers'


class BoundaryTests(unittest.TestCase):
    def session(self, **changes):
        return '\n'.join(k + '=' + v for k, v in
                         {**W.SESSION_EXPECTED, 'TTY': 'tty3', **changes}.items()) + '\n'

    def test_tty3_acceptance_and_sudo_pty_rejection(self):
        devices = [(stat.S_IFCHR | 0o600, 4, 3)] * 3
        self.assertTrue(W.console_ok(['/dev/tty3'] * 3, devices, {}))
        self.assertFalse(W.console_ok(['/dev/pts/3'] * 3, devices, {}))

    def test_ssh_gui_tmux_screen_markers(self):
        for name in ('SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY', 'DISPLAY',
                     'WAYLAND_DISPLAY', 'TMUX', 'STY'):
            with self.subTest(name=name):
                self.assertFalse(W.console_ok(['/dev/tty3'] * 3,
                    [(stat.S_IFCHR, 4, 3)] * 3, {name: 'synthetic'}))

    def test_valid_current_session(self):
        self.assertTrue(W.session_ok(self.session(), '/dev/tty3'))

    def test_ssh_gui_wrong_user_other_vt_stale_locked_sessions(self):
        for changes in ({'Remote': 'yes'}, {'Type': 'x11'}, {'Type': 'wayland'},
                        {'User': '1001'}, {'TTY': 'pts/3'}, {'TTY': 'tty4'},
                        {'Active': 'no'}, {'State': 'closing'}, {'State': 'online'},
                        {'LockedHint': 'yes'}, {'Service': 'sshd'}, {'Class': 'manager'}):
            with self.subTest(changes=changes):
                self.assertFalse(W.session_ok(self.session(**changes), '/dev/tty3'))

    def test_session_unknown_duplicate_missing_oversized_data_rejected(self):
        for output in (self.session() + 'Untrusted=value\n', self.session() + 'Active=yes\n',
                       self.session().replace('State=active\n', ''), 'x' * 2049,
                       self.session().replace('State=active', 'malformed')):
            self.assertFalse(W.session_ok(output, '/dev/tty3'))

    def identity_environment(self):
        return {**W.CLEAN_ENV, 'SUDO_UID': '1000', 'SUDO_GID': '1000',
                'SUDO_USER': 'synthetic-owner', 'SUDO_COMMAND': str(W.INSTALLED) + ' --diagnostic'}

    def identity(self, changes=None, loginuid='1000', uid=0):
        with patch.dict(W.os.environ, {**self.identity_environment(), **(changes or {})}, clear=True), \
             patch.object(W.os, 'getuid', return_value=uid), \
             patch.object(W.Path, 'read_text', return_value=loginuid), \
             patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_name='synthetic-owner')):
            W.require_operator_identity()

    def test_sudo_operator_identity_positive(self):
        self.identity()

    def test_wrong_uid_loginuid_root_login_or_wrong_command_rejected(self):
        for change in ({'SUDO_UID': '1001'}, {'SUDO_UID': '0'}, {'SUDO_USER': 'other'},
                       {'SUDO_COMMAND': '/bin/sh'}, {'SUDO_COMMAND': str(W.INSTALLED)},
                       {'SUDO_COMMAND': str(W.INSTALLED) + ' --scoped-diagnostic 1:2'}):
            with self.subTest(change=change), self.assertRaises(W.Rejected):
                self.identity(change)
        for origin in ('0', '1001', '4294967295', ''):
            with self.subTest(origin=origin), self.assertRaises(W.Rejected):
                self.identity(loginuid=origin)
        with self.assertRaises(W.Rejected):
            self.identity(uid=1000)

    def environment(self, changes=None):
        with patch.dict(W.os.environ, {**self.identity_environment(), **(changes or {})}, clear=True), \
             patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_gid=1000)):
            W.require_operator_environment()

    def test_clean_sudo_environment_accepted(self):
        self.environment()

    def test_preserved_environment_path_shell_injection_denied(self):
        for changes in ({'PATH': '/tmp'}, {'PYTHONPATH': '/tmp'}, {'BASH_ENV': '/tmp'},
                        {'LD_PRELOAD': 'synthetic'}, {'SUDO_ASKPASS': 'synthetic'},
                        {'SHELL': '/tmp/sh'}, {'HOME': '/tmp'}, {'SUDO_GID': '1001'},
                        {'LANG': '$(false)'}, {'TERM': '`false`'}, {'TERM': 'x\ny'},
                        {'SSH_CONNECTION': 'synthetic'}, {'TMUX': 'synthetic'},
                        {'STY': 'synthetic'}, {'DISPLAY': 'synthetic'}):
            with self.subTest(changes=changes), self.assertRaises(W.Rejected):
                self.environment(changes)

    def test_logind_query_is_fixed_private_and_no_fallback(self):
        with patch.object(W.subprocess, 'run', return_value=SimpleNamespace(
                returncode=0, stdout=self.session(), stderr='')) as run, \
             patch.object(W.os, 'ttyname', return_value='/dev/tty3'):
            W.require_console_session()
        command = run.call_args.args[0]
        self.assertEqual(command[:5], ['/usr/bin/loginctl', '--no-pager', '--no-ask-password',
                                      'show-session', 'self'])
        self.assertNotIn('auto', command)
        self.assertEqual(run.call_args.kwargs['env'], W.CLEAN_ENV)
        self.assertTrue(run.call_args.kwargs['close_fds'])
        self.assertEqual(run.call_args.kwargs['timeout'], 10)

    def test_missing_logind_or_unexpected_stderr_denied(self):
        for code, error in ((1, ''), (0, 'SYNTHETIC_NOT_FOR_PUBLICATION')):
            with patch.object(W.subprocess, 'run', return_value=SimpleNamespace(
                    returncode=code, stdout=self.session(), stderr=error)), \
                 patch.object(W.os, 'ttyname', return_value='/dev/tty3'), self.assertRaises(W.Rejected):
                W.require_console_session()

    def test_new_boundary_failures_only_symbolic_and_never_authorize(self):
        for guard, symbol in (('require_operator_identity', 'operator_identity'),
                              ('require_operator_environment', 'operator_environment'),
                              ('require_console_session', 'console_session')):
            code, helper, run, reports, output, _ = base.FlowTests().exercise(
                args=('--diagnostic',), guard_failure=guard)
            self.assertEqual(code, 1)
            helper.assert_not_called()
            run.assert_not_called()
            self.assertEqual(reports[-1], W.failure(True, symbol))
            self.assertNotIn('SYNTHETIC_PRIVATE_DETAIL', output)

    def test_arbitrary_arguments_shell_escape_and_substitution_rejected(self):
        for args in (('--diagnostic', '/bin/sh'), ('--diagnostic;false',), ('$(false)',),
                     ('--diagnostic', '--output=/tmp/x'), ('--bootstrap',), ('--init',),
                     ('--diagnostic', '--secret=synthetic'), ('--scoped', '1:2', '/bin/sh')):
            with redirect_stdout(io.StringIO()):
                code, helper, run, _, _, _ = base.FlowTests().exercise(args=args)
            self.assertNotEqual(code, 0)
            helper.assert_not_called()
            run.assert_not_called()

    def test_helper_hardlink_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-boundary-') as folder:
            source = Path(folder) / 'source'
            source.touch(mode=0o600)
            os.link(source, Path(folder) / 'alias')
            with patch.object(W, 'checked_path', return_value=source.stat()), self.assertRaises(W.Rejected):
                W.checked_bytes(source)

    def test_alternate_script_path_rejected(self):
        for path in ('/tmp/operator', '/proc/self/fd/3', str(W.INSTALLED) + '-alias'):
            with patch.object(W, '__file__', path), self.assertRaises(W.Rejected):
                W.trusted_helper()


class PolicyTests(unittest.TestCase):
    def test_policy_activation_rollback_retains_root_transaction_reg_cb_01(self):
        document = (ROOT / 'docs/qualification/OPERATOR_CHECKPOINT.md').read_text()
        matches = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", document, re.S)
        self.assertEqual(len(matches), 1)
        transaction = matches[0]
        self.assertIsNone(re.search(r'\bsudo\b', transaction))
        self.assertEqual(transaction.count('/usr/bin/unlink -- /etc/sudoers.d/ai-invest-operator-qualification'), 1)
        self.assertIn('test ! -e /etc/sudoers.d/ai-invest-operator-qualification', transaction)
        self.assertIn('test ! -L /etc/sudoers.d/ai-invest-operator-qualification', transaction)
        # Exercise exactly the documented control flow with inert command doubles.
        # No install, unlink, sudo, root operation or host-policy change is executed.
        script = transaction.replace('/usr/bin/install', 'fake_install').replace(
            '/usr/sbin/visudo', 'fake_visudo').replace('/usr/bin/unlink', 'fake_unlink').replace('/usr/bin/mv', 'fake_mv')
        script = re.sub(r'test ! -(?:e|L) /etc/sudoers.d/\.?ai-invest-operator-qualification(?:\.pending)?', 'true', script)
        script = script.replace('test -e /etc/sudoers.d/.ai-invest-operator-qualification.pending', 'true')
        functions = '''
fake_install() { printf "install\\n"; test "$fail_stage" != install; }
fake_mv() { printf "activate\\n"; test "$fail_stage" != rename; }
fake_unlink() {
  case "$*" in
    "-- /etc/sudoers.d/.ai-invest-operator-qualification.pending") printf "unlink-pending\\n";;
    "-- /etc/sudoers.d/ai-invest-operator-qualification") printf "unlink-policy\\n";;
    *) exit 99;;
  esac
}
fake_visudo() {
  if test "$#" = 4; then
    printf "candidate\\n"; test "$fail_stage" != candidate
  else
    printf "validate\\n"; count=$((count+1))
    test "$fail_stage" != aggregate || test "$count" -gt 1
  fi
}
count=0
'''
        for fail_stage, status, output in (
                ('none', 0, 'install\ncandidate\nactivate\nvalidate\n'),
                ('install', 1, 'install\nunlink-pending\n'),
                ('candidate', 1, 'install\ncandidate\nunlink-pending\n'),
                ('rename', 1, 'install\ncandidate\nactivate\nunlink-pending\n'),
                ('aggregate', 1, 'install\ncandidate\nactivate\nvalidate\nunlink-policy\nvalidate\n')):
            result = subprocess.run(['/bin/sh', '-c', 'fail_stage=' + fail_stage + '\n' + functions + script],
                                    env=W.CLEAN_ENV, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, status)
            self.assertEqual(result.stdout, output)
            self.assertEqual(result.stderr, '')

    def test_actual_installed_visudo_strict_syntax(self):
        result = subprocess.run(['/usr/sbin/visudo', '-c', '-s', '-f', str(POLICY)],
                                capture_output=True, env=W.CLEAN_ENV, timeout=10)
        self.assertEqual(result.returncode, 0, 'Reviewed policy failed installed visudo parser')

    def test_digest_exact_arguments_and_single_command_scope(self):
        text = POLICY.read_text()
        digest = hashlib.sha256((ROOT / 'scripts/qualification/run_operator_preflight.py').read_bytes()).hexdigest()
        lines = [line for line in text.splitlines() if line and (not line.startswith('#') or line.startswith('#1000 '))]
        self.assertEqual(lines[0], 'Cmnd_Alias AI_INVEST_DIAGNOSTIC = sha256:' + digest +
                         ' /usr/local/sbin/ai-invest-operator-preflight --diagnostic')
        self.assertEqual(lines[-1], '#1000 ALL=(root:root) PASSWD: NOSETENV: AI_INVEST_DIAGNOSTIC')
        self.assertTrue(all(line.startswith('Defaults!AI_INVEST_DIAGNOSTIC ') for line in lines[1:-1]))
        self.assertNotIn('*', '\n'.join(lines))
        self.assertNotIn('NOPASSWD', text)

    def test_fresh_auth_no_replayable_artifact_and_no_unrelated_defaults(self):
        text = POLICY.read_text()
        for control in ('authenticate', 'timestamp_timeout=0', '!exempt_group', 'PASSWD:',
                        'NOSETENV:', '!use_pty', 'fdexec=never', 'closefrom=3', '!closefrom_override',
                        'env_reset', '!env_keep', '!env_check', '!setenv', '!log_input', '!log_output',
                        '!log_stdin', '!log_stdout', '!log_stderr', '!log_ttyin', '!log_ttyout'):
            self.assertIn(control, text)
        # No artifact TTL/reboot simulation can certify PAM freshness. Runtime checks are separate.
        self.assertFalse(any(line.startswith(('Defaults ', 'Defaults:')) for line in text.splitlines()))


if __name__ == '__main__':
    unittest.main()
