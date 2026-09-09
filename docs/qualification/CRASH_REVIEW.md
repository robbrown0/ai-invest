# Independent Review — Bounded Synthetic Crash Checkpoint

**Disposition:** No blocking finding remains for the reviewed **partial non-secret human checkpoint only**. This is not approval of secret entry, comprehensive leakage suppression, LUKS bootstrap or Gate 2.

## Independence and scope

The reviewer did not author the harness, wrapper, policy or installation instructions. The reviewer read `AGENTS.md`, the prior operator/console qualification evidence, the current wrapper and metadata helper, the new [crash harness](../../scripts/qualification/crash_canary.py), [qualification design](CRASH_QUALIFICATION.md), [human checkpoint](CRASH_CHECKPOINT.md) and regression tests. This review document is the reviewer's only repository edit.

The human's successful metadata result is accepted for the earlier reviewed snapshot. It is not a crash result and does not qualify the newly changed scope command. Earlier failed prerequisites and console/environment checks remain valid historical evidence. The reviewer performed no sudo installation, protected runtime launch, runtime canary generation, deliberate crash, secret operation, service deployment or unrelated host inspection.

## Findings, disagreements and corrections

| ID | Independent challenge | Resolution / remaining limitation |
| --- | --- | --- |
| CR-01 | Numeric cleanup could signal an unrelated reused PID if interrupted after `waitpid` reaped a child but before the caller cleared its variable | Corrected to pidfd signaling, never a numeric cleanup fallback. Regression simulates already-reaped identity, ESRCH/ECHILD and absent-handle refusal. An unreaped child pins its PID while the handle is opened. |
| CR-02 | Blocking cleanup `waitpid(..., 0)` escaped the advertised deadline | Corrected to bounded nonblocking polling; failed cleanup is explicit FAIL. Kernel-uninterruptible tasks cannot be promised immediately killable. Missing pidfd is not permission to target a numeric PID; parent-death controls are backup, not a successful reap assertion. |
| CR-03 | Failure publication lacked the same canary-containment check as normal publication | Both paths now use the common bounded encoder. Regression forces containment rejection for success and failure metadata. Raw exception text is never formatted. |
| CR-04 | Own-PID journal searches would miss kernel/Apport-attributed messages and create false-negative assurance | Such searches were not presented as comprehensive coverage. Collector retention, journal, sudo logs, history, files, swap bytes, Git/CI and future human input remain NOT_TESTED. Overall checks remain false even when local trial predicates pass. |
| CR-05 | Shell positional variables caused version-sensitive systemd argument expansion warnings | Bash and `$1`/`$2` removed; explicit `--expand-environment=no`, absolute isolated Python and validated numeric inode arguments remain. Core limits are established before launch and re-established in the scoped process. A real unprivileged exec-inheritance regression passes; corrected privileged launch remains unrun. |
| CR-06 | Child-branch protection failures initially had mostly source-level coverage | Added inert child-branch tests for successful signal reachability and failed protection preventing SIGABRT, alongside protection/cgroup tests. These are not actual kernel crash evidence. |
| CR-07 | Private mount propagation could be mistaken for filesystem/network containment | Design explicitly states the host filesystem remains visible. Fixed reviewed code contains no network or normal-file writing operation; ambient root authority is not a restricted filesystem/network sandbox. |

The principal design disagreement was whether a narrow fork/crash outcome could be labeled complete collector/leakage qualification. It cannot. This interim test is useful to falsify the selected process mechanism, but the still-missing attributable observation and human-input designs block secret bootstrap. No LUKS procedure is prepared.

## Adversarial assessment

