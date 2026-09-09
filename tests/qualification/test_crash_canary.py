"""Inert doubles only: this suite neither generates a runtime canary nor crashes."""
import ast
from contextlib import ExitStack
import hashlib
import importlib.util
import inspect
import json
import re
from pathlib import Path
import signal
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_operator_wrapper as base

W, ROOT = base.WRAPPER, base.ROOT
spec = importlib.util.spec_from_file_location('crash_module', ROOT / 'scripts/qualification/crash_canary.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)


class ExitDouble(BaseException):
    pass


class CrashTests(unittest.TestCase):
    def simulated_trial(self, *, status=signal.SIGABRT, protection_error=None,
                        wait_error=None, read_value=b'INERT_METADATA', cleanup=True, fork_result=123,
                        setup_failure=None):
        events, writes = [], []
        sentinel = bytes([147]) * 32  # Inert fixture, NOT a generated runtime canary.
        with ExitStack() as stack:
            stack.enter_context(patch.object(H, 'protect',
                side_effect=protection_error or (lambda pid: events.append('protect'))))
            stack.enter_context(patch.object(H, 'detach', side_effect=lambda fd: events.append('detach')))
            stack.enter_context(patch.object(H, 'runtime_limits', side_effect=lambda *args: events.append('limits') or Path('/synthetic')))
            rng = stack.enter_context(patch.object(H.os, 'getrandom', side_effect=lambda size: events.append('generate') or sentinel))
            stack.enter_context(patch.object(H, 'bounded_read', return_value=read_value))
            observer = stack.enter_context(patch.object(H, 'Observation'))
            observer.return_value.finish.return_value = {}
            observer.return_value.setup = dict.fromkeys(H.SETUP_STAGES, 'PASS')
            observer.return_value.ready = setup_failure is None
            if setup_failure:
                observer.return_value.setup[setup_failure] = 'FAIL'
            stack.enter_context(patch.object(H, 'wait_exit'))
            stack.enter_context(patch.object(H.os, 'fork', side_effect=lambda: events.append('fork') or fork_result))
            stack.enter_context(patch.object(H.os, 'close', side_effect=lambda fd: events.append('close')))
            stack.enter_context(patch.object(H.os, 'kill', side_effect=lambda *args: events.append('signal')))
            stack.enter_context(patch.object(H.signal, 'signal'))
            stack.enter_context(patch.object(H.signal, 'pthread_sigmask'))
            stack.enter_context(patch.object(H.os, 'pidfd_open', return_value=456))
            stack.enter_context(patch.object(H, 'wait_child', side_effect=wait_error, return_value=status))
            stack.enter_context(patch.object(H, 'prctl', return_value=0))
            stack.enter_context(patch.object(H.faulthandler, 'is_enabled', return_value=False))
            stack.enter_context(patch.object(H, 'reap_owned', side_effect=lambda *args: events.append('cleanup') or cleanup))
            stack.enter_context(patch.object(H.os, 'write', side_effect=lambda fd, data: writes.append(data) or len(data)))
            def exiting(code):
                events.append('exit:' + str(code))
                raise ExitDouble()
            stack.enter_context(patch.object(H.os, '_exit', side_effect=exiting))
            with self.assertRaises(ExitDouble):
                H.trial(999, 100)
            self.assertTrue(all(not H.contains(sentinel, data) for data in writes))
            result = json.loads(writes[-1])
            self.assertEqual(H.validate(result), result)
            return result, events, rng.call_count

    def test_local_success_is_not_complete_qualification(self):
        result, events, count = self.simulated_trial()
        self.assertEqual(count, 1)
        self.assertEqual(events[:5], ['protect', 'detach', 'limits', 'limits', 'generate'])
        for key in ('dumpable_parent', 'dumpable_child', 'crash_signal', 'kernel_core_flag',
                    'own_argv', 'own_environment', 'stdio_detached', 'child_reaped', 'cleanup'):
            self.assertEqual(result['results'][key], 'PASS')
        self.assertFalse(result['checks_passed'])
        self.assertEqual(result['failed_checks'], ['coverage_incomplete'])
        for key in ('collector_retention', 'journal', 'swap_bytes', 'human_input_path'):
            self.assertEqual(result['results'][key], 'NOT_TESTED')
        for key in ('sudo_logs', 'shell_history', 'application_logs', 'temporary_files',
                    'git_worktree', 'git_index', 'git_history', 'ci_artifacts'):
            self.assertEqual(result['results'][key], 'NOT_APPLICABLE')
        self.assertFalse(result['secret_entry_authorized'])
        self.assertFalse(result['runtime_crash_suppression_qualified'])

    def test_failed_protection_prevents_generation(self):
        result, _, count = self.simulated_trial(protection_error=H.Refused())
        self.assertEqual(count, 0)
        self.assertEqual(result['failed_checks'], ['crash_trial_failed'])

    def test_core_dump_bit_fails(self):
        result, _, _ = self.simulated_trial(status=int(signal.SIGABRT) | 128)
        self.assertEqual(result['results']['kernel_core_flag'], 'FAIL')
        self.assertEqual(result['failed_checks'], ['crash_trial_failed'])

    def test_wrong_exit_or_signal_fails(self):
        for status in (0, 71 << 8, signal.SIGKILL):
            result, _, _ = self.simulated_trial(status=status)
            self.assertEqual(result['results']['crash_signal'], 'FAIL')

    def test_own_argv_or_environment_containment_fails_without_leak(self):
        result, _, _ = self.simulated_trial(read_value=bytes([147]) * 32)
        self.assertEqual(result['results']['own_argv'], 'FAIL')
        self.assertEqual(result['results']['own_environment'], 'FAIL')

    def test_exception_details_not_published(self):
        result, _, _ = self.simulated_trial(wait_error=RuntimeError('UNPUBLISHED_EXCEPTION_DETAIL'))
        self.assertNotIn('UNPUBLISHED_EXCEPTION_DETAIL', json.dumps(result))
        self.assertEqual(result['failed_checks'], ['crash_trial_failed'])

    def test_interruption_cleanup(self):
        for error in (KeyboardInterrupt(), SystemExit(), H.Refused()):
            result, events, _ = self.simulated_trial(wait_error=error)
            self.assertIn('cleanup', events)
            self.assertEqual(result['failed_checks'], ['crash_trial_failed'])

    def test_failed_cleanup_not_pass(self):
        result, _, _ = self.simulated_trial(cleanup=False)
        self.assertEqual(result['results']['cleanup'], 'FAIL')

    def test_encoder_checks_failure_and_success_reg_cr03(self):
        for values in ({'kernel_core_flag': 'PASS'}, {'runtime_limits': 'FAIL'}):
            with patch.object(H, 'contains', return_value=True) as check:
                with self.assertRaises(H.Refused):
                    H.encode_result(values, b'INERT_SENTINEL')
                check.assert_called_once()

    def test_schema_and_flags_fail_closed(self):
        for value in ({**H.report(), 'canary': 'INERT'},
                      {**H.report(), 'secret_entry_authorized': True},
                      {**H.report(), 'runtime_crash_suppression_qualified': True},
                      {**H.report(), 'checks_passed': True},
                      {**H.report(), 'results': {'arbitrary': 'PASS'}}):
            with self.assertRaises(H.Refused):
                H.validate(value)
            with self.assertRaises(W.Rejected):
                W.validate_report(value)
        self.assertEqual(W.CRASH_CATEGORIES, set(H.CATEGORIES))

    def test_no_external_command_file_writer_or_stdout_sink(self):
        source = inspect.getsource(H)
        tree = ast.parse(source)
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        forbidden = {'print', 'eval', 'exec', 'system', 'popen', 'execv', 'execve', 'execvp',
                     'spawnv', 'Popen', 'NamedTemporaryFile', 'write_text', 'write_bytes'}
        self.assertFalse(any((isinstance(node.func, ast.Name) and node.func.id in forbidden)
                             or (isinstance(node.func, ast.Attribute) and node.func.attr in forbidden)
                             for node in calls))
        self.assertNotIn('O_CREAT', source)
        self.assertNotIn('O_TMPFILE', source)
        writes = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == 'write']
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0].args[1].id, 'candidate')

    def test_child_protected_before_crash_no_exec_or_output(self):
        source = inspect.getsource(H.trial)
        self.assertLess(source.index('protect(supervisor_pid)'), source.index('os.getrandom(32)'))
        self.assertLess(source.index('runtime_limits()'), source.index('os.getrandom(32)'))
        child = source.split('if child == 0:', 1)[1].split('child_fd =', 1)[0]
        for text in ('protect(parent)', 'os.close(output_fd)', 'runtime_limits(group)', 'prctl(3) == 0'):
            self.assertIn(text, child)
        self.assertNotIn('write(', child)
        self.assertNotIn('exec(', child)

    def test_protect_checks_pdeath_dumpable_core_faulthandler(self):
        with patch.object(H, 'prctl', side_effect=[0, 0, 0]) as control, \
             patch.object(H.os, 'getppid', return_value=100), \
             patch.object(H.faulthandler, 'disable') as disable, \
             patch.object(H.faulthandler, 'is_enabled', return_value=False), \
             patch.object(H.resource, 'getrlimit', return_value=(0, 0)):
            H.protect(100)
            self.assertEqual([call.args for call in control.call_args_list], [(1, signal.SIGKILL), (4, 0), (3,)])
            disable.assert_called_once()

    def test_missing_core_limit_fails(self):
        with patch.object(H, 'prctl', return_value=0), patch.object(H.os, 'getppid', return_value=100), \
             patch.object(H.faulthandler, 'disable'), patch.object(H.faulthandler, 'is_enabled', return_value=False), \
             patch.object(H.resource, 'getrlimit', return_value=(0, 1)):
            with self.assertRaises(H.Refused):
                H.protect(100)

    def test_inert_child_branch_closes_output_before_crash(self):
        _, events, _ = self.simulated_trial(fork_result=0)
        before_exit = events[:events.index('exit:71')]
        self.assertLess(before_exit.index('close'), before_exit.index('signal'))
        self.assertGreaterEqual(before_exit.count('protect'), 2)
        self.assertGreaterEqual(before_exit.count('limits'), 2)

    def test_failed_child_protection_cannot_reach_signal(self):
        calls = []
        def protection(pid):
            calls.append(pid)
            if len(calls) == 2:
                raise H.Refused()
        _, events, _ = self.simulated_trial(fork_result=0, protection_error=protection)
        self.assertNotIn('signal', events[:events.index('exit:71')])


