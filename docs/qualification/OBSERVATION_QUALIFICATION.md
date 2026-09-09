# Bounded Crash Observation — Qualification Amendment

**Subsequent human evidence:** At commit 531671a5e6e3bf8c7efc3bddb899c53d53cd1c27, local crash checks passed but all five observer categories remained NOT_TESTED. Supplied /var/log metadata proves a policy mismatch, without proving first-failure order or journal access. See [the focused read-only correction and setup gate](LOG_SOURCE_QUALIFICATION.md) and [current checkpoint](LOG_SOURCE_CHECKPOINT.md). The NOT-run/prepared wording and results below record the original handoff; they are preserved as history.

**Status:** NON-SECRET checkpoint prepared; new observer has NOT run on the host. Gate 2 NOT PASSED. Both authorization flags remain false.

## Historical human evidence (one trial)

The owner reports installing source commit **5975603575b6761fb44932b84dc1519676639584**, running the exact --crash-test command at the physical console, and retrieving the result after non-symlink/root-owner/mode/link-count checks. This is **one human-observed trial**. Retrieval or re-reading is not another trial. Its random comparison material is gone; no retrospective canary search is possible.

Exact reported artifact (unaltered):

```json
{
  "checks_passed": false,
  "failed_checks": ["coverage_incomplete"],
  "mode": "crash-test",
  "results": {
    "application_logs": "NOT_TESTED",
    "bounded_result": "PASS",
    "child_reaped": "PASS",
    "ci_artifacts": "NOT_TESTED",
    "cleanup": "PASS",
    "collector_retention": "NOT_TESTED",
    "crash_signal": "PASS",
    "dumpable_child": "PASS",
    "dumpable_parent": "PASS",
    "git_history": "NOT_TESTED",
    "git_index": "NOT_TESTED",
    "git_worktree": "NOT_TESTED",
    "human_input_path": "NOT_TESTED",
    "journal": "NOT_TESTED",
    "kernel_core_flag": "PASS",
    "own_argv": "PASS",
    "own_environment": "PASS",
    "runtime_limits": "PASS",
    "shell_history": "NOT_TESTED",
    "stdio_detached": "PASS",
    "sudo_logs": "NOT_TESTED",
    "swap_bytes": "NOT_TESTED",
    "temporary_files": "NOT_TESTED"
  },
  "runtime_crash_suppression_qualified": false,
  "secret_entry_authorized": false
}
```

**11 implemented checks PASS; zero FAIL; 12 NOT_TESTED.** Expected and actual narrow success agree. Overall incomplete is correct.

| PASS | Precise meaning in tested source |
| --- | --- |
| runtime_limits | At implemented parent/child checkpoints: one thread; same expected non-root cgroup; memory.max positive and at most 2 GiB; memory.swap.max/current both zero; pids.max positive and at most 32; positive CPU quota at most one period; zero soft/hard RLIMIT_CORE; private mount namespace versus PID1; same PID namespace. Not continuous measurement or future-service evidence. |
| dumpable_parent | PR_SET_DUMPABLE(0), PR_GET_DUMPABLE==0, faulthandler disabled, core limits zero, parent-death binding checked before generation; non-dumpable rechecked later. PASS means **non-dumpable**, not permission to dump. |
| dumpable_child | Fixed child branch checks non-dumpable/core/cgroup protection before its only SIGABRT call. PASS inferred from reaching expected termination through that graph, not an external memory inspection. |
| crash_signal | wait status reports child terminated by SIGABRT. |
| kernel_core_flag | WCOREDUMP bit was not set on that wait status. This does **not** show what a collector retained. |
| own_argv / own_environment | Worker read its own proc metadata and found neither exact canary bytes nor lowercase hex encoding at that time. No general encoding or other-process search. |
| stdio_detached | Worker closed inherited descriptors except fixed result pipe and verified descriptors 0/1/2 identify /dev/null before generation. |
| child_reaped | Owned child was observed/reaped through bounded wait. |
| cleanup | Cleanup returned success for the owned child/pidfd; no broad process cleanup. |
| bounded_result | Fixed-enum JSON was bounded and locally compared against raw/hex canary before its sole write; validated artifact was published by the wrapper. |

Previous storage prerequisite stop, VT-to-sudo-PTY mismatch, tty_identity, operator_environment and environment_path failures and reviewed corrections remain in [the historical index](README.md), [console design](CONSOLE_TRUST_BOUNDARY.md), [PATH correction](PATH_INDEPENDENCE.md), [original crash plan](CRASH_QUALIFICATION.md) and [original checkpoint](CRASH_CHECKPOINT.md). None are rewritten as first-attempt successes.

