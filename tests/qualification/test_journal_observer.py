"""Focused observer regressions. Fixtures are public, never a runtime canary."""
import hashlib
import inspect
import json
import subprocess
import unittest
from unittest.mock import Mock, patch
from test_crash_canary import H, W, ROOT
import test_crash_observation as previous
from test_crash_observation import Reader, observation, entry, FIXTURE, BOOT


class JournalDiagnosticsTests(unittest.TestCase):
    def run_reader(self, reader, end=2):
        obj = observation(reader)
        with patch.object(H.time, 'monotonic', return_value=1.5):
            try:
                answer = obj.journal(123, FIXTURE, end)
            except H.JournalIncomplete:
                answer = ('NOT_TESTED', True)
        return answer, obj.journal_diagnostic

    def failure(self, reader, stage, reason):
        answer, diagnostic = self.run_reader(reader)
        self.assertEqual(answer, ('NOT_TESTED', True))
        self.assertEqual(diagnostic, {'journal_stage': stage, 'journal_reason': reason})
        report = H.report({'journal': answer[0], **diagnostic})
        self.assertEqual(H.validate(report), report)
        self.assertEqual(W.validate_report(report), report)
        for forbidden in ('UNPUBLISHED', FIXTURE.decode(), BOOT):
            self.assertNotIn(forbidden, json.dumps(report))
        self.assertFalse(report['secret_entry_authorized'])
        self.assertFalse(report['runtime_crash_suppression_qualified'])

    def test_each_api_operation_is_identified_without_exception_text(self):
        cases = [('process', 'initial_change'), ('seek_cursor', 'cursor_restore'),
                 ('test_cursor', 'cursor_restore'), ('add_match', 'filters'),
                 ('add_disjunction', 'filters'), ('seek_monotonic', 'seek'),
                 ('_get_monotonic', 'timestamp_boot'), ('_get', 'field_read')]
        for method, stage in cases:
            with self.subTest(method=method):
                reader = Reader([(1500000, entry())])
                setattr(reader, method, Mock(side_effect=OSError('UNPUBLISHED_DETAIL')))
                self.failure(reader, stage, 'api_error')
        reader = Reader()
        reader._next = Mock(side_effect=[True, OSError('UNPUBLISHED')])
        self.failure(reader, 'iteration', 'api_error')
        reader = Reader()
        reader.process = Mock(side_effect=[0, OSError('UNPUBLISHED')])
        self.failure(reader, 'final_change', 'api_error')

    def test_initial_invalidation_or_unsupported_state(self):
        for state, reason in ((2, 'invalidation'), (3, 'unexpected_representation'),
                              ('UNPUBLISHED', 'unexpected_representation')):
            reader = Reader()
            reader.process = Mock(return_value=state)
            self.failure(reader, 'initial_change', reason)

    def test_anchor_unavailable(self):
        for method in ('_next', 'test_cursor'):
            reader = Reader()
            setattr(reader, method, Mock(return_value=False))
            self.failure(reader, 'cursor_restore', 'anchor_unavailable')

    def test_final_invalidation_and_append_at_eof_and_later_timestamp_reg_j01_j02(self):
        for entries in ([], [(2000001, entry())]):
            for state, reason in ((2, 'invalidation'), (1, 'append_pending')):
                reader = Reader(entries)
                reader.process = Mock(side_effect=[0, state])
                self.failure(reader, 'final_change', reason)

    def test_valid_empty_and_matching_are_complete(self):
        for rows, expected in (([], ('PASS', False)),
                               ([(1500000, entry())], ('PASS', True))):
            reader = Reader(rows)
            reader.process = Mock(side_effect=[1, 0])
            result, diagnostic = self.run_reader(reader)
            self.assertEqual(result, expected)
            self.assertEqual(diagnostic, {'journal_stage': 'complete', 'journal_reason': 'complete'})

    def test_time_boundaries_are_inclusive(self):
        for stamp in (1000000, 2000000):
            self.assertEqual(self.run_reader(Reader([(stamp, entry())]))[0], ('PASS', True))
        self.failure(Reader([(999999, entry())]), 'timestamp_boot', 'record_before_window')
        self.assertEqual(self.run_reader(Reader([(2000001, entry())]))[0], ('PASS', False))

    def test_monotonic_representation_and_boot(self):
        for value in ((1.5, bytes.fromhex(BOOT)), (1500000, BOOT), None,
                      (1500000,), [1500000, bytes.fromhex(BOOT)]):
            reader = Reader([(1500000, entry())])
            reader._get_monotonic = Mock(return_value=value)
            self.failure(reader, 'timestamp_boot', 'unexpected_representation')
        reader = Reader([(1500000, entry())])
        reader._get_monotonic = Mock(return_value=(1500000, bytes.fromhex('b' * 32)))
        self.failure(reader, 'timestamp_boot', 'record_boot_mismatch')

    def test_missing_required_boot_and_wrong_attribution(self):
        value = entry()
        del value['_BOOT_ID']
        self.failure(Reader([(1500000, value)]), 'attribution', 'incomplete_field')
        for value in (entry(_BOOT_ID=b'wrong'), {'_BOOT_ID': BOOT.encode(), '_PID': b'999'}):
            self.failure(Reader([(1500000, value)]), 'attribution', 'attribution_mismatch')

    def test_optional_missing_field_is_not_api_error(self):
        self.assertEqual(self.run_reader(Reader([(1500000, {
            '_BOOT_ID': BOOT.encode(), 'COREDUMP_PID': b'123'})]))[0], ('PASS', True))

    def test_field_shape_and_threshold(self):
        for value in ('UNPUBLISHED', [b'UNPUBLISHED'], None):
            self.failure(Reader([(1500000, entry(MESSAGE=value))]),
                         'field_shape', 'unexpected_representation')
        self.failure(Reader([(1500000, entry(MESSAGE=b'x' * (H.MAX_FIELD - 8)))]),
                     'field_shape', 'incomplete_field')

    def test_positive_prefix_survives_truncation_or_later_failure(self):
        for value in (FIXTURE, FIXTURE.hex().encode(), FIXTURE + b'x' * H.MAX_FIELD):
            reader = Reader([(1500000, entry(MESSAGE=value))])
            reader.process = Mock(side_effect=[0, OSError('UNPUBLISHED')])
            answer, diagnostic = self.run_reader(reader)
            self.assertEqual(answer, ('FAIL', True))
            self.assertEqual(diagnostic['journal_reason'], 'positive_match')
            self.assertEqual(reader.process.call_count, 1)

    def test_record_byte_and_time_budgets_are_distinct(self):
        self.failure(Reader([(1500000, entry())] * 256), 'budget', 'record_limit')
        with patch.object(H, 'MAX_OBSERVATION', 1):
            self.failure(Reader([(1500000, entry())]), 'budget', 'byte_limit')
        obj = observation(Reader())
        with patch.object(H.time, 'monotonic', side_effect=[1, 4]):
            with self.assertRaises(H.JournalIncomplete):
                obj.journal(123, FIXTURE, 2)
        self.assertEqual(obj.journal_diagnostic, {'journal_stage': 'budget', 'journal_reason': 'time_limit'})

    def test_finish_keeps_actionable_diagnostic_and_later_positive(self):
        obj = observation(Reader())
        obj.reader.process = Mock(return_value=2)
        obj.apport = Mock(return_value=('FAIL', True))
        obj.store_events = Mock(side_effect=OSError('UNPUBLISHED'))
        with patch.object(H.time, 'monotonic', side_effect=[2, 12, 12, 12]), \
             patch.object(H.time, 'time', return_value=111):
            result = obj.finish(123, FIXTURE)
        self.assertEqual(result['journal'], 'NOT_TESTED')
        self.assertEqual(result['journal_stage'], 'initial_change')
        self.assertEqual(result['journal_reason'], 'invalidation')
        self.assertEqual(result['collector_retention'], 'FAIL')
        self.assertNotIn('UNPUBLISHED', json.dumps(H.report(result)))

    def test_allowlists_identical_and_arbitrary_values_rejected(self):
        self.assertEqual(H.JOURNAL_STAGES, W.JOURNAL_STAGES)
        self.assertEqual(H.JOURNAL_REASONS, W.JOURNAL_REASONS)
        for key in ('journal_stage', 'journal_reason'):
            report = H.report()
            report['results'][key] = 'UNPUBLISHED'
            with self.assertRaises(H.Refused): H.validate(report)
            with self.assertRaises(W.Rejected): W.validate_report(report)

    def test_nonjournal_security_paths_byte_identical(self):
        old = subprocess.run(['/usr/bin/git', 'show',
            '55339d0a222d95f8b58cf373d1de14f4a51bea88:scripts/qualification/run_operator_preflight.py'],
            capture_output=True, check=True, cwd=ROOT, timeout=10).stdout.decode()
        for function in (W.checked_path, W.checked_bytes, W.require_operator_environment,
                         W.require_operator_identity, W.scope_command):
            self.assertIn(inspect.getsource(function), old)


