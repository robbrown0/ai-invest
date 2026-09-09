# Bounded Journal Traversal Compatibility Correction

**Status:** Prepared synthetic-only correction, not installed or run in the protected host context by agents. Gate 2 NOT PASSED. secret_entry_authorized=false; runtime_crash_suppression_qualified=false.

## Confirmed protected-host condition

Human-tested commit: **99dc9d518470bd54db81d6e6a4e26780947db511**. The human ran the reviewed command at the physical console and safely retrieved this excerpt (not the complete schema):

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
    "journal_reason": "record_before_window",
    "collector_retention": "NOT_TESTED"
  },
  "runtime_crash_suppression_qualified": false,
  "secret_entry_authorized": false
}
```

Existing runtime protection/crash/output/cleanup checks also passed, per the owner. In that source, valid interval, representation and entry-header boot checks precede record_before_window. **This establishes a correctly typed same-boot record earlier than the lower bound**, not its identity, originating process or the precise internal library branch.

The full /var/tmp/ai-invest-crash-boot-time.json remains untouched. Agents did not reread it, inspect old record bodies or request another diagnostic-only run. This is one human trial. [Earlier evidence](BOOT_TIME_QUALIFICATION.md), [earlier review](BOOT_TIME_REVIEW.md), all prior results and [the complete chronology](README.md) remain historical, not rewritten as successful qualification.

## Reproduction first; explicit before/after result

Before editing, author and independent reviewer ran the current native fixture against the unchanged production observer. Its multiple_files case contains one earlier fixed-scope record and a genuine in-window positive in another journal file.

| Same isolated native case | Observer result | Payload/coverage meaning |
| --- | --- | --- |
| Human-tested 99dc9d5 implementation | NOT_TESTED / timestamp_boot / record_before_window | Zero payload reads; current positive was not reached |
| Corrected implementation | FAIL / field_shape / positive_match | Genuine in-window positive detected; excluded historical payload not read |

Here FAIL means successful detection of the harmless injected positive, not a failing regression. The fixture's separate compatibility output is exactly multiple_files=POSITIVE_DETECTED. Test PASS formerly meant expected refusal; that expectation was deliberately updated. Git and the old qualification documents preserve the historical refusal.

## Small production correction

The original one-time cursor restore, seven boot/process/scope disjunctions and monotonic seek remain. Start/end and inclusive integer-microsecond boundaries are unchanged. No earlier start or tolerance is added.

For each returned record:

1. Consume one of the existing iteration slots and check the existing time budget.
2. Read only the raw entry-header monotonic timestamp and boot; validate their representation.
3. Refuse a wrong boot. The indexed _BOOT_ID match is not a substitute.
4. Refuse a negative or decreasing observed timestamp as fixed ordering_ambiguous; equal timestamps remain allowed.
5. If stamp is below lower **or above upper**, advance once without _get or any payload extraction.
6. Otherwise run unchanged fixed-field/size/attribution checks and immediate positive detection.

There is no repeated seek, retry, expanded selector or extra process. record_before_window remains an allowlisted historical reason, but an otherwise valid early timestamp is no longer itself a refusal. Both processes validate the new ordering_ambiguous symbol; raw values are never published.

**The first stamp above upper no longer ends the search.** Only actual EOF can reach the final change/time checks for an absence PASS. INVALIDATE, final APPEND, API errors and resource exhaustion remain incomplete. This avoids relying on a single timestamp to declare every file finished.

## Supported traversal and termination argument

The [v255 reader implementation](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c) provides the relevant behavior: matching monotonic positioning can fall back to an earlier data entry; subsequent discrete traversal advances matching file offsets while retaining other candidate files. Merge comparison can prioritize a shared sequence source before timestamps. This explains why skipping payload at an upper crossing is safer than assuming all files are exhausted.

The supported finite argument is conditional on the already-trusted valid native-file/index and source-sequence semantics:

- Each file begins at its matching seek candidate: at/after lower, or earlier via the reproduced fallback. The query/boot remains fixed.
- Advancing once through the same reader preserves other files' candidates; excluding an old record does not reset the seek or discard another file's in-window candidate.
- Supported same-boot streams have coherent native sequence/index ordering. Observed monotonic regression now refuses; this is not a validator for hidden/corrupt indexes.
- Every returned in-window record receives the existing payload checks unless a detected positive terminates with FAIL or incomplete evidence stops the trial. No excluded record contributes payload evidence.
- Absence requires EOF plus final NOP and remaining time budget. An upper crossing alone is insufficient. If the reader cannot finish, no absence claim is made.
- Every returned record, including pre-/post-window metadata, spends the existing 256-iteration/2-second query budgets. Native tests demonstrate 255 excluded records plus EOF may complete, while 256 without an EOF slot refuse. No limit is increased. The existing 1 MiB aggregate payload cap, field threshold and outer worker deadline remain unchanged.

This source argument is backed by actual native tests, not mocks alone. It does **not** prove arbitrary corrupt or adversarially constructed journal storage is complete. Library-silent malformed-file/record skipping, duplicate values beyond raw _get's first value, arbitrary unqueried fields, delayed/unattributable channels and compromised root/kernel/trusted logging services remain the prior explicit exclusions. An observed ordering anomaly is incomplete; unseen corruption is not claimed detectable. Journal PASS remains finite API-visible fixed-field evidence, not universal collector-memory non-retention.

## Native and mocked evidence

Installed fixture version gates remain systemd/libsystemd0 255.4-1ubuntu8.17 with python3-systemd235-1build4. No package changes occurred. The existing test-only native writer remains unprivileged, version-gated, resource-bounded and confined to owned temporary files; no shared journal or real host log is opened. Harmless fixed strings are not a runtime random canary.

**72 native cases executed**: 11 original API cases plus 61 boundary/traversal cases. The actual production Observation.journal runs through cursor restoration, full filters, seek, iteration, metadata and applicable payload extraction.

Coverage includes:

- Pre-window-only, previous fixed-scope runs, old-then-negative and old-then-positive, both within one file and across files.
- All seven selectors across two files, positive/negative outcomes and both reader discovery orders.
- Independent sequence sources and an explicitly verified shared source; native cursor metadata confirms shared sequence identity locally without publishing it.
- Lower/upper exact endpoints, immediately outside both, fractional endpoints, overlapping boots and header/indexed boot inconsistencies.
- An upper-crossing followed by visible timestamp regression: incomplete, no payload extraction.
- Native pre-/post-window record-budget boundaries: expected completion versus expected refusal.
- Guarded _get forwarding asserts every extracted payload is same-boot and in-window.
- Existing positive, threshold, duplicate-value limitation and empty-result cases.

During review, TR-01 found that a substring-based fixture permutation test confused selector 1 with order 1. The fixture now parses the explicit order token, with a permanent all-selector/order regression. Initial attempts that reversed fixture creation chronology instead of reader order produced a cursor refusal; that was an invalid permutation experiment, not host evidence or a production defect. The corrected experiment reverses reader file order while preserving coherent clock chronology.

Mocked fault tests separately cover metadata-only exclusion, API failure after upper crossing, wrong boot after upper, regressing order, time/record/byte exhaustion, final invalidation/pending append, cursor loss, unchanged selectors/single seek, bounded publication and both false flags. Already detected positives remain FAIL despite later hypothetical incomplete evidence.

Full suite: **254 tests PASS, no skips**, including the 72-case native test. [Independent review](TRAVERSAL_REVIEW.md) records its own before/after runs and disposition. These tests do not qualify the correction in the protected host context.

Final local validation also passed candidate-only strict visudo parsing, 40 documentation shell-block syntax checks, Markdown structure/local-link checks (75 files, 322 links), and common secret-pattern checks over working files, staging and reachable history. Nine Mermaid blocks received declaration/fence checks only, not rendering. Dedicated gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck and Mermaid tooling were unavailable; nothing was installed. These bounded checks are not a claim of exhaustive secret detection or functioning deployment CI.

## Next checkpoint and unchanged gates

Use [one guarded upgrade and rollback](TRAVERSAL_CHECKPOINT.md), not historical installation blocks. The helper/wrapper hashes and exact-command sudo digest are updated; no new grant or authentication/PTY policy is added. Existing result/recovery files remain intact. New exclusive result: /var/tmp/ai-invest-crash-traversal.json.

The next physical-console command remains sudo /usr/local/sbin/ai-invest-operator-preflight --crash-test. It tests this actual compatibility correction, not another diagnostic subdivision. It can complete finite journal evidence, detect a positive, or report an unchanged/new bounded failure. Overall coverage_incomplete can remain even when all implemented checks pass.

Still outstanding: protected-host execution of the correction; human input/recovery-output qualification, wider finite-channel limitations, equivalent controls for future secret-handling services, and original storage/TDE/OpenBao/recovery, tenant isolation, simulator and CI Gate 2 evidence. No secret-entry authorization is inferred.

No privileged installation, protected crash run, real secrets/recovery generation, LUKS/OpenBao initialization, brokerage connectivity, production deployment, paid service, global sudo/logging/swap/clock/crash changes, reboot or unrelated workload changes. Public source does not alter private/LAN-only application access. PR #14 remains DRAFT and unmerged.
