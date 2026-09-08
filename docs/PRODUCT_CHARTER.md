# Product Charter

**Purpose:** Define the experiment, product boundaries, stakeholders, and success criteria.

**Status:** DRAFT — Design Gate 1 proposal; human approval is required before implementation.

## Mission and hypothesis

`ai-invest` is a temporary internal name for a secure, multi-tenant, local-first investment research and paper-trading experiment. Its purpose is to determine whether quantitative methods augmented with AI research improve investment decisions after risk and externally billed costs. Useful evidence includes a finding of no benefit. Model eloquence and a profitable short interval do not establish investment edge.

Start with approximately $100–$300 of simulated capital per experimental arm. Compare a quantitative baseline, local-AI assistance, optional frontier-expert assistance, and a preselected passive benchmark under consistent capital, timing, risk, data, and cost assumptions. Real capital of a similarly small size is a possible later experiment, never an outcome automatically earned by paper performance. An extended paper/shadow evaluation, explicit human authorization with fresh authentication, security evidence, and a separately approved release are prerequisites for considering it.

## Product principles

- HOLD / DO NOTHING is a first-class outcome, including when evidence, data quality, economics, or infrastructure are inadequate.
- Discover opportunities outside existing positions, investigate repricing catalysts, and challenge every serious thesis with a bear case and invalidation conditions.
- Maintain opportunity memory for purchased, rejected, expired, and deferred ideas. Preserve contemporaneous evidence and subsequent outcomes without rewriting history.
- Use deterministic calculations and statistics where reliable; reserve language models for interpretation and synthesis. Escalate to deeper local reasoning selectively and to external review only within an approved cost/disclosure boundary.
- Recommendations have no trading authority. Only a deterministic risk-approved proposal may reach the separately authorized execution service.
- Tenant ownership, authorization, auditability, testing, encryption, and recovery are product requirements from the first implementation.
- Favor understandable components on one host with portable interfaces; do not simulate commercial scale prematurely.

## Personas

| Persona | Need | V0 scope | Future extension |
| --- | --- | --- | --- |
| Individual experimental investor | Understand evidence, risk, outcomes, uncertainty | Primary user; simulated portfolio and manual expert review | Separate approval process for any real-money experiment |
| Tenant administrator | Control membership and tenant settings | Explicit role/tenant boundary; initial owner may hold this role | Invitations, export, retention administration |
| Platform administrator | Operate the host and services | Separate operational identity; no standing tenant-data/trade permission | Additional operators and stronger separation of duties |
| Investment/research analyst | Investigate and challenge ideas | Distinct research permissions; cannot bypass risk | Collaborative research |
| Support/security operator | Diagnose with minimal exposure | Redacted health/security access; emergency access design | Customer-authorized, time-limited support |
| Auditor/compliance reviewer | Reconstruct decisions and controls | Read-only synthetic/paper walkthrough | Scoped exports and validated retention |
| Ordinary retail investor | Understandable and informed choices | Research persona only; no public onboarding | Commercialization/legal gates before service |

One person may perform multiple V0 roles, but permissions and resulting limitations must be explicit. Self-review is not independent security review. Tests use at least two tenants, users, accounts, and portfolios; one experimental owner is not a data-model shortcut.

## Scope and lifecycle

| Context | Purpose | Broker submissions |
| --- | --- | --- |
| BACKTEST | Historical replay with information available at decision time | None |
| PAPER | Forward simulation using Alpaca paper service | Paper orders only, after all controls |
| SHADOW | Prospective non-submitting comparison | None |
| LIVE_LIMITED | Possible future constrained real-money evaluation | Unsupported in V0 |
| LIVE | Possible future broader real-money operation | Unsupported in V0 |

BACKTEST and SHADOW are evaluation contexts, not alternative permitted trading modes: PAPER remains the only permitted trading mode under `AGENTS.md`. V0 cannot promote accounts to real-money modes. Versioned lifecycle records do not transform historical results or migrate broker authority. Fresh experiments receive new run identifiers and baselines.

The lifecycle is not an automatic maturity ladder. Treat a context change as creating a separately identified sandbox/run with explicit human selection, compatible data and permissions; do not mutate a historical run's meaning.

