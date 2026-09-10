# Running PostgreSQL V0

Status: deployed, private/local only. PostgreSQL-backed **disconnected synthetic** trading works. Actual Alpaca PAPER connectivity is not yet delivered. Gate 2 NOT PASSED; `secret_entry_authorized=false` and `runtime_crash_suppression_qualified=false` remain unchanged. The owner's narrow approval authorized the development local TDE keys, not a general secret-bootstrap or LIVE gate.

## Use the application now

From the existing checkout, with the dedicated encrypted filesystem mounted:

```bash
cd /home/rob/ai-invest
docker compose -f infrastructure/application/compose.yaml run --rm --no-deps cli status
docker compose -f infrastructure/application/compose.yaml run --rm --no-deps cli recover
docker compose -f infrastructure/application/compose.yaml run --rm --no-deps --user 10002:26 cli status
```

Tenant A currently has one synthetic FILLED order, one fill, $189.995 cash, 0.5 units, no reservation, six audit events and exactly one simulated submission. Tenant B remains empty with $200 synthetic cash. No quoted value is market/account data. `recover` is repeatable reconciliation, not another order attempt. `stop` records a durable stop. `isolation` runs the bounded tenant-access assertions. `exercise` is only for an unused synthetic tenant and intentionally leaves UNKNOWN after a process exit; it refuses existing trade state. Do not reset data to repeat it.

To start the existing database after a planned stop (not initialize it):

```bash
docker compose -f infrastructure/postgres/compose.yaml --profile manual-database up -d postgres
```

For source rebuilds only: `/bin/bash scripts/build_postgres_runtime.sh`. It compiles the reviewed native guard and builds the two images; it does not start services, access runtime state or initialize keys. PostgreSQL must use its reviewed guarded image. Never bypass the preload, run arbitrary entrypoints against the key mount, rerun `initdb`, blindly rerun migrations/seeding, or replace the keyring. Existing bootstrap modes are controlled engineering operations, not an end-user initialization interface.

## Actual deployment evidence

| Check | Observed result / precise scope |
| --- | --- |
| Storage | Dedicated ext4 LUKS2 mapper mounted at `/srv/ai-invest-secure`, nosuid/nodev/noexec; service leaves verified UID/GID26 with restrictive modes before initialization. Prior directory setup result preserved. |
| Stack | PostgreSQL17.11 / Percona17.11.1; pg_tde package2.2.2, SQL extension version **2.2**. Percona upstream image pinned by digest in the Dockerfile. Application Python3.12, psycopg/psycopg-binary3.3.5, typing-extensions4.16.0. |
| Initialization | `initdb` with page checksums, peer local authentication and rejected network authentication completed. Empty-cluster metadata bootstrap temporarily used WAL encryption off to configure keys; no application rows were written in that phase. |
| Keys | PostgreSQL generated data/default and dedicated WAL principal keys internally through the approved file provider. Keyring is outside PGDATA, entirely on encrypted storage. No actual key bytes, reversible representation or key digest was returned. Two exclusive mode0600 recovery copies were internally byte-compared and fsynced. |
| TDE | All10 intended application/probe tables reported encrypted and FORCE RLS; all12 indexes reported encrypted. Synthetic probe exercised heap, primary index, TOAST heap and TOAST index. Known public marker readable through SQL, absent in those four raw relation files. |
| WAL | Final `pg_tde.wal_encrypt=on`, functional server/default keys, bounded synthetic write interval decoded by `pg_tde_waldump` with key-provider access; identical interval refused without it. Repeated after restart. This is runtime differential evidence, not merely a config check. |
| Runtime | Constructor checks bounded memory/CPU/tasks, cgroup swap.max=0/current=0, zero core limits, non-dumpable state and no-new-privileges before guarded executable entry. Actual native fork/crash probe passed. Seven PostgreSQL processes observed with zero core limits and root-owned protected proc metadata; no environment contents read. |
| Migration/persistence | Migrations0001/0002 applied;0003 added the disconnected broker fixture. Two fixed tenant peer roles provisioned. Existing PostgresLedger now performs real psycopg transactions: immutable-intent payload/digest, risk, reservation, order, fills, reconciliation and cash/position state in bounded JSONB; atomic append-only revision snapshots in runtime_event. The foundation's normalized proposal/audit tables are not falsely claimed to be populated by this aggregate workflow. |
| RLS | Both UIDs10001/10002 authenticated as their exact peer login. Cross-tenant reads empty, cross-tenant updates zero, cross-tenant event inserts and forbidden role/mapping/event operations denied with SQLSTATE42501. Caller-set tenant GUC does not change session-user binding. |
| Application interruption | Separate application child committed UNKNOWN, broker acceptance/fill committed independently, then child exited75. One submission remained durable. |
| Database restart | After graceful PostgreSQL restart, new application process reconciled FILLED, one fill, five audit events, one submission. A subsequent durable stop created event6; PostgreSQL container SIGKILL and restart recovered state with six events and still one submission. No host reboot/unrelated process interruption. |
| Resource snapshot | Dedicated PostgreSQL container:25.64MiB/2GiB,0.03%CPU,7tasks at one observation. Not a sustained-load benchmark. |
| Review/tests | Independent [review](reviews/POSTGRES_RUNTIME_REVIEW.md),101 V0 +282 preserved qualification tests PASS. Offline mocks/source tests and native compile checks are distinct from the deployed trials above. |

