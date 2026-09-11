# Finite Observer Milestone and Synthetic Terminal Candidate

**Status:** Narrow observer milestone CLOSED for further synthetic work. Input/output milestone NOT QUALIFIED. Unwired candidate only; host integration/installation STOPPED at the explicit policy-scope approval boundary. Gate 2 NOT PASSED. Both authorization flags remain false.

## One successful human trial — not an agent run

The owner reports installing **46ce2ac030b69c70cfbbf01c7b238289f205a134**, running the protected physical-console crash test, and safely retrieving /var/tmp/ai-invest-crash-traversal.json. The complete artifact remains untouched; agents neither read nor overwrite it. No timestamp is inferred and retrieval is not another trial.

| Reported category | Human-observed result |
| --- | --- |
| Four observer setup stages | PASS |
| Existing local protection/crash/publication/cleanup checks | PASS |
| observation_window, apport_log, crash_store | PASS |
| journal / journal_stage / journal_reason | PASS / complete / complete |
| collector_retention | PASS |
| Category totals | 20 PASS, 8 NOT_APPLICABLE, 2 NOT_TESTED |
| Remaining NOT_TESTED | human_input_path, swap_bytes |
| Overall | checks_passed=false; failed_checks=[coverage_incomplete] |
| Authorization | secret_entry_authorized=false; runtime_crash_suppression_qualified=false |

This table records the supplied summary, not a reconstruction of the complete JSON. [The tested traversal design](TRAVERSAL_QUALIFICATION.md), [review](TRAVERSAL_REVIEW.md) and [original finite observation criteria](OBSERVATION_QUALIFICATION.md) define the claim. Journal PASS means completed bounded API-visible fixed-field observation; collector_retention PASS means no reviewed indicator in the finite attributable journal/Apport/store observations. It does not mean universal memory non-retention.

The owner explicitly permits using this evidence for further SYNTHETIC work under those trust assumptions/exclusions. No new defect or change requires reopening journal traversal, console/sudo/PATH, or log-source validation. Their code and policy remain byte-for-byte unchanged and their regressions remain.

The eight source-backed NOT_APPLICABLE categories remain limited to the old internally generated, detached-stdio harness: sudo_logs, shell_history, application_logs, temporary_files, git_worktree, git_index, git_history and ci_artifacts. They are not copied into a new interactive report. Compromised root/kernel/trusted logging, unavailable or library-skipped storage, duplicate-field limitations, delayed records and future processes remain outside the closed milestone.

**swap_bytes stays NOT_TESTED.** The effective memory.swap.max=0 and memory.swap.current=0 samples, together with the fixed process design, are separate prevention evidence. No raw swap device or unrelated memory was read; no swap-byte search is required or claimed for this step. Kernel buffers and future services are not qualified by process cgroup samples.

All earlier failed storage, TTY, environment, PATH, log-source and journal attempts and artifacts remain historical evidence. The new success does not rewrite their outcomes.

## Necessary approval boundary, not another diagnostic run

The existing exact sudo grant permits only --diagnostic and --crash-test. Its source and reviewed data flow explicitly accept no human input. Silently replacing --crash-test with an interactive command would change that contract and the basis for its scoped exclusions.

The smallest honest next entry is **one additional fixed --io-test argument** to the same digest-pinned executable, with the same human authentication, command-specific PTY exception, NOSETENV, environment/identity/session/host/integrity checks and fixed bounded scope. This is a privilege-policy scope addition, **not a digest-only update**. The user requires stopping and explaining such a change before installation. Accordingly this amendment prepares only an unwired candidate/test library. It does not alter the wrapper, policy, installed files, log observation or result publication.

See [the single approval checkpoint](INPUT_OUTPUT_CHECKPOINT.md). There is no authorized current --io-test invocation or installation block. Do not invoke the candidate via sudo Python or an arbitrary shell as a workaround. Candidate code is not an independently authorized root entry point.

## Finite acceptance criteria for the subsequent integrated checkpoint

These criteria distinguish mechanism tests from the still-required protected human trial. No report must be made green by expanding forensic access.

