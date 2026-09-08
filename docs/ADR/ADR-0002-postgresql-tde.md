# ADR-0002: Qualify Percona PostgreSQL TDE before sensitive data

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

PostgreSQL TDE is mandatory under AGENTS.md; ordinary disk encryption alone is insufficient. Extension support, WAL and backup behavior depend on exact versions.

## Decision

Recommend Percona Server for PostgreSQL with pg_tde, externally stored principal keys, encrypted user tables and WAL, plus encrypted local volumes for spill/system metadata. Pin a supported version set only after table/index/TOAST/WAL/backup/restore/rotation tests. A failing qualification blocks sensitive deployment.

## Alternatives Considered

Upstream PostgreSQL plus volume encryption fails the explicit TDE requirement. Managed TDE adds recurring cost. Another TDE implementation needs separate evidence and human review.

## Security Impact

TDE protects stored data, not privileged SQL/host access; current pg_tde limitations include catalog and query spill exposure. Identity-provider tables and extension-created tables must also be qualified; never silently exempt them.

## Operational Impact

WAL tooling and restoration must be proven for the pinned build, including old key versions. Do not assume generic backup compatibility.

## Consequences

Percona-specific operations create a maintenance obligation but preserve required encryption. No fallback to unencrypted data is authorized.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
