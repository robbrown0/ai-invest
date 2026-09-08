# Architecture, Operations and QA Challenge Passes

**Status:** DRAFT — specialist design objections, not approvals.
**Purpose:** Record distinct Principal Architect, SRE and QA/SDET perspectives for lead integration.

## Principal Application Architect

### Top five concerns

1. Excess service boundaries could consume V0 effort before the first scientifically useful paper experiment.
2. A shared control application that can set arbitrary tenant context can still leak data despite RLS.
3. A risk approval based on a stale portfolio snapshot can become unsafe before dispatch.
4. An outbox replay after crash can be mistaken for permission to resend a broker order.
5. Shared conceptual vocabulary may hide inconsistent lifecycle or approval semantics across docs.

### Assumptions that may be wrong

The operator can maintain isolated identities/networks on the local Ubuntu development host; one database handles both research and financial IO comfortably; paper brokerage supports the chosen safe fractional order form; local IdP persistence works with qualified encrypted tables.

### Failure modes

Research saturates DB resources; a forged tenant job crosses scope; valid approval replay doubles exposure; UI labels acceptance as fill; backtest mode inherits an execution route.

### Missing requirements raised

Explicit tenant/actor-bound contracts; atomic account reservations and stop epoch; priority queue/resource isolation; no live adapter/config switch; UNKNOWN state across DB/network boundary.

### Simplifications worth considering

One modular product app, one durable database queue and one bounded local inference worker; no Redis/NATS/Kubernetes until measured need. Keep synchronous interactive API plus durable long jobs, not events everywhere.

### Disagreement

SRE preferred fewer processes including in-process risk. Security requires a separate risk issuer and isolated broker holder. Resolution proposed: combine ordinary product modules but preserve risk/execution/ingestion identities as distinct runtime boundaries; pure libraries may be shared. Human review still required.

## SRE / Infrastructure Architect

### Top five concerns

1. Single shared host and root/GPU-driver compromise defeat colocated isolation.
2. Manual OpenBao unseal conflicts with unattended recovery after power loss.
3. TDE/WAL backup tool incompatibilities can make a seemingly healthy backup unrecoverable.
4. NAS reliability can accidentally enter the order path through blocking mounted paths.
5. Local models can exhaust memory/disk/IO and starve audit or reconciliation.

### Assumptions that may be wrong

CPU/RAM availability under normal development-host load; free local disk can support encrypted backups; owner has separately protected recovery material; operator can meet proposed four-hour restore target.

### Failure modes

Reboot leaves OpenBao sealed and DB unable to recover; retained keys missing after rotation; WAL fills disk; research OOM kills critical services; NAS outage stalls a synchronous archive write.

### Missing requirements raised

Measured resource reservation, independent local spool, cold-start recovery drill, disk watermark policy, explicit operator-availability caveat and no automatic re-arm.

### Simplifications worth considering

Single local OpenBao instance rather than colocated pseudo-HA cluster; local status/metrics before hosted dashboards; schedule deep reasoning overnight; encrypted asynchronous NAS transfer only.

### Disagreement

Product wants continuous monitoring, security wants manual unseal and fail-closed operation. Resolution proposed: accept visible downtime and missed opportunities in V0, stop at reboot, require operator recovery; do not buy KMS or hide raw unseal keys in configuration. Human must accept recovery targets and custody.

## QA / SDET Lead

### Top five concerns

1. Passing isolated happy-path tests says little about ambiguous orders and stop races.
2. RLS tests with superuser mocks can falsely certify tenant isolation.
3. AI confidence and a short favorable market window can be misreported as predictive skill.
4. Provider documentation has inconsistent fractional/paper behavior; mocks may reproduce the wrong contract.
5. A single owner cannot supply independent review by self-approving a checklist.

### Assumptions that may be wrong

Meaningful point-in-time historical evidence is freely available; synthetic broker fault behavior covers real responses; intended coverage gates will actually be configured and enforced on the public source repository. Branch/push protections now exist, but CI status checks and independent-review approval counts are not yet enforced.

### Failure modes

Repeated accepted-but-timeout submissions; test-only tenant context differs from production; future data contaminates recommendations; zero variance/fee double counting corrupts metrics; restored outbox dispatches old trades.

### Missing requirements raised

Actual database-role and runtime network tests, model/financial regression rule, independent arithmetic oracles, property/state-machine fault schedules, explicit tool/version evidence and owner-readable UAT.

### Simplifications worth considering

Test two synthetic tenants comprehensively before many personas; simulator-first contracts before credentials; one matched experimental ledger instead of comparing incompatible dashboards.

### Disagreement

Product favors rapid scheduled paper autonomy; financial systems and QA require initial human-triggered dispatch, then a separately scoped/expiring mandate after recovery and stop evidence. Resolution: P0 manual, P1 supervised bounded PAPER automation. Human approval required for the P1 mandate.

## Lead integration notes

These are role-based challenge passes by the lead agent, supplemented by separate-agent security/data, product/UX/privacy and research/quant/execution reviews. They do not imply twelve independent human reviewers. The final cross-agent review and unresolved decisions are recorded in [PHASE2_REVIEW.md](../PHASE2_REVIEW.md).
