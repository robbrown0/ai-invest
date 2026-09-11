# Independent Review — Bounded Crash Observation

**Disposition:** No blocking finding remains for the reviewed **bounded non-secret human checkpoint only**. This is not runtime qualification, secret-entry approval or Gate 2 approval.

## Independence and evidence boundary

The reviewer did not author the harness, wrapper, sudo policy, tests or human installation procedure. This document is the reviewer's only repository edit. Review included AGENTS.md, the prior crash implementation/checkpoint/review, the supplied human result, the revised observer and its inert regressions. No host logs or crash contents were read; no privileged installation, runtime canary generation, deliberate crash, secret operation or service deployment was performed by the reviewer.

The result supplied for commit 5975603575b6761fb44932b84dc1519676639584 is one human-observed trial: eleven implemented local checks PASS, none FAIL, remaining categories NOT_TESTED. Re-reading that artifact is not an independent trial. Earlier prerequisite and console/environment failures remain historical evidence.

## Independent findings and resolutions

| Finding | Challenge | Disposition |
| --- | --- | --- |
| OB-01 | A journal field-size check that ignores the field name and equals sign can accept threshold-truncated data | Corrected: full FIELD=value length must remain below the configured threshold. A positive match is preserved even if later evidence is incomplete. |
| OB-02 | A collector PID is not pinned like the unreaped crashing child; attributing every line with that PID can inspect a reused process's messages | Corrected: only exact target-PID marker lines are searched. Other new Apport activity makes evidence incomplete; no historical log body is read. |
| OB-03 | python-systemd 235 _get_all uses an enumeration macro that can end on an error and return a partial dictionary without surfacing the error | Corrected: fixed individual _get calls distinguish missing fields from read errors. The claim is narrowed to the reviewed fixed fields, not every journal byte. |
| OB-04 | A final partial Apport record could erase an already detectable positive match in an earlier complete record | Corrected: complete records are examined and a positive match survives a later partial/malformed record. Partial data never supports an absence PASS. |
| OB-05 | WCOREDUMP=false, an empty child-only query or one expected crash filename cannot establish collector non-retention | The observer includes independently attributed collector fields, new-tail metadata and directory event watches. Any activity/unsupported observation remains incomplete. A proposed collector PASS means only no observed indicator in the specified finite window and sinks. |
| OB-06 | In systemd 255, process() returns NOP without initializing journal inotify; opening/seeking alone could miss newly rotated journal files | Corrected: fileno() must initialize the notification mechanism before the anchor and generation; initialization failure leaves observation incomplete. Regression verifies ordering and failure. |
| OB-07 | Child-side high-level cleanup of an inherited journal object is origin-sensitive and does not establish closure of inherited descriptors | Corrected: the child closes only its own raw descriptor references through detach(-1), never invoking the inherited reader's cleanup. Version 255 has an origin/PID guard, so shared-watch removal is not recorded as an observed or confirmed defect. |

The installed binding is python3-systemd 235-1build4 with libsystemd0 255.4-1ubuntu8.17. The reviewer checked installed API documentation without opening journal records and examined [versioned reader source](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c). Individual _get exposes errors except ENOENT, which becomes KeyError; monotonic timestamps are microseconds and boot identifiers are bytes. Repeated field instances and arbitrary fields are outside the fixed-field claim.

