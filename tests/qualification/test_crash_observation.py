"""Isolated harmless fixtures only; never opens host logs or generates a canary."""
import inspect
import hashlib
import json
import re
import signal
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_crash_canary import H, W, ROOT

FIXTURE = b'harmless-observation-fixture'
BOOT = 'a' * 32


class Reader:
    def __init__(self, entries=()):
        self.entries = iter(entries)
        self.anchor = True
        self.matches = []
        self.payload_reads = 0
    def process(self): return 0
    def seek_cursor(self, cursor): pass
    def test_cursor(self, cursor): return True
    def add_match(self, value): self.matches.append(value)
    def add_disjunction(self): self.matches.append('OR')
    def seek_monotonic(self, stamp, boot): self.anchor = False
    def _next(self):
        if self.anchor: return True
        self.current = next(self.entries, None)
        return self.current is not None
    def _get_monotonic(self): return self.current[0], bytes.fromhex(BOOT)
    def _get(self, key):
        self.payload_reads += 1
        return self.current[1][key]


def observation(reader=None):
    obj = H.Observation.__new__(H.Observation)
    obj.reader, obj.boot, obj.anchor = reader, BOOT, 'inert-cursor'
    obj.start, obj.wall, obj.ready = 1.0, 100.0, True
    obj.log, obj.watch_fd = H.LogSource(), None
    return obj


def entry(**changes):
    value = {'_BOOT_ID': BOOT.encode(), 'COREDUMP_PID': b'123', '_PID': b'999', 'MESSAGE': b'no match'}
    value.update(changes)
    return value


class DetectorTests(unittest.TestCase):
    def test_positive_raw_hex_and_negative_fixtures(self):
        for data in (FIXTURE, b'prefix' + FIXTURE + b'suffix', FIXTURE.hex().encode()):
            self.assertTrue(H.contains(FIXTURE, data))
            self.assertTrue(H.journal_entry(entry(MESSAGE=data), H.journal_groups(BOOT, 44, 123), FIXTURE)[0])
        self.assertFalse(H.contains(FIXTURE, b'negative fixture'))

    def test_collector_other_pid_is_attributable(self):
        self.assertEqual(H.journal_entry(entry(), H.journal_groups(BOOT, 44, 123), FIXTURE), (False, True))

    def test_wrong_boot_or_unattributed_entry_rejected(self):
        for value in (entry(_BOOT_ID=b'wrong'), {'_BOOT_ID': BOOT.encode(), '_PID': b'999'}):
            with self.assertRaises(H.Refused):
                H.journal_entry(value, H.journal_groups(BOOT, 44, 123), FIXTURE)

    def test_threshold_counts_field_name_and_separator_reg_ob01(self):
        for value in (b'x' * (H.MAX_FIELD - len('MESSAGE') - 1), [b'duplicate'], 'text'):
            with self.assertRaises(H.Refused):
                H.journal_entry(entry(MESSAGE=value), H.journal_groups(BOOT, 44, 123), FIXTURE)

    def test_apport_attribution_positive_and_negative(self):
        prefix = b'ERROR: apport (pid 999) Wed Sep 9 12:00:00 2026: '
        target = b'host pid 123 crashed in a separate mount namespace, ignoring'
        self.assertEqual(H.apport_records(prefix + target + b' ' + FIXTURE + b'\n', 123, FIXTURE), (True, False))
        self.assertEqual(H.apport_records(prefix + target + b'\n', 123, FIXTURE), (False, False))
        self.assertEqual(H.apport_records(b'', 123, FIXTURE), (False, True))

    def test_collector_pid_does_not_attribute_unrelated_lines_reg_ob02(self):
        prefix = b'ERROR: apport (pid 999) Wed Sep 9 12:00:00 2026: '
        rows = prefix + b'called for global pid 123, signal 6\n' + prefix + FIXTURE + b'\n'
        with patch.object(H, 'contains', wraps=H.contains) as detector:
            self.assertEqual(H.apport_records(rows, 123, FIXTURE), (False, False))
            self.assertNotIn(FIXTURE, [call.args[1] for call in detector.call_args_list])

    def test_partial_malformed_or_oversize_apport_not_absence(self):
        self.assertEqual(H.apport_records(b'partial', 123, FIXTURE), (False, False))
        with self.assertRaises(H.Refused): H.apport_records(b'x' * (H.MAX_OBSERVATION + 1), 123, FIXTURE)
        self.assertEqual(H.apport_records(b'unsupported\n', 123, FIXTURE), (False, False))

    def test_target_match_survives_partial_final_line_reg_ob04(self):
        data = b'ERROR: apport (pid 999) Wed Sep 9 12:00:00 2026: called for global pid 123, signal 6 ' + FIXTURE + b'\npartial'
        self.assertEqual(H.apport_records(data, 123, FIXTURE), (True, False))


