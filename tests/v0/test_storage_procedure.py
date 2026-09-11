"""Isolated preparation tests only. Never execute initializer/worker/root tools."""
import ast
from contextlib import ExitStack
import hashlib
import importlib.util
from pathlib import Path
import stat
import subprocess
import termios
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'scripts/storage_init.py'
spec = importlib.util.spec_from_file_location('prepared_storage',SOURCE)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)  # Definitions only, never main()/worker().


class StoragePreparationTests(unittest.TestCase):
    def test_exact_approved_targets_and_full_allocation(self):
        self.assertEqual(str(S.IMAGE),'/var/lib/ai-invest/qualification.luks')
        self.assertEqual(str(S.MAPPER),'/dev/mapper/ai-invest-qualification')
        self.assertEqual(str(S.MOUNT),'/srv/ai-invest-secure')
        self.assertEqual(S.SIZE,68719476736)
        text=SOURCE.read_text()
        self.assertIn('os.posix_fallocate(image_fd,0,SIZE)',text)
        self.assertIn('os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW',text)
        self.assertNotIn('unlink(',text)
        self.assertNotIn('rmtree(',text)

    def test_no_arbitrary_scope_or_command_arguments(self):
        args=S.scope_command('10:20')
        for value in ('MemoryMax=2G','MemorySwapMax=0','TasksMax=32','CPUQuota=100%',
                      'RuntimeMaxSec=900','--expand-environment=no','--mount','--propagation','private','-i'):
            self.assertIn(value,args)
        self.assertEqual(args[-3:],[str(S.INSTALLED),'--worker','10:20'])
        for value in ('10:20;sh','$(whoami)','../x','','0:1:2'):
            with self.assertRaises(S.Refused): S.scope_command(value)

    def test_policy_digest_exact_authentication_and_no_worker_grant(self):
        text=(ROOT/'infrastructure/qualification/ai-invest-storage-init.sudoers').read_text()
        self.assertIn(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),text)
        self.assertEqual(text.count(' /usr/local/sbin/ai-invest-storage-init --initialize'),1)
        self.assertNotIn('--worker',text)
        self.assertNotIn('NOPASSWD',text)
        self.assertIn('PASSWD: NOSETENV:',text)
        self.assertIn('Defaults!AI_INVEST_STORAGE_INIT !use_pty',text)
        self.assertNotIn('Defaults !use_pty',text)

    def test_capacity_revalidation_does_not_double_subtract_allocation(self):
        value={'local_nonrotational_block_backing':True,'root_owned_nonwritable_ancestors':True,
            'mount_parent_same_filesystem':True,'available_bytes':300*1024**3,'total_bytes':1000*1024**3}
        preflight=Mock(); preflight.plan_snapshot.return_value=value
        with patch.object(S,'memory_headroom'):
            S.storage_safety(preflight,allocated=True)
            preflight.plan_ok.assert_not_called()
            for field in ('local_nonrotational_block_backing','root_owned_nonwritable_ancestors','mount_parent_same_filesystem'):
                with self.subTest(field=field):
                    preflight.plan_snapshot.return_value={**value,field:False}
                    with self.assertRaises(S.Refused): S.storage_safety(preflight,allocated=True)
            preflight.plan_snapshot.return_value={**value,'available_bytes':199*1024**3}
            with self.assertRaises(S.Refused): S.storage_safety(preflight,allocated=True)

    def test_low_memory_stops_before_any_operation(self):
        for content in ('MemAvailable: 4194303 kB\n','MemAvailable: bad kB\n',''):
            with patch.object(Path,'read_text',return_value=content):
                with self.assertRaises(S.Refused): S.memory_headroom()
        with patch.object(Path,'read_text',return_value='MemAvailable: 4194304 kB\n'):
            S.memory_headroom()

    def terminal_fixture(self,stack):
        original=[0,0,0,termios.ECHO|termios.ECHONL,0,0,[]]
        quiet=original.copy(); quiet[3]=0
        stack.enter_context(patch.object(S,'integrity'))
        protect=stack.enter_context(patch.object(S,'protection'))
        attrs=stack.enter_context(patch.object(S.termios,'tcgetattr',side_effect=[original,quiet,original]))
        setattrs=stack.enter_context(patch.object(S.termios,'tcsetattr'))
        flush=stack.enter_context(patch.object(S.termios,'tcflush'))
        child=Mock(); child.wait.return_value=0; child.poll.return_value=0
        launch=stack.enter_context(patch.object(S.subprocess,'Popen',return_value=child))
        return protect,attrs,setattrs,flush,child,launch

    def test_no_echo_verified_before_cryptsetup_no_pipe_or_secret_capture(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            S.terminal_command(['/usr/sbin/cryptsetup','FIXTURE_ONLY'],None,None)
            self.assertEqual(launch.call_args.kwargs,{'env':S.ENV,'close_fds':True})
            self.assertEqual(protect.call_count,2)
            self.assertEqual(setattrs.call_count,2)
            self.assertEqual(child.wait.call_args.kwargs,{'timeout':300})

    def test_failed_echo_disable_never_launches(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            attrs.side_effect=[[0,0,0,termios.ECHO,0,0,[]]]*3
            with self.assertRaises(S.Refused): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            launch.assert_not_called()

    def test_failed_protection_never_touches_terminal_or_launches(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            protect.side_effect=S.Refused()
            with self.assertRaises(S.Refused): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            attrs.assert_not_called(); launch.assert_not_called()

    def test_cleanup_flush_failure_still_restores_terminal(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            flush.side_effect=[None,OSError('synthetic')]
            with self.assertRaises(S.Refused): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            self.assertEqual(setattrs.call_count,2)

    def test_timeout_reaps_child_then_restores(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            child.wait.side_effect=[subprocess.TimeoutExpired('fixed',300),0]
            child.poll.side_effect=[None,0]
            with self.assertRaises(subprocess.TimeoutExpired): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            child.terminate.assert_called_once()
            self.assertEqual(setattrs.call_count,2)

    def test_scope_failed_state_with_processes_is_not_idle(self):
        with patch.object(S,'run',return_value='failed\n'),patch.object(Path,'exists',return_value=True), \
             patch.object(Path,'read_text',return_value='populated 1\nfrozen 0\n'):
            self.assertFalse(S.scope_idle())

    def test_terminate_error_does_not_skip_reap_or_terminal_restore(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            child.wait.side_effect=[subprocess.TimeoutExpired('fixed',300),0]
            child.poll.side_effect=[None,None,0]
            child.terminate.side_effect=ProcessLookupError()
            with self.assertRaises(subprocess.TimeoutExpired): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            child.kill.assert_called_once()
            self.assertEqual(setattrs.call_count,2)

    def test_still_live_reader_keeps_echo_off_for_outer_scope_cleanup(self):
        with ExitStack() as stack:
            protect,attrs,setattrs,flush,child,launch=self.terminal_fixture(stack)
            child.wait.side_effect=subprocess.TimeoutExpired('fixed',300)
            child.poll.return_value=None
            with self.assertRaises(S.Refused): S.terminal_command(['/usr/sbin/cryptsetup'],None,None)
            self.assertEqual(setattrs.call_count,1)

    def test_file_identity_sparse_size_mode_and_inode_fixtures(self):
        fields=dict(st_mode=stat.S_IFREG|0o600,st_size=S.SIZE,st_blocks=S.SIZE//512,st_dev=8,st_ino=11)
        with patch.object(S,'checked',return_value=SimpleNamespace(**fields)):
            self.assertEqual(S.file_identity(),(8,11))
        for changed in ({'st_size':1},{'st_blocks':1},{'st_mode':stat.S_IFREG|0o644}):
            with patch.object(S,'checked',return_value=SimpleNamespace(**{**fields,**changed})):
                with self.assertRaises(S.Refused): S.file_identity()
        with patch.object(S,'file_identity',return_value=(8,12)):
            with self.assertRaises(S.Refused): S.mapper_identity((8,11))

    def test_strict_path_owner_links_and_writable_ancestor(self):
        target=Path('/fixed/image')
        directory=SimpleNamespace(st_mode=stat.S_IFDIR|0o755,st_uid=0,st_nlink=2)
        file=SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_uid=0,st_nlink=1)
        for altered in (SimpleNamespace(st_mode=stat.S_IFLNK|0o777,st_uid=0,st_nlink=1),
                        SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_uid=0,st_nlink=2),
                        SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_uid=1000,st_nlink=1)):
            with patch.object(Path,'resolve',return_value=target),patch.object(Path,'lstat',side_effect=[directory,directory,altered]):
                with self.assertRaises(S.Refused): S.checked(target)
        writable=SimpleNamespace(st_mode=stat.S_IFDIR|0o775,st_uid=0,st_nlink=2)
        with patch.object(Path,'resolve',return_value=target),patch.object(Path,'lstat',return_value=writable):
            with self.assertRaises(S.Refused): S.checked(target)

    def test_scope_exit_checked_before_releasing_cleanup_and_mounting(self):
        text=SOURCE.read_text()
        start=text.index('result = subprocess.run(scope_command')
        tail=text[start:]
        self.assertLess(tail.index('require(scope_idle())'),tail.index('scope_started = False'))
        self.assertLess(tail.index('require(result.returncode==0'),tail.index('mount_and_validate(preflight)'))

    def test_installer_rollback_owned_before_policy_activation_reg_st05(self):
        text=(ROOT/'docs/STORAGE_INITIALIZATION.md').read_text()
        self.assertLess(text.index('    policy_active=1'),
            text.index('    /usr/bin/mv -T /etc/sudoers.d/.ai-invest-storage-init.pending'))
        self.assertIn('test -f /etc/sudoers.d/ai-invest-storage-init',text)
        self.assertIn("populated 0",text)

    def test_result_has_only_fixed_nonsecret_fields(self):
        with patch.object(S.os,'lseek'),patch.object(S.os,'ftruncate'),patch.object(S.os,'fsync'), \
             patch.object(S.os,'fchmod') as mode,patch.object(S.os,'write',side_effect=lambda fd,data:len(data)) as write:
            S.report(99,'complete',True,publish=True)
            import json
            value=json.loads(write.call_args.args[1])
            self.assertEqual(value,{'mode':'storage-init','storage_ready':True,'stage':'complete','gate2_passed':False})
            mode.assert_called_once_with(99,0o644)
            with self.assertRaises(S.Refused): S.report(99,'raw_exception')

    def test_destructive_source_order_and_fixed_kdf(self):
        text=SOURCE.read_text(); ast.parse(text)
        worker=text[text.index('def worker('):text.index('def mount_and_validate(')]
        self.assertLess(worker.index('storage_safety(preflight,allocated=True)'),worker.index("'luksFormat'"))
        self.assertLess(worker.index('mapper_identity(identity)'),worker.index("'/usr/sbin/mke2fs'"))
        self.assertIn("'--pbkdf-memory','1048576','--pbkdf-parallel','1'",worker)
        self.assertIn("'--pbkdf-force-iterations','4'",worker)
        self.assertNotIn("'-F'",worker)
        self.assertNotIn('--key-file',text)
        self.assertNotIn('dmsetup',text)
        self.assertNotIn('shell=True',text)
        self.assertIn("'nodev,nosuid,noexec'",text)


if __name__=='__main__': unittest.main()
