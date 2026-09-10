"""Unprivileged synthetic terminal/filesystem tests. Never real credentials."""
import ast
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import select
import signal
import stat
import tempfile
import termios
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
P=load('paper_provision','scripts/paper_provision.py')
T=load('paper_terminal','scripts/qualification/terminal_exchange.py')
I=load('paper_install','scripts/install_paper_provision.py')
INERT='PUBLIC_SYNTHETIC_INPUT_ONLY'


class Terminal(unittest.TestCase):
    def setUp(self):
        self.master,self.slave=os.openpty();self.before=termios.tcgetattr(self.slave)
    def tearDown(self): os.close(self.master);os.close(self.slave)
    def test_hidden_input_restored_no_terminal_echo(self):
        state={}
        with T.quiet_terminal(self.slave,state):
            os.write(self.master,INERT.encode()+b'\n')
            self.assertEqual(P.read_value(T,self.slave,time.monotonic()+1),INERT)
            self.assertFalse(select.select([self.master],[],[],0)[0])
        self.assertTrue(state['restored']);self.assertEqual(termios.tcgetattr(self.slave),self.before)
    def test_cancel_eof_invalid_and_oversized_restore(self):
        for raw in (b'\x03',b'\x04',b'\x1a',b'\xff',b'\n',b'A'*257,b'bad space'):
            with self.subTest(raw_kind=len(raw)),self.assertRaises(P.Refused):
                with T.quiet_terminal(self.slave,{}):
                    os.write(self.master,raw);P.read_value(T,self.slave,time.monotonic()+1)
            self.assertEqual(termios.tcgetattr(self.slave),self.before)
    def test_timeout_restores(self):
        with self.assertRaises(T.Refused):
            with T.quiet_terminal(self.slave,{}): P.read_value(T,self.slave,time.monotonic()-1)
        self.assertEqual(termios.tcgetattr(self.slave),self.before)
    def test_catchable_interruption_restores(self):
        with self.assertRaises(T.Refused):
            with T.interruptions(),T.quiet_terminal(self.slave,{}): signal.raise_signal(signal.SIGTERM)
        self.assertEqual(termios.tcgetattr(self.slave),self.before)
    def test_nonblocking_read_race_retries(self):
        with patch.object(P.os,'read',side_effect=[BlockingIOError(),*map(lambda c:bytes([c]),INERT.encode()+b'\n')]):
            self.assertEqual(P.read_value(Mock(),self.slave,time.monotonic()+1),INERT)


class Publication(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='ai-invest-paper-fixture-')
        self.path=Path(self.temp.name);self.fd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY)
        self.chown=patch.object(P.os,'fchown');self.chown.start()
    def tearDown(self): self.chown.stop();os.close(self.fd);self.temp.cleanup()
    def test_exclusive_protected_publication(self):
        P.publish(self.fd,INERT,INERT)
        s=(self.path/P.PENDING).stat()
        self.assertEqual(stat.S_IMODE(s.st_mode),0o600);self.assertEqual(s.st_nlink,1)
        self.assertEqual(set(os.listdir(self.path)),{P.PENDING})
        self.assertEqual(json.loads((self.path/P.PENDING).read_text())['target_role'],'ai_web_a')
    def test_no_overwrite(self):
        P.publish(self.fd,INERT,INERT);before=(self.path/P.PENDING).read_bytes()
        with self.assertRaises(FileExistsError): P.publish(self.fd,INERT,'PUBLIC_OTHER_VALUE')
        self.assertEqual((self.path/P.PENDING).read_bytes(),before)
    def test_symlink_and_hardlink_temp_refused(self):
        (self.path/'other').touch()
        for create in (lambda:os.symlink('other',self.path/P.TEMP),lambda:os.link(self.path/'other',self.path/P.TEMP)):
            create()
            with self.assertRaises(FileExistsError): P.publish(self.fd,INERT,INERT)
            (self.path/P.TEMP).unlink()
    def test_replacement_detected_not_removed(self):
        real=P.os.fchown
        def substitute(*args):
            (self.path/P.TEMP).unlink();(self.path/P.TEMP).write_text('PUBLIC_REPLACEMENT')
        with patch.object(P.os,'fchown',side_effect=substitute):
            with self.assertRaises(P.Refused): P.publish(self.fd,INERT,INERT)
        self.assertEqual((self.path/P.TEMP).read_text(),'PUBLIC_REPLACEMENT')
    def test_partial_write_failure_removes_only_own_temp(self):
        with patch.object(P.os,'write',side_effect=OSError('UNPUBLISHED')):
            with self.assertRaises(OSError): P.publish(self.fd,INERT,INERT)
        self.assertFalse(list(self.path.iterdir()))


