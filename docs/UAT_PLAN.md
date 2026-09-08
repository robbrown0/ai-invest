# User Acceptance Test Plan

**Status:** DRAFT — scenarios for a future implemented PAPER release.
**Purpose:** Give the product owner understandable evidence of safe, explainable operation.

## Preconditions and evidence

Execute after approved implementation tests and independent security review, on an isolated PAPER environment with two synthetic tenants and a $100–$300 virtual capital budget. A human provisions PAPER credentials through the approved secret channel; never paste them into an assistant. Establish a frozen quote/source fixture, independent expected benchmark ledger, and a second tenant with different users, portfolios and opportunities.

BACKTEST/SHADOW scenarios use no broker-submission path. Record scenario ID, release/model/prompt/policy versions, UTC time, user role, tenant alias, expected/observed outcome, sanitized screenshots or audit references, and pass/fail. Block the trial on any unintended order, tenant disclosure, secret exposure, unexplained ledger difference or unreconstructable action. All scenarios below are future acceptance plans, not tests claimed run during design.

## Scenarios

| ID | Product-owner actions | Observable pass criterion |
| --- | --- | --- |
| UAT-01 | Sign in with enrolled passkey; sign out; attempt an old session and wrong tenant | Valid session works, old session denied, accessible errors disclose no other tenant; recovery requires approved identity proof |
| UAT-02 | Create tenant profile and PAPER portfolio with $200 simulated capital | Persistent PAPER badge; effective risk capital is $200 even if broker balance is larger; zero route to live modes |
| UAT-03 | Connect human-provisioned paper connection and inspect balances | Environment and last sync visible; credentials/real account identifiers never displayed in logs/model context; mixed/live grant rejected |
| UAT-04 | Open dashboard, positions, performance and benchmark | Cash/equity/exposure reconcile to independent fixture; stale values labeled; same window and cashflow conventions for benchmark |
| UAT-05 | Observe scan and open opportunity not owned in portfolio | Source timestamps, thesis versions, bull/bear evidence, catalysts, invalidation and missed evidence are visible |
| UAT-06 | Inspect a proposed BUY and a HOLD recommendation | Recommendation is distinguishable from order; role/model/prompt/cutoff/confidence provenance visible; HOLD produces no order |
| UAT-07 | Approve a small allowed paper proposal through risk and execution | One proposal, deterministic reasons, one consumed approval, broker acknowledgment then fill/state; never confuse sent with executed |
| UAT-08 | Propose above-limit size and prohibited asset; retry with confident AI text | Clear rule-specific rejection; no broker dispatch; rejected recommendation persists for later outcome analysis |
| UAT-09 | Generate duplicate requests and simulate broker timeout | UI shows existing/UNKNOWN order, reserved exposure and investigation; no second trade; eventual reconciliation resolves original |
| UAT-10 | Trigger portfolio, account, tenant and global kill switches with queued and partially filled paper orders | Each scope blocks subsequent dispatch under deny precedence; canceled/pending cancel/possible residual fills visible; no liquidation or silent restart |
| UAT-11 | Try re-arm with expired authentication and restart the host | Denied until fresh human authentication, health/reconciliation pass; stop stays engaged after reboot |
| UAT-12 | Generate frontier review packet and inspect export preview | Only consented minimized context, source provenance and packet expiry; no broker IDs/secrets/PII; blind stage hides local thesis |
| UAT-13 | Import valid expert response, then malformed, replayed and malicious responses | Valid response quarantined/reviewable advisory record; invalid inputs rejected; accepted idea still goes through ordinary fresh risk chain |
| UAT-14 | Inspect high-confidence, rejected and unexecuted recommendation outcomes | All serious ideas retained at original cutoff with fixed horizons; missing prices labeled; no hindsight rewriting |
| UAT-15 | Compare A/B/C/D experiment arms and external-cost totals | Consistent capital/window/pricing, benchmark and net cost labels; manual subscription allocations disclosed; no annualized certainty claim |
| UAT-16 | Reconstruct one partial fill and rejection from audit | Navigate actor, intent, policy/state, model/source evidence, broker response and economic event without secret exposure |
| UAT-17 | With tenant B credentials, reuse tenant A URLs, exports, jobs and object IDs | No reads/writes or existence leakage; deny appears in security audit; own tenant remains usable |
| UAT-18 | Change risk limits as unauthorized role then as authorized fresh session | Unauthorized denied; authorized change versioned/audited, stale approvals invalidated, affected scopes previewed |
| UAT-19 | Disconnect data, model, OpenBao, DB and broker separately in test environment | Specific degraded state shown; no unsafe fallback or stale execution; recovery reconciliation required |
| UAT-20 | Disconnect both NAS devices during local operation | Dashboard/control continues from local state, archive lag visible; recovery copies resume and integrity verifies |
| UAT-21 | Restore isolated encrypted backup using recovery procedure | No automatic dispatch/outbox replay, audit/ledger matches expected state; key-loss variant fails explicitly; measured RPO/RTO recorded |
| UAT-22 | Review admin/support/security views | Least-privilege scope, no default tenant impersonation or key viewing, time-limited break-glass events visible |
| UAT-23 | Complete core tasks on narrow mobile viewport and keyboard/screen reader | Mode/status not color-only, focus/errors announced, usable tap targets, stop reachable, financial table alternatives understandable |
| UAT-24 | Attempt BACKTEST/SHADOW to LIVE_LIMITED/LIVE using UI and tampered request | Unsupported mode rejected, no live endpoint/secret lookup/submission, audit explains denial |
| UAT-25 | Attempt model version change and compare adverse source injection fixture | Unapproved version blocked, approved change shadow-tested and versioned; injected source cannot request tools/credentials/orders |

## Traceability and sign-off

[REQUIREMENTS.md](REQUIREMENTS.md) identifies P0/P1 stories; [TEST_STRATEGY.md](TEST_STRATEGY.md) provides ADV cases covering implementation-level boundaries. All P0 stories need an automated test family and one applicable UAT scenario; final issue owners maintain the map as implementation evolves. No scenario counts as passed solely because a mock UI behaves correctly.

Product owner signs PAPER readiness only after reviewing UAT evidence and unresolved residual risks. Security reviewer signs authorization/tenancy/audit boundaries; quantitative reviewer signs financial/experiment calculations. Failed scenarios become tracked defects and regression tests. Sign-off cannot authorize LIVE_LIMITED/LIVE or outside-customer use. Design Gate 1 merely approves proceeding to the separately planned implementation.
