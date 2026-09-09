# Independent Review — Read-only Log Source Boundary

**Disposition:** No blocking finding remains for the reviewed **non-secret human checkpoint only**. This is not actual-host observer qualification, secret-entry authorization or Gate 2 approval.

## Independence and evidence boundary

This reviewer did not author the implementation, tests, sudo policy or installation procedure. This review document is the reviewer's only repository edit. Review covered AGENTS.md, the observer at human-tested commit 531671a5e6e3bf8c7efc3bddb899c53d53cd1c27, its prior qualification/checkpoint/review, the supplied bounded host evidence, and the focused correction and regressions.

The reviewer read no host log or crash contents, opened no actual journal reader, generated no runtime canary, deliberately crashed no process and installed no privileged code or configuration. Test filesystem/event activity was confined to disposable fixtures; fictional ownership/group metadata does not qualify the actual host.

## Confirmed mismatch and limits

The original strict root_path predicate necessarily rejects the supplied root:syslog 0775 /var/log directory, both directly and as an apport.log ancestor. That is a definite implementation/platform mismatch. Because earlier setup exceptions were collapsed, it does not prove that this was the first encountered exception or that journal initialization succeeded. The supplied journal probe proves import/API presence only. Earlier failures and human results remain historical evidence; no new host trial is inferred from reading them.

## Findings and disposition

| Finding | Challenge | Resolution and regression evidence |
| --- | --- | --- |
| LP-01 | A short read containing an attributable positive prefix could fail the length check before detection, discarding a positive as merely incomplete. | Corrected: inspect returned bounded complete records first; retain a positive before enforcing absence/completeness checks. The focused fixture combines rotation and a short positive read. |
| LP-02 | Failed observer setup previously still allowed random generation and another deliberate crash, while hiding the failing setup boundary. | Corrected: four fixed stages collect independent safe readiness results; file setup depends on validated directory setup. Any missing required readiness stops before RNG and trial-child fork/SIGABRT. Every stage has a no-generation/no-crash regression and bounded-report checks. |
| LP-03 | Identity and timestamp snapshots alone can miss rename-away/back within timestamp granularity; this occurred in the author's isolated fixture. | Corrected: inotify is anchored to the held log-directory FD before readiness. Target mutation, invalidation/overflow, parser/read errors and incomplete draining latch failure permanently. Isolated rename-back, absent create/remove, malformed-event and consumed-event regressions pass. This is not an immutable audit ledger. |
| LP-04 | An approved group/mode can hide additional effective writers through a named-user POSIX access ACL. Assuming only syslog writers from mode bits would overstate the boundary. | Corrected following independent challenge: the held log directory must have no extended access ACL, accepting only ENODATA from the fixed metadata check. Present, unsupported or unavailable ACL metadata fails closed; pre/post checks and ACL-change regressions cover drift. No ACL is modified or published. |

The reviewer independently challenged positive preservation, directory-write authority, snapshot-only races, cleanup after partial setup, ACL assumptions and privilege separation. All four findings are resolved in the reviewed source. Duplicate imported test classes were also removed so discovery counts are not inflated by incidental imports.

## Read-only trust boundary assessment

The exception is confined to the fixed observation path: /var/log must be root-owned and root:root 0755, root:syslog 0755 or root:syslog 0775. Group IDs come from the local account database. Root and /var retain non-group/other-writable ownership/type checks. Literal apport.log requires a root-owned regular single-link non-executable file with no group/other write. Symlinks, hardlinks and unsupported objects are refused.

Every ancestor is opened separately through retained directory descriptors with no-follow handling, rather than trusting only a final-path O_NOFOLLOW. Named and held objects are compared before and after opens/observation. The file reader keeps its original descriptor and never opens a replacement merely to recover a passing result. Inotify follows only the kernel-generated reference to this process's held directory FD, not a caller-selected path. Bounded event metadata and appended content remain local and untrusted; neither is executed, evaluated, imported or converted into a command.

