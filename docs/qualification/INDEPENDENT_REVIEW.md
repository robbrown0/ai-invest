# Independent Adversarial Review — Phase 3 Prerequisite Stop

**Status:** Reviewed as a prerequisite-blocked evidence package; Gate 2 NOT PASSED.
**Review date:** 2026-09-09 UTC.
**Reviewer perspective:** Separate security/qualification reviewer, not the author of the inventory or proposed controls.
**Purpose:** Challenge the stopping decision, evidence classifications and safe resumption conditions.

## Scope and independence

Read AGENTS.md, the merged security/data/risk/operations designs and tenancy ADR, then independently reviewed [the gate assessment](README.md), [sanitized inventory](HOST_INVENTORY.md) and [resumption proposal](RESUMPTION_PLAN.md). This reviewer did not implement controls, generate keys, start services or modify host configuration. Only this review document was authored by the reviewer.

The reviewed checkout was on phase3/synthetic-qualification at starting commit 924aaceac9df3e72d79b7ceecc141b98b6c6222a. Read-only Git inspection showed the qualification directory as the only untracked change and no tracked diff at that observation. The lead agent remains responsible for final staged-file, secret-pattern, commit and PR validation.

This is independent interpretation of the lead agent's selected observations and repository documents, not independent remeasurement of the host or a forensic attestation. No control implementation or runtime test result exists to evaluate. A second agent's review is not independent human release approval.

## Findings and disposition

| Finding | Assessment | Required treatment |
| --- | --- | --- |
| Encrypted project storage not demonstrated | Valid prerequisite stop; unrelated encrypted storage grants no project authority | Retain NOT QUALIFIED; do not describe this as a failed TDE implementation |
| Active file-backed host swap | Future secret-process protection is unproved, not universally impossible | Qualify project-scoped no-swap and core-dump controls; do not change shared-host swap implicitly |
| Docker daemon available | Read-only metadata access establishes availability only | Runtime isolation, egress, resource ceilings and negative tests remain NOT RUN |
| Existing non-loopback listeners | Neither remote reachability nor effective isolation was tested | Preserve uncertainty; do not describe the application as exposed or the network as secured |
| TDE/OpenBao/RLS/simulator/security-pipeline tests absent | Correctly marked NOT RUN or NOT QUALIFIED | Planned regression identifiers must never be counted as executed tests |
| Public disclosure scope | No hostname, private network address, unrelated workload name or credential value identified in reviewed documents | Continue sanitized reporting; final scanner results remain separate evidence |
| QH-06 transient measurement wording | Low-severity advisory corrected by author | Verified wording now says "one transient snapshot"; no idle/load assurance is inferred |
| Unrelated encrypted storage capacity | Low-severity advisory corrected by author | Verified unrelated mount capacity removed; unavailable-for-project status retained |

No blocking misrepresentation was found in the evidence package. The missing prerequisites themselves block qualification. Documentation of that block is suitable for a clearly labeled draft PR, not for Gate 2 approval or a claim that Phase 3 completed.

The author's added GitHub-controls section was also reread: it distinguishes existing enabled repository settings from unexecuted Phase 3 workflows/scanning and explicitly leaves QS-01 unqualified. This reviewer did not independently repeat the GitHub API requests; that limitation remains part of the evidence scope.

## Challenge to stopping versus alternatives

Stopping before key-bearing services is justified by the approved design's storage and secret-bootstrap obligations and the user's explicit stop-on-failed-assumption instruction. Lack of a visible crypt ancestor is evidence that encryption was not demonstrated; it does not exclude every possible hardware or external encryption layer.

Global swap disablement is not the only potential remedy. Docker supports preventing container swap with equal positive memory and memory-swap limits; actual cgroup enforcement and every secret-bearing helper still require testing. [Docker memory controls](https://docs.docker.com/engine/containers/resource_constraints/)

Tmpfs-only testing would not establish persistent cold recovery and may itself use swap. Synthetic unit tests could provide partial functional evidence, but cannot substitute for the required encrypted recovery qualification. [Docker tmpfs limitations](https://docs.docker.com/engine/storage/tmpfs/)

The smallest scoped owner decision is a dedicated approved encrypted local runtime/recovery location, protected human bootstrap/recovery custody and permission to qualify project-only memory/container controls. Do not reuse unrelated encrypted storage, request blanket administrative authority or use Docker access to circumvent the missing host-operator prerequisite.

## Required independent falsification after resumption

- Recover a cold database and secret manager with correct, missing, wrong and historical key versions. Warm-cache reads and absent plaintext markers alone cannot prove encryption or recoverability.
- Attack every implemented tenant access path, including CRUD, COPY/export, ownership-changing updates, composite foreign keys, views/functions, role escalation and stale pooled context. FORCE RLS does not constrain superuser/BYPASSRLS; deny runtime TRUNCATE/DDL and assess constraint-error leakage. [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- If tenant-role pools are selected, document the trusted selector's cross-tenant authority. If signed context is selected, independently verify it at the database boundary; application-only verification cannot contain a compromised application login.
- Use a separately durable simulator acceptance ledger to crash after acceptance but before acknowledgment. Duplicate workers, expired leases and temporary not-found lookups must not cause a second submission; UNKNOWN retains reservations and blocks new account dispatch.
- Race every scoped stop against admission. No post-stop admission may occur; previously admitted effects may still arrive and must remain reconstructable. Restart stays stopped.
- Demonstrate actual scanner execution and negative fixtures, not merely workflow configuration; resource and network safety require scoped runtime measurements.

Every discovered implementation defect involving finance, authorization, tenancy, security or model safety requires a regression test. The present REG-HOST specifications remain unimplemented; they do not close the prerequisite findings.

## Final independent position

Gate 2 is NOT PASSED. No TDE, recovery, OpenBao, RLS, financial-state-machine, network-isolation, CI or sustained-resource assurance is granted. The reviewed changes propose no host mutation, brokerage adapter, credentials, LIVE capability, public application exposure or commercial authority. Resume only after the owner resolves the scoped prerequisites; return actual qualification evidence for a new independent review and human gate decision.
