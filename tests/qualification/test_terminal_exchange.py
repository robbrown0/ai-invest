"""Unprivileged PTY mechanics and mocked controls; NOT a protected VT trial.

All displayed/typed values are fixed harmless fixtures, never generated runtime
material. No sudo, host observer, project secret, shell input, or crash is used.
"""
import ast
from contextlib import redirect_stdout, redirect_stderr
import fcntl
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import termios
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('terminal_candidate',
    ROOT / 'scripts/qualification/terminal_exchange.py')
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
FIXTURE = b'SYNTHETIC-' + b'93' * 16


class PtyCase(unittest.TestCase):
    def setUp(self):
        self.master, self.slave = os.openpty()
        self.original = termios.tcgetattr(self.slave)
        self.flags = fcntl.fcntl(self.slave, fcntl.F_GETFL)

    def tearDown(self):
        os.close(self.master)
        os.close(self.slave)

    def restored(self, state):
        self.assertTrue(state['restored'])
        self.assertEqual(termios.tcgetattr(self.slave), self.original)
        self.assertEqual(fcntl.fcntl(self.slave, fcntl.F_GETFL), self.flags)


class MechanicsTests(PtyCase):
    def test_real_pty_echo_disabled_and_restored(self):
        state = {}
        with T.quiet_terminal(self.slave, state):
            self.assertTrue(T.no_echo(termios.tcgetattr(self.slave)))
            os.write(self.master, FIXTURE + b'\n')
            self.assertEqual(T.read_disposable(self.slave, time.monotonic() + 1), FIXTURE)
            self.assertFalse(select.select([self.master], [], [], 0)[0])
        self.restored(state)

    def test_pty_pending_input_flushed_at_entry_and_exit(self):
        os.write(self.master, b'INERT_PREEXISTING\n')
        state = {}
        with T.quiet_terminal(self.slave, state):
            self.assertFalse(select.select([self.slave], [], [], 0)[0])
            os.write(self.master, b'INERT_PENDING')
        self.restored(state)
        self.assertFalse(select.select([self.slave], [], [], 0)[0])

    def test_real_pty_cancel_eof_and_suspend_restore(self):
        for key, reason in ((b'\x03', 'input_cancelled'), (b'\x04', 'input_eof'),
                            (b'\x1a', 'input_cancelled')):
            state = {}
            with self.assertRaises(T.Refused) as error:
                with T.quiet_terminal(self.slave, state):
                    os.write(self.master, b'INERT-PARTIAL' + key)
                    T.read_disposable(self.slave, time.monotonic() + 1)
            self.assertEqual(error.exception.reason, reason)
            self.restored(state)

    def test_real_pty_timeout_restores(self):
        state = {}
        with self.assertRaises(T.Refused) as error:
            with T.quiet_terminal(self.slave, state):
                T.read_disposable(self.slave, time.monotonic() - 1)
        self.assertEqual(error.exception.reason, 'input_timeout')
        self.restored(state)

    def test_real_catchable_signals_restore_terminal_and_handlers(self):
        for number in T.CATCH_SIGNALS:
            state = {}
            previous = signal.getsignal(number)
            with self.assertRaises(T.Refused) as error:
                with T.interruptions(), T.quiet_terminal(self.slave, state):
                    signal.raise_signal(number)
            self.assertEqual(error.exception.reason, 'interrupted')
            self.assertEqual(signal.getsignal(number), previous)
            self.restored(state)

    def test_read_length_invalid_controls_and_backspace(self):
        for data in (b'\n', b'\x1b', b'\xff', b'A' * (T.MAX_INPUT + 1)):
            with T.quiet_terminal(self.slave, {}):
                os.write(self.master, data)
                with self.assertRaises(T.Refused) as error:
                    T.read_disposable(self.slave, time.monotonic() + 1)
                self.assertEqual(error.exception.reason, 'input_invalid')
        with T.quiet_terminal(self.slave, {}):
            os.write(self.master, b'SYNTHETIC-X\x7fY\n')
            self.assertEqual(T.read_disposable(self.slave, time.monotonic() + 1), b'SYNTHETIC-Y')

    def test_real_display_goes_only_to_owned_pty(self):
        with T.quiet_terminal(self.slave, {}):
            T.display(self.slave, FIXTURE, time.monotonic() + 1)
            self.assertEqual(os.read(self.master, len(FIXTURE)), FIXTURE)

    def test_production_vt_gate_rejects_real_pty_even_mock_root(self):
        with patch.object(T.os, 'geteuid', return_value=0):
            with self.assertRaises(T.Refused) as error:
                T.require_vt(self.slave)
        self.assertEqual(error.exception.reason, 'terminal_identity')

    def test_partial_flush_failure_still_restores_termios_and_flags_reg_io01(self):
        real_flush = T.termios.tcflush
        calls = 0
        def flush(fd, mode):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('UNPUBLISHED')
            return real_flush(fd, mode)
        state = {}
        with patch.object(T.termios, 'tcflush', side_effect=flush):
            with self.assertRaises(T.Refused) as error:
                with T.quiet_terminal(self.slave, state):
                    pass
        self.assertEqual(error.exception.reason, 'terminal_restore')
        self.assertNotIn('restored', state)
        self.assertEqual(termios.tcgetattr(self.slave), self.original)
        self.assertEqual(fcntl.fcntl(self.slave, fcntl.F_GETFL), self.flags)

    def test_termios_failure_still_restores_flags_reg_io01(self):
        real_set = T.termios.tcsetattr
        count = 0
        def setter(*args):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('UNPUBLISHED')
            return real_set(*args)
        try:
            with patch.object(T.termios, 'tcsetattr', side_effect=setter):
                with self.assertRaises(T.Refused):
                    with T.quiet_terminal(self.slave, {}):
                        pass
            self.assertEqual(fcntl.fcntl(self.slave, fcntl.F_GETFL), self.flags)
        finally:
            real_set(self.slave, termios.TCSANOW, self.original)