## Protection and recovery limits

The local key provider is approved only for private single-host V0 PAPER development. Supported provider APIs retain the later OpenBao/KMS migration path. No OpenBao initialization occurred. Same-volume recovery copies guard against individual file loss, **not loss of the encrypted volume**; independently protected offline custody and a full backup/cold-restore drill remain necessary. No wrong-key/lost-key/PITR qualification is claimed.

TDE covers demonstrated relations/indexes/TOAST and new WAL; catalogs, prior bootstrap WAL, temporary files, configuration and logs additionally depend on LUKS. Do not claim every PGDATA byte is TDE ciphertext. [Percona WAL guidance](https://docs.percona.com/pg-tde/wal-encryption.html) describes additional archival/restore handling; archiving has not been enabled here.

Database network is none; application mounts only its Unix socket, never PGDATA, keyring or recovery copies. The two exact peer roles have no passwords, ownership, role memberships, superuser/BYPASSRLS or DDL authority. Tenant identity comes from `session_user`, not a caller assertion. Host root, Docker administrators, kernel, reviewed images/configuration and service-owned paths remain trusted. The aggregate runtime role can update its own ledger; immutable audit enforcement is not protection from root/database administrators or a complete independent audit service.

The native preload is fixed image code, not caller-supplied configuration. The actual loader/constructor and proc checks support this trusted deployment; the fork/core-status probe is **not** universal collector-retention proof. Previous observer/input-output qualification, failures and deferred candidate remain untouched. All future credential holders and executable transitions still need their actual protections established.

## Corrections preserved

Repository validation:150 source files,255 prior reachable Git-history blobs,88 Markdown documents and359 local links passed existing common-secret-pattern/link/fence checks. Both Compose configurations passed. Full Mermaid rendering and dedicated SAST/dependency/container scanners were unavailable/not run; no equivalent assurance is claimed. Runtime keys/copies are outside the repository and were never included in build contexts or scan output.

- Initial guard build required a GLIBC2.38 symbol unavailable in the RHEL-based image. It failed before key generation; bounded manual parsing removed the dependency. Permanent ABI regression added.
- Application image initially tried to create already-existing Debian GID26; build refused. Reuses that group numerically now; no host group changed.
- Initial validation incorrectly equated package2.2.2 with SQL extension2.2. It failed at the version predicate, not encryption. Fixed to the observed SQL version; actual encrypted-byte/WAL tests then passed.
- Review requested directory-fd-relative recovery operations, destination prevalidation/source stability and exact authorization-denial SQLSTATE. Implemented and regression-tested. An offline seed-test fixture initially used a container-only path; corrected without changing the production path.

## Next real PAPER boundary

The existing execution-side adapter supports bounded account, positions, recent orders, clock and IEX quote reads with fixed HTTPS destinations, TLS validation and expected-account binding, but has not used credentials or made a real request. No actual order POST or LIVE endpoint exists. `/usr/bin/python3 -I -B scripts/v0.py paper-readiness` now checks the actual PostgreSQL CLI and reports the remaining credential/execution blockers; its Docker-client timeout is not a future credential-worker lifecycle guarantee.

Real PAPER credential entry remains a specific human-only handoff: an execution-only protected file/descriptor on this encrypted volume, restrictive ownership, no argv/environment/log/UI/model disclosure, and protection of every plaintext-holding process. A naive `docker run -it` prompt adds Docker-client/terminal/SSH plaintext holders not covered by the database constructor; it is not silently accepted as qualified. No new privilege grant, credential prompt, generic runner or --io-test installation was introduced. The next narrow decision is the protected PAPER provisioning path, followed by real account binding and read ingestion. Actual PAPER dispatch still additionally needs real-data risk eligibility, bounded execution/reconciliation and broker contract tests; it is not just one API key away.
