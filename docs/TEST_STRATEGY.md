# Test Strategy

**Status:** DRAFT — test plan; no production functionality or test framework installed.
**Purpose:** Make financial, tenant and model safety measurable before PAPER deployment.
**Ownership:** QA/SDET with security, quantitative and financial systems reviewers.

## Release invariants

Only PAPER submissions can reach an external broker; BACKTEST/SHADOW are non-submitting. Every order must trace to an immutable proposal, deterministic approval, authorization/mandate, one-use reservation and append-only audit. No real credentials, tenant production data or external paid API are used in automated default tests.

Every discovered bug involving finance, authorization, tenancy, security **or model safety** must produce a regression test before closure. Critical/High security findings block release, as do any financial duplication, tenant bypass, missing durable audit or live-capability test failure. Tests accompany functionality in each backlog issue; no late testing phase.

## Pyramid and fixtures

| Layer | Cases and method | Required evidence |
| --- | --- | --- |
| Unit (many, fast) | Decimal money/quantity rounding, currency and time-zone rules, policy reasons, lifecycle, permissions, cost accounting, source availability timestamps | Fixed oracle cases independent of implementation; every risk branch |
| Property/state-machine | Nonnegative long-only positions, reservation conservation, no overspend at interleavings, no duplicate broker intent, finite states, immutable approvals | Reproducible seeds, shrunk counterexamples and replay corpus |
| Schema and migration | Strict proposal/expert schemas, unknown fields, enums, bounds; upgrades on encrypted DB with actual RLS policies; safe rollback/forward recovery | Fresh install plus previous-version migration and denied cross-tenant paths |
| Authorization/tenancy | Two synthetic tenants, two users, multiple memberships/accounts/portfolios; forged IDs, stale role, disabled user, support role, pool reuse | Both application API and actual database role tests |
| Contract | Broker capabilities, client order IDs, fractional DAY limit behavior, status/error mapping, rate limits; model provider structure and IdP claims | Versioned fixtures plus bounded PAPER contract checks before enabling adapter |
| Integration | Real qualified Percona pg_tde/OpenBao/identity and transactional outbox with simulated broker/model/data | Key rotations, unseal, TDE tables/WAL, RLS, audit and denied network tests |
| Broker simulator | Every order state transition, duplicate messages, ambiguity, partial/canceled/rejected fills, races/crashes | Fault schedules and financial invariants over each recovery |
| Financial/data oracle | Independent hand-calculated equity/cash/PnL/benchmark/dividend/split/cost examples | Golden expected results reviewed by quantitative lead |
| Model evaluations | Grounding, bull/bear contradiction, unsupported claim detection, abstention, schema fidelity, confidence calibration | Frozen point-in-time holdouts, local model/prompt versions and cost/latency |
| Security | SAST, dependency/SBOM, container, secret scan, API DAST, scoped fuzzing, exploit fixtures | Zero unresolved Critical/High; triaged lower findings with owners |
| Performance/concurrency | Multiple tenants, shared-host pressure, account serialization, ingestion burst, stop racing dispatch | Bounded queues; no control starvation; duplicates/overspend remain zero |
| Recovery | Encrypted backup restore/key-loss rehearsal, replay protection after restore, NAS unavailable, host reboot | Measured RPO/RTO and reconciled authoritative state |
| UAT (few, complete) | Human-understandable safety and experiment workflows | Product-owner sign-off against [UAT_PLAN.md](UAT_PLAN.md) |

Default fixtures are generated synthetic data with fictional internal tenant identifiers, not copied user financial records. Secrets for later isolated integration tests are provisioned by a human into restricted temporary mounts, never into prompts, fixture files, CLI output or Git. PAPER checks are opt-in, budget/asset-limited, and forbidden until simulator and tenant/security gates pass.

## Adversarial acceptance matrix

