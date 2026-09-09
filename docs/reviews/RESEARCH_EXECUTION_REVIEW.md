# Research and Financial Systems Specialist Review

**Purpose:** Record independent disciplinary challenges, assumptions and simplifications for Design Gate 1.

**Status:** DRAFT — virtual specialist analysis, not human sign-off or implementation verification.

## Quantitative Research / Data Science Lead

### Top five concerns

1. A $100–$300 portfolio and a short paper run cannot establish an edge; correlated forecasts reduce effective sample size further.
2. Current LLMs may know historical outcomes, so frozen retrieved data alone cannot remove backtest look-ahead.
3. Frontier imports arrive later and discover extra information, confounding pure intelligence comparisons.
4. Rejected-idea analysis and risk-engine ablations suffer selection/opportunity-cost bias.
5. Paper fills, missing dividends and subscription allocation can make gross winners into net losers or incomparable arms.

### Assumptions that may be wrong

Free data may lack point-in-time constituents, delistings, adequate corporate actions or redistribution rights. Models may add no incremental value. Enough market regimes may not appear during the owner's evaluation horizon. Normalized portfolio exports may change the expert's usefulness.

### Failure modes

Repeated holdout tuning, dropping delisted/missing ideas, backdating frontier output, matching separate strategies to aggregate broker fills, overcounting independent observations, and hindsight-defined regimes all produce false evidence.

### Missing requirements identified

Require preregistration, separate economic/operational ledgers, immutable recommendation horizons, delayed-import availability rules, explicit UNKNOWN data/cost fields and an exploration/ablation protocol. These are now included in Experiment Design and Cost Model. Numerical power/effect-size targets remain an owner decision after baseline data exists.

### Simplifications worth considering

One deterministic simulator and a limited liquid universe before full-market historical reconstruction; one primary endpoint; simple interpretable baseline; fixed-horizon outputs before complex online learning. Broader discovery can start as WATCH without relaxing tradability.

### Disagreement and resolution

The AI perspective favors deeper/scouting research to improve quality; the quant perspective demands equal cutoffs and randomized/paired attribution. Resolution: distinguish equal-information reasoning experiments from end-to-end discovery value, log all new sources/delay, and preregister separate analyses. Do not claim one measures the other.

## AI/ML Architect

### Top five concerns

1. A dozen autonomous agents would consume 8 GB VRAM/host capacity and amplify correlated hallucinations.
2. Opportunity memory can persist poisoned claims and spread them into future runs.
3. Manual frontier export can reveal private portfolio patterns even after removing account IDs.
4. Helpful tool access can turn a document's instructions into credential or broker access.
5. Mutable model tags/prompts and uncalibrated confidence can silently change investment behavior.

### Assumptions that may be wrong

A 7–8B quantized model may not meet evidence quality or shared-host memory constraints. Larger offloaded models may miss research deadlines. A two-stage manual workflow may be too burdensome, and provider-reported model versions may be unverifiable.

### Failure modes

OOM/starvation, cross-tenant retrieval leakage, fake citations, instruction-laden memory, secret-like text entering prompts, active HTML in imports, forged packet ownership, and automatic paid/cloud fallback.

### Missing requirements identified

Add strict projections, no inference tools/egress, nonce bound by local tenant authorization, closed import schemas, blinding/provenance strength, visible export consent, model-release registry and fail-closed unavailable/HOLD. No adversarial prompt alone is accepted as a boundary.

### Simplifications worth considering

Four initial logical tasks on one serialized serving queue; deterministic financial math; no vector database until retrieval quality requires it; no local fine-tuning/online self-modification; optional unblinded import labeled outside blinded experiments.

### Disagreement and resolution

Product wants rich self-contained expert packets; privacy/AI safety limits exported detail. Resolution: public facts plus explicitly consented rounded weights and simulated-capital range, no identifiers/exact balances/raw logs. The exact allowed normalized exposure fields remain a human decision. Richer export is not assumed authorized by accepting a packet.

## Brokerage / Financial Systems Engineer

### Top five concerns

1. Timeouts and reboots can leave accepted orders invisible locally; retry can duplicate exposure.
2. Approval expires or state changes between risk check and dispatch, enabling overspend or policy bypass.
3. A nominally paper configuration can accidentally accept a live-capable credential or arbitrary endpoint.
4. A kill switch cannot undo accepted orders or promise no fills after activation.
5. Fractional order, free quote and settlement assumptions may not support strict small-capital controls.

### Assumptions that may be wrong

Documentation may overstate fractional limit support for the actual account/API; free quote coverage may be too sparse; broker lookup may lag; paper may expose margin-like buying power despite a no-margin strategy; an order may fill during cancellation.

### Failure modes

Blind retries/new IDs, expired lease causing a second sender, partial fills released as cash too early, stale state authorizing two portfolios, calendar/DST errors, corporate-action quantity changes, and treating stream events as exactly-once complete truth.

### Missing requirements identified

Add account-level serialization/reservations, stable intent/client IDs, immutable payload-bound approvals, final dispatch admission, unknown-state quarantine, periodic reconciliation, paper-only adapter/egress/provenance, conservative cash ledger and provider compatibility gates. No secret is copied to a data reader when a broker key also grants order authority.

### Simplifications worth considering

One active order per broker account, one active portfolio binding per account, regular-session DAY limit quantity orders, no modify/bracket/extended-hours paths, explicit human P0 dispatch. Full broker abstraction is an interface/capability contract, not multiple implementations.

### Disagreement and resolution

Availability-oriented retries conflict with duplicate-trade safety. Resolution: bounded retries for reads only after an ambiguous submit; preserve reservation and pause new account orders until reality is established, escalating unresolved cases to the owner/provider. This accepts missed opportunities to avoid invented certainty.

The convenience of fractional market orders conflicts with bounded execution price. Resolution: require a fractional DAY limit contract test; if unsupported, keep the account unenabled/use simulation and request a separately reviewed policy decision. Do not silently fall back to market orders.

## Integration decisions and human gates

Adopt logical specialists, minimized model/export projections, immutable evidence and paired cost-aware research; separate risk/execution identities; accept explicit uncertainty around in-flight orders and paper fidelity. P0 remains human-triggered, P1 scheduling follows P0 and recovery/patch gates. Human decisions remain policy thresholds, benchmark/protocol/power target, model/license after host benchmarks, allowed export fields, paper/free-data capability proof, cost allocation and a real independent reviewer. All are design recommendations; no runtime safety claim is certified by these documents.
