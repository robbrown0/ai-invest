# ADR-0007: PostgreSQL durable jobs and transactional outbox

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

V0 needs reliable scheduling and recoverable financial work, not a high-volume event platform.

## Decision

Use tenant-scoped durable PostgreSQL jobs/outbox atomically written with business events, bounded leases/backoff, immutable input references and idempotent consumers. Notifications are hints; at-least-once delivery is assumed. Order ambiguity is resolved by execution, never generic queue retry.

## Alternatives Considered

Redis requires separate durability design; NATS JetStream is appropriate if future fanout/throughput warrants it; a transient in-memory queue loses work.

## Security Impact

Worker claims must validate tenant/actor scopes. Separate privileges prevent job bodies being interpreted as authority or executable code.

## Operational Impact

Database outage stops work safely; control backlog priority and capacity to protect reconciliation. SKIP LOCKED is a queue technique, not a financial snapshot guarantee.

## Consequences

Simplifies atomic state transitions at the cost of one failure domain. Reconsider when measured contention or multi-host consumers justify a broker.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
