# Security, Red-Team and Data Specialist Challenge Review

**Status:** DRAFT — separate virtual-role challenges, integrated 2026-09-08; not human approval or operational verification.

**Purpose:** Record disagreements, falsifiable assumptions and remaining gates arising from security, adversarial and data reviews.

The three perspectives below were applied separately to the common design. They are not three independent human reviewers and cannot satisfy the constitution's future independent security-sensitive release review by themselves. Reviewed [architecture](../ARCHITECTURE.md), [operations](../OPERATIONS_PLAN.md), [security](../SECURITY_ARCHITECTURE.md), [threat model](../THREAT_MODEL.md) and [data design](../DATA_ARCHITECTURE.md).

## Security Architect

### Top five concerns

1. Shared-role RLS commonly mistakes a freely set tenant value for authenticated authority. A compromised application can select a different tenant unless the database boundary independently validates scope or uses distinct tenant credentials.
2. PodFlix root/Docker administrators and unrelated workloads share the secret-manager, execution and plaintext-memory compromise domain. Container count is not physical separation.
3. TDE does not cover every on-disk surface; query spills/catalogs and decrypted WAL backup intermediates can defeat broad encryption claims. Key loss can defeat every apparently valid backup.
4. Single-owner operations cannot offer true dual control, and passkey recovery/secret-zero bootstrap can silently recreate standing privileged secrets.
5. A stopped application cannot retract broker-accepted/in-flight orders, and a stolen execution credential can trade outside application risk controls.

### Assumptions that may be wrong

An appropriately scoped PAPER key can be operationally attested without live access; Keycloak and its database/migrations fit the encrypted local platform; an independent human reviewer is available; dedicated encrypted local storage can be added without disrupting PodFlix; operators can maintain separate recovery custody.

### Failure modes

Application-controlled tenant settings bypass intended isolation; a provider token is accidentally written into database logs/configuration; OpenBao and PostgreSQL form a circular bootstrap dependency; cached permits survive revocation; a model receives credentials through debugging; recovery restores data but not historical keys or identity revocations.

### Missing requirements identified and added

Independently authenticated tenant context gate; no generic broker OAuth in V0; token-file delivery outside PGDATA; encryption coverage assertions/forced-spill tests; restoring historical key versions; conditional recovery-time target; explicit in-flight stop semantics; secret-zero enrollment and scoped human break-glass. Legacy blank `.env.example` secret names are inventory, not permission to provision raw secrets through ordinary configuration.

### Simplifications worth considering

Private access and one local identity provider; one OpenBao with manual unseal; no broker OAuth/live adapters; no same-host HA cluster; no separate service per research persona. Maintain separate risk/execution/ingestion identities even when deployment artifacts share a codebase. Defer customer support impersonation entirely rather than implement broad standing access in V0.

### Challenge disposition

Security initially favors database-per-tenant and independently hosted keys for stronger compromise containment. Data/SRE favor shared schema/local OpenBao to meet V0 cost and maintainability. Proposed resolution: retain local/shared V0 only with verified tenant-context qualification, narrow privileges and explicit host-root residual; require a new isolation/key-hosting decision before customers/live funds. This is conditional recommendation, not acceptance of a Critical/High vulnerability.

## Threat Model / Red Team Reviewer

### Top five concerns

1. Prompt isolation prevents direct authority abuse but does not prevent a persuasive malicious filing from producing a plausible permitted trade. Financial caps bound loss, not truth.
2. Expert-review packets and imports can launder untrusted recommendations into apparent human approval, leak identity via holdings, or use packet IDs to target another tenant.
3. Timeout/replay/lease/restore combinations defeat naive idempotency; a stable client ID alone does not resolve broker uncertainty.
4. Audit hashes and evidence URLs are weaker than advertised if a privileged operator can rewrite the whole local chain or a source disappears.
5. Hindsight, rejected-idea omission, unavailable historical data and missing paid-model costs can manufacture apparent AI value without any classical security exploit.

### Assumptions that may be wrong

Broker lookup/deduplication semantics hold under retries and stale responses; egress policies really block private networks/IPv6/redirects; parser sandboxes survive realistic documents; imported model provenance is verifiable; all retained sources remain legal and sufficient to reconstruct a decision.

### Failure modes

Allowed-size malicious proposal passes risk; rich-text import executes in the browser; SSRF reaches OpenBao; queued authorization outlives membership/stop changes; restored outbox resends an accepted order; deletion removes the tail of a hash chain without detection; a late publication timestamp contaminates a historical experiment.

### Missing requirements identified and added

Thirty-three threat scenarios with falsification evidence and owners, including compromise of execution credentials outside the app; malicious export/import tenant binding; DNS/redirect address revalidation; cross-account/epoch replay; source availability and missing-tail evidence; inherited confidentiality of embeddings/caches; prospective outcome definitions and all recommendation outcomes.

### Simplifications worth considering

No model browser/shell/SQL tools initially; deterministic fetch workers and bounded local context; structured JSON import only rather than arbitrary documents/plugins; one serialized account dispatcher; maintain explicit UNKNOWN state rather than attempting distributed exactly-once machinery. Use external encrypted checkpoint copies before considering elaborate ledger platforms, while clearly stating the limits of non-immutable NAS storage.

### Challenge disposition