class JournalTests(unittest.TestCase):
    def run_reader(self, reader, end=2):
        with patch.object(H.time, 'monotonic', return_value=1.5):
            return observation(reader).journal(123, FIXTURE, end)

    def test_fixed_fields_no_error_suppressing_get_all_reg_ob03(self):
        source = inspect.getsource(H.Observation.journal)
        self.assertNotIn('._get_all(', source)
        self.assertIn('reader._get(key)', source)
        self.assertEqual(self.run_reader(Reader([(1500000, entry())])), ('PASS', True))

    def test_empty_complete_filtered_interval(self):
        self.assertEqual(self.run_reader(Reader()), ('PASS', False))

    def test_each_match_group_binds_boot(self):
        reader = Reader()
        self.run_reader(reader)
        self.assertEqual(reader.matches.count('_BOOT_ID=' + BOOT), 7)
        self.assertEqual(reader.matches.count('OR'), 6)
        self.assertIn('COREDUMP_PID=123', reader.matches)
        self.assertIn('OBJECT_PID=123', reader.matches)

    def test_read_failure_not_absence(self):
        reader = Reader([(1500000, entry())])
        reader._get = Mock(side_effect=OSError('UNPUBLISHED_DETAIL'))
        with self.assertRaises(OSError): self.run_reader(reader)

    def test_detected_match_cannot_be_erased_by_later_failure(self):
        reader = Reader([(1500000, entry(MESSAGE=FIXTURE)), (1500001, {})])
        self.assertEqual(self.run_reader(reader), ('FAIL', True))

    def test_before_window_wrong_boot_rejected_after_window_not_read(self):
        with self.assertRaises(H.Refused): self.run_reader(Reader([(999999, entry())]))
        reader = Reader([(2000001, entry(MESSAGE=FIXTURE))])
        self.assertEqual(self.run_reader(reader), ('PASS', False))
        self.assertEqual(reader.payload_reads, 0)
        reader = Reader([(1500000, entry())])
        reader._get_monotonic = Mock(return_value=(1500000, b'wrong'))
        with self.assertRaises(H.Refused): self.run_reader(reader)

    def test_rotation_anchor_loss_and_entry_cap_incomplete(self):
        for attribute, value in (('process', 2), ('test_cursor', False)):
            reader = Reader()
            setattr(reader, attribute, Mock(return_value=value))
            with self.assertRaises(H.Refused): self.run_reader(reader)
        with self.assertRaises(H.Refused): self.run_reader(Reader([(1500000, entry())] * 256))

    def test_observation_query_timeout(self):
        with patch.object(H.time, 'monotonic', side_effect=[1, 4]):
            with self.assertRaises(H.Refused): observation(Reader()).journal(123, FIXTURE, 2)


