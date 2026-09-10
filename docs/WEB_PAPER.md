# Web-first PAPER onboarding

**Current owner direction:** [the HTTP LAN shell](LAN_V0.md) is now deployed. TLS and certificate automation are deferred. The HTTPS onboarding implementation below remains preserved/stopped; no credential entry, stored financial view or approval is exposed in the HTTP shell.

Status: implemented and isolated-test validated; **not yet LAN-deployed or connected to Alpaca**. The owner changed normal onboarding to browser-first. The CLI remains a disconnected simulator/administrative tool, not the credential-entry experience. Gate 2 remains NOT PASSED; both qualification authorization flags remain false. The deferred synthetic `--io-test` candidate is unchanged.

## User workflow

Open the private HTTPS application from an enrolled trusted desktop/iPad/iPhone → **Connect Alpaca PAPER** → enter dedicated PAPER key and secret → backend validates the account → see account cash/equity, positions, recent orders and an optional SPY IEX quote. Refresh is explicit; observations display timestamps. A missing market-data entitlement does not fabricate a quote. Recent orders are not complete fill reconciliation.

Select an existing connection to replace credentials. The candidate must validate against the same PAPER account before replacing the active reference. Disconnect durably removes local authority, then removes its credential file. It does **not** revoke the key remotely or cancel orders: the screen links to Alpaca for revocation/regeneration. No stored secret or API key is returned to the browser. Failed replacement preserves the existing active reference. A broker-side key rotation can independently invalidate the old key; the application cannot undo that.

The next implementation remains proposal → deterministic risk → web approval → PAPER dispatch/reconciliation. This gateway has **no order POST, LIVE endpoint, automatic scheduler or AI execution**. The placeholder button is disabled. Existing simulated execution is not presented as a real broker connection.

## Current deployment boundary

TLS terminates directly in the execution-owned gateway, not a general backend/reverse proxy or model process. Initial access uses TLS 1.3 client certificates with a server-controlled fingerprint allowlist. One execution process/peer role is bound to one tenant; multiple PAPER connections are supported per tenant. Certificate enrollment is a one-time administrator prerequisite, not CLI onboarding of brokerage keys. See [the interim draft ADR](ADR/ADR-0011-private-web-paper-onboarding.md) and [independent review](reviews/WEB_V0_SECURITY_REVIEW.md). Outside users and public application exposure are not authorized.

The actual LAN hostname/address and browser-trusted server/client TLS provisioning are **not yet established**. Do not bypass certificate verification or open a public listener to work around that. Compose currently binds **127.0.0.1:8443 only** and has not been started. An exact private-interface binding and certificate SAN/origin must be configured together after the owner supplies the intended name. No private key or credential should be sent to an assistant.

Prepared execution mounts, all inside the dedicated encrypted filesystem:

| Host runtime leaf | Owner / mode | Gateway access |
| --- | --- | --- |
| `paper-credentials` | UID10003:GID26 / 0700 | Read/write; exclusive 0600 credential-version files |
| `web-tls` | UID10003:GID26 / 0700 | Read-only; `server.crt`, `server.key`, `client-ca.crt`, each 0600 |
| `web-policy` | UID0:GID26 / 0750 | Read-only; root-owned non-writable `web.json` |
| Existing `postgres-socket` | Existing protected database ownership | Socket only; no PGDATA/keyring mount |

`web.json` contains only an exact HTTPS origin on port8443 and 1–16 enrolled certificate SHA256 fingerprints (`origin` and `clients` keys). It never contains a broker key, TLS private key or tenant chosen by the browser. Fingerprints bind authenticated devices to the service tenant; they are not bearer credentials. Future additional tenants require distinct peer identities/processes, not an arbitrary request tenant header.

The protected service applies a fixed native pre-main guard, isolated Python, no-new-privileges, no capabilities, core0, non-dumpable state, 512MiB memory/no container swap, 1 CPU and 32 tasks. It verifies encrypted mount metadata before TLS-key loading. No research/model service receives the credential directory. Fixed asynchronous HTTPS GET destinations use verified TLS, no redirects/proxies, bounded responses and deadlines. Application destination restrictions are **not** a network egress firewall.

## One non-secret directory preparation