| Requirement | Evidence needed / completion | Current evidence / exclusion |
| --- | --- | --- |
| Authorized fixed entry | Explicit approval of exactly --io-test; reviewed pinned integration and exact-argument policy; human candidate/aggregate validation and rollback | STOPPED before integration/install. Current wrapper rejects proposed mode without creating a result. |
| Plaintext-holder protection | Actual worker after final exec/fork has private mount, bounded memory/CPU/tasks, no-swap max/current zero, zero core limits, non-dumpable state, faulthandler disabled, parent-death binding and only reviewed descriptors before generation/read | Candidate calls existing controls before material and after exchange; tests mock these controls. Existing crash trial qualifies its old graph only. |
| Synthetic recovery display | Fresh disposable SYNTHETIC-prefixed fixture displayed only to verified direct VT; bounded write completes; human retypes it exactly | Local PTY roundtrip PASS with fixed inert fixture. Actual human display/custody not tested. No claim of offline recovery-copy custody. |
| No-echo input | Effective termios flags sampled with ECHO family, canonical handling, signal characters and extensions disabled; bounded byte reader receives only displayed disposable value | Actual owned-PTY mechanics tested. Privileged VT origin/protection mocked in candidate exchange tests, not qualified. |
| Cancellation/EOF/timeout/interruption | Fixed bounded refusal, pending input flushed, original terminal settings/status flags restored and verified, owned worker cleaned up | Local PTY controls and catchable signal tests; supervisor/worker interruption and actual protected console still unimplemented. |
| Output containment | Only direct labeled display may contain fixture; own argv/env and serialized-result checks; fixed enum schema with false flags; no log/file/network/exec path after material | Source/data-flow plus positive/negative fixture tests. No new host-log search, collector run or universal encoding/erasure assertion. |
| Result publication | Future supervisor validates fixed IO schema and exclusively publishes fresh root-owned non-symlink single-link sanitized result; interrupted/invalid output never PASS | Existing crash publisher remains unchanged and rejects candidate mode. New IO publication/integration is NOT implemented. |
| Milestone closure | Reviewed fixed integration, actual successful human roundtrip and required refused/cleanup paths, finite scope accepted by owner | NOT QUALIFIED. All-pass candidate test values still produce checks_passed=false. Neither global authorization flag changes. |

The integrated checkpoint should consolidate normal roundtrip and planned cancellation/EOF/short-timeout exercises where safe, without repeating old observer investigations. A single success cannot stand in for unperformed failure-path tests. Any new actual exec/credential transition or extra plaintext recipient changes this acceptance scope and requires its own pre-material controls; no inheritance assumption is sufficient.

## Candidate implementation and intended process boundary

[terminal_exchange.py](../../scripts/qualification/terminal_exchange.py) has no CLI, launcher, subprocess, fork, file opener/writer, network client or logger. It is not imported by the existing wrapper. It returns only bounded fixed-schema bytes to a future reviewed worker, not the typed/displayed values. The candidate's controls parameter is an internal seam intended for the already-pinned crash helper, not runtime caller configuration or a generic command API. Tests use doubles at that seam. There is deliberately no selectable executable/path/command argument.

Proposed integration, not implemented here:

1. Existing physical-console authorization and clean-environment scope finish all exec transitions before any synthetic material exists.
2. A fixed supervisor opens a **new independent file description** for the already verified VT using no-follow/CLOEXEC handling and verifies its identity/foreground binding. It must not merely duplicate inherited stdin: file status flags are shared by dup/fork descriptions. No new terminal or arbitrary device path is allowed.
3. A worker is forked before material, closes unrelated descriptors, detaches standard streams to /dev/null, and retains only its dedicated direct VT and sanitized-result pipe. Supervisor and wrappers never read or receive input bytes. The supervisor enforces a fixed deadline and bounded owned-child cleanup; it may retain metadata needed for terminal restoration, not plaintext.
4. The worker reapplies/verifies existing controls after this transition. The candidate validates root/VT foreground and exact already-clean environment, verifies protections, disables/readbacks terminal echo, then creates a random **disposable test fixture**, not an encryption key or recovery share.
5. It displays the clearly labeled fixture locally and requires exact no-echo retyping. Wrong input is never echoed. A 48-byte reader cap and 90-second absolute exchange budget apply. Partial nonblocking I/O remains within the same deadline. The eventual supervisor deadline must bound the entire worker; this library alone is not such a supervisor.
6. Local raw/hex own-argv/environment and encoded-result comparisons run inside that same worker. The direct display is intentional, not a leak-free terminal claim. No exec, fork, credential change or external consumer occurs after material in this proposed path.
7. Terminal input is flushed and original termios/file flags restored and checked before a bounded result is handed to the supervisor. Missing/invalid result or restoration failure must remain failure/incomplete. The worker exits; Python allocator copies are not claimed securely erased.

