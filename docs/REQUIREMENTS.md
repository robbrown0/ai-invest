# Requirements

**Purpose:** Define prioritized user stories, measurable acceptance criteria, and test traceability.

**Status:** DRAFT — Design Gate 1 proposal; no capability described here is implemented.

## Priorities and evidence

P0 is mandatory for initial end-to-end V0 paper acceptance. P1 follows stable P0; specified P1 operations are mandatory before unattended evaluation. P2 improves research/usability. Future capabilities are unavailable in V0. Security invariants apply at every priority and cannot be deferred.

Stable `REQ-*` identifiers belong in implementation issues, test names, and UAT evidence. Test labels below describe required evidence, not existing tests. See [Test Strategy](TEST_STRATEGY.md) and [UAT Plan](UAT_PLAN.md). Numerical risk/capital values are proposed experiment parameters requiring human approval, not runtime configuration or investment advice.

## P0 stories

### REQ-P0-01 — Authenticate and terminate sessions

As an experimental investor, I want strong authentication so only authorized people can access my tenant.

Acceptance: approved identities authenticate through the chosen provider; evaluate passkey/WebAuthn and recovery before provider qualification. Unauthenticated requests reveal no protected data. Sessions have enforced expiry/revocation, secure cookie handling, and CSRF protection as applicable. Logout/revocation makes replay fail. Privileged actions require fresh authentication under the security policy. Recovery is audited without secret disclosure. Evidence: authorization/session integration tests and login/recovery UAT.

### REQ-P0-02 — Keep tenants and roles separate

As a tenant administrator, I want resources isolated so another tenant cannot read, change, or trigger activity in my tenant.

Acceptance: two or more tenant fixtures prove denied cross-tenant reads/writes, IDOR, exports, jobs, caches, research retrieval, audits, and dispatch. Application checks and PostgreSQL RLS both deny missing/invalid tenant context. Composite references reject cross-tenant account/portfolio links. Platform/support roles have no automatic tenant-data or trade access. Evidence: direct SQL, API/job isolation, and two-user UAT.

### REQ-P0-03 — Create a bounded paper portfolio

As an investor, I want a paper portfolio with $100–$300 experimental capital so results reflect the intended scale.

Acceptance: bind portfolio to tenant/account/experiment arm/currency/versioned risk profile; show PAPER on every relevant screen. Permit one active broker-linked portfolio per brokerage account; other comparison arms use isolated simulator ledgers. Enforce the application budget independently of a larger broker paper balance, including open-order reservations. Invalid capital/ownership/lifecycle inputs fail. Resets create new runs/baselines and preserve history. Reject LIVE_LIMITED/LIVE server-side. Evidence: domain/tenant tests and portfolio UAT.

### REQ-P0-04 — Verify the paper connection and account state

As an investor, I want verified paper balances and connection state so I know which simulation is used.

Acceptance: execution's adapter is the only component performing authenticated broker operations; UI receives sanitized snapshots without secrets/raw identifiers. Plan paper-specific credentials provisioned into OpenBao outside LLM sessions; no credentials are provisioned in Phase 2. Verify environment, ownership, cash, restrictions, positions, and as-of time; buying power never permits margin. Unverified state blocks orders. Evidence: broker-simulator/account contracts and connection UAT.

### REQ-P0-05 — Label and validate market inputs

As a researcher, I want timestamped data with entitlement/quality labels so incomplete data is not mistaken for certainty.

Acceptance: record provider/feed, instrument identity, event/source/receipt times, and quality state. Duplicate, future-dated, stale, invalid, and missing observations follow a versioned reject/quarantine policy. Label delayed and single-venue feeds. Missing required price/liquidity evidence causes HOLD/rejection; no automatic purchase or unapproved feed substitution. Evidence: schema/data-quality contracts and stale-feed UAT.

### REQ-P0-06 — Run a cheap quantitative baseline

As a research lead, I want reproducible quantitative screening so AI has a fair comparator.

Acceptance: versioned universe/rules produce ranked candidates or HOLD with feature/data versions and decision cutoff. Numerical calculations occur outside LLMs. Exclude unavailable-at-cutoff data. Bound candidate counts and resource budgets. Evidence: independent financial fixtures, determinism/leakage tests, research UAT.

