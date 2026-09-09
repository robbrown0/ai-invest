# Product, UX and Privacy Specialist Review

**Purpose:** Record explicit challenges from three distinct specialist perspectives and their dispositions.

**Status:** DRAFT — role-based design review; not legal advice, gate approval or implementation verification.

## Product Manager / Business Analyst

### Top five concerns

1. At $100–$300, model/data subscriptions can exceed plausible absolute gains. A polished research experience could conceal an economically negative experiment. Require separate gross, cost-adjusted and subscription-attributed reporting, including unknown costs (REQ-P0-17).
2. An entire-universe, many-agent product can exhaust V0 scope before a baseline exists. Start with a predeclared investable subset and A/B/D; make optional C explicit. Record coverage limitations and grow discovery after correctness.
3. Human confidence in articulate research can substitute for measurable benefit. Preserve HOLD/rejections and predeclared outcomes; compare against quantitative and passive controls across regimes, not selected winning trades.
4. Automated paper operation is operationally more demanding than a manual happy path. Separate P0 human-triggered dispatch from P1 unattended schedules; require recovery, stop/reconciliation and independent review before the latter.
5. One operator can become the de facto tenant, platform admin, trader and auditor. Explicit roles and multi-tenant fixtures prevent accidental single-user architecture; a single person does not provide independent human review.

Potentially wrong assumptions: free data covers the desired universe/timing; tiny notional orders satisfy broker precision and liquidity rules; existing host capacity is spare; premium review is available consistently; current simulated capital approximates real execution friction.

Failure modes: profitable cherry-picked arm; research pauses excluded from denominator; rejected ideas disappear; paper broker balance exceeds the experiment cap; resetting a run silently erases losses; optional review costs are zeroed.

Missing requirements identified and added: application capital independent of broker buying power (REQ-P0-03/04); new run on reset; outside-portfolio and rejected-opportunity memory; explicit unknown costs; baseline and legal gates; scope boundary between manual and unattended paper.

Simplifications: no billing engine, public signup, arbitrary strategy code, native mobile or many independent microservices in V0. Use one interface for evidence, proposals and audit with appropriately separated authority behind it.

## UX/UI Designer

### Top five concerns

1. Users may read proposal, allowed and executed as synonyms. Separate action labels and persisted states; an UNKNOWN broker result must stay visible and cannot invite a retry (REQ-P0-08 through 11).
2. A kill button can imply canceled fills or immediate liquidation. Label Stop paper dispatch; report request/acknowledgement and residual fills; never imply selling holdings (REQ-P0-14).
3. Security friction during an emergency stop may cause harm. Keep authenticated authorized stop immediate; reserve fresh authentication and deliberate review for resuming or weakening controls.
4. Expert-packet export hides a privacy boundary and can contaminate independent review. Preview exact minimized content, confirm disclosure and seal Stage A before revealing local conclusions (REQ-P0-15/16).
5. Dense financial tables and color-only badges fail on phones and assistive technology. Target WCAG 2.2 AA, mobile reflow, keyboard/screen-reader walkthroughs, text state and tabular alternatives (NFR-02).

Potentially wrong assumptions: users understand risk-adjusted metrics, single-venue feed coverage, uncalibrated confidence and cancellation races; device/network is reliable during stop; redacted holdings feel nonsensitive; operator can interpret raw logs.

Failure modes: double click after timeout; green badge on stale data; account switch leaves another tenant's dialog open; screen reader misses changed stop status; expert import looks like order confirmation; wide table hides account/mode.

Missing requirements identified and added: no stop-success claim without acknowledgement; clear freshness/UNKNOWN labels; unit/currency/timezone context; immutable historical evidence view; safe external-link rendering; manual tasks usable without reading logs.

Simplifications: responsive web only; plain-language reason tables before complex charts; no celebratory trade interactions; keep future live lifecycle in roadmap text rather than disabled controls that resemble an unlockable feature.

## Privacy / Compliance Risk Analyst

### Top five concerns

