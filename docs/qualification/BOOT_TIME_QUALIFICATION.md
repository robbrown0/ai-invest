# Boot/Time Predicate Qualification

**Status:** Synthetic-only checkpoint prepared; not installed or run by agents. Gate 2 NOT PASSED. Both authorization flags remain false.

## Protected-host evidence

Human-tested commit: **24310834bf00b66273eb89c04cf88d41e8d97758**. The owner supplied this excerpt, **not a complete result schema**:

```json
{
  "checks_passed": false,
  "failed_checks": ["coverage_incomplete"],
  "mode": "crash-test",
  "results": {
    "setup_journal": "PASS",
    "setup_log_directory": "PASS",
    "setup_log_file": "PASS",
    "setup_crash_store": "PASS",
    "observation_window": "PASS",
    "apport_log": "PASS",
    "crash_store": "PASS",
    "journal": "NOT_TESTED",
    "journal_stage": "timestamp_boot",
    "journal_reason": "attribution_mismatch",
    "collector_retention": "NOT_TESTED"
  },
  "runtime_crash_suppression_qualified": false,
  "secret_entry_authorized": false
}
```

The owner also reports existing local protection/crash/cleanup checks PASS. This is one new human trial; artifact retrieval is not another trial. The earlier empty SSH probe never returned a matching record. All earlier failed prerequisites and trial evidence remain preserved in [the index](README.md) and [the previous journal record](JOURNAL_QUALIFICATION.md).

**The precise human failure remains unresolved.** The shared reason could mean wrong record boot, a pre-window record, or a reversed interval. Representation validation passed before that reason was produced. We do not infer which of the three occurred.

## Minimal source change and trust boundary

The existing journal result allowlists in both harness and wrapper gain three fixed reasons:

| Stage | Reason | Exact predicate |
| --- | --- | --- |
| seek | invalid_observation_interval | Original start/end are ordered and nonnegative; converted lower is no greater than upper |
| timestamp_boot | record_boot_mismatch | Returned entry-header boot equals the selected current boot |
| timestamp_boot | record_before_window | Returned integer microsecond timestamp is at least lower |

Interval validity is checked once before seek, including the original floating-point ordering so a sub-microsecond reversal cannot disappear through integer conversion. Header boot validation precedes the lower-bound check. The upper boundary remains inclusive; a record later than upper receives no payload reads and still leads through final change processing. In-window fixed-field attribution remains a separate attribution_mismatch predicate; the indexed _BOOT_ID field does not substitute for the entry-header boot.

No actual boot ID, timestamp, cursor, PID, message, environment value, canary or raw exception is published. Both false authorization flags and the 4096-byte result bound remain. Console, authentication, PATH/environment, log-source, crash protection and existing resource limits are unchanged. The sudoers update is digest-only, with no new executable/arguments.

## Clock and API trace

- After all required setup stages PASS, self.start is captured with time.monotonic(), before runtime canary generation. A separate wall-clock sample exists only for the established observation-window sanity check.
- finish waits its bounded observation period and captures end with time.monotonic().
- The installed Python clock reports clock_gettime(CLOCK_MONOTONIC). Start/end are seconds in that clock domain; both endpoints become int(seconds * 1000000).
- For nonnegative values this conversion floors to integer microseconds. Both endpoints are inclusive at that resolution. The lower bin can include a fraction of a microsecond before the floating start; this is existing timestamp quantization, not an added tolerance.
- The raw binding accepts integer microseconds for seek and returns integer microseconds plus 16-byte entry boot data. It does not apply high-level datetime conversion. No timezone conversion participates.

No evidence implicates NTP, timezone or wall-clock settings. The monotonic and wall-clock sanity checks are not interchanged. Versions remain python3-systemd235-1build4 and systemd/libsystemd0 255.4-1ubuntu8.17. See the [v235 raw binding](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c).

## Demonstrated library behavior, not a demonstrated host cause

