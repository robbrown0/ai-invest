# Independent Financial and Scientific Integration Review

**Purpose:** Challenge other specialists' integrated architecture, security, data, requirements, test/UAT and ten draft ADRs before the draft PR.

**Status:** DRAFT — design inspection only; no runtime tests or human gate approval are implied.

## Review scope and independence

The financial/research reviewer inspected the application/security/data specialists' documents, test/UAT plan and ADRs after writing the research/risk designs. This supplies an independent perspective on those artifacts, but is not an independent human security audit and does not independently validate the reviewer's own scientific protocol. Findings below are conditions observed at review; the Lead Architect records final dispositions in [Phase 2 Review](../PHASE2_REVIEW.md).

## Findings and required disposition

| ID / severity | Evidence at review | Why it matters / requested resolution |
| --- | --- | --- |
| FIN-01 — HIGH design ambiguity | [Architecture](../ARCHITECTURE.md), dispatch paragraph: finite account lease/fencing stated to prevent duplicate broker dispatch after crash | A broker does not enforce the database fence. A paused old worker can resume after lease expiry. Require persistent dispatch-admitted/unknown state that is never resent merely because ownership changes, and a fault test pausing the first sender while another claims the job. Local fencing governs local state, not external exactly-once effects. |
| FIN-02 — MEDIUM control inconsistency | [Security Architecture](../SECURITY_ARCHITECTURE.md), financial stops; [Data Architecture](../DATA_ARCHITECTURE.md), StopState; architecture kill paragraph; UAT-10 | These listed global/tenant/account but omitted required portfolio scope; UAT only mentioned global/account. Standardize all four hard-stop scopes and test portfolio/tenant stop isolation plus precedence. A strategy mandate is additional P1 policy, not a competing V0 stop taxonomy. |
| FIN-03 — MEDIUM ownership ambiguity | [Data Architecture](../DATA_ARCHITECTURE.md), relationship explanation says V0 may restrict one active PAPER portfolio per account | [REQ-P0-03](../REQUIREMENTS.md) requires that restriction. Make it mandatory with a schema/concurrency proof; future multi-portfolio allocation remains conceptual. Otherwise experiments can double-count cash or attribute aggregate fills incorrectly. |
| FIN-04 — MEDIUM privacy inconsistency | [ADR-0006](../ADR/ADR-0006-ai-execution-isolation.md), export excludes unconsented PII | Data classification prohibits all PII in model/export context. Remove wording implying consent permits direct PII export. Consent applies only to the approved minimized non-PII projection. |
| FIN-05 — MEDIUM implementation-qualification risk | [Risk Model](../RISK_MODEL.md), 10-second quote / 15-second account / 5-second approval candidates and fractional limit gate | Sparse free quotes, user delay and strict spread checks may yield near-universal rejection. The final approval must be generated after human intent; pre-click results are previews. Measure allowed/rejected opportunity rates, source coverage and latency before enabling PAPER; keep simulator/HOLD if safe controls cannot be supported. No automatic market-order or paid-data fallback. |
| FIN-06 — LOW clarity gap | [Test Strategy](../TEST_STRATEGY.md), broad financial fixtures; [Experiment Design](../EXPERIMENT_DESIGN.md) common simulator versus PAPER | Add explicit fixture with $200 virtual cap against larger broker balance and separate broker/economic ledgers including a dividend and outside-broker subscription bill. Ensure P0 UAT distinguishes execution-fidelity results from A/B/C/D strategy results. |

FIN-01 is an unsafe implementation interpretation to resolve before design handoff, not an observed production vulnerability: no order sender exists. FIN-05 is a qualification/human-decision gate, not a reason to weaken safety to make the UI busy.

## Verified integration dispositions

The reviewer re-read the integrated documents after corrections. Resolved here means the design inconsistency is corrected; no future runtime acceptance evidence is waived or claimed complete.

| Finding | Disposition after verification | Remaining implementation evidence |
| --- | --- | --- |
| FIN-01 | RESOLVED IN DESIGN: Architecture now limits fencing to local ownership/admission, allows at most one outbound attempt per admitted intent, requires unknown-state reconciliation, and forbids clearing ambiguity from not-found alone. ADV-07 and V0-06 explicitly test the paused original worker, expired lease and takeover. | Simulator fault evidence proving no replay; quiescence and broker-outcome checks before later intent. |
| FIN-02 | RESOLVED IN DESIGN: Security Architecture, Data Architecture, Architecture, ADV-19 and UAT-10 consistently include global/platform, tenant, account and portfolio hard stops. Strategy scheduling permission remains distinct P1 policy. | Scope-isolation, precedence, concurrent admission and restart tests. |
| FIN-03 | RESOLVED IN DESIGN: Data Architecture now makes at most one active PAPER portfolio/account a constraint-enforced V0 invariant while retaining multiple historical/multi-account records. | Schema and concurrency test; independent virtual-capital reservations. |
| FIN-04 | RESOLVED IN DESIGN: ADR-0006 now excludes all PII and explicitly states consent does not waive the exclusion. | Context/export allowlist and canary tests across model and manual workflows. |
| FIN-05 | PARTLY RESOLVED; QUALIFICATION GATE RETAINED: final risk is after human intent and pre-click previews are non-authoritative. Free-feed freshness/coverage and fractional DAY limits remain unverified and deliberately block PAPER enablement if unsupported. | Measure end-to-end latency, rejection/eligibility rates, fractional minimums/precision and source coverage; owner approves usable thresholds without silent weakening. |
| FIN-06 | RESOLVED IN DESIGN: Test Strategy now includes a combined tiny-capital oracle with $100,000 broker buying power against $200 virtual equity, rejection of a $50 order under the proposed $25 cap, and $2 analytic dividend less $20 outside-broker bill producing $182 net equity and -9% return. V0-04/V0-11 own it; no broker cash/fills are fabricated. | Implement the independent oracle, concurrency/reservations and gross/net/no-double-subtraction checks; link observed results to cost/benchmark UAT. |

