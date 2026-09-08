# ADR-0010: Capability-aware PAPER broker adapter

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

Alpaca is initial target, but accounts, order types, fractional support and data capabilities vary by provider; generic OAuth may include live grants.

## Decision

Define a capability-aware adapter inside execution for paper account sync, asset/calendar metadata, order submit/query/cancel and reconciliation. V0 uses manually provisioned paper-only credentials. No live adapter or endpoint configuration. Qualify fractional DAY limit orders explicitly; unsupported safe order form yields HOLD/simulator fallback, not a weaker market order.

## Alternatives Considered

Hardcoding Alpaca throughout the app hinders portability. A universal order interface that hides capability differences can produce unsafe fallbacks. Generic OAuth onboarding adds unnecessary live-grant risk now.

## Security Impact

Only allowlisted paper broker transport is reachable from execution; no redirects to live hosts, user-supplied URLs or model-selected secret paths. IDs are scoped and never disclosed to models.

## Operational Impact

Persist stable client order identity before send; on timeout query/reconcile original order and retain reservation. Never promise exactly-once remote effects.

## Consequences

Enables later broker adapters without assuming identical semantics. Human must approve paper contract results; live integration remains a separate future authorization design.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