| Source context | Requested context | Permitted V0 behavior |
| --- | --- | --- |
| BACKTEST or SHADOW | PAPER | Human creates a new paper run/account binding with fresh baseline/risk approval and verified paper connection; historical results confer no authority. |
| PAPER | SHADOW | Stop the applicable paper dispatch scope, reconcile in-flight orders, then create a non-submitting shadow run from a labeled snapshot; never copy executable jobs or credentials. |
| PAPER or SHADOW | BACKTEST | Create an isolated replay run with predeclared historical cutoffs; no broker path or rewriting of original decisions. |
| BACKTEST | SHADOW | Create a prospective non-submitting run with new decision-time provenance; historical fit is not forward evidence. |
| Any supported context | Same context reset/clone | Create new run ID/baseline, preserve original history and disclose clone/selection in experiment results. |
| Any context | LIVE_LIMITED or LIVE | Reject; no V0 transition route, credential flow, network authorization or deployment capability. |

PAPER and non-submitting evaluation runs may coexist only with separate run state and explicit portfolio/account bindings. V0 permits one active broker-linked portfolio per brokerage account; comparison arms use independent simulator ledgers and cannot commingle fills in that account. Cloning never grants permissions, resets a stop latch or resumes an existing account. Human selection here authorizes only the documented paper/non-submitting action, never real money.

V0 covers authenticated local access; tenant-aware paper portfolios; legally usable free data; quantitative screening; bounded local research; proposal/risk/execution/reconciliation; durable decision records; dashboard/benchmark/cost measurement; emergency stop; backups and restore evidence; manual review packet export and quarantined import. P0 dispatch is human-triggered; scheduled paper automation is P1 after operational acceptance.

Out of V0: live broker onboarding, transfers/withdrawals, margin use, shorting, options, leveraged/inverse ETFs, OTC/penny-stock trading, customer billing, public SaaS launch, native mobile apps, arbitrary strategy code, unrestricted model tools, and autonomous model/risk-policy changes. Phase 2 creates design documents only.

## Operating and economic assumptions

PodFlix is a continuously running bare-metal Ubuntu host with an RTX 2070 Super (8 GB VRAM). CPU/RAM and overnight offload are available in principle; actual free RAM, disk, GPU support, and interference with existing workloads must be measured before model selection. Local compute is not a meaningful incremental experimental expense; capacity and operator effort are still recorded. Containers do not make a shared host highly available or immune to host compromise.

Required recurring external infrastructure/inference cost target: approximately $0. Prefer local PostgreSQL with required TDE, OpenBao, local inference/monitoring, and free paper/data services with entitlement checks. Optional paid adapters are disabled by default with no automatic upgrades. A pre-existing premium chat subscription is not free intelligence: record attributable subscription allocation and human review time separately from marginal API bills.

The two Synology NAS devices may hold encrypted backups/archives. Primary database, execution state, active keys, and current audit writes remain local. NAS outage must not stop ordinary local operation. Local disk exhaustion from archive backlog must trigger a visible safe stop before audit loss.

## Success measures

| Dimension | Acceptance evidence |
| --- | --- |
| Control correctness | All P0 criteria pass; zero unauthorized, cross-tenant, duplicate, or non-paper orders in adversarial/failure suites |
| Explainability | Owner traces a fill to proposal, evidence, model/prompt versions, deterministic decision, authorization, and reconciliation |
| Scientific integrity | A/B/D and optional C share predeclared rules; rejected ideas, missing data, costs, outages, and changes remain observable |
| Usability | Owner completes critical UAT, understands HOLD/rejection, and stops dispatch without reading logs |
| Operations | Synthetic recovery/key restore demonstrated; workload fits measured host capacity |
| Economics | No required paid service; all external usage attributed or explicitly unknown |

Success is not a target return or a promise of outperformance. Evidence of benefit needs uncertainty, sensitivity analysis, meaningful observation across regimes, and replication. Short evaluations establish plumbing and safety only. See [Experiment Design](EXPERIMENT_DESIGN.md).

## Governance and gates

Design Gate 1 provides the proposal, alternatives, draft ADRs, threat/data/risk/model designs, UX, testing/UAT, and backlog. It neither accepts ADRs nor authorizes implementation. Human approval is required before coding. Security-sensitive implementation later requires independent review; Critical/High findings block release.

Subsequent gates first prove simulator contracts, the synthetic control chain, security/storage boundaries and recovery. Only then may a human provision paper-specific credentials through the approved secret channel. Authenticated Alpaca paper contract checks and owner UAT follow before PAPER dispatch readiness. Real-money or outside-customer gates remain separate and unavailable in V0; see [Regulatory Questions](REGULATORY_QUESTIONS.md).

Human decisions include universe/benchmark, capital/risk parameters, exposure/identity/recovery, model/data licensing, evaluation horizon, backup/key custody, and optional frontier disclosure/budget. Recommendations remain DRAFT until approved.