class BootTimeTests(unittest.TestCase):
    def test_three_failures_publish_only_fixed_reasons(self):
        cases = [(Reader([(999999, entry())]), 2, 'record_before_window'),
                 (Reader(), 0.5, 'invalid_observation_interval')]
        wrong_boot = Reader([(1500000, entry())])
        wrong_boot._get_monotonic = Mock(return_value=(1500000, bytes.fromhex('b' * 32)))
        cases.append((wrong_boot, 2, 'record_boot_mismatch'))
        for reader, end, reason in cases:
            obj = observation(reader)
            with patch.object(H.time, 'monotonic', return_value=1.5):
                with self.assertRaises(H.JournalIncomplete):
                    obj.journal(123, FIXTURE, end)
            self.assertEqual(obj.journal_diagnostic['journal_reason'], reason)
            value = H.report(obj.journal_diagnostic)
            self.assertEqual(H.validate(value), W.validate_report(value))
            self.assertFalse(value['secret_entry_authorized'])
            self.assertFalse(value['runtime_crash_suppression_qualified'])
            self.assertEqual(reader.payload_reads, 0)
            for private in (BOOT, FIXTURE.decode(), 'UNPUBLISHED', '1500000'):
                self.assertNotIn(private, json.dumps(value))

    def test_reversal_checked_once_before_seek_even_when_integer_bounds_equal(self):
        obj = observation(Reader())
        obj.start = 1.0000009
        obj.reader.seek_monotonic = Mock()
        with self.assertRaises(H.JournalIncomplete):
            obj.journal(123, FIXTURE, 1.0000001)
        obj.reader.seek_monotonic.assert_not_called()
        self.assertEqual(obj.journal_diagnostic, {
            'journal_stage': 'seek', 'journal_reason': 'invalid_observation_interval'})

    def test_seconds_to_microseconds_and_inclusive_fractional_boundaries(self):
        for stamp in (123456123456, 123457123456):
            reader = Reader([(stamp, entry(MESSAGE=FIXTURE))])
            original = reader.seek_monotonic
            reader.seek_monotonic = Mock(side_effect=original)
            obj = observation(reader)
            obj.start = 123456.1234567
            self.assertEqual(obj.journal(123, FIXTURE, 123457.1234567), ('FAIL', True))
            reader.seek_monotonic.assert_called_once_with(123456123456, BOOT)

    def test_zero_width_inclusive_interval(self):
        obj = observation(Reader([(1000000, entry(MESSAGE=FIXTURE))]))
        self.assertEqual(obj.journal(123, FIXTURE, 1.0), ('FAIL', True))

    def test_header_boot_is_not_inferred_from_matching_payload_field(self):
        reader = Reader([(1500000, entry(MESSAGE=FIXTURE))])
        reader._get_monotonic = Mock(return_value=(1500000, bytes.fromhex('b' * 32)))
        with self.assertRaises(H.JournalIncomplete):
            observation(reader).journal(123, FIXTURE, 2)
        self.assertEqual(reader.payload_reads, 0)

    def test_early_record_stays_incomplete_not_absence_or_skipped_positive(self):
        reader = Reader([(999999, entry()), (1500000, entry(MESSAGE=FIXTURE))])
        obj = observation(reader)
        with self.assertRaises(H.JournalIncomplete):
            obj.journal(123, FIXTURE, 2)
        self.assertEqual(obj.journal_diagnostic['journal_reason'], 'record_before_window')
        self.assertEqual(reader.payload_reads, 0)

    def test_all_three_new_reasons_allowed_but_no_raw_extensions(self):
        for reason in ('record_boot_mismatch', 'record_before_window', 'invalid_observation_interval'):
            report = H.report({'journal_stage': 'timestamp_boot', 'journal_reason': reason})
            self.assertEqual(W.validate_report(report), report)
            report['results']['journal_reason'] = reason + ':UNPUBLISHED'
            with self.assertRaises(W.Rejected):
                W.validate_report(report)

    def test_nonjournal_protection_and_clock_origin_unchanged(self):
        old = subprocess.run(['/usr/bin/git', 'show',
            '24310834bf00b66273eb89c04cf88d41e8d97758:scripts/qualification/crash_canary.py'],
            capture_output=True, check=True, cwd=ROOT, timeout=10).stdout.decode()
        for function in (H.Observation.__init__, H.Observation.setup_journal,
                         H.Observation.finish, H.runtime_limits, H.protect, H.root_path):
            self.assertIn(inspect.getsource(function), old)


