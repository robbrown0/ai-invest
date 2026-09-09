"""Fault-injection diagnostics: no privileged scope, secret or host mutation."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_operator_preflight as helper_tests
import test_operator_wrapper as wrapper_tests

H = helper_tests.PREFLIGHT
W = wrapper_tests.WRAPPER
SENTINEL = 'SYNTHETIC_PRIVATE_DETAIL /synthetic/not-to-be-returned'


def diagnostic(check=None):
    return {'mode': 'diagnostic', 'checks_passed': check is None,
            'failed_checks': [] if check is None else [check],
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}


class MetadataDiagnosticsTests(unittest.TestCase):
    def source_fixture(self, unavailable=None):
        stack = ExitStack()
        self.addCleanup(stack.close)
        group = Path('/synthetic/cgroup')
        field_ids = {'cpu.max': 'cpu_max', 'memory.max': 'memory_max',
                     'memory.swap.max': 'memory_swap_max', 'memory.swap.current': 'memory_swap_current',
                     'pids.max': 'pids_max', 'core_pattern': 'core_pattern'}
        values = {'cpu.max': '100000 100000', 'memory.max': str(H.MAX_MEMORY),
                  'memory.swap.max': '0', 'memory.swap.current': '0', 'pids.max': '32',
                  'core_pattern': H.CORE_PATTERN}

        def obtain(check, value):
            if unavailable == check:
                raise OSError(SENTINEL)
            return value

        def read_text(path, *args, **kwargs):
            return obtain(field_ids[path.name], values[path.name])

        def ns_stat(path, *args, **kwargs):
            kind = 'mount_namespace' if str(path).endswith('/mnt') else 'pid_namespace'
            inode = 2 if kind == 'mount_namespace' and '/self/' in str(path) else 1
            return obtain(kind, SimpleNamespace(st_ino=inode))

        stack.enter_context(patch.object(H, 'cgroup_directory', side_effect=lambda: obtain('cgroup_membership', group)))
        stack.enter_context(patch.object(H.resource, 'getrlimit', side_effect=lambda *args: obtain('rlimit_core', (0, 0))))
        stack.enter_context(patch.object(H.os, 'isatty', return_value=True))
        stack.enter_context(patch.object(H.os, 'ttyname', side_effect=lambda fd: obtain('tty_identity', '/dev/tty1')))
        stack.enter_context(patch.object(H.os, 'geteuid', side_effect=lambda: obtain('root_operator', 0)))
        stack.enter_context(patch.object(H.os, 'stat', side_effect=ns_stat))
        stack.enter_context(patch.object(H.Path, 'read_text', read_text))
        stack.enter_context(patch.object(H.Path, 'read_bytes', side_effect=lambda: obtain('apport_handler', b'SYNTHETIC_SOURCE')))
        stack.enter_context(patch.object(H, 'APPORT_SHA256', hashlib.sha256(b'SYNTHETIC_SOURCE').hexdigest()))
        return stack

    def test_every_actual_unavailable_source_returns_only_its_identifier(self):
        for check in H.METADATA_CHECKS:
            with self.subTest(check=check), self.source_fixture(check):
                report = H.diagnostic_report()
                self.assertEqual(report, diagnostic(check))
                self.assertNotIn(SENTINEL, json.dumps(report))
                self.assertEqual(set(report), set(diagnostic()))

    def test_all_readable_valid_sources_succeed_without_values(self):
        with self.source_fixture():
            self.assertEqual(H.diagnostic_report(), diagnostic())

    def test_each_unsafe_predicate_reports_its_symbol(self):
        cases = {'root_operator': ('root_operator', False), 'tty_identity': ('direct_virtual_console', False),
                 'cpu_max': ('cpu_limit_bounded', False), 'rlimit_core': ('core_soft_zero', False),
                 'mount_namespace': ('mount_namespace_differs_from_visible_pid1', False),
                 'pid_namespace': ('pid_namespace_matches_visible_pid1', False),
                 'apport_handler': ('reviewed_apport_handler', False),
                 'core_pattern': ('reviewed_core_pattern', False), 'memory_max': ('memory_max', 'max'),
                 'pids_max': ('pids_max', '65'), 'memory_swap_max': ('memory_swap_max', '1'),
                 'memory_swap_current': ('memory_swap_current', '1')}
        for check, (field, value) in cases.items():
            snapshot = helper_tests.OperatorTests().valid()
            snapshot[field] = value
            with self.subTest(check=check), patch.object(H, 'operator_snapshot', return_value=snapshot):
                self.assertEqual(H.diagnostic_report(), diagnostic(check))

    def test_unparseable_numeric_evaluation_maps_to_source(self):
        for field in ('memory_max', 'pids_max'):
            for value in ('²', '9' * 5000):
                snapshot = helper_tests.OperatorTests().valid()
                snapshot[field] = value
                with self.subTest(field=field), patch.object(H, 'operator_snapshot', return_value=snapshot):
                    self.assertEqual(H.diagnostic_report(), diagnostic(field))

    def test_exception_details_and_types_never_appear(self):
        for error in (OSError(SENTINEL), ValueError(SENTINEL), RuntimeError(SENTINEL),
                      subprocess.CalledProcessError(1, SENTINEL, output=SENTINEL, stderr=SENTINEL)):
            with self.assertRaises(H.MetadataUnavailable) as caught:
                H.metadata('memory_max', lambda: (_ for _ in ()).throw(error))
            self.assertEqual(caught.exception.check, 'memory_max')
            self.assertEqual(str(caught.exception), '')

    def test_bad_diagnostic_arguments_never_echo_payload(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, 'argv', ['helper', 'diagnostic', SENTINEL]), \
             redirect_stdout(output), redirect_stderr(errors):
            self.assertEqual(H.main(), 1)
        self.assertEqual(json.loads(output.getvalue()), diagnostic('operator_evaluation'))
        self.assertEqual(errors.getvalue(), '')

    def test_ordinary_success_and_failure_match_original_committed_helper(self):
        source = subprocess.check_output(['git', 'show', W.HELPER_BASELINE_COMMIT + ':scripts/qualification/operator_preflight.py'], cwd=helper_tests.ROOT)
        original = {'__name__': 'original_preflight'}
        exec(compile(source, '<reviewed-original-helper>', 'exec'), original)
        snapshot = helper_tests.OperatorTests().valid()
        for fail in (False, True):
            for mode in ('plan', 'operator'):
                def read():
                    if fail:
                        raise OSError(SENTINEL)
                    return snapshot
                original[mode + '_snapshot'] = read
                original['plan_ok'] = lambda value: True
                outputs = []
                for old in (True, False):
                    output = io.StringIO()
                    with patch.object(sys, 'argv', ['preflight', mode]), redirect_stdout(output), \
                         patch.object(H, mode + '_snapshot', side_effect=read), \
                         patch.object(H, 'plan_ok', return_value=True):
                        code = original['main']() if old else H.main()
                    outputs.append((code, output.getvalue()))
                self.assertEqual(outputs[0], outputs[1])


class WrapperDiagnosticsTests(unittest.TestCase):
    def test_early_unwritable_result_fallback_is_bounded_and_nonsecret(self):
        cases = ((1000, ['--diagnostic'], None, 'root_operator'),
                 (0, ['--diagnostic', SENTINEL], None, 'arguments'),
                 (0, ['--diagnostic'], FileExistsError(SENTINEL), 'result_file'))
        for uid, args, file_error, check in cases:
            output, errors = io.StringIO(), io.StringIO()
            with self.subTest(check=check), ExitStack() as stack:
                stack.enter_context(patch.object(sys, 'argv', ['wrapper', *args]))
                stack.enter_context(patch.object(W.os, 'geteuid', return_value=uid))
                stack.enter_context(patch.object(W.resource, 'setrlimit'))
                stack.enter_context(patch.object(W.os, 'umask'))
                create = stack.enter_context(patch.object(W, 'create_result', side_effect=file_error))
                run = stack.enter_context(patch.object(W.subprocess, 'run'))
                stack.enter_context(redirect_stdout(output))
                stack.enter_context(redirect_stderr(errors))
                self.assertEqual(W.main(), 1)
                run.assert_not_called()
                if check != 'result_file':
                    create.assert_not_called()
            self.assertEqual(json.loads(output.getvalue()), diagnostic(check))
            self.assertNotIn(SENTINEL, output.getvalue() + errors.getvalue())
            self.assertNotIn('Traceback', errors.getvalue())

    def test_exact_allowlist_and_schema_reject_untrusted_payloads(self):
        for check in W.DIAGNOSTIC_CHECKS:
            self.assertEqual(W.validate_report(diagnostic(check)), diagnostic(check))
            self.assertLess(len(json.dumps(diagnostic(check)).encode()), 512)
        self.assertEqual(W.validate_report(diagnostic()), diagnostic())
        bad = [dict(diagnostic(), failed_checks=SENTINEL),
               dict(diagnostic(), failed_checks=[SENTINEL]),
               dict(diagnostic(), failed_checks=['tty_identity', 'cpu_max']),
               dict(diagnostic(), failed_checks=[True]), dict(diagnostic(), failed_checks={}),
               dict(diagnostic(), observations={}), dict(diagnostic(), error=SENTINEL),
               dict(diagnostic(), secret_entry_authorized=True),
               dict(diagnostic(), runtime_crash_suppression_qualified=True),
               dict(diagnostic(), checks_passed=False), dict(diagnostic('cpu_max'), checks_passed=True)]
        for report in bad:
            with self.subTest(report_index=bad.index(report)), self.assertRaises(W.Rejected):
                W.validate_report(report)

    def test_diagnostic_scope_differs_only_in_fixed_internal_flag(self):
        normal = W.scope_command('1:2')
        expected = [part.replace(' --scoped ', ' --scoped-diagnostic ') for part in normal]
        self.assertEqual(W.scope_command('1:2', True), expected)

    def test_early_wrapper_failure_is_symbolic_and_stops_scope(self):
        for guard, check in (('require_console', 'tty_identity'), ('require_host', 'host_context')):
            code, helper, run, reports, errors, _ = wrapper_tests.FlowTests().exercise(
                args=('--diagnostic',), guard_failure=guard)
            self.assertEqual(code, 1)
            self.assertEqual(reports[-1], diagnostic(check))
            self.assertNotIn('SYNTHETIC_PRIVATE_DETAIL', errors)
            run.assert_not_called()
            helper.assert_not_called()

    def test_diagnostic_plan_failure_and_valid_scoped_reports(self):
        code, _, run, reports, _, _ = wrapper_tests.FlowTests().exercise(args=('--diagnostic',), plan_pass=False)
        self.assertEqual(code, 1)
        run.assert_not_called()
        self.assertEqual(reports[-1], diagnostic('plan_preflight'))
        for candidate, status in ((diagnostic(), 0), (diagnostic('memory_max'), 1)):
            code, _, _, reports, _, _ = wrapper_tests.FlowTests().exercise(
                args=('--diagnostic',), candidate=candidate, scope_code=status)
            self.assertEqual(code, status)
            self.assertEqual(reports[-1], candidate)

    def test_scoped_payload_or_status_mismatch_becomes_fixed_validation_id(self):
        for candidate, status in ((dict(diagnostic(), detail=SENTINEL), 0), (diagnostic(), 1)):
            code, _, _, reports, errors, _ = wrapper_tests.FlowTests().exercise(
                args=('--diagnostic',), candidate=candidate, scope_code=status)
            self.assertEqual(code, 1)
            self.assertEqual(reports[-1], diagnostic('report_validation'))
            self.assertNotIn(SENTINEL, json.dumps(reports[-1]) + errors)

    def test_diagnostic_path_does_not_replace_ordinary_result_path(self):
        self.assertEqual(str(W.DIAGNOSTIC_RESULT), '/var/tmp/ai-invest-operator-diagnostic.json')
        wrapper_tests.FlowTests().exercise(args=('--diagnostic',), plan_pass=False)
        self.assertEqual(W.RESULT, W.DIAGNOSTIC_RESULT)
        wrapper_tests.FlowTests().exercise(plan_pass=False)
        self.assertEqual(W.RESULT, W.ORDINARY_RESULT)


if __name__ == '__main__':
    unittest.main()
