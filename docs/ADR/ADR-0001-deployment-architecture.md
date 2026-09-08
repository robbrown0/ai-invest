# ADR-0001: Modular core with isolated financial and research processes

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

A single existing host and near-zero cash budget cannot justify independently deployed services for each product module or research role. A single process would expose broker authority to untrusted research.

## Decision

Recommend a modular product application plus dedicated ingestion/research, inference, deterministic risk and execution processes with distinct identities, mounts and network policy. Compose is the initial orchestrator; no Kubernetes or multi-host HA promise.

## Alternatives Considered

Many microservices offer independent scaling but add deployment/queue/network state. A monolith minimizes operations but shares privileges. Separate only where privilege or failure boundaries justify it.

## Security Impact

A shared host remains a common compromise boundary. Separate containers alone do not establish authorization; identities and deny-by-default egress are required.

## Operational Impact

Keep one deployment manifest family, versioned contracts and bounded queues. Benchmark shared-host contention before release.

## Consequences

Fewer operational parts with deliberate control boundaries; future splits use existing module interfaces. Owner must accept single-host availability and approve isolation qualification.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
