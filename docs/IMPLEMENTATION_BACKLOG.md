# Proposed V0 Implementation Backlog

**Status:** DRAFT — Design Gate 1 proposal, not work authorization.
**Purpose:** Define a manageable set of implementation epics with acceptance, security and testing included.

All issues are initially P0 and grouped into conceptual milestones. P1/P2/Future requirements remain a roadmap, not hundreds of speculative tickets. Dependencies refer to stable V0 IDs; [GITHUB_BACKLOG.md](GITHUB_BACKLOG.md) will map them to created GitHub issues after documentation stabilizes. Nothing in this backlog authorizes live trading.

## V0-01: Qualify PodFlix storage, Percona TDE and OpenBao recovery

**Milestone:** M1 Foundations
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-18, REQ-P0-20; NFR-06

### Problem

Sensitive paper-account and tenant data must not enter a deployment whose encryption, key boot sequence and restore path are unproven.

### Scope

Inventory the approved host without altering unrelated workloads; select/pin supported Percona/pg_tde and OpenBao builds; prototype encrypted tables/WAL, encrypted residual storage, independent key storage, rotation and isolated restore. Record exact compatibility and resource measurements.

### Acceptance Criteria

- Owner approves host capacity, disk-encryption approach, private access and recovery custodians; replace legacy blank secret variable inventory with approved secret references/restricted mounts before provisioning any service.
- All tenant/identity tables, indexes, TOAST and WAL coverage verified; residual plaintext catalog/spill exposure mitigated and documented.
- Cold start, sealed OpenBao, old/new key rotation, full and point-in-time restore evidence meets owner-approved RPO/RTO or blocks deployment.
- NAS disconnect leaves critical-path operation independent; missing key restoration fails explicitly.

### Security Considerations

No sensitive real data in qualification; secrets via human-provisioned restricted mounts only. No DB-root keys in config/Git; no paid services.

### Testing Requirements

Integration qualification on exact builds; missing/corrupt backup/key/WAL, disk-full, identity migrations, network isolation and restore-outbox replay denial. Run dependency/container/secrets scans. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

Explicit Design Gate 1 approval; unresolved qualification decisions in PHASE2_REVIEW.md.

### Out of Scope

Application features, brokerage credentials, live access, HA cluster, other PodFlix service changes.

## V0-02: Build identity, membership and tenant isolation foundation

**Milestone:** M1 Foundations
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-01, REQ-P0-02; NFR-01, NFR-07

### Problem

A single-user prototype can accidentally bake global mutable identity into every financial operation.

### Scope

Qualify local OIDC provider/passkey recovery, server sessions, explicit memberships/roles, tenant-keyed conceptual entities and FORCE RLS/composite constraints. Supply scoped background-worker context and denied support defaults.

### Acceptance Criteria

- Two synthetic tenants with multiple memberships/accounts remain isolated through APIs, DB queries, jobs, exports and pool reuse.
- Expired/revoked sessions, forged issuer/audience/tenant and unauthorized fresh-auth actions fail with auditable denial.
- Runtime identities are not owner/superuser/BYPASSRLS; migration identity is separated. Qualify independently verified expiring capability context at the database boundary or tenant-scoped role pools; arbitrary SET under a shared runtime login cannot select tenant authority.
- Recovery flow and privileged changes use owner-approved fresh authentication and cannot enable live modes.

### Security Considerations

Independent security review mandatory. Identity is not execution authority; no generic broker OAuth in V0.

### Testing Requirements

Unit authorization, actual RLS integration, cross-tenant read/write/IDOR, migration/pool-reuse, session/CSRF/XSS and recovery tests; ADV-01/02/09/12/13/23. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-01, plus explicit Design Gate 1 approval.

### Out of Scope

Public registration, enterprise federation, support impersonation, paid identity or production user migration.

## V0-03: Build licensed market-data ingestion and point-in-time evidence

**Milestone:** M2 Data and ledger
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-05, REQ-P0-06; NFR-07

### Problem

Untrusted, stale or retrospectively revised data can create unsafe trades and false performance claims.

### Scope

Provider/capability abstractions, security master/calendar, free-source license register, coverage labels, quarantine/fetch parsing, immutable source availability timestamps, corporate actions and deterministic candidate scan.

### Acceptance Criteria

- Every used observation has event/publication/ingestion/available-at timestamps and immutable provenance/version.
- Free-feed limits and IEX versus consolidated coverage visible; unmet freshness/liquidity evidence yields HOLD/reject.
- Fetchers cannot reach private/internal metadata/broker/key networks through redirects or DNS changes.
- Historical revisions and universe membership preserve the as-of view; missing/delisted evidence is explicit.

