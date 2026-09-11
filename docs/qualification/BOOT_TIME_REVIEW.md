# Independent Review — Journal Boot and Time Boundary

**Disposition:** No blocking finding for one further non-secret, fail-closed diagnostic checkpoint. The demonstrated seek compatibility problem remains open; this is not approval of complete journal observation, secret entry, crash-suppression qualification or Gate 2.

## Independence and evidence

The reviewer did not author the observer, wrapper, fixtures, tests, policy or installation procedure. This review document is the reviewer's only repository edit. Review covered AGENTS.md, the human-tested 24310834 implementation, the supplied result excerpt, production journal traversal, existing and expanded isolated native fixtures, version-specific sources and the focused amendment.

The reported human result identifies timestamp_boot / attribution_mismatch, which previously combined three predicates. It does not identify which predicate failed. The earlier empty SSH probe did not exercise a matching record. **The exact protected-host cause remains unresolved.** The native reproduction below establishes a real compatibility problem, not retrospective identification of the human event.

No review operation opened a host journal reader, read historical host messages, wrote to a shared journal, generated a runtime canary, deliberately crashed a process, installed privileged files or changed host configuration. Native test strings are fixed public fixtures, not secret material.

## Findings and disposition

| Finding | Independent challenge | Disposition |
| --- | --- | --- |
| BT-01 | Header boot mismatch, pre-window record and reversed interval shared a reason, concealing the next actionable boundary. | Three fixed reasons distinguish them. Harness and wrapper reject arbitrary diagnostic values. Record boot and lower-time checks remain enforced before payload extraction. |
| BT-02 | Installed v255 can return a pre-window match after monotonic seek, including a previous-run scope record from another journal file. | Independently reproduced. The observer still refuses with record_before_window; no tolerance, skipped attribution, expanded query or resource-limit increase is introduced. This compatibility limitation remains unresolved. |
| BT-03 | Checking only floored integer bounds could miss a reversed interval shorter than one microsecond. | Original start/end ordering is also validated before seek. Both ordinary and sub-microsecond reversals are refused as invalid_observation_interval. |
| BT-04 | The indexed _BOOT_ID filter is not the same evidence as the entry-header boot returned by the monotonic API. | A deliberately inconsistent isolated native record reaches the production path and is refused as record_boot_mismatch before any payload read. Header validation was not removed. |

The reviewer considered bounded metadata-only traversal as a possible future workaround for initial-seek fallback. The author retained strict refusal for this checkpoint. That conservative choice is acceptable: correct traversal across files, ordering anomalies and limits would require its own coverage proof, and the human event still does not distinguish its three possible causes. This amendment must be described as **diagnostic refinement plus compatibility reproduction**, not as a completed fix for the library behavior.

## Clock, API and ordering assessment

Local read-only version inspection confirmed systemd/libsystemd0 255.4-1ubuntu8.17 and python3-systemd 235-1build4. Python reports clock_gettime(CLOCK_MONOTONIC) for time.monotonic. The protected parent obtains start after setup and end after its bounded wait; both use that clock. Integer conversion represents their bounds in microseconds. Inclusive comparisons retain records at both endpoints; flooring has microsecond-resolution conservatism, not a configurable time tolerance. The separate wall/monotonic elapsed-time sanity check does not select journal records. No evidence implicates timezone or NTP.

The [v235 raw binding](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c) passes an unsigned microsecond timestamp into seek and returns header microseconds plus 16-byte boot data. It does not apply high-level datetime/timedelta conversions on this path.

The [v255 seek documentation](https://github.com/systemd/systemd/blob/v255/man/sd_journal_seek_head.xml) describes selection of the following entry when next follows a timestamp seek. However, [v255 find_location_for_match](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c) falls back to a direction-based data entry when its monotonic lookup returns zero. Initial LOCATION_SEEK selection is not subjected to the later discrete-position comparison. This provides a versioned explanation for the independently reproduced pre-window results; it is not a claim that older records are universally expected or safe to accept.

The actual production sequence is exercised: restore a cursor, build all seven boot/process/scope disjunctions, seek, advance and read header metadata. Isolated readers open only explicit temporary files. Earlier-run scope records and multiple boots/files are represented. Payload-access guards reject reads outside the selected header boot and inclusive interval.

## Completeness and residual risk

The split-file fixture containing old scope metadata and a genuine current positive stops incomplete before reaching that positive. This is a known coverage limitation, **not a false absence PASS and not successful positive detection**. Within supported single-file/current-window cases, positives at both endpoints and through every selector are detected. A pre-window-only test passes when it reproduces the expected refusal; that does not mean the journal category passed.

Final invalidation/append handling, time/record/byte limits and immediate preservation of already observed positives remain required. Missing evidence never becomes absence. Existing fixed-field, first-value, trusted-journal/root/kernel and finite-window limitations from [the prior review](JOURNAL_REVIEW.md) remain unchanged. The fixture cannot establish protected reader state, actual host journal topology, historical record contents or the human event's exact predicate.

Both authorization flags remain false. No real-secret bootstrap is permitted. PR #14 must remain draft and unmerged; Gate 2 remains NOT PASSED.

## Independent validation

The reviewer independently executed the installed-binding fixture during development (11 prior API cases plus 21 boundary scenarios), then repeated the final **35-case** fixture (11 prior plus 24 boundary scenarios). These were isolated native API executions, not mocked host evidence or protected-console trials. The pre-window and header/field mismatch results were observed directly in the fixture. Every final expected outcome is asserted; known refusal cases are not mislabeled as completed observations.

| Independent validation | Actual result | Limit |
| --- | --- | --- |
| Focused diagnostics, boot/time and native-binding unittest classes | 24 tests PASS, no skips | Includes mocked faults and isolated native records, not a host crash trial |
| Final complete qualification suite | 240 tests PASS, no skips | Includes 35-case native fixture and inert installation/rollback fault tests |
| Final native fixture, separately repeated | 35 cases PASS | Expected incomplete cases reproduce refusal, not absence |
| Current checkpoint shell syntax | Four Bash blocks PASS | Parsed only; no installation/rollback command executed |
| Current harness/wrapper/policy hashes against checkpoint | PASS | Installed state remains a human check |
| Candidate strict visudo syntax | PASS | Candidate only; no global sudo change or aggregate host-policy read |
| Whitespace | git diff --check PASS | Not a secrets-scanner result |

The [guarded checkpoint](BOOT_TIME_CHECKPOINT.md) was read in full. It preserves earlier result files and uses a fresh exclusive boot-time result. Old/new reviewed hashes, root ownership, modes, link checks, root-only recovery copies, candidate/aggregate syntax validation and caught-failure restoration are retained. Policy changes only the command digest; its exact arguments, PASSWD/NOSETENV and command-scoped PTY behavior remain unchanged. Ordinary sudo verification and deliberate rollback are human-only. Three-file replacement is explicitly non-atomic; power loss, uncatchable termination, I/O failure and concurrent root tampering are not falsely covered by shell traps. No broader privilege grant or generic runner was added.

Reviewed SHA-256 values:

- Harness: d2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595
- Wrapper: 7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f
- Policy: a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06

No protected-host trial or privileged installation was performed by the reviewer. No blocking review finding remains for the stated strict synthetic diagnostic checkpoint; the known seek compatibility issue and unresolved actual-host condition remain explicitly open.