class LimitTests(unittest.TestCase):
    def exercise(self, changes=None, expected=None):
        values = {'memory.max': '2147483648', 'memory.swap.max': '0',
                  'memory.swap.current': '0', 'pids.max': '32', 'cpu.max': '100000 100000'}
        values.update(changes or {})
        def namespace(path):
            return SimpleNamespace(st_ino=2 if path == '/proc/self/ns/mnt' else 1)
        with patch.object(H, 'runtime_group', return_value=Path('/synthetic/group')), \
             patch.object(H.Path, 'read_text', lambda path: values[path.name]), \
             patch.object(H.os, 'stat', side_effect=namespace), \
             patch.object(H.Path, 'iterdir', return_value=iter([Path('/synthetic/thread')])), \
             patch.object(H.resource, 'getrlimit', return_value=(0, 0)):
            return H.runtime_limits(expected)

    def test_exact_synthetic_no_swap_limits_accepted(self):
        self.assertEqual(self.exercise(), Path('/synthetic/group'))

    def test_swap_nonzero_unlimited_missing_or_malformed_denied(self):
        for name in ('memory.swap.max', 'memory.swap.current'):
            for value in ('1', 'max', '-1', '', 'arbitrary'):
                with self.assertRaises(H.Refused):
                    self.exercise({name: value})

    def test_cpu_pids_memory_over_limit_denied(self):
        for fixture in ({'memory.max': '2147483649'}, {'memory.max': '0'},
                        {'pids.max': '33'}, {'cpu.max': '200000 100000'},
                        {'cpu.max': 'max 100000'}, {'cpu.max': '1 0'}):
            with self.assertRaises(H.Refused):
                self.exercise(fixture)

    def test_cgroup_migration_refused(self):
        with self.assertRaises(H.Refused):
            self.exercise(expected=Path('/synthetic/different'))


