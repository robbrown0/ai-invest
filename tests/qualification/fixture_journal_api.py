"""Test-only v255 native journal fixture; NEVER imported by privileged helpers.

Executed unprivileged in a bounded subprocess. Writes only its TemporaryDirectory.
Uses the installed private v255 ABI, not a portable application dependency.
No journal send API, host reader, runtime canary, crash or secret.
"""
import ctypes as C
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import tempfile

LIBRARY = '/usr/lib/x86_64-linux-gnu/systemd/libsystemd-shared-255.so'
BOOT = bytes.fromhex('a' * 32)
FIXTURE = b'public-journal-fixture-positive'
ROOT = Path(__file__).resolve().parents[2]


class Timestamp(C.Structure):
    _fields_ = [('realtime', C.c_uint64), ('monotonic', C.c_uint64)]


class Identifier(C.Union):
    _fields_ = [('bytes', C.c_ubyte * 16), ('qwords', C.c_uint64 * 2)]


class IOVec(C.Structure):
    _fields_ = [('base', C.c_void_p), ('length', C.c_size_t)]


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    if os.geteuid() == 0:
        return {'status': 'UNSUPPORTED'}
    version = subprocess.run(['/usr/bin/dpkg-query', '-W', '-f=${Version}\n',
        'libsystemd0', 'systemd'], capture_output=True, timeout=2, check=True,
        env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
    if version != b'255.4-1ubuntu8.17\n255.4-1ubuntu8.17\n' or not Path(LIBRARY).is_file():
        return {'status': 'UNSUPPORTED'}
    from systemd import _reader
    lib = C.CDLL(LIBRARY)
    pointer = C.c_void_p
    lib.mmap_cache_new.argtypes, lib.mmap_cache_new.restype = [], pointer
    lib.mmap_cache_unref.argtypes, lib.mmap_cache_unref.restype = [pointer], pointer
    lib.journal_file_close.argtypes, lib.journal_file_close.restype = [pointer], pointer
    lib.journal_file_open.argtypes = [C.c_int, C.c_char_p, C.c_int, C.c_int,
        C.c_uint, C.c_uint64, pointer, pointer, pointer, C.POINTER(pointer)]
    lib.journal_file_open.restype = C.c_int
    lib.journal_file_append_entry.argtypes = [pointer, C.POINTER(Timestamp),
        C.POINTER(Identifier), C.POINTER(IOVec), C.c_size_t, pointer, pointer, pointer, pointer]
    lib.journal_file_append_entry.restype = C.c_int
    spec = importlib.util.spec_from_file_location('fixture_harness',
        ROOT / 'scripts/qualification/crash_canary.py')
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    results = {}
    selectors = harness.journal_groups(BOOT.hex(), os.getpid(), 123)
    cases = [('empty', [('_PID', '999')], b'negative', False),
             ('positive', [('COREDUMP_PID', '123')], FIXTURE, True)]
    cases += [('clause_' + str(i), [group[1]], b'negative', False)
              for i, group in enumerate(selectors)]
    cases += [('threshold', [('COREDUMP_PID', '123')], b'x' * 65536, False)]
    cases += [('duplicate_limit', [('COREDUMP_PID', '123'), ('MESSAGE', FIXTURE.decode())],
               b'negative', False)]
    for name, fields, message, positive in cases:
        with tempfile.TemporaryDirectory(prefix='ai-invest-native-journal-') as directory:
            path = str(Path(directory) / 'fixture.journal')
            cache, journal = lib.mmap_cache_new(), pointer()
            assert cache
            try:
                assert lib.journal_file_open(-1, os.fsencode(path),
                    os.O_RDWR | os.O_CREAT | os.O_EXCL, 0, 0o600, 0,
                    None, cache, None, C.byref(journal)) >= 0
                records = [b'_BOOT_ID=' + BOOT.hex().encode(),
                           b'MESSAGE=' + message]
                records += [(key + '=' + value).encode() for key, value in fields]
                buffers = [C.create_string_buffer(value) for value in records]
                vectors = (IOVec * len(buffers))(*[IOVec(C.cast(buf, pointer), len(value))
                    for buf, value in zip(buffers, records)])
                stamp = Timestamp(1700000000000000, 1500000)
                boot = Identifier()
                boot.bytes[:] = BOOT
                assert lib.journal_file_append_entry(journal, C.byref(stamp), C.byref(boot),
                    vectors, len(vectors), None, None, None, None) >= 0
            finally:
                if journal:
                    lib.journal_file_close(journal)
                lib.mmap_cache_unref(cache)
            with _reader._Reader(flags=0, files=[path]) as reader:
                assert reader.fileno() >= 0
                reader.data_threshold = harness.MAX_FIELD
                reader.seek_tail()
                assert reader._previous()
                assert type(reader._get('MESSAGE')) is bytes
                if name == 'duplicate_limit':
                    # Demonstrate the raw API's first-value-only limit, NOT a
                    # successful whole-record absence test. No host data involved.
                    assert reader._get('MESSAGE') == b'negative'
                    assert reader._get_all()['MESSAGE'] == [b'negative', FIXTURE]
                    results[name] = 'PASS'
                    continue
                assert reader._get_monotonic()[0] == 1500000
                assert reader._get_monotonic()[1] == BOOT
                try:
                    reader._get('OBJECT_PID')
                except KeyError:
                    pass
                else:
                    assert name == 'clause_3'
                obj = harness.Observation.__new__(harness.Observation)
                obj.reader, obj.boot, obj.anchor = reader, BOOT.hex(), reader._get_cursor()
                obj.start = 1.0
                try:
                    answer = obj.journal(123, FIXTURE, 2.0)
                except harness.JournalIncomplete:
                    assert name == 'threshold'
                    assert obj.journal_diagnostic == {
                        'journal_stage': 'field_shape', 'journal_reason': 'incomplete_field'}
                else:
                    assert answer[0] == ('FAIL' if positive else 'PASS')
                    assert answer[1] == (positive or name == 'clause_2')
                results[name] = 'PASS'
    return {'status': 'PASS', 'cases': results}


if __name__ == '__main__':
    try:
        result = main()
    except BaseException:
        result = {'status': 'FAIL'}
    print(json.dumps(result, sort_keys=True))
