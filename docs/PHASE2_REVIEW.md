# Phase 2 Cross-Functional Review — Design Gate 1

**Status:** DRAFT — design package ready for human review; Design Gate 1 is NOT approved.
**Purpose:** Integrate specialist objections, independent review, unresolved decisions and evidence limits.
**Review date:** 2026-09-08.
**Branch:** `phase2/product-architecture-design`.
**Baseline:** `826a380c99b50883639041a0fa473bc5d9f5e17a` on main.

## Recommendation to the product owner

Review a modular core application with separated ingestion/inference, deterministic risk and PAPER execution processes on the local Ubuntu development host. Use tenant-aware PostgreSQL with mandatory qualified Percona pg_tde, supplemental encrypted local storage and separately managed OpenBao keys. Prefer local OIDC identity, PostgreSQL jobs/outbox and one bounded local inference queue. Keep NAS asynchronous and outside the financial path. All ten ADRs remain DRAFT.

V0 measures $100–$300 simulated portfolios using matched quantitative, local-AI, optional frontier and passive benchmark arms. Model output and manual frontier imports remain advice. P0 submission is human-triggered; a fresh deterministic approval follows that intent. BACKTEST/SHADOW cannot submit. No live adapter, credential provisioning, mode promotion, public SaaS or billing is authorized.

This package recommends moving to a narrowly scoped synthetic qualification phase only after explicit owner approval. It does not certify runtime controls: no implementation, services, financial tests or penetration tests exist yet.

## Review process and independence

Three specialist agents worked alongside the lead. They contributed nine perspectives; the lead performed Principal Application Architect, SRE and QA/SDET challenge passes and integrated the result. Each of the twelve perspectives recorded five concerns, potentially wrong assumptions, failure modes, missing requirements and simplifications. These are virtual roles, not twelve independent human approvers.

| Perspectives | Challenge record |
| --- | --- |
| Product Manager/Business Analyst; UX/UI Designer; Privacy/Compliance Risk Analyst | [Product and UX role reviews](reviews/PRODUCT_UX_REVIEW.md) |
| Security Architect; Threat Model/Red Team Reviewer; Data Architect | [Security and data role reviews](reviews/SECURITY_DATA_REVIEW.md) |
| Quantitative Research/Data Science; AI/ML Architect; Brokerage/Financial Systems Engineer | [Research and execution role reviews](reviews/RESEARCH_EXECUTION_REVIEW.md) |
| Principal Application Architect; SRE/Infrastructure Architect; QA/SDET Lead | [Architecture, operations and QA role reviews](reviews/ARCHITECTURE_OPERATIONS_QA_REVIEW.md) |

After drafts existed, separate agents read other authors' work and wrote [independent security](reviews/INDEPENDENT_SECURITY_REVIEW.md), [independent financial](reviews/INDEPENDENT_FINANCIAL_REVIEW.md) and [independent product](reviews/INDEPENDENT_PRODUCT_REVIEW.md) reviews. Lead integration corrected cross-document inconsistencies and retained qualification risks. Independent human review of security-sensitive code is still a future requirement.

## Meaningful disagreements and dispositions