class ExchangeTests(PtyCase):
    def exercise(self, *, entered=FIXTURE, protection_error=None, metadata=b'INERT',
                 read_error=None, rng=b'\x93' * 16, limit_failure=None):
        events = []
        limit_count = 0
        def limits(*args):
            nonlocal limit_count
            limit_count += 1
            events.append('limits')
            if limit_count == limit_failure:
                raise RuntimeError('UNPUBLISHED_LIMIT_FAILURE')
            return '/fixture'
        controls = SimpleNamespace(
            protect=Mock(side_effect=protection_error or (lambda _: events.append('protect'))),
            runtime_limits=Mock(side_effect=limits),
            prctl=Mock(return_value=0), bounded_read=Mock(return_value=metadata),
            contains=lambda v, data: v in data or v.hex().encode() in data)
        captures = []
        def display(fd, data, deadline):
            events.append('display')
            captures.append(data)
            self.assertTrue(T.no_echo(termios.tcgetattr(fd)))
        def reading(fd, deadline):
            events.append('input')
            if read_error:
                raise read_error
            return entered
        out, err = io.StringIO(), io.StringIO()
        with patch.object(T, 'require_vt'), patch.object(T, 'display', side_effect=display), \
             patch.object(T, 'read_disposable', side_effect=reading), \
             patch.object(T.os, 'getrandom', side_effect=lambda _: events.append('generate') or rng), \
             redirect_stdout(out), redirect_stderr(err):
            value = T.exercise(self.slave, controls)
        self.assertEqual(out.getvalue() + err.getvalue(), '')
        self.assertNotIn(FIXTURE, value)
        self.assertNotIn(FIXTURE.hex().encode(), value)
        result = json.loads(value)
        self.assertFalse(result['checks_passed'])
        self.assertFalse(result['secret_entry_authorized'])
        self.assertFalse(result['runtime_crash_suppression_qualified'])
        self.assertEqual(termios.tcgetattr(self.slave), self.original)
        return result, events, captures

    def test_success_protection_order_and_no_other_output(self):
        result, events, captures = self.exercise()
        self.assertEqual(events[:4], ['protect', 'limits', 'limits', 'generate'])
        self.assertLess(events.index('generate'), events.index('display'))
        self.assertLess(events.index('display'), events.index('input'))
        self.assertEqual(events[-1], 'limits')
        self.assertIn(FIXTURE, captures[0])  # Only intentional direct display fixture.
        self.assertEqual(set(result['results'].values()), {'PASS'})
        self.assertEqual(result['failed_checks'], ['coverage_incomplete'])

    def test_protection_failure_never_generates_displays_or_reads(self):
        result, events, captures = self.exercise(protection_error=RuntimeError('UNPUBLISHED'))
        self.assertEqual(events, [])
        self.assertFalse(captures)
        self.assertEqual(result['results']['terminal_restored'], 'NOT_TESTED')

    def test_short_random_refused_before_display(self):
        result, events, captures = self.exercise(rng=b'\x93')
        self.assertEqual(result['failed_checks'], ['protected_context'])
        self.assertFalse(captures)
        self.assertNotIn('input', events)

    def test_runtime_precheck_failure_no_input_and_postcheck_failure_not_pass(self):
        for call in (1, 2):
            result, events, captures = self.exercise(limit_failure=call)
            self.assertNotIn('generate', events)
            self.assertNotIn('input', events)
            self.assertFalse(captures)
        result, _, _ = self.exercise(limit_failure=3)
        self.assertEqual(result['results']['input_roundtrip'], 'PASS')
        self.assertEqual(result['results']['protection_after'], 'NOT_TESTED')
        self.assertEqual(result['failed_checks'], ['internal_error'])

    def test_input_mismatch_not_returned_or_echoed(self):
        result, _, captures = self.exercise(entered=b'SYNTHETIC-WRONG')
        self.assertEqual(result['failed_checks'], ['input_mismatch'])
        self.assertNotIn('SYNTHETIC-WRONG', json.dumps(result))
        self.assertNotIn(b'SYNTHETIC-WRONG', b''.join(captures))

    def test_cancellation_eof_timeout_interruption_fixed_results(self):
        for reason in ('input_cancelled', 'input_eof', 'input_timeout', 'interrupted'):
            result, _, _ = self.exercise(read_error=T.Refused(reason))
            self.assertEqual(result['failed_checks'], [reason])
            self.assertEqual(result['results']['terminal_restored'], 'PASS')
            self.assertEqual(result['results']['input_roundtrip'], 'NOT_TESTED')

    def test_raw_error_never_returned(self):
        result, _, _ = self.exercise(read_error=RuntimeError('UNPUBLISHED_EXCEPTION_DETAIL'))
        self.assertEqual(result['failed_checks'], ['internal_error'])
        self.assertNotIn('UNPUBLISHED', json.dumps(result))
        self.assertEqual(result['results']['terminal_restored'], 'PASS')

    def test_argv_environment_containment_failure_is_not_absence(self):
        for metadata in (FIXTURE, FIXTURE.hex().encode()):
            result, _, _ = self.exercise(metadata=metadata)
            self.assertEqual(result['results']['own_argv'], 'FAIL')
            self.assertEqual(result['results']['own_environment'], 'FAIL')
            self.assertEqual(result['failed_checks'], ['containment'])

    def test_actual_pty_roundtrip_with_mocked_authority_and_protection(self):
        # Exercise actual candidate I/O, but never claim this is a VT/cgroup test.
        controls = SimpleNamespace(protect=Mock(), runtime_limits=Mock(return_value='/fixture'),
            prctl=Mock(return_value=0), bounded_read=Mock(return_value=b'INERT'),
            contains=lambda v, data: v in data or v.hex().encode() in data)
        driver_ok = []
        def human_fixture():
            buffer = bytearray()
            deadline = time.monotonic() + 2
            try:
                while b'Ctrl-C cancels.\r\n' not in buffer:
                    if len(buffer) >= 512 or not select.select([self.master], [], [], max(0, deadline - time.monotonic()))[0]:
                        return
                    buffer.extend(os.read(self.master, 512 - len(buffer)))
                if FIXTURE not in buffer:
                    return
                os.write(self.master, FIXTURE + b'\n')
                driver_ok.append(True)
            except BaseException:
                return
        thread = threading.Thread(target=human_fixture, daemon=True)
        thread.start()
        try:
            with patch.object(T, 'require_vt'), patch.object(T.os, 'getrandom', return_value=b'\x93' * 16), \
                 patch.object(T, 'SECONDS', 2):
                encoded = T.exercise(self.slave, controls)
        finally:
            thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(driver_ok, [True])
        self.assertNotIn(FIXTURE, encoded)
        self.assertEqual(set(json.loads(encoded)['results'].values()), {'PASS'})
        self.assertEqual(termios.tcgetattr(self.slave), self.original)

    def test_entered_report_token_refuses_publication(self):
        with self.assertRaises(T.Refused) as error:
            self.exercise(entered=b'PASS')
        self.assertEqual(error.exception.reason, 'containment')