class CleanupTests(unittest.TestCase):
    def test_interruption_after_reap_cannot_signal_reused_pid_reg_cr01(self):
        with patch.object(H.signal, 'pidfd_send_signal', side_effect=ProcessLookupError) as send, \
             patch.object(H, 'wait_child', side_effect=ChildProcessError), \
             patch.object(H.os, 'kill') as numeric, patch.object(H.os, 'close') as close:
            self.assertTrue(H.reap_owned(123, 456))
            numeric.assert_not_called()
            send.assert_called_once_with(456, signal.SIGKILL, None, 0)
            close.assert_called_once_with(456)

    def test_cleanup_timeout_reported_reg_cr02(self):
        with patch.object(H.signal, 'pidfd_send_signal'), \
             patch.object(H, 'wait_child', side_effect=H.Refused()), patch.object(H.os, 'close') as close:
            self.assertFalse(H.reap_owned(123, 456))
            close.assert_called_once_with(456)

    def test_no_numeric_kill_fallback(self):
        with patch.object(H.os, 'kill') as numeric:
            self.assertFalse(H.reap_owned(123, None))
            numeric.assert_not_called()

    def test_reaped_handle_only_closed(self):
        with patch.object(H.os, 'close') as close, patch.object(H.signal, 'pidfd_send_signal') as send:
            self.assertTrue(H.reap_owned(None, 456))
            close.assert_called_once_with(456)
            send.assert_not_called()

    def test_wait_nonblocking_and_bounded(self):
        with patch.object(H.time, 'monotonic', side_effect=[1, 3]), \
             patch.object(H.time, 'sleep'), patch.object(H.os, 'waitpid', return_value=(0, 0)) as wait:
            with self.assertRaises(H.Refused):
                H.wait_child(123, 2)
            wait.assert_called_once_with(123, H.os.WNOHANG)