The [systemd 255 journal implementation](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c) supports OB-06 and the origin-sensitive close analysis; its [origin helper](https://github.com/systemd/systemd/blob/v255/src/basic/origin-id.h) binds objects to their creating PID. Library discovery can ignore some directory errors, so a valid notification descriptor does not prove every possible journal file was accessible. The finite result assumes a functioning trusted local journal store, not exhaustive forensic coverage of undiscovered/corrupt files.

## Threat-model assessment

- Canary material remains inside the protected worker and its fork child. Protections precede generation, the observer library is loaded first, and process/thread/cgroup checks are repeated. No external process receives the comparison material. Python copies may exist in protected memory; zeroization or physical RAM erasure is not claimed.
- The crashing PID remains unreaped through observation, preventing numeric PID reuse during attribution. Cleanup retains pidfd identity and deadlines. Child raw observer-descriptor references are closed before the crash without high-level library cleanup; the parent retains its handles and performs normal cleanup. SIGABRT or os._exit avoids Python object teardown in the child.
- Journal groups are OR clauses, each containing boot identity AND one exact process/scope selector. Kernel/collector records with no reviewed attribution field, duplicate field instances, delayed records and arbitrary record fields are outside the claim. No broad kernel-message scan is introduced.
- Apport access is limited to a cursor captured before generation and bounded new bytes. Unrelated historical contents are excluded. Unattributed new activity is conservatively incomplete, not searched as target payload and not called a leak.
- Directory watches read event metadata, not crash contents. Any event, overflow or directory replacement makes evidence incomplete. This avoids guessing a single report filename when Apport may identify a script rather than its interpreter.
- Source/dataflow exclusions for application logs, CI, Git, shell history, sudo logging and own temporary files apply only to this fixed in-memory harness. They are not runtime searches and waive no future application, service or human-input requirement.
- Effective cgroup no-swap evidence is retained separately. No raw swap or unrelated process memory is read. Generated bytes do not qualify a typed passphrase or recovery-output path.
- Ambient root/kernel integrity remains trusted. Private mount propagation is not a filesystem access sandbox. The observer adds fixed read-only metadata/log observation, not a generic command runner or new sudo argument.

Both secret_entry_authorized and runtime_crash_suppression_qualified must remain false. Overall coverage_incomplete remains expected even if bounded observation succeeds.

## Human upgrade and rollback assessment

The reviewer read the complete [current guarded checkpoint](OBSERVATION_CHECKPOINT.md) and [coverage matrix](OBSERVATION_QUALIFICATION.md). The installation block checks clean expected checkout, exact old/new hashes, protected ownership/permissions/ancestry, single links and absent staging targets. Candidate policy and existing aggregate configuration are parsed before activation; the installed aggregate is parsed afterward. Root-only copies are rechecked before use. Source-to-candidate substitution therefore cannot quietly bypass the reviewed hashes.

Caught activation failures restore policy first and independently restore wrapper and harness; complete restoration is reported only when all three legs succeed. Three-file activation is not atomic. Power loss, uncatchable termination, I/O failure and concurrent privileged changes remain explicit limitations. A restored old helper may refuse the newer checkout. No pin bypass is authorized.

The fresh fixed result path preserves the earlier human artifact. Exclusive publication and enum validation remain unchanged. Deliberate rollback removes only the exact reviewed project sudo drop-in, validates the aggregate and tests ordinary sudo access/TTY behavior; it does not modify global sudo, swap or crash policy. The owner uses existing administrator authority to install, not a new installer/root-shell grant.

The policy diff changes only command digests. Its two exact command/argument grants, password and environment requirements and command-specific PTY exception are unchanged. The wrapper diff changes only helper pin, three result categories and the fixed fresh output path. Runtime effective policy and observation still require the human checkpoint.

## Validation in this review pass

| Independent procedure | Actual result | Evidence boundary |
| --- | --- | --- |
| Full qualification unittest suite | **177 tests PASS**, zero skips | Includes final journal-notification/fork-descriptor and guarded-upgrade activation/rollback regressions; inert observer/crash doubles and existing safe regressions; no runtime canary, host log query or crash |
| New observer suite, separately executed | **28 tests PASS** at that review snapshot | Harmless positive/negative fixtures validate detector/parser logic, not the live collector transport |
| Installed visudo strict candidate parsing | PASS | No policy installed |
| All four Bash blocks in current checkpoint, bash -n | **4 PASS** | Syntax only; no commands executed |
| Reviewed artifact/checkpoint hashes | PASS | Future installed bytes still require human validation |

Reviewed harness SHA-256: 68fc9bcea6fecb98a2436992f3cc13c4a4b582a39ac867d025b5bc0fc3f66927.

Reviewed wrapper SHA-256: f339e600891fcb864d50014e684c7f63d90d7dcba04612ef20336ad10644eecd.

Reviewed policy SHA-256: 3864c8d21dfad3efbb6c90dc56eba55f33788a5f79329fbb6f5e99b5224a7913.

The remaining blockers are actual bounded observer evidence and human review of its finite exclusions, the separate synthetic human-input/recovery-output path, service-specific plaintext protections and later explicit secret-bootstrap authorization. No real secret was generated and no LUKS/OpenBao initialization, brokerage connectivity or production deployment occurred. PR #14 remains required to stay DRAFT and unmerged; both authorization flags remain false.