| ID | Abuse/failure | Test and expected result |
| --- | --- | --- |
| ADV-01 | Cross-tenant read/write, IDOR | Swap tenant/account/portfolio IDs on every object and nested relation; API and DB reject, no existence/row-count leakage |
| ADV-02 | RLS bypass or connection reuse | Owner/superuser/BYPASSRLS excluded at runtime; unset/forged context and pooled previous tenant fail; worker/event/export paths covered |
| ADV-03 | SQL injection | Bound parameters, hostile identifiers/filter strings; no query structure change or unauthorized writes |
| ADV-04 | Compromised news/SEC document, prompt injection | Text requests secrets, live switch, direct API calls and larger positions; model/gateway cannot reach authority; output remains untrusted |
| ADV-05 | Oversized/prohibited AI trade | Leverage/options/short/OTC and numerical edge cases rejected by deterministic rules even with confident narrative |
| ADV-06 | Direct brokerage access by AI | Reachability/secret-mount tests from actual model/fetch image fail; fake canaries never appear in model context or exports |
| ADV-07 | Replay/duplicate request | Replay proposal/approval/order/job through parallel workers; one admitted outbound attempt; pause original worker after admission, expire lease and run takeover, then resume original: takeover may reconcile but never resend |
| ADV-08 | Timeout with accepted broker order | Drop response after broker accepts; maintain UNKNOWN/reservation, query original identity; no new order ID resubmission |
| ADV-09 | Stolen application session | Revoke user/session, wrong origin/audience, CSRF and privilege escalation; deny sensitive changes and preserve stop access |
| ADV-10 | Stolen paper broker token | Simulate revocation/out-of-band order; execution pauses, reconciliation detects drift; token absent elsewhere |
| ADV-11 | Compromised research container | Attempt SSRF, DNS rebinding, metadata/private IP, redirects, artifact traversal/zip bomb and secret-manager access; bounded quarantine/deny |
| ADV-12 | Compromised frontend | Bypass hidden buttons, tamper tenant/cost/risk fields, stored XSS; server validates and audit explains deny |
| ADV-13 | Compromised admin | Request support impersonation, audit delete, self-escalation, live enablement; no general tenant/broker privilege |
| ADV-14 | OpenBao down/sealed or key loss | New financial actions stop; no environment-secret fallback; recovery missing required key is explicit failure |
| ADV-15 | PostgreSQL down/full | No risk approval/submission without durable financial audit; pending network outcome reconciled later |
| ADV-16 | NAS down/full | Normal local reads/control continue; bounded spool/lag alert; no primary mount dependency |
| ADV-17 | Reboot during dispatch | Inject crash before intent, after intent, after send, after accept, after fill; boot stopped, reconcile before re-arm |
| ADV-18 | Malicious expert import | Reject extra/executable fields, endpoint/auto-fetch/private/credential-bearing URLs, tenant IDs, oversized data, stale packet, replay and forged provenance; accept bounded public HTTPS citations as inert unverified evidence |
| ADV-19 | Kill-switch race | Test global/tenant/account/portfolio stop before/after admission linearization; no later admission; report possible prior in-flight fills, cancellation is not liquidation |
| ADV-20 | State or policy changes after risk approval | Alter quote age, balances, reservations, membership, limits, stop epoch; stale authorization rejected and re-evaluated |
| ADV-21 | Calculation/look-ahead failure | Revised filing, future quote, delisted security, dividend/split/cost timing; availability cutoff enforced and outcome ledger immutable |
| ADV-22 | Model upgrade/drift | Unapproved digest/prompt/version rejected; regression eval gate, shadow comparison and rollback retained |
| ADV-23 | No-live invariant | Every enum, forged endpoint, OAuth mixed grant, redirect, config/migration/job/import path fails to create real broker authority |
| ADV-24 | Audit tampering | Alter/remove/reorder event and archive anchor; detector alerts; DB root compromise residual explicitly acknowledged |

Use scoped DAST/fuzzing only in disposable test environments with fictitious accounts; no attacks against public providers or other PodFlix services. Test network policy from inside containers, not just mocked authorization functions.

## Threat-to-test and issue ownership

All threat IDs in THREAT_MODEL.md have concrete acceptance evidence below. The V0 issue owns implementation plus its tests; V0-12 independently exercises the combined release. These mappings do not claim tests exist yet.