### Security Considerations

Treat SEC/news/PDF imports as adversarial; MIME/size/decompression quotas, bounded SSRF-safe fetch; no secret-bearing source URLs.

### Testing Requirements

Parser/schema/fuzz/data-quality tests; stale/feed-outage/split/dividend fixtures; point-in-time cutoff and injection tests; ADV-04/11/21. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-01, V0-02, plus explicit Design Gate 1 approval.

### Out of Scope

Paid market data, broad redistribution, LLM inference, unsupported historical completeness claims.

## V0-04: Build portfolio ledger and deterministic broker simulator

**Milestone:** M2 Data and ledger
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-03, REQ-P0-11, REQ-P0-13; NFR-03

### Problem

Broker requests and fill events must resolve to a reproducible economic ledger even under retries, partial fills or tiny fractional capital.

### Scope

Tenant/account/portfolio ownership, decimal arithmetic, virtual $100–$300 capital caps, order/fill/position/cash snapshots, corporate-action adjustments and a programmable broker simulator.

### Acceptance Criteria

- Balances/positions rebuild from immutable economic events using independently reviewed fixtures.
- Broker buying power never overrides virtual capital; reservations and partial fills cannot overspend or oversell.
- Simulator injects duplicate/reordered events, accepted-but-timeout responses, cancellations, outages and reboot schedules.
- No provider/live endpoint or credential is needed for default tests.

### Security Considerations

Separate ledger write ownership from advisory research; append-only corrections and tenant-aware unique event identities.

### Testing Requirements

Property/state-machine concurrency tests and hand-calculated cash/equity/dividend/split/fee fixtures; ADV-07/08/17/21. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-01, V0-02, plus explicit Design Gate 1 approval.

### Out of Scope

Real broker connectivity, tax accounting, margin/options/shorts, real capital.

## V0-05: Implement deterministic proposal risk and reservation controls

**Milestone:** M3 Controlled PAPER slice
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-08, REQ-P0-09; NFR-03

### Problem

Advisory output and human clicks must not bypass objective capital, instrument, freshness and authorization limits.

### Scope

Strict proposal intake, versioned long-only risk policies, explanation codes, atomic reservations, one-use approvals and state/policy/stop-epoch validation.

### Acceptance Criteria

- All proposed buys/sells pass hard asset/capital/position/sector/liquidity/loss/turnover/time/freshness rules, independent of AI confidence.
- Immutable approval binds proposal digest, tenant/account/portfolio, current mandate/state/policy, quote, expiry and stop epoch.
- Concurrent proposals cannot overspend reserved cash or oversell; policy/state changes invalidate stale approvals.
- HOLD and every rejection are auditable and retained for outcome tracking.

### Security Considerations

Only risk identity mints approvals; denied-by-default rules and no caller-controlled account/secret resolution. Numeric limits require owner approval.

### Testing Requirements

Every risk branch plus decimals/nonfinite/extremes, concurrency, stale-state TOCTOU, oversized/prohibited AI input, replay; ADV-05/07/20/23. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-02, V0-03, V0-04, V0-07, plus explicit Design Gate 1 approval.

### Out of Scope

AI-selected limits, risk override, live modes, derivatives/leverage, automatic liquidation.

## V0-06: Implement PAPER execution, reconciliation and emergency stop

**Milestone:** M3 Controlled PAPER slice
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-04, REQ-P0-10, REQ-P0-11, REQ-P0-14

### Problem

A lost broker response or racing worker must not cause duplicated trades or an unexplained residual order.

### Scope

Execution-only paper credential retrieval, allowlisted Alpaca adapter/capability qualification, durable intent/dispatch fencing, order query/cancel/fill reconciliation, stop epochs and stopped-at-boot behavior.

### Acceptance Criteria

- P0 dispatch requires human trigger and current risk approval; only paper-specific credentials and endpoints are accepted.
- Fractional DAY limit behavior qualifies through simulator and bounded paper contracts; unsupported behavior blocks, never silently relaxes safety.
- Timeout UNKNOWN preserves stable client ID/reservation; a paused original worker plus lease-expiry takeover never causes a second submission attempt; partial/canceled/rejected outcomes reconcile. Broker not-found alone never clears an admitted unknown intent.
- Stop blocks later dispatch, reports in-flight residuals and best-effort cancel; restart requires fresh human re-arm after reconciliation.

### Security Considerations

No live provider/config/OAuth grants; only execution service has order authority. Independent financial/security review before any paper credential provisioning.

### Testing Requirements

