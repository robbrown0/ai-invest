"""Isolated filesystem/metadata fixtures. No host log access, runtime RNG or crash."""
from contextlib import ExitStack
import hashlib
import inspect
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_crash_canary import H, W, ROOT
import test_crash_canary as crash_tests
import test_crash_observation as observation_tests
from test_crash_observation import FIXTURE


class LogFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ai-invest-log-source-fixture-')
        self.root = Path(self.tmp.name)
        (self.root / 'var/log').mkdir(parents=True)
        self.path = self.root / 'var/log/apport.log'
        self.path.write_bytes(b'')
        self.path.chmod(0o640)
        self.logdir = self.path.parent
        self.syslog_gid = 43110  # Fictional fixture lookup result, not host GID.
        self.metadata = {}
        self.real_stat, self.real_fstat, self.real_open = os.stat, os.fstat, os.open
        self.metadata[self.real_stat(self.root).st_ino] = {'st_mode': stat.S_IFDIR | 0o755}
        self.metadata[self.real_stat(self.root / 'var').st_ino] = {'st_mode': stat.S_IFDIR | 0o755}
        self.metadata[self.real_stat(self.logdir).st_ino] = {'st_mode': stat.S_IFDIR | 0o775, 'st_gid': self.syslog_gid}
        self.metadata[self.real_stat(self.path).st_ino] = {'st_gid': 43111}  # adm fixture
        self.calls = []
        self.stack = ExitStack()
        self.stack.enter_context(patch.object(H.grp, 'getgrnam', side_effect=lambda name:
            SimpleNamespace(gr_gid={'root': 0, 'syslog': self.syslog_gid}[name])))
        self.stack.enter_context(patch.object(H.os, 'stat', side_effect=self.mock_stat))
        self.stack.enter_context(patch.object(H.os, 'fstat', side_effect=lambda fd: self.convert(self.real_fstat(fd))))
        self.stack.enter_context(patch.object(H.os, 'open', side_effect=self.mock_open))
        self.source = H.LogSource()

    def convert(self, info):
        values = {key: getattr(info, key) for key in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns',
                  'st_ctime_ns', 'st_mode', 'st_nlink', 'st_gid', 'st_mtime', 'st_atime', 'st_ctime')}
        values['st_uid'] = 0
        values.update(self.metadata.get(info.st_ino, {}))
        return SimpleNamespace(**values)

    def mock_stat(self, path, *, dir_fd=None, follow_symlinks=True):
        return self.convert(self.real_stat(self.root if path == '/' else path,
            dir_fd=dir_fd, follow_symlinks=follow_symlinks))

    def mock_open(self, path, flags, mode=0o777, *, dir_fd=None):
        self.calls.append((path, flags, dir_fd))
        return self.real_open(self.root if path == '/' else path, flags, mode, dir_fd=dir_fd)

    def setup_source(self):
        self.source.setup_directory()
        self.source.setup_file()

    def tearDown(self):
        try:
            self.source.close()
        finally:
            self.stack.close()
            self.tmp.cleanup()

    def change(self, path, **values):
        self.metadata.setdefault(self.real_stat(path).st_ino, {}).update(values)

    def test_observed_root_syslog_775_and_root_adm_640(self):
        self.setup_source()
        self.assertEqual(self.source.observe(123, FIXTURE), ('PASS', False))
        self.assertEqual([call[0] for call in self.calls], ['/', 'var', 'log', 'apport.log'])
        self.assertTrue(all(flags & os.O_NOFOLLOW and flags & os.O_CLOEXEC for _, flags, _ in self.calls))
        self.assertTrue(all(flags & os.O_DIRECTORY for _, flags, _ in self.calls[:3]))
        self.assertTrue(self.calls[-1][1] & os.O_NONBLOCK)
        self.assertEqual(self.calls[-1][2], self.source.chain[-1][0])

    def test_reject_unapproved_log_owner_group_modes(self):
        cases = ({'st_uid': 1000}, {'st_gid': 12345}, {'st_gid': 0},
                 {'st_mode': stat.S_IFDIR | 0o777}, {'st_mode': stat.S_IFDIR | 0o1775},
                 {'st_mode': stat.S_IFDIR | 0o2775}, {'st_mode': stat.S_IFDIR | 0o770})
        initial = dict(self.metadata[self.real_stat(self.logdir).st_ino])
        for values in cases:
            self.metadata[self.real_stat(self.logdir).st_ino] = {**initial, **values}
            with self.assertRaises(H.Refused): self.source.setup_directory()
            self.source.close()

    def test_strict_root_owned_755_log_directory_supported(self):
        self.change(self.logdir, st_gid=0, st_mode=stat.S_IFDIR | 0o755)
        self.setup_source()
        self.assertEqual(self.source.observe(123, FIXTURE), ('PASS', False))

    def test_unsafe_ancestor_outside_exception_rejected(self):
        for ancestor in (self.root, self.root / 'var'):
            self.change(ancestor, st_mode=stat.S_IFDIR | 0o775, st_gid=self.syslog_gid)
            with self.assertRaises(H.Refused): self.source.setup_directory()
            self.source.close()
            self.change(ancestor, st_mode=stat.S_IFDIR | 0o755, st_gid=0)

    def test_missing_group_lookup_never_guesses_gid(self):
        with patch.object(H.grp, 'getgrnam', side_effect=KeyError('UNPUBLISHED')):
            with self.assertRaises(KeyError): self.source.setup_directory()
        self.assertEqual(self.calls, [])

    def test_access_acl_or_unknown_acl_support_rejected(self):
        for value in (b'fictional ACL fixture', OSError(H.errno.EOPNOTSUPP, 'UNPUBLISHED'),
                      OSError(H.errno.EACCES, 'UNPUBLISHED')):
            with patch.object(H.os, 'getxattr', return_value=value,
                    side_effect=value if isinstance(value, OSError) else None):
                with self.assertRaises(H.Refused): self.source.setup_directory()
            self.source.close()

    def test_acl_change_after_setup_prevents_absence(self):
        self.setup_source()
        with patch.object(H.os, 'getxattr', return_value=b'fictional ACL fixture'):
            with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_directory_symlink_rejected_without_following(self):
        moved = self.root / 'saved-log'
        self.logdir.rename(moved)
        self.logdir.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(H.Refused): self.source.setup_directory()

    def test_file_symlink_hardlink_fifo_directory_rejected(self):
        self.source.setup_directory()
        for kind in ('symlink', 'hardlink', 'fifo', 'directory'):
            if self.path.exists(): self.path.unlink()
            target = self.root / ('target-' + kind)
            target.write_bytes(b'harmless unrelated fixture')
            if kind == 'symlink': self.path.symlink_to(target)
            elif kind == 'hardlink': os.link(target, self.path)
            elif kind == 'fifo': os.mkfifo(self.path)
            else: self.path.mkdir()
            # Rebaseline fixture directory, as if this were the initial setup.
            self.source.close(); self.source.setup_directory()
            with self.assertRaises(H.Refused): self.source.setup_file()
            if kind == 'directory': self.path.rmdir()
            else: self.path.unlink()

    def test_file_owner_write_execute_or_special_bits_rejected(self):
        self.source.setup_directory()
        initial = dict(self.metadata[self.real_stat(self.path).st_ino])
        for values in ({'st_uid': 1000}, {'st_mode': stat.S_IFREG | 0o660},
                       {'st_mode': stat.S_IFREG | 0o666}, {'st_mode': stat.S_IFREG | 0o740},
                       {'st_mode': stat.S_IFREG | 0o4640}):
            self.metadata[self.real_stat(self.path).st_ino] = {**initial, **values}
            with self.assertRaises(H.Refused): self.source.setup_file()

    def test_substitution_between_stat_and_open_fails(self):
        self.source.setup_directory()
        original = self.mock_open
        def replace(path, flags, mode=0o777, *, dir_fd=None):
            if path == 'apport.log':
                self.path.rename(self.root / 'original')
                self.path.write_bytes(b'new file')
            return original(path, flags, mode, dir_fd=dir_fd)
        with patch.object(H.os, 'open', side_effect=replace):
            with self.assertRaises(H.Refused): self.source.setup_file()

    def test_directory_replacement_rejected(self):
        self.setup_source()
        self.logdir.rename(self.root / 'original-log')
        self.logdir.mkdir()
        self.path.write_bytes(b'')
        with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_file_rotation_and_rename_back_do_not_pass(self):
        self.setup_source()
        saved = self.logdir / 'saved'
        self.path.rename(saved)
        saved.rename(self.path)
        with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_absent_baseline_creation_and_removal_not_absence_pass(self):
        self.path.unlink()
        self.setup_source()
        self.assertEqual(self.source.observe(123, FIXTURE), ('PASS', False))
        self.path.write_bytes(b'ephemeral fixture')
        self.path.unlink()
        with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_truncation_or_interrupted_read_incomplete(self):
        self.path.write_bytes(b'initial historical fixture not searched')
        self.setup_source()
        with patch.object(H.os, 'pread', side_effect=InterruptedError('UNPUBLISHED')):
            with self.assertRaises(InterruptedError): self.source.observe(123, FIXTURE)
        self.path.write_bytes(b'')
        with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_only_new_bytes_at_original_offset_read(self):
        self.path.write_bytes(b'historical fixture')
        self.setup_source()
        with patch.object(H.os, 'pread', wraps=H.os.pread) as read:
            self.assertEqual(self.source.observe(123, FIXTURE), ('PASS', False))
            read.assert_called_once_with(self.source.fd, 0, len(b'historical fixture'))

    def test_unrelated_existing_log_append_does_not_alias_target(self):
        other = self.logdir / 'other-fixture.log'
        other.write_bytes(b'initial')
        self.setup_source()
        other.write_bytes(b'changed')
        self.assertEqual(self.source.observe(123, FIXTURE), ('PASS', False))

    def test_event_watcher_is_bound_to_held_fd(self):
        with patch.object(H.LIBC, 'inotify_add_watch', wraps=H.LIBC.inotify_add_watch) as watch:
            self.setup_source()
            self.assertEqual(watch.call_args.args[1],
                             ('/proc/self/fd/' + str(self.source.chain[-1][0])).encode('ascii'))
            self.assertTrue(watch.call_args.args[2] & 0x01000000)

    def test_event_errors_latch_and_cannot_be_drained_to_pass(self):
        self.setup_source()
        def event(mask, name=b'apport.log\0', wd=None):
            name += b'\0' * (-len(name) % 4)
            return H.struct.pack('iIII', self.source.watch_id if wd is None else wd, mask, 0, len(name)) + name
        for data in (event(0x40), event(0x4000, b'', -1), event(0x8000, b''),
                     event(0x2000, b''), event(0x800, b''), b'partial', b'',
                     event(0x10000000, b'other\0')):
            self.source.watch_changed = False  # Fixture reset only; production never resets.
            with patch.object(H.os, 'read', return_value=data):
                with self.assertRaises(H.Refused): self.source.verify_events()
            self.assertTrue(self.source.watch_changed)
            with patch.object(H.os, 'read', side_effect=BlockingIOError()):
                with self.assertRaises(H.Refused): self.source.verify_events()

    def test_event_read_budget_and_unavailable_watch(self):
        self.setup_source()
        record = H.struct.pack('iIII', self.source.watch_id, 2, 0, 8) + b'other\0\0\0'
        with patch.object(H.os, 'read', return_value=record) as read:
            with self.assertRaises(H.Refused): self.source.verify_events()
            self.assertEqual(read.call_count, 4)
        self.source.close()
        with patch.object(H.LIBC, 'inotify_add_watch', return_value=-1):
            with self.assertRaises(H.Refused): self.source.setup_directory()

    def test_positive_survives_rotation_and_short_read_reg_lp01(self):
        self.setup_source()
        line = b'ERROR: apport (pid 999) Wed Sep 9 12:00:00 2026: called for global pid 123, signal 6 ' + FIXTURE + b'\n'
        self.path.write_bytes(line + b'longer announced content')
        self.path.rename(self.root / 'rotated')
        self.path.write_bytes(b'replacement not read')
        with patch.object(H.os, 'pread', return_value=line):
            self.assertEqual(self.source.observe(123, FIXTURE), ('FAIL', True))

    def test_change_after_read_prevents_absence(self):
        self.setup_source()
        def read(*args):
            self.path.rename(self.root / 'changed-after-read')
            self.path.write_bytes(b'')
            return b''
        with patch.object(H.os, 'pread', side_effect=read):
            with self.assertRaises(H.Refused): self.source.observe(123, FIXTURE)

    def test_cleanup_closes_remaining_descriptors_after_one_error(self):
        self.setup_source()
        calls = []
        original_close = H.os.close
        def close(fd):
            calls.append(fd)
            original_close(fd)
            if len(calls) == 1: raise OSError('UNPUBLISHED')
        with patch.object(H.os, 'close', side_effect=close):
            with self.assertRaises(H.Refused): self.source.close()
        self.assertEqual(len(calls), 5)
        self.assertEqual(self.source.chain, [])


