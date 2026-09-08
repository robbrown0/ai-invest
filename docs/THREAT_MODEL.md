# Threat Model

**Purpose:** Identify assets, actors, trust boundaries, abuse cases, threats, mitigations, and residual risk.

**Status:** DRAFT — V0 design review, not a completed penetration test or residual-risk acceptance.

## Method, scope and threat actors

Use STRIDE: spoofing (S), tampering (T), repudiation (R), information disclosure (I), denial of service (D), and elevation of privilege (E). Review each flow and trust boundary in [security architecture](SECURITY_ARCHITECTURE.md), then add financial consistency and experimental-validity hazards that do not fit neatly into STRIDE. [Microsoft STRIDE reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)

Scope is private-access V0 on shared PodFlix: human/browser, identity provider, modular control application, ingestion/evidence, local inference, deterministic risk, execution, PostgreSQL, OpenBao, broker PAPER, optional NAS and operator/repository supply chain. No real funds, live authority, service deployment or exploit execution occurs during this phase.

Actors include an unauthenticated Internet attacker; malicious/compromised tenant; stolen-session holder; malicious document/data publisher; manipulated or faulty model; compromised research/frontend/execution container; malicious dependency/model artifact; careless or compromised administrator; and failing host/network/provider. Natural outages are modeled alongside hostile actions because both can cause ambiguous financial state.

Assets are tenant confidentiality, secret/key material, paper execution authority and future live authority boundary, accurate cash/position ledgers, immutable proposal/risk/order provenance, scientific evidence, operational availability and recoverable encrypted backups.

## Assumptions to falsify

1. PodFlix host root and Docker administration remain trusted. Containers cannot enforce separation against root; shared unrelated workloads expand attack surface.
2. A dedicated PAPER credential can be verified without live endpoint access, and PAPER endpoints cannot be redirected to live destinations.
3. The chosen database role/context design can prove tenant authority independently of arbitrary application tenant settings.
4. TDE, encrypted local volumes, key custody and compatible backups can be operated and restored within the proposed targets.
5. Broker identities and reconciliation APIs support robust deduplication. Client-order IDs alone do not prove exactly-once effects.
6. Sufficient legally retainable evidence and affordable point-in-time data exist to support reconstructable research and fair experiments.
7. Strong authentication and independent review are feasible for a single experimental owner without pretending there are two people.

Qualification must disprove unsafe assumptions before paper automation. Lack of evidence is an open gate, not implicit acceptance.

## Prioritization

The severity column is inherent design impact if the control fails, not a claim that a vulnerability exists in the documentation. Critical means unauthorized real-money capability or broad privileged compromise; High means tenant/secret exposure, financial duplication or destruction of consequential evidence; Medium means bounded interruption/research distortion. Likelihood is qualitative and changes after testing. All applicable Critical/High implementation findings block release; planned controls are not evidence of mitigation. Each threat ID must map to an acceptance test and owner in the backlog.

## Abuse and failure catalogue

