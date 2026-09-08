# ADR-0004: Tenant-keyed data with application checks and FORCE RLS

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

The initial user cannot justify a single global portfolio, broker connection or mutable tenant context.

## Decision

Recommend tenant_id on all owned rows, composite tenant-aware foreign keys/uniqueness, scoped service identities, mandatory application membership validation and FORCE RLS. Before tenant data, qualify independently verified expiring identity/capability context at the database trust boundary or tenant-scoped role pools; arbitrary tenant settings under a shared login are insufficient. Context is cleared between pooled requests; migrations/administration use separate audited roles. The exact verifier/role-pool mechanism is a recorded human and implementation-qualification decision, not an accepted implementation.

## Alternatives Considered

Database-per-tenant offers stronger administrative partition at increased lifecycle cost. Application filtering alone misses background/export paths. Schema-per-tenant adds management without sufficient default isolation.

## Security Impact

Superuser/BYPASSRLS and compromised trusted context setters can bypass or misuse RLS; do not claim RLS contains full backend/host compromise. Audit privileged access and keep support denied by default.

## Operational Impact

Two synthetic tenants are mandatory in integration, migration, export, worker and pool-reuse tests. Future export/deletion retain classification and legal holds.

## Consequences

Shared-schema V0 can evolve toward isolated tenant databases through repository contracts; outside-customer release requires revisiting residual privilege risk.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
