# Engineering Constitution

This file governs all work in this repository. Its requirements are non-negotiable unless an explicitly authorized human review approves a compliant amendment.

1. Never expose brokerage credentials, authentication tokens, encryption keys, or other secrets to an LLM.
2. An AI model must never communicate directly with a brokerage execution API.
3. All proposed trades must pass through a deterministic risk engine before reaching an execution service.
4. The execution service is the only application component that may eventually possess authorization to submit brokerage orders.
5. PAPER trading is the only permitted mode during initial development.
6. No agent, script, test, migration, deployment process, or AI component may switch an account into LIVE trading.
7. Any future transition to real-money trading must require an explicitly designed human authorization process.
8. Multi-tenancy must be treated as a core architectural requirement from the beginning.
9. Tenant isolation must eventually be enforced at both application and database layers.
10. PostgreSQL encryption at rest using TDE is a project requirement.
11. Sensitive values may require additional application-level envelope encryption even when TDE is enabled.
12. Secrets and primary encryption keys must not be stored in source control or directly in ordinary application configuration.
13. OpenBao is the initial preferred local secrets and key-management platform.
14. Every financial decision and trade workflow must be auditable.
15. Every trade proposal, risk evaluation, order, response, fill, rejection, and relevant model decision must eventually be reconstructable.
16. Every bug involving money movement, authorization, tenancy, or security must result in a regression test.
17. Security-sensitive code must receive independent review.
18. Critical and High severity security findings block release.
19. Prompt injection must be considered an untrusted-input security problem.
20. Internet-facing research components must never inherit brokerage execution authority.
21. Developers and AI agents must use least privilege.
22. Avoid unnecessary external paid services during initial development.
23. Local infrastructure and local inference should be preferred when practical.
24. Architecture must remain portable so local components can later be replaced by managed cloud services without redesigning the entire application.
25. Do not optimize prematurely for commercial scale, but do not introduce single-user assumptions into core data models or service boundaries.
26. Never commit secrets, private keys, tokens, account data, personal financial information, or production data to Git.
27. Tests must be added with functionality. Do not defer testing until the end of development.
28. Architecture decisions that materially affect security, data, tenancy, execution, or AI governance should be documented using ADRs.
29. Do not silently weaken a security requirement because implementation is inconvenient.
30. If a requested implementation conflicts with one of these rules, stop and identify the conflict rather than bypassing the rule.

`AGENTS.md` is a living engineering constitution. Changes that weaken financial, security, tenant-isolation, or audit controls require explicit human review.