| Disagreement or finding | Decision / disposition | Evidence limit |
| --- | --- | --- |
| Many microservices versus in-process simplicity | Modular product core; isolate research, risk and execution authority; do not deploy a service per analyst role | ADR-0001/0005 remain proposals |
| Continuous unattended recovery versus protected keys | Manual OpenBao unseal, stopped boot, human re-arm; accept possible V0 downtime | Owner must approve custody/RTO; colocated pseudo-HA rejected |
| Raw tenant SET context versus stronger isolation | Application + FORCE RLS plus independently verified DB-boundary authority or scoped role pools; exact mechanism must qualify | No claim that RLS alone contains shared-login compromise |
| Lease/fencing said to prevent broker duplication | **Corrected High design assurance error:** fencing protects local admission only. Admitted/unknown intent never gets another outbound attempt on expired lease; paused original worker/takeover tested | Broker cannot enforce local fences; UNKNOWN may require prolonged halt |
| UX risk preview before human click versus five-second permit | **Corrected:** preview is non-authoritative; human dispatch intent triggers fresh risk/reservation, then execution rechecks | Real latency/data support remains untested |
| Global/account-only stop versus user-required scoped stop | **Corrected:** global/platform, tenant, account, portfolio; strategy mandate suspension is separate P1 policy | In-flight broker orders can still fill |
| Strict free-data limits versus usable $200 portfolio | Keep no-margin/freshness/liquidity rules; benchmark rejection rate and fractional DAY limit capability; simulator/HOLD if unmet | Do not weaken controls or buy data silently |
| Distinct experiment arms versus one broker balance | Separate economic simulator ledgers; one active broker-linked PAPER portfolio per account | Paper fill fidelity is a separate experiment, not independent arm evidence |
| Export convenience versus financial privacy | No secrets, raw broker IDs or PII even with consent; minimized weights/public facts only with fresh-auth disclosure approval | Portfolio composition may still reveal preferences |
| Reject all URLs versus cite evidence | **Corrected:** bounded public HTTPS citation strings are inert unverified data; deny endpoint/auto-fetch/private/credential-bearing destinations | Ingestion still validates every requested retrieval |
| Large expert context versus blind comparison | Independent Stage A omits local conclusions; lock it before Stage B; mark contaminated/unblinded runs | Model/version assertions are not independently authenticated |
| TDE checkbox versus actual recovery | Qualify exact build/table/WAL/backup/key/IdP-migration matrix and encrypted residual storage | No plaintext fallback; loss of sole keys may be permanent |
| Fast paper autonomy versus review burden | Human-triggered P0; bounded scheduled PAPER mandate only after P1 recovery/patch evidence | No automated real-money promotion at any score |
| Rich dashboard metrics versus scientific attribution | Preregister cutoffs/arms/costs/horizons, all serious ideas and rejected outcomes; forward evidence primary | Short windows and current-model historical backtests can be misleading |

FIN-06's combined accounting fixture is now explicit in TEST_STRATEGY: $200 virtual equity remains the risk denominator despite a larger synthetic broker balance; analytic dividends and outside-model costs must not fabricate broker cash. Reviewer findings resolved here are documentation corrections, not claims that runtime defects were tested or fixed.

## Fourteen-question final review

| # | Question | Integrated answer and residual |
| --- | --- | --- |
| 1 | Could it accidentally execute an unauthorized real-money trade? | Current repository has no execution implementation or credentials. Proposed V0 removes live adapters/endpoints/grants and rejects live/mixed OAuth. Actual future proof requires ADV-23; a host owner installing different software is outside repository guarantees. |
| 2 | Could one tenant access another's information? | Application ownership, composite constraints, independently bound DB context/RLS and scoped caches/jobs/exports are required. Shared-login/issuer/DBA/host compromise remains residual; prove two-tenant runtime tests before data. |
| 3 | Could compromised Internet research directly cause a trade? | No direct authority, broker route or permit issuer in research. Intake, human P0 intent, deterministic risk and execution are required. A plausible poisoned thesis may still influence an allowed-size trade. |
| 4 | Could an LLM obtain broker credentials? | Allowlisted projections and absent secret mounts/routes prevent intended access; no credentials are configured now. Prove runtime canary/egress tests; never rely solely on prompt instructions or regex redaction. |
| 5 | Could ambiguity/duplicates create duplicate trades? | Persist one intent and stable identity; never resend admitted/UNKNOWN work because lease expired. Read reconciliation and reservations hold the account. Simulated paused-worker, lost-response and restart tests are mandatory; no distributed exactly-once claim. |
| 6 | Can financial actions be reconstructed? | Required chain covers actor/authority, evidence availability, versions, proposal, risk, intent, broker observations, unique fills/corrections and costs. Licensed evidence retention and independent audit anchors must qualify; local hash chain alone cannot resist host root. |
| 7 | Are costs unnecessary? | No required paid infrastructure, KMS, telemetry, model API or data subscription. Optional manual subscription use is separately allocated. Small capital makes even modest external costs material; no automatic paid fallback. |
| 8 | Can it run on the local Ubuntu development host? | Design is sized for one bounded local model queue, local DB and a small set of services, but host free resources/GPU/IO/encryption were not inventoried. Qualification must prove fit and protect existing workloads. |
| 9 | Can it support commercial multi-tenancy later? | Ownership and provider boundaries avoid single-user redesign. Commercial deployment still requires privileged isolation, availability, retention, legal and support controls; it is not a free configuration change. |
| 10 | Does it test AI value rather than assume it? | Matched A/B/C/D arms, frozen protocols, rejected/HOLD ideas, costs, forward predictions, uncertainty and ablations permit falsification. No durable-edge claim from a brief pilot; missing history and training contamination are disclosed. |
| 11 | Are numerical and language tasks separated? | Code/statistics handle arithmetic, eligibility, signals, sizing, risk and performance; LLMs interpret evidence, challenge theses and synthesize under governed schemas. Roles sharing a model are not independent votes. |
| 12 | Can a person explain proposal and permission? | UX separates evidence/thesis/bull-bear, risk preview, human intent, fresh rule results, submitted/UNKNOWN/fill states and audit. Stored concise rationales replace any demand for private model reasoning. UAT must validate comprehension. |
| 13 | Are host/DB/keys/broker/model/data/network failures handled? | Outage matrix, stopped reboot, manual unseal, UNKNOWN reconciliation, stale-data rejection, resource caps and local NAS-independent spool are specified. Test failures at every financial boundary and restore old key versions; operator absence affects RTO. |
| 14 | Can complexity be removed? | No Kubernetes, general event broker, vector database, independent analyst microservices, billing, broker OAuth or paid API in V0. Keep security-sensitive process separation; postpone scale features and measure before adding infrastructure. |

