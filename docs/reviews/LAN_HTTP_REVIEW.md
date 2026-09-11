# Independent LAN HTTP review

Status: no blocking source finding remains for the scoped HTTP workspace; deployment evidence is recorded separately.

The reviewer did not author the LAN implementation. Scope is the owner's explicitly authorized HTTP-only, public-symbol V0 workspace, not approval for HTTP credential onboarding or trading.

## Findings and disposition

- **Deployment blocker found and fixed:** the new image copied the native guard without making it readable by UID10004. An independent isolated run printed the loader's fixed preload failure; ten HTTP tests passed without that protection. Those initial results prove application behavior only, not protected startup. The author restored the existing explicit 0444 guard mode and added a permanent loaded-guard/no-swap regression. The reviewer independently reran the fixed image: all eleven tests passed, including native guard state and effective memory.swap.max/current both zero.
- The reviewer requested a direct assertion that forbidden credential routes do not call the request-body reader. The author added it; the independent ten-test run includes that assertion.
- No other blocking source defect was identified in the reviewed HTTP boundary. This is not approval of future credential, account-data, approval or execution routes.

## Boundary checked

The HTTP image copies only the new shell, its separate static assets and fixed startup code; it does not contain the execution package. Its only protected host mount is the PostgreSQL socket. The peer-authenticated health role has no application-schema grant, tenant mapping, role memberships or brokerage authority. The status SQL is literal and returns bounded health labels rather than account state. The existing TLS execution gateway, credential mounts and authentication policy are unchanged and are not enabled by this deployment.

The configured bind must be an RFC1918 IPv4 address. HTTP checks the exact Host, a same-/24 source address and the exact POST Origin, rejects proxy/authentication/cookie headers and query strings, and has no credential form or credential/order route. Forbidden routes are rejected before body parsing. These are access-scope defenses, not authentication or confidentiality. LAN peers and a malicious network intermediary remain inside the explicitly accepted HTTP threat boundary. Binding to a private interface does not independently establish the router's forwarding/VPN configuration.

Research accepts one of four fixed public symbols, not arbitrary prompts, URLs or account data. One bounded request runs at a time with a cooldown, finite input/output sizes and deadlines. The model has an internal-only network, no published port, no brokerage/data/key mount, no tool invocation and read-only public weights. Responses are strict bounded strings rendered with textContent; output is unverified WATCH_ONLY with execution blocked. Instructions cannot guarantee that every generated sentence is a question or accurate: displayed warnings and the absence of execution authority are material controls. This is a research checklist, not validated predictive investment research.

## Independent checks actually executed

- JavaScript/Python syntax and Compose schema validation: PASS at the reviewed source snapshot.
- Ten isolated application tests: PASS, actual local HTTP with fake database/model and synthetic addresses; no production mounts or external network. The first run exposed the preload issue above and must not be described as guarded runtime evidence.
- Fixed image `sha256:c21e190378cdd65495394f9dc6b32253aefedbb615a8d070b680a0da72ea7e05`: eleven independent tests PASS with the loaded guard, UID10004, read-only root, no network, no capabilities, no-new-privileges, 256MiB memory/no swap, half CPU, 32 PIDs and core0. Actual HTTP tests still use fake model/database, not the deployed LAN or real inference.
- Source review of PUBLIC/schema grants, peer identity, native-control delta (only the new UID), fixed model destinations, static DOM sinks, read-only mounts, exact host publication and disabled credential/execution paths.
- Reviewed the separate actual-database test: literal SELECT LIMIT0 probes and SET ROLE must fail specifically with insufficient privilege, rather than accepting any connection/SQL error as isolation evidence. No account row values are selected.

## Remaining limits

Actual host health-role denials, effective model memory/swap/CPU/PID limits, real local inference, interface publication and loaded native guard require runtime evidence. No real credentials, TLS certificate, broker call, model capability evaluation or mobile-device interaction was performed by this review. No universal crash-retention or secret-handling claim transfers to the model process. Unauthenticated public-symbol results are ephemeral and not a private persistent tenant research history. Future account display requires protected access, and consequential recommendations/orders still require durable provenance and deterministic risk/approval controls.

Gate 2 remains NOT PASSED; both qualification authorization flags remain false.