class BootTimeCheckpointTests(previous.CheckpointTests):
    def text(self):
        return (ROOT / 'docs/qualification/BOOT_TIME_CHECKPOINT.md').read_text()

    def test_current_hashes_and_prior_evidence_preserved(self):
        text = self.text()
        for path in ('scripts/qualification/crash_canary.py', 'scripts/qualification/run_operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            self.assertIn(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), text)
        self.assertIn('/var/tmp/ai-invest-crash-journal.json', text)
        self.assertNotIn('unlink -- /var/tmp', text)


class NativeBindingTests(unittest.TestCase):
    def test_installed_binding_against_eleven_private_native_journal_cases(self):
        result = subprocess.run(['/usr/bin/python3', '-I', '-B',
            str(ROOT / 'tests/qualification/fixture_journal_api.py')],
            capture_output=True, timeout=15, env=W.CLEAN_ENV)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b'')
        value = json.loads(result.stdout)
        if value == {'status': 'UNSUPPORTED'}:
            self.skipTest('Pinned unprivileged v255 native fixture ABI unavailable')
        self.assertEqual(value.get('status'), 'PASS')
        self.assertEqual(len(value['cases']), 11)
        self.assertEqual(set(value['cases'].values()), {'PASS'})
        self.assertEqual(len(value['boundaries']), 24)
        self.assertEqual(set(value['boundaries'].values()), {'PASS'})


class CheckpointTests(previous.CheckpointTests):
    def text(self):
        return (ROOT / 'docs/qualification/JOURNAL_CHECKPOINT.md').read_text()

    def test_current_hashes_and_prior_evidence_preserved(self):
        text = self.text()
        for path in ('scripts/qualification/crash_canary.py', 'scripts/qualification/run_operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            original = subprocess.run(['/usr/bin/git', 'show',
                '24310834bf00b66273eb89c04cf88d41e8d97758:' + path],
                cwd=ROOT, capture_output=True, check=True, timeout=10).stdout
            self.assertIn(hashlib.sha256(original).hexdigest(), text)
        self.assertIn('/var/tmp/ai-invest-crash-log-source.json', text)
        self.assertNotIn('unlink -- /var/tmp', text)


if __name__ == '__main__':
    unittest.main()