Fault injection at every send/commit/accept/fill boundary, broker outage, replay/fencing, stop races, host reboot; ADV-06/07/08/10/17/19/23. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-04, V0-05, V0-07, plus explicit Design Gate 1 approval.

### Out of Scope

Scheduled/unattended automation, broker OAuth, live accounts, cancel-and-replace strategy, new broker adapters.

## V0-07: Build audit, safe job delivery and release/recovery evidence

**Milestone:** M1 Foundations
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-12, REQ-P0-18, REQ-P0-20

### Problem

Consequential actions need durable correlated evidence, and financial jobs cannot rely on transient delivery or unreviewed releases.

### Scope

Transactional audit/outbox, scoped jobs with leases, append-only financial/security history, tamper evidence/checkpoints, encrypted local spool/NAS archiving, local health, supply-chain checks and incident runbooks.

### Acceptance Criteria

- A failed durable audit append blocks new financial actions; every intent has causation/correlation and versioned input references.
- At-least-once jobs are deduplicated; expired financial leases enter reconciliation rather than blind submit.
- Secret/header/prompt-context canaries never appear in logs/metrics/archives; cross-tenant audit access denied.
- Restore verifies chain/checkpoints and never auto-replays broker dispatch; independent review and Critical/High gate documented in release evidence.

### Security Considerations

Hash chains are tamper evidence, not host-root immutability; anchors/recovery custody separated. No hosted paid monitoring required.

### Testing Requirements

Audit alteration/truncation, disk-full, retry/dead letter, key/NAS outage, restore/replay, secret-canary and tenant tests; ADV-14/15/16/24. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-01, V0-02, plus explicit Design Gate 1 approval.

### Out of Scope

Live incident operations, paid immutable storage, HA/event streaming, implementation during Phase 2.

## V0-08: Build local research memory and governed inference funnel

**Milestone:** M4 Research and experiments
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-06, REQ-P0-07, REQ-P0-19

### Problem

Repeated research loses value without versioned memory, and unbounded agents waste resources or turn untrusted content into authority.

### Scope

Deterministic scan, scoped sanitized gateway, bounded local inference/runtime qualification, logical specialist roles, versioned theses/catalysts/bull-bear cases, recommendation registry and model approval/rollback.

### Acceptance Criteria

- Serious unpurchased/rejected/HOLD ideas persist with sources/cutoffs/invalidation and later outcomes.
- Model inputs contain no credentials/raw broker IDs; model cannot access DB/broker/OpenBao or arbitrary internal URLs.
- Record model weights/digest/quantization/prompt/agent/schema/source provenance; unapproved changes cannot alter active behavior.
- Benchmarked local queue fits host budget with degraded HOLD behavior; no billed frontier API required.

### Security Considerations

Architectural injection containment, tenant-isolated caches/retrieval, approved artifact provenance/licenses and bounded context.

### Testing Requirements

Frozen grounded/adversarial evals, hallucination/abstention/calibration, schema regression, source injection, memory revision, model rollback and resource contention; ADV-04/06/11/22 as applicable. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-02, V0-03, V0-07, plus explicit Design Gate 1 approval.

### Out of Scope

One deployed service per specialist, autonomous execution, premium API calls, automatic model upgrades.

## V0-09: Build accessible portfolio and safety UX

**Milestone:** M3 Controlled PAPER slice
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-03, REQ-P0-08, REQ-P0-13, REQ-P0-14, REQ-P0-20; NFR-02

### Problem

Users must distinguish evidence, advice, permission, submission and actual fills, especially during degraded operation.

### Scope

Login/onboarding, tenant switch, paper portfolio, balances/positions/performance, proposal/risk/order/audit drilldown, stop/re-arm, health/admin/security views and responsive accessibility.

### Acceptance Criteria

- Every financial screen and confirmation displays PAPER or non-submitting context plus tenant/portfolio and freshness.
- Proposal/approval/submitted/UNKNOWN/filled/cancel states visibly differ; HOLD is a complete outcome.
- Global/account stop remains easy to reach; re-arm needs fresh auth and health checks; residual fills explained.
- Keyboard/screen-reader/narrow-mobile tasks and number/currency/time-zone labels pass UAT.

### Security Considerations

Server enforcement for all actions, secure sessions/CSP/CSRF, no unsafe render of research, deny support by default.

### Testing Requirements

Component/contract/accessibility plus full user journeys and authorization tampering; UAT-01…11/16…24 relevant cases. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-02, V0-04, V0-05, V0-06, V0-07, plus explicit Design Gate 1 approval.

### Out of Scope

Marketing/return claims, public SaaS onboarding, billing UI, live controls.