class ObservationTests(unittest.TestCase):
    def test_sticky_exception_is_exact_root_owned_crash_directory(self):
        def run(target, owner=0, parent_writable=False):
            def metadata(path):
                mode = stat.S_IFDIR | (0o1777 if path == target else 0o777 if parent_writable else 0o755)
                return SimpleNamespace(st_uid=owner if path == target else 0, st_mode=mode)
            with patch.object(H.Path, 'resolve', lambda path, strict=True: path), \
                 patch.object(H.Path, 'lstat', metadata):
                return H.root_path(target, directory=True, sticky=True)
        self.assertIsNotNone(run(Path('/var/crash')))
        for target, owner, parent in ((Path('/other'), 0, False), (Path('/var/crash'), 1000, False), (Path('/var/crash'), 0, True)):
            with self.assertRaises(H.Refused): run(target, owner, parent)

    def test_symlink_root_path_rejected(self):
        with patch.object(H.Path, 'resolve', return_value=Path('/different')):
            with self.assertRaises(H.Refused): H.root_path('/var/crash', directory=True, sticky=True)

    def finish(self, journal=('PASS', False), apport=('PASS', False), store='PASS'):
        obj = observation()
        obj.journal = Mock(side_effect=journal if isinstance(journal, BaseException) else None, return_value=journal)
        obj.apport = Mock(return_value=apport)
        obj.store_events = Mock(return_value=store)
        with patch.object(H.time, 'monotonic', side_effect=[2, 12, 12]), \
             patch.object(H.time, 'time', return_value=111):
            return obj.finish(123, FIXTURE)

    def test_finite_complete_window_flags_still_false(self):
        value = H.report(self.finish())
        self.assertEqual(value['results']['collector_retention'], 'PASS')
        self.assertFalse(value['checks_passed'])
        self.assertFalse(value['secret_entry_authorized'])
        self.assertFalse(value['runtime_crash_suppression_qualified'])
        self.assertNotIn(FIXTURE.decode(), json.dumps(value))

    def test_observation_failure_remains_incomplete_without_exception(self):
        value = self.finish(journal=OSError('UNPUBLISHED_DETAIL'))
        self.assertEqual(value['journal'], 'NOT_TESTED')
        self.assertEqual(value['collector_retention'], 'NOT_TESTED')
        self.assertNotIn('UNPUBLISHED_DETAIL', json.dumps(value))

    def test_activation_or_store_activity_never_retention_pass(self):
        for kwargs in ({'journal': ('PASS', True)}, {'apport': ('NOT_TESTED', True)}, {'store': 'NOT_TESTED'}):
            self.assertEqual(self.finish(**kwargs)['collector_retention'], 'NOT_TESTED')

    def test_detected_leak_fails(self):
        self.assertEqual(self.finish(journal=('FAIL', True))['collector_retention'], 'FAIL')

    def test_clock_step_or_delayed_window_incomplete(self):
        for sequence, wall in (([2, 12, 12], 500), ([2, 15, 15], 114)):
            with patch.object(H.time, 'monotonic', side_effect=sequence), patch.object(H.time, 'time', return_value=wall):
                with self.assertRaises(H.Refused): observation().finish(123, FIXTURE)

    def test_unavailable_initial_observation_no_false_pass(self):
        obj = observation()
        obj.ready = False
        self.assertEqual(set(obj.finish(123, FIXTURE).values()), {'NOT_TESTED'})

    def test_store_events_no_artifact_content_reads(self):
        obj = observation()
        obj.stores = []
        for event in (b'mutation', b'overflow'):
            with patch.object(H.os, 'read', return_value=event):
                self.assertEqual(obj.store_events(), 'NOT_TESTED')
        with patch.object(H.os, 'read', side_effect=BlockingIOError()):
            self.assertEqual(obj.store_events(), 'PASS')
        self.assertNotIn('open(', inspect.getsource(H.Observation.store_events))

    def test_log_rotation_truncation_rewrite_and_short_read(self):
        def info(size=10, ino=1, stamp=1):
            return SimpleNamespace(st_dev=1, st_ino=ino, st_size=size, st_mtime_ns=stamp,
                                   st_ctime_ns=stamp, st_mode=stat.S_IFREG | 0o640, st_uid=0)
        obj = observation()
        obj.log.info, obj.log.fd = info(), 5
        for current in (info(9), info(10, 2), info(10, stamp=2), info(11, stamp=2)):
            with patch.object(obj.log, 'verify_directory'), patch.object(obj.log, 'verify_file', return_value=current), \
                 patch.object(H.os, 'fstat', return_value=current), \
                 patch.object(H.os, 'pread', return_value=b''):
                try:
                    result = obj.apport(123, FIXTURE)
                except H.Refused:
                    continue
                self.assertEqual(result, ('NOT_TESTED', True))

    def test_close_is_idempotent_and_closes_only_owned_fds(self):
        obj = observation(Mock())
        obj.log.fd, obj.watch_fd = 7, 8
        with patch.object(H.os, 'close') as close:
            obj.close(); obj.close()
            self.assertEqual([call.args for call in close.call_args_list], [(7,), (8,)])

    def test_zombie_held_and_canary_lifetime_source(self):
        source = inspect.getsource(H.trial)
        self.assertLess(source.index('Observation()'), source.index('os.getrandom(32)'))
        self.assertLess(source.index('wait_exit('), source.index('observation.finish('))
        self.assertLess(source.index('observation.finish('), source.index('status = wait_child('))
        child = source.split('if child == 0:')[1].split('child_fd =')[0]
        self.assertIn('detach(-1)', child)
        self.assertNotIn('observation.close()', child)
        self.assertLess(child.index('detach(-1)'), child.index('os.kill('))
        self.assertLess(H.OBSERVATION_SECONDS + 12, H.DEADLINE)

    def test_wait_exit_nonreaping_timeout_and_identity(self):
        with patch.object(H.time, 'monotonic', return_value=1), \
             patch.object(H.os, 'waitid', return_value=SimpleNamespace(si_pid=123)) as wait:
            H.wait_exit(123, 2)
            self.assertEqual(wait.call_args.args[2] & H.os.WNOWAIT, H.os.WNOWAIT)
        with patch.object(H.time, 'monotonic', return_value=3):
            with self.assertRaises(H.Refused): H.wait_exit(123, 2)

    def test_journal_change_watch_established_before_anchor_reg_ob05(self):
        source = inspect.getsource(H.Observation.setup_journal)
        self.assertIn('require(self.reader.fileno() >= 0)', source)
        self.assertLess(source.index('self.reader.fileno()'), source.index('self.reader.seek_tail()'))
        self.assertLess(source.index('self.reader.fileno()'), source.index('self.anchor ='))

    def test_unavailable_journal_change_watch_closes_without_host_read(self):
        for failure in (-1, OSError('UNPUBLISHED_WATCH_FAILURE')):
            reader = Mock()
            reader.fileno = Mock(return_value=failure, side_effect=failure if isinstance(failure, Exception) else None)
            binding = SimpleNamespace(_Reader=Mock(return_value=reader), LOCAL_ONLY=1, SYSTEM=4)
            with patch.dict(sys.modules, {'systemd': SimpleNamespace(_reader=binding)}), \
                 patch.object(H, 'bounded_read', return_value=BOOT.encode()), \
                 patch.object(H.LogSource, 'setup_directory'), patch.object(H.LogSource, 'setup_file'), \
                 patch.object(H.Observation, 'setup_store'), \
                 patch.object(H, 'root_path') as path:
                obj = H.Observation()
                self.assertFalse(obj.ready)
                path.assert_not_called()
                obj.close()
                reader.close.assert_called_once()

    def test_scope_and_result_remain_fixed(self):
        policy = (ROOT / 'infrastructure/qualification/ai-invest-operator.sudoers').read_text()
        self.assertEqual(policy.count('/usr/local/sbin/ai-invest-operator-preflight'), 2)
        self.assertNotIn('NOPASSWD', policy)
        self.assertEqual(str(W.CRASH_RESULT), '/var/tmp/ai-invest-crash-log-source.json')
        self.assertIn('os.O_EXCL', inspect.getsource(W))