## Top ten risks

| Rank | Risk | Proposed mitigation / unresolved consequence |
| --- | --- | --- |
| 1 | Shared development host root or dependency/GPU compromise defeats local isolation | Minimal privileges/segmentation/scanning; single-host residual requires owner acceptance for paper and new deployment review for outside customers/live |
| 2 | Tenant context spoofing or privileged RLS bypass | DB-boundary capability/role-pool qualification, FORCE RLS and two-tenant tests; trusted issuer/DBA compromise remains |
| 3 | Ambiguous broker send, stale worker or stop race creates unexpected orders | Single admitted attempt, reservations, UNKNOWN/reconciliation, stopped recovery; accepted orders may fill after stop |
| 4 | Stolen execution credential bypasses in-app risk outside the platform | PAPER-only custody, no model exposure, isolated execution, broker revocation/reconciliation; future live token theft is a separate control problem |
| 5 | TDE residual plaintext, incompatible WAL backups or lost keys destroys confidentiality/recovery | Pinned qualification, encrypted volumes/backups, independent key custody and real restore; lost sole keys can be irreversible |
| 6 | Prompt injection/compromised evidence creates convincing bad proposals | Architectural authority removal, evidence checks/bear cases/governance; deterministic limits do not establish investment merit |
| 7 | Free-data coverage/licensing/freshness and fractional broker constraints make V0 unusable | Capability/source-rights/rejection-rate qualification; use HOLD or simulator, no silent safety relaxation |
| 8 | Local-only audit anchors and missing licensed source copies defeat reconstruction | Append-only history and independent checkpoints, permitted retained evidence; root rewrite remains residual until stronger archive separation |
| 9 | Look-ahead, small samples, regime dependence and costs create false AI edge | Forward preregistered comparisons, all outcomes/costs, uncertainty and multiplicity controls; evidence may remain inconclusive for years |
| 10 | Single-owner review/recovery and shared-host resource pressure conflict with unattended safety | Independent reviewer/custodians, resource budgets, manual P0, later automation gate; required CI checks and an independent approval count remain unenforced despite enabled branch/push protections |

Threat catalogue severity is inherent failure impact; these are not reports of exploitable running code. Critical/High implementation findings block release regardless of paper mode.

## Human decision register