## Threat model and finite completion

Trusted: current kernel, root administrator, installed/pinned Apport route, systemd/libsystemd and standard Python runtime. This is not a defense against a malicious kernel/root, debugger with administrative authority, arbitrary modified collector, forensic physical RAM capture, or unlimited future logging delay.

New observation runs inside the protected worker. No raw records leave it. No agent reads host logs, crash artifacts or runtime canary material. Human installation/run authorizes ONLY the fixed read-only observation described here; no global configuration change.

Evidence labels: **A** directly tested PASS; **B** directly tested FAIL; **C** not applicable to this exact harness, supported by source/data-flow analysis (not a runtime search); **D** untested/unresolved. Prior trial has eleven A and no B. Current observer runtime categories remain D until the next human trial.

| Prior NOT_TESTED category | Plausible path and evidence method | Completion criterion / bootstrap relevance | Current disposition and outside claim |
| --- | --- | --- | --- |
| collector_retention | Kernel crash routing may invoke Apport before/as a child dies; collector PID differs. Source + new journal, Apport interval and crash-store observation. | No observed invocation/retention indicator in reviewed sinks during bounded window, with complete subobservations; any activity/unknown route needs review. Required finite collector assurance before bootstrap, not WCOREDUMP alone. | D. New PASS, if obtained, means ONLY finite no-indicator observation. Delayed collection, unstructured kernel records and volatile collector memory remain outside that result. Human must review adequacy; no authorization flag change. |
| journal | Kernel/collector/scope may log independently of child PID. Runtime fixed-field search of attributable stored records. | Complete boot/time-bounded enumeration of reviewed fields, no raw/hex match, no read error/threshold/rotation/timeout. Logging-path evidence required. | D. Excludes dropped/unflushed/delayed entries, duplicate field instances, arbitrary custom fields and unstructured MESSAGE-only kernel records without supported identity. Not all-log-byte assurance. |
| sudo_logs | Sudo starts before canary exists; neither wrapper/supervisor nor sudo receives it. No echo/stdout/input exists; I/O logging already disabled only for exact commands. Source data-flow plus prior protected path/stdio evidence. | Review fixed no-input/no-export graph and unchanged exact sudo policy. No runtime canary search of unrelated sudo logs is justified for this graph. | C for this internally generated trial after its local checks pass. Future typed input/recovery output and changed sudo handling must be qualified separately. |
| shell_history | No shell after generation, no typed canary/argv/env assignment. Source data-flow. | Confirm no shell invocation or input/export. | C, scoped only to this graph; future human input remains D. |
| application_logs | No application service/logger is running in this test path; only fixed JSON output pipe. Source + bounded-result/stdio checks. | No logging sink/import/callback accepting canary. | C, does not waive future application logging tests. Collector logging is covered separately. |
| temporary_files | Harness never creates a ordinary file, tempfile or plaintext payload; result pipe carries enum JSON. Reader may map existing system journal pages but never writes canary. Source/descriptor flow. | No writer/memfd/temp path; fixed result publisher validates enums. | C for harness-created plaintext files. Crash files belong collector_retention, not this exclusion. Memory/swap are separate. |
| git_worktree | No Git command or file writer after generation, no canary export to operator/model. Source flow. | No edge from canary to checkout; repository scans check submitted source, not unknowable vanished canary. | C for runtime canary path; ordinary repository secret scanning still required. |
| git_index | Same graph: no index access/writer/subprocess. | No edge to index. | C; not a retrospective canary search. |
| git_history | Same graph: no commit/Git/network operation receiving canary. | No edge to Git objects. | C; does not assert all prior repository history is secret-free. |
| ci_artifacts | No CI involved in human root trial; inert test fixtures are different non-secret inputs. | No runtime canary export/network/upload. | C; future CI/application changes require new review. |
| swap_bytes | Physical host swap is outside allowed inspection. Effective cgroup no-swap controls are the relevant prevention mechanism. Runtime controls + fixed process graph. | memory.swap.max=0/current=0 before material, child inheritance and sampled verification after; no raw swap-device read. Byte-search requirement is NOT claimed complete. | D for byte search; A for previous process/control samples. Raw byte search is not required by this scoped plan, subject to owner approval; kernel/root trusted, prior resident pages/future processes excluded. |
| human_input_path | No typed input or recovery output exists in this harness; generated bytes do not exercise terminal/input handling. | Separate minimal synthetic-only typed input and synthetic recovery-output exercise after collector evidence review. This remains a bootstrap blocker. | D, not relabeled C. No real secret input requested. |

