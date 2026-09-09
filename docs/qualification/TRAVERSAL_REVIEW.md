# Independent Review — Bounded Journal Traversal

**Disposition:** No blocking finding remains for the stated non-secret protected-host compatibility checkpoint. This is not approval of secret entry, full crash/leakage assurance or Gate 2. Both authorization flags remain false.

## Independence and scope

The reviewer did not author the production change, fixture, tests, policy or installer. This review document is the reviewer's only repository edit. Reviewed AGENTS.md, BOOT_TIME_QUALIFICATION.md, BOOT_TIME_REVIEW.md, the actual journal method and its native/mocked tests. The supplied human excerpt establishes a correctly typed same-boot record before the observation lower bound; it does not identify the historical message, originating process or exact internal library branch.

The reviewer independently ran the unchanged 35-case native fixture before the correction: multiple_files asserted NOT_TESTED / record_before_window with zero payload reads. That assertion passing was reproduction of the old refusal, not detection of its later positive. The same scenario after correction asserted FAIL / positive_match with payload reads, and the expanded fixture explicitly reports POSITIVE_DETECTED for that compatibility case.

No review operation opened a host journal reader, read unrelated historical messages, wrote shared journals, generated a runtime canary, crashed a process, installed privileged files or changed host configuration. All native records are harmless isolated fixtures, not secrets. Version checks found systemd/libsystemd0 255.4-1ubuntu8.17, python3-systemd235-1build4 and CLOCK_MONOTONIC unchanged.

## Challenges and findings

| Finding | Challenge | Disposition |
| --- | --- | --- |
| TR-01 | The first expanded fixture used a substring to choose reversed discovery order; selector number 1 also matched, so its two requested order variants were not distinct. | Author changed this to explicit structured-name parsing and added a permanent all-selector/order/kind regression. This was a fixture coverage defect, not a production privilege defect. |
| TR-02 | A timestamp beyond upper does not alone establish all matching files have been exhausted. | The early exit was removed. Every returned header consumes the existing iteration/time budget; excluded records receive no fixed-field reads. Absence requires actual EOF plus final change and time checks. |
| TR-03 | Adding continue alone would conceal unsupported ordering and would not demonstrate the hidden positive was reached. | Same-boot visible timestamp regressions now produce ordering_ambiguous, not PASS. Native old-file/current-positive, discovery permutations and shared-sequence-source cases exercise the real observer; unsupported order remains incomplete. |
| TR-04 | Indexed _BOOT_ID is not evidence of entry-header boot identity, including for excluded records. | Header type/boot checks precede ordering and interval exclusion. Header disagreement remains incomplete; in-window indexed-field attribution remains separate. |

There was no request to widen the query or resource ceilings. The reviewer suggested exercising shared sequence sources and both discovery orders, rather than asserting that independent-file examples prove every library ordering. The author adopted those fixture extensions. A monotonic regression refusal is conservative: it can leave a later positive unread, but cannot be presented as an absence PASS.

## Supported traversal argument

For valid native indexes and coherent source sequence data, the reader keeps per-file candidates while advancing the selected file through matching offsets; it merges candidates and suppresses consumed duplicates. Sequence identity can precede timestamp in ordering. The reviewed correction therefore does not use an upper timestamp as EOF. It consumes the bounded iterator, rejecting visible backward timestamps and header boot disagreement. See the [versioned v255 reader](https://github.com/systemd/systemd/blob/v255/src/libsystemd/sd-journal/sd-journal.c).

The compatibility case starts from the existing restored cursor, retains all seven boot/process/scope clauses, performs one unchanged monotonic seek, and advances the actual installed binding. Earlier candidates are excluded by header metadata only; no earlier start, time tolerance, repeated seek, retry, extra selector or payload access is introduced. For the supported valid-file streams, a relevant in-window candidate is reached unless an explicit bound, API/state failure or unsupported-order refusal intervenes. This is corroborated by native fixtures, not source reasoning alone.

Limits are unchanged: 256 iteration slots, two-second traversal deadline, existing field-size/aggregate-byte caps, final invalidation/pending-append handling and outer worker protections. A slot is spent even on an excluded record; 255 excluded records can reach EOF, whereas 256 leave insufficient evidence and refuse. An observed positive returns FAIL immediately and cannot be erased by later incomplete evidence. Wrong boot or unsupported order is never converted into successful absence.

Clock origin and inclusive integer-microsecond endpoints are unchanged. Original interval validation remains before seeking. The monotonic header and indexed boot are checked for different purposes. Out-of-window field values are deliberately not extracted, so old record contents cannot be claimed searched; only in-window returned fixed fields support the scoped observation.

## Limits of the claim

Native fixtures exercise the installed binding against explicit temporary journals, not the protected host's actual topology. A successful fixture cannot establish the next console trial's result or reconstruct an earlier record. The reader's API-visible valid-storage view remains the scope: library-silent malformed-file/index omissions, duplicate-field first-value behavior, hidden/inaccessible storage, compromised trusted logging/root/kernel, delayed records after the finite window and future secret input/output are not newly qualified. The fixture explicitly retains duplicate-field and malformed-record limitations.

The correction increases neither host access nor observation bounds. Walking additional already-filtered headers within the unchanged budget is intentional; it does not permit historical payload inspection. Both flags remain false, Gate 2 remains NOT PASSED and PR #14 must remain draft and unmerged.

## Independent validation and handoff

The reviewer independently executed the historical 35-case refusal reproduction, corrected same 35 cases, expanded 72 native cases, then repeated focused and complete regression validation after the fixture-order correction. Expected incomplete/refusal cases are not journal PASS.

| Independent check actually executed | Result | Limit |
| --- | --- | --- |
| Final focused diagnostic/boot/traversal/native tests | 35 tests PASS, no skips | Mocked faults plus real installed-binding isolated files, not a protected trial |
| Final entire qualification suite | 254 tests PASS, no skips | Includes 72 native cases and inert install/rollback fault tests |
| Native compatibility case before/after source change | Prior expected refusal; revised positive detected | Same old-scope/current-positive split-file scenario; no host messages |
| Candidate strict visudo parsing | PASS | Candidate file only; no host aggregate policy change |
| Guarded checkpoint Bash blocks | Four syntax checks PASS | No installation, rollback or console command executed |
| Current artifact hashes against checkpoint | PASS | Actual installed files remain a human check |
| git diff --check | PASS | Not an independent secrets scan |

The [current checkpoint](TRAVERSAL_CHECKPOINT.md) was read in full. It preserves all existing result/recovery files, uses a fresh exclusive traversal result path, validates old and new hashes and root ownership/modes/links, and keeps candidate/aggregate sudo validation and caught-failure restoration. The existing three-file upgrade is explicitly non-atomic; power loss, uncatchable termination or root tampering is not covered by shell traps. The final ordinary sudo check and guarded project-only rollback remain human steps. Policy changes only the wrapper digest; exact commands/arguments, PASSWD/NOSETENV and command-specific PTY exception remain unchanged.

Reviewed SHA-256 values:

- Harness: 688b64b9c0659a34e7926091345c5734763bb2d8a53f75ed3a05edde3f749377
- Wrapper: 17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5
- Policy: 92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832

No protected runtime trial or privileged installation has been performed by the reviewer. Human qualification remains necessary; no real-secret bootstrap follows from this review.
