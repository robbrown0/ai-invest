# Read-only Log Source Policy and Observer Setup Gate

**Status:** Prepared synthetic-only correction; NOT installed or run on the host by agents. Gate 2 NOT PASSED. Both authorization flags remain false.

## New human evidence and definite mismatch

Human-tested observer commit: **531671a5e6e3bf8c7efc3bddb899c53d53cd1c27**. The owner reports that its local crash checks passed while observation_window, journal, apport_log, crash_store and collector_retention remained NOT_TESTED. This is a reported observer trial, not a new successful collector observation. No complete new JSON is invented from that summary; prior exact artifacts remain unchanged.

Separate bounded SSH metadata supplied by the owner:

| Fixed path | Reported owner:group | Mode | Type |
| --- | --- | --- | --- |
| /var | root:root | 0755 | directory |
| /var/log | root:syslog | 0775 | directory |
| /var/log/apport.log | root:adm | 0640 | regular, empty |
| /var/crash | root:whoopsie | 03777 | directory |
| /var/lib | root:root | 0755 | directory |
| /var/lib/systemd | root:root | 0755 | directory |
| /var/lib/systemd/coredump | root:root | 0755 | directory |

Exact supplied compatibility result:

```json
{
  "journal_import": "PASS",
  "missing_required_methods": [],
  "required_flags_present": true
}
```

This establishes **import/API presence only**, not reader initialization, access, watch/anchor success or runtime observation.

The tested root_path predicate forbids group/other write except its fixed sticky /var/crash case. Its direct /var/log check and its ancestor check for apport.log both necessarily reject root:syslog 0775. This is a **definite source/host mismatch**, not speculation. Because journal setup preceded it and exceptions were collapsed, it is **not proof that this was the first exception or that journal setup succeeded**.

Earlier missing-storage, VT/sudo PTY, tty_identity, operator_environment, environment_path and observer failures remain historical in [the index](README.md), [prior observer qualification](OBSERVATION_QUALIFICATION.md), [prior review](OBSERVATION_REVIEW.md) and their original result artifacts. No canary from an earlier trial is available for retrospective search.

## Trust policy: observation is not executable integrity

The new LogSource is a fixed read-only reader for /var/log/apport.log, not an executable/path loader. Existing wrapper checked_path/checked_bytes, digest verification, operator identity/console/sudo/PATH checks and root_path's separate /var/crash handling are unchanged.

Directory policies:

- Root and /var ancestors: real directories, root-owned, no group/other write; every component opened separately without following symlinks.
- Exactly /var/log through the retained /var descriptor: root:root 0755, root:syslog 0755, or root:syslog **0775**. No other owner/group/mode combination is admitted by this observation policy. Both group IDs are resolved through grp.getgrnam in the local account database; no host numeric GID is invented or exposed.
- /var/crash: the previous root-owned sticky-directory exception stays in root_path, limited to that exact path. It is not reused for logs or installed code.
- apport.log: no-follow regular file, root owner, one link, mode 0600/0640/0644 only. Read-only group access does not establish writing authority; group/other-write, executable/special bits, symlink, hardlink and non-regular objects are rejected. The observed root:adm 0640 case is supported.

Root ownership of a group-writable directory **does not make entries immutable**. A syslog-group directory writer can unlink/rename/substitute entries, rotate a root-owned file it cannot directly write, or hide records before the observer's baseline. Root-owned file metadata alone cannot authenticate all past contents. Assumptions therefore include trusted root/kernel/account database, the pinned collector implementation, and trusted directory-writing logging components/group members. This does **not** defend against a compromised trusted logging service. No logging membership or permissions are changed.

Source contents remain untrusted: no execution, import, evaluation, command construction or arbitrary path following from log/crash data. The directory permission exception cannot be used to load code. No actual directory membership list, environment, historical log body or unrelated crash contents were requested/read by agents.

Mode/group metadata can hide a named-user access ACL with write authority. The held log directory must therefore have **no POSIX access ACL**: getxattr checks only the fixed system.posix_acl_access attribute, accepts ENODATA, and treats a present ACL, unsupported operation or read error as setup failure. Presence is rechecked before/after observation without exposing attribute contents. This is not a group-membership audit: root and local account/group membership administration remain trusted. No ACL is changed. The owner's supplied metadata did not test this predicate, so actual-host ACL/readiness remains unverified.

