# Protected Metadata PASS and Bounded Crash Trial

**Status:** Human metadata runtime PASS on the reviewed PATH snapshot; crash/leakage runtime NOT RUN. Gate 2 NOT PASSED.
**Scope:** Synthetic qualification only. Both authorization flags remain false.

## Human evidence and exact meaning

The owner installed the PATH-independence correction at commit f1dfe6cf10f22d0d5da3e39f2b49dc12ee286181 and reported this fresh physical-console result:

~~~json
{"checks_passed":true,"failed_checks":[],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
~~~

This is accepted human-observed real-host evidence for that exact metadata/control path, not a rerun performed by an agent. No timestamps or raw observations beyond the supplied evidence are invented.

| Predicate implemented in that snapshot | What the successful path establishes |
| --- | --- |
| Console | All three descriptors refer to the same real VT character device, major 4/minor 1–63; controlling TTY agrees; retained SSH/GUI/multiplexer markers are rejected |
| Sudo/identity | Exact diagnostic command progressed under the human-installed digest policy; root real/effective UID, expected invoking UID/name, audit loginuid and exact SUDO_COMMAND passed |
| Environment | Existing key allowlist and non-PATH value predicates passed; inherited environment was then replaced with fixed PATH/LANG/LC_ALL |
| Console provenance | loginctl self returned exactly the expected active/unlocked/local tty login session, user and matching VT |
| Code integrity | Canonical root-owned/non-writable/single-link installed wrapper/helper, expected source checkout/branch/remote and helper digest/byte equality passed |
| Host | Enrolled machine identity matched locally, root context and systemd/namespace checks passed; no identifying value is published |
| Plan | Local nonrotational SATA/ext4 backing, capacity reserve, root-owned ancestors and absent storage targets passed at that run; no volume was created |
| Namespace | Scoped mount namespace differs from visible host PID1; PID/user context checks remain host-bound; mountinfo lacks shared/master/propagate-from propagation markers |
| Memory | Finite positive memory.max no greater than 2 GiB |
| Swap | memory.swap.max exactly 0 and memory.swap.current exactly 0 at the checked scope |
| CPU / tasks | Actual predicate accepts positive CPU quota no greater than two periods and positive pids.max no greater than 64; scope configuration requests CPUQuota=100% and TasksMax=32. The JSON does not disclose exact readback values for those two limits |
| Core limits | Both effective soft and hard RLIMIT_CORE equal zero |
| Crash metadata | Exact reviewed core_pattern and SHA-256 of the installed Apport handler matched |
| Output | Exclusive fixed-result creation and allowlisted JSON publication completed |

An all-pass path supports use of the installed exact-command correction; it does not separately prove every sudo-policy negative case, password cache timing, physical-keyboard intent against compromised root, or future reboot behavior. The physical session is a trusted boundary with documented host/account-compromise residuals.

The initial missing encrypted-storage prerequisite, VT/sudo PTY mismatch, tty_identity, operator_environment and environment_path failures remain in [qualification history](README.md), prior checkpoint documents and Git. This success is an additional observation, not a rewrite of those failures. QH-02 remains open; QH-03 now has this narrow metadata sub-result, not complete memory/crash qualification.

## Four distinct crash questions

1. RLIMIT_CORE zero is runtime-qualified for the old diagnostic scope.
2. core_pattern routing and reviewed Apport source are runtime-qualified metadata.
3. Whether a real crash invokes/escapes collector suppression remains separate.
4. Whether any canary is retained anywhere remains a separate leakage question.

Piped core handlers can ignore RLIMIT_CORE. The new trial therefore proposes per-process PR_SET_DUMPABLE=0, checks PR_GET_DUMPABLE, disables Python faulthandler, and avoids exec or credential changes afterward. Fork retains the protected memory/context. This standard Linux mechanism prevents dumpable-state core generation; it is not protection from privileged memory readers or kernel compromise. See [core handling](https://man7.org/linux/man-pages/man5/core.5.html) and [dumpable control](https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html).

## Exact bounded trial design

The new fixed --crash-test argument reuses console, identity, environment, current session, host, plan and installed-code verification. Only after a fresh scoped diagnostic succeeds can the wrapper execute the separately digest-pinned crash_canary.py. It accepts no caller program, path, environment, test payload or project secret.

The scoped supervisor contains no canary. It forks a worker; before generation the worker verifies parent-death protection, disables dumpability/faulthandler, detaches stdin/stdout/stderr to /dev/null, closes other descriptors except a result pipe, and independently checks the effective cgroup/core/mount controls. It generates 32 ephemeral random bytes using os.getrandom inside that protected worker. The value, raw or hashed, is never returned.

Private mount propagation is not a restricted filesystem view: existing host mounts remain visible. Fixed reviewed code and the absence of normal-file writers/external commands bound this trial; it is not a filesystem sandbox or protection from a compromised root interpreter.

The worker examines only its own bounded /proc/self/cmdline and /proc/self/environ for raw/hex containment, then forks one child. That child re-verifies protections and same cgroup and deliberately sends itself SIGABRT with the default disposition. It closes the result pipe before crashing. No subprocess exec, external command, network operation or normal-file creation occurs after generation.

The worker retains the canary strongly while checking SIGABRT termination, WCOREDUMP=false, reaping, no-swap and dumpability afterward. Child dumpable PASS is inferred from the fixed crash branch being reachable only after its checks, not a separately published child value. A hostile kernel/root can falsify that inference. Worker and child may contain interpreter copies; no deterministic zeroization or proof of physical RAM erasure is claimed.

A canary-free supervisor enforces a 20-second collection deadline. Local child wait is bounded to five seconds and cleanup polling to two seconds. pidfd signaling targets only pinned child identities; no PID reuse fallback exists. PDEATHSIG and immediate parent checks provide backup for parent loss. Kernel-uninterruptible tasks remain a host limitation: report cleanup failure rather than claiming guaranteed instantaneous termination.

Only fixed categories with PASS/FAIL/NOT_TESTED/NOT_APPLICABLE may cross the pipe into the root-owned exclusive result file. Publication checks reject true authorization flags and unknown content. All failure/normal worker output uses the same containment-checked encoder. A local trial may pass while overall checks_passed remains false with coverage_incomplete.

## Coverage limits and why this is an interim checkpoint

| Channel | Implemented trial / limitation |
| --- | --- |
| Own argv/environment | Bounded local raw/hex comparison; values never returned |
| Terminal, shell interpolation, child output | No input, no shell/exec after generation; detached stdio, child result FD closed; tested source/control graph |
| Result | Allowlisted schema plus local containment check before publication; no canary/hash persisted |
| Application logs / temporary files | Harness has no normal-file writer/logging API, but external retention is not thereby inspected; NOT_TESTED |
| Shell history / sudo logs / journald | No canary command/input/env is supplied, but no attributable retention search yet; NOT_TESTED |
| Collector artifacts | WCOREDUMP=false is a specific kernel outcome, not exhaustive non-retention proof; NOT_TESTED |
| Swap | Effective cgroup metadata before/after generation is tested; no raw host swap read or pressure test; swap-byte search NOT_TESTED |
| Git working tree/index/history | No Git/file write or network operation is implemented in the fixed harness; ordinary pattern validation is separate and not a canary search; NOT_TESTED |
| CI artifacts | No CI used for runtime trial; no canary artifact search; NOT_TESTED |
| Future secret input | Generated-in-memory canary does not test human typing, terminal buffering, OpenBao initialization output or other programs; NOT_TESTED |

This does NOT complete the requested comprehensive crash/canary layer. It safely narrows the next falsification step. Searching only the crashing PID's journal would miss Apport/kernel-attributed records; broadly scanning personal files, historical crash artifacts or unrelated logs would violate scope. An attributable collector/log observation design remains required after this trial, without inferring non-retention from empty/omitted searches. No actual crash, runtime canary generation or leakage search has been performed by agents. A real protected trial still requires the human checkpoint.

## Equivalent protection for future processes

| Future secret-bearing context | Required design and proof before secrets |
| --- | --- |
| Human bootstrap/key/recovery helper | Dedicated bounded systemd cgroup before input/generation; MemorySwapMax=0, current swap zero, core limits, private mounts and per-process dumpability verified before any plaintext; protected human I/O remains unqualified |
| OpenBao | Initially evaluate 512 MiB ceiling, equal positive container memory+swap limits or equivalent systemd controls; inspect its actual host cgroup and process startup/dumpability, mlock behavior and every unseal/rotation helper; no container started |
| PostgreSQL/pg_tde | Initially evaluate 2 GiB ceiling; actual no-swap and core protection for postmaster, backends, workers and key provider/spill/backup helpers; generic wrapper PR_SET_DUMPABLE before exec is not sufficient |
| Execution credential-handling process | Initially evaluate 512 MiB ceiling; enforce before any credential fetch, verify actual process/cgroup, fail startup or quiesce on lost invariants; no broker/credential code exists |
| Temporary plaintext/backup/rekey helper | Separate identity and bounded cgroup before key retrieval; same no-swap/core/dumpability/input/output requirements, encrypted writable state and short lifetime |

These are qualification requirements, not deployed settings or approved total concurrent reservations. Limits must fit measured shared-host headroom. Do not disable host swap or globally change crash handling. Each executable may reset dumpability on exec/credential changes and needs its own tested process design; the synthetic fork child is not a proxy pass for those services. Compose syntax alone is never evidence.

## Systemd warning: root cause and correction

Installed systemd is 255.4-1ubuntu8.17. Its systemd-run(1) documentation says scope argument expansion currently defaults off for compatibility and will change in a future release. The prior scope argument contained the shell's quoted $1 and $2, intended for Bash positional expansion, not systemd environment expansion. This is brittle even though the metadata run succeeded.

The correction removes Bash and its positional variables completely, uses absolute /usr/bin/python3 -I -B, and passes the fixed scoped mode plus validated numeric result inode directly. It also specifies --expand-environment=no. No argument contains a dollar sign. The root parent already sets both core limits to zero before launch; they survive exec and scoped Python sets them again. A real unprivileged exec-inheritance regression verifies that property. No global systemd configuration changes. Installed manual/help and [versioned source](https://github.com/systemd/systemd/blob/v255/src/run/run.c) support the warning analysis; the corrected root scope itself still needs human runtime evidence.

## Review, checkpoint and gate

See [independent review](CRASH_REVIEW.md) and [guarded human installation/run procedure](CRASH_CHECKPOINT.md). CR-01 PID-reuse cleanup, CR-02 blocking cleanup and CR-03 inconsistent failure containment were found during independent review and corrected with permanent regressions before any privileged test.

No LUKS bootstrap procedure is prepared: actual crash/collector, comprehensive canary and future input-path prerequisites have not passed. No LUKS/OpenBao initialization, real key/recovery material, brokerage connection, live capability, production service or UI is introduced. Public source does not change private/LAN-only application access.

Original Gate 2 blockers remain: encrypted local storage, pinned Percona/TDE/WAL, encrypted restart/restore, OpenBao lifecycle/recovery, tenant/RLS adversarial evidence, financial simulator/reliability, functioning CI/security scans and sustained resource qualification. Both secret_entry_authorized and runtime_crash_suppression_qualified remain false.

## Completion validation for this amendment

Lead and independent reviewer each passed **142 tests**, zero skips, with /usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q. Thirty-three new methods extend the prior 109-test suite; crash branches and failures use inert doubles, never an actual generated runtime canary or deliberate crash. Actual unprivileged exec inheritance of zero soft/hard core limits passed. Tests include nine inert upgrade activation outcomes and unknown-harness rollback refusal.

Installed strict visudo candidate parsing PASS. All **20 Bash instruction blocks** across current/historical checkpoint documents pass bash -n without execution. Markdown validation parsed **60 documents**, checked **241 local links** and nine unchanged Mermaid declarations/fences; no full renderer is available. git diff --check PASS.

Bounded common-secret-pattern checks pass over **83 tracked/non-ignored source files**, index content and **130 pre-commit reachable history blobs**, without printing matching values. Repeat after staging/commit. No real secret or runtime canary was generated by agents. The inert byte fixture is a unit-test double, not captured runtime material. PAPER/false placeholders and .env exclusion remain unchanged; no production application code or brokerage adapter is added.

No gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck or mmdc executable is available on PATH. GitHub Actions queries report zero runs and zero artifacts. No functioning security pipeline or CI-canary search is claimed. These pattern/syntax tests are not actual collector, swap-byte, or comprehensive leakage evidence. No policy was installed, privileged scope launched or host service altered by agents.