### REQ-P0-07 — Research and remember serious opportunities

As an analyst, I want persistent local research on unpurchased and purchased ideas so effort accumulates and outcomes can be measured.

Acceptance: record security, thesis/status, bull/bear cases, catalysts, invalidation/watch conditions, confidence meaning, source references/timestamps, model/prompt versions, review date, and horizon. Updates append immutable versions; uncertainty/contradictions are visible. Rejected, expired, and HOLD recommendations retain outcomes. Minimized research inputs contain no brokerage secrets or authority. Evidence: research schema/evaluation/provenance tests and opportunity UAT.

### REQ-P0-08 — Generate proposals, including HOLD

As an investor, I want labeled proposals so advice is distinguishable from an order.

Acceptance: validate structured action/instrument/notional-or-quantity/account/portfolio/expiry/research references/rationale. HOLD persists with a reason and creates no order. Reject executable content, credential requests, and caller-chosen execution URLs. Repeated outputs cannot silently create duplicate intent. Evidence: schema/fuzz tests and proposal UAT.

### REQ-P0-09 — Enforce deterministic financial risk

As an investor, I want all proposals checked against current account/risk state so AI cannot bypass limits.

Acceptance: every [Risk Model](RISK_MODEL.md) control returns reason codes, observed values, policy version, and expiry. Missing facts fail closed. Cover cash-only behavior, prohibited assets, position/sector/concentration/turnover limits, liquidity, loss/drawdown, stale data/recommendations, market hours, price/order sanity, reservations, account status, and kill state. Risk has no broker credential and cannot submit. Evidence: unit/boundary/property tests and rejection UAT.

### REQ-P0-10 — Submit authorized paper intent only

As an investor, I want an approved paper proposal submitted once so the risk decision controls actual intent.

Acceptance: P0 human dispatch of the exact proposal triggers a fresh authoritative risk evaluation; any earlier preview evaluation grants no execution authority. Execution validates the resulting short-lived, single-use approval bound to tenant/account/proposal/policy/state. Recheck environment, kill state, authorization freshness, reservations/state immediately before dispatch. Fixed paper endpoint; reject supplied broker URLs and live grants. Expired approval requires reevaluation; the user is not asked to review within its short TTL. No direct UI/model order route. Evidence: execution/replay/concurrency contracts and full-chain UAT.

### REQ-P0-11 — Reconcile all order outcomes

As an investor, I want truthful states after failures so timeouts cannot create duplicate trades or false fills.

Acceptance: durable intent and stable broker client-order identity precede requests. Timeouts become UNKNOWN/RECONCILIATION_REQUIRED, never success or a new retry identity. Reconcile by account/stable identity before retry. Specify partial fills, cancellation races, rejections, duplicate/out-of-order events, corporate actions, restarts, and outages. Derive positions/cash from reconciled facts with correction history. Evidence: crash/replay/simulator tests and ambiguous-order UAT.

### REQ-P0-12 — Reconstruct consequential actions

As an auditor, I want a complete tenant-scoped event chain so financial and administrative actions can be explained.

Acceptance: resolve actor/service, authorization, configuration/risk versions, source availability, model/input/output versions, proposal, evaluation, dispatch, response, fills, and reconciliation for each order. Audit auth, import, lifecycle, kill, access/change/failure events. Durable audit failure blocks new dispatch. Never record secrets; tamper-evidence verification detects tested alteration/deletion. Evidence: integrity/redaction tests and audit UAT.

### REQ-P0-13 — Understand portfolio and performance

As an investor, I want a clear dashboard so risk and return can be compared with a passive benchmark.

Acceptance: show positions, cash/reservations, pending/unknown orders, exposure, realized/unrealized performance, drawdown, benchmark, timestamps, and mode. Strategy/benchmark share windows and cash-flow conventions. Label provisional/unavailable/insufficient-history metrics. Show return net of external costs alongside gross results without promises. Evidence: independently calculated fixtures and dashboard/benchmark UAT.

