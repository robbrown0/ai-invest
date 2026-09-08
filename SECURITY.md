# Security Policy

## Experimental scope

ai-invest is experimental financial/AI research software, currently design/bootstrap documentation only. Initial development is PAPER/synthetic only; BACKTEST and SHADOW cannot submit brokerage orders. No real-money capability or supported production release exists. Do not deploy this project to manage real funds.

The source repository is public. The proposed V0 application remains private-access/LAN-only; public source does not authorize public application exposure or weaken tenant isolation, authentication or execution controls.

## Report vulnerabilities privately

Please report security vulnerabilities responsibly through [GitHub private vulnerability reporting](https://github.com/robbrown0/ai-invest/security/advisories/new). This feature is enabled for this repository. Sign in to GitHub and use the repository's Security tab, then Report a vulnerability, to send a private report to maintainers. See [GitHub's reporting instructions](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/privately-reporting-a-security-vulnerability).

Do not open public issues, discussions, pull requests or comments containing exploitable vulnerabilities, exploitation details, secrets, credentials, PII or financial account information. Coordinate disclosure with maintainers before making exploitable details public.

Provide a sanitized description, affected commit/document/component, likely impact and minimal reproduction using synthetic data. Never attach real credentials, account identifiers, personal financial information or unredacted logs, even to a private report. No real brokerage credentials belong in GitHub issues, discussions, pull requests, advisories, attachments or repository content.

If GitHub private reporting is unavailable, do not fall back to a public vulnerability report. A working private reporting mechanism must be established before production use. No alternative email address or response-time guarantee is currently established.

## Safe investigation and exposure response

Test only systems you own or are explicitly authorized to assess, with synthetic data and no real-money trading. Do not probe the owner's host, unrelated services, other tenants or brokerage infrastructure.

If a credential may have been exposed, its owner should revoke or rotate it through the issuer's secure interface and investigate affected access; deleting a GitHub comment or commit does not invalidate a credential or erase copies. Report only sanitized facts through the private path, never the credential itself.

Maintainers must triage reports, restrict access, preserve sanitized evidence and coordinate remediation and disclosure. Critical/High security findings block release. Financial, authorization, tenancy, security and model-safety defects require regression tests when functionality exists. The project does not claim production readiness or regulatory compliance.
