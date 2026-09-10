"""Non-secret preparation regressions; never perform host setup."""
import importlib.util
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('web_setup',ROOT/'scripts/setup_web_dirs.py')
S=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(S)


class Setup(unittest.TestCase):
    def test_exact_service_uid_socket_gid_reg_web03(self):
        for uid,mode in ((10003,0o700),(0,0o750)):
            good={'st_uid':uid,'st_gid':26,'st_mode':stat.S_IFDIR|mode,'st_dev':99}
            with patch.object(S.os,'fstat',return_value=SimpleNamespace(**good)): S.leaf(1,uid,mode,99)
            for delta in ({'st_gid':uid},{'st_uid':26},{'st_dev':100},{'st_mode':stat.S_IFDIR|0o777},{'st_mode':stat.S_IFLNK|mode}):
                with self.subTest(uid=uid,delta=delta),patch.object(S.os,'fstat',return_value=SimpleNamespace(**{**good,**delta})),self.assertRaises(RuntimeError): S.leaf(1,uid,mode,99)
    def test_root_and_no_arguments_required(self):
        with patch.object(S.os,'geteuid',return_value=1000),self.assertRaises(RuntimeError): S.setup()
        with patch.object(S.os,'geteuid',return_value=0),patch.object(S.sys,'argv',['setup','anything']),self.assertRaises(RuntimeError): S.setup()
    def test_no_credential_or_service_operation(self):
        source=(ROOT/'scripts/setup_web_dirs.py').read_text()
        for text in ('subprocess','getpass','cryptsetup','rmtree','unlink(','os.system','input('): self.assertNotIn(text,source)
        self.assertIn('module.mounted_device()',source)
        self.assertIn('module.empty(current)',source)


if __name__=='__main__': unittest.main()