### REQ-P0-14 — Stop dispatch safely

As an authorized operator, I want a persistent emergency stop so new paper dispatch ceases even while research runs.

Acceptance: global/tenant/account/portfolio scopes have deny precedence and durable latches checked by every dispatch. Distinguish stop requested/confirmed/unreachable; show in-flight orders. Attempt open-order cancellation and reconcile residual fills. Stop is not liquidation or reversal of sent requests. Restart never clears the latch. Resume requires a separate fresh-authenticated human action after reconciliation; agents cannot resume. Evidence: dispatch-race/restart/cancel-failure tests and stop UAT.

### REQ-P0-15 — Generate a minimized expert packet

As an investor, I want a self-contained manual review packet so deeper research does not need an application API account.

Acceptance: tenant-scoped preview shows exact export and requires external-disclosure confirmation and fresh authentication under the security policy. Allowlist excludes credentials, keys, raw account identifiers, PII, sessions, hidden prompts, and unrestricted documents. Include schema/version, a one-time random export nonce, source/snapshot cutoffs, constraints, redacted holdings, questions, and output contract. Never export internal tenant/portfolio/research/run identifiers; nonce-to-resource mapping stays inside the tenant-scoped application. Stage A solicits broad independent research without local conclusions; Stage B reveals local hypotheses after A is sealed. Evidence: export/redaction/isolation tests and packet UAT.

### REQ-P0-16 — Import expert advice as untrusted evidence

As an investor, I want safe import so external advice can be compared and challenged.

Acceptance: quarantine with size/type/schema checks, packet/tenant/expiry binding, provenance/cost capture, and human preview. Commands, attachments, auto-fetch URLs, malformed values, prohibited assets, or stale evidence cannot become orders. Valid imports create versioned research/proposals only, subject to the complete risk/dispatch chain. Claimed citations remain unverified until checked. Re-import is idempotent. Evidence: malicious-import/fuzz/isolation tests and import UAT.

### REQ-P0-17 — Measure experiments and external costs

As a research lead, I want consistent A/B/C/D outcomes so additional intelligence is tested rather than presumed valuable.

Acceptance: pre-register arm rules, capital, benchmark, timing, costs, metrics, horizons, and exclusions. C is optional; missing C is not success. Preserve executed/rejected/HOLD ideas with decision-time facts and later outcomes. Report total/excess return, drawdown, volatility, risk-adjusted measures, turnover, win rate, mean gain/loss, largest loss, concentration/correlation, execution/data/model costs, slippage assumptions, and net return with uncertainty. Show subscription allocations and unknown costs. Evidence: leakage/cost fixtures and experiment UAT.

### REQ-P0-18 — Recover encrypted data and keys

As an operator, I want validated encrypted backups so host loss does not silently erase audit history or weaken controls.

Acceptance: required TDE, sensitive-field envelope encryption, OpenBao permissions, backup encryption, and separate recovery-key custody pass synthetic evidence before paper credential provisioning. Restore verifies data and historical decryptability. Missing DB/key service blocks dispatch. NAS outage affects archive health but not local operation while local capacity is sufficient. Human-approved RPO/RTO are exercised. Evidence: rotation/key-loss/backup/restore/NAS tests and restore UAT.

### REQ-P0-19 — Govern models and failure safely

As a model steward, I want explicit versions and rollback so changes cannot silently alter behavior.

Acceptance: record provider/model/version (or honest unknown), artifact/quantization hashes, prompt/agent/schema versions, input provenance/cutoff, validation, latency/cost. Promotion requires regression/shadow evaluation and human approval. Invalid output, outage, hallucination, injection, or budget exhaustion produces HOLD/failed research with audit evidence. Models cannot reach broker/secrets/host sockets/privileged APIs. Evidence: evaluation/injection/isolation tests and provenance UAT.

### REQ-P0-20 — Make operational failure visible

As an operator, I want health/capacity/security signals so local failures do not quietly corrupt the experiment.

