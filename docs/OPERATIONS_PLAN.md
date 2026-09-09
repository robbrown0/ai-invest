# Operations, Recovery and Host Plan

**Status:** DRAFT — no services installed or host changes authorized by this document.
**Purpose:** Define an affordable operational envelope and evidence required before PAPER operation.

## Host and deployment qualification

The local Ubuntu development host is shared with existing workloads, not a dedicated financial appliance. An NVIDIA GPU with 8 GB VRAM and CPU/RAM availability are owner assumptions, not measured capacity. Inventory listening ports, existing workloads, storage health/capacity, encryption, patches, driver versions, private network access and backup routes after Design Gate 1 approval. Agree maintenance windows with the host owner.

Single-host Compose is a deliberate V0 availability limitation. Separate containers reduce privileges but cannot protect secrets from host root/kernel compromise. No claim of SaaS availability or production-grade physical separation. Before outside-customer/live use, revisit dedicated host, stronger isolation, independent key hosting, availability and operator duties.

Proposed service rollout: encrypted local storage and OpenBao recovery first, qualified Percona TDE database next, local identity/edge, control/risk/execution in simulator mode, then research/model worker. Stop is engaged at boot and at every deployment. Database migrations run with short-lived elevated identity while dispatch is paused. Model jobs have lower resource priority and bounded disk/VRAM allocation.

## Operational controls

| Area | Proposed control | Release evidence |
| --- | --- | --- |
| Host | Supported Ubuntu security updates; SSH keys/passkeys via private admin path; no password/root network login; local firewall; time sync; encrypted swap or disabled swap/core dumps for secret processes | Owner-approved host checklist and exposure scan |
| Containers | Pinned verified image digests, non-root processes, minimal images, read-only root filesystems, dropped capabilities, no Docker socket; scoped writable volumes | Container scan and negative capability/network tests |
| Segmentation | Dedicated financial/management networks and enforced egress; no broker route from research; identity on private TLS edge | Reachability tests from each actual runtime identity |
| Resources | CPU/RAM/IO limits protect DB/identity/reconciliation; single GPU task initially; queue quotas per tenant; disk watermark stops new ingestion before financial audit starvation | Load/soak test with simulated shared-host pressure |
| Patching | Weekly review; urgent exploitable Critical/High findings trigger containment and expedited patch; stop dispatch before financial component changes | Vulnerability register, change record and rollback drill |
| Monitoring | Local health metrics/log rotation, no hosted telemetry required; low-cardinality tenant-safe labels | Alerts for stop, reconciliation lag, stale quotes, errors, key leases, clock drift, DB/WAL disk, archive lag |
| Deployment | Reproducible signed/reviewed release manifest; schema compatibility; rollback tested; no automatic dependency/model deployment | Test report, independent security review, owner approval |
| Runtime outage | Fail closed for new financial actions, preserve read-only stale labels and unresolved orders | Fault-injection and UAT evidence |

Health checks expose status categories, never config dumps, request headers or key values. Logs separate authentication/security, financial audit and operational telemetry; confidentiality controls apply even in a private LAN.

## Backup and restore contract

TDE does not by itself encrypt logical exports, every metadata file, or external research archives. Select a tested, pinned Percona/pg_tde/backup combination; encrypted WAL compatibility is a release gate. Do not treat a successful copy or a tool checksum as a successful recovery. See [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md) for key separation.

Proposed initial recovery objectives, requiring human acceptance: local financial-state RPO at most 15 minutes from verified recoverable backup/WAL; RTO at most 4 hours when an operator and all recovery material are available. These are targets, not measured guarantees. NAS outage extends off-host RPO; operator absence can exceed RTO with manual unseal. Display actual last-restorable time and oldest unarchived event, not a false green SLA.

Maintain an encrypted local backup spool and asynchronous copies to each NAS on separate failure/credential paths. Neither primary PostgreSQL files nor order-path data live on NAS. NAS shares have quotas/timeouts and cannot block primary DB writes. Do not store sole decrypt/unseal material beside backup ciphertext or grant NAS credentials access to OpenBao. Offline human-protected recovery material and restore instructions are necessary; two NAS devices in one building are not off-site disaster recovery.

Restore rehearsal sequence:

1. Isolate an empty recovery environment from all broker routes, keep execution disabled and restore secrets-manager state plus separately held recovery material.
2. Validate encryption key versions and least-privilege access, restore qualified database/base backup and WAL, then verify schemas, FORCE RLS, constraints and audit chain anchors.
3. Restore required evidence/manifests and identity configuration; inspect principal key/ciphertext compatibility across rotation.
4. Compare restored internal intents and last snapshot with broker open orders/fills through a paper-only reconciliation channel. A restored outbox must never replay orders automatically.
5. Mark missing time intervals explicitly; unresolved financial state blocks dispatch. Rebuild derived positions/performance from preserved events and verify totals.
6. Human reviews evidence and explicitly re-arms PAPER after fresh authentication.

Test successful restore, missing/latest/old key versions, corrupted archives, missing WAL, expired credentials, NAS disconnect, full local disk and host reboot. Loss of the only principal/envelope/backup key can make data irrecoverable; no password reset is a cryptographic recovery mechanism.

## Incident and break-glass plan

Declare severity based on suspected financial authority, tenant confidentiality, integrity and availability. Operator first engages the durable stop; if core services are unavailable, stops execution or denies its broker egress through the independent host admin path. This cannot reverse already accepted orders. Reconcile residual exposure and use the broker's own paper console where needed.

Contain affected process/network identities; preserve minimally scoped encrypted evidence; revoke sessions and rotate only affected credentials with a documented dependency order; assess tenant and source impact; recover from known-good artifacts. Record timeline, authorization, actions, uncertainty, preserved hashes, recovery checks and postmortem regression tests. External notification timing is for qualified privacy/legal review.

Break-glass grants are time-limited, reason/ticket-bound, separately authenticated and audited; they cannot disable audit, mint model privileges or enable live mode. A lone V0 operator is a separation-of-duties limitation. Independent human security review is required before security-sensitive implementation releases; subagent review is design evidence, not a substitute.

## Open decisions

Agree recovery custodians, encrypted disk feasibility without disturbing existing services on the development host, backup size/retention budget, resource reservations, private access method and a separate disaster-recovery location. No paid infrastructure dependency is introduced by this plan.