Directory writers can remove or substitute entries they cannot directly modify. Root, the account database, approved logging-group members and the installed logging components remain trusted; this design does not resist a compromised trusted logging service, deliberate pre-baseline concealment or root/kernel tampering. Group membership is not audited. Access-ACL absence prevents silently admitting extra ACL writers, but is not proof those trusted components are uncompromised.

A changed target, rotation, truncated read, unsupported observation or lost watch cannot yield an absence PASS. Legitimate logging/rotation may leave coverage incomplete. Ordinary append events for other existing log files are not interpreted as Apport activity; their contents are not read. Broader unrelated directory-entry mutation remains conservatively incomplete. Known targeted positives survive incomplete subsequent evidence.

Strict wrapper checked_path/checked_bytes and the existing root_path implementation remain byte-for-byte unchanged. The sticky /var/crash exception is not generalized. Wrapper changes are the helper digest, fresh result path and fixed setup-result schema; the sudoers change is digest-only. Console/session authentication, exact two command arguments, clean environment, PATH independence and unrelated sudo PTY behavior are not redesigned or widened.

## Setup, cleanup and human checkpoint assessment

The four identifiers are fixed: setup_journal, setup_log_directory, setup_log_file and setup_crash_store. Actual reader/watch/anchor setup is required for setup_journal PASS. Independent failures are collected together; a dependent unattempted file stage is NOT_TESTED. No arbitrary exception, file path, ACL content, group ID or environment value can be included in these reports. Cleanup attempts remaining owned resources after a close error. Both authorization flags and overall checks_passed remain false.

The complete [guarded upgrade](LOG_SOURCE_CHECKPOINT.md) was reviewed. It verifies expected old/new hashes, protected ownership/modes/links/ancestry, clean intended checkout and absent fresh staging/result targets. Candidate and existing aggregate sudo syntax are checked before activation; installed aggregate syntax is checked afterward. Fixed root-only recovery copies and caught-failure rollback preserve the prior policy, wrapper and harness independently. Activation is not atomic; power loss, uncatchable termination, concurrent root modification or I/O failure remain explicit limitations, not automatic-recovery promises.

The new fixed result path preserves both earlier crash artifacts. Publication remains exclusive and schema-bounded. Documented retrieval checks the fixed file's non-symlink/root-owner/mode/link/type properties before display. Deliberate rollback removes only the exact reviewed project sudo drop-in and checks normal sudo access/TTY behavior; it does not weaken global sudo or logging. No privileged change was installed by this reviewer.

## Validation actually performed independently

| Procedure | Result | Boundary |
| --- | --- | --- |
| Full qualification unittest discovery on final reviewed source | **210 tests PASS**, no skips | Isolated fixtures and existing safe regressions; no actual observer/canary/crash run |
| Earlier targeted log/setup tests | **28 tests PASS** | Interim fixture-only review before the final ACL additions |
| Current checkpoint's four Bash blocks | **4 syntax checks PASS** within the suite | Commands not executed; inert activation/rollback fault cases also pass |
| Installed visudo strict candidate parsing | PASS | Candidate only; no host policy installation or aggregate-policy qualification |
| Three executable/policy hashes and checkpoint references | PASS | Installed bytes must still be verified by the human upgrade |

Reviewed SHA-256 values:

- Harness: 8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420
- Wrapper: 0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf
- Policy: 0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8

Actual-host readiness, access-ACL/watch support, journal access and bounded collector/log observation remain unverified. Separate synthetic human-input/recovery-output assurance, every future plaintext-handling service's protections and explicit later human authorization still block real-secret bootstrap. No real secret, LUKS/OpenBao initialization, brokerage connectivity, production deployment or global logging/swap/crash change occurred. PR #14 must remain DRAFT and unmerged; Gate 2 remains NOT PASSED; secret_entry_authorized=false and runtime_crash_suppression_qualified=false.