1. Private paper experimentation does not settle future adviser, compensation or privacy classification. Create qualified-review gates; never claim compliance based on technical controls or disclaimers (LEG-01 through 07).
2. A paper setting does not prove an OAuth token lacks live authority. Alpaca documents combined grants. Recommend paper-specific V0 credentials and defer generic OAuth (LEG-04).
3. Free market data may be incomplete and may lack intended export/commercial/AI rights. Track feed provenance and license entitlements; no automatic subscription or redistribution (LEG-08/11).
4. Manual premium-model export is disclosure even without an API call; holdings can reveal financial interests after identifiers are removed. Minimize, preview, permission and record exports; never expose secrets.
5. Retention, deletion, immutable audits and encrypted backup recovery can conflict. Define classification and policy/hold/export workflows now; obtain legal periods later rather than guessing (LEG-09/10).

Potentially wrong assumptions: all future users are US-based; internal research is never later marketing; a chat subscription permits every data use; all broker tokens are least-privilege; encryption makes data anonymous; account deletion covers backups.

Failure modes: live-capable grant enters paper service; customer data in an expert packet; licensed feed copied to a model; unsupported performance claim published; blanket deletion removes required evidence or leaves undocumented copies.

Missing requirements identified and added: exact disclosure manifest; self-reported external provenance explicitly weaker than verified provenance; applicability/jurisdiction questions; separate pricing alternatives and performance-fee gate; no selected regulatory retention period.

Simplifications: no public customers/billing in V0; minimal identity fields; paper-only key provisioning rather than generic OAuth; plain rights metadata before a complex licensing engine. These are scope reductions, not conclusions that obligations never apply.

## Disagreements and dispositions

| Disagreement | Challenge | Draft resolution or human decision |
| --- | --- | --- |
| Broad opportunity scout vs implementable experiment | Product ambition says entire market; free feeds and local capacity may not support it reliably. | Predeclare a smaller lawful universe for P0 and disclose coverage. P1 expands event/overnight discovery. Human chooses universe and representative benchmark. |
| Automatic research-to-trade vs experimental clarity | Automation accelerates learning but hides approval, state and outage defects. | P0 is human-triggered paper dispatch through all controls; P1 automation only after operational acceptance. Human intervention is recorded in experimental analysis. |
| Fresh auth for every privileged action vs fast stop | Generic security policy could delay an emergency protective action. | Authorized stop uses existing valid session and durable scope checks; fresh auth is required to resume or relax controls. No unauthenticated global stop endpoint. |
| Comprehensive expert packet vs minimization | More context improves research but can disclose positions, private theses and licensed data. | Default approved aliases/weights and permitted evidence; exact preview/consent. Human decides allowable private disclosure and provider policy; never secrets. |
| Independent review vs convenience | One packet containing local conclusions anchors frontier output. | Seal Stage A independent response before Stage B reveals local conclusions; mark unavoidable exposure unblinded and analyze separately. |
| Immediate broker OAuth UX vs no live authority | Convenient OAuth can grant both paper and live access. | Paper-specific OpenBao provisioning only in V0. Future OAuth must verify environment/grant and undergo a new security review. |
| Audit permanence vs deletion | Financial reconstruction conflicts with broad account deletion promises. | Classify, minimize, use policy/holds and documented backup handling; counsel determines legal periods before customer promises. |
| Zero cost vs full evaluation honesty | Existing premium chat seems free, but intelligence cost affects economic conclusions. | Show incremental cash expense plus attributed subscription cost and human time; no mandatory paid service. Human chooses allocation convention. |

## Integration handoff

No specialist accepts the design unconditionally. Human decisions remain: capital/risk thresholds, universe/benchmark, horizon and economic allocation, identity/recovery/exposure, backup/key custody, optional external disclosure and future commercialization facts. The lead integration pass must check every UI promise against actual service state machines, risk/audit boundaries and testing evidence.

Final independent review should specifically challenge stale approvals after UI edits, multi-tenant browser/jobs/exports, stop acknowledgement races, mixed broker OAuth grants, blinding contamination, and affordability/coverage assumptions. This review does not replace the separately recorded final cross-functional review in `docs/PHASE2_REVIEW.md`.
