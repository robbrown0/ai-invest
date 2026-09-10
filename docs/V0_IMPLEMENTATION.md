# Working V0 Implementation — Current Direction

**Current status:** The [PostgreSQL-backed CLI](POSTGRES_RUNTIME.md) now runs against encrypted persistent storage, with migration, RLS and restart evidence. Real PAPER connectivity still requires protected credential provisioning and real execution integration. Gate 2 NOT PASSED. No LIVE capability or unattended trading authorization. The first-slice record below is preserved as historical implementation context.

## Owner direction and preserved qualification

The owner explicitly deferred the synthetic --io-test command and requested priority for database/backend, actual Alpaca PAPER integration and market/account data, deterministic risk, execution/reconciliation, research and minimal usable UI. Code development toward that V0 is authorized; the earlier synthetic-only implementation restriction no longer describes the current product direction. This does not authorize unsafe credential handling, real-money trading, public application exposure, commercial use, or bypassing AGENTS.md.

The terminal candidate, tests, input/output design and every historical qualification artifact are preserved unchanged. No IO command, policy extension or installation is being pursued. Revisit it only if a concrete provisioning need cannot be met safely with simpler standard mechanisms, or before later secret-infrastructure work. Its former approval request is not the current work gate.

The successful finite observer milestone remains valid for its exact tested graph. Neither secret_entry_authorized nor runtime_crash_suppression_qualified is changed; neither becomes a general prerequisite to writing backend/UI code. Actual future secret-bearing processes still need appropriate protections. No Gate 2 criterion is silently marked passed.

## Implemented in this slice

| Component | Implementation | Evidence and present limit |
| --- | --- | --- |
| Database source | Transactional first migration for tenant, PAPER brokerage-account identity, portfolios, immutable trade proposals and append-only audit references; compound ownership FKs, one active PAPER portfolio per account, stopped defaults | Five tables explicitly request tde_heap; extension/access-method presence checked. FORCE RLS, no policies and no runtime grants mean default deny. Migration NOT APPLIED; no TDE/WAL/restore/SQL-runtime proof claimed. |
| Backend contracts | Strict scoped UUID/value types, BACKTEST/PAPER/SHADOW only, immutable exact-quantity DAY-limit intent, bounded decimal parsing, context-independent notional, canonical digest binding scope/payload/timestamps | Offline unit tests. An intent is data, not authenticated identity, financial eligibility or risk approval. No order can be submitted with this package. |
| Broker-facing transport | Execution-only read-only Alpaca PAPER account reader, literal HTTPS host/port/path, verified TLS, no redirect/proxy endpoint selection, expected broker-account identity check, bounded response, strict field projection, redacted repr/errors | Mocked HTTP tests; no real credentials or request. Requires trusted tenant/account binding, protected runtime and whole-operation deadline before actual account ingestion. |

