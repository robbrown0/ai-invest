# Independent Review — V0 Foundation Slice

**Status:** Reviewed for a foundation-only commit; not yet operationally qualified for deployment or credential use. No blocking finding remains for this limited, unwired source slice.
**Scope:** Unapplied database source, immutable trade-intent contracts, and an unwired read-only Alpaca PAPER account adapter. The reviewer did not author the implementation or tests; only this review document is reviewer-authored.

## Authority and evidence boundaries

The owner deferred `--io-test`; its candidate, historical evidence and tests remain preserved. This slice does not implement or install that command. The owner authorizes PAPER development and the simplest reasonably secure PAPER credential provisioning when needed. No renewed blanket PAPER approval or automatic return to the deferred IO-policy request is required by this review. Actual process/storage/credential safeguards remain implementation prerequisites, not a claim that this source-only slice already satisfies them. No real-money capability or Gate 2 passage follows.

Reviewed `AGENTS.md`, architecture/data/risk requirements, and the actual source in `backend/ai_invest_core/intents.py`, `backend/migrations/0001_tenant_foundation.sql`, `execution/ai_invest_execution/alpaca_paper.py`, and `tests/v0/test_foundations.py`. No database migration, broker request, credential provisioning, privileged checkpoint or service deployment was performed by this reviewer.

An immutable intent is data, not risk approval or authenticated tenant authority. FORCE RLS with no policies/grants is deny-by-default scaffolding, not demonstrated usable tenancy isolation. TDE access-method declarations are not encryption, WAL or recovery evidence. Mocked transport results do not establish Alpaca compatibility or connectivity.

## Findings

| ID | Finding | Disposition |
| --- | --- | --- |
| VF-01 | Accepted extreme timezone-aware timestamps could overflow later UTC canonicalization, producing an uncaught failure rather than an invalid-intent result. Independently reproduced using synthetic year-one timestamps. | Fixed: normalize representable standard-timezone timestamps at intake and reject overflow/underflow. Verified `test_utc_underflow_overflow_rejected_at_intake_reg_vf01`. |
| VF-02 | The security-conscious `*.sql` ignore rule hid the new reviewed source migration from ordinary staging. | Fixed: one exact source-migration exception; other dumps remain ignored. Verified `test_source_migration_not_ignored_but_dumps_still_ignored_reg_vf02`. |
| VF-03 | Default TLS trust construction depended on trust-store environment; a fixed destination alone did not qualify the whole execution process. | Fixed for trust-store selection: explicit system CA file and TLS context; hostile SSL_CERT_FILE/DIR regression passes. Trusted runtime/OpenSSL/code/CA configuration and clean process environment remain required. |
| VF-04 | The initial reader/snapshot did not bind expected provider account identity to its tenant/account scope. Removing broker identifiers from the projection did not establish that binding. | Fixed contract: require trusted Scope and expected provider UUID, compare broker response ID before returning scoped data. Mismatch/refusal regressions pass. This does not authenticate the caller or provision the trusted binding. |
| VF-05 | Socket timeout and response-size limits do not supply a whole-operation deadline against slow transport/DNS behavior. | Explicitly unqualified in module scope; bounded supervisor deadline needed before credential use. |
| VF-06 | Installed Python's `ssl.create_default_context` reads SSLKEYLOGFILE and can create a TLS session-key log even with an explicit CA file. Such a sink could expose request credentials with captured transport. Independently confirmed from installed library source without generating a key/log. | Fixed: explicit SSLContext(PROTOCOL_TLS_CLIENT), fixed CA load and verification/key-log invariants; default factory removed. Verified `test_tls_keylog_environment_cannot_create_sink_reg_vf06` leaves no file and no keylog filename under hostile environment input. |

Numeric SQL typmods were changed during implementation to unconstrained numeric plus explicit scale/range checks, avoiding a silent rounding-before-check claim. These are source checks only until PostgreSQL execution and adversarial tests exist.

## Independently executed tests

The reviewer independently reproduced VF-01 before correction and inspected the installed standard-library factory for VF-06. After corrections, independently executed:

```text
/usr/bin/python3 -B -m unittest discover -s tests/v0 -p 'test_*.py'
31 tests: PASS
/usr/bin/python3 -B -m unittest discover -s tests/qualification -p 'test_*.py'
282 tests: PASS
```

These 313 test cases combine mocked transport, local TLS-context creation, synthetic Python contracts, SQL/source assertions, and the existing isolated qualification/native-fixture checks. No real HTTP request, PostgreSQL execution, protected human-console checkpoint or secret entry occurred. The lead agent remains responsible for final staging, secret-pattern scans, commit and PR verification.

## Adversarial assessment

- Fixed literal HTTPS host, port, GET path, verified TLS context, no redirect following, no proxy-derived destination and no order method narrow the adapter. Same-process malicious Python/monkeypatching is outside this boundary; runtime identity and network isolation remain necessary.
- Credential constructors reject header-control characters; reprs redact financial/credential fields; ordinary exceptions suppress transport detail. Debugging with local-variable dumps, generic dataclass serialization, memory inspection or logging raw request objects is not safe and is not authorized by repr redaction.
- Advisory input cannot supply tenant/account/portfolio scope or execution flags. Exact numeric parsing rejects floats, non-finite values, exponent notation and excessive scale; independent Decimal context bounds multiplication. Application authentication, instrument eligibility, freshness, reservations and approval consumption remain unimplemented.
- Composite foreign keys bind the proposal to its tenant/portfolio/account tuple. All five tables request TDE and FORCE RLS without runtime policies or grants. A superuser/BYPASSRLS principal, table-owner DDL, TRUNCATE or trigger disabling is not contained by these declarations; future runtime roles must lack those authorities and be tested.
- Append-only triggers alone do not provide complete audit capture, externally anchored tamper evidence or durable execution reliability. There is no submission/reconciliation path in this slice.

## Required before operational use

Qualify the pinned TDE/key/storage/restore stack and trusted tenant access; build independently tested risk/execution/reconciliation controls; verify account/key ownership; establish a simple human-only credential provision mechanism outside Git, logs, UI, argv and model context; qualify execution no-swap/core/timeout/clean-environment protections. Do not automatically resurrect the deferred synthetic I/O command or substitute plaintext persistence for required encryption.

Final consistency review of [the current implementation direction](../V0_IMPLEMENTATION.md), root README and current operator routing confirmed that the first slice is not portrayed as a runnable application or renewed blanket-approval stop. Historical synthetic-only and IO-checkpoint records remain evidence, not the current coding work queue.

Market data, research workflow, authenticated backend routes and a usable UI remain follow-on work. This is not a complete working V0 or evidence of safe unattended PAPER operation. Both existing qualification authorization flags and Gate 2 remain unchanged.
