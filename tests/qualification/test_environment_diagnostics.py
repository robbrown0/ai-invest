"""Bounded synthetic environment fixtures only; never inspect the sudo environment."""
import inspect
import re
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_operator_wrapper as base

W, ROOT = base.WRAPPER, base.ROOT
BASELINE = '41d4721e7d4ffaceba1033f0bd45717281d22977'


class EnvironmentTests(unittest.TestCase):
    def safe(self):
        return {'PATH': W.CLEAN_ENV['PATH'], 'SUDO_GID': '1000'}

    def exercise(self, environment):
        with patch.dict(W.os.environ, environment, clear=True), \
             patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_gid=1000)):
            W.require_operator_environment()

    def assert_failure(self, changes, symbol, remove=()):
        environment = {**self.safe(), **changes}
        for key in remove:
            environment.pop(key, None)
        with self.assertRaises(W.EnvironmentRejected) as caught:
            self.exercise(environment)
        self.assertEqual(caught.exception.check, symbol)
        self.assertEqual(str(caught.exception), '')

    def test_each_predicate_independently_fails(self):
        cases = [({'UNAPPROVED_SYNTHETIC': 'not-for-output'}, 'environment_keyset'),
                 ({'PATH': '/synthetic'}, 'environment_path'),
                 ({'LANG': '\n'}, 'environment_locale'), ({'LC_ALL': '\n'}, 'environment_locale'),
                 ({'TERM': '\n'}, 'environment_term'), ({'HOME': '/synthetic'}, 'environment_home'),
                 ({'USER': 'synthetic'}, 'environment_user'), ({'LOGNAME': 'synthetic'}, 'environment_logname'),
                 ({'MAIL': '/synthetic'}, 'environment_mail'), ({'SHELL': '/synthetic'}, 'environment_shell'),
                 ({'SUDO_GID': '1001'}, 'environment_sudo_gid')]
        for changes, symbol in cases:
            with self.subTest(symbol=symbol, fixture=list(changes)):
                self.assert_failure(changes, symbol)

    def test_missing_path_is_not_normalized_to_success(self):
        self.assert_failure({}, 'environment_path', remove=('PATH',))

    def test_missing_gid_fails(self):
        self.assert_failure({}, 'environment_sudo_gid', remove=('SUDO_GID',))

    def test_loader_python_shell_and_extra_keys_rejected_without_naming_them(self):
        for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME',
                    'PYTHONINSPECT', 'BASH_ENV', 'ENV', 'SHELLOPTS', 'IFS',
                    'BASH_FUNC_synthetic%%', 'SUDO_ASKPASS', 'SUDO_PS1', 'UNAPPROVED_SYNTHETIC'):
            with self.subTest(fixture=key):
                self.assert_failure({key: 'SYNTHETIC_NOT_FOR_OUTPUT'}, 'environment_keyset')

    def test_locale_and_term_parser_boundaries_unchanged(self):
        for key in ('LANG', 'LC_ALL', 'TERM'):
            for value in ('$(false)', '`false`', 'x/y', 'x y', 'x\ny', 'é', 'a' * 65):
                self.assert_failure({key: value}, 'environment_term' if key == 'TERM' else 'environment_locale')
            for value in ('', 'C', 'en_US.UTF-8', 'a' * 64):
                self.exercise({**self.safe(), key: value})

    def test_safe_minimal_environment(self):
        self.exercise(self.safe())

    def test_safe_full_previously_accepted_environment(self):
        self.exercise({**self.safe(), 'LANG': 'C', 'LC_ALL': 'C', 'TERM': 'linux',
                       'HOME': '/root', 'USER': 'root', 'LOGNAME': 'root', 'MAIL': '/var/mail/root',
                       'SHELL': '/bin/bash', 'SUDO_UID': '1000', 'SUDO_USER': 'synthetic-owner',
                       'SUDO_COMMAND': str(W.INSTALLED) + ' --diagnostic'})

    def test_first_failure_order(self):
        self.assert_failure({'UNAPPROVED_SYNTHETIC': '', 'PATH': '/synthetic', 'HOME': '/synthetic'}, 'environment_keyset')
        self.assert_failure({'PATH': '/synthetic', 'LANG': '\n', 'HOME': '/synthetic'}, 'environment_path')
        self.assert_failure({'LANG': '\n', 'TERM': '\n'}, 'environment_locale')
        self.assert_failure({'HOME': '/synthetic', 'USER': 'synthetic'}, 'environment_home')

    def test_exception_details_never_become_diagnostic_content(self):
        for check in W.ENVIRONMENT_CHECKS:
            with self.assertRaises(W.EnvironmentRejected) as caught:
                W.environment_require(check, lambda: (_ for _ in ()).throw(
                    OSError('SYNTHETIC_PRIVATE_TEXT /synthetic/path')))
            self.assertEqual(caught.exception.check, check)
            self.assertEqual(str(caught.exception), '')

    def test_every_symbol_publishes_only_fixed_schema_and_false_flags(self):
        for check in W.ENVIRONMENT_CHECKS:
            code, helper, run, reports, output, _ = base.FlowTests().exercise(
                args=('--diagnostic',), guard_failure='require_operator_environment',
                guard_effect=W.EnvironmentRejected(check))
            self.assertEqual(code, 1)
            helper.assert_not_called()
            run.assert_not_called()
            self.assertEqual(reports[-1], W.failure(True, check))
            self.assertEqual(set(reports[-1]), {'mode', 'checks_passed', 'failed_checks',
                             'secret_entry_authorized', 'runtime_crash_suppression_qualified'})
            self.assertNotIn('SYNTHETIC_PRIVATE', output)

    def test_invalid_symbols_and_forged_reports_rejected(self):
        for check in ('LD_PRELOAD', '/synthetic/path', 'synthetic-value', '', None, 1):
            with self.assertRaises(W.Rejected):
                W.EnvironmentRejected(check)
            value = {**W.failure(True, 'environment_keyset'), 'failed_checks': [check]}
            with self.assertRaises(W.Rejected):
                W.validate_report(value)
        for flag in ('secret_entry_authorized', 'runtime_crash_suppression_qualified'):
            with self.assertRaises(W.Rejected):
                W.validate_report({**W.failure(True, 'environment_keyset'), flag: True})

    def test_unknown_environment_exception_remains_coarse_and_sanitized(self):
        code, _, _, reports, output, _ = base.FlowTests().exercise(
            args=('--diagnostic',), guard_failure='require_operator_environment',
            guard_effect=RuntimeError('SYNTHETIC_PRIVATE_TEXT'))
        self.assertEqual(code, 1)
        self.assertEqual(reports[-1], W.failure(True, 'operator_environment'))
        self.assertNotIn('SYNTHETIC_PRIVATE_TEXT', output)

    def test_success_continues_to_scope_with_exact_clean_environment(self):
        original = W.require_operator_environment
        def valid_environment():
            W.os.environ.update(self.safe())
            with patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_gid=1000)):
                original()
        success = {'mode': 'diagnostic', 'checks_passed': True, 'failed_checks': [],
                   'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}
        code, helper, run, reports, _, _ = base.FlowTests().exercise(
            args=('--diagnostic',), candidate=success, guard_failure='require_operator_environment',
            guard_effect=valid_environment)
        self.assertEqual(code, 0)
        self.assertEqual(reports[-1], success)
        self.assertEqual(run.call_args.kwargs['env'], W.CLEAN_ENV)
        self.assertEqual(set(run.call_args.kwargs['env']), {'PATH', 'LANG', 'LC_ALL'})
        self.assertEqual(helper.call_args_list[0].args[1], 'plan')

    def test_ordinary_mode_and_unknown_boundary_cannot_emit_refinement(self):
        self.assertEqual(base.FlowTests().exercise()[0], 0)
        _, _, _, reports, _, _ = base.FlowTests().exercise(
            args=('--diagnostic',), guard_failure='require_console_session',
            guard_effect=W.EnvironmentRejected('environment_path'))
        self.assertEqual(reports[-1], W.failure(True, 'console_session'))

    def test_acceptance_equivalent_to_committed_baseline(self):
        source = subprocess.check_output(['git', 'show', BASELINE + ':scripts/qualification/run_operator_preflight.py'], cwd=ROOT)
        old = {'__name__': 'baseline_not_main'}
        exec(compile(source, '<reviewed-baseline>', 'exec'), old)
        fixtures = [self.safe(), {}, {**self.safe(), 'TERM': 'linux'}]
        for key in ('PATH', 'LANG', 'LC_ALL', 'TERM', 'HOME', 'USER', 'LOGNAME', 'MAIL', 'SHELL',
                    'SUDO_GID', 'UNAPPROVED_SYNTHETIC', 'LD_PRELOAD', 'PYTHONHOME'):
            for value in ('', 'C', '/root', '/bin/bash', '1000', 'x\ny', '$(false)', 'a' * 65):
                fixtures.append({**self.safe(), key: value})
        def accepted(function):
            try:
                function()
                return True
            except Exception:
                return False
        with patch.object(W.pwd, 'getpwuid', return_value=SimpleNamespace(pw_gid=1000)):
            for fixture in fixtures:
                with patch.dict(W.os.environ, fixture, clear=True):
                    self.assertEqual(accepted(W.require_operator_environment),
                                     accepted(old['require_operator_environment']))

    def test_policy_change_is_digest_only(self):
        path = 'infrastructure/qualification/ai-invest-operator.sudoers'
        old = subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT).decode()
        normalize = lambda value: re.sub(r'sha256:[a-f0-9]{64}', 'sha256:REVIEWED_DIGEST', value)
        self.assertEqual(normalize(old), normalize((ROOT / path).read_text()))

    def test_python_isolation_with_synthetic_python_settings(self):
        result = subprocess.run(['/usr/bin/python3', '-I', '-c',
            'import sys; print("PASS" if sys.flags.isolated and sys.flags.ignore_environment and sys.flags.no_user_site else "FAIL")'],
            env={**W.CLEAN_ENV, 'PYTHONHOME': '/synthetic-not-a-python-home',
                 'PYTHONPATH': '/synthetic-not-a-module-path', 'PYTHONINSPECT': '1'},
            capture_output=True, text=True, timeout=10)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'PASS\n', ''))

    def test_authorization_evidence_validated_before_normalization(self):
        source = inspect.getsource(W.main)
        order = ['require_console()', 'trusted_helper()', 'require_operator_identity()',
                 'require_operator_environment()', 'require_console_session()',
                 'os.environ.clear()', 'os.environ.update(CLEAN_ENV)', 'require_host(scoped)']
        positions = [source.index(item) for item in order]
        self.assertEqual(positions, sorted(positions))
        code, helper, run, reports, _, _ = base.FlowTests().exercise(
            args=('--diagnostic',), guard_failure='require_operator_identity')
        self.assertEqual(code, 1)
        helper.assert_not_called()
        run.assert_not_called()
        self.assertEqual(reports[-1], W.failure(True, 'operator_identity'))

    def test_paired_upgrade_restores_old_pair_in_same_transaction(self):
        document = (ROOT / 'docs/qualification/ENVIRONMENT_DIAGNOSTICS.md').read_text()
        matches = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", document, re.S)
        self.assertEqual(len(matches), 1)
        transaction = matches[0]
        self.assertIsNone(re.search(r'\bsudo\b', transaction))
        self.assertIn('trap rollback EXIT HUP INT TERM', transaction)
        self.assertIn('environment-wrapper.previous', transaction)
        self.assertIn('environment-policy.previous', transaction)
        self.assertIn('/etc/sudoers.d/.ai-invest-environment.pending', transaction)
        script = transaction.replace('/usr/bin/install', 'fake_command').replace(
            '/usr/bin/mv', 'fake_command').replace('/usr/sbin/visudo', 'fake_command')
        # Only inert command doubles execute: no real installation, rename or sudo.
        functions = '''
count=0
fake_command() { count=$((count+1)); printf "step:%s\\n" "$count"; test "$count" -ne "$fail_at"; }
'''
        for fail_at in range(7):
            result = subprocess.run(['/bin/sh', '-c', 'fail_at=' + str(fail_at) + '\n' + functions + script],
                                    env=W.CLEAN_ENV, capture_output=True, text=True, timeout=10)
            count = fail_at + 5 if fail_at else 6
            self.assertEqual(result.stdout, ''.join('step:' + str(i) + '\n' for i in range(1, count + 1)))
            self.assertEqual(result.returncode, 1 if fail_at else 0)
            self.assertEqual(result.stderr,
                'Upgrade refused; prior reviewed pair restored. No secret entry.\n' if fail_at else '')

    def test_policy_recovery_attempt_precedes_wrapper_failure_reg_er_01(self):
        document = (ROOT / 'docs/qualification/ENVIRONMENT_DIAGNOSTICS.md').read_text()
        transaction = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", document, re.S)[0]
        rollback = transaction.split('rollback() {', 1)[1].split('exit 1', 1)[0]
        self.assertLess(rollback.index('environment-policy.previous'), rollback.index('environment-wrapper.previous'))
        script = transaction.replace('/usr/bin/install', 'fake_command').replace(
            '/usr/bin/mv', 'fake_command').replace('/usr/sbin/visudo', 'fake_command')
        # Fail aggregate activation, then fail one rollback step. Policy recovery
        # does not depend on wrapper restoration; each recovery leg is attempted.
        for rollback_failure, count in ((7, 9), (8, 10), (9, 11), (10, 10), (11, 11)):
            functions = 'count=0\nrollback_failure=' + str(rollback_failure) + '''
fake_command() { count=$((count+1)); printf "step:%s\\n" "$count"; test "$count" -ne 6 && test "$count" -ne "$rollback_failure"; }
'''
            result = subprocess.run(['/bin/sh', '-c', functions + script], env=W.CLEAN_ENV,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, ''.join('step:' + str(i) + '\n' for i in range(1, count + 1)))
            self.assertEqual(result.stderr, 'Upgrade refused; recovery requires human review. No secret entry.\n')


if __name__ == '__main__':
    unittest.main()