The research/product desire for an expert to search independently conflicts with giving a privileged browser agent rich tenant context. Resolution: human-initiated minimized packet with explicit disclosure preview, evidence-only independent research first, and untrusted structured import; the expert never receives secrets/account IDs or execution connectivity. Red Team does not accept wording that a kill switch guarantees no later fills; the design now distinguishes new dispatch from in-flight broker effects.

## Data Architect

### Top five concerns

1. Tenant IDs without compound ownership references permit cross-tenant joins/references even when each object ID is unique.
2. Free public data may lack point-in-time universe membership, revisions, delisted securities or permitted archival, making outcome comparisons biased or unreconstructable.
3. Decimal precision, partial fills, corporate actions and multiple portfolios sharing one account can produce divergent balances despite apparently valid APIs.
4. A database backup and separately copied evidence files can recover to incompatible times; neither a source hash nor a live URL restores missing evidence.
5. Immutable financial history, tenant deletion/export, backup retention and legal holds pull in different directions and cannot be settled with an invented retention duration.

### Assumptions that may be wrong

Broker reports provide sufficient unique fill/correction identities; symbol history and corporate actions can be licensed affordably; all tenant access paths are catalogued; privacy rights allow the proposed evidence retention; suitable encrypted backup tooling works with the pinned pg_tde release.

### Failure modes

Ticker reuse joins the wrong company; split-adjusted historical values enter an earlier decision; duplicated/out-of-order fills double cash; concurrent portfolio reservations overspend one account; null-tenant convenience policy leaks data; restored deleted tenant regains access; archive migration removes evidence still needed by an active proposal.

### Missing requirements identified and added

Compound tenant foreign keys and scoped business uniqueness; stable instrument identity; separate event/receipt/availability timestamps; versioned corrections; account-level allocation/reservations; immutable recommendation/HOLD history; explicit actual/estimated/imputed costs; database/artifact backup manifests; restoration deletion/revocation replay; licensed evidence sufficiency gate.

### Simplifications worth considering

Shared schema with narrow roles/verified RLS; PostgreSQL jobs/outbox; local encrypted evidence with manifests; no vector database, time-series extension or warehouse until measured need. Allow multiple accounts/tenants in the model, while V0 can limit one active paper portfolio per broker account operationally. Avoid database columns that store raw broker tokens when a secret reference suffices.

### Challenge disposition

Data prefers shared schema for transactional consistency and operational simplicity, but accepts Security's objection that raw session context is not independent tenant authentication. The draft tenancy ADR must qualify verified capability context or scoped role pools before tenant data. Data also rejects indefinite retain-everything architecture: provenance must be sufficient and licensed; retention/deletion/holds remain qualified legal-review inputs rather than fictitious compliance rules.

## Integration disagreements and decisions

| Disagreement | Resolution or required human decision | Evidence/gate |
| --- | --- | --- |
| Strong isolation versus zero-cost single host | Modular application with isolated dangerous processes; explicit common root/key-memory risk; separate live/commercial review | Negative service-identity/network tests; owner accepts bounded paper deployment |
| Database-per-tenant versus shared RLS | Shared proposed conditionally; independently verified context or tenant role pools mandatory | Tenant-context spike before any sensitive tenant data |
| TDE checkbox versus full encrypted storage | Mandatory TDE plus encrypted residual surfaces and separately encrypted backups | Pinned-version coverage/rotation/restart/restore qualification |
| Automated availability versus human key custody | Manual unseal/local independent OpenBao; no circular auto-unseal | Custody choice and observed reboot/restore timings |
| Security draft one-working-day restore versus SRE four-hour target | Align to proposed RTO at most four hours only when operator and all recovery materials are available | Human approval and timed rehearsal; absence can exceed target |
| Kill switch as instant no-fill guarantee versus broker reality | Durable stop blocks subsequent dispatch; existing orders may fill, cancellation best effort | Race tests and honest pending-exposure UX |
| Complete immutable evidence versus licensing/privacy | Retain legally permitted sufficient evidence; block consequential use if reconstruction inadequate | Data-license/evidence qualification and future legal retention review |
| Expert independent research versus data minimization | Packet-scoped sanitized facts, explicit human preview/consent, no IDs/secrets, untrusted import | Export canaries, wrong-tenant import and schema/adversarial tests |
| Scientific breadth versus free-data reality | Preserve missingness, universe limitations and all serious recommendations; no short-period edge claim | Preregistered experiment/data-quality review |

## Factual findings affecting integration

As checked 2026-09-08: pg_tde 2.2.2 documentation distinguishes encrypted temporary tables from unencrypted query spill, excludes internal catalogs, requires Percona server compatibility, and imposes special encrypted-WAL backup tooling constraints. These are qualification inputs, not a recommendation to install any version now. Sources and the detailed design interpretation are in [security architecture](../SECURITY_ARCHITECTURE.md).

PostgreSQL RLS does not constrain superusers/BYPASSRLS, nor authenticate arbitrary context chosen by a shared role. OpenBao's database-key KV provider is distinct from Transit-based application envelope encryption, and unseal/recovery material is distinct from the database principal key. The design must preserve these distinctions in ADRs and implementation acceptance criteria.

## Remaining approval questions

Human ownership is required for recovery custodians/targets, private-access method, independent reviewers, encrypted volume changes on shared PodFlix, and eventual live/commercial isolation. Technical spikes must select a demonstrable tenant-context mechanism and compatible TDE/identity/backup versions. None of those decisions is silently resolved by this virtual review, and no production code, credentials or services were added.