| ID | Decision required | Proposed direction | Blocks |
| --- | --- | --- | --- |
| H-01 | Accept product scope, manual P0 and separated-process architecture | Approve only a synthetic qualification implementation after Design Gate 1 | Starting implementation |
| H-02 | Accept the shared local Ubuntu development host exposure and encrypted-storage change boundary | Private access, owner-reviewed host inventory; no disturbance to other services | Deployment qualification |
| H-03 | Exact Percona/pg_tde/OpenBao/backup/IdP combination and key custody | Pin proven versions; manual unseal; independent recovery copies/custodians; <=15m local RPO, <=4h operator-available RTO targets | Any sensitive data/paper credentials |
| H-04 | Trusted tenant-context mechanism and identity/recovery provider | Keycloak candidate; independent DB verifier or scoped tenant-role pools; Authentik alternative remains | Tenant storage and authentication release |
| H-05 | Pilot capital, risk thresholds, ETF exceptions and loss/settlement policy | Review RISK_MODEL candidate numbers; keep no margin/shorts/options/live; measure feasibility | PAPER eligibility |
| H-06 | Licensed/free data, safe fractional order capability and usable quote cadence | Prove exact provider contract/feed coverage; HOLD/simulator when insufficient | PAPER submissions |
| H-07 | Benchmark, primary endpoint, baseline strategy, horizons, power/uncertainty and late-frontier fallback | Preregister before outcomes; no fixed-duration proof | Scientific experiment start |
| H-08 | External packet disclosure and subscription cost allocation | No PII/secrets/IDs, consented normalized facts; record allocated and marginal costs | Manual frontier exports/comparisons |
| H-09 | Model candidates/licenses, host resource budgets and release thresholds | Local quantized model benchmark and held-out safety/grounding tests | Model-assisted evaluation release |
| H-10 | Independent reviewer, operator duties, stop/recovery/incident process | Human security-sensitive review; no self-approved financial releases; fresh-auth re-arm | Broker-connected/unattended PAPER |
| H-11 | Public-source disclosure discipline and independent review/CI gates | Retain public source and private-access/LAN-only application; enabled branch/push protections do not replace independent human review or future CI checks | Release governance |
| H-12 | Future legal/commercialization/live/billing scope | Qualified service-specific review; all future authority remains unavailable | Outside customers or real money only |
| H-13 | Source-code licensing | No license introduced; public visibility does not imply permission for reuse; owner must explicitly decide future licensing | License grant / distribution policy |

H-03 through H-10 can be investigated with synthetic qualification work only if H-01 explicitly approves that scope. No unresolved gate acquires a permissive default. Risk/lifecycle/cost/provider decisions cannot be quietly accepted by an implementation agent.

## Design Gate 1 checklist

| Required package element | Artifact / state |
| --- | --- |
| Product mission/personas/scope | [PRODUCT_CHARTER.md](PRODUCT_CHARTER.md) — substantively drafted |
| P0/P1 and later requirements/acceptance | [REQUIREMENTS.md](REQUIREMENTS.md) — 20 P0, 8 P1, 5 P2, 5 Future, 8 NFR; UAT mapping |
| Proposed architecture and alternatives | [ARCHITECTURE.md](ARCHITECTURE.md) — modular/separated process recommendation |
| Security and threat model | [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md), [THREAT_MODEL.md](THREAT_MODEL.md) — 33 threats with test/issue owners |
| Conceptual data model/classification | [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) |
| Deterministic risk/execution reliability | [RISK_MODEL.md](RISK_MODEL.md) |
| AI and model governance | [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md), [MODEL_GOVERNANCE.md](MODEL_GOVERNANCE.md) |
| Scientific and cost methodology | [EXPERIMENT_DESIGN.md](EXPERIMENT_DESIGN.md), [COST_MODEL.md](COST_MODEL.md) |
| UX storyboards | [UX_DESIGN.md](UX_DESIGN.md) |
| Testing/UAT | [TEST_STRATEGY.md](TEST_STRATEGY.md), [UAT_PLAN.md](UAT_PLAN.md) |
| Operational recovery and legal gates | [OPERATIONS_PLAN.md](OPERATIONS_PLAN.md), [REGULATORY_QUESTIONS.md](REGULATORY_QUESTIONS.md) |
| Major architecture decisions | [ADR index](ADR/README.md) — 10 DRAFT records, none accepted |
| Proposed implementation backlog | [IMPLEMENTATION_BACKLOG.md](IMPLEMENTATION_BACKLOG.md), [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md), [GitHub map](GITHUB_BACKLOG.md) — 12 V0 epics |
| Disagreements, independent review, human decisions | This document and linked review records |
| No implementation/live authorization | Changes limited to README, SECURITY.md and Markdown under docs; no services installed or credentials configured |

