# Independent Review — Runnable Disconnected V0 Slice

**Status:** Reviewed for the disconnected runnable milestone; no blocking finding remains in that limited scope after corrections. This is not authorization for actual account ingestion, credential use, TDE deployment or PAPER order submission.

## Scope and evidence boundary

The reviewer did not author the implementation or its tests. Reviewed AGENTS.md, the existing financial/data constraints, the prior foundation review, the new workflow, SQLite synthetic store/broker, unapplied PostgreSQL ledger migration/adapter, local CLI and expanded read-only PAPER adapter. Only this review document is reviewer-authored.

The owner requests a runnable real-PAPER milestone. The present slice is a smaller, explicitly disconnected runnable fallback while required encrypted storage/database and protected credential execution are unavailable. Its SQLite state is synthetic only, never an encrypted PostgreSQL substitute for actual account information. Strict concrete-type admission prevents attaching the current workflow to the PostgreSQL adapter or real PAPER reader through a configuration switch. This is a code boundary, not protection against malicious modification of the installed Python application.

The preserved --io-test candidate is not installed or extended. Its deferral is not Gate 2 passage. Neither authorization flag changes.

## Findings

| ID | Finding | Disposition |
| --- | --- | --- |
| RV-01 | Decimal JSON numbers can encode huge positive/negative exponents compactly. Formatting an unbounded Decimal before checking magnitude/scale can allocate far beyond the bounded HTTP response size. | Fixed: reject nonfinite, magnitude and exponent/scale violations before fixed-point formatting. Independently verified test_compact_decimal_expansion_refused_before_format_reg_rv01 prevents calling the formatter for compact oversized/undersized exponents. |
| RV-02 | Reconciliation indexed an observation by expected client ID but did not validate its embedded client ID or constrain observation keys before updating the durable order. An inconsistent record could replace authority fields. | Independently reproduced before correction with isolated synthetic state: a mismatched client ID and added approval_consumed=false on a zero-fill REJECTED observation yielded reconciled=true, stopped=false and changed binding. Fixed: exact observation fields and embedded client ID validation precede mutation. Independently verified test_client_identity_and_unexpected_update_fields_refused_reg_rv02 preserves binding/approval and stops on both cases. |
| RV-03 | The author found evaluation-clock sampling could precede the just-created synthetic quote, making a successful demonstration refuse its own quote as future data. | Fixed by sampling evaluation time after quote observation. Independently verified the permanent test_quote_evaluation_occurs_after_observation_reg_rv03. This is not a clock-synchronization claim for real feeds. |

An additional author correction makes normal state opening refuse missing/unrecognized demo databases instead of silently reinitializing missing state. The dedicated initialization path requires a fresh directory; the missing-database regression passes. No previously initialized data is automatically overwritten.

## Control assessment

- Immutable intent reconstruction verifies canonical fields and digest before dispatch. Account serialization commits the risk result, approval consumption, reservation and UNKNOWN order before the only broker attempt. An admitted request can complete after a stop; the implementation and test do not promise otherwise.
- Duplicate dispatch returns the durable existing state. A timeout, abrupt process exit or temporarily absent lookup does not authorize resubmission or release its reservation. Broker state and application state persist independently, allowing a distinct restarted process to reconcile the accepted order.
- Cumulative accounting validates quantities/value and matches explicit fill records. Missing/conflicting evidence latches a stop and leaves reconciliation incomplete. This is a deliberately narrow BUY-only fixed-security simulator, not real-market risk-policy qualification, a broker contract test or complete accounting for corrections/corporate actions.
- Parameterized PostgreSQL source serializes account state with FOR UPDATE and revision checks and appends events in the same transaction. Tenant selection derives from a restricted session_user mapping, not caller-set tenant variables. FORCE RLS/TDE declarations, role checks and source tests are not PostgreSQL runtime isolation/encryption evidence. No runtime grants are provisioned; a future operational role must also lack identity-map/DDL/trigger-disabling authority.
- The local demo requires owned private directories/files and refuses common symlink/hardlink/permission hazards. This is ordinary single-OS-user synthetic storage, not a boundary against that same OS user modifying files or code. SQL source and synthetic event triggers do not prove immutable archival or protection against database administrators.
- Read-only PAPER projections retain fixed HTTPS destinations, explicit TLS trust, bounded responses, expected-account checks and no POST method. Orders are a bounded recent projection, not complete reconciliation. Real credentials, full-operation deadlines, no-swap/core protections, account binding, encrypted state and actual provider compatibility remain unqualified; no real requests were made.

## Independent validation

Initial review independently ran 46 V0 tests and 282 preserved qualification tests successfully. V0 includes actual separate-process CLI crash/restart and concurrent-submit tests on isolated synthetic SQLite state, plus mocked HTTP/source checks. Existing qualification tests include their native fixtures; they are not new protected-console trials.

After corrections the reviewer independently ran:

```text
/usr/bin/python3 -B -m unittest discover -s tests/v0 -q
59 tests: PASS
/usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q
282 tests: PASS
```

The reviewer also executed the actual single-command exercise in a fresh owned temporary directory, independently of the author's run. It launched a synthetic submit child that exited with code 75 after durable broker acceptance, then a distinct reconciliation process. Result: FILLED, exactly one broker submission, cash 189.995, quantity 0.5, reservation zero and five durable audit transitions. Both qualification flags stayed false. The owned fixture directory was removed by the test's TemporaryDirectory cleanup; no real data was involved.

The exercise invokes the fixed local CLI using an absolute Python interpreter and isolated mode, no shell, no credential input and ten-second child timeouts. It refuses reuse of an existing directory and preserves partial state on failure for inspection. It does not contact Alpaca, apply PostgreSQL migrations or install privileged code. Source/mock tests for PostgreSQL and PAPER reads remain clearly distinct from the actual local synthetic execution.

The lead engineer performs final repository-wide scans, commit/push and PR state verification.

## Remaining operational blockers

The requested real connected milestone is not complete: encrypted PostgreSQL/TDE runtime and trusted DB roles have not been deployed/tested; actual secret-handling execution and safe human provisioning are not wired; the synthetic policy cannot approve a real broker order; no real POST/lookup/fill reconciliation, market eligibility/settlement checks or actual Alpaca end-to-end trial exists. A successful local demonstration does not waive any of these requirements or silently authorize LIVE capability.