No unresolved HIGH design inconsistency remains from this review after the verified corrections. Post-design qualification gates remain required before credentials, paper orders or unattended operation, according to their gate sequence.

## Fourteen-question cross-functional challenge

| Question | Assessment and evidence needed |
| --- | --- |
| 1. Unauthorized real-money trade possible? | No Phase 2 runtime exists. Proposed V0 excludes live adapters, grants/routes and mode transitions at multiple boundaries. Later implementation must prove mixed/live grants, redirects and forged modes cannot create authority; host compromise remains outside process guarantees. |
| 2. Cross-tenant access possible? | Application checks, composite references and FORCE RLS are proposed. Shared-login tenant settings alone are explicitly rejected; independently verified context or tenant role pools remain a blocking qualification choice. Test direct SQL, pool reuse, jobs, exports and support privileges. |
| 3. Compromised Internet research trades directly? | Network/identity/tool isolation denies direct access and outputs remain proposals. Plausible poisoned evidence can still influence an allowed trade, so grounding/adversarial/outcome checks remain necessary. |
| 4. LLM gets broker credentials? | Only execution retrieves them; shared order-capable credentials never migrate to read services. Projections, mounts/egress and canary tests must prove this at runtime. Manual packets/imports need the same boundary. |
| 5. Ambiguous/duplicate request creates duplicate trade? | Durable intents, stable client IDs, reservation retention and no blind resend are correct direction. Resolve FIN-01; lease fencing alone cannot control an external broker. Test crash, pause/resume, lost acknowledgment and duplicate events. |
| 6. Every financial action reconstructed? | Atomic intent/audit, source/model/policy versions, broker observations and append-only corrections support it. Lost licensed source snapshots or archive gaps create honest limitations; block consequential reliance without adequate permitted evidence. |
| 7. Unnecessary recurring spend? | No mandatory paid provider. PostgreSQL queue and one local inference queue remove extra services. Manual subscription costs are allocated transparently, including failed research and bills paid outside brokerage. |
| 8. Fits PodFlix? | Plausible architecture, unverified capacity. Identity/TDE/OpenBao and one GPU model still need disk/RAM/VRAM/IO benchmarks under existing workloads. Manual unseal creates operator-dependent availability. |
| 9. Commercial multi-tenancy without core rewrite? | Ownership, composite constraints, scoped jobs/caches/costs and provider boundaries avoid singleton redesign. Commercial operations/legal review/host isolation still require new work; portability is not proof of readiness. |
| 10. Measures AI value rather than assuming it? | A/B/C/D, fixed information cutoffs, net expenses, rejected ideas and uncertainty address this. Prospective samples and preregistration remain essential; current-model historic backtests cannot prove unbiased edge. |
| 11. Quantitative tasks separated from LLM tasks? | Deterministic math/eligibility/risk and statistical regime/features; LLMs synthesize cited evidence. Logical specialist ablation tests must justify extra tasks instead of rewarding narrative complexity. |
| 12. Human understands proposal and rejection? | Immutable evidence, bull/bear, assumptions and deterministic reason/value displays provide a path. Final risk must be computed after intent, and pre-click preview must not imply guaranteed future execution. |
| 13. Outage handling designed? | Host/DB/OpenBao/broker/data/model/network/NAS failures have explicit stop/unknown/reconcile behavior. Restore replay, local disk exhaustion, key loss and clock errors require fault evidence, not merely a runbook. |
| 14. Removable complexity? | Retain modular core, separate authority boundaries, one inference queue, one active order and one portfolio binding per account. Defer vector DB, event broker, many autonomous services, multiple live brokers and automated paid API fallback. |

## Threshold and scientific usability review

At $200 capital, a $25 maximum order and 40% daily absolute turnover cap allow limited gradual portfolio formation. A 60% broad-ETF cap does not imply it can be reached in one order/day. Minimum notional, fractional precision and residual sell quantity need tested behavior. Unknown sector/quote data blocks new exposure; the owner must understand sparse free data may leave the strategy mostly in cash. This is an observable experiment outcome, not permission to relax controls.

Daily loss/drawdown use virtual economic equity and include declared expenses; an externally billed research subscription can therefore dominate the small portfolio's economics. Report raw broker cash separately. Passive control mandate differences, frontier review latency/new information, historical LLM knowledge and selection bias must remain visible. No duration alone passes an economic success gate.

## Recommendation

The verified authority/ownership corrections support handing this DRAFT design to the owner. Keep provider/tenant-context/TDE/host-fit/risk-threshold tests and the combined accounting fixture as explicit implementation obligations. Design Gate 1 can approve planning direction only; it does not certify safe software, authorize credentials, or permit real-money operation.