Package completeness is not human approval. The owner must review the draft PR and explicitly approve/revise the gate; no merge or implementation follows automatically.

## Validation and tooling record

Validation is documented in [VALIDATION.md](VALIDATION.md). It distinguishes parsing/link/structure/secret checks from unperformed runtime tests. Mermaid parser/render tooling is not installed; diagram syntax receives manual and basic declaration/fence review. No application dependencies or services are installed for validation.

### Public-source amendment and verified GitHub state — 2026-09-08

GitHub account remains `robbrown0`. The human product owner intentionally made the SOURCE REPOSITORY PUBLIC. This amendment preserves that visibility and supersedes the earlier private-repository entitlement findings. The V0 APPLICATION remains private-access/LAN-only: no deployment, public exposure, implementation or live authority is authorized.

Public source can be copied, forked, indexed and retained indefinitely. Keep tenant/account information, credentials, private host identifiers and operational inventory out of commits, issues, discussions, PRs and artifacts. Treat external contributions as untrusted; do not execute them with secrets or privileged infrastructure access. Current documentation and PR wording generalize unnecessary home-lab identifiers while retaining bare-metal Ubuntu, local SSD financial storage and an NVIDIA GPU with 8 GB VRAM. Historical commits and third-party copies may retain earlier identifiers; no history rewrite is performed.

| Feature | Verified state | Limitation / interpretation |
| --- | --- | --- |
| Dependency vulnerability alerts | Enabled; API read succeeds (204) | No dependency manifests exist yet; enablement is not evidence of a dependency audit |
| Dependabot security updates | Enabled, not paused | No update PRs expected without supported dependencies; no auto-merge configured |
| Secret scanning | Enabled | Supported provider patterns; not a guarantee that every secret is detectable |
| Secret push protection | Enabled | Pattern coverage and bypass limitations still require pre-publication checks |
| Main branch protection | Enabled and enforced for administrators | PR required; force-push/deletion blocked; linear history and resolved conversations required |
| Required reviewer approvals / CI status checks | Zero approvals; no status checks configured | Intentional documentation-phase configuration, not an authorization/plan blocker; independent human security review still required by AGENTS.md before security-sensitive code release |
| Private vulnerability reporting | Enabled | Use the private GitHub path in [SECURITY.md](../SECURITY.md); reporting enabled now, policy file will reach the default branch only after an owner-authorized merge |
| Supplemental generic/non-provider secret patterns | Disabled; enable request succeeds but returned state remains disabled | GitHub documents this as an organization/Secret Protection entitlement feature, unavailable for this personal repository; no authorization error was returned |
| Optional validity/extended-metadata checks | Validity setting reports disabled | GitHub documents Team/Enterprise Secret Protection eligibility; not a token-authorization failure |
| Code scanning / CI workflows | Not configured | No application code or supported language target yet; workflow design remains a later phase, not a paid-plan workaround |

Entitlement references: [generic-pattern eligibility](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enabling-secret-scanning-for-generic-patterns) and [validity/metadata eligibility](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns). The authenticated integration can administer this repository and changed all requested core settings without authorization errors. No paid service, subscription or trial was enabled. Classic branch protection satisfies the main-protection requirement; a duplicative ruleset was not added. Repository administrators can still change settings; current settings do not establish immutable governance.

[SECURITY.md](../SECURITY.md) defines responsible private reporting and prohibits real brokerage credentials anywhere on GitHub, including private reports. No license is added. Source licensing remains an explicit future product-owner decision; public visibility does not imply permission for reuse.

The host's filesystem sandbox helper intermittently fails with a loopback permission error. Approved shell-wrapped apply_patch was used for the requested documentation edits. Specialist work resumed after a usage-limit interruption. No credential-bearing output was requested or retained.

## Handoff rule

Commit and push only the Phase 2 branch, open a DRAFT PR against main, and do not merge. Proposed issues are gated design artifacts. Stop at this handoff and await explicit product-owner approval of Design Gate 1.