class SetupTests(unittest.TestCase):
    def exercise(self, failures=()):
        with ExitStack() as stack:
            mocks = {}
            for name, owner, method in (
                ('setup_journal', H.Observation, 'setup_journal'),
                ('setup_log_directory', H.LogSource, 'setup_directory'),
                ('setup_log_file', H.LogSource, 'setup_file'),
                ('setup_crash_store', H.Observation, 'setup_store')):
                mocks[name] = stack.enter_context(patch.object(owner, method,
                    side_effect=OSError('UNPUBLISHED_SECRET_LIKE_TEXT') if name in failures else None))
            obj = H.Observation()
            return obj, mocks

    def test_all_four_stages_and_safe_result(self):
        obj, _ = self.exercise()
        self.assertTrue(obj.ready)
        self.assertEqual(obj.setup, dict.fromkeys(H.SETUP_STAGES, 'PASS'))
        report = H.report(obj.setup)
        self.assertEqual(W.validate_report(report), report)
        self.assertFalse(report['secret_entry_authorized'])
        self.assertFalse(report['runtime_crash_suppression_qualified'])

    def test_each_stage_failure_symbolic_only(self):
        for stage in H.SETUP_STAGES:
            obj, mocks = self.exercise((stage,))
            self.assertFalse(obj.ready)
            report = H.report(obj.setup)
            self.assertEqual(report['failed_checks'], [stage])
            self.assertEqual(W.validate_report(report), report)
            self.assertNotIn('UNPUBLISHED', json.dumps(report))
            if stage == 'setup_log_directory':
                mocks['setup_log_file'].assert_not_called()
                self.assertEqual(obj.setup['setup_log_file'], 'NOT_TESTED')
            mocks['setup_crash_store'].assert_called_once()
            mocks['setup_journal'].assert_called_once()

    def test_independent_failures_collected_together(self):
        obj, _ = self.exercise(('setup_journal', 'setup_log_directory', 'setup_crash_store'))
        self.assertEqual(H.report(obj.setup)['failed_checks'],
                         ['setup_journal', 'setup_log_directory', 'setup_crash_store'])

    def test_setup_failure_prevents_rng_fork_and_sigabrt_reg_lp02(self):
        for stage in H.SETUP_STAGES:
            result, events, generated = crash_tests.CrashTests().simulated_trial(setup_failure=stage)
            self.assertEqual(generated, 0)
            self.assertNotIn('fork', events)
            self.assertNotIn('signal', events)
            self.assertEqual(result['failed_checks'], [stage])
            self.assertEqual(result['results']['crash_signal'], 'NOT_TESTED')
            self.assertEqual(result['results']['runtime_limits'], 'PASS')
            self.assertFalse(result['secret_entry_authorized'])
            self.assertFalse(result['runtime_crash_suppression_qualified'])

    def test_observer_close_attempts_all_resources_on_error(self):
        obj, _ = self.exercise()
        obj.reader = Mock()
        obj.reader.close.side_effect = OSError('UNPUBLISHED')
        obj.log = Mock()
        obj.watch_fd = 42
        with patch.object(H.os, 'close') as close:
            with self.assertRaises(H.Refused): obj.close()
            obj.log.close.assert_called_once()
            close.assert_called_once_with(42)

    def test_strict_executable_functions_unchanged(self):
        original = subprocess.run(['/usr/bin/git', 'show', '531671a5e6e3bf8c7efc3bddb899c53d53cd1c27:scripts/qualification/run_operator_preflight.py'],
            cwd=ROOT, capture_output=True, text=True, check=True, timeout=10).stdout
        for function in (W.checked_path, W.checked_bytes):
            self.assertIn(inspect.getsource(function), original)
        previous = subprocess.run(['/usr/bin/git', 'show', '531671a5e6e3bf8c7efc3bddb899c53d53cd1c27:scripts/qualification/crash_canary.py'],
            cwd=ROOT, capture_output=True, text=True, check=True, timeout=10).stdout
        self.assertIn(inspect.getsource(H.root_path), previous)

    def test_no_import_eval_shell_or_writes_from_log_source(self):
        source = inspect.getsource(H).split('class LogSource:', 1)[1].split('\ndef journal_groups', 1)[0]
        for forbidden in ('exec(', 'eval(', 'subprocess', 'import_module', 'O_WRONLY', 'O_RDWR', 'O_CREAT', 'write('):
            self.assertNotIn(forbidden, source)
        self.assertEqual(W.CRASH_SETUP_STAGES, H.SETUP_STAGES)
        for stage in H.SETUP_STAGES:
            value = H.report({stage: 'FAIL'})
            self.assertEqual(set(value), set(H.report()))
            self.assertLess(len(json.dumps(value)), H.MAX_RESULT)


class CurrentCheckpointTests(observation_tests.CheckpointTests):
    def text(self):
        return (ROOT / 'docs/qualification/LOG_SOURCE_CHECKPOINT.md').read_text()

    def test_current_hashes_and_prior_evidence_preserved(self):
        text = self.text()
        for path in ('scripts/qualification/crash_canary.py', 'scripts/qualification/run_operator_preflight.py',
                     'infrastructure/qualification/ai-invest-operator.sudoers'):
            self.assertIn(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), text)
        self.assertIn('/var/tmp/ai-invest-crash-observation.json', text)
        self.assertNotIn('unlink -- /var/tmp', text)


if __name__ == '__main__':
    unittest.main()
