# Independent Review — Bounded Journal Observation

**Disposition:** No blocking finding remains for the reviewed non-secret human checkpoint only. This is not host observation qualification, secret-entry authorization or Gate 2 approval. The protected-host failure remains unresolved and the broader absence limitations below remain material.

## Independence and evidence boundary

The reviewer did not author the observer, wrapper, tests, policy or installation procedure. This review document is the reviewer's only repository change. Review covered AGENTS.md, the human-tested 55339d0 implementation, the supplied human observations, installed API docstrings, upstream version-specific binding/library implementation, the focused diff and isolated regressions.

The latest human trial reportedly passed setup, local protection/crash/cleanup, observation_window, apport_log and crash_store while journal and collector_retention remained NOT_TESTED. The separate empty metadata probe establishes only the operations it actually exercised. Neither report identifies the earlier failing journal operation. Re-reading either is not another trial.

**The actual protected-host journal failure remains unresolved.** The new isolated native fixtures pass both empty and matching paths. This rules out several simple API/type/filter assumptions in that fixture context; it does not prove what happened inside the protected process or exclude journal invalidation during that earlier trial.

No reviewer operation opened a host journal reader, read historical host logs or crash contents, wrote to shared journals, generated a runtime canary, deliberately crashed a process or installed privileged code/configuration. Public fixture strings are not the random trial canary.

## Findings and disposition

| Finding | Independent challenge | Disposition |
| --- | --- | --- |
| JR-01 | Collapsed exceptions made API, attribution, field and completeness failures indistinguishable. | Fixed symbolic stage/reason fields are now preserved through finish and independently allowlist-validated in both harness and wrapper. Raw exceptions, field values, identifiers and canary data cannot be published through these fields. |
| JR-02 | Reaching an entry after the observation end returned PASS without checking final invalidation. | Corrected: both EOF and later-timestamp exits converge on final change processing. Regressions cover INVALIDATE in both branches. |
| JR-03 | Accepting final APPEND could miss an in-window record delivered after traversal reached EOF. | Corrected following review: initial APPEND is allowed, but final APPEND is incomplete with append_pending. A later checkpoint may remain incomplete on a busy journal; no automatic retry or weakened absence claim is substituted. |
| JR-04 | Generic budget reporting and tuple-unpacking failures could hide the next actionable boundary. | Corrected: record, byte and time limits have distinct fixed reasons; unexpected timestamp container/element representations are separated from API exceptions. The native struct-sequence remains supported. |
| JR-05 | Fixed-field _get reads the first duplicate value, and libsystemd can internally skip malformed backing data. | Explicit residual limitation, not a claimed fix or demonstrated human failure. An added native fixture directly demonstrates first-value-only behavior; it is not an absence PASS. API-visible first-value checks are not exhaustive enumeration or journal-integrity proof. Broader absence/secret-bootstrap claims must not rely on them alone. |

These corrections tighten completeness and reporting; they do not establish the protected-host root cause. Positive detection returns FAIL immediately before later incompleteness can erase it. A positive seen before full attribution is a conservative failure, not proof that a particular collector retained it.

## API and false-negative assessment

The installed raw binding and high-level Reader are not interchangeable. Version-specific source shows that raw _get returns bytes despite its stale str docstring, _get_monotonic returns microseconds plus a 16-byte boot identifier in a tuple-compatible struct-sequence, and only KeyError denotes a missing field at the Python API boundary. Other errors must remain incomplete. The actual native fixture exercises these behaviors rather than approximating them with a second observer.

Each of the seven disjunction clauses binds the boot identifier and one process/scope selector. The fixture invokes the production Observation.journal method using the complete filters, cursor restoration, monotonic seek, record extraction and attribution. Independent negative, positive, threshold and failure tests cover both no-match and matching paths. No high-level conversion, shell command, arbitrary filter argument or journal-derived executable is introduced.

The two-second query budget is checked across iteration and fields; record and aggregate-byte limits remain bounded. Every absence exit checks final change state and time. Missing required attribution, unsupported field shape, threshold-sized data, cursor loss, invalidation, pending append or exhausted limits cannot produce an absence PASS. An optional missing field is distinguished from an API error.

The result remains finite: selected API-visible fields, selected processes/scope, one boot and one bounded interval. It excludes later asynchronous activity, arbitrary fields/encodings, duplicate values not returned by _get, malformed data silently skipped inside libsystemd, and malicious root/kernel/trusted logging components. Library-level file discovery is not an independent audit of every journal store. Reader initialization, fixture success and WCOREDUMP alone do not prove collector non-retention.

Relevant primary references are the [python-systemd v235 raw reader](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c) and the [systemd v255 journal reader](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c). Test-only native writing follows the [v255 journal-file declarations](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/journal-file.h), not a new production dependency.

## Privilege and fixture scope

Console/session/identity/environment checks, strict executable integrity, private-mount/resource context and log-directory trust code are not redesigned. The wrapper adds only the fixed result schema/path and reviewed helper pin; the sudoers grant remains the same exact two arguments and digest-pinned executable. No generic privileged runner or reader-selected path is added.

The native fixture is test-only, rejects root execution, gates the installed version/ABI, and creates a disposable private journal with harmless fixed records. Its reader opens only that explicit file. CPU, address-space, file-size, core and outer subprocess-time limits bound it. No journal send API or host reader is used. Private systemd writer APIs are intentionally not portable: unsupported versions must skip this fixture, not count as successful qualification. The generated native file is removed with its owning TemporaryDirectory and is not committed.

## Validation actually performed independently

| Procedure | Result | Boundary |
| --- | --- | --- |
| Focused journal diagnostics and native-binding unittest classes | **16 tests PASS**, no skips | Mocked failure branches plus the real isolated native API fixture |
| Direct bounded native fixture execution | **10 initial cases PASS**; **11 final cases PASS** within the full suite | Seven complete filter clauses, empty match set, positive match, field threshold and added duplicate-value limitation reproduction; not a protected-host trial |
| Complete qualification suite | **229 tests PASS**, no skips | Independently repeated after current pins/checkpoint integration; mocked failures and isolated fixtures remain distinct from actual-host observation |
| Current guarded checkpoint | **4 Bash syntax checks PASS**, plus inherited inert activation/rollback fault tests within the suite | No installation block executed |
| Installed visudo strict candidate parser | PASS | Candidate only, not installed aggregate policy validation |
| Current harness, wrapper and policy hashes | PASS against the checkpoint | Installed artifacts still require the guarded human procedure |

The [current guarded upgrade](JOURNAL_CHECKPOINT.md) preserves prior evidence/result files, checks old and new reviewed hashes and protected file properties, validates candidate and aggregate sudo syntax, keeps root-only recovery copies and restores the prior three-artifact state on caught activation failures. The digest-only policy diff grants no new command or argument. Power loss, uncatchable termination, concurrent root tampering and I/O failure remain explicit non-atomic-upgrade limitations. Deliberate rollback removes only the project exception and verifies ordinary sudo; it does not alter global use_pty. The fresh result is exclusively created; documented retrieval checks non-symlink, owner, mode, link count and regular-file properties before display.

Reviewed SHA-256 values:

- Harness: e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3
- Wrapper: 93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52
- Policy: 7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545

Both authorization flags remain false. Future human input/recovery output, per-service plaintext handling, complete leakage assurance and explicit later human authorization remain separate blockers before real-secret bootstrap. No LUKS/OpenBao initialization, brokerage connectivity or global host change is authorized. PR #14 remains DRAFT and unmerged; Gate 2 remains NOT PASSED.