The candidate uses standard termios/select/fcntl/signals, not custom authentication cryptography or a secret service. [Python's termios API](https://docs.python.org/3.12/library/termios.html) documents attributes and restoration interfaces. The [Linux file-status interface](https://man7.org/linux/man-pages/man2/F_GETFL.2const.html) explains shared open-file-description flags. Per-process [dumpability](https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html) must be verified after transitions; a prior fork-only result cannot qualify a future real executable.

## Plaintext holders and terminal trust

| Holder | Scope / required protection |
| --- | --- |
| Human | Sees intentionally labeled disposable recovery fixture and retypes only it; no actual password/token/key/share. Never paste it into chat, issue, log or command. |
| Kernel input/TTY/console/video buffers | Intentional input/output route; trusted kernel, console drivers and physical display. Not userspace cgroup memory, not proven erased by tcflush, and no claim excludes screen/scrollback retention. |
| Proposed worker / Python runtime | Random bytes, ASCII display, input buffer, comparison and transient string/bytes copies. Must be protected before material and stay protected until exit. Candidate local test does not prove real process integration. |
| Supervisor, sudo, systemd, unshare, env, shell | Intended to receive no plaintext; hold only metadata or enum result. Descriptor/data-flow and actual I/O-logging policy must be reviewed in integration. Historical NOT_APPLICABLE status does not automatically transfer. |
| Other services / consumers | None in the candidate. No clipboard, pager, tee, logger, application, Git, network or CI recipient. Future OpenBao/cryptsetup input/output introduces new processes and is unqualified. |

Physical origin is not exclusive input confidentiality. The console login/user, administrator, kernel and display path must be trusted; another process with terminal access might read/write or record it. Root ownership of the installed helper and no-echo do not prove absence of another reader. No new tty permissions, group changes, exclusive-access ioctl or session service is introduced. Before real secrets, the owner must review this dedicated-console-session assumption or authorize a separately designed stronger boundary. Do not claim resistance to a compromised same-user session.

No-echo protects ordinary line echo only. Human typing before the prompt or after cancellation/return may reach other terminal consumers; instructions must prohibit it. In the candidate, Ctrl-C/Ctrl-Z bytes cancel and Ctrl-D/zero read means EOF. External catchable signals invoke restoration; their handlers and masks are restored. Pending input flush is best effort, not atomic against later typing.

SIGKILL, uncatchable parent death, hardware loss, kernel hang or terminal disconnect cannot promise cleanup. Stop typing immediately. Before any future recovery command, confirm through a reviewed bounded supervisor result that the test worker is gone; if that cannot be established, stop for human recovery review. Only then may the human restore their console with the standard stty sane procedure, accepting that it is not exact restoration or memory erasure. No automatic global terminal fix, broad kill, reboot or unrelated-service action is supplied here.

## Validation and independent review

Interpreter: /usr/bin/python3 **3.12.3**, read-only version query. Inherited observer's version pins and regressions unchanged; no package installation. [Focused tests](../../tests/qualification/test_terminal_exchange.py) use harmless fixed fixtures; no runtime random value was generated or exposed to agents.

Actual local tests exercise owned PTY termios, no echo, display/retype, byte limits, Ctrl-C/Ctrl-D/Ctrl-Z, timeout, six catchable signals, pending-input flush, and restoration. Candidate root/VT/no-swap/non-dumpable gates are mocked for roundtrip tests; the real candidate VT gate separately rejects the PTY. Mocked faults cover pre/post protection failures, partial/EAGAIN writes/reads, metadata contamination, malformed schema, fixed-token containment collisions and cleanup errors. No host logs, physical VT, unrelated memory, raw swap, or privileged runtime were inspected. This is not a physical-console trial.

Independent review identified IO-01: one restoration error could prevent later restoration attempts. Cleanup now independently attempts flush, terminal settings and status flags; any failure remains terminal_restore. Permanent regressions cover flush and termios failure. Another initial test fixture contained an underscore outside the accepted input alphabet and therefore reached input_invalid before cancellation; changing only that inert fixture corrected the test. Neither finding is rewritten as a host trial.

[Independent review](INPUT_OUTPUT_REVIEW.md) records its disposition and executed checks. Author and reviewer each ran **282 tests PASS, no skips**, including 28 new terminal candidate tests and the preserved 72 native-journal cases. Existing observer/policy hashes are regression-checked against 46ce2ac; no working mechanism has been reopened.

Final local checks: candidate-only unchanged visudo syntax PASS; 78 Markdown documents/339 local links PASS; nine Mermaid blocks receive structural declaration/fence checks only. Common secret-pattern checks cover 107 nonignored working files, staged changes and reachable history without printing matching values; these are not exhaustive secret detection or a runtime-fixture search. Dedicated gitleaks, trufflehog, bandit, semgrep, trivy and full Mermaid renderer executables were unavailable; no new tooling was installed for this task. No CI was used for the candidate trial.

## Concrete remaining prerequisites

Before a synthetic protected IO run: explicit exact-mode policy approval; reviewed fixed supervisor/descriptor/terminal-restoration/result integration with pins; guarded human installation/aggregate validation/rollback; then actual human qualification. These remain necessary work, not completed implementation.

Before real-secret bootstrap: successful integrated input/output evidence and refusal-path recovery; review of terminal/session/custody assumptions; protection and execution-boundary qualification for every real tool or additional plaintext holder; current capacity/local encrypted-storage plan revalidation; practical offline custody/restore plan; and **fresh explicit authorization for real secret-bearing bootstrap**. A synthetic displayed fixture does not test OpenBao output, cryptsetup passphrase handling or offline recovery-copy durability.

Original Gate 2 still additionally requires LUKS-encrypted storage, exact Percona/pg_tde/WAL/restart/backup/restore/key qualification, OpenBao lifecycle/recovery, service controls, tenant/RLS attacks, broker simulator/reliability, CI/security scanning and host-load evidence. None is passed here. No production service, brokerage, global host policy, live mode or real secret was introduced. Public repository visibility does not authorize public application exposure.
