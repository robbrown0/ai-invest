# ADR-0005: Separate risk authority from order authority

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

A compromised research/control component must not self-approve and submit trades. A risk-approved proposal can become unsafe before dispatch.

## Decision

Risk owns deterministic evaluation and one-use approval/reservation creation. Execution verifies immutable proposal digest, tenant/account, mandate, state/policy versions, expiry and stop epoch before dispatch. Only execution holds paper broker authority; broker reads stay there too.

## Alternatives Considered

In-process risk library is useful for shared calculations but not an independent approval boundary. Giving a reporting service order-capable credentials creates another authority holder.

## Security Impact

Approval rows/signatures and DB grants cannot be minted by research/control; signing/service credentials remain outside model payloads. No cross-tenant account or secret-path selection from model text.

## Operational Impact

Requires serialized account dispatch, durable intent, reconciliation and clear UNKNOWN handling. Financial services can share reviewed pure calculations without sharing credentials.

## Consequences

One extra process boundary and test surface are justified by control separation; full execution/host compromise remains a severe residual.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
