# ADR-0003: Local OpenBao with separated recovery material

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

Secrets and principal keys cannot live in Git or ordinary application configuration; a secret-manager/database circular boot dependency would prevent recovery.

## Decision

Recommend a distinct local OpenBao service using integrated storage independent of PostgreSQL, TLS, workload-specific policies, separate key domains and human-controlled Shamir unseal for V0. Execution alone can obtain paper broker secrets. Keep recovery shares offline/separately protected.

## Alternatives Considered

External KMS adds cost/dependency. Colocated multi-node OpenBao does not solve host loss. File-based raw key storage beside ciphertext undermines separation. Hardware/off-host unseal may be revisited.

## Security Impact

Separate key storage from data logically and in backup custody; one-host root compromise remains residual. AI/model services have no secret-manager grant.

## Operational Impact

Manual unseal requires operator availability after restart. Restore OpenBao state and recovery material before encrypted DB recovery; test rotation/revocation and old backups.

## Consequences

Accept deliberate cold-start availability cost for V0. Human must designate custodians and approve recovery objectives.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