## V0-10: Build manual frontier review packet and safe import

**Milestone:** M4 Research and experiments
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-15, REQ-P0-16

### Problem

Optional human-run expert research must be reproducible, private and incapable of granting financial authority.

### Scope

Two-stage blind export packet, minimization/consent preview, content hash/version/expiry, self-contained instructions/sources, closed-schema import quarantine/provenance and ordinary proposal generation.

### Acceptance Criteria

- Stage-one expert conclusions lock before local conclusions are revealed; deviations labeled.
- Export omits secrets/raw broker IDs/PII and unconsented sensitive data; manual subscription attribution recorded.
- Import rejects unknown/executable/endpoint/auto-fetch/private or credential-bearing URL/tenant fields, expired/replayed packet and invalid recommendations; bounded public HTTPS citations remain inert unverified evidence.
- Accepted expert ideas remain advisory and need fresh deterministic risk plus human PAPER trigger.

### Security Considerations

Untrusted import cannot choose execution context, call URLs/tools or change policy. Human-attested provider/version provenance is labeled, not falsely verified.

### Testing Requirements

Malicious/replayed/stale/oversized expert corpus, redaction canaries, tenant swaps, blind leakage and full risk rejection UAT; ADV-18. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-08, V0-09, plus explicit Design Gate 1 approval.

### Out of Scope

OpenAI API integration, automatic browser scraping, sharing brokerage records, frontier execution tools.

## V0-11: Build preregistered A/B/C/D experiment and cost accounting

**Milestone:** M4 Research and experiments
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** REQ-P0-13, REQ-P0-17

### Problem

Better narratives and short-run winners do not demonstrate incremental investment value.

### Scope

Matched quantitative/local/frontier/passive experiment arms, frozen protocol, point-in-time recommendation outcomes, benchmark/metrics, data/execution/slippage costs and externally billed intelligence attribution.

### Acceptance Criteria

- Same initial capital, universe constraints, data cutoffs, decision windows and cost conventions across arms; frontier discovery bias tracked.
- All serious executed/rejected/unselected ideas retain prespecified horizons and missing-outcome handling.
- Report gross, execution-net and billed-intelligence-net results; manual subscription marginal/allocated costs separated without double count.
- Report uncertainty, multiple testing/regime limitations and minimum evidence gates; no short-run proof or automated live promotion.

### Security Considerations

Tenant-scoped cost and research data, immutable protocol/results versions, exports minimized. No new billing/paid service requirement.

### Testing Requirements

Independent arithmetic oracles, counterfactual replay, timestamp/look-ahead, survivorship/corporate actions, missingness and cost allocation fixtures; ADV-21. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-03, V0-04, V0-07, V0-08, plus explicit Design Gate 1 approval.

### Out of Scope

Pricing/billing collection, guarantee of edge, automatic optimization on holdout, real-money experiment.

## V0-12: Run integrated adversarial, recovery and owner UAT gate

**Milestone:** M5 PAPER readiness gate
**Priority:** P0
**Status:** PROPOSED — blocked until human approval of Design Gate 1.
**Traceability:** All P0; TEST_STRATEGY ADV matrix and UAT_PLAN

### Problem

Individually passing components do not prove the full financial control chain remains safe during compromise or outage.

### Scope

Independent code/security review, all required scanner/test evidence, threat-model abuse scenarios, shared-host/concurrency soak, backup/restore drill, complete owner UAT and residual-risk disposition.

### Acceptance Criteria

- No open Critical/High security or blocking financial/tenant/audit/model-safety defects; every discovered safety bug has regression coverage.
- Zero duplicate dispatch, cross-tenant data access, live capability or secret-bearing model payload in the full fault corpus.
- Owner reconstructs financial actions, stops/re-arms safely and verifies benchmark/cost ledger using UAT evidence.
- Owner explicitly approves only bounded human-triggered PAPER readiness; P1 unattended automation remains separately gated.

### Security Considerations

Disposable environments and synthetic tenants; external provider checks confined to approved paper scope. No unscoped attacks on host or public services.

### Testing Requirements

Complete TEST_STRATEGY and UAT_PLAN matrices, actual runtime network denials, scanner reports, measured recovery targets and reproducible evals. Every discovered finance, authorization, tenancy, security or model-safety bug requires a regression test.

### Dependencies

V0-01, V0-02, V0-03, V0-04, V0-05, V0-06, V0-07, V0-08, V0-09, V0-10, V0-11, plus explicit Design Gate 1 approval.

### Out of Scope

Implementing missing features under a test-only issue, live/customer launch, merging without owner approval.