class Boundaries(unittest.TestCase):
    def test_exact_scope_and_clean_environment(self):
        cmd=P.scope_command('--physical')
        for value in ('MemoryMax=512M','MemorySwapMax=0','TasksMax=32','CPUQuota=50%',
                      '--expand-environment=no','/usr/bin/unshare','--mount','private','/usr/bin/python3','-I','-B'):
            self.assertIn(value,cmd)
        self.assertEqual(P.CLEAN,{'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'})
        self.assertFalse(any('$' in value for value in cmd))
        ssh=P.scope_command('--ssh')
        self.assertEqual(ssh[-2:],['/usr/local/sbin/ai-invest-paper-provision','--worker','--ssh'][-2:])
        self.assertEqual(P.scope_command('--physical')[-1],'--worker')
    def test_ssh_mode_requires_pts_and_bounded_environment(self):
        bad=dict(P.CLEAN,SSH_TTY='/dev/pts/7',SSH_CONNECTION='a b c d',LD_PRELOAD='bad')
        with patch.dict(P.os.environ,bad,clear=True):
            with self.assertRaises(P.Refused): P.require_ssh_environment()
        with patch.object(P.os,'isatty',return_value=False):
            with self.assertRaises(P.Refused): P.require_ssh_terminal({})
    def test_ssh_environment_keeps_path_incidental_and_rejects_term_modes(self):
        safe=dict(P.CLEAN,PATH='/usr/local/bin',TERM='xterm-256color',SUDO_GID='1000')
        with patch.dict(P.os.environ,safe,clear=True): P.require_ssh_environment()
        device=os.makedev(136,7); character=SimpleNamespace(st_mode=stat.S_IFCHR,st_rdev=device)
        valid={'TERM':'xterm-256color','SSH_TTY':'/dev/pts/7'}
        fixture=patch.object(P.os,'isatty',return_value=True),patch.object(P.os,'ttyname',return_value='/dev/pts/7'),\
            patch.object(P.os,'fstat',return_value=character),patch.object(P.os,'lstat',return_value=character),\
            patch.object(P.Path,'read_text',return_value=') S 0 0 0 '+str(device)),patch.object(P.os,'tcgetpgrp',return_value=P.os.getpgrp())
        with fixture[0],fixture[1],fixture[2],fixture[3],fixture[4],fixture[5]:
            P.require_ssh_terminal(valid)
            for term in ('screen','tmux-256color'):
                with self.subTest(term=term):
                    with self.assertRaises(P.Refused): P.require_ssh_terminal(dict(valid,TERM=term))
            with self.assertRaises(P.Refused): P.require_ssh_terminal(dict(valid,SSH_TTY='/dev/pts/8'))
            with patch.object(P.os,'tcgetpgrp',return_value=P.os.getpgrp()+1):
                with self.assertRaises(P.Refused): P.require_ssh_terminal(valid)
    def test_ssh_logind_binds_tty_service_and_rejects_duplicates(self):
        keys=('Active','Remote','Type','Class','User','LockedHint','State','TTY','Service')
        good='\n'.join([f'{key}='+({'Active':'yes','Remote':'yes','Type':'tty','Class':'user','User':'1000','LockedHint':'no','State':'active','TTY':'pts/7','Service':'sshd'}[key]) for key in keys])+'\n'
        result=type('Result',(),{'returncode':0,'stderr':'','stdout':good})()
        with patch.object(P.os,'ttyname',return_value='/dev/pts/7'),patch.object(P.subprocess,'run',return_value=result): P.require_ssh_session()
        for altered in (good.replace('TTY=pts/7','TTY=pts/8'),good.replace('Service=sshd','Service=login'),good.replace('User=1000','User=1001'),good+'Remote=yes\n',good.replace('TTY=pts/7','TTY=bad')):
            with self.subTest(altered=altered[-20:]),patch.object(P.os,'ttyname',return_value='/dev/pts/7'),patch.object(P.subprocess,'run',return_value=type('Result',(),{'returncode':0,'stderr':'','stdout':altered})()):
                with self.assertRaises(P.Refused): P.require_ssh_session()
    def test_no_process_network_or_interpolation_after_input(self):
        source=inspect.getsource(P.worker)
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Call):
                self.assertNotIn(ast.unparse(node.func),('subprocess.run','os.execve','os.fork','eval','exec'))
        self.assertLess(source.index('group=protect'),source.index('read_value'))
        self.assertLess(source.index('operator_ok'),source.index('read_value'))
        self.assertNotIn('key}',source);self.assertNotIn('value}',source)
    def test_failed_protection_prevents_input(self):
        console,metadata,terminal,storage=Mock(),Mock(),Mock(),Mock()
        with patch.dict(P.os.environ,P.CLEAN,clear=True),patch.object(P.Path,'read_text',return_value='1000'),patch.object(P,'protect',side_effect=P.Refused):
            with self.assertRaises(P.Refused): P.worker(console,metadata,terminal,storage,"--physical")
        terminal.read_disposable.assert_not_called();terminal.display.assert_not_called()
    def test_refusal_is_bounded_and_flags_false(self):
        with patch.object(P.os,'getuid',return_value=1000),patch.object(P.os,'write') as write:
            self.assertEqual(P.main(),1)
        result=json.loads(write.call_args.args[1]);self.assertFalse(result['connected'])
        self.assertFalse(result['secret_entry_authorized']);self.assertFalse(result['runtime_crash_suppression_qualified'])
        self.assertNotIn(INERT,str(result))
    def test_pinned_source_and_no_argument_sudo_scope(self):
        for source,_,_,digest in I.FILES: self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),digest)
        policy=(ROOT/I.FILES[-1][0]).read_text()
        self.assertIn('/usr/local/sbin/ai-invest-paper-provision ""',policy)
        self.assertIn('/usr/local/sbin/ai-invest-paper-provision --ssh',policy)
        self.assertNotIn('NOPASSWD',policy);self.assertNotIn('--worker',policy)
        self.assertNotIn('ALL=(ALL)',policy)
        for line in policy.splitlines():
            if line.startswith('Defaults'): self.assertTrue(line.startswith('Defaults!AI_INVEST_PAPER_PROVISION '))
    def test_installer_nonroot_refused_no_files(self):
        with patch.object(I.os,'getuid',return_value=1000),patch.object(I,'write') as write:
            with self.assertRaises(RuntimeError): I.install()
        write.assert_not_called()
    def test_source_symlink_and_writable_file_rejected(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-installer-fixture-') as tmp:
            path=Path(tmp)/'script';path.write_text('PUBLIC');path.chmod(0o666)
            digest=hashlib.sha256(b'PUBLIC').hexdigest()
            with patch.object(I,'parents'):
                with self.assertRaises(RuntimeError): I.read(path,digest,True)
                path.chmod(0o600);link=Path(tmp)/'link';link.symlink_to(path)
                with self.assertRaises(OSError): I.read(link,digest,True)


class Installation(unittest.TestCase):
    def exercise(self,replace=False,fail=True):
        with tempfile.TemporaryDirectory(prefix='ai-invest-install-fixture-') as tmp:
            root=Path(tmp);lib=root/'lib';lib.mkdir(mode=0o700)
            targets=[root/'command',lib/'helper',root/'policy']
            files=tuple(('source'+str(i),path,0o600,'f'*64) for i,path in enumerate(targets))
            original_lstat=Path.lstat
            def root_stat(path,*args,**kwargs):
                info=original_lstat(path,*args,**kwargs)
                if path in targets:
                    values=list(info);values[4]=0;return os.stat_result(values)
                return info
            calls=0
            def validate(path=None):
                nonlocal calls
                calls+=1
                if calls==4 and fail:
                    if replace:
                        # Preserve the old inode to prevent immediate inode reuse.
                        targets[-1].rename(root/'old-policy')
                        targets[-1].write_text('PUBLIC_REPLACEMENT')
                    raise RuntimeError('UNPUBLISHED')
            with patch.object(I.os,'getuid',return_value=0),patch.object(I.sys,'argv',['installer']),\
                 patch.object(I,'LIB',lib),patch.object(I,'FILES',files),patch.object(I,'DEPENDENCIES',()),\
                 patch.object(I,'parents'),patch.object(I,'read',return_value=b'PUBLIC_FIXTURE'),\
                 patch.object(I,'validate',side_effect=validate),patch.object(Path,'lstat',root_stat):
                if fail:
                    with self.assertRaises(RuntimeError): I.install()
                else: self.assertEqual(I.install(),'installed_not_provisioned')
            if fail:
                self.assertFalse(targets[0].exists());self.assertFalse(targets[1].exists())
                self.assertEqual(targets[2].exists(),replace)
                if replace: self.assertEqual(targets[2].read_text(),'PUBLIC_REPLACEMENT')
            else: self.assertTrue(all(path.exists() for path in targets))
            self.assertFalse(list(lib.glob('paper-install-*')))
    def test_partial_install_failure_removes_only_created_artifacts(self): self.exercise()
    def test_partial_failure_preserves_replaced_artifact(self): self.exercise(replace=True)
    def test_candidate_aggregate_and_final_validation_success(self): self.exercise(fail=False)