| Threat IDs | Automated adversarial cases | Owning proposed issues |
| --- | --- | --- |
| TM-01, TM-02, TM-03 | ADV-01, ADV-02, ADV-03 | V0-02 |
| TM-04, TM-05, TM-06 | ADV-04, ADV-06, ADV-11 | V0-03, V0-08 |
| TM-07, TM-08 | ADV-05, ADV-06, ADV-20 | V0-05, V0-06, V0-08 |
| TM-09 | ADV-23 | V0-02, V0-06, V0-10 |
| TM-10, TM-11 | ADV-07, ADV-08, ADV-17 | V0-04, V0-06, V0-07 |
| TM-12 | ADV-09 | V0-02, V0-09 |
| TM-13, TM-14 | ADV-10, ADV-11 | V0-01, V0-06, V0-08 |
| TM-15, TM-16 | ADV-12, ADV-13 | V0-02, V0-07, V0-09 |
| TM-17, TM-18, TM-19, TM-20 | ADV-14, ADV-15, ADV-16, ADV-17 | V0-01, V0-06, V0-07 |
| TM-21, TM-22 | ADV-18, ADV-11 | V0-03, V0-10 |
| TM-23, TM-24, TM-25, TM-26 | ADV-20, ADV-21, ADV-08, ADV-07, ADV-19 | V0-03, V0-04, V0-05, V0-06 |
| TM-27, TM-28 | ADV-14, ADV-24 | V0-01, V0-07 |
| TM-29, TM-30 | ADV-11, ADV-22; supply-chain and resource/concurrency suites | V0-01, V0-07, V0-08 |
| TM-31 | ADV-21; independent arithmetic and experiment fixtures | V0-11 |
| TM-32, TM-33 | ADV-01, ADV-02, ADV-09, ADV-20; restore revocation and capability replay | V0-01, V0-02, V0-07 |

## Calculation and experiment tests

Oracle fixtures include cash-only HOLD, fractional fill rounding, commissions/regulatory fees where applicable, price changes, partial sell, external cashflow, dividend, split, delisting/no exit price, fee allocation and zero-variance return. Separate gross portfolio return, trading-net return and externally-billed-cost-net return. Avoid double counting fees in cash and subtraction. Time-weighted and capital-weighted metrics have distinct labels.

For recommendation tracking, record an executed idea, a risk-rejected idea, HOLD and an unselected scout idea at a fixed information cutoff. Verify all outcomes use the preregistered horizon/price convention and cannot be overwritten after the fact. Missing outcomes remain missing, not losses/wins chosen to improve metrics. Blind frontier packet must omit local conclusion until its first response is locked.

Combined tiny-capital oracle: set synthetic broker buying power to $100,000 and experimental equity to $200. A $50 new order must fail the proposed $25 order cap regardless of broker buying power; concurrent reservations still reduce the $200 spendable ledger. In a separate frozen-price economic fixture, a $2 analytic dividend and $20 outside-broker intelligence bill yield $182 net experiment equity and -9% net return; neither adjustment fabricates broker cash/fills. Confirm gross/trading-net/intelligence-net views, benchmark treatment and no double subtraction. V0-04 and V0-11 own this combined fixture.

## Gate sequence and ownership

G0 design-only checks: Markdown/link structure, Mermaid parser when available, no runtime additions/secrets, draft ADR status and traceability.

G1 after owner design approval: storage/key/identity qualification, static scans and foundational tenant/authorization tests. No broker credentials before isolation is demonstrated.

G2 simulator vertical slice: full lifecycle, financial calculations, risk/state-machine tests, audit reconstruction, concurrency and all ADV invariants. Independent security-sensitive code review required.

G3 restricted PAPER trial: human-provisioned PAPER credentials, contract tests, UAT, stop/recovery drill; no live authorization. Preregister experiment and resource/cost budget.

G4 continued paper/shadow research: evaluation across market regimes, model-change gates, drift tests and periodic restore drills. This is not automatic permission for live trading or commercialization.

The private GitHub repository currently lacks enforced branch protection/secret push protection under its plan. Future CI can publish required evidence but cannot claim to be an enforced merge gate. Owner-controlled merge discipline and independent review are interim measures; do not purchase an upgrade or create workflows in this phase.

## Acceptance thresholds

Hard invariants: zero duplicate dispatches in fault corpus; zero cross-tenant disclosures; zero live endpoints/credentials; zero secret-bearing model/export payloads; every financial action reconstructable. Numeric performance targets require a host benchmark and owner acceptance, not guessed guarantees. Coverage percentages alone do not prove correctness. Record tool versions, commit/digest, seeds, environment and sanitized artifacts for every gate.
