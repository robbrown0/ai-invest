# Implementation Roadmap

**Status:** DRAFT — all implementation awaits explicit human approval of Design Gate 1.
**Purpose:** Sequence evidence-producing work while keeping financial authority disabled until tested.

## Gate and milestones

| Stage | Work | Exit evidence | Authority after exit |
| --- | --- | --- | --- |
| Design Gate 1 (this phase) | Product/requirements, architecture/threat/data/risk/model/experiment/UX/test/UAT plans, draft ADRs, backlog and independent review | Draft PR and owner decisions recorded | Documentation only; no implementation until explicit approval |
| M1 Foundations | V0-01 host/TDE/keys, V0-02 identity/tenancy, V0-07 audit/jobs/release evidence | Qualified encryption/restore, scoped identities, actual RLS/isolation checks | Synthetic fixtures and simulator only |
| M2 Data and ledger | V0-03 licensed data/provenance, V0-04 economic ledger/simulator | Point-in-time datasets, independent arithmetic oracle, fault simulator | Backtest/shadow evaluation; no broker submissions |
| M3 Controlled PAPER slice | V0-05 deterministic risk, V0-06 execution/reconciliation, V0-09 accessible control UX | Independent review, all order/stop/freshness/replay tests, qualified paper contracts | Human-triggered PAPER only after explicit readiness approval |
| M4 Research and experiments | V0-08 local AI/memory/governance, V0-10 manual expert review, V0-11 experimental metrics/cost | Frozen eval/protocol, sanitized context/import adversarial checks, matched benchmark | Advisory research; same risk/authorization chain |
| M5 PAPER readiness gate | V0-12 integrated adversarial/recovery/UAT | Product-owner review of actual evidence and residual risks | Restricted manual PAPER experiment, no live capability |
| P1 supervised automation | Scheduled/event/overnight research and explicitly bounded PAPER mandate, recovery/patch drills | Fresh-auth mandate, expiry/scope, resource/cost cap, stop drill, reviewed unattended-failure behavior | Only PAPER under human-issued mandate |
| P2 extended evaluation | Richer sources/scouting/regime analysis, longitudinal outcome and model comparisons | Multiple regimes, prespecified uncertainty and cost assessment | Still research/paper/shadow |
| Future separate gates | Outside-customer SaaS, legal review, availability, billing, possible live authorization design | Qualified legal/security/financial review and explicit human authorization | Not granted by any step in this roadmap |

M3 parts can be built against the simulator before paper credentials are provisioned. M4 may progress in parallel with M3 after foundations. Issue dependencies are binding; milestone display order is not permission to skip prerequisites.

## First implementation task after approval

Start V0-01 with a non-sensitive qualification plan and exact version matrix. Measure PodFlix resources and evaluate encrypted local storage without disrupting existing services. Prove OpenBao cold start/unseal, TDE scope and backup/key recovery with synthetic data before data ingestion or brokerage connectivity. This is a feasibility gate, not authorization to install anything during Phase 2.

Do not select model weights on reputation or commit to a frontend/backend framework before tiny targeted spikes establish maintainability. Do not let identity-provider migrations silently create unencrypted tables. Do not allocate shared-host GPU/IO to research before critical services have reserved capacity.

## Planning policies

Use [IMPLEMENTATION_BACKLOG.md](IMPLEMENTATION_BACKLOG.md) as the issue specification and [GITHUB_BACKLOG.md](GITHUB_BACKLOG.md) for external references. Every issue includes security and tests in its own completion criteria; M5 integrates evidence and is not when testing first begins.

Each implementation PR names requirements, relevant ADRs, threat cases, tests, operational impact and rollback. Security-sensitive code requires independent review; Critical/High security findings block release. No agent accepts its own ADR or merges design approval on the owner's behalf.

Estimate effort only after qualification; there is no justified delivery date or availability promise yet. Keep local recurring cost near zero, with any externally billed experiment requiring a visible human-approved budget and cost ledger. P0 includes manual frontier packet generation/import, but no paid API dependency.

## Human decisions before dependent work

[PHASE2_REVIEW.md](PHASE2_REVIEW.md) is the decision register. In particular: approve risk/capital thresholds and investable universe, benchmark/evaluation protocol, identity/recovery method, TDE/toolchain/volume approach, source licenses, shared-host residual risk, independent reviewer and recovery custodians. Live transitions and pricing remain future questions, not choices to make in this phase.

A completed design package is **ready for review**, not a passed human gate. Stop after draft PR publication and await explicit product-owner approval.
