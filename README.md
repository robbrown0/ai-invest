# ai-invest

An experimental, multi-tenant, local-first AI-assisted investment research and paper-trading project. The internal name may change.

The owner has authorized development toward a working PAPER-only V0. A [runnable disconnected CLI](docs/RUN_V0.md) now exercises durable intents, deterministic risk, simulated submission, reconciliation and process-restart recovery. **Actual Alpaca PAPER connectivity is not yet runnable; Gate 2 remains NOT PASSED.** The synthetic --io-test command is deferred. See [foundation context](docs/V0_IMPLEMENTATION.md) and the CLI guide for concrete remaining database/credential blockers. Draft ADRs are not silently marked accepted.

Current runnable milestone: [PostgreSQL-backed V0 CLI](docs/POSTGRES_RUNTIME.md), with deployed TDE/WAL encryption, tenant isolation and restart recovery. Dedicated storage/database setup is complete. Alpaca PAPER credential provisioning and real execution remain unconnected; no OpenBao initialization occurred.

The goal is to test whether quantitative methods, local AI and optional frontier research improve risk-adjusted results after externally billed costs. No investment return or AI outperformance is promised. Initial experiments use $100–$300 simulated capital; PAPER is the only permitted external trading mode. BACKTEST/SHADOW do not submit orders, and no real-money functionality exists here.

Proposed deployment is containerized services on the local bare-metal Ubuntu development host, with local PostgreSQL TDE/OpenBao and local inference. Primary financial storage stays local; NAS is optional encrypted archive. The target is approximately zero recurring external infrastructure cost.

The SOURCE REPOSITORY is public by product-owner decision. The V0 APPLICATION remains private-access/LAN-only; public source does not authorize public endpoints, onboarding or application exposure. Do not publish deployment inventory, private addresses, tenant data or credentials.

Report vulnerabilities through the private path in [SECURITY.md](SECURITY.md), not public issues. No software license is introduced: licensing remains an explicit future product-owner decision, and public visibility does not imply permission for reuse.

Start with [AGENTS.md](AGENTS.md), then:

- [Product charter](docs/PRODUCT_CHARTER.md) and [requirements](docs/REQUIREMENTS.md)
- [Proposed architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY_ARCHITECTURE.md) and [threat model](docs/THREAT_MODEL.md)
- [Data](docs/DATA_ARCHITECTURE.md), [risk/execution](docs/RISK_MODEL.md), [AI](docs/AI_ARCHITECTURE.md) and [model governance](docs/MODEL_GOVERNANCE.md)
- [UX storyboards](docs/UX_DESIGN.md), [experiment design](docs/EXPERIMENT_DESIGN.md), [costs](docs/COST_MODEL.md) and [legal questions](docs/REGULATORY_QUESTIONS.md)
- [Testing](docs/TEST_STRATEGY.md), [UAT](docs/UAT_PLAN.md) and [operations/recovery](docs/OPERATIONS_PLAN.md)
- [Draft ADRs](docs/ADR/README.md), [roadmap](docs/IMPLEMENTATION_ROADMAP.md), [proposed backlog](docs/IMPLEMENTATION_BACKLOG.md) and [GitHub issue map](docs/GITHUB_BACKLOG.md)
- [Cross-functional review and unresolved human decisions](docs/PHASE2_REVIEW.md)

Security, tenant isolation, deterministic risk controls, auditability and testing are requirements from the beginning. The blank `.env.example` is a bootstrap variable inventory, not an approved runtime secret-provisioning mechanism; future implementation must use scoped secret references/mounts rather than raw secrets in ordinary application configuration.