class IntegrationTests(unittest.TestCase):
    def test_harness_pin_and_fixed_result(self):
        self.assertEqual(hashlib.sha256((ROOT / 'scripts/qualification/crash_canary.py').read_bytes()).hexdigest(), W.CRASH_SHA256)
        self.assertEqual(str(W.CRASH_RESULT), '/var/tmp/ai-invest-crash-log-source.json')

    def test_systemd_warning_removed_reg_sd01(self):
        for diagnostic, crash in ((False, False), (True, False), (True, True)):
            command = W.scope_command('1:2', diagnostic, crash)
            self.assertIn('--expand-environment=no', command)
            self.assertFalse(any('$' in item or chr(96) in item for item in command))
            self.assertNotIn('/bin/bash', command)
            self.assertEqual(command[-6:-3], ['/usr/bin/python3', '-I', '-B'])
        for bad in ('$(false)', '1:2;false', '../1', '', '1:2\n'):
            with self.assertRaises(W.Rejected):
                W.scope_command(bad, True, True)

    def test_real_unprivileged_exec_preserves_core_limits(self):
        code = ('import resource,os; resource.setrlimit(resource.RLIMIT_CORE,(0,0)); '
                'os.execve("/usr/bin/python3",["/usr/bin/python3","-I","-B","-c",'
                '"import resource; print(\\"PASS\\" if resource.getrlimit(resource.RLIMIT_CORE)==(0,0) else \\"FAIL\\")"],'
                '{"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LANG":"C","LC_ALL":"C"})')
        result = subprocess.run(['/usr/bin/python3', '-I', '-B', '-c', code],
                                env=W.CLEAN_ENV, capture_output=True, text=True, timeout=10)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'PASS\n', ''))

    def test_bad_metadata_prevents_harness(self):
        with patch.object(W, 'invoke_crash') as trial:
            result = base.FlowTests().exercise(args=('--scoped-crash-test', '1:2'), plan_pass=False)
            self.assertEqual(result[0], 1)
            trial.assert_not_called()

    def test_run_fails_before_fork_or_rng(self):
        with patch.object(H.os, 'geteuid', return_value=1000), \
             patch.object(H.os, 'fork') as fork, patch.object(H.os, 'getrandom') as rng:
            result = H.run()
            fork.assert_not_called()
            rng.assert_not_called()
            self.assertEqual(result['failed_checks'], ['crash_trial_failed'])


