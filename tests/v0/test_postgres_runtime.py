"""Offline guard/recovery regressions. Real DB trials are separately recorded."""
import contextlib
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
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('pg_bootstrap',ROOT/'infrastructure/postgres/bootstrap.py')
B=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)


class RuntimeTests(unittest.TestCase):
    def test_native_guard_build_abi_reg_pg_runtime01(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-guard-build-') as directory:
            target=Path(directory)/'guard.so'
            subprocess.run(['/usr/bin/cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',
                '-o',str(target),str(ROOT/'infrastructure/postgres/runtime_guard.c')],check=True,capture_output=True)
            symbols=subprocess.run(['/usr/bin/objdump','-T',str(target)],check=True,capture_output=True,text=True).stdout
            self.assertNotIn('GLIBC_2.38',symbols)
            self.assertIn('ai_guard_status',symbols)

    def test_guard_controls_and_no_key_access(self):
        source=(ROOT/'infrastructure/postgres/runtime_guard.c').read_text()
        for value in ('PR_SET_DUMPABLE, 0','PR_SET_NO_NEW_PRIVS','RLIMIT_CORE',
            'memory.swap.max','memory.swap.current','memory.max','cpu.max','pids.max','uid != geteuid()',
            'quota > period','WCOREDUMP','UINT64_MAX','O_NOFOLLOW'):
            self.assertIn(value,source)
        for value in ('strtoull(', 'sscanf(', 'getenv(', 'keyring', 'system('): self.assertNotIn(value,source)

    def test_isolated_app_has_socket_only_and_pinned_base(self):
        source=(ROOT/'infrastructure/application/compose.yaml').read_text()
        self.assertEqual(source.count('source:'),1)
        self.assertIn('network_mode: none',source)
        self.assertIn('create_host_path: false',source)
        self.assertIn('memswap_limit: 256m',source)
        image=(ROOT/'infrastructure/application/Dockerfile').read_text()
        self.assertIn('@sha256:',image)
        self.assertNotIn('groupadd',image)  # Debian already contains GID26.
        self.assertIn('"-I", "-B"',image)
        self.assertIn('psycopg[binary]==3.3.5',image)
        self.assertIn('chmod 0444 /usr/local/lib/ai-invest/runtime_guard.so',image)

    def test_migration_not_ignored_and_rls_is_preserved(self):
        path='backend/migrations/0003_synthetic_broker.sql'
        self.assertEqual(subprocess.run(['/usr/bin/git','check-ignore',path],cwd=ROOT,capture_output=True).returncode,1)
        source=(ROOT/path).read_text()
        for value in ('USING tde_heap','FORCE ROW LEVEL SECURITY','database_role=session_user','FOREIGN KEY (tenant_id,account_id)'):
            self.assertIn(value,source)

    def test_fixed_seed_matches_application_state(self):
        import sys
        sys.path.insert(0,str(ROOT/'backend'))
        from ai_invest_core.workflow import initial_state
        calls=[]
        with patch.object(B,'sql',side_effect=lambda text,*args:calls.append(text)), \
            patch.object(B.Path,'read_text',return_value='FIXED_SYNTHETIC_MIGRATION_FIXTURE'):
            B.seed()
        self.assertIn(json.dumps(initial_state()),calls[-1])
        for value in ('NOINHERIT NOSUPERUSER','NOBYPASSRLS','GRANT SELECT,INSERT','REVOKE ALL ON DATABASE'):
            self.assertIn(value,calls[-1])
        self.assertNotIn('GRANT ALL',calls[-1])

    def test_package_sql_version_distinction_reg_pg_runtime03(self):
        source=(ROOT/'infrastructure/postgres/bootstrap.py').read_text()
        self.assertIn("!='2.2'",source)
        self.assertNotIn("!='2.2.2'",source)

    def test_sql_failure_does_not_publish_raw_errors(self):
        with patch.object(B.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout='SENSITIVE_FIXTURE',stderr='SENSITIVE_FIXTURE')):
            with self.assertRaisesRegex(RuntimeError,'^sql_failed$'): B.sql('SELECT 1')

    def test_protected_failure_precedes_key_operations(self):
        with patch.object(B,'protected',side_effect=RuntimeError('SENSITIVE_FIXTURE')),patch.object(B,'keys') as keys, \
            patch.object(B.sys,'argv',['bootstrap','keys']),contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(B.main(),1)
            keys.assert_not_called()
        self.assertNotIn('SENSITIVE_FIXTURE',output.getvalue())
        self.assertFalse(json.loads(output.getvalue())['passed'])

    def test_unknown_mode_never_echoes_argument(self):
        with patch.object(B,'protected'),patch.object(B.sys,'argv',['bootstrap','SENSITIVE_FIXTURE']),contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(B.main(),1)
        self.assertEqual(json.loads(output.getvalue())['mode'],'invalid')
        self.assertNotIn('SENSITIVE_FIXTURE',output.getvalue())

    def recovery(self,mutation=None):
        with tempfile.TemporaryDirectory(prefix='ai-invest-recovery-fixture-') as directory:
            base=Path(directory)
            locations={name:base/str(index) for index,name in enumerate(('/var/lib/ai-invest-keys','/recovery-a','/recovery-b'))}
            for path in locations.values(): path.mkdir(mode=0o700)
            source=locations['/var/lib/ai-invest-keys']/'v0.keyring'
            source.write_bytes(b'PUBLIC_SYNTHETIC_RECOVERY_FIXTURE')
            source.chmod(0o600)
            if mutation: mutation(source,locations)
            original_open,original_fstat=os.open,os.fstat
            def opening(path,flags,*args,**kwargs):
                return original_open(locations.get(str(path),path),flags,*args,**kwargs)
            def metadata(fd):
                result=original_fstat(fd)
                return SimpleNamespace(**{name:getattr(result,name) for name in ('st_mode','st_nlink','st_size','st_dev','st_ino','st_mtime_ns','st_ctime_ns')},st_uid=26)
            with patch.object(B,'protected'),patch.object(B.os,'open',side_effect=opening),patch.object(B.os,'fstat',side_effect=metadata):
                B.recovery_copies()
            for name in ('/recovery-a','/recovery-b'):
                target=locations[name]/'v0.keyring'
                self.assertEqual(target.read_bytes(),source.read_bytes())
                self.assertEqual(stat.S_IMODE(target.stat().st_mode),0o600)

    def test_recovery_exclusive_verified_copies(self): self.recovery()

    def test_recovery_unsafe_source_refused(self):
        for mode in (0o644,0o660):
            with self.subTest(mode=mode),self.assertRaises(RuntimeError):
                self.recovery(lambda source,locations:source.chmod(mode))

    def test_recovery_hardlink_refused(self):
        with self.assertRaises(RuntimeError): self.recovery(lambda source,locations:os.link(source,source.parent/'extra'))

    def test_recovery_symlink_refused(self):
        def replace(source,locations):
            target=source.with_name('fixture')
            source.rename(target)
            source.symlink_to(target)
        with self.assertRaises(OSError): self.recovery(replace)

    def test_existing_second_copy_refused_before_first_created(self):
        def existing(source,locations):
            (locations['/recovery-b']/'v0.keyring').write_bytes(b'EXISTING_PUBLIC_FIXTURE')
        with self.assertRaises(RuntimeError): self.recovery(existing)

    def test_no_observation_flags_promoted(self):
        source=(ROOT/'scripts/postgres_v0.py').read_text()
        self.assertIn("'secret_entry_authorized':False",source)
        self.assertIn("'runtime_crash_suppression_qualified':False",source)
        self.assertIn("getattr(error,'sqlstate',None)!='42501'",source)
        self.assertNotIn('Alpaca',source)


if __name__=='__main__': unittest.main()
