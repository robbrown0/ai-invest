"""Non-secret preparation tests; never execute root setup or initialize keys."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('pg_setup',ROOT/'scripts/setup_postgres_dirs.py')
S=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)


class SetupTests(unittest.TestCase):
    def test_exact_mapper_chain_rejects_misbinding_reg_pg01(self):
        values={
            '/proc/self/mountinfo': '1 0 253:9 / /srv/ai-invest-secure rw,nosuid,nodev,noexec - ext4 /dev/mapper/ai-invest-qualification rw\n',
            '/sys/dev/block/253:9/dm/name': 'ai-invest-qualification\n',
            '/sys/dev/block/253:9/dm/uuid': 'CRYPT-LUKS2-'+'a'*32+'-ai-invest-qualification\n',
            '/sys/dev/block/253:9/slaves/loop7/loop/backing_file': '/var/lib/ai-invest/qualification.luks\n'}
        def info(path):
            if str(path).endswith('.luks'):
                return SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_uid=0,st_nlink=1,st_size=68719476736)
            return SimpleNamespace(st_mode=stat.S_IFDIR|0o755,st_uid=0)
        def run(changes=None, slaves=None, metadata=info):
            data={**values,**(changes or {})}
            with patch.object(Path,'read_text',autospec=True,side_effect=lambda path:data[str(path)]), \
                 patch.object(Path,'iterdir',return_value=iter(slaves or [Path('/sys/dev/block/253:9/slaves/loop7')])), \
                 patch.object(Path,'lstat',autospec=True,side_effect=metadata):
                return S.mounted_device()
        self.assertEqual(run(),os.makedev(253,9))
        for changes in ({'/proc/self/mountinfo':''},
            {'/sys/dev/block/253:9/dm/name':'unrelated'},
            {'/sys/dev/block/253:9/dm/uuid':'CRYPT-LUKS2-bad'},
            {'/sys/dev/block/253:9/slaves/loop7/loop/backing_file':'/unrelated.luks'}):
            with self.assertRaises(RuntimeError): run(changes)
        with self.assertRaises(RuntimeError): run(slaves=[Path('/sys/dev/block/253:9/slaves/sda1')])
        with self.assertRaises(RuntimeError): run(slaves=[Path('loop7'),Path('loop8')])
        def writable(path):
            return SimpleNamespace(st_mode=stat.S_IFDIR|0o777,st_uid=0) if str(path)=='/var/lib' else info(path)
        with self.assertRaises(RuntimeError): run(metadata=writable)

    def test_fixed_nonsecret_scope(self):
        self.assertEqual(str(S.BASE),'/srv/ai-invest-secure')
        self.assertEqual(len(S.TARGETS),7)
        self.assertIn(('runtime','tde-keys',0o700),S.TARGETS)
        source=(ROOT/'scripts/setup_postgres_dirs.py').read_text()
        for forbidden in ('subprocess','getpass','rmtree','unlink(', 'open(\'w', 'cryptsetup', 'docker'):
            self.assertNotIn(forbidden,source)
        self.assertIn('len(sys.argv) == 1',source)
        self.assertIn('os.O_NOFOLLOW',source)

    def test_wrong_user_and_extra_argument_fail_before_mount(self):
        for uid,args in ((1000,['setup']), (0,['setup','unexpected'])):
            with patch.object(S.os,'geteuid',return_value=uid),patch.object(S.sys,'argv',args),patch.object(S,'mounted_device') as mounted:
                with self.assertRaises(RuntimeError): S.setup()
                mounted.assert_not_called()

    def test_directory_owner_mode_device_refusals(self):
        good=dict(st_mode=stat.S_IFDIR|0o700,st_uid=26,st_gid=26,st_dev=10)
        with patch.object(S.os,'fstat',return_value=SimpleNamespace(**good)):
            S.directory(1,26,0o700,10)
        for changes in ({'st_uid':0},{'st_gid':0},{'st_mode':stat.S_IFDIR|0o777},
                        {'st_mode':stat.S_IFLNK|0o700},{'st_dev':11}):
            with patch.object(S.os,'fstat',return_value=SimpleNamespace(**{**good,**changes})):
                with self.assertRaises(RuntimeError): S.directory(1,26,0o700,10)

    def test_empty_fixture_and_no_file_content_access(self):
        with tempfile.TemporaryDirectory(prefix='ai-invest-pg-setup-') as name:
            fd=os.open(name,S.FLAGS)
            try:
                S.empty(fd)
                (Path(name)/'unread-fixture').touch()
                with self.assertRaises(RuntimeError): S.empty(fd)
            finally: os.close(fd)

    def test_failure_output_sanitized(self):
        output=io.StringIO()
        with patch.object(S,'setup',side_effect=ValueError('UNTRUSTED_DETAILS')),contextlib.redirect_stdout(output):
            self.assertEqual(S.main(),1)
        value=json.loads(output.getvalue())
        self.assertFalse(value['directories_ready'])
        self.assertFalse(value['keys_created'])
        self.assertFalse(value['database_started'])
        self.assertNotIn('UNTRUSTED',output.getvalue())

    def test_compose_candidate_no_external_or_privileged_access(self):
        text=(ROOT/'infrastructure/postgres/compose.yaml').read_text()
        for required in ('network_mode: none','read_only: true','cap_drop: [ALL]',
                         'mem_limit: 2g','memswap_limit: 2g','soft: 0, hard: 0','profiles: [manual-database]'):
            self.assertIn(required,text)
        self.assertEqual(text.count('type: bind'),text.count('create_host_path: false'))
        for forbidden in ('privileged:', 'docker.sock', 'ports:', 'network_mode: host','POSTGRES_PASSWORD'):
            self.assertNotIn(forbidden,text)
        self.assertNotIn('tde-recovery',text)

    def test_wal_and_peer_only_configuration(self):
        text=(ROOT/'infrastructure/postgres/postgresql.conf').read_text()
        self.assertIn('pg_tde.wal_encrypt = on',text)
        self.assertIn("listen_addresses = ''",text)
        hba=(ROOT/'infrastructure/postgres/pg_hba.conf').read_text()
        self.assertIn('local all postgres peer',hba)
        self.assertNotIn(' trust',hba)


if __name__=='__main__': unittest.main()