The [v255 seek documentation](https://github.com/systemd/systemd/blob/v255/man/sd_journal_seek_head.xml) describes next selecting the closest following entry after a timestamp seek. We therefore did not assume that an older return was normal.

The installed native fixture **does reproduce older returns** for pre-window-only matching files, including a multi-file query with another in-window positive. It invokes the full actual sequence: restored cursor, complete seven-clause disjunction, monotonic seek, next and entry-header readback.

Versioned [v255 reader source](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c) explains the divergence: find_location_for_match tries monotonic positioning for a discrete match; a zero result can fall through to the first matching entry. During initial LOCATION_SEEK, next_beyond_location does not apply the comparison reserved for LOCATION_DISCRETE. This is a reproduced compatibility limitation, not evidence that the earlier host took that path.

**Selected disposition: retain strict rejection.** We have not implemented a traversal workaround. A pre-window-only query remains incomplete, not absence PASS. In the split-file case the later positive is not reached; no successful search of it is claimed. Bounded metadata-only continuation was considered, but would require its own completeness argument for forward progress, same-boot ordering, all files and unchanged budgets. It is not necessary to guess that remediation before distinguishing the actual human condition.

## Isolated tests and exact completion meaning

The existing test-only native writer and protected-from-host-data fixture were expanded, not replaced by another observer. It still refuses root, pins the private installed ABI, creates only owned temporary native journals, and uses unchanged CPU/address-space/file/core limits plus a subprocess timeout. No shared journal writes, actual host journal readers, deliberate crashes, real secrets or runtime canaries were involved. Native file headers may contain local library metadata, kept local and removed with the fixture.

**35 native cases** executed: the previous 11 plus 24 boot/time cases. The latter include:

| Cases | Expected and observed meaning |
| --- | --- |
| Pre-window-only and immediately-before positive | record_before_window, zero payload reads; NOT_TESTED |
| Prior fixed-scope history plus current matching record, all seven clauses | Current positive detected where traversal reaches it |
| Exactly lower/upper and realistic fractional-uptime endpoints | In-window positive detected; inclusive integer-microsecond boundaries |
| Immediately after upper | No payload read; finite empty-window PASS after final checks |
| Overlapping boot timestamps, including multiple files | Selected-boot in-window positive detected |
| Entry-header/indexed boot disagreement | record_boot_mismatch, zero payload reads |
| Old-only file plus current-positive file | record_before_window before later positive; NOT_TESTED, not a detected positive |
| Multiple pre-window-only files | record_before_window; NOT_TESTED |
| Reversed and sub-microsecond reversed intervals | invalid_observation_interval before seek, no payload read |

Every case asserts its expected result. Fixture PASS means the assertion passed, including expected refusal; it is not a claim that all 35 journal observations passed. The test reader forwards actual binding operations and guards payload access against out-of-window/wrong-boot records. Fault-injection mocks separately cover all three symbolic reasons, no payload reads on rejection, conversion, zero-width inclusivity, interval ordering, bounded output and unchanged protection functions.

Full suite: **240 tests PASS, no skips**, including the 35-case native test. The independent review is [BOOT_TIME_REVIEW.md](BOOT_TIME_REVIEW.md). These fixtures do not determine the host's specific cause or qualify a protected runtime journal observation. Prior duplicate-field and API-visible-storage limitations remain unchanged.

Additional checks actually run: strict candidate visudo parsing PASS; **36 qualification shell blocks** syntax-checked without execution; **72 Markdown documents / 308 local links** validated; nine unchanged Mermaid blocks structurally checked (no renderer). Common-secret-pattern checks passed for **99 nonignored working-tree files**, the index and **183 pre-amendment reachable history blobs**, with values suppressed. Staged/final history is rechecked at commit. Pattern scans are not exhaustive secret detection. No scanner/package installation or CI execution was performed. git diff --check passed.

## Human handoff and remaining blockers

Use only [the guarded upgrade and rollback](BOOT_TIME_CHECKPOINT.md). It verifies expected old/new hashes, protected ownership/modes/links, candidate/aggregate sudo syntax, and preserves root-only recovery copies. Nothing privileged is installed by agents. Fresh exclusive result: /var/tmp/ai-invest-crash-boot-time.json; every earlier result remains untouched.

The physical-console command remains sudo /usr/local/sbin/ai-invest-operator-preflight --crash-test. It will either complete finite observation or distinguish the blocking boot/time condition, subject to the unchanged setup/resource/error safeguards. Overall coverage_incomplete is still expected even if finite checks pass. Do not delete previous artifacts to rerun.

Outstanding: actual protected-host boot/time diagnosis and successful finite observation; any reviewed library workaround; wider leakage/input/output and future service protection; original encrypted storage/TDE/OpenBao/recovery, tenancy, simulator and CI Gate 2 work. No LUKS/OpenBao initialization, real key/recovery generation, brokerage connectivity, package/host-policy change, production deployment or unrelated workload change. Source remains public; application remains private/LAN-only. PR #14 remains DRAFT and unmerged. secret_entry_authorized=false; runtime_crash_suppression_qualified=false.