This command is prepared and reviewed, **not executed by the agent**. It verifies both source dependencies and creates only three empty protected directories. It generates no certificate/key/credential and starts no listener. From the trusted checkout over SSH:

```bash
cd /home/rob/ai-invest &&
printf '%s\n' \
  'a6b15eb11284b7be846e1fc925a89f4df039ffcf1b4a71451ad9f7c63c9630bf  scripts/setup_web_dirs.py' \
  'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706  scripts/setup_postgres_dirs.py' | sha256sum --check - &&
sudo /usr/bin/python3 -I -B /home/rob/ai-invest/scripts/setup_web_dirs.py
```

Expected bounded result: `directories_ready=true`, `credentials_created=false`, `tls_created=false`, `web_started=false`, `gate2_passed=false`. Existing nonempty/unexpected paths cause refusal; no destructive reset. This is not sufficient to start the web service. The next handoff must provision the agreed TLS trust on the protected server and enrolled devices without exposing private keys, install the root-owned non-secret policy, validate actual service protections and publish only the agreed private interface. Never paste an API key into a shell, Compose file or chat.

## Evidence actually obtained

- Migration0004 applied to the existing isolated PostgreSQL instance: dedicated peer role, tenant, TDE connection/event tables, FORCE RLS and append-only events. No production data or credentials were inserted.
- Real database test using UID10003 verified save/refresh/disconnect transactions and three events, denied cross-tenant INSERT and audit/role/identity-map mutation, then rolled back all synthetic test rows. The empty foreign-row query is **not** proof of read isolation against a known foreign record; that new-table sentinel exercise remains outstanding. Existing two-tenant simulator isolation evidence is preserved separately.
- Existing database-backed simulator recovered after the scoped database image update: one FILLED order, one fill, six audit events and exactly one simulated submission. No resubmission.
- **408 automated tests passed:** 104 V0, 282 preserved qualification and 22 web tests. Web tests use actual isolated local TLS/HTTP and temporary test-only certificates, but fake broker/database responses. Directory tests and refusal of an interactive PEM-password fallback mock metadata/library calls. These are not a real Alpaca or protected-human onboarding trial.
- Independent reviewer reproduced web21/setup3 and additional storage tests; partial-write cleanup, zero-row transaction and UID/GID bugs were fixed with regressions. See review for residual limitations.
- Common-secret-pattern scans passed over working/staged source and reachable Git history; Markdown/link/fence checks, JavaScript syntax and Compose validation passed. Dedicated SAST/dependency/container scanners and full Mermaid rendering were unavailable/not run; no equivalent assurance is claimed. This slice does not add a CI workflow.

## Credential handling and remaining limits

The trusted browser transiently holds entered values, with echo masked, no application storage/cookies/analytics, no-store responses and clearing on submit/page changes. Browser/OS compromise, extensions, password-manager behavior, input methods, memory copies and guaranteed JavaScript zeroization are outside that assurance; use an enrolled trusted device and decline saving keys. Server cgroup checks do not qualify client memory or kernel buffers.

The execution process immediately writes a protected immutable candidate file before broker validation, then atomically commits the active file reference and audit event. SQL receives only the reference and allowlisted account observations, never the credential bytes. Definite failed candidates are removed; ambiguous commit outcomes retain the possibly active protected file rather than deleting it. A 32-file cap bounds accumulation; protected orphan recovery needs an operator procedure before substantial use. Logs, transport error bodies and credential diagnostics are suppressed rather than echoed.

Deployment still requires trusted TLS/device enrollment, the protected directories, exact LAN origin/binding, actual startup/control verification and a human browser credential submission. Failed-auth/provision audit coverage, comprehensive new-table foreign-row tests, client revocation/recovery, whole-volume cold recovery, actual PAPER risk/dispatch/reconciliation and device testing remain incomplete. No full crash-retention proof for this different TLS process or Gate 2 passage follows from local tests. No real secrets were provisioned in this change.

References: [Alpaca authentication](https://docs.alpaca.markets/us/docs/authentication), [aiohttp server](https://docs.aiohttp.org/en/stable/web_reference.html), [aiohttp client](https://docs.aiohttp.org/en/stable/client_reference.html).
