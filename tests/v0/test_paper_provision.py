"""Unprivileged synthetic terminal/filesystem tests. Never real credentials."""
import ast
import contextlib
import io
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
        with patch.dict(P.os.environ,dict(safe,SSH_AUTH_SOCK='/run/user/1000/agent.sock'),clear=True): P.require_ssh_environment()
        with patch.dict(P.os.environ,dict(safe,LC_TIME='C',LC_MONETARY='C'),clear=True): P.require_ssh_environment()
        with patch.dict(P.os.environ,dict(safe,SSH_ORIGINAL_COMMAND=''),clear=True): P.require_ssh_environment()
        with patch.dict(P.os.environ,dict(safe,SSH_ORIGINAL_COMMAND='id'),clear=True):
            with self.assertRaises(P.Refused): P.require_ssh_environment()
        with patch.dict(P.os.environ,dict(safe,LD_PRELOAD='bad'),clear=True):
            with self.assertRaises(P.Refused): P.require_ssh_environment()
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
    def test_ssh_scope_uses_parent_session_boundary(self):
        self.assertNotIn('require_ssh_session()',inspect.getsource(P.worker))
        self.assertIn('phase("ssh_session",require_ssh_session)',inspect.getsource(P.main))

    def test_ssh_logind_binds_tty_service_and_rejects_duplicates(self):
        keys=('Active','Remote','Type','Class','User','LockedHint','State','TTY','Service')
        good='\n'.join([f'{key}='+({'Active':'yes','Remote':'yes','Type':'tty','Class':'user','User':'1000','LockedHint':'no','State':'active','TTY':'pts/7','Service':'sshd'}[key]) for key in keys])+'\n'
        result=type('Result',(),{'returncode':0,'stderr':'','stdout':good})()
        with patch.object(P.os,'ttyname',return_value='/dev/pts/7'),patch.object(P.subprocess,'run',return_value=result): P.require_ssh_session()
        for altered in (good.replace('TTY=pts/7','TTY=pts/8'),good.replace('Service=sshd','Service=login'),good.replace('User=1000','User=1001'),good+'Remote=yes\n',good.replace('TTY=pts/7','TTY=bad')):
            with self.subTest(altered=altered[-20:]),patch.object(P.os,'ttyname',return_value='/dev/pts/7'),patch.object(P.subprocess,'run',return_value=type('Result',(),{'returncode':0,'stderr':'','stdout':altered})()):
                with self.assertRaises(P.Refused): P.require_ssh_session()
    def test_ssh_logind_fallback_resolves_unique_remote_tty_session(self):
        direct=type('Result',(),{'returncode':1,'stderr':'','stdout':''})()
        listing=type('Result',(),{'returncode':0,'stderr':'','stdout':'42 1000 rob - pts/7 online\n'})()
        shown='\n'.join([f'{key}='+({'Active':'yes','Remote':'yes','Type':'tty','Class':'user','User':'1000','State':'online','TTY':'pts/7','Service':'sshd'}[key]) for key in ('Active','Remote','Type','Class','User','State','TTY','Service')])+'\n'
        resolved=type('Result',(),{'returncode':0,'stderr':'','stdout':shown})()
        with patch.object(P.os,'ttyname',return_value='/dev/pts/7'),patch.object(P.subprocess,'run',side_effect=(direct,listing,resolved)):
            P.require_ssh_session()

    def test_no_process_network_or_interpolation_after_input(self):
        source=inspect.getsource(P.worker)
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Call):
                self.assertNotIn(ast.unparse(node.func),('subprocess.run','os.execve','os.fork','eval','exec'))
        self.assertLess(source.index('group=phase'),source.index('read_value'))
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
                 patch.object(I,'validate',side_effect=validate),patch.object(I,'validate_manifest',return_value=b'MANIFEST'),patch.object(Path,'lstat',root_stat):
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
    def test_replacement_aggregate_substitutes_duplicate_policy_once(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-sudoers-fixture-') as tmp:
            root=Path(tmp);included=root/'sudoers.d';included.mkdir();base=root/'sudoers';candidate=root/'candidate';old=included/'ai-invest-paper-provision';other=included/'other'
            policy=b'Cmnd_Alias AI_INVEST_TEST = /bin/true\nrob ALL=(root) AI_INVEST_TEST\n'
            base.write_text('@includedir /etc/sudoers.d\n');old.write_bytes(policy);other.write_bytes(b'Cmnd_Alias OTHER_TEST = /bin/false\nrob ALL=(root) OTHER_TEST\n');candidate.write_bytes(policy)
            bad=root/'bad';bad.write_text('@include '+str(old)+'\n@include '+str(candidate)+'\n')
            with self.assertRaises(Exception): I.validate(bad)
            real_fstat=os.fstat
            def fake_fstat(fd):
                info=real_fstat(fd);values=list(info);values[4]=0;return os.stat_result(values)
            with patch.object(I,'SUDOERS',base),patch.object(I,'SUDOERS_DIR',included),patch.object(I,'POLICY',old),patch.object(I.os,'fstat',side_effect=fake_fstat):
                data=I.replacement_aggregate(candidate)
            self.assertNotIn(str(old).encode(),data);self.assertEqual(data.count(('@include '+str(candidate)).encode()),1)
            aggregate=root/'aggregate';aggregate.write_bytes(data);I.validate(aggregate)

    def test_in_place_upgrade_verifies_old_artifacts_and_rolls_back(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-upgrade-fixture-') as tmp:
            root=Path(tmp);lib=root/'lib';lib.mkdir(mode=0o700);policy=root/'sudoers';
            targets=(root/'command',lib/'terminal',lib/'storage',policy)
            sources=('one','two','three','four');old=b'OLD-PUBLIC';new=b'NEW-PUBLIC'
            old_digest=hashlib.sha256(old).hexdigest();new_digest=hashlib.sha256(new).hexdigest()
            files=tuple((source, target, 0o600, new_digest) for source,target in zip(sources,targets))
            old_files=tuple((target,0o600,old_digest) for target in targets)
            approved=(("fixture",old_files),)
            for source,target,_,_ in files:
                (root/source).write_bytes(new);(root/source).chmod(0o600);target.write_bytes(old);target.chmod(0o600)
            def fake_artifact(path,digest,mode):
                if digest==old_digest: return old
                if digest==new_digest: return new
                raise RuntimeError('wrong_digest')
            def fake_replace(path,data,mode):
                temp=path.parent/('.tmp-'+path.name);temp.write_bytes(data);temp.chmod(mode);os.replace(temp,path)
            with patch.object(I,'ROOT',root),patch.object(I,'LIB',lib),patch.object(I,'POLICY',policy),\
                patch.object(I,'FILES',files),patch.object(I,'OLD_FILES',old_files),patch.object(I,'APPROVED_OLD_VERSIONS',approved),patch.object(I,'DEPENDENCIES',()),\
                patch.object(I,'parents'),\
                patch.object(I,'validate'),patch.object(I,'validate_manifest',return_value=b'MANIFEST'),patch.object(I,'replacement_aggregate',return_value=b'PUBLIC_AGGREGATE'),patch.object(I,'artifact',side_effect=fake_artifact),\
                patch.object(I,'replace_file',side_effect=fake_replace),patch.object(I.os,'getuid',return_value=0),\
                patch.object(I.sys,'argv',['installer','--upgrade']):
                    self.assertEqual(I.upgrade(),'upgraded_not_provisioned')
            self.assertTrue(all(path.read_bytes()==new for path in targets))
            backups=[I.backup_path(path,'fixture') for path in targets]
            self.assertTrue(all(path.exists() and path.read_bytes()==old for path in backups))
            with patch.object(I,'ROOT',root),patch.object(I,'LIB',lib),patch.object(I,'POLICY',policy),\
                patch.object(I,'FILES',files),patch.object(I,'OLD_FILES',old_files),patch.object(I,'APPROVED_OLD_VERSIONS',approved),patch.object(I,'validate'),patch.object(I,'validate_manifest',return_value=b'MANIFEST'),patch.object(I,'replacement_aggregate',return_value=b'PUBLIC_AGGREGATE'),patch.object(I,'artifact',side_effect=fake_artifact),\
                patch.object(I,'replace_file',side_effect=fake_replace),patch.object(I.os,'getuid',return_value=0),\
                patch.object(I.sys,'argv',['installer','--rollback-upgrade']):
                    self.assertEqual(I.rollback_upgrade(),'rolled_back_previous_version')
            self.assertTrue(all(path.read_bytes()==old for path in targets));self.assertTrue(all(not path.exists() for path in backups))
    def test_approved_ssh_predecessor_hashes_are_allowlisted(self):
        versions=dict(I.APPROVED_OLD_VERSIONS)
        self.assertEqual(versions['ssh-v1'][0][2],'559a059870ff73e83afecd397d1dac32304d1aad1ec2d0b6555c40c6eaa53659')
        self.assertEqual(versions['ssh-v1'][-1][2],'8562e5d48f623825c5d707548b66a5e40918f8ba9f93877d258346e2523b866e')
        self.assertEqual(versions['ssh-diagnostic-v3'][0][2],'d5829e80d0b9fd4dca994e1ecfad3d524d3cff30074530c29955b2b5dabb8ab6')
        self.assertEqual(versions['ssh-session-v4'][0][2],'939c802cf6e0908858d504c383fcb6323be51dfa86db0f968710f162a21537fb')
        self.assertEqual(versions['ssh-session-v5'][0][2],'a65158bb67af7291e61d153d7ad90326af21945ddcef7f2c83f84565c60bd097')
        self.assertEqual(versions['ssh-session-v8'][0][2],'44fa2a4ba8e0af3f9dbd6b684e8ab478d7afbc74c2f53cffc378299fc8894ea2')

    def test_sequential_upgrade_preserves_prior_rollback_sets(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-sequential-') as tmp:
            root=Path(tmp);lib=root/'lib';lib.mkdir(mode=0o700);policy=root/'sudoers';targets=(root/'command',lib/'terminal',lib/'storage',policy)
            old=b'OLD';first=b'FIRST';scope=b'SCOPE';diagnostic=b'DIAGNOSTIC';final=b'FINAL';mode=0o600
            for target in targets: target.write_bytes(old);target.chmod(mode)
            def digest(data): return hashlib.sha256(data).hexdigest()
            contents=(old,first,scope,diagnostic,final)
            names=('baseline','ssh-v1','ssh-scope-v2','ssh-diagnostic-v3')
            versions=tuple(tuple((target,mode,digest(data)) for target in targets) for data in contents)
            sources=('one','two','three','four')
            def run(files,approved,content):
                for source in sources: (root/source).write_bytes(content);(root/source).chmod(mode)
                def fake_artifact(path,expected,requested_mode):
                    values={digest(data):data for data in contents}
                    values.update({I.manifest_digest(name,version):I.manifest_bytes(name,version) for name,version in approved})
                    if expected not in values: raise RuntimeError('wrong_digest')
                    return values[expected]
                def fake_replace(path,data,requested_mode):
                    temp=path.parent/('.tmp-'+path.name);temp.write_bytes(data);temp.chmod(requested_mode);os.replace(temp,path)
                with patch.object(I,'ROOT',root),patch.object(I,'LIB',lib),patch.object(I,'POLICY',policy),patch.object(I,'FILES',files),patch.object(I,'OLD_FILES',versions[0]),patch.object(I,'APPROVED_OLD_VERSIONS',approved),patch.object(I,'DEPENDENCIES',()),patch.object(I,'parents'),patch.object(I,'validate'),patch.object(I,'validate_manifest',return_value=b'MANIFEST'),patch.object(I,'replacement_aggregate',return_value=b'AGGREGATE'),patch.object(I,'artifact',side_effect=fake_artifact),patch.object(I,'replace_file',side_effect=fake_replace),patch.object(I.os,'getuid',return_value=0),patch.object(I.sys,'argv',['installer','--upgrade']):
                    self.assertEqual(I.upgrade(),'upgraded_not_provisioned')
            for index in range(1,len(contents)):
                next_files=tuple((source,target,mode,digest(contents[index])) for source,target in zip(sources,targets))
                approved=tuple((names[prior],versions[prior]) for prior in range(index))
                run(next_files,approved,contents[index])
            for name in names[:-1]:
                self.assertTrue(all(I.backup_path(target,name).exists() for target in targets))
            self.assertTrue(all(target.read_bytes()==final for target in targets))
            # Exercise rollback in the middle of the same lineage, then continue
            # upgrading from the rolled-back generation.
            rollback_values={digest(data):data for data in contents}
            rollback_values.update({I.manifest_digest(name,versions[i]):I.manifest_bytes(name,versions[i]) for i,name in enumerate(names)})
            def rollback_artifact(path,expected,requested_mode):
                if expected not in rollback_values: raise RuntimeError('wrong_digest')
                return rollback_values[expected]
            def rollback_replace(path,data,requested_mode):
                temp=path.parent/('.rollback-'+path.name); temp.write_bytes(data); temp.chmod(requested_mode); os.replace(temp,path)
            with patch.object(I,'ROOT',root),patch.object(I,'LIB',lib),patch.object(I,'POLICY',policy),patch.object(I,'FILES',tuple((source,target,mode,digest(final)) for source,target in zip(sources,targets))),patch.object(I,'APPROVED_OLD_VERSIONS',tuple((names[i],versions[i]) for i in range(4))),patch.object(I,'validate'),patch.object(I,'validate_manifest',return_value=b'MANIFEST'),patch.object(I,'artifact',side_effect=rollback_artifact),patch.object(I,'replace_file',side_effect=rollback_replace),patch.object(I.os,'getuid',return_value=0),patch.object(I.sys,'argv',['installer','--rollback-upgrade']):
                self.assertEqual(I.rollback_upgrade(),'rolled_back_previous_version')
            self.assertTrue(all(target.read_bytes()==diagnostic for target in targets))
            final_files=tuple((source,target,mode,digest(final)) for source,target in zip(sources,targets))
            run(final_files,tuple((names[i],versions[i]) for i in range(4)),final)
            self.assertTrue(all(target.read_bytes()==final for target in targets))

    def test_rollback_selects_newest_verified_generation_and_retains_older(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-rollback-generations-') as tmp:
            root=Path(tmp); lib=root/'lib'; lib.mkdir(mode=0o700); policy=root/'sudoers'
            targets=(root/'command',lib/'terminal',lib/'storage',policy); mode=0o600
            payloads=(b'BASE',b'SSH',b'SCOPE',b'DIAG',b'CURRENT')
            for target in targets: target.write_bytes(payloads[-1]); target.chmod(mode)
            def digest(data): return hashlib.sha256(data).hexdigest()
            current=tuple((target,mode,digest(payloads[-1])) for target in targets)
            approved=tuple((name,tuple((target,mode,digest(data)) for target in targets))
                           for name,data in zip(('baseline','ssh-v1','ssh-scope-v2','ssh-diagnostic-v3'),payloads[:-1]))
            for name,data in zip(('baseline','ssh-v1','ssh-scope-v2','ssh-diagnostic-v3'),payloads[:-1]):
                for target in targets:
                    backup=I.backup_path(target,name); backup.write_bytes(data); backup.chmod(mode)
            values={digest(data):data for data in payloads}
            values.update({I.manifest_digest(name,version):I.manifest_bytes(name,version) for name,version in approved})
            def fake_artifact(path,expected,requested_mode):
                return values[expected]
            with patch.object(I,'LIB',lib), patch.object(I,'FILES',tuple((str(target),target,mode,digest(payloads[-1])) for target in targets)), \
                 patch.object(I,'APPROVED_OLD_VERSIONS',approved), patch.object(I,'validate_manifest',return_value=b'MANIFEST'), patch.object(I,'artifact',side_effect=fake_artifact):
                selected=I.rollback_candidates()
            self.assertEqual(selected[0],'ssh-diagnostic-v3')
            self.assertTrue(all(I.backup_path(target,'ssh-v1').exists() for target in targets))
            self.assertTrue(all(I.backup_path(target,'ssh-scope-v2').exists() for target in targets))

    def test_upgrade_reports_bounded_failure_stage(self):
        output=io.StringIO()
        with patch.object(I,"install",side_effect=I.StageFailure("backup_creation")),contextlib.redirect_stdout(output):
            self.assertEqual(I.main(),1)
        result=json.loads(output.getvalue())
        self.assertEqual(result["failure_stage"],"backup_creation")
        self.assertEqual(set(result)-{"mode","state","credentials_entered","connected","failure_stage"},set())
        self.assertNotIn("PRIVATE_DETAIL",output.getvalue())

    def test_upgrade_phase_maps_unexpected_error_to_fixed_stage(self):
        with patch.object(I,"validate",side_effect=RuntimeError("PRIVATE_DETAIL")),patch.object(I.os,"getuid",return_value=0),patch.object(I.sys,"argv",["installer","--upgrade"]):
            with self.assertRaises(I.StageFailure) as failure: I.upgrade()
        self.assertEqual(failure.exception.stage,"precheck")

    def test_upgrade_refuses_changed_old_artifact_before_backup(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-upgrade-refuse-') as tmp:
            root=Path(tmp);lib=root/'lib';lib.mkdir(mode=0o700);target=root/'command';target.write_bytes(b'CHANGED')
            files=(('one',target,0o600,hashlib.sha256(b'NEW').hexdigest()),)
            old_files=((target,0o600,hashlib.sha256(b'OLD').hexdigest()),)
            with patch.object(I,'ROOT',root),patch.object(I,'LIB',lib),patch.object(I,'POLICY',target),\
                patch.object(I,'FILES',files),patch.object(I,'OLD_FILES',old_files),patch.object(I,'DEPENDENCIES',()),\
                patch.object(I,'validate'),patch.object(I.os,'getuid',return_value=0),patch.object(I.sys,'argv',['installer','--upgrade']):
                    with self.assertRaises(Exception): I.upgrade()
            self.assertFalse(I.backup_path(target).exists())
