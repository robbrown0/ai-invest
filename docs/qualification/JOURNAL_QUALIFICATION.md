# Journal Observation — Bounded Failure Reporting and API Qualification

**Status:** Synthetic-only prepared checkpoint; not installed or run in the protected host context by agents. Qualification Gate 2 NOT PASSED. secret_entry_authorized=false; runtime_crash_suppression_qualified=false.

## New human evidence, preserved without reinterpretation

Human-tested source: **55339d0a222d95f8b58cf373d1de14f4a51bea88**.

The owner reports one protected crash trial with all four setup stages and existing local protection/crash/cleanup checks PASS, plus observation_window, apport_log and crash_store PASS. Journal and collector_retention remained NOT_TESTED. This is the owner's summary, not an invented full JSON artifact. Re-reading its result does not constitute another trial. The earlier exact artifacts and failures remain in [the qualification index](README.md), [log-source qualification](LOG_SOURCE_QUALIFICATION.md) and [earlier observer evidence](OBSERVATION_QUALIFICATION.md).

The separate ordinary-sudo SSH metadata-only probe returned:

```json
{
  "anchor_current_boot": true,
  "anchor_restored": true,
  "change_state": "APPEND",
  "completed": true,
  "matching_entry_present": false,
  "probe": "journal_metadata_only"
}
```

It exercised import, reader creation, notification-FD setup, anchoring/restoration, current-boot comparison, a simple boot-plus-own-PID filter, monotonic seek and an empty iteration. It did **not** exercise a matching record, extraction/validation, all disjunctions, protected context, or the earlier trial's invalidation state. We did not ask for another host probe or inspect broad journal output.

**The human trial's journal failure root cause remains unresolved.** Neither the successful empty probe nor our isolated fixture justifies claiming an actual-host cause. The prior catch discarded the operation that failed. This amendment makes the next protected run actionable rather than guessing a relaxed acceptance rule.

## Focused correction

The existing Observation.journal path remains the implementation; there is no second runtime observer or generic diagnostic runner. The wrapper still runs the exact digest-pinned two commands. Console, sudo authentication, identity, environment/PATH, host binding, log-directory policy, resource/crash protections and ordinary diagnostic behavior are unchanged. The sudoers amendment changes only the executable digest.

Two genuine false-absence risks were identified in source review and reproduced with fixtures, **not attributed to the human's NOT_TESTED result**:

1. A record beyond the upper timestamp bound previously returned before final change processing. It now takes the same final change check as end-of-stream. INVALIDATE cannot become absence PASS.
2. An APPEND arriving after traversal ended could indicate newly visible unexamined records. Final APPEND now reports incomplete/append_pending; initial APPEND remains permitted. A new run is not silently retried to obtain a green interval.

Time is checked within record extraction as well as at iteration/final completion; record, byte and time limits have distinct symbolic reasons. Raw field representation is checked before byte operations. A bounded positive prefix remains FAIL even if the field is oversized or a later operation would fail. Such conservative detection does not itself establish attribution. Missing required boot metadata and attribution mismatches stay incomplete.

The child remains held as a zombie during the bounded observation period; the reader was created in the protected parent and is used only there. The crashing child closes inherited descriptors before its controlled crash and never invokes that reader. No new process receives the runtime canary.

## Fixed result additions

Two keys are added **inside the existing results dictionary**: journal_stage and journal_reason. Both harness and wrapper independently validate the same finite enums. No arbitrary exception attribute or raw message is serialized. Existing category PASS/FAIL/NOT_TESTED/NOT_APPLICABLE meanings and all false authorization flags are preserved.

