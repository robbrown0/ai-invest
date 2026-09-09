# Run the V0 CLI — Disconnected Milestone

**Status:** Runnable disconnected flow; the requested real Alpaca PAPER end-to-end milestone is NOT complete. Gate 2 NOT PASSED. Both qualification authorization flags remain false.

## Run now

No dependencies, containers, credentials, web ports or privileged commands are needed. From the checkout:

```bash
cd /home/rob/ai-invest
demo_root=$(mktemp -d /tmp/ai-invest-demo.XXXXXX)
/usr/bin/python3 -I -B scripts/v0.py demo --state-dir "$demo_root/state" exercise
/usr/bin/python3 -I -B scripts/v0.py demo --state-dir "$demo_root/state" audit
/usr/bin/python3 -I -B scripts/v0.py demo --state-dir "$demo_root/state" --tenant b status
```

The first command initializes a **new** private synthetic directory, reconciles/resumes a fixed $200 account, records an immutable BUY intent, evaluates risk and starts a separate CLI process. That child commits UNKNOWN before the outbound attempt, durably fills at the disconnected broker, and deliberately exits with status 75 before writing the application response. Another process reconciles the existing order. Re-dispatch of its ID must not send again. This is a userspace application exit, not a kernel/core/crash-collector experiment.

Expected final summary: DISCONNECTED_SYNTHETIC_ONLY; result process_crash_reconciled_without_resubmission; one broker submission; one FILLED order; cash 189.995; position 0.5; reservation 0; one fill; five durable audit transitions. Tenant B remains stopped with $200, no position/orders/audit. These are artificial amounts, not market prices or account data. Existing directories are never overwritten by exercise/init. Demo files remain available for inspection and subsequent commands; nothing is automatically deleted.

## Manual controls

Use `demo --state-dir "$demo_root/state"` before each action. `init` creates a fresh scenario. `reconcile` refreshes durable local/broker state; `resume` requires successful reconciliation and no active order; `stop` blocks new dispatch admission. `propose --quantity 0.5 --limit 20.01` returns a synthetic intent UUID. `submit UUID` evaluates and submits that exact intent. `status` and `audit` inspect results. All commands are explicit human invocations; no daemon/scheduler is installed.

For fault exercises, submit accepts only fixed synthetic choices `--fault timeout`, `--fault partial` or `--fault crash-after-accept`. `complete-fill` advances only existing synthetic fills. Reconcile after timeout/crash; never create a replacement intent to evade UNKNOWN. Cancel/expire/reject accounting branches exist but a broker-cancel command is not implemented. Commands have no import path, real symbol/account selector, credential option, URL or actual broker constructor. SQLite is exclusively the disconnected simulator's persistence, **not a substitute for PostgreSQL/TDE with actual account data**.

The initial demonstration permits BUY of one synthetic security only, no margin/short/options/extended-hours, DAY limit intent, $25 order ceiling, $120 position ceiling, $80 lifetime-demo turnover ceiling, cash/reservations, one active order, fresh bounded quote, bounded spread/price, expiry, digest binding and stops. It is named SYNTHETIC_V0_1 and is not an activated real-trading risk profile. Actual instrument eligibility, settled cash, daily loss/drawdown/calendar/fees and IEX coverage still require implementation before real PAPER submission.

## What is implemented versus connected

| Path | Current evidence / limit |
| --- | --- |
| CLI → intent → risk → durable admission → broker → fills/cash/positions → audit | Executed against the disconnected durable simulator, including real process restart and concurrent duplicate submissions. |
| PostgreSQL persistence | Unapplied second TDE migration and scoped account-aggregate/event transaction adapter; row lock, revision CAS and audit append in one transaction. Constructor refuses superuser/BYPASSRLS, role switching/membership, wrong tenant, table ownership or missing FORCE RLS/TDE metadata. No PostgreSQL driver/database execution or RLS runtime proof. Runtime roles/mapping/grants/seeds not provisioned. |
| Actual Alpaca PAPER reads | Account reader extended with positions, bounded recent orders, clock and IEX quote projections. Expected account binding checked before projection; fixed destinations; no redirects or environment TLS-key logging. Tests use HTTP doubles, not account connectivity. |
| Actual PAPER execution | NOT connected. No real order POST or credential provisioning command exposed. The runnable workflow rejects non-synthetic adapters/stores; it cannot quietly turn into a real PAPER dispatcher. |

