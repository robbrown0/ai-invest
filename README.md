# ai-invest

`ai-invest` is an experimental AI-assisted investment research and automated trading platform. The project is currently in its architecture and repository-bootstrap phase; this repository contains no production application code.

Paper trading is mandatory during initial development. Real-money trading functionality must not be enabled yet, and no claim is made that AI can reliably outperform financial markets.

The system is intended to be multi-tenant from the beginning. Its initial deployment target is bare-metal Ubuntu with containerized services. Local infrastructure and local AI inference are preferred where practical to limit recurring costs while preserving portability to managed services later.

Security, tenant isolation, deterministic risk controls, auditability, and testability are first-class requirements. See [AGENTS.md](AGENTS.md) for the engineering constitution and [`docs/`](docs/) for draft planning documents.