class UpgradeTests(unittest.TestCase):
    def transaction(self):
        text = (ROOT / 'docs/qualification/CRASH_CHECKPOINT.md').read_text()
        found = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", text, re.S)
        self.assertEqual(len(found), 1)
        self.assertNotRegex(found[0], r'\bsudo\b')
        return found[0]

    def simulate(self, fail_at=0, bad_hash=False):
        script = self.transaction()
        for name in ('/usr/bin/install', '/usr/bin/mv', '/usr/sbin/visudo'):
            script = script.replace(name, 'fake_command')
        script = script.replace('/usr/bin/test', 'fake_test').replace(
            '/usr/bin/sha256sum', 'fake_hash').replace('/usr/bin/unlink', 'fake_unlink')
        functions = 'count=0\nharness=0\nfail_at=' + str(fail_at) + '\nbad_hash=' + str(int(bad_hash)) + r'''
fake_command() {
  count=$((count+1)); printf "step:%s\n" "$count"
  test "$count" -ne "$fail_at" || return 1
  case "$*" in *"/usr/local/libexec/ai-invest/crash_canary.py") harness=1;; esac
}
fake_test() {
  case "$1:$2" in "!:-e") test "$harness" = 0;; "!:-L") return 0;; "-f:"*) test "$harness" = 1;; *) return 1;; esac
}
fake_hash() { while IFS= read -r line; do :; done; test "$bad_hash" = 0; }
fake_unlink() { harness=0; printf "harness-removed\n"; }
'''
        return subprocess.run(['/bin/sh', '-c', functions + script],
                              env=W.CLEAN_ENV, capture_output=True, text=True, timeout=10)

    def test_activation_and_each_failure_restore_prior_state(self):
        for failure in range(9):
            result = self.simulate(failure)
            self.assertEqual(result.returncode, int(bool(failure)))
            if failure:
                self.assertIn('prior reviewed pair and harness absence restored', result.stderr)
            else:
                self.assertEqual(result.stderr, '')
                self.assertEqual(len(result.stdout.splitlines()), 8)

    def test_unknown_harness_bytes_not_removed(self):
        result = self.simulate(8, bad_hash=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('recovery requires human review', result.stderr)
        self.assertNotIn('harness-removed', result.stdout)

    def test_historical_digests_in_human_checkpoint(self):
        text = (ROOT / 'docs/qualification/CRASH_CHECKPOINT.md').read_text()
        for file in ('scripts/qualification/run_operator_preflight.py',
                     'scripts/qualification/crash_canary.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            original = subprocess.run(['/usr/bin/git', 'show',
                '5975603575b6761fb44932b84dc1519676639584:' + file],
                cwd=ROOT, capture_output=True, check=True, timeout=10).stdout
            self.assertIn(hashlib.sha256(original).hexdigest(), text)
        self.assertLess(self.transaction().index('crash-policy.previous'),
                        self.transaction().index('crash-wrapper.previous'))


if __name__ == '__main__':
    unittest.main()
