# ADR-0008: Local OIDC identity with passkeys

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

V0 needs strong authentication and recoverable sessions without inventing password/passkey security or paying an external identity provider.

## Decision

Propose local Keycloak OIDC with passkeys/WebAuthn and verified recovery flows, private TLS exposure, Authorization Code with PKCE, server-managed secure sessions, issuer/audience validation and fresh authentication for sensitive changes. Tenant membership/permissions remain application-owned.

## Alternatives Considered

Authentik remains viable with operator-fit evaluation. Application-native identity removes a service but increases security implementation burden. Managed identity adds recurring dependency/cost.

## Security Impact

Identity authentication does not grant broker execution or support impersonation. Recovery must not be weaker than login; admin routes and IdP keys isolated. No generic brokerage OAuth in V0.

## Operational Impact

Qualify exact IdP/PostgreSQL/pg_tde migration behavior, session revocation, clock drift and backup restore. Do not deploy Keycloak development mode.

## Consequences

Adds one mature identity service and update duty. Final provider and recovery method require human review after the qualification spike.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