| Stage | Operation | Representative fixed reasons |
| --- | --- | --- |
| not_started | Journal traversal not attempted | not_started |
| initial_change | First reader.process call | invalidation, api_error, unexpected_representation |
| cursor_restore | seek_cursor, next, test_cursor | anchor_unavailable, api_error |
| filters | Seven boot-bound process/scope disjunctions | api_error |
| seek | Microsecond monotonic seek for the selected boot | api_error |
| iteration | Next matching entry | api_error |
| timestamp_boot | Raw monotonic struct-sequence and boot/window checks | unexpected_representation, attribution_mismatch, api_error |
| field_read | Individual fixed _get operations | api_error |
| field_shape | Bytes representation and full FIELD=value threshold | unexpected_representation, incomplete_field, positive_match |
| attribution | Required boot and one complete filter clause | incomplete_field, attribution_mismatch |
| final_change | End-of-stream or upper-bound change processing | invalidation, append_pending, api_error, unexpected_representation |
| budget | Traversal/extraction/final limits | record_limit, byte_limit, time_limit |
| complete | Traversal and final checks completed | complete |

The exact enum declarations in source govern validation. No count, cursor, PID, boot, field contents, exception text, host/environment identifiers or canary is returned. The result remains bounded by 4096 bytes. Journal errors leave journal=NOT_TESTED and collector_retention incomplete unless another observed positive requires FAIL. A positive is never downgraded by a later missing observation.

For example, a newly observed end-of-window invalidation would add only:

```json
{
  "journal": "NOT_TESTED",
  "journal_stage": "final_change",
  "journal_reason": "invalidation"
}
```

This is a schema example, **not a claimed host result**. Failures outside journal traversal retain their existing setup/category reporting; a supervisor timeout remains incomplete and cannot promise a completed inner diagnostic.

## Installed API audit and finite scope

Versions inspected locally: python3-systemd **235-1build4**; systemd and libsystemd0 **255.4-1ubuntu8.17**. Candidate sudo parser remains **1.9.15p5**. No package was installed.

The [v235 binding implementation](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c) confirms that raw _get accepts a field name and returns bytes despite its stale string docstring. Missing fields raise KeyError; other API failures must not be treated as absence. Raw monotonic results contain integer microseconds and 16-byte boot data. High-level Reader conversions are deliberately not used. The same binding exposes cursor, match, seek and change APIs used by the observer.

Installed-binding fixture execution confirms those contracts for matching records, each of the seven complete boot/process/scope clauses, exact cursor restoration and microsecond bounds. Explicit files= fixture readers require flags=0; the production SYSTEM|LOCAL_ONLY reader is not changed to a fixture reader. The normal parent owns the reader throughout traversal.

Important limitations follow from [systemd v255 retrieval implementation](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c) and the binding:

- Individual _get exposes only the first value for a repeated field. A real native duplicate-MESSAGE fixture demonstrates this limitation. Its test PASS means the limitation was reproduced, **not** that the second value was searched.
- _get_all is not substituted into production: its v235 enumeration can conceal errors. It is used only on a wholly owned harmless fixture to demonstrate the repeated-field behavior.
- libsystemd can internally skip malformed backing objects and expose no field. API-visible absence is not validation of every backing object, file or possible record.
- A field at/above the configured threshold is incomplete; the threshold is not a promise that every underlying decompression/allocation is smaller. Scope memory and outer deadlines remain required.
- Only fixed fields in the finite attributed view are examined; optional absent fields are not errors, but required boot/selector evidence is enforced. Arbitrary fields, duplicate later values and unverifiable corrupted storage are outside this PASS claim.

Thus journal PASS is **API-visible first-value fixed-field evidence under trusted root/kernel/journal-service assumptions**, not whole-record forensic absence or tamper resistance. Collector_retention PASS remains only the prior finite combined-sink indication, never proof that all memory retention is impossible. Broadening those semantics or qualifying duplicate/corrupted/unattributable channels would need explicit further design/review. Neither authorization flag is changed by this amendment.

## Tests: real API versus mocks versus human execution

The test-only fixture_journal_api.py uses the installed private libsystemd-shared-255 ABI to create disposable native journals. It is gated on exact systemd/libsystemd0 versions, refuses root, and runs under a 15-second subprocess timeout, 5-second CPU limit, 512 MiB address-space limit, 32 MiB file limit and zero core limits. The private writer ABI is not a production dependency and is never installed into the operator path.