| ID / STRIDE | Scenario and inherent impact | Required control | Falsification/acceptance evidence | Owner / residual |
| --- | --- | --- | --- | --- |
| TM-01 S/I/E | Cross-tenant reads or IDOR expose another tenant's positions/research. High; plausible. | Object authorization, authenticated tenant context, RLS, tenant-scoped caches/exports. | Tenant A requests every B endpoint/object/job/export/subscription; zero B content or existence leak. | Data + security; compromised global issuer remains risk. |
| TM-02 T/E | Cross-tenant writes/references attach a B account to A proposal. High; plausible. | Compound ownership foreign keys, write policies, authenticated account binding. | Attempts through APIs, direct runtime DB role, bulk/import/queue paths all fail atomically. | Data; privileged DBA still trusted. |
| TM-03 T/I/E | SQL injection or unsafe privileged function bypasses RLS. High; plausible. | Parameterized SQL, narrow grants, fixed search paths for reviewed privileged functions, verified context. | Injection/fuzz tests plus attempts to SET arbitrary tenant and invoke privileged functions cannot gain scope. | Application/data; shared-role context design unresolved until qualification. |
| TM-04 T/E | Compromised news source manipulates research. High for future money; plausible. | Quarantine/provenance, no authority in inference, independent evidence checks, deterministic limits. | Malicious article may be summarized but cannot access broker/secrets or change policy; unsupported claims flagged. | AI/security; false but plausible thesis can survive. |
| TM-05 T/E | Malicious SEC document embeds instructions or attacks parser. High; plausible. | Sandboxed parsers, resource caps, labeled content, no model tools/secret mounts. | Hostile PDF/HTML corpus tests parser containment and zero policy/order side effects. | Ingestion; parser/kernel vulnerabilities remain. |
| TM-06 T/I/E | Prompt injection requests secrets or hidden tool actions. High; plausible. | Projection allowlist, no secrets in context, network/capability boundaries, strict output schema. | Synthetic canaries outside projection are absent from prompts/outputs; broker/OpenBao routes denied from model. | AI/security; model-output quality not guaranteed. |
| TM-07 T/E | AI proposes oversized trade, prohibited asset, margin/short/options or leverage. High; plausible. | Deterministic asset/account/notional/exposure checks, immutable hard policy. | Boundary/property tests reject each prohibited class and malformed numeric input regardless of confidence. | Risk; data-label corruption requires independent checks. |
| TM-08 E | AI attempts direct broker access or risk-permit forgery. Critical; plausible if coupled. | No route/credentials; risk-only permit authority; execution validates caller/scope. | Network probe from research fails; fabricated/altered permit rejected before broker calls. | Security/execution; compromised execution has direct PAPER authority. |
| TM-09 S/T/E | Import/config/OAuth accidentally grants LIVE or LIVE_LIMITED. Critical; plausible. | No live adapters/endpoints/config knobs; PAPER-only egress/credential attestation; no generic broker OAuth. | Enumerate config/modes/redirects/imports; all live selections rejected; no live request emitted. | Architecture/execution; host owner could install different software outside V0. |
| TM-10 S/T | Replay prior trade request/permit. High; plausible. | Expiry, content binding, account/tenant/mode, stop epoch, one-use durable identity. | Replay after success/expiry/policy change/stop/restart yields zero additional submissions. | Risk/execution; uniqueness must persist across restore. |
| TM-11 T | Timeout followed by retry creates duplicate execution. High; likely without design. | Durable intent, stable client identity, UNKNOWN state, query/reconcile before retry. | Broker accepts then drops response; retries/restart produce one logical order and all observed fills. | Execution; broker contract cannot be assumed perfect. |
| TM-12 S/E | Stolen session performs risk increase/export or privilege change. High; plausible. | Revocation, fresh authentication, scoped authorization, CSRF/session controls, limits. | Revoked/stale sessions fail privileged operations and queued tasks; valid ordinary session cannot bypass step-up. | Identity/application; active endpoint compromise remains. |
| TM-13 I/E | Stolen broker token submits outside risk service. Critical future/High PAPER; plausible. | Execution-only retrieval, no logs/model exposure, least provider scope, rotation and broker revocation runbook. | Simulated token compromise drills stop/revoke/reconcile without printing a credential. | Security/execution; application risk cannot constrain stolen external token. |
| TM-14 E/I | Compromised research container pivots into secrets or database. High; plausible. | Network allowlists, no sensitive mounts/socket, restricted identity and sanitized work payload. | Runtime compromise simulation cannot reach internal APIs/volumes or mint trusted work context. | SRE/security; same-host kernel escape residual. |
| TM-15 S/T/I | Compromised frontend steals sessions or misrepresents recommendation as execution. High; plausible. | CSP/output encoding, HttpOnly sessions, server authorization, explicit order-state UI, step-up. | Stored/reflected XSS and tampered client tests cannot authorize direct broker calls; authoritative server state remains visible. | UX/application; active client compromise can deceive user. |
| TM-16 E/I/R | Compromised admin account reads tenants, changes limits or deletes audit. Critical; plausible. | Privilege separation, fresh auth, restricted support, append-only grants, independent review/checkpoints. | Tenant admin cannot grant platform role; platform support needs scoped access; audit tamper detected externally. | Security; root/control-plane compromise cannot be eliminated locally. |
| TM-17 D | OpenBao unavailable/sealed or credentials expire. High operational impact; expected. | Fail closed on new orders; no plaintext fallback; independent storage/manual unseal runbook. | Seal/unavailability/renewal loss pauses submission, preserves intents and recovers under authorized procedure. | SRE; cached keys may remain in memory. |
| TM-18 D/T | PostgreSQL down, full disk or audit write failure. High; expected. | No durable state means no send; bounded buffers; stop and reconcile on recovery. | Inject failure before/after every transaction boundary; no unaudited new submission or lost acknowledged intent. | Data/execution; accepted broker orders may still fill. |
| TM-19 D | NAS unavailable or archive credentials lost. Medium; expected. | Local execution/active data, asynchronous archive, backlog/capacity alerts. | Disconnect both NAS endpoints; normal local operation continues, archive lag becomes visible. | SRE; off-host recovery point degrades. |
| TM-20 D/T | Host reboot/crash during an order. High; expected. | Durable intent/stop epoch, startup stopped, unseal/reconcile before resume. | Crash each state transition; recover broker identity/status and do not resubmit ambiguity. | Execution/SRE; hardware loss may exceed local RPO. |
| TM-21 T/E/I | Malicious expert-review import injects scripts, tenant IDs, live requests or forged confidence. High; plausible. | Bounded versioned schema, packet/tenant binding, sanitized rendering, no executable fields, risk chain. | Wrong packet/tenant/version, oversized payload, HTML/scripts and unauthorized modes rejected; accepted advice remains proposal only. | AI/application; human-pasted research still untrusted. |
| TM-22 I/E | SSRF through source URL, redirect, IPv6/private address or DNS rebinding. High; plausible. | Restricted fetch egress, address verification per redirect/connect, no privileged network route. | Redirect/rebinding/encoded-address corpus cannot contact metadata/OpenBao/DB/loopback/internal services. | Ingestion/security; egress control needs real runtime test. |
| TM-23 T/D | Stale/manipulated market data or incorrect corporate action causes wrong size/value. High; plausible. | Source quality, timestamps, price sanity, security identity/history, independent cross-checks. | Delayed feed/split/halt/outlier fixtures block execution or correctly adjust valuation without hindsight. | Data/risk; correlated provider errors remain. |
| TM-24 D/T | Broker/network outage, partial fill, cancellation race or closed market. High; expected. | Bounded retries only after known safe failure, status state machine, reconciliation, market calendar. | Simulate partial/canceled/rejected/stale orders and out-of-order fills; ledger converges without assuming send equals fill. | Execution; broker outages cannot be prevented. |
| TM-25 T | Concurrent proposals overspend shared account cash/exposure. High; plausible. | Serializable/locked reservation invariant at account scope, one-use permits and state versions. | Race proposals across strategies/portfolios/tenants; reservations plus positions never exceed available authorized exposure. | Risk/data; external manual orders require reconciliation. |
| TM-26 T/D | Kill switch races with submit/cancel or stale permit. High; plausible. | Durable stop epoch checked at dispatch; serialized account coordination; explicit in-flight semantics. | Deterministic race tests show zero submissions authorized after stop linearization; accepted/in-flight fills remain audited. | Execution/UX; stop cannot undo broker acceptance. |
| TM-27 I/D | Encrypted backup unrecoverable or ciphertext stored with all unseal material. High; plausible. | Separated keys/shares, version manifest, independent backup encryption, restore drills. | Lost-host recovery with offline custody; wrong/missing historical key fails clearly without plaintext fallback. | SRE/security; permanent key loss can be permanent data loss. |
| TM-28 R/T | Audit modified/truncated or research source disappears. High; plausible. | Append-only events, atomic outbox, signed external checkpoints, retained permitted evidence. | Alter/delete/reorder/tail-truncate events and remove source artifacts; verification detects gap or marks decision unverifiable. | Data/security; same-host-only chain can be rewritten. |
| TM-29 E/I | Dependency/container/model artifact compromises host or loads remote code. Critical; plausible. | Verified/pinned artifacts, minimal privileges, scanning/review, safe serialization, no remote model code. | Tampered digest/unsafe artifact rejected; vulnerable reachable Critical/High blocks release. | SRE/AI; signatures do not prove safe behavior. |
| TM-30 D | Malicious tenant causes GPU/queue/disk exhaustion or paid-model cost spike. High availability/cost; plausible. | Tenant budgets/quotas, bounded queues, job deadlines, paid providers disabled V0. | Flood/fan-out/huge-context tests preserve control/execution resources and do not call a paid API. | SRE/AI; fair scheduling on 8 GB requires measurement. |
| TM-31 T/R | Look-ahead leakage, hindsight edits or cherry-picked outcomes invent investment edge. High scientific impact; plausible. | Immutable cutoffs/universes/forecasts, preregistration, all recommendations/outcomes/costs. | Future-dated/corrected inputs excluded; rejected/HOLD/missing-cost cases preserved and disclosed. | Quant/data; small samples remain inconclusive. |
| TM-32 I/T | Tenant export/deletion leaks data or restore resurrects revoked/deleted tenant. High; plausible. | Scoped export, encrypted delivery, tombstones, hold register and post-restore revocation replay. | Two-tenant export contains only owner data; restored deleted tenant remains disabled with eligible content removed. | Privacy/data; legal holds/backup expiry need review. |
| TM-33 S/T | Service identity/permit stolen or signed context replayed to another component. High; plausible. | Distinct audience/tenant/account/operation, expiry, nonce/one-use identity, narrow key custody. | Cross-audience/tenant/account replay and expired identity fail at recipient; rotate without privilege expansion. | Security; issuer compromise remains trusted-boundary failure. |

