# Approved Synthetic Prerequisites — Resumed Assessment

**Status:** Owner-approved direction; runtime prerequisites NOT QUALIFIED; Gate 2 NOT PASSED.
**Observation date:** 2026-09-09 UTC.
**Purpose:** Record the subsequent human authorization and actual progress without erasing the original prerequisite failure.

## Authorization and implementation boundary

The owner subsequently approved a dedicated local LUKS2 loopback volume, sole-owner recovery custody, project-scoped no-swap/core-dump protection and an isolated Compose baseline. This supersedes the undecided alternatives in the historical [resumption proposal](RESUMPTION_PLAN.md), not the failed observations. Approval remains synthetic only. No Alpaca connectivity, brokerage credentials, unattended trading, LIVE_LIMITED/LIVE, outside users, public application exposure or commercial use is authorized.

Only a read-only metadata preflight and synthetic regression tests have been implemented. No backing file, mapper, filesystem, secret, image download, service, database, schema, simulator or CI workflow has been created. Actual privileged qualification requires the [human operator checkpoint](OPERATOR_CHECKPOINT.md). Do not infer permission to bypass sudo or use Docker as host administration.

## Storage proposal and measured capacity

| Property | Proposed / observed value |
| --- | --- |
| Backing file | `/var/lib/ai-invest/qualification.luks`; new project-owned location only |
| Mapper / mount | `/dev/mapper/ai-invest-qualification` / `/srv/ai-invest-secure` |
| Full allocation | 64 GiB = 68,719,476,736 bytes; not a sparse capacity promise |
| Parent filesystem | Local ext4 on nonrotational SATA disk/partition ancestry; not a NAS mount |
| Filesystem capacity | 1,005,867,986,944 bytes |
| Available at recorded preflight | 464,778,457,088 bytes |
| Expected available after allocation | 396,058,980,352 bytes, approximately 369 GiB |
| Proposed safety floor | At least 200 GiB AND 20% of filesystem capacity free after allocation |
| Target state | Project parent, mount point and mapper absent; existing `/var/lib` and `/srv` ancestors root-owned and not group/world writable |

Repeat capacity, backing ancestry, mount and absence checks immediately before allocation. If any fails, STOP; do not shrink the reserve, substitute another location, overwrite an existing target or use unrelated encrypted storage. Stop if existing workload growth makes the measured headroom unsafe. Metadata relies on the trusted host/kernel/device stack; it is not hardware attestation. The automated locality check is deliberately limited to the observed SATA topology; unknown or network transports fail closed.

Create only new root-owned protected paths after operator qualification. Future provisioning must reject symlinks/existing targets, fully allocate the exact new file, and confirm free-space reserve afterward before formatting. Never run an unattended reformat on retries. LUKS2 creation is destructive to its exact target and therefore needs a separately reviewed, guarded operator procedure. No such operation has run.

Planned encrypted filesystem directories: `postgresql/`, `openbao/`, `runtime/`, `financial-audit/`, `qualification-backups/` and `qualification-restores/`. Assign distinct identities and permissions before services start; keep restore jobs separate from running data. Put PostgreSQL temporary/spill state and any key-bearing writable state on this encrypted path. Bound logs/backups/restore usage and alert before exhaustion. Leave large public model weights and non-sensitive bulk data outside it. NAS may later receive encrypted copies asynchronously; it must not be a runtime dependency.

The loopback volume shares the host disk and failure domain: it is neither independent disaster recovery nor protection from a compromised running host. A mounted LUKS volume does not replace TDE, field encryption, authorization or secret-manager policy.

## Resource and memory proposal

Measured host RAM is approximately 15.5 GiB; the recent snapshot had approximately 10.8 GiB available and active host swap. Do not change global swap, core handling or unrelated workloads. Docker 28.3.3 / Compose 2.39.1 and cgroup v2 are present, but no project container baseline has been exercised.

For the short operator probe propose 2 GiB memory, zero swap, 32 tasks and one CPU, with hard and soft core limits zero. Re-measure before resource-consuming tests. Later initial service ceilings to qualify sequentially: PostgreSQL 2 GiB, OpenBao 512 MiB and a single qualification helper 512 MiB, each with equal positive memory and memory-plus-swap limits. These are ceilings to evaluate, not measured sufficient limits or permission for concurrent stress. Avoid concurrent operator/KDF and service-load tests; select Argon2 memory/parallelism only after measured headroom and security review. Do not silently weaken KDF parameters to get a test to run.

