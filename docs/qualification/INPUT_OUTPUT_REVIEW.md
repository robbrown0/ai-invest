# Independent Synthetic Input/Output Candidate Review

**Disposition:** No blocking finding for committing the **unwired candidate library and local tests**. This is not approval to install a new sudo grant, run a privileged interactive checkpoint, handle real secrets, or claim input/output qualification. Gate 2 remains NOT PASSED; both authorization flags remain false.

## Independent scope and evidence

The reviewer did not author the candidate implementation or its tests. Review covered AGENTS.md, the current wrapper/crash observer, exact sudo policy, existing observation/traversal evidence, terminal_exchange.py, test_terminal_exchange.py, and the final [qualification criteria](INPUT_OUTPUT_QUALIFICATION.md) and [approval checkpoint](INPUT_OUTPUT_CHECKPOINT.md). The current protected console/identity/environment/journal design was not reopened.

The latest owner-reported trial at 46ce2ac030b69c70cfbbf01c7b238289f205a134 closes the finite collector/logging observation for that exact internally generated canary design under its published assumptions. It is one human observation, not an independently repeated review run or proof of this new interactive path. The reviewer did not read or alter the artifact.

Independent commands actually executed:

```text
/usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q
```

Baseline: 254 tests PASS. Final independent run with candidate tests: **282 tests PASS, no skips**. The 28 new tests combine mocks with actual termios, owned-PTY I/O and catchable-signal behavior. The final additions exercise pre/post protection failure, exact clean-environment/foreground metadata, and refusal of the proposed mode before result creation. Stricter result validation rejects numeric zero in place of false, missing/unknown reasons and incomplete category sets. Existing native observer cases remain in the suite. No protected VT trial, real runtime random value, host journal read, deliberate crash, sudo invocation, or host installation was performed by this reviewer.

## Findings and disposition

| Finding | Challenge | Disposition |
| --- | --- | --- |
| IO-01: sequential cleanup could skip restoration | An error flushing input originally prevented restoring termios and file flags; termios failure also skipped flags. | Fixed before handoff. Cleanup attempts each independently and retains terminal_restore failure if any step fails. Two permanent fault-injection regressions passed. |
| IO-02: shared file-description flags | F_SETFL changes flags on the open file description; dup of inherited stdin could affect shell/sudo holders. | Explicit future integration requirement: use an independently opened, verified VT description, not dup/inherited stdin. This candidate neither opens the descriptor nor launches a worker; no present installed-path change. |
| IO-03: privilege-scope change | Existing policy permits exactly diagnostic and crash-test; adding input to crash-test would invalidate its no-input data-flow claims. | Existing wrapper, observer, metadata helper and policy remain byte-for-byte unchanged, enforced by regression against 46ce2ac. No new grant or installer is prepared as executable handoff. A distinct fixed io-test proposal requires explicit owner approval before integration/installation. |
| IO-04: console confidentiality is not established by no echo | Same-user terminal readers, privileged input observers, screen retention and kernel buffers are not excluded by cgroup/termios checks. | Trust assumptions and residual blocker, not a claimed control. Dedicated trusted console session and same-user access expectations need owner review. Do not claim TIOCEXCL or no-echo prevents all existing readers. |
| IO-05: representation and failure-output containment | Entered material could equal a report token; a raw exception or Python traceback could disclose locals. | Fixed enum reports, no print/log sink and exact/raw-hex output comparison. Regression refuses publication on token collision. Future supervisor must handle missing/invalid output with a fixed reason, never exception details. |

## Plaintext-holder and transition review

Candidate exercise generates a disposable SYNTHETIC-prefixed display fixture only after protection checks. It writes that value only to the supplied terminal descriptor and accepts its retyping with echo, canonical processing and terminal-generated signals disabled. The same process holds generated and entered bytes; no exec, fork, subprocess, file writer, shell, logger, network or external output consumer exists in the library.

Python can create multiple in-process copies; this review does not assert secure zeroization. Intentional physical-console display leaves terminal/display/kernel state outside userspace cgroup evidence. Current tests use fixed harmless fixture material and an isolated PTY driver, not the future process graph.

The candidate calls the supplied fixed-control interface before generation/input and rechecks after input. That is useful ordering evidence, not proof of an installed worker, pinned dependency, descriptor closure, verified resource group, foreground VT/session provenance or protection after a new exec. Those are **unimplemented integration gates**. The existing wrapper rejects the candidate report schema and does not import the library. The candidate has no CLI entry point.

## Terminal behavior and bounds

Tests demonstrate no input echo on an owned PTY, pending-input flush on entry/exit, termios/file-flag restoration, EOF/cancellation, timeout and the six handled signals. Both successful and refused paths retain false authorization flags. Generation precedes intentional display, and display precedes direct input. A successful write means queued output, not human custody; a future successful retyping supports the narrower displayed-fixture round trip.

Input is bounded to 48 ASCII alphanumeric/hyphen bytes, the exchange deadline is 90 seconds, and output is bounded. Nonblocking descriptor handling, partial writes, transient unavailable reads, fixed errors and restoration failures are covered. There is no claim that an unwired library deadline replaces a fixed external worker supervisor.

SIGKILL, SIGSTOP, supervisor death, terminal disappearance and uncatchable termination cannot guarantee restoration. Repeated signal storms and kernel failure are not qualified. Future operator recovery must stop typing, recover the trusted console explicitly and avoid assuming buffered input cannot reach a resumed shell. Late input after restoration is outside the completed flush claim.

## Remaining required review before a human runtime checkpoint

1. Explicit approval of the separate fixed command and its exact policy scope; no reuse of crash-test semantics.
2. Reviewed integration with pinned imports, independent VT open/binding, descriptor closure, no material-bearing parent, bounded worker supervision and protected process transitions.
3. Fresh exclusive sanitized result publication, exact candidate/aggregate sudo validation and recovery-preserving installation/rollback.
4. Actual protected-host synthetic success and failure exercises, with restoration and output-containment evidence. Mocked controls or ordinary PTY mechanics cannot substitute.
5. Owner acceptance of trusted console/session, kernel/logging and finite-observation exclusions. No inherited qualification for cryptsetup, OpenBao or any future secret-bearing process.

No real secret bootstrap approval follows from this review. swap_bytes remains NOT_TESTED; effective project no-swap samples are separate evidence. No LUKS/OpenBao initialization, recovery material, brokerage capability, host-policy change or PR merge is authorized or performed.