class CheckpointTests(unittest.TestCase):
    def text(self):
        return (ROOT / 'docs/qualification/OBSERVATION_CHECKPOINT.md').read_text()

    def test_current_hashes_and_prior_evidence_preserved(self):
        text = self.text()
        for path in ('scripts/qualification/crash_canary.py', 'scripts/qualification/run_operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            original = subprocess.run(['/usr/bin/git', 'show',
                '531671a5e6e3bf8c7efc3bddb899c53d53cd1c27:' + path],
                cwd=ROOT, capture_output=True, check=True, timeout=10).stdout
            self.assertIn(hashlib.sha256(original).hexdigest(), text)
        self.assertNotIn('unlink -- /var/tmp', text)
        self.assertIn('/var/tmp/ai-invest-crash-qualification.json', text)

    def test_all_checkpoint_shell_blocks_parse_without_execution(self):
        blocks = re.findall(r'```bash\n(.*?)```', self.text(), re.S)
        self.assertEqual(len(blocks), 4)
        for block in blocks:
            result = subprocess.run(['/bin/bash', '-n'], input=block, text=True,
                capture_output=True, timeout=10, env=W.CLEAN_ENV)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_activation_each_failure_and_rollback_failure(self):
        script, = re.findall(r"sudo /bin/sh -c '\n(.*?)\n  '", self.text(), re.S)
        self.assertNotRegex(script, r'\bsudo\b')
        for name in ('/usr/bin/install', '/usr/bin/mv', '/usr/sbin/visudo'):
            script = script.replace(name, 'fake_command')
        for fail_at in range(9):
            fixture = 'count=0\nfail_at=' + str(fail_at) + '''
fake_command() {
  count=$((count+1))
  printf "step:%s\\n" "$count"
  test "$count" -ne "$fail_at"
}
'''
            result = subprocess.run(['/bin/sh', '-c', fixture + script], text=True,
                capture_output=True, timeout=10, env=W.CLEAN_ENV)
            self.assertEqual(result.returncode, int(bool(fail_at)))
            if fail_at:
                self.assertIn('prior reviewed three-artifact state restored', result.stderr)
            else:
                self.assertEqual(len(result.stdout.splitlines()), 8)
        fixture = 'fake_command() { return 1; }\n'
        result = subprocess.run(['/bin/sh', '-c', fixture + script], text=True,
            capture_output=True, timeout=10, env=W.CLEAN_ENV)
        self.assertEqual(result.returncode, 1)
        self.assertIn('recovery requires human review', result.stderr)
        self.assertNotIn('state restored', result.stderr)


if __name__ == '__main__':
    unittest.main()