## Attack-chain challenge

A malicious source can influence a model and therefore a plausible proposal. The intended break is architectural: neither source nor model has credentials, authenticated tenant capability, policy mutation rights or execution connectivity. Valid-looking malicious advice may still satisfy hard limits, so risk controls bound financial exposure rather than establish investment merit. Track that effect through adversarial research evaluations, bear cases and recommendation outcomes.

A stolen execution credential is a separate attack chain: broker orders outside the application can bypass its risk engine entirely. Credential custody, isolated PAPER-only capability and broker-side revocation are essential; no document should imply application risk protects a stolen external token. For future live design, reassess broker-side restrictions, independent account controls and execution-host isolation before requesting live authorization.

OWASP describes both indirect prompt injection and limitations of model-based guardrails; our design keeps authority outside models. [Prompt-injection guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) URL allowlists also require address/redirect handling, rather than string matching alone. [SSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

## Top ten unresolved risk themes

1. Shared PodFlix root and unrelated workloads remain a common compromise domain.
2. Tenant RLS can be ineffective against a compromised shared role unless authority is independently bound.
3. TDE residual plaintext, version-sensitive WAL tooling and lost-key recovery may invalidate backup assumptions.
4. Broker timeout/retry and stop races can create duplicates or unexpected in-flight fills.
5. Broker credentials stolen from execution bypass application risk controls outside the platform.
6. Prompt injection can corrupt research even when direct authority is removed.
7. Free data coverage, licensing, corrections and missing point-in-time history may invalidate conclusions.
8. A local audit chain and mutable source URLs cannot prove reconstruction against administrator tampering.
9. Limited capital, costs, small samples and multiple testing can create misleading AI-value claims.
10. Single-owner privileged review/key recovery and zero-recurring-cost ambitions may be operationally incompatible with live/commercial assurance.

These are design risks requiring qualification or future scope gates, not known exploitable implementation findings. Do not accept Critical/High findings merely because the account is paper. The Phase 2 review must keep evidence status distinct from recommendation status.

## Review triggers and ownership

Revisit the model for any change to credentials, identities, tenant context, permissions, execution, lifecycle, data provider, model tools, external export, public exposure, paid service, database/crypto or backup method. Security and QA own threat-to-test coverage; component owners implement controls; independent reviewers challenge them. Every finance/authorization/tenancy/security/model-safety defect produces a regression test. Live/customer operation adds qualified legal review and explicit human design approval, never automatic promotion. See [test strategy](TEST_STRATEGY.md), [UAT](UAT_PLAN.md), and [role challenges](reviews/SECURITY_DATA_REVIEW.md).
