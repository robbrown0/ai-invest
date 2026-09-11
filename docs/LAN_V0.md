# Running the HTTP LAN workspace

## Professional workspace update

The running shell now has desktop/sidebar and mobile navigation for Dashboard,
Research, Opportunities, Portfolio, Orders, Strategies, Activity and System.
Live service health, structured local research questions, counterarguments,
missing evidence and safe loading/error states work. Unimplemented features are
explicit empty states, not fabricated account values, charts or rankings.
Activity is session-only; no browser persistent storage or analytics was added.

Real Chromium fixture checks passed 66 assertions across desktop, iPad-sized and
iPhone-sized viewports, including navigation, no horizontal overflow, inert text
rendering and no credential fields/cookies. Actual Apple-device testing remains
outstanding. The web service alone was rebuilt/restarted; the model and database
were not replaced. Current PAPER provisioning is [prepared here](PAPER_PROVISIONING.md),
not yet installed or exercised. The following original deployment record is
preserved as historical evidence; its no-financial-data HTTP boundary still applies.

Status: **deployed and responding on the owner-approved private IPv4 address, port8443, over HTTP**. Exact host binding is in ignored `infrastructure/lan/deployment.env`, not public source. No TLS, certificate enrollment/automation, public listener or credential provisioning was added. The earlier HTTPS gateway remains unchanged and stopped. Gate 2 NOT PASSED; both qualification authorization flags remain false.

## What works now

- Responsive LAN web shell: dashboard, live PostgreSQL/WAL-encryption health, local inference health and explicit connection/execution status.
- The Alpaca connection button is disabled with a secure-transport warning. There are **no key/secret input elements or HTTP credential endpoints**, and no stored account balances/positions are exposed. No broker credentials have been provisioned.
- Select SPY, AAPL, MSFT or NVDA and generate a local-model research checklist. It returns bull/bear questions, evidence needed, model/prompt provenance and a generation timestamp. No free-form prompt, URL, portfolio data or private note entry is accepted.
- Output is untrusted and source-free: no current prices/news are fetched, no confidence is calibrated, and the deterministic result is WATCH_ONLY / BLOCKED. These are research questions, not a demonstrated predictive strategy or an executable recommendation. They remain ephemeral and are not persisted as tenant research memory or trade proposals.
- No approval/order/reconciliation operation is exposed by HTTP. Existing disconnected simulator and protected execution code remain separate.

## Operate the current deployment

Normal use: open the HTTP URL provided in the completion report from the same LAN. Desktop/tablet/phone layout uses responsive controls; actual Safari/iPad/iPhone testing is still a human usability check.

From the checkout, these commands affect only the two new ai-invest LAN services:

```bash
docker compose --env-file infrastructure/lan/deployment.env -f infrastructure/lan/compose.yaml ps
docker compose --env-file infrastructure/lan/deployment.env -f infrastructure/lan/compose.yaml up -d
docker compose --env-file infrastructure/lan/deployment.env -f infrastructure/lan/compose.yaml restart web
docker compose --env-file infrastructure/lan/deployment.env -f infrastructure/lan/compose.yaml stop
```

Compose requires an explicit private IPv4 bind address; there is no all-interface fallback. The server independently checks exact Host, same /24 source subnet and POST Origin, rejects forwarding/auth/cookie claims, and supplies no-store/CSP headers. This is **LAN access filtering, not authenticated identity or encryption**. A LAN attacker, compromised router or TLS-free browser connection remains able to observe/tamper with traffic. No account/private content is permitted. Router forwarding/SNAT configuration has not been independently attested; never forward this port or attach a public proxy. No existing router, VPN, host firewall, global service or unrelated Docker workload was changed.

For another host, create the ignored non-secret deployment file with `AI_INVEST_LAN_ADDRESS` set to that host's reviewed RFC1918 IPv4 address. Provision only the documented public model artifact below and the existing protected database socket. Do not copy credentials or deployment inventory into source. This is a local V0 deployment, not a portable production installer.

## Isolation and local AI

The LAN image contains only its own HTTP module/static assets, not execution/broker modules. UID10004 authenticates to PostgreSQL as `ai_lan_status`, a new no-membership/no-bypass role with database CONNECT but **no application-schema/table privileges**. Its only application query reads database readiness and WAL-encryption status. No credential, PGDATA, TDE-key, TLS-key, Docker socket or research archive is mounted. The status image uses the existing native pre-main guard with unchanged protection thresholds.

