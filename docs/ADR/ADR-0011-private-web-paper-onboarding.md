# ADR-0011: Private web-first PAPER credential onboarding

## Status

DRAFT — owner explicitly requested web-first provisioning; interim identity/deployment details remain reviewable. This does not accept or supersede all future identity/KMS decisions or pass Gate 2.

## Date

2026-09-09

## Context

Normal users must connect Alpaca PAPER from a private TLS web interface, not a CLI. Only execution may hold brokerage authorization. Local encrypted storage and PostgreSQL/TDE already exist; real web credentials do not.

## Decision

Implement a small execution-owned direct-TLS gateway with transient browser input, protected local versioned credential files and transactional tenant-scoped references/events. Use an interim client-certificate identity allowlist mapped to a fixed peer-role tenant, isolated processes for additional tenants, exact origin/CSRF validation and no public listener. Server/client certificate enrollment must precede deployment. No LIVE or order operation is implemented in this slice.

## Alternatives Considered

- CLI provisioning: administrative fallback only; conflicts with requested normal UX.
- Unauthenticated LAN form: rejected; LAN membership is not user authorization.
- Full OIDC deployment now: retains the long-term identity direction but adds immediate services/bootstrap; not required for this small owner-device read milestone.
- TLS reverse proxy: useful later, but introduces another credential-plaintext holder to protect. Direct execution-owned termination keeps this initial boundary explicit.

## Security Impact

The browser is authorized to hold manually entered PAPER credentials transiently during provisioning, never retrieve stored secrets. Only the execution gateway handles them server-side. Device trust and certificate custody remain necessary; no claim of fresh human presence, uncompromised browser memory or production identity assurance. File storage on the approved encrypted V0 volume is a scoped development arrangement, not future LIVE/commercial KMS approval.

## Operational Impact

One-time trusted device/TLS enrollment and a root-owned origin/fingerprint policy are required. Read-only image/root, dedicated encrypted mounts, no-swap/core protections and explicit private binding are startup prerequisites. Local disconnect does not remotely revoke broker keys. No OpenBao, new generic privileged runner or --io-test installation.

## Consequences

Web onboarding and account display can precede risk/order UI implementation. Outside-user authentication/recovery, external secrets management, failed-auth auditing and actual execution controls remain future work. [Implementation and test limits](../WEB_PAPER.md) must stay distinct from a real connected deployment.