Recent-order reads refuse a full 200-record page as incomplete; they are not complete history/fill reconciliation. Unknown/malformed data is refused. Free IEX quotes are single-venue observations, not consolidated market coverage. Per-operation socket timeout is not a whole-operation deadline. Protected process/service identity and a total deadline are still required before supplying credentials. Provider contracts: [orders](https://docs.alpaca.markets/us/reference/getallorders-1), [market-data coverage](https://docs.alpaca.markets/us/docs/market-data-faq), [account](https://docs.alpaca.markets/us/reference/getaccount-1).

## Concrete real-environment blocker

Read-only checks during this task found no `/srv/ai-invest-secure`, `/dev/mapper/ai-invest-qualification` or `/var/lib/ai-invest/qualification.luks`, no ai-invest-labelled Compose containers and no installed PostgreSQL client/driver. The existing plan preflight passed local capacity/locality checks: 464,299,520,000 bytes available; 395,580,043,264 expected after the proposed 64 GiB allocation. This is capacity evidence only. No volume, service or key was created. No unrelated workload/log/credential configuration was read or changed.

There is therefore no intended encrypted development database on which to safely apply either migration. Initial storage/key provisioning requires a human-only secret-bearing operation outside the assistant session under the existing protection requirements. That is the next required human dependency, before Alpaca credential entry. A reviewed executable secret-bootstrap procedure and the protected actual database/execution processes are not supplied by this slice; **do not run historical qualification blocks as bootstrap or send any secret in chat**. This task does not silently relax that boundary, generate a TDE key in ordinary storage, initialize LUKS/OpenBao, or resurrect --io-test.

The shortest path to real PAPER remains: establish dedicated encrypted storage and TDE keys through the human-only boundary; deploy/validate the isolated database, identity and migrations; qualify the actual execution process; provision execution-only PAPER credentials using standard protected OS/service credentials; then integrate actual risk/dispatch/reconciliation and run a human-triggered PAPER contract test. Ordinary application configuration holds references only. No secret belongs in argv, environment files, UI, logs, Git, CI or model context. Those implementation tasks remain work, not achievements hidden behind one missing API key.

`/usr/bin/python3 -I -B scripts/v0.py paper-readiness` reports these known implementation blockers and exits 2. It never asks for secrets or connects. It is not a new qualification framework or a claim to probe/attest a future deployment.

## Executed verification

- 59 V0 tests PASS: actual isolated SQLite transactions and separate CLI processes; mocked HTTP/PG contracts and earlier foundation regressions.
- All 282 existing qualification tests PASS, including the preserved terminal candidate and native journal fixtures; no privileged console trial repeated.
- Common-secret-pattern checks passed over 124 tracked/non-ignored working files, index content and reachable Git history; matching values suppressed. Markdown/link checks passed. Dedicated secret/SAST/container scanners are not installed; no equivalent full-scanner claim is made.
- Actual one-command exercise, separate audit command and tenant-B status executed successfully with the expected summary above. Data persisted after the child exit; re-reading it is not another crash trial. No host reboot or power-loss/fsync hardware guarantee claimed.
- Independent review found and corrected Decimal expansion (RV-01), untrusted reconciliation field/identity overwrite (RV-02), and reviewed the implementation-found quote-clock ordering regression (RV-03). See [review and disposition](reviews/RUNNABLE_V0_REVIEW.md).

The PostgreSQL JSONB aggregate is a bounded first persistence primitive, not normalized analytics or a complete audit/security separation design. Events are immutable through supported application operations/triggers, not against the database owner/root. SQLite directory-write trust assumes the local user is not compromised. No database/credential/runtime-release assurance follows from mock or source tests. Research/UI beyond this CLI, automated scheduling and outside-user access are not delivered.