The adapter uses the real [Alpaca account endpoint](https://docs.alpaca.markets/us/reference/getaccount-1), not a simulated account API. It has not contacted that endpoint. Dedicated paper credentials and paper destination must both be verified; a class name or key prefix is not credential provenance. Paper simulation limitations remain those of the [provider's paper environment](https://docs.alpaca.markets/us/docs/paper-trading).

The database requires the [tde_heap access method](https://docs.percona.com/pg-tde/index/table-access-method.html), with no ordinary-heap substitute. [PostgreSQL RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html) declarations do not constrain superuser/BYPASSRLS or replace trusted context. No insecure SET app.tenant_id policy, broad login, credential, extension/key initialization or sample tenant data is created by the migration. Future grants/policies must be tested against at least two tenants before real data. Only this exact source migration is excepted from the existing SQL-dump ignore rule.

The initial schema contains no broker secrets or raw provider account identifier. The provisioned connection mapping and expected provider identity must be persisted under the required protection in a later migration; the account projection omits that provider ID after validating it. No in-memory singleton tenant/account is used. A caller-supplied Scope object alone does not prove application authorization; authenticated repository/service boundaries remain to be implemented.

Decimal parser bounds are representation/safety bounds, not approved investment policy. No draft capital/position limits have been activated. SQL uses explicit scale/range checks without numeric typmods that would round before validation. Runtime database tests remain necessary to validate those checks and actual migration behavior.

## Practical next slices

1. Qualify/provision the required local encrypted PostgreSQL/TDE stack through an approved human secret boundary; add migration execution tests, trusted tenant access, repository transactions and authenticated backend routes. Continue building those paths against tests while runtime setup is pending; do not replace TDE with plaintext or SQLite for actual account data.
2. Complete the execution read worker: trusted connection-to-tenant binding, service identity, no-swap/core controls, whole-operation timeout, safe credential loading and audit/persistence. Add positions, market data and freshness/provenance using the actual provider contracts. Do not request credentials during code-only work.
3. Implement deterministic risk and account-level reservations, immutable approvals, durable order intents, single-use dispatch, UNKNOWN reconciliation, idempotent fills and stop races. Test against a simulator, then explicitly human-triggered PAPER contract tests. No generic order method before these controls.
4. Add persistent research and the minimal private-access UI: balances/positions with timestamps, evidence/thesis, proposal/risk outcome, order/reconciliation history and stop control. Models receive minimized facts, never credentials or provider identifiers.

This is the requested working V0 direction, not a claim these later slices are already complete. No full product, deterministic risk engine, execution/reconciliation engine, market-data ingestion, research workflow or UI is claimed from the current foundation.

## Credential provisioning, when actually needed

Use the simplest standard mechanism that satisfies the remaining security requirements: prefer an execution-only OS/service-managed credential file or descriptor/reference over a custom interactive service. Do not choose or install a provisioning mechanism prematurely. OpenBao remains the preferred secrets platform in the design, but it is not a reason to resume --io-test merely to continue application coding.

Before actual provisioning, verify where credentials persist, who can read them, rotation/removal, encrypted-at-rest handling, process no-swap/core protection, clean startup/TLS configuration and absence of I/O/debug/exception-local logging. Ordinary application configuration may contain references, never raw keys. Human enters actual PAPER credentials outside assistant-controlled sessions; no argv, environment files, shell history, browser input field, model prompt, Git, CI or general logs. No real value is requested in this amendment.

The reader deliberately has no provisioning CLI or general URL/command input. Only the isolated execution component may hold credentials, even for account reads. Broker account matching prevents attaching a returned snapshot to the wrong expected provider account, but authentication and trusted stored ownership must still supply that binding. It is not safe to expose this library directly as an unauthenticated API.

TLS uses an explicit verifying client context and the Ubuntu system CA bundle, not environment-selected roots or Python's SSLKEYLOGFILE-enabled default-context helper. HTTP debug logging is disabled before the request. Redacted repr/error strings do not make raw object serialization, traceback-local capture or generic request logging safe.

The socket timeout is five seconds per blocking operation, **not a total DNS/header/body deadline**. A bounded execution-worker supervisor is a required next integration step before supplying credentials. There is no deployed worker in this slice. Do not run the library ad hoc with real keys to bypass that requirement.

## Validation and review

Run from the repository root; standard-library tests require no services, dependencies or credentials:

```bash
/usr/bin/python3 -B -m unittest discover -s tests/v0 -v
/usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q
```

Author results: 31 new offline V0 tests PASS; all 282 existing qualification tests PASS, including 72 native journal fixture cases. Database tests inspect migration structure only; no PostgreSQL process or SQL execution occurred. All HTTP interactions are doubles; no credentials or broker requests occurred. New TLS tests create only an owned temporary fixture directory and prove no key-log file is created. Existing IO tests remain preserved, not installed or promoted.

[Independent security/financial review](reviews/V0_FOUNDATION_REVIEW.md) challenged UTC canonicalization, migration tracking, TLS environment/key logging, scope binding and deadline claims. Findings corrected in this slice have permanent regressions. Unimplemented runtime/authorization/encryption gates are explicitly not replaced with static checks.

No services installed/deployed, LUKS/OpenBao initialized, real keys or brokerage credentials generated, actual account/market data read, order submitted, public listener created, existing workload modified, paid service enabled, or PR merged. The initial source/migration is reversible through ordinary source review; there is no applied database state to roll back. PR #14 remains draft and Gate 2 remains NOT PASSED.
