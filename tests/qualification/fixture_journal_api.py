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


def reverse_discovery(name):
    parts = name.split('_')
    return len(parts) == 4 and parts[0] == 'split' and parts[2] == '1'


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
    def write_file(path, rows, file_number=0, sequence=None):
        cache, journal = lib.mmap_cache_new(), pointer()
        assert cache
        try:
            assert lib.journal_file_open(-1, os.fsencode(path),
                os.O_RDWR | os.O_CREAT | os.O_EXCL, 0, 0o600, 0,
                None, cache, None, C.byref(journal)) >= 0
            for index, (usec, header_boot, fields, message) in enumerate(rows):
                records = [b'MESSAGE=' + message]
                records += [(key + '=' + value).encode() for key, value in fields]
                buffers = [C.create_string_buffer(value) for value in records]
                vectors = (IOVec * len(buffers))(*[IOVec(C.cast(buf, pointer), len(value))
                    for buf, value in zip(buffers, records)])
                stamp = Timestamp(1700000000000000 + file_number * 100 + index, usec)
                boot = Identifier()
                boot.bytes[:] = header_boot
                assert lib.journal_file_append_entry(journal, C.byref(stamp), C.byref(boot),
                    vectors, len(vectors), C.byref(sequence[0]) if sequence else None,
                    C.byref(sequence[1]) if sequence else None, None, None) >= 0
        finally:
            if journal:
                lib.journal_file_close(journal)
            lib.mmap_cache_unref(cache)

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
            write_file(path, [(1500000, BOOT, [('_BOOT_ID', BOOT.hex()), *fields], message)])
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
    # Same restored-cursor/full-DNF/seek/next production path, realistic history.
    scope = ('_SYSTEMD_UNIT', 'ai-invest-operator-preflight.scope')
    other_boot = bytes.fromhex('b' * 32)
    def row(usec, selector=scope, message=b'negative', boot=BOOT, field_boot=None):
        return (usec, boot, [('_BOOT_ID', (field_boot or boot).hex()), selector], message)
    boundary_cases = [
        ('pre_only', [[row(999999)]], 1.0, 2.0),
        ('pre_then_scope_positive', [[row(999999), row(1500000, message=FIXTURE)]], 1.0, 2.0),
        ('old_scope_new_child', [[row(999999), row(1500000, ('_PID', '123'), FIXTURE)]], 1.0, 2.0),
        ('lower_positive', [[row(1000000, message=FIXTURE)]], 1.0, 2.0),
        ('upper_positive', [[row(2000000, message=FIXTURE)]], 1.0, 2.0),
        ('outside_lower_positive', [[row(999999, message=FIXTURE)]], 1.0, 2.0),
        ('outside_upper_positive', [[row(2000001, message=FIXTURE)]], 1.0, 2.0),
        ('earlier_runs', [[row(100), row(500000), row(999999), row(1500000)]], 1.0, 2.0),
        ('overlapping_boots', [[row(1500000, boot=other_boot), row(999999), row(1500000, message=FIXTURE)]], 1.0, 2.0),
        ('boot_header_field_disagreement', [[row(1500000, boot=other_boot, field_boot=BOOT),
             row(2000001, ('_PID', '999'))]], 1.0, 2.0),
        ('multiple_files', [[row(999999)], [row(1500000, ('COREDUMP_PID', '123'), FIXTURE)]], 1.0, 2.0),
        ('multiple_files_pre_only', [[row(500000)], [row(999999)]], 1.0, 2.0),
        ('multiple_files_boots', [[row(1500000, boot=other_boot)],
             [row(1500000, message=FIXTURE)]], 1.0, 2.0),
        ('fractional_lower', [[row(123456123456, message=FIXTURE)]], 123456.1234567, 123457.0),
        ('fractional_upper', [[row(123457123456, message=FIXTURE)]], 123456.0, 123457.1234567),
        ('reversed_interval', [[row(1500000)]], 2.0, 1.0),
        ('submicrosecond_reversal', [[row(1500000)]], 1.0000009, 1.0000001),
        ('pre_then_negative', [[row(999999), row(1500000)]], 1.0, 2.0),
        ('split_negative', [[row(999999)], [row(1500000)]], 1.0, 2.0),
        ('upper_then_regression', [[row(2000001), row(1500000)]], 1.0, 2.0),
        ('pre_budget_pass', [[row(500000 + i) for i in range(255)]], 1.0, 2.0),
        ('pre_budget_fail', [[row(500000 + i) for i in range(256)]], 1.0, 2.0),
        ('post_budget_pass', [[row(2000001 + i) for i in range(255)]], 1.0, 2.0),
        ('post_budget_fail', [[row(2000001 + i) for i in range(256)]], 1.0, 2.0),
        ('shared_positive', [[row(999999)], [row(1500000, message=FIXTURE)]], 1.0, 2.0),
        ('shared_negative', [[row(999999)], [row(1500000)]], 1.0, 2.0),
    ]
    boundary_cases += [('history_clause_' + str(i),
        [[row(999999), row(1500000, group[1], FIXTURE)]], 1.0, 2.0)
        for i, group in enumerate(selectors)]
    for i, group in enumerate(selectors):
        for reverse in (False, True):
            for positive in (False, True):
                files = [[row(999999)], [row(1500000, group[1], FIXTURE if positive else b'negative')]]
                boundary_cases.append(('split_' + str(i) + '_' + str(int(reverse)) +
                    ('_positive' if positive else '_negative'), files, 1.0, 2.0))
    boundary_results = {}
    for name, files, start, end in boundary_cases:
        with tempfile.TemporaryDirectory(prefix='ai-invest-native-boundary-') as directory:
            paths = []
            sequence = (C.c_uint64(0), Identifier()) if name.startswith('shared_') else None
            if sequence:
                sequence[1].bytes[:] = bytes.fromhex('c' * 32)
            for index, rows in enumerate(files):
                path = str(Path(directory) / ('fixture-' + str(index) + '.journal'))
                write_file(path, rows, index, sequence)
                paths.append(path)
                if sequence:
                    with _reader._Reader(flags=0, files=[path]) as one:
                        one.seek_tail()
                        assert one._previous()
                        assert one._get_cursor().split(';')[0] == 's=' + bytes(sequence[1].bytes).hex()
            # Permute reader discovery order, not synthetic clock chronology.
            if reverse_discovery(name):
                paths.reverse()
            class ObservedReader(_reader._Reader):
                payload_reads = 0
                def _get(self, key):
                    stamp, boot = self._get_monotonic()
                    assert boot == BOOT and int(start * 1000000) <= stamp <= int(end * 1000000)
                    self.payload_reads += 1
                    return super()._get(key)
            with ObservedReader(flags=0, files=paths) as reader:
                assert reader.fileno() >= 0
                reader.data_threshold = harness.MAX_FIELD
                reader.seek_tail()
                assert reader._previous()
                obj = harness.Observation.__new__(harness.Observation)
                obj.reader, obj.boot, obj.anchor = reader, BOOT.hex(), reader._get_cursor()
                obj.start = start
                try:
                    answer = obj.journal(123, FIXTURE, end)
                except harness.JournalIncomplete:
                    answer = ('NOT_TESTED', True)
                # Expected incomplete cases are successful regression assertions,
                # NOT successful journal observations or absence claims.
                incomplete = {
                    'upper_then_regression': 'ordering_ambiguous',
                    'pre_budget_fail': 'record_limit',
                    'post_budget_fail': 'record_limit',
                    'boot_header_field_disagreement': 'record_boot_mismatch',
                    'reversed_interval': 'invalid_observation_interval',
                    'submicrosecond_reversal': 'invalid_observation_interval',
                }
                if name in incomplete:
                    assert answer[0] == 'NOT_TESTED'
                    assert obj.journal_diagnostic['journal_reason'] == incomplete[name]
                    assert reader.payload_reads == 0
                elif name in ('earlier_runs', 'outside_upper_positive', 'pre_only',
                              'outside_lower_positive', 'multiple_files_pre_only',
                              'pre_then_negative', 'split_negative', 'pre_budget_pass',
                              'post_budget_pass') or name.endswith('_negative'):
                    assert answer[0] == 'PASS'
                    assert obj.journal_diagnostic['journal_reason'] == 'complete'
                    if name in ('pre_only', 'outside_lower_positive', 'outside_upper_positive',
                                'multiple_files_pre_only', 'pre_budget_pass', 'post_budget_pass'):
                        assert reader.payload_reads == 0
                else:
                    assert answer[0] == 'FAIL'
                    assert obj.journal_diagnostic['journal_reason'] == 'positive_match'
                    assert reader.payload_reads > 0
                boundary_results[name] = 'PASS'
    return {'status': 'PASS', 'cases': results, 'boundaries': boundary_results,
            'compatibility': {'multiple_files': 'POSITIVE_DETECTED'}}


if __name__ == '__main__':
    try:
        result = main()
    except BaseException:
        result = {'status': 'FAIL'}
    print(json.dumps(result, sort_keys=True))
