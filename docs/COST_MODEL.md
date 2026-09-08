# Cost Model

**Purpose:** Keep the experiment near zero recurring infrastructure cost and measure investment outcomes after all externally billed costs.

**Status:** DRAFT — no paid service, subscription, dependency or infrastructure has been purchased or enabled by Phase 2.

## V0 spending boundary

PodFlix already runs continuously. Existing local CPU/RAM/GPU use is treated as no meaningful incremental financial cost for this experiment, while resource utilization is measured for feasibility and interference. This accounting convention is explicit and does not claim electricity, hardware or operator time are universally free. V0 requires no cloud database/KMS, hosted observability, paid data feed or continuous paid LLM API.

| Category | Initial approach | Financial treatment / failure behavior |
| --- | --- | --- |
| Database, keys, queues, identity | Local open-source components subject to ADRs | No required external bill; measure disk/RAM/operations |
| Inference | Local evaluated artifacts, pinned licenses/runtime | Report tokens, latency, GPU/RAM/CPU separately; no paid fallback |
| Research/market data | Legally permitted free sources within entitlements | Track coverage/limits; missing data pauses affected decisions |
| Brokerage | Alpaca PAPER initially | Track actual broker costs where any arise and simulated execution-cost assumptions; paper is not proof of live fees |
| Monitoring/security | Local tools and existing GitHub capabilities | No paid upgrade assumed; record unavailable controls and local alternatives |
| Storage/backups | Local primary storage; existing NAS for encrypted async archives | No required subscription; record capacity and backlog |
| Manual frontier session | Optional existing user subscription; no application API | Separate incremental cash cost from allocated subscription cost |
| Future API/provider | Disabled abstraction only | Human-authorized budget, estimate/reserve/reconcile before use; never required for V0 |

No workload automatically purchases capacity, extends a subscription, upgrades a plan or enables a billed endpoint. Operator approval of a model does not authorize API spending. Resource saturation queues/abstains and reports lost opportunities.

## CostRecord contract

Each record has tenant ownership, currency, amount in fixed precision, incurred/recorded time, provider/category, allocation method/version, evidence reference, actual/estimate/unknown status, project-incremental versus allocated-shared classification, experiment/arm, and optional research-run/model/task/source links. Use idempotent provider charge references where available and append-only corrections; never store billing secrets, account numbers or complete invoices in logs/Git/model inputs.

Record failed/retried research costs and shared acquisition costs, not just successful trades. Allocate a shared cost once by a preregistered method such as research-run usage or time, with weights summing to one. Do not charge the same subscription fully to every candidate/arm. Unallocable costs remain visible at project level; unknown cost is UNKNOWN, not zero. Tenant authorization and export/retention apply to billing records even though V0 has no billing product.

For optional manual subscriptions show two net-return views: incremental project cash paid and a disclosed allocated share of the full subscription. If an existing subscription incurs no extra cash, its allocated economic contribution can still be nonzero. Record date, human-reported provenance and allocation basis; do not scrape private billing accounts. If the owner purchases a subscription primarily for the project, that expense enters project costs even without API calls.

## Net-performance convention

Use the [Experiment Design](EXPERIMENT_DESIGN.md) economic ledger. Show gross return, execution-cost-adjusted return and return after allocated externally billed intelligence/data/services. Expenses paid outside the brokerage reduce analytic net equity at the appropriate time; they do not alter operational broker cash. If a fee already appears in broker/economic cash, do not subtract it again.

Illustration only: with $200 simulated initial equity, a $20 project-attributed bill creates a 10% initial-capital drag before trading gains. This is arithmetic, not a price quotation or forecast. Costs at $100–$300 demand strict measurement of whether optional research earns enough incremental value to justify itself.

Include spread/slippage, transaction/regulatory fees when relevant, subscription/data license costs, failed API calls and recurring external service charges. Identify whether spreads are already embedded in simulated fill prices to avoid double counting. Local compute and human minutes are operational metrics with optional sensitivity valuations, excluded from the initial cash-cost objective as specified by the owner.

## Future budget and billing abstractions

If later approved, introduce per-tenant/project/provider hard spend caps, per-run token/time caps, estimated-charge reservation, actual settlement/reconciliation and alerts before exhaustion. Retries count against the same budget. Unknown price/usage prevents a new paid call unless a bounded human-approved allowance explicitly covers it. No paid fallback on a model or data outage.

Keep usage/cost metering separate from customer price plans. Future subscription, usage and legally appropriate AUM/other charging models may consume this ledger; no final pricing is selected. Performance fees and AUM/advice-related pricing require qualified legal/compliance review, as do data licensing and external service commercial terms. See [Regulatory Questions](REGULATORY_QUESTIONS.md).

## Human decisions and tests

Approve cost-allocation method and unknown-cost treatment before comparing arms. Validate synthetic duplicate charges, currency/rounding, cross-tenant access, shared-allocation totals, subscription periods, corrections, outside-broker bills and net-return reconciliation. Final report must distinguish a free pilot from a pilot relying on an already-paid subscription.