class BoundsAndScopeTests(unittest.TestCase):
    def test_mock_vt_metadata_requires_clean_post_transition_environment(self):
        info = SimpleNamespace(st_mode=stat.S_IFCHR, st_rdev=os.makedev(4, 3))
        with patch.object(T.os, 'fstat', return_value=info), patch.object(T.os, 'geteuid', return_value=0), \
             patch.object(T.os, 'isatty', return_value=True), patch.object(T.os, 'tcgetpgrp', return_value=7), \
             patch.object(T.os, 'getpgrp', return_value=7), patch.dict(T.os.environ, T.CLEAN_ENV, clear=True):
            T.require_vt(99)
            with patch.dict(T.os.environ, {'PYTHONPATH': 'UNTRUSTED'}):
                with self.assertRaises(T.Refused):
                    T.require_vt(99)
            with patch.object(T.os, 'tcgetpgrp', return_value=8):
                with self.assertRaises(T.Refused):
                    T.require_vt(99)

    def test_partial_nonblocking_write_and_read(self):
        with patch.object(T, 'wait_ready'), patch.object(T.os, 'write',
                side_effect=[BlockingIOError(), 2, 2]) as write:
            T.display(99, b'TEST', 1)
            self.assertEqual(write.call_count, 3)
        with patch.object(T, 'wait_ready'), patch.object(T.os, 'read',
                side_effect=[BlockingIOError(), b'X', b'\n']):
            self.assertEqual(T.read_disposable(99, 1), b'X')

    def test_zero_write_and_deadlines_refuse(self):
        with patch.object(T, 'wait_ready'), patch.object(T.os, 'write', return_value=0):
            with self.assertRaises(T.Refused):
                T.display(99, b'TEST', 1)
        for writing in (False, True):
            with self.assertRaises(T.Refused):
                T.wait_ready(99, time.monotonic() - 1, writing)
        with self.assertRaises(T.Refused):
            T.display(99, b'A' * 513, 1)

    def test_result_rejects_unknown_fields_values_flags_and_material(self):
        base = T.result()
        for value in ({**base, 'secret_entry_authorized': True},
                      {**base, 'runtime_crash_suppression_qualified': True},
                      {**base, 'extra': 'UNPUBLISHED'}, {**base, 'checks_passed': True},
                      {**base, 'secret_entry_authorized': 0},
                      {**base, 'failed_checks': []}, {**base, 'failed_checks': ['UNPUBLISHED']},
                      {**base, 'results': {}}):
            with self.assertRaises(T.Refused):
                T.encode(value, ())
        for value in ({'unknown': 'PASS'}, {'input_roundtrip': 'UNPUBLISHED'}):
            with self.assertRaises(T.Refused):
                T.result(value)
        with self.assertRaises(T.Refused):
            T.encode(T.result(), (b'coverage_incomplete',))

    def test_no_cli_exec_fork_file_writer_network_log_or_print(self):
        source = inspect.getsource(T)
        self.assertNotIn('__main__', source)
        tree = ast.parse(source)
        forbidden = {'print', 'exec', 'eval', 'open', 'fork', 'system', 'popen', 'Popen',
            'run', 'execve', 'execv', 'write_text', 'write_bytes', 'connect', 'send', 'logging'}
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        for node in calls:
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', '')
            self.assertNotIn(name, forbidden)
        writes = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'write']
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0].args[0].id, 'fd')

    def test_working_wrapper_policy_observer_unchanged(self):
        for name in ('scripts/qualification/run_operator_preflight.py',
                     'scripts/qualification/crash_canary.py',
                     'scripts/qualification/operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            original = subprocess.run(['/usr/bin/git', 'show',
                '46ce2ac030b69c70cfbbf01c7b238289f205a134:' + name],
                cwd=ROOT, capture_output=True, check=True, timeout=10).stdout
            self.assertEqual((ROOT / name).read_bytes(), original)

    def test_candidate_acceptance_never_qualifies_old_or_future_report(self):
        from test_operator_wrapper import WRAPPER
        with self.assertRaises(WRAPPER.Rejected):
            WRAPPER.validate_report(T.result(dict.fromkeys(T.CATEGORIES, 'PASS')))

    def test_existing_wrapper_refuses_proposed_mode_without_creating_result(self):
        from test_operator_wrapper import WRAPPER
        with patch.object(WRAPPER.sys, 'argv', [str(WRAPPER.INSTALLED), '--io-test']), \
             patch.object(WRAPPER.os, 'geteuid', return_value=0), \
             patch.object(WRAPPER, 'create_result') as create, \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(WRAPPER.main(), 1)
            create.assert_not_called()


if __name__ == '__main__':
    unittest.main()