## Race-aware fixed read-only implementation

LogSource retains descriptors for /, var and log, opened one component at a time with O_DIRECTORY, O_NOFOLLOW and O_CLOEXEC. The named component is checked without following symlinks before/after each open, against fstat of the held descriptor. This avoids relying on O_NOFOLLOW on only a full path's final component. Later checks verify the retained chain's current parent/name bindings and policies.

The file is opened only as literal apport.log relative to the held log dirfd, O_RDONLY/O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC. It is verified as the same regular, root-owned, single-link object through pre-open metadata, fstat and named-entry checks. The held original descriptor is never replaced by opening a newly substituted log. Initial absence is an explicitly supported baseline only after repeated relative absence checks and validated directory/watch state.

Before generation and throughout observation:

- Preserve identity, size, mtime and ctime snapshots. Directory-entry changes, file replacement, permission drift and rotation invalidate absence; atime is excluded because reading may update it.
- Timestamp snapshots alone proved insufficient in an isolated rename-away/back fixture. A separate nonblocking inotify watch is attached to the **held log directory** using only the kernel-provided /proc/self/fd reference, with IN_ONLYDIR and the fixed mutation mask. This is not a caller-selected symlink/path.
- Read at most four 64 KiB event batches per check. Parse complete bounded metadata records; never publish names/IDs. apport.log mutation, directory self-event, overflow, removed/unmounted watch, malformed record, unsupported mask, read error or exhausted budget permanently latches incomplete. Consuming an event never clears the failure.
- Ordinary append events for a different existing log file are ignored as outside this path; their contents are never read. Other directory-entry mutations still conservatively invalidate timestamp checks. Legitimate logging/rotation activity can make this trial incomplete without implying compromise.
- Only bounded new bytes beyond the original file offset are searched. The original FD may still be searched after rotation to preserve a positive attributable match. No replacement or historical body is opened. Short reads/rotation/interruptions cannot support absence; a detected positive in returned complete target records survives later incomplete data. Post-read chain/file/event checks precede every absence PASS.