Fixtures contain only fixed public test strings and fictional selectors/timestamps/boot data. The native library can put local machine metadata and ordinary random journal identifiers in temporary headers; those stay local, are never printed/committed and are removed with the owned directory. These identifiers are not encryption keys or recovery material. No actual runtime canary, host journal reader, shared journal write, deliberate crash, elevated operation or real secret is involved.

Actual binding tests use the **same Observation.journal method**, not an approximate metadata probe:

- Empty matching set despite a valid restorable anchor.
- Seven individual selector cases through the complete production disjunction construction.
- Matching positive bytes and oversized-field rejection.
- One duplicate-field limitation demonstration.

This is **11 isolated native cases** within one unittest, not 11 protected-host trials. On an unsupported private ABI the test explicitly skips; that cannot be counted as qualified. Here all 11 executed and passed.

Focused mocked regressions cover API failures at every traversal operation, initial/final invalidation, final append, unavailable anchor, inclusive timestamp boundaries/wrong boot, required/optional missing fields, unsupported representations, threshold handling, record/byte/time limits, positive preservation, sanitized publication and unchanged security functions. These mocks are fault injection, not evidence of actual host conditions.

Full validation at handoff: **229 automated tests PASS**, including the 11-case native test; no skips. Candidate strict visudo parsing PASS. Checkpoint shell syntax and inert activation/rollback regressions PASS. Repository documentation/secret-pattern validation is recorded below and in the completion report. No protected crash trial or privileged installation was executed by the agent.

See [the separate independent review](JOURNAL_REVIEW.md) for findings and disposition.

Additional validation actually run:

| Check | Result | Limit |
| --- | --- | --- |
| All qualification shell blocks | 32 syntax checks PASS | No installation block executed; current activation/rollback exercised only with inert command doubles |
| Markdown and local links | 69 documents / 294 links PASS | Nine Mermaid blocks structurally checked; no renderer installed |
| Common-secret-pattern scan | 96 nonignored working-tree files, index and 170 pre-amendment reachable history blobs PASS | Matching values suppressed; staged/final history rechecked before publication; not a proof against every secret format |
| Dedicated scanners | gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck and mmdc unavailable | Nothing installed; no dedicated scanner success claimed |
| GitHub Actions metadata | Zero runs and zero artifacts | No CI execution or canary upload occurred; functioning CI remains Gate 2 work |
| Whitespace and change scope | git diff --check PASS | Qualification-only source/tests/docs and digest-only project policy change; no application implementation |

## Next human checkpoint and unresolved gates

Use only [the current guarded upgrade](JOURNAL_CHECKPOINT.md), which pins old/new wrapper, harness and policy hashes, validates candidate/aggregate sudo configuration, retains root-only recovery copies and provides rollback. No manual sudoers editing or global policy change. Existing result files are preserved; the fresh exclusive output is /var/tmp/ai-invest-crash-journal.json.

Physical-console command remains sudo /usr/local/sbin/ai-invest-operator-preflight --crash-test. The run can produce finite journal evidence or precise journal stage/reason. Overall coverage_incomplete remains expected even if every implemented check passes. Do not delete prior results to repeat a run.

Still unresolved before real-secret bootstrap: successful protected-context journal observation, explicit acceptance or further treatment of finite observation limitations, separate synthetic human-input/recovery-output testing and all future plaintext-handling contexts. Effective no-swap metadata remains the already-qualified process/time-specific scope, not a raw swap-byte search or proof for unbuilt services. Complete Gate 2 also still needs encrypted storage/TDE/OpenBao/recovery, tenant isolation, broker-simulator reliability and functioning CI/security evidence.

No LUKS/OpenBao initialization, real key/recovery generation, brokerage connectivity, production service deployment, paid services, global logging/sudo/swap/crash changes, reboot or unrelated workload changes. Source remains public; application access remains private/LAN-only. PR #14 stays DRAFT and unmerged.