- **Canary lifetime:** cryptographic generation occurs only in the worker after no-swap, zero-core, non-dumpable, single-thread and namespace checks. The supervisor never receives the value or a hash. A strong reference survives fork so the crashing child actually contains the synthetic bytes. Interpreter copies may exist; no deterministic zeroization or physical RAM-erasure claim is supported.
- **Output and execution:** worker stdio is detached, inherited descriptors are closed except the fixed enum-result pipe, and the crashing child closes that pipe. Python faulthandler is disabled. No shell, exec, external command or normal-file writer follows generation. Only fixed result categories cross into the existing protected publication path. Tests use inert doubles rather than a generated runtime canary.
- **Crash inference:** the child's intended SIGABRT branch follows protection checks without exec or credential transitions. `WCOREDUMP=false` is a bounded kernel status observation, not exhaustive proof that no privileged collector or other process retained memory. Host root, kernel and interpreter integrity remain trusted assumptions.
- **Swap:** the new harness checks the same effective cgroup before and after the trial, exact zero swap limit/current usage, memory at most 2 GiB, task limit at most 32 and CPU quota at most one period. This strengthens CPU/task thresholds relative to the earlier metadata predicate. It does not inspect raw swap, prove continuing invariants against root migration, or qualify OpenBao/PostgreSQL/other future executables.
- **Privilege scope:** exactly two digest-pinned arguments are proposed for one fixed installed wrapper. No arbitrary argument, executable, payload, environment, internal scoped command or standalone crash-helper sudo grant is added. All command-scoped authentication/environment/PTY defaults remain unchanged; unrelated sudo behavior is not widened. Effective merged policy and runtime behavior require human verification.
- **Publication and cleanup:** the new fixed result must be absent, uses the existing exclusive/root-owned/inode-checked publication design, and cannot convert incomplete coverage into a success or true authorization flag. Reused or unknown result targets must not be deleted to force a rerun. pidfds, deadlines and parent-death controls bound cleanup without broad process-group targeting.

## Installation and rollback review

The guarded human block verifies reviewed old/new hashes, expected checkout, root-owned non-writable ancestry, single-link installed artifacts, absent staging/new targets, existing metadata helper and enrolled-host marker permissions. It parses candidate and aggregate sudo configuration. Recovery restores policy first, independently restores the old wrapper, and restores the new harness's prior absence only for its exact recognized contents. Unknown/symlink harness targets are not unlinked.

All three recovery legs must succeed before complete recovery is reported. This is not an atomic multi-file installation: power loss, uncatchable termination, storage failure or concurrent root modification can require manual recovery. Root-only snapshots/staging remain available; prior qualification snapshots and result files are not erased. A restored wrapper may refuse a newer checkout, correctly. The deliberate rollback removes only the verified project policy exception, not ordinary sudo access or global PTY protection. The installation block uses the human's pre-existing administrator authority, not a new general root-runner grant.

## Independently executed validation

| Procedure | Actual result | Boundaries |
| --- | --- | --- |
| `python3 -I -B -m unittest discover -s tests/qualification -q` | **142 tests PASS**, zero skips | Inert crash/control and activation fault tests; no actual crash or canary generation |
| `/usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers` | `parsed OK` | Installed parser only; no policy installed |
| `bash -n` for all four Bash blocks in the new checkpoint | **4 PASS** | Syntax only; none executed |
| SHA-256 comparison with reviewed checkpoint table | PASS for wrapper, harness and policy | Does not attest future installed bytes or concurrent root activity |

Reviewed wrapper SHA-256: `c95e4d462070e6577ceeba77051be504e67fe5d3f4cb62dc9125654e1b03e461`.

Reviewed harness SHA-256: `781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415`.

Reviewed policy SHA-256: `034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae`.

## Stop boundary

No blocking implementation issue remains for this narrowly described synthetic checkpoint. Actual corrected-scope/crash execution, comprehensive collector and leakage coverage, future secret I/O and service-specific protection remain unqualified. This review is not a release or Gate 2 approval. Both `secret_entry_authorized` and `runtime_crash_suppression_qualified` remain false. No real secret, encrypted-volume/OpenBao initialization, brokerage connectivity or LIVE capability was introduced. PR #14 must remain DRAFT and unmerged.
