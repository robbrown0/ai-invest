# ai-invest

An experimental, multi-tenant, local-first AI-assisted investment research and paper-trading project. The internal name may change.

The repository contains design documents and bootstrap placeholders only. **Phase 2 is at Design Gate 1 review; implementation requires explicit product-owner approval.** All architecture decisions remain DRAFT.

The goal is to test whether quantitative methods, local AI and optional frontier research improve risk-adjusted results after externally billed costs. No investment return or AI outperformance is promised. Initial experiments use $100–$300 simulated capital; PAPER is the only permitted external trading mode. BACKTEST/SHADOW do not submit orders, and no real-money functionality exists here.

Proposed deployment is containerized services on the existing bare-metal Ubuntu PodFlix host, with local PostgreSQL TDE/OpenBao and local inference. Primary financial storage stays local; NAS is optional encrypted archive. The target is approximately zero recurring external infrastructure cost.

Start with [AGENTS.md](AGENTS.md), then:

- [Product charter](docs/PRODUCT_CHARTER.md) and [requirements](docs/REQUIREMENTS.md)
- [Proposed architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY_ARCHITECTURE.md) and [threat model](docs/THREAT_MODEL.md)
- [Data](docs/DATA_ARCHITECTURE.md), [risk/execution](docs/RISK_MODEL.md), [AI](docs/AI_ARCHITECTURE.md) and [model governance](docs/MODEL_GOVERNANCE.md)
- [UX storyboards](docs/UX_DESIGN.md), [experiment design](docs/EXPERIMENT_DESIGN.md), [costs](docs/COST_MODEL.md) and [legal questions](docs/REGULATORY_QUESTIONS.md)
- [Testing](docs/TEST_STRATEGY.md), [UAT](docs/UAT_PLAN.md) and [operations/recovery](docs/OPERATIONS_PLAN.md)
- [Draft ADRs](docs/ADR/README.md), [roadmap](docs/IMPLEMENTATION_ROADMAP.md), [proposed backlog](docs/IMPLEMENTATION_BACKLOG.md) and [GitHub issue map](docs/GITHUB_BACKLOG.md)
- [Cross-functional review and unresolved human decisions](docs/PHASE2_REVIEW.md)

Security, tenant isolation, deterministic risk controls, auditability and testing are requirements from the beginning. The blank `.env.example` is a bootstrap variable inventory, not an approved runtime secret-provisioning mechanism; future implementation must use scoped secret references/mounts rather than raw secrets in ordinary application configuration.
