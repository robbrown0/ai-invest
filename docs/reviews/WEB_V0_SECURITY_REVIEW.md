# V0 PAPER web onboarding — independent security review

Scope: execution-owned direct-TLS gateway, browser onboarding/dashboard, local protected credential files, migration `0004`, image/Compose boundaries and the non-secret directory helper. The reviewer did not author these controls. This is private single-host PAPER development, not authorization for orders, outside users, LIVE or Gate 2 passage.

## Disposition

The corrected implementation is suitable for the isolated read-only web milestone and controlled deployment preparation. Real credential use still requires trusted server/client TLS provisioning, exact origin and client-certificate policy, protected directories, applied/validated database role and migration, and effective runtime protections. No production TLS identity or brokerage credential was supplied to this review. The deployment currently publishes loopback only; changing that to a specific private LAN interface requires the intended TLS name and host exposure to be established first.

The new database migration may be applied within the existing isolated PostgreSQL scope: it is transactional, creates only its dedicated non-owner/no-bypass peer role and tenant, uses TDE and FORCE RLS, and grants no identity-map writes, role membership or audit mutation. No credential value is stored in SQL. The real-database fixture is synthetic and rolls back its own writes; it must not run over existing owner connection data.

## Findings and corrections

- **REG-WEB01:** a partial credential-file write could leave an unpublished file that the caller could not identify for cleanup. Definite pre-publication failures now remove that file. Ambiguous database commits deliberately preserve the possibly active protected candidate. A fixed directory-entry cap bounds candidate accumulation; resolving protected orphans remains an operator task, not automatic deletion of potentially active credentials.
- **REG-WEB02:** a conditional SQL mutation could affect zero rows yet append an event and advertise success. Save, disconnect and refresh now require exactly one affected row before their transaction can succeed.
- **REG-WEB03:** the first web-directory helper reused a validator requiring UID equal to GID, while creating the intended `10003:26` and `0:26` leaves. That would have failed after partial setup. A narrowly local leaf validator now checks the exact separate UID/GID; strict existing root-ancestor checks remain unchanged. A guarded human handoff must validate both the new script and its imported `setup_postgres_dirs.py` dependency.
- A query returning zero rows for another tenant is not read-isolation evidence unless a known other-tenant record exists. The initial real-database test lacked that sentinel. Cross-tenant INSERT refusal is meaningful; a complete read-isolation claim requires the known-foreign-row fixture, separately reported runtime execution and cleanup.

## Security boundary inspected

- TLS terminates directly in the protected execution-owned process. TLS 1.3, required client certificates, a fixed fingerprint allowlist, disabled tickets and rejection of resumed sessions authenticate the narrow service tenant. Exact Host/Origin checks, rejected forwarding claims and one-use short-lived certificate-bound CSRF tokens protect mutations. This is an interim certificate-based owner identity, not implemented OIDC, human-presence detection or a complete outside-user recovery platform.
- The browser has no third-party scripts, credential persistence, analytics, cookies or token URL parameters. Credential inputs are cleared and results use safe text rendering and no-store responses. A trusted browser/device, certificate custody and absence of hostile extensions remain assumptions. Server cgroup controls do not qualify browser memory, operating-system buffers or guaranteed JavaScript string erasure.
- Broker destinations and operations are fixed PAPER/data GETs; redirects, environment proxies and caller-selected URLs are absent. Request/dashboard/gateway deadlines and response limits bound network processing. No order endpoint or LIVE selection exists. Local disconnect removes the stored authorization reference; it does not revoke credentials at Alpaca or cancel orders.
- Credential files are exclusive-created, owner-only, tenant/connection-bound and opened relative to the protected directory descriptor. Reads reject unsafe types, links, permissions and observed mutation. Rotation validates the candidate/account before changing the active pointer and durable audit transaction. Operations are serialized locally and by a tenant-service PostgreSQL advisory lock.
- Native protection and encrypted-mount checks precede server private-key loading. TLS/policy metadata checks additionally rely on fixed read-only bind mounts and trusted host ownership; they are not protection against a malicious root administrator or deliberately concurrent host-side replacement. The gateway has neither PGDATA/TDE-key mounts nor a research/model execution path. Prepared directories and trust policy must not be installed by the agent as a privilege workaround.

## Independently executed evidence

- Four new Python entry/module files passed syntax parsing.
- Six isolated fake-credential file checks passed: round-trip, wrong tenant, hardlink, unsafe permissions, partial-write cleanup and removal.
- Three directory-setup regression tests passed, including the corrected UID/GID matrix. These mock metadata and never perform host setup.
- Twenty-one web tests passed in the guarded web image with no external network, a read-only root, bounded resources and disposable tmpfs fixtures. They exercise actual local TLS/HTTP with temporary test-only certificate material, but fake the broker and database. They do not establish real Alpaca connectivity or a successful protected human onboarding.
- `git diff --check` passed at review time. No real secret, runtime credential file or unrelated host state was read by the reviewer.

Remaining limitations include incomplete failed-authentication/provisioning audit coverage, manual client-identity revocation/recovery, no network-layer destination allowlist beyond fixed application transport, protected orphan handling, and future dispatch/risk/reconciliation controls. Do not describe this review as completion of those controls, a cold recovery trial, or assurance for every future secret-bearing process. Both qualification authorization flags and Gate 2 remain false/not passed.

## Final delta review

The final TLS loader supplies a refusing password callback, preventing OpenSSL from falling back to an interactive encrypted-PEM password prompt. Its focused regression confirms refusal without invoking input or proceeding to CA loading. The reviewer independently reran the final **22 web tests: PASS** in the same isolated no-external-network container setup. The CSRF local-variable rename does not change token generation or validation. Both source digests in the guarded directory handoff match the reviewed files.

The implementation author subsequently reported applying migration0004 and passing the rolled-back real PostgreSQL transaction/write-denial fixture, with TDE/FORCE RLS and WAL-encryption metadata confirmed. These are author-run observations, not additional independent runtime trials. Reporting now explicitly leaves `foreign_row_read=NOT_TESTED`, avoiding a false foreign-row absence claim. The documented simulator recovery remains distinct from real broker execution.

`WEB_PAPER.md` and draft ADR0011 correctly retain the missing exact LAN origin, trusted server/client TLS enrollment and human browser onboarding as deployment prerequisites. The service is not listening, has no actual brokerage credentials and implements no order endpoint. No new blocking source defect was found in this final delta; the disposition remains scoped implementation/deployment preparation, not approval to bypass those prerequisites or either qualification gate.