New JSON adds only **observation_window**, **apport_log**, **crash_store** to the fixed category allowlist. Source-backed C rows become NOT_APPLICABLE only after local trial controls complete without FAIL. Historical JSON remains unchanged. No NOT_TESTED row is relabeled PASS solely from source configuration.

## New observation design and scope

1. Existing wrapper/identity/console/host/integrity prechecks and exact systemd scope remain. Both parent and child require protections before canary generation/inheritance; runtime limits are rechecked after observer library loading.
2. Protected worker loads installed python3-systemd before generation, opens read-only observation handles, then obtains 32 random bytes internally. Child inherits non-dumpable/no-swap/core-zero state, closes observation/result handles, rechecks protection, and SIGABRTs.
3. Parent uses waitid(WNOWAIT) to observe termination **without reaping**, retaining the child PID and pidfd during a ten-second post-exit observation. Comparison bytes remain only in worker/child memory. Child is then reaped; handles closed. Parent result encoding scans its sole output. No subprocess, shell, file writer, network or new canary receiver exists.
4. Supervisor deadline 35 seconds plus existing bounded cleanup; child-exit deadline five seconds; observation ten seconds; journal query budget two seconds/256 records/1 MiB reviewed values, fields strictly below 64 KiB including field-name separator. Scheduling delay over two seconds or wall/monotonic disagreement over 250 ms fails the trial rather than claiming a valid interval. A wedged kernel cannot be guaranteed killable; no global kill/reboot fallback.
5. Fixed journal matches: current boot AND worker PID, child PID, COREDUMP_PID, OBJECT_PID, or fixed scope in _SYSTEMD_UNIT / OBJECT_SYSTEMD_UNIT / UNIT. Explicit disjunctions prevent accidental AND across different attribution selectors. Start/end monotonic bounds reject earlier/reused identity records. A current-boot tail cursor is read as metadata only, verified still retained; invalidation/rotation/missing anchor is incomplete.
6. Reviewed journal fields are exactly JOURNAL_FIELDS in crash_canary.py: boot/PID/scope attribution, MESSAGE, COREDUMP, COREDUMP_FILENAME, COREDUMP_CMDLINE, COREDUMP_ENVIRON, COREDUMP_PROC_STATUS/MAPS/LIMITS and _CMDLINE. Individual _get reads distinguish absence from errors. Fixed fields avoid v235 _get_all enumeration-error suppression. The raw or lowercase-hex detector is local; no claim covers arbitrary encoding or every duplicate/custom field. Trusted installed collector and no-output data flow bound those residuals. Any core-dump field indicator leaves collector coverage incomplete; no referenced arbitrary artifact path is opened.
7. Apport: root-owned fixed /var/log/apport.log is anchored before generation. Only newly appended bytes (maximum 1 MiB) may be read; no historical body is read. These interval bytes can transiently include contemporaneous unrelated records: header/target attribution is parsed locally, **only exact child-target marker lines are searched**, and nothing raw is returned. Collector PID alone never attributes other payload lines. Any append, unsupported/partial record, creation, replacement, truncation or rewrite prevents a collector absence PASS. A known targeted positive is retained even with a later partial/malformed record.
8. Crash stores: read-only inotify metadata subscriptions on /var/crash and /var/lib/systemd/coredump (existing immediate parent if absent). No historical names/contents are enumerated. Root-owned sticky /var/crash may be writable as Ubuntu normally requires; only that fixed directory receives the exception. Any mutation/move/deletion/overflow/identity change is incomplete, including unrelated current activity. No arbitrary reported path is followed. Queue silence is only no observed mutation, not inspection of files or all collector storage.
9. Collector PASS requires a complete interval, journal PASS with no core indicator, unchanged/absent-baseline Apport log, and no reviewed store event. This is an **explicit proposed finite qualification semantic**, not the old/global proposition “collectors cannot retain memory.” Owner review is required before using it in a bootstrap decision. Overall checks_passed=false and both flags=false remain unconditional.

Journal change-watch initialization explicitly calls fileno() before the anchor and generation: on installed v255, process() alone can return without establishing watches. Missing watch initialization was found in independent source review and corrected before this checkpoint. In the child, detach(-1) closes inherited raw descriptors instead of calling the process-origin-bound journal library cleanup. The v255 library refuses post-fork cleanup; no claim is made that it destroyed the parent's watches. Parent retains and closes its own observer normally.