Open-at directory descriptors address path races described in the [Linux open manual](https://man7.org/linux/man-pages/man2/open.2.html). The [inotify manual](https://man7.org/linux/man-pages/man7/inotify.7.html) describes event queues, overflow and descriptor lifetime. Event monitoring is not an immutable audit ledger: pre-watch concealment, malicious trusted writers, root mount changes, unsupported filesystems and unobserved collector channels remain outside the finite assurance claim. The project uses the observed local filesystem; no network log source is approved.

## Four actionable setup stages — no crash without readiness

The result schema adds exactly four fixed identifiers, using only existing PASS / FAIL / NOT_TESTED enums:

| Identifier | PASS means | Failure/dependency handling |
| --- | --- | --- |
| setup_journal | Actual reader construction, change-watch initialization, current-boot tail anchor and required metadata succeed | Any exception is symbolic FAIL; log/store setup still attempted independently |
| setup_log_directory | Approved local group lookup, pinned directory chain, policy and directory watch succeed | FAIL; setup_log_file stays NOT_TESTED because no trusted prerequisite dirfd exists |
| setup_log_file | Relative open and regular/link/policy/identity validation, or verified absent baseline, succeed | FAIL; unrelated journal/store stages retain their own results |
| setup_crash_store | Existing fixed store/parent checks and watch subscriptions succeed | FAIL; no canary or crashing child |

These are readiness results, not leakage results. Failed stages are listed in fixed order in failed_checks; no exception text, GID, username, arbitrary name/path, record or environment content is returned. Ordinary diagnostic mode remains unchanged. All required stages must be PASS and ready before random generation or the trial's child fork/SIGABRT. The already-protected, canary-free supervisory worker still runs to collect setup safely.

Setup failure leaves crash_signal/dumpable_child/collector observation NOT_TESTED, not PASS. Current process protection checks may still PASS. Cleanup attempts every owned descriptor even if another close fails; cleanup failure remains visible in its fixed category. The 35-second supervisor deadline and scoped resource protections remain unchanged. A kernel-stuck operation cannot be promised cancellable or attributable to one setup stage.

Successful setup continues to the existing ten-second bounded trial without a separate metadata-only console visit. Its finite collector semantics/exclusions remain as documented in [the coverage matrix](OBSERVATION_QUALIFICATION.md). Overall coverage_incomplete remains expected after a successful finite trial; neither authorization flag can become true.

## Regression and independent review evidence

Tests use disposable project-qualified directories with fictional ownership/group metadata, real descriptor-relative reads and isolated directory event watches. They do not chmod/chown the host's log directories, query host log contents, run privileged observer code or generate a runtime canary.

Permanent regressions include:

- Supplied root:syslog 0775 / root:adm 0640 combination; local group resolution, unapproved owner/group/modes, unsafe ancestors.
- Directory/file symlink, hardlink, FIFO and directory substitutions; stat/open races; retained FD and post-read identity checks.
- Rotation, rename-away/back within timestamp granularity, initially absent create/remove, truncation, interruption and mutation/error latches.
- Known positive retained despite rotated/short-read evidence (LP-01); setup failure blocks RNG/fork/SIGABRT (LP-02); event watch closes timestamp-only false-negative gap (LP-03).
- Bounded event parser, overflow/removed-watch/unknown-mask/partial data/read-budget errors and no reset-to-PASS.
- Hidden access-ACL authority, unsupported/failed attribute inspection and ACL change after setup are rejected (LP-04).
- Strict executable/helper validation and sticky crash exception byte-for-byte unchanged; fixed result schema/flags and safe publication.
- Guarded upgrade hashes, shell syntax and inert activation/rollback fault tests.

See [the separate adversarial review](LOG_SOURCE_REVIEW.md). Mocked metadata/API tests and isolated filesystem tests are **not host observation qualification**. Final test/scan results are recorded at handoff and in PR #14.

Actual amendment validation:

| Procedure | Result | Limits |
| --- | --- | --- |
| Full qualification unittest discovery | **210 tests PASS**, no skips; independently repeated | Isolated fixtures and existing safe unprivileged regressions, not a host observer trial |
| Candidate sudoers strict installed parser | PASS | No privileged installation or active aggregate-policy claim; human procedure validates installed state |
| Qualification Bash code blocks | **28 syntax checks PASS** | Not executed; current fixed activation/rollback also simulated with inert command doubles |
| Markdown/link validation | **66 documents / 280 local links PASS** | Nine unchanged Mermaid blocks received structural checks only, no full renderer |
| Common-secret-pattern validator | **91 nonignored source files**, index and **157 pre-amendment history blobs PASS**; values suppressed | Pattern detection only; staged/final commit history rechecked before completion; no vanished runtime-canary search |
| Dedicated scanner availability | gitleaks/trufflehog/bandit/semgrep/trivy/shellcheck/mmdc unavailable | No software installed and no claimed dedicated scanner result |

The agent did not install privileged code/policy, open host logs/journal readers, generate a runtime canary or run the deliberate crash. Actual-host readiness, including the newly explicit access-ACL predicate, remains unverified.

## Next checkpoint and remaining blockers

Use [one guarded upgrade and console run](LOG_SOURCE_CHECKPOINT.md), not older installation blocks. New result is /var/tmp/ai-invest-crash-log-source.json. All previous artifacts, including /var/tmp/ai-invest-crash-observation.json, remain untouched.

Still unverified: corrected observer initialization on the actual host, journal access beyond API presence, current bounded collector/log results and the logging trust assumptions. Future human secret-input/recovery-output, each service's protections, encrypted storage/TDE/OpenBao/recovery, tenant isolation, simulator reliability and CI remain Gate 2 work. No real-secret bootstrap authorization follows from this correction.

No host logging/sudo/swap/crash policy or membership change; no LUKS/OpenBao initialization, real secrets, brokerage connection, production deployment or paid service. Application remains private-access/LAN-only. PR #14 must remain DRAFT and unmerged; Gate 2 NOT PASSED. secret_entry_authorized=false and runtime_crash_suppression_qualified=false.
