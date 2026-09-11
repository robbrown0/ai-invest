# Scoped Prerequisites for Resuming Phase 3

**Historical proposal:** The owner subsequently approved the LUKS2/local-storage, sole-custodian and project-scoped protection direction. See [the resumed assessment](APPROVED_PREREQUISITES.md) for current status. The original proposal below remains as historical evidence; no new storage or secret-bearing runtime is yet qualified.

**Status:** PROPOSED — requires product-owner decision; no host change authorized by this document.
**Purpose:** Resolve the observed prerequisite failure without weakening encryption or touching unrelated workloads.

## Smallest recommended change

Designate and provision a dedicated encrypted local area for ai-invest runtime data and restore exercises, with logically separated PostgreSQL, OpenBao and encrypted backup locations. Keep original recovery/unseal material under separately protected human custody, outside Git, model context and ordinary application configuration. Do not reuse the unrelated encrypted mount.

The owner should confirm the exact target, size/resource ceiling, mount/unlock ownership and recovery-custodian procedure through an appropriate private channel. Never paste encryption keys, passwords, tokens or unseal shares into the assistant or GitHub. Host commands requiring elevation should be performed through an approved operator process; do not grant blanket passwordless sudo or use Docker to circumvent this prerequisite.

A new encrypted loopback volume on local SSD may be a qualification candidate if explicitly approved: it avoids repartitioning but still requires host-level setup, storage/custody review and cold-recovery evidence. Alternatively provide a dedicated isolated encrypted test host/VM with demonstrated protection from host swap. These are alternatives for owner review, not changes already made.

## Memory and container baseline to qualify

Keep global host swap and unrelated services unchanged. Evaluate positive equal container memory/memory-swap limits, actual cgroup v2 memory.swap.max of zero, disabled core dumps and protected bootstrap/helper memory. An untested Compose setting alone does not qualify the control. Tmpfs-only storage is not cold-recovery evidence and may itself swap. [Docker memory controls](https://docs.docker.com/engine/containers/resource_constraints/), [tmpfs limitations](https://docs.docker.com/engine/storage/tmpfs/)

After prerequisite approval, propose a dedicated Compose project with no published ports, internal-only networks, distinct non-root identities, dropped capabilities, no-new-privileges, default seccomp/AppArmor, read-only roots and explicitly bounded writable encrypted mounts. No host networking, Docker socket mounts, privileged containers, other-project networks/volumes or daemon/firewall reconfiguration. Exact images must be verified/pinned and scanned before test service use.

Per-service memory/CPU/PID/storage ceilings and test duration must be selected within owner-approved headroom. No host reboot, global disk exhaustion or stress of existing workloads is implied; simulate process failures inside the disposable project first.

## Secret bootstrap and human recovery

The qualification requires an explicit safe bootstrap plan before generating key-bearing state. Use only synthetic test data. Secret values must stay in protected processes/files and never appear in command output, diagnostics, CI artifacts or LLM context. Replace the legacy blank secret-variable inventory with approved secret references/mounts before any service starts, as required by the Phase 2 design.

An automated disposable fixture may test cryptographic APIs, but cannot demonstrate human custody, operator-absent recovery or independent recovery copies. Those results must remain separate. No fabricated custodian or recovery-time acceptance is implied by Design Gate 1 approval. Establish who performs unseal/recovery and what evidence can be safely published.

## Required regression specifications before dependent work

These are planned tests, not implemented or passed tests.

| Reference | Negative case | Required result |
| --- | --- | --- |
| REG-HOST-01 | Approved mount absent, wrong backing storage, or only unrelated encrypted mount available | Preflight refuses all key-bearing service startup; no plaintext fallback |
| REG-HOST-02 | Swap prevention/core-dump coverage missing for any secret-bearing service or helper | Refuse startup; changing host swap globally is not an automatic repair |
| REG-HOST-03 | Compose requests published ports, privileged/socket/host mounts or lacks required limits | Reject configuration and independently test actual runtime denial |
| REG-RECOVERY-01 | Warm-cache success but wrong/missing keys at cold restart/restore | Mark recovery failed; no inferred pass from prior reads |
| REG-TENANT-01 | Runtime role attempts SET-based tenant forgery, elevated SET ROLE, cross-tenant CRUD/COPY/FK or TRUNCATE | Deny foreign scope and forbidden operations; test every implemented path |
| REG-EXEC-01 | Broker accepts then loses response; original worker pauses and another takes over | UNKNOWN plus held reservation, blocked account, no second outbound attempt |
| REG-STOP-01 | All four scoped stops race admission and process restart | No post-stop admission; already admitted effects remain auditable; restart stopped |

Once storage/bootstrap prerequisites are satisfied, resume the user's work order with exact Percona/pg_tde/OpenBao/backup pins, encrypted recovery/key-loss tests, two-tenant schema, simulator fault corpus, independent implementation review and functioning public-repository CI/security scans. No current backlog issue is claimed completed.

## Approval boundary

Approval to supply these prerequisites would resume synthetic qualification only. It would not pass Gate 2 or grant brokerage connectivity, real credentials, unattended trading, LIVE capability, public application exposure or commercial operation. A later draft PR must carry actual qualification results and residual limitations for human Gate 2 review.
