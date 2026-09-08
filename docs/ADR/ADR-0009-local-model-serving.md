# ADR-0009: Provider-neutral bounded local inference

## Status

DRAFT — proposed for Design Gate 1; not ACCEPTED.

## Date

2026-09-08

## Context

8 GB VRAM on a shared NVIDIA GPU limits concurrent contexts and model size; overnight CPU offload is acceptable.

## Decision

Introduce one local inference contract and bounded priority queue. Benchmark Ollama and llama.cpp with small quantized models for triage, larger CPU-offloaded reasoning only when evidence warrants. Record exact weights/license/digest/quantization/template and approved version; no automatic model upgrades.

## Alternatives Considered

One large model everywhere wastes latency; one service per specialist wastes resources. High-throughput runtimes and paid APIs are future options behind the contract.

## Security Impact

Inference has no brokerage credentials or execution tools. Disable outbound access after approved model provisioning, bound context/artifact ingestion and keep tenant caches isolated.

## Operational Impact

Measure memory, latency, structured output quality and contention on actual host. Deterministic/statistical tasks do not call an LLM.

## Consequences

No model name or fit claim is accepted without evaluation. Premium external review remains optional and separately cost-accounted.

See [Architecture](../ARCHITECTURE.md), [Security Architecture](../SECURITY_ARCHITECTURE.md) and [Phase 2 Review](../PHASE2_REVIEW.md) for supporting evidence, unresolved decisions and cross-functional objections.