Local inference uses the official CPU-only llama.cpp image pinned to `sha256:adcaa8dcf950de0a5c826e265d823b49d6426dec90b7c616e3ddbe6421e4dad2` (image revision `304665fe7ac957df95e3ff8c8c4ffdf92dd6ffa3`, b10868). The official Qwen3-0.6B Q8_0 GGUF is pinned to publisher revision `23749fefcc72300e3a2ad315e1317431b06b590a`, size639446688 and SHA256 `9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031`. It was downloaded over HTTPS and hash-verified before use. Weights are ignored local files under `data/models`, mounted read-only. They are public non-sensitive material, allowed outside critical encrypted runtime storage. No real key generation or Ollama/cloud identity bootstrap occurred.

Model: non-root UID10005, read-only root, capabilities dropped, no-new-privileges, core0, 2GiB/no-swap, one CPU,32 tasks, one model slot and2048-token context. No GPU device or model host port. Its only Docker network is internal with no Internet route; the API is not proxied to browsers. Only fixed public-symbol messages reach it. No tools, browsing, paid fallback, arbitrary provider/model selection or model download API is exposed. Public research output is schema/size checked and rendered with textContent. Source instructions are not treated as a security boundary: absent execution authority and secret access are the boundary.

HTTP: 256MiB/no-swap, half a CPU,32 tasks, logging disabled. Research: one in-flight request, bounded output256 tokens/16KiB,90-second model deadline and15-second post-completion cooldown. These bound host impact, not comprehensive denial-of-service prevention. A client disconnect/timeout can leave one bounded model generation completing; it cannot cause an order or start a retry loop.

Primary references: [llama.cpp Docker images](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md), [official Qwen model and Apache-2.0 model license](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/23749fefcc72300e3a2ad315e1317431b06b590a). This does not introduce a license for ai-invest source.

## Actual evidence and limits

| Check | Result |
| --- | --- |
| LAN host/address/port | Intended address exists; port free before deployment; exact-interface publish only. HTTP status and static page responded. No public bind/model port. |
| Database | Migration0005 applied; literal health query PASS; application-table SELECT and role-switch attempts denied42501. No account rows read. |
| Actual local AI path | HTTP POST of public SPY symbol → real local model → three validated questions → WATCH_ONLY/BLOCKED;3.8seconds in one trial. No external model API. |
| Effective web controls | Native guard=1; cgroup swap.max=0/current=0. |
| Effective model controls | Memory2147483648, swap.max=0/current=0, CPU100000/100000, pids32, soft/hard core0; internal network=true, no published ports or GPU devices. Not secret-process crash-retention qualification. |
| Resource snapshot after request | Web31.12MiB, model334.3MiB, database24.66MiB; each0%CPU at this idle observation. Not a sustained load benchmark. |
| Independent review | Initial image lacked read permission on native guard; corrected before deployment with chmod0444 and a permanent effective-load/no-swap regression. Independent final11 LAN tests PASS; see review. |

All **419 regression tests passed** (104 V0,282 existing qualification,22 preserved HTTPS-web,11 LAN). The actual deployed page/credential-route/order-route/Host/Origin checks passed; a scoped web restart returned database/model READY. Existing simulator recovery still reports exactly one fill/submission and six audit events. Working-tree/index/history common-secret-pattern checks, Markdown links/fences, JavaScript syntax and Compose validation passed. Dedicated SAST/dependency/container scanners and full Mermaid rendering were unavailable/not run; no substitute assurance is claimed. [Independent review](reviews/LAN_HTTP_REVIEW.md).

Tests use isolated actual HTTP with a fixture peer identity and fake database/model where stated; deployed health-role and local inference trials are separate actual evidence. Do not count repeated status retrievals as new independent qualification. The old TLS suite remains unchanged. Browser MITM protection, authenticated private data, actual Alpaca reads, persistent tenant research, genuine risk/proposal approval and PAPER dispatch/reconciliation are not delivered by this HTTP milestone.

Next: maintain this usable no-secret HTTP shell, then add safe execution-owned server-side PAPER credential provisioning and authenticated protection for financial views/actions. No such credential-entry command is installed yet; do not use an ad-hoc shell/environment/UI workaround. Add TLS only after separate owner authorization. Existing HTTPS capability is preserved for later use, not being deployed or redesigned now.
