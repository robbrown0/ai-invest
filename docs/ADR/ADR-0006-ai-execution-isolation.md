# ADR-0006: Advisory AI behind a sanitized evidence gateway

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

Internet content and frontier imports are adversarial input. Prompt instructions cannot securely restrict an otherwise privileged agent.

## Decision

LLMs receive allowlisted sanitized context and produce strict untrusted advisory schemas. They have no broker/secret/financial-write tools, general DB access or internal network reachability. Trusted intake resolves authorized portfolio and creates proposals; deterministic risk remains mandatory.

## Alternatives Considered

Tool-rich autonomous trading agents concentrate authority. Prompt-only prohibitions and manual review alone do not contain injection. Separate logical specialists improve analysis but do not create security boundaries by themselves.

## Security Impact

Test SSRF, document/parser abuse, exfiltration and indirect prompt injection at actual runtime boundaries. Manual export never includes credentials, raw account IDs or PII; consent does not waive these exclusions.

## Operational Impact

Maintain provenance, content-size budgets, quarantine and redaction tests; local deterministic HOLD is valid when evidence is poor.

## Consequences

Some convenient context and tools are deliberately unavailable. Human review remains advisory to the risk gate, not a bypass.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
