"""PATH is discarded, never an executable selector; synthetic fixtures only."""
import ast
import inspect
import re
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_operator_wrapper as base
import test_environment_diagnostics as environment_tests

W, ROOT = base.WRAPPER, base.ROOT
PATHS = (None, '', '.', '.:/tmp:/writable', 'relative/bin', '/nonexistent',
         '/usr/games:/snap/bin', '$(false):\x60false\x60', '/tmp\n/synthetic')


class PathIndependenceTests(unittest.TestCase):
    def test_arbitrary_and_absent_path_are_never_execution_selectors(self):
        original = W.require_operator_environment
        success = {'mode': 'diagnostic', 'checks_passed': True, 'failed_checks': [],
                   'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}
        commands = []
        for value in PATHS:
            def environment():
                W.os.environ.update({'SUDO_GID': '1000'})
                if value is not None:
                    W.os.environ['PATH'] = value
                with patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_gid=1000)):
                    original()
            code, _, run, reports, _, _ = base.FlowTests().exercise(
                args=('--diagnostic',), candidate=success,
                guard_failure='require_operator_environment', guard_effect=environment)
            self.assertEqual(code, 0)
            self.assertEqual(reports[-1], success)
            commands.append(run.call_args.args[0])
            self.assertEqual(run.call_args.kwargs['env'], W.CLEAN_ENV)
            self.assertFalse(run.call_args.kwargs.get('shell', False))
        self.assertTrue(all(command == W.scope_command('1:2', True) for command in commands))

    def test_precleanup_login_query_uses_absolute_executable_and_clean_env(self):
        reply = '\n'.join(key + '=' + value for key, value in
                          {**W.SESSION_EXPECTED, 'TTY': 'tty3'}.items())
        for value in PATHS:
            environment = {} if value is None else {'PATH': value}
            with patch.dict(W.os.environ, environment, clear=True), \
                 patch.object(W.os, 'ttyname', return_value='/dev/tty3'), \
                 patch.object(W.subprocess, 'run', return_value=SimpleNamespace(
                     returncode=0, stdout=reply, stderr='')) as run:
                W.require_console_session()
                self.assertEqual(run.call_args.args[0][0], '/usr/bin/loginctl')
                self.assertEqual(run.call_args.kwargs['env'], W.CLEAN_ENV)
                self.assertTrue(run.call_args.kwargs['close_fds'])
                self.assertFalse(run.call_args.kwargs.get('shell', False))

    def test_complete_subprocess_surface_has_no_hidden_lookup_or_shell(self):
        tree = ast.parse(inspect.getsource(W))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)
                 and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess']
        self.assertEqual([node.func.attr for node in calls], ['run', 'run', 'run'])
        selectors = set()
        for call in calls:
            self.assertNotIn('shell', {kw.arg for kw in call.keywords})
            self.assertEqual(next(kw.value.id for kw in call.keywords if kw.arg == 'env'), 'CLEAN_ENV')
            arg = call.args[0]
            if isinstance(arg, ast.List):
                selectors.add(arg.elts[0].value)
            elif isinstance(arg, ast.Name):
                self.assertEqual(arg.id, 'command')
            else:
                self.assertIsInstance(arg, ast.Call)
                self.assertEqual(arg.func.id, 'scope_command')
        self.assertEqual(selectors, {'/usr/bin/systemd-detect-virt'})
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                             and node.func.attr in ('system', 'popen', 'execvp', 'execvpe', 'spawnvp')
                             for node in ast.walk(tree)))
        self.assertEqual(W.scope_command('1:2')[0], '/usr/bin/systemd-run')

    def test_helper_programs_and_both_shebangs_are_absolute(self):
        helper = (ROOT / 'scripts/qualification/operator_preflight.py').read_text()
        wrapper = (ROOT / 'scripts/qualification/run_operator_preflight.py').read_text()
        for source in (helper, wrapper):
            self.assertEqual(source.splitlines()[0], '#!/usr/bin/python3 -I')
        calls = [node for node in ast.walk(ast.parse(helper)) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == 'command']
        self.assertEqual({call.args[0].value for call in calls}, {'/usr/bin/findmnt', '/usr/bin/lsblk'})

    def test_isolated_interpreter_ignores_path_and_python_injection(self):
        # No privileged execution or real LD_PRELOAD is attempted.
        for value in PATHS:
            environment = {'PYTHONHOME': '/synthetic-missing', 'PYTHONPATH': '.',
                           'PYTHONSTARTUP': '/synthetic-missing', 'LANG': 'C'}
            if value is not None:
                environment['PATH'] = value
            result = subprocess.run(['/usr/bin/python3', '-I', '-B', '-c',
                'import sys,json,pathlib; print("PASS" if sys.flags.isolated and '
                'sys.flags.ignore_environment and sys.flags.no_user_site and '
                '"" not in sys.path and "." not in sys.path else "FAIL")'],
                env=environment, capture_output=True, text=True, timeout=10)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'PASS\n', ''))

    def test_dangerous_keys_still_rejected_even_without_path(self):
        for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME',
                    'PYTHONSTARTUP', 'BASH_ENV', 'ENV', 'SHELLOPTS', 'UNKNOWN_SYNTHETIC'):
            with self.assertRaises(W.EnvironmentRejected) as caught:
                environment_tests.EnvironmentTests().exercise({'SUDO_GID': '1000', key: '/synthetic'})
            self.assertEqual(caught.exception.check, 'environment_keyset')
            self.assertEqual(str(caught.exception), '')

    def test_retired_identifier_is_historical_only_and_never_authorizes(self):
        self.assertNotIn('environment_path', W.ENVIRONMENT_CHECKS)
        with self.assertRaises(W.Rejected):
            W.EnvironmentRejected('environment_path')
        report = W.validate_report(W.failure(True, 'environment_path'))
        self.assertFalse(report['secret_entry_authorized'])
        self.assertFalse(report['runtime_crash_suppression_qualified'])

    def test_clean_transition_and_no_shell_before_cleanup(self):
        source = inspect.getsource(W.main)
        ordered = ['require_operator_identity()', 'require_operator_environment()',
                   'require_console_session()', 'os.environ.clear()', 'os.environ.update(CLEAN_ENV)',
                   'require_host(scoped)', "invoke_helper(source, 'plan')"]
        positions = [source.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(W.CLEAN_ENV, {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C', 'LC_ALL': 'C'})
        scope = W.scope_command('1:2')
        for executable in ('/usr/bin/unshare', '/usr/bin/env', '/usr/bin/python3'):
            self.assertIn(executable, scope)
        self.assertNotIn('/bin/bash', scope)
        self.assertIn('--expand-environment=no', scope)


class UpgradeTests(unittest.TestCase):
    def transaction(self):
        document = (ROOT / 'docs/qualification/PATH_INDEPENDENCE.md').read_text()
        matches = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", document, re.S)
        self.assertEqual(len(matches), 1)
        self.assertIsNone(re.search(r'\bsudo\b', matches[0]))
        return matches[0]

    def simulate(self, failure, recovery_failure=0):
        script = self.transaction().replace('/usr/bin/install', 'fake_command').replace(
            '/usr/bin/mv', 'fake_command').replace('/usr/sbin/visudo', 'fake_command')
        functions = ('count=0\nfail_at=' + str(failure) + '\nrecovery_failure=' + str(recovery_failure) + r'''
fake_command() { count=$((count+1)); printf "step:%s:%s\n" "$count" "$*"; test "$count" -ne "$fail_at" && test "$count" -ne "$recovery_failure"; }
''')
        return subprocess.run(['/bin/sh', '-c', functions + script], env=W.CLEAN_ENV,
                              capture_output=True, text=True, timeout=10)

    def test_all_eight_activation_steps_and_rollback(self):
        for failure in range(9):
            result = self.simulate(failure)
            self.assertEqual(result.returncode, int(bool(failure)))
            if failure:
                self.assertEqual(result.stderr,
                                 'Upgrade refused; prior reviewed snapshots restored. No secret entry.\n')
                recovery = result.stdout.splitlines()[failure:]
                self.assertIn('path-policy.previous', recovery[0])
                self.assertTrue(any('path-helper.previous' in line for line in recovery))
                self.assertTrue(any('path-wrapper.previous' in line for line in recovery))
            else:
                self.assertEqual(len(result.stdout.splitlines()), 8)
                self.assertEqual(result.stderr, '')

    def test_rollback_legs_independent_and_partial_failure_never_claims_restored(self):
        for failure in range(9, 16):
            result = self.simulate(8, failure)
            self.assertEqual(result.returncode, 1)
            self.assertIn('recovery requires human review', result.stderr)
            self.assertNotIn('snapshots restored', result.stderr)
            recovery = result.stdout.splitlines()[8:]
            for artifact in ('policy', 'helper', 'wrapper'):
                self.assertTrue(any('path-' + artifact + '.previous' in line for line in recovery))

    def test_exact_snapshot_hashes_and_separate_recovery_paths(self):
        import hashlib
        document = (ROOT / 'docs/qualification/PATH_INDEPENDENCE.md').read_text()
        for name in ('scripts/qualification/run_operator_preflight.py',
                     'scripts/qualification/operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            snapshot = subprocess.check_output(['/usr/bin/git', 'show',
                'f1dfe6cf10f22d0d5da3e39f2b49dc12ee286181:' + name], cwd=ROOT)
            self.assertIn(hashlib.sha256(snapshot).hexdigest(), document)
        self.assertNotIn('.ai-invest-environment.pending', document)
        self.assertIn('path-helper.previous', document)
        self.assertIn('"$policy_restored:$helper_restored:$wrapper_restored" = 1:1:1', document)


if __name__ == '__main__':
    unittest.main()