Every secret-bearing process must independently demonstrate effective `memory.swap.max = 0`, no existing swapped pages, bounded memory/CPU/PIDs, core protection and appropriate encrypted writable paths. Include bootstrap/unseal helpers, terminal input path, OpenBao, PostgreSQL, backup/key-rotation tools and future execution-secret helpers. Compose syntax alone is not evidence. Absence of the encrypted mount or any required runtime protection must deny startup with no plaintext fallback. [Docker memory controls](https://docs.docker.com/engine/containers/resource_constraints/)

## New falsified core-dump assumption

The host uses Apport 2.28.1-0ubuntu3.8 through a piped kernel core handler. Inspection of the installed handler demonstrates that a zero `RLIMIT_CORE` alone is insufficient to prevent an Apport report containing a core. The reviewed source skips collection for a different mount namespace sharing the host PID namespace. This branch is a candidate mitigation, not yet a successful kernel crash test. Handler SHA-256 is pinned in the metadata probe; changes require re-review. [Linux core-dump behavior](https://man7.org/linux/man-pages/man5/core.5.html)

Also, an SSH/GUI terminal, multiplexer or PTY relay may buffer secret keystrokes outside a protected child scope. The next probe therefore requires a direct physical host virtual console, no relay/recording, and no secrets. Matching namespace inodes against visible PID 1 does not independently prove execution on the host; human verification of direct host context is required. Distinct mount namespace does not itself prove private propagation. Actual suppression, propagation and the complete input path remain unqualified.

## Recovery custody and future interactive sequence

The product owner is the sole V0 custodian. Multiple recovery copies are redundancy, NOT multi-person separation of duties. True independent custody remains a future real-money/commercial gate.

After the protected operator path passes runtime qualification, the human alone must perform interactive LUKS passphrase entry and OpenBao initialization/unseal/recovery in that verified environment. The assistant must not run or observe secret-bearing commands. Never send values through command arguments, environment files, shell history, terminal recording, assistant prompts, GitHub, ordinary Compose configuration or diagnostic output. Disable history/recording and avoid clipboard/password relay software for this procedure. Service key references are not permission to expose their contents.

1. Human verifies the reviewed command/source snapshot, safe capacity, protected direct-console scope and exact new storage targets. No automated unlock or secret generation by the assistant.
2. Human creates/formats/unlocks the new LUKS2 target using interactive input only. Mounting in a private namespace does not publish a host mount: a separate non-secret host-side mount action must be reviewed and verified before service use. Never pass a passphrase as a command argument. [LUKS formatting](https://man7.org/linux/man-pages/man8/cryptsetup-luksFormat.8.html)
3. Human establishes at least two separately stored offline protected recovery copies. LUKS header backups contain sensitive key-slot material and must also stay offline/protected, outside Git and ordinary backups; retained old headers can preserve old-passphrase access. Document copy identifiers and custody dates only, not content or storage addresses.
4. Before OpenBao initialization, qualify its encrypted persistence, TLS, no-swap/core controls and helper path. Then human handles initialization output/root token/unseal shares directly and places necessary narrowly scoped service credentials through a reviewed protected channel. No assistant-connected terminal and no initialization output capture. Revoke bootstrap root authority after policy/service setup is verified; do not claim this has occurred.
5. Cold recovery: stop only project services, obtain an encrypted backup and separately held recovery material, unlock the dedicated restore area, restore OpenBao/key availability before database recovery, verify synthetic data/TDE/WAL/audit state, and remove temporary recovery authority. Record redacted outcomes and exact versions. NAS outage must not stop normal operation.
6. Exercise wrong/unavailable/lost-key behavior using isolated disposable fixtures and copies, never by destroying the only usable recovery material. Genuine loss of all usable LUKS or OpenBao recovery/key material can make encrypted state permanently unrecoverable. A warm-cache read is not recovery proof.

## Executed evidence and remaining work

Relevant observed operator tooling: Ubuntu 24.04.3, kernel 6.11.0-26-generic, systemd 255 (255.4-1ubuntu8.17), cryptsetup 2.7.0 and Apport 2.28.1-0ubuntu3.8. None of these version observations constitutes qualification of a cryptographic operation or the proposed scope.

Python 3.12.3 executes the read-only [preflight](../../scripts/qualification/operator_preflight.py) and [tests](../../tests/qualification/test_operator_preflight.py). `plan` returned `checks_passed: true`; in the assistant session `operator` returned exit 1 with `metadata_unavailable`. Both always returned `secret_entry_authorized: false` and `runtime_crash_suppression_qualified: false`. No raw exception/environment/secret output is included.

The regression suite covers capacity floors, required predicates, local-versus-unknown/remote transport, invalid memory/swap/PID settings, unsafe terminal/core metadata, fail-closed sanitized output, and the pinned Apport source branch. These are predicate/source tests, not runtime proof. See the [checkpoint validation and independent review](OPERATOR_REVIEW.md) for actual counts and limitations.

QH-02/QH-03 remain NOT QUALIFIED. All original TDE/WAL/recovery/key lifecycle, RLS, simulator/fault, CI/scanning and sustained host-resource gates remain unexecuted. The authorization resumes work toward those gates; it does not pass them.

## Checkpoint repository validation

The lead and independent reviewer each ran all 17 regression tests successfully. Local validation parsed 49 Markdown files, checked 191 local links and checked declarations/fences for 9 unchanged Mermaid blocks. No full Mermaid renderer is installed. Common-secret-pattern checks passed over 63 tracked/non-ignored working-tree files, the index and 83 pre-amendment reachable history blobs; matching values are never printed. Ignored interpreter bytecode is not a source artifact. No secret-bearing runtime files were created; unrelated host logs/configuration are intentionally outside the inspection scope.

No dedicated gitleaks, trufflehog, bandit, semgrep, trivy or Mermaid executable was available on PATH. This checkpoint does not claim SAST, dependency/container scanning or a functioning CI/security pipeline. GitHub reported zero Actions runs and zero Actions artifacts at inspection. Local metadata/test output contains no keys/credentials; no initialization output or crash dump was captured. Pattern checks cannot prove absence of every possible secret in all host state.

The amendment changes only qualification documentation, a read-only preflight, its tests and ignore rules for LUKS images/header backups. Bootstrap environment placeholders remain unchanged and LIVE flags remain false. No production application/trading code, brokerage adapter, secret material, service deployment or software license was added. Public source visibility does not change the private/LAN-only application boundary. PR #14 remains a draft checkpoint, not a completed Gate 2 submission.