Acceptance: local dashboards show DB/keys/data/broker/model/audit/backup health without secrets. Bound jobs, input sizes, timeouts, GPU/RAM/disk usage; prioritize execution/reconciliation over optional research. Reboot, disk exhaustion, network/dependency/clock failure has a documented safe state. Critical/High findings block release. Every finance/auth/tenant/security/model-safety bug creates a regression test. Evidence: outage/capacity/security suites and health UAT.

## P1 stories

| ID | Story | Measurable acceptance and evidence |
| --- | --- | --- |
| REQ-P1-01 | As an investor, I want scheduled paper operation without constant interaction. | Human-enabled PAPER schedule, account budgets/leases, idempotent jobs, calendar/backpressure; missed jobs never backfill stale orders. Required before unattended evaluation; schedule/outage/concurrency UAT. |
| REQ-P1-02 | As a researcher, I want event/overnight research for material changes and outside opportunities. | Deduplicated triggers, bounded queues, recorded coverage/new-symbol attribution, quality/budget caps; no new broker authority. Load/trigger and overnight UAT. |
| REQ-P1-03 | As an analyst, I want watch conditions for serious unpurchased ideas. | Versioned predicates, expiry/review queue, immutable history, outcome joins by instrument identity; corporate-action/point-in-time tests. |
| REQ-P1-04 | As a tenant owner, I want scoped membership administration. | Invite expiry, role enforcement, last-owner protection, revocation propagation/audit; no support trading. Role-matrix/revoked-job tests. |
| REQ-P1-05 | As a model steward, I want calibrated agent comparisons. | Predeclared confidence/horizons, held-out scoring, agent ablations by regime/version, uncertainty/insufficient-sample flags; evaluation UAT. |
| REQ-P1-06 | As an operator, I want controlled support/incident access. | Reason, approver, fresh authentication, expiry, scope, audit; no unilateral trade/lifecycle power. Break-glass/access-expiry exercise. |
| REQ-P1-07 | As a tenant owner, I want secure export/deletion requests. | Tenant-only manifest export excluding secrets, verified identity, retention holds, restored-backup handling; cross-tenant/export tests. Legal periods remain unselected. |
| REQ-P1-08 | As an operator, I want repeatable recovery/patch drills. | Restore, dependency/key rotation, rollback and incident exercises meet approved targets; independent review before unattended paper release. |

## P2 stories

| ID | Story | Measurable acceptance and evidence |
| --- | --- | --- |
| REQ-P2-01 | As an investor, I want richer diversification/hypothesis visuals. | Accessible tables for charts, consistent filters, correlation sample/coverage labels; financial/UX fixtures. |
| REQ-P2-02 | As a researcher, I want additional local model choices. | Provider contract, artifact/license inventory, measured capacity, evaluation/rollback gate; no automatic installation/promotion. |
| REQ-P2-03 | As an analyst, I want broader licensed datasets. | Entitlement/redistribution/retention and quality gates per feed; explicit billed-usage approval; contracts. |
| REQ-P2-04 | As an investor, I want optional budgeted frontier API review. | Disabled-by-default adapter, approved data policy, redaction, hard budget, cost attribution, existing risk chain; exfiltration/budget tests. |
| REQ-P2-05 | As an operator, I want alternate encrypted archives. | Independent data/key placement, integrity and restore evidence; no NAS dependency for primary DB/execution. |

## Future stories — unavailable in V0

| ID | Story | Gate before consideration |
| --- | --- | --- |
| REQ-F-01 | As an owner, I may want a limited real-money experiment. | Separate implementation/release, extended predeclared paper/shadow evidence, human approval/fresh authentication, new credential/network/security/UAT evidence; never a mode-flag or score promotion. |
| REQ-F-02 | As a customer, I may want commercial automated investing. | Qualified legal/compliance review, consent, risk profiling/disclosures, privacy/incident/support operations, independent security and tenancy evidence. |
| REQ-F-03 | As a business operator, I may want billing. | Subscription/usage/AUM alternatives reviewed; performance fees require specific legal analysis; separate costs/billing/performance. No V0 billing. |
| REQ-F-04 | As an investor, I may want another broker. | Capability/environment/identity contracts and full reconciliation/failure suite; no weakening of controls. |
| REQ-F-05 | As an operator, I may want managed infrastructure/high availability. | Portability/migration/restore, custody, tenancy, residency, cost/failure-domain review without replacing ownership/authority boundaries. |