The journal claim is limited to the API-visible local system journal view. Libsystemd can internally skip directory-discovery/watch errors; fileno success is not proof every journal store is accessible. Surface read errors, missing anchor and invalidation are incomplete. Undiscovered/corrupt/unreadable stores and dropped/delayed transport remain residual exclusions requiring owner review, not an exhaustive absence claim. No privileged host observation has run in this amendment. Unit fixtures prove detector positive/negative behavior, caps, attribution, error handling and cleanup; they do not prove the real journal/Apport transport functions. A future runtime PASS must be interpreted with these documented exclusions.

## Installed interface versions and references

Read-only API/source inspection: python3-systemd **235-1build4**, libsystemd0/systemd **255.4-1ubuntu8.17**, sudo **1.9.15p5**. Existing operator preflight pins Apport helper SHA-256 and exact kernel core_pattern, rejecting drift before trial. No package installation occurred.

The [v235 binding source](https://github.com/systemd/python-systemd/blob/v235/systemd/_reader.c) documents individual reads and its all-fields iteration behavior; the [v255 match API](https://github.com/systemd/systemd/blob/v255/man/sd_journal_add_match.xml) and [data API](https://github.com/systemd/systemd/blob/v255/man/sd_journal_get_data.xml) inform match grouping and truncation bounds. Runtime calls must succeed; package presence is not control qualification.

## Smallest separate future input/output test — NOT implemented/authorized here

After finite collector/log evidence is reviewed, propose one fixed synthetic-only VT helper, not a general secret service: enter a clearly synthetic value through a non-echoing controlling-terminal read directly into the protected helper; exercise a separate synthetic recovery-output display/custody path if future bootstrap requires it. No argv/env/shell-history transport or general command execution. Identify every plaintext holder before implementation: terminal/kernel buffers, protected helper, and any specific protected output consumer. Sudo/wrapper/supervisor must never receive plaintext. A protected comparison process and bounded test-local sink observation must qualify that exact path, including terminal restoration on failure/interruption. Generated internal random bytes do not substitute for this test.

Future bootstrap helper, OpenBao, PostgreSQL/pg_tde, execution credential helpers and transient key helpers each require their own demonstrated pre-material memory.max/memory.swap.max=0/current=0, core-zero/non-dumpable where supported, crash/log behavior, and restart evidence. The current scope does not confer those properties on containers or services that do not exist yet. Host-wide swap and crash handling stay unchanged.

## Validation actually performed

| Procedure | Actual result | Limit |
| --- | --- | --- |
| Full qualification unittest discovery | 177 tests PASS, independently repeated | Inert observer/crash fixtures; existing unprivileged core-limit exec test; no runtime RNG, crash or host-log read by agents |
| Strict installed visudo candidate parser | PASS | Candidate only; installed aggregate/effective policy belongs to human checkpoint |
| All documented qualification Bash blocks | 24 syntax checks PASS | None executed; current upgrade also has inert success/eight activation-failure/rollback-failure simulations |
| Markdown, local links, Mermaid declarations | 63 documents, 261 local links, 9 structural Mermaid checks PASS | No full Mermaid renderer available |
| Common-secret-pattern validator | 87 nonignored source files, index and 145 pre-amendment reachable history blobs PASS; no matching values printed | Pattern scan, not universal secret detection or runtime-canary search; staged/final history rechecked at commit |
| Dedicated tooling availability | gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck, mmdc unavailable | No installation or claimed dedicated scanner result |
| GitHub Actions metadata | Zero runs and zero artifacts | No CI participated in this trial; not a functioning CI qualification |
| Diff/scope checks | Qualification code/tests/docs and digest-only policy change | No application code, service deployment, credential generation or broker adapter |

Both the author and independent reviewer used harmless deterministic fixtures for positive/negative detector tests. These are not the owner's vanished runtime canary and do not qualify the live collection transport.

## Remaining gates

See [current checkpoint](OBSERVATION_CHECKPOINT.md) and [independent review](OBSERVATION_REVIEW.md). Preserve original result files. One new consolidated run is required, not another standalone metadata repetition.

Even all new finite subchecks PASS leaves overall **coverage_incomplete** expected. Remaining real-secret blockers: actual new observer runtime evidence and review of its finite exclusions; separate human-input/recovery-output assurance; explicit later owner secret-bootstrap authorization; demonstrated protection for every additional plaintext-handling process. No LUKS bootstrap is prepared/executed on this incomplete evidence.

Gate 2 additionally lacks encrypted volume/storage, exact Percona/pg_tde/WAL/backup/restore/key tests, OpenBao lifecycle/recovery, service resource/crash controls, RLS attacks, simulator/financial fault tests, functioning complete CI/security scans and host-load evidence. No application or brokerage capability was introduced.
