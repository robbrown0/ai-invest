"""Non-privileged wrapper regressions; no installation/scope/bootstrap execution."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('operator_wrapper', ROOT / 'scripts/qualification/run_operator_preflight.py')
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)


def good_report(mode='operator', passed=True):
    if mode == 'operator':
        observations = dict.fromkeys(WRAPPER.OP_BOOL, True)
        observations.update(memory_max='2147483648', memory_swap_max='0', memory_swap_current='0', pids_max='32')
    else:
        observations = dict.fromkeys(WRAPPER.PLAN_BOOL, True)
        observations.update(dict.fromkeys(WRAPPER.PLAN_INT, 1000))
        observations['filesystem_type'] = 'ext4'
    return {'mode': mode, 'checks_passed': passed, 'observations': observations,
            'secret_entry_authorized': False, 'runtime_crash_suppression_qualified': False}


class ConsoleTests(unittest.TestCase):
    devices = [(stat.S_IFCHR | 0o600, 4, 1)] * 3

    def test_real_vt_metadata(self):
        self.assertTrue(WRAPPER.console_ok(['/dev/tty1'] * 3, self.devices, {}))

    def test_reject_pts_gui_other_terminals_reg_wrapper_tty_01(self):
        for name in ('/dev/pts/0', '/dev/tty', '/dev/ttyS0', '/dev/tty0', '/dev/console', '', '/dev/tty64'):
            with self.subTest(name=name):
                self.assertFalse(WRAPPER.console_ok([name] * 3, self.devices, {}))

    def test_reject_ssh_display_multiplexer_even_with_vt(self):
        for key in ('SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY', 'DISPLAY', 'WAYLAND_DISPLAY', 'TMUX', 'STY'):
            self.assertFalse(WRAPPER.console_ok(['/dev/tty1'] * 3, self.devices, {key: 'synthetic'}))

    def test_reject_wrong_device_or_redirected_descriptor(self):
        for devices in ([(stat.S_IFREG, 4, 1)] * 3, [(stat.S_IFCHR, 136, 0)] * 3,
                        [(stat.S_IFCHR, 4, 2)] * 3):
            self.assertFalse(WRAPPER.console_ok(['/dev/tty1'] * 3, devices, {}))
        self.assertFalse(WRAPPER.console_ok(['/dev/tty1', '/dev/pts/0', '/dev/tty1'], self.devices, {}))


class CommandTests(unittest.TestCase):
    def test_exact_required_properties_and_no_pty(self):
        command = WRAPPER.scope_command('1:2')
        properties = [command[index + 1] for index, value in enumerate(command) if value == '-p']
        self.assertEqual(properties, ['MemoryMax=2G', 'MemorySwapMax=0', 'TasksMax=32', 'CPUQuota=100%'])
        self.assertEqual(command[:3], ['/usr/bin/systemd-run', '--scope', '--unit=ai-invest-operator-preflight'])
        self.assertNotIn('--pty', command)
        self.assertNotIn('--pipe', command)

    def test_private_mount_and_clean_environment(self):
        command = WRAPPER.scope_command('1:2')
        at = command.index('/usr/bin/unshare')
        self.assertEqual(command[at:at + 4], ['/usr/bin/unshare', '--mount', '--propagation', 'private'])
        at = command.index('/usr/bin/env')
        self.assertEqual(command[at:at + 5], ['/usr/bin/env', '-i', 'PATH=/usr/sbin:/usr/bin:/sbin:/bin', 'LANG=C', 'LC_ALL=C'])
        self.assertEqual(set(WRAPPER.CLEAN_ENV), {'PATH', 'LANG', 'LC_ALL'})

    def test_core_limits_isolated_interpreter_and_no_shell_profiles(self):
        command = WRAPPER.scope_command('1:2')
        at = command.index('/bin/bash')
        self.assertEqual(command[at:at + 4], ['/bin/bash', '--noprofile', '--norc', '-c'])
        self.assertEqual(command[at + 4],
                         'set -eu; ulimit -Sc 0; ulimit -Hc 0; exec /usr/bin/python3 -I -B "$1" --scoped "$2"')
        self.assertEqual(command[-2:], [str(WRAPPER.INSTALLED), '1:2'])
        self.assertTrue((ROOT / 'scripts/qualification/run_operator_preflight.py').read_text().startswith('#!/usr/bin/python3 -I\n'))

    def test_original_helper_pin_matches_committed_baseline(self):
        source = (ROOT / 'scripts/qualification/operator_preflight.py').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), WRAPPER.HELPER_SHA256)
        committed = subprocess.check_output(['git', 'show', WRAPPER.HELPER_BASELINE_COMMIT + ':scripts/qualification/operator_preflight.py'], cwd=ROOT)
        self.assertEqual(hashlib.sha256(committed).hexdigest(), WRAPPER.HELPER_BASELINE_SHA256)


class ReportTests(unittest.TestCase):
    def test_allowlisted_reports(self):
        for value in (good_report(), good_report('plan'), WRAPPER.failure()):
            self.assertEqual(WRAPPER.validate_report(value), value)

    def test_unknown_fields_and_authorization_changes_rejected(self):
        for value in ({**good_report(), 'token': 'SYNTHETIC_FORBIDDEN_FIELD'},
                      {**good_report(), 'secret_entry_authorized': True},
                      {**good_report(), 'runtime_crash_suppression_qualified': True},
                      {**good_report(), 'checks_passed': 1}):
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.validate_report(value)

    def test_arbitrary_observation_strings_rejected(self):
        value = good_report()
        value['observations']['memory_max'] = 'SYNTHETIC_NOT_METADATA'
        with self.assertRaises(WRAPPER.Rejected):
            WRAPPER.validate_report(value)
        value = good_report('plan')
        value['observations']['filesystem_type'] = 'SYNTHETIC_NOT_METADATA'
        with self.assertRaises(WRAPPER.Rejected):
            WRAPPER.validate_report(value)

    def test_capture_preserves_os_descriptors(self):
        source = (ROOT / 'scripts/qualification/operator_preflight.py').read_bytes()
        before = [os.fstat(fd) for fd in (0, 1, 2)]
        # Operator rejects our non-privileged test context; no scope is launched.
        report = WRAPPER.invoke_helper(source, 'operator')
        self.assertFalse(report['checks_passed'])
        self.assertEqual(before, [os.fstat(fd) for fd in (0, 1, 2)])


class TrustTests(unittest.TestCase):
    def path_fixture(self, mode=stat.S_IFREG | 0o644, uid=0):
        path = Mock(spec=Path)
        path.is_absolute.return_value = True
        path.resolve.return_value = path
        path.parents = []
        path.lstat.return_value = SimpleNamespace(st_mode=mode, st_uid=uid)
        return path

    def test_reject_symlinks_noncanonical_and_writable_paths(self):
        for mode in (stat.S_IFLNK | 0o777, stat.S_IFREG | 0o664, stat.S_IFREG | 0o646):
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.checked_path(self.path_fixture(mode))
        path = self.path_fixture()
        path.resolve.return_value = Path('/canonical/elsewhere')
        with self.assertRaises(WRAPPER.Rejected):
            WRAPPER.checked_path(path)
        with self.assertRaises(WRAPPER.Rejected):
            WRAPPER.checked_path(self.path_fixture(uid=1000))

    def test_reject_writable_or_nonroot_installed_ancestors(self):
        for mode, uid in ((stat.S_IFDIR | 0o775, 0), (stat.S_IFDIR | 0o755, 1000)):
            path = self.path_fixture()
            parent = Mock()
            parent.lstat.return_value = SimpleNamespace(st_mode=mode, st_uid=uid)
            path.parents = [parent]
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.checked_path(path)

    def trusted_fixture(self, mutation=None):
        helper = (ROOT / 'scripts/qualification/operator_preflight.py').read_bytes()
        files = {
            WRAPPER.INSTALLED: b'reviewed-wrapper',
            WRAPPER.CHECKOUT / 'scripts/qualification/run_operator_preflight.py': b'reviewed-wrapper',
            WRAPPER.HELPER: helper,
            WRAPPER.CHECKOUT / 'scripts/qualification/operator_preflight.py': helper,
            WRAPPER.CHECKOUT / '.git/config': b'[remote "origin"]\nurl = https://github.com/robbrown0/ai-invest.git\n',
            WRAPPER.CHECKOUT / '.git/HEAD': b'ref: refs/heads/phase3/synthetic-qualification\n',
        }
        if mutation:
            files[mutation] = b'SYNTHETIC_UNREVIEWED_BYTES'
        with patch.object(WRAPPER, '__file__', str(WRAPPER.INSTALLED)), \
             patch.object(WRAPPER, 'checked_path'), \
             patch.object(WRAPPER, 'checked_bytes', side_effect=lambda path, **kwargs: files[path]):
            return WRAPPER.trusted_helper()

    def test_trusted_snapshot_positive(self):
        self.assertEqual(hashlib.sha256(self.trusted_fixture()).hexdigest(), WRAPPER.HELPER_SHA256)

    def test_modified_helper_or_checkout_wrapper_rejected_reg_wrapper_trust_01(self):
        for path in (WRAPPER.HELPER, WRAPPER.CHECKOUT / 'scripts/qualification/operator_preflight.py',
                     WRAPPER.CHECKOUT / 'scripts/qualification/run_operator_preflight.py'):
            with self.assertRaises(WRAPPER.Rejected):
                self.trusted_fixture(path)

    def test_wrong_branch_rejected(self):
        with self.assertRaises(WRAPPER.Rejected):
            self.trusted_fixture(WRAPPER.CHECKOUT / '.git/HEAD')

    def test_host_enrollment_mismatch_rejected_without_command(self):
        with patch.object(WRAPPER.Path, 'read_text', return_value='systemd'), \
             patch.object(WRAPPER.Path, 'stat', return_value=SimpleNamespace(st_mode=0o600)), \
             patch.object(WRAPPER, 'checked_bytes', side_effect=[b'1' * 32, b'2' * 32]), \
             patch.object(WRAPPER.subprocess, 'run') as run:
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.require_host()
            run.assert_not_called()


class OutputTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='ai-invest-wrapper-test-')
        self.addCleanup(self.directory.cleanup)
        self.result = Path(self.directory.name) / 'result.json'
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(WRAPPER, 'RESULT', self.result))
        self.stack.enter_context(patch.object(WRAPPER, 'result_parent_ok'))

    def test_exclusive_creation_and_readable_sanitized_publication(self):
        fd = WRAPPER.create_result()
        try:
            self.assertEqual(stat.S_IMODE(self.result.stat().st_mode), 0o600)
            output = io.StringIO()
            with redirect_stdout(output):
                WRAPPER.save_result(fd, WRAPPER.failure(), publish=True)
            self.assertEqual(output.getvalue(),
                             'A new sanitized result is ready at /var/tmp/ai-invest-operator-preflight.json.\n')
            self.assertEqual(stat.S_IMODE(self.result.stat().st_mode), 0o644)
            self.assertEqual(json.loads(self.result.read_text()), WRAPPER.failure())
        finally:
            os.close(fd)

    def test_existing_regular_symlink_hardlink_not_overwritten_reg_output_02(self):
        other = Path(self.directory.name) / 'original'
        other.touch(mode=0o600)
        for kind in ('regular', 'symlink', 'hardlink'):
            if kind == 'regular':
                self.result.touch(mode=0o600)
            elif kind == 'symlink':
                self.result.symlink_to(other)
            else:
                os.link(other, self.result)
            with self.assertRaises(FileExistsError):
                WRAPPER.create_result()
            self.assertEqual(other.read_bytes(), b'')
            self.result.unlink()

    def test_no_alternate_output_or_invalid_identity(self):
        self.assertEqual(str(SPEC.origin).split('/')[-1], 'run_operator_preflight.py')
        for identity in ('../../etc/shadow', '-1:2', '1:2:3', ''):
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.open_scoped_result(identity)

    def test_publication_rejects_unapproved_data(self):
        fd = WRAPPER.create_result()
        try:
            with self.assertRaises(WRAPPER.Rejected):
                WRAPPER.save_result(fd, {'environment': 'SYNTHETIC'}, publish=True)
            self.assertEqual(self.result.stat().st_size, 0)
            self.assertEqual(stat.S_IMODE(self.result.stat().st_mode), 0o600)
        finally:
            os.close(fd)


class FlowTests(unittest.TestCase):
    def exercise(self, args=(), plan_pass=True, scoped=False, scope_code=0, save_error=False,
                 candidate=None, guard_failure=None, guard_effect=None):
        reports = []
        stream = io.StringIO()
        with ExitStack() as stack:
            stack.enter_context(patch.object(WRAPPER.os, 'environ', {}))
            stack.enter_context(patch.object(WRAPPER.os, 'geteuid', return_value=0))
            stack.enter_context(patch.object(WRAPPER.sys, 'argv', ['wrapper', *args]))
            stack.enter_context(patch.object(WRAPPER.resource, 'setrlimit'))
            stack.enter_context(patch.object(WRAPPER.os, 'umask'))
            stack.enter_context(patch.object(WRAPPER.os, 'close'))
            stack.enter_context(patch.object(WRAPPER.os, 'lseek'))
            stack.enter_context(patch.object(WRAPPER.os, 'read', return_value=json.dumps(
                good_report() if candidate is None else candidate).encode()))
            stack.enter_context(patch.object(WRAPPER.os, 'fstat', return_value=SimpleNamespace(st_dev=1, st_ino=2)))
            for name in ('require_console', 'require_host', 'require_operator_identity',
                         'require_operator_environment', 'require_console_session'):
                stack.enter_context(patch.object(WRAPPER, name,
                    side_effect=(guard_effect if guard_effect is not None else OSError('SYNTHETIC_PRIVATE_DETAIL'))
                    if guard_failure == name else None))
            stack.enter_context(patch.object(WRAPPER, 'create_result', return_value=100))
            stack.enter_context(patch.object(WRAPPER, 'open_scoped_result', return_value=100))
            stack.enter_context(patch.object(WRAPPER, 'trusted_helper', return_value=b'checked'))
            helper = stack.enter_context(patch.object(WRAPPER, 'invoke_helper',
                side_effect=lambda source, mode: good_report(mode, plan_pass if mode == 'plan' else True)))
            run = stack.enter_context(patch.object(WRAPPER.subprocess, 'run', return_value=SimpleNamespace(returncode=scope_code)))
            save = stack.enter_context(patch.object(WRAPPER, 'save_result',
                side_effect=OSError('SYNTHETIC_DIAGNOSTIC') if save_error else lambda fd, report, publish=False: reports.append(report)))
            with redirect_stderr(stream):
                code = WRAPPER.main()
            return code, helper, run, reports, stream.getvalue(), save

    def test_plan_failure_stops_before_scope_reg_wrapper_plan_01(self):
        code, helper, run, reports, _, _ = self.exercise(plan_pass=False)
        self.assertEqual(code, 1)
        run.assert_not_called()
        self.assertEqual([call.args[1] for call in helper.call_args_list], ['plan'])
        self.assertFalse(reports[-1]['checks_passed'])

    def test_scoped_entry_also_requires_plan(self):
        code, helper, run, _, _, _ = self.exercise(args=('--scoped', '1:2'), plan_pass=False)
        self.assertEqual(code, 1)
        self.assertEqual([call.args[1] for call in helper.call_args_list], ['plan'])
        run.assert_not_called()

    def test_scope_keeps_real_fds_and_clean_env(self):
        code, _, run, reports, _, _ = self.exercise()
        self.assertEqual(code, 0)
        self.assertEqual(run.call_args.kwargs, {'env': WRAPPER.CLEAN_ENV, 'check': False, 'close_fds': True})
        self.assertTrue(reports[-1]['checks_passed'])
        self.assertFalse(reports[-1]['secret_entry_authorized'])

    def test_scope_failure_invalidates_success_json_reg_wrapper_status_01(self):
        code, _, _, reports, _, _ = self.exercise(scope_code=1)
        self.assertEqual(code, 1)
        self.assertEqual(reports[-1], WRAPPER.failure())

    def test_output_io_error_does_not_disclose_diagnostics(self):
        code, _, _, _, diagnostic, _ = self.exercise(save_error=True)
        self.assertEqual(code, 1)
        self.assertNotIn('SYNTHETIC_DIAGNOSTIC', diagnostic)
        self.assertNotIn('Traceback', diagnostic)

    def test_all_bootstrap_secret_and_output_arguments_refused(self):
        for argument in ('--init', '--unseal', '--format', '--secret', '--token', '--passphrase', '--output', 'LIVE'):
            code, helper, run, _, _, _ = self.exercise(args=(argument,))
            self.assertEqual(code, 1)
            helper.assert_not_called()
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