## Cross-cutting non-functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| NFR-01 | Defense in depth | Independently tested networks/identities/authorization, non-owner/non-bypass RLS roles, TLS, supply-chain/container review, no Critical/High release findings. |
| NFR-02 | Accessibility/mobile | Target WCAG 2.2 AA; keyboard/screen-reader critical journeys, text beyond color, 320 CSS-pixel reflow, 200% zoom, focus/errors, no precision gesture to stop. |
| NFR-03 | Financial arithmetic | Versioned decimal/precision/rounding/calendar conventions; independent expected results and invariant/property tests. |
| NFR-04 | Observability | Research-to-fill correlation, no secrets, redacted metrics, visible freshness/UNKNOWN states. |
| NFR-05 | Cost/capacity | Required external recurring cost $0; approved optional budgets; measured host reservations before model deployment. |
| NFR-06 | Recovery/containment | Approved measurable recovery targets; NAS outside critical path; missing durable state/key access blocks dispatch and demands reconciliation. |
| NFR-07 | Privacy/retention | Classification/minimization, approved external exports, policy-driven retention/export/deletion; no invented statutory period/compliance claims. |
| NFR-08 | Portability | Broker/model/identity/storage interfaces, versioned contracts/migrations/ADRs; no global tenant/account singleton. |

## Requirement-to-UAT map

These scenario references identify future evidence in [UAT Plan](UAT_PLAN.md). Automated test categories remain specified in each story above. A scenario demonstrates user-observable behavior and does not replace direct SQL, concurrency, cryptographic or service-isolation tests.

| Requirement | UAT scenarios |
| --- | --- |
| REQ-P0-01 | UAT-01, UAT-11 |
| REQ-P0-02 | UAT-17, UAT-22 |
| REQ-P0-03 | UAT-02, UAT-24 |
| REQ-P0-04 | UAT-03 |
| REQ-P0-05 | UAT-04, UAT-05, UAT-19 |
| REQ-P0-06 | UAT-05, UAT-15 |
| REQ-P0-07 | UAT-05, UAT-14 |
| REQ-P0-08 | UAT-06 |
| REQ-P0-09 | UAT-08, UAT-18 |
| REQ-P0-10 | UAT-07, UAT-24 |
| REQ-P0-11 | UAT-09, UAT-16 |
| REQ-P0-12 | UAT-16, UAT-22 |
| REQ-P0-13 | UAT-04, UAT-15 |
| REQ-P0-14 | UAT-10, UAT-11 |
| REQ-P0-15 | UAT-12 |
| REQ-P0-16 | UAT-13 |
| REQ-P0-17 | UAT-14, UAT-15 |
| REQ-P0-18 | UAT-19, UAT-20, UAT-21 |
| REQ-P0-19 | UAT-06, UAT-25 |
| REQ-P0-20 | UAT-19, UAT-20, UAT-22 |
| REQ-P1-01 | Extend UAT-07/09/10/19 for unattended schedules before P1 acceptance |
| REQ-P1-02, REQ-P1-03 | Extend UAT-05/14 for event, overnight and watch-trigger runs |
| REQ-P1-04, REQ-P1-06 | Extend UAT-17/22 for invites, revocation and support-expiry scenarios |
| REQ-P1-05 | Extend UAT-14/15/25 for calibration and agent ablations |
| REQ-P1-07 | Extend UAT-17/21/22 for export, deletion holds and restored backups |
| REQ-P1-08 | UAT-11, UAT-19 through 22 with approved recovery/patch drill targets |
| NFR-02 | UAT-23 plus manual WCAG-focused checks |

P2/Future stories require new or expanded UAT plans when authorized; no initial UAT sign-off accepts those capabilities. Unapproved thresholds, cadence, recovery targets, provider choices, benchmark/universe, research horizon, and disclosure policy must not acquire permissive runtime defaults. See [Phase 2 Review](PHASE2_REVIEW.md) for human decisions.
