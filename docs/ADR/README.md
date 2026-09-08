# Architecture Decision Records

**Purpose:** Record material architecture recommendations and their review status.
**Status:** DRAFT — none of these decisions is ACCEPTED.

Use `ADR-0001-short-description.md`. Each record contains Status, Date, Context, Decision, Alternatives Considered, Security Impact, Operational Impact and Consequences. Number monotonically; superseding decisions link prior records rather than rewriting historical acceptance.

## Phase 2 proposals

- [ADR-0001: Modular core with isolated financial and research processes](ADR-0001-deployment-architecture.md) — DRAFT
- [ADR-0002: Qualify Percona PostgreSQL TDE before sensitive data](ADR-0002-postgresql-tde.md) — DRAFT
- [ADR-0003: Local OpenBao with separated recovery material](ADR-0003-openbao-secrets-and-keys.md) — DRAFT
- [ADR-0004: Tenant-keyed data with application checks and FORCE RLS](ADR-0004-tenant-isolation.md) — DRAFT
- [ADR-0005: Separate risk authority from order authority](ADR-0005-financial-service-boundaries.md) — DRAFT
- [ADR-0006: Advisory AI behind a sanitized evidence gateway](ADR-0006-ai-execution-isolation.md) — DRAFT
- [ADR-0007: PostgreSQL durable jobs and transactional outbox](ADR-0007-durable-jobs-and-outbox.md) — DRAFT
- [ADR-0008: Local OIDC identity with passkeys](ADR-0008-identity-authentication.md) — DRAFT
- [ADR-0009: Provider-neutral bounded local inference](ADR-0009-local-model-serving.md) — DRAFT
- [ADR-0010: Capability-aware PAPER broker adapter](ADR-0010-brokerage-provider-abstraction.md) — DRAFT

Human review of Design Gate 1 must explicitly resolve acceptance or requested revisions. Publishing this branch, opening a draft PR or creating implementation issues does not accept these ADRs or authorize implementation.
