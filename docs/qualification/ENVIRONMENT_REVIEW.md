# Independent Review — Bounded Environment Diagnostics

**Status:** Acceptable for the documented non-secret human checkpoint only; Gate 2 NOT PASSED.
**Date:** 2026-09-09.
**Reviewer:** Independent adversarial agent, separate from the implementation and upgrade-procedure author.

## Scope and evidence boundary

The reviewer read `AGENTS.md`, the current wrapper, existing qualification/security reviews, installed sudo environment documentation, the proposed [environment amendment](ENVIRONMENT_DIAGNOSTICS.md), [operator checkpoint](OPERATOR_CHECKPOINT.md), policy and regression tests. The reviewer did not author the implementation or upgrade transaction. This review is the reviewer's only repository edit in this amendment.

The human reports reaching `operator_environment` after installing the prior console-policy amendment. The specific failing environment predicate is still **UNKNOWN**. Neither a MAIL mismatch, an extra key, PATH mismatch nor any other cause is inferred. Prior failed results remain historical evidence. No actual privileged environment, variable list, environment values, session metadata, sudo logs, credentials or secret material was inspected or requested by the reviewer. No sudo authentication, installation, privileged scope or secret operation was performed.

## Independent challenges and dispositions

| ID | Challenge | Disposition |
| --- | --- | --- |
| ER-01 | The first upgrade rollback restored the wrapper before policy using one short-circuit chain. Wrapper-copy failure could prevent any attempt to recover a broken aggregate sudo policy. Existing tests assumed rollback always succeeded. | FIXED after independent challenge. Restore and validate the verified prior policy first; independently attempt wrapper restoration; report complete restoration only when both succeed. Permanent `test_policy_recovery_attempt_precedes_wrapper_failure_reg_er_01` injects failure into each rollback step after an activation failure. Partial recovery remains a refusal requiring human review. |
| ER-02 | Splitting a guard might silently normalize or broaden allowed environments. | No widening found. The same predicates are evaluated immediately in the same order. A direct comparison with committed baseline `41d4721e7d4ffaceba1033f0bd45717281d22977` agrees on all 107 synthetic fixtures. Incidental target-account expectations remain unchanged pending bounded runtime diagnosis. |
| ER-03 | Diagnostics could leak an unknown key name, value, raw exception or arbitrary path. | Ten fixed symbolic identifiers only. The exception constructor validates the closed identifier set and carries no message. Refinement applies only to diagnostic mode at the environment boundary; other exceptions remain coarse. Fixed-schema publication and both false authorization flags are regression-tested. |
| ER-04 | `env_reset`, `NOSETENV`, secure PATH or Python isolation could be misrepresented as exact environment attestation. | Documentation corrected/explicit: sudo's minimal environment is not the wrapper's exact keyset, and target-account/PAM/configured sources may affect it. Python `-I` ignores Python environment settings and user site imports, not all OS environment. Loader startup protection must precede a Python-level refusal. |
| ER-05 | Updating the installed policy could broaden the PTY exception, bypass fresh authentication, leave a partial active policy or require a new sudo invocation after breaking policy. | Policy change is digest only, verified against the committed baseline. The guarded human procedure preserves verified prior snapshots, stages under ignored filenames, uses same-directory atomic rename and retains authenticated root execution through validation/rollback. No new shell/installer grant is added. Concurrent root edits and interrupted two-file updates remain residuals. |
| ER-06 | A metadata diagnostic could be treated as permission for future sensitive bootstrap. | Both authorization flags remain false. Source equivalence and synthetic tests do not qualify the actual environment, effective protected cgroup, crash suppression, canary path or secret bootstrap. |

## Independently executed tests

Installed sudo/visudo documentation is version **1.9.15p5**, grammar **50**. Python is **3.12.3**. The reviewer read the installed `sudoers(5)` sections for environment reset, target-user initialization, PAM merging, `NOSETENV`, `secure_path` and keep/check lists, plus local Python isolation help. No command was used to dump an environment or query privileged runtime values.

The reviewer independently ran:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests/qualification -q
Ran 98 tests
OK
```

Zero skips. Earlier independent runs passed 94 and 97 tests before the additional upgrade-recovery regression. The final suite includes:

- Every fixed environment predicate, missing PATH/GID, unsupported keys, parser boundaries and first-failure precedence using synthetic fixtures only.
- Baseline acceptance equivalence, successful clean-child behavior, unknown-error fallback, forged diagnostic rejection and immutable false authorization flags.
- A real unprivileged Python `-I` subprocess supplied only synthetic Python settings; it reports isolation flags without displaying environment data.
- Seven inert upgrade control-flow cases and five additional rollback-failure cases extracted from the exact documented transaction. No actual install, rename, sudo or root operation runs in these tests.
- Existing console, identity, session, file-integrity, policy-scope, result-publication, no-swap/core predicate and diagnostic regressions.

The proposed policy also independently passes the installed `visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers` parser. This is candidate syntax evidence only, not a check of installed aggregate policy or effective authentication behavior.

| Reviewed artifact | SHA-256 |
| --- | --- |
| Wrapper | `9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb` |
| Unchanged metadata helper | `a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6` |
| Digest-updated sudoers policy | `0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698` |
| Environment diagnostic tests | `aec968c47c9c44b08f2e37a6aa21995e6c96395fadfc0e4f6fe98e1bcb6dae5d` |

## Residual limitations and final disposition

No blocking source/policy issue remains for this diagnostic-only handoff after ER-01 correction. The reviewer recommends only the guarded human upgrade and exact physical-console diagnostic documented in the current checkpoint. The returned first-failure symbol may justify a later reviewed correction; it does not authorize guessing or requesting raw values now.

Underlying I/O errors, failed policy restoration, uncatchable termination and power loss can defeat complete upgrade recovery. The fixed transaction reports partial recovery honestly; it is not power-loss-qualified. Existing administrator authority, host-root/kernel/PAM/interpreter trust and compromise of an already-authorized physical login remain outside this probe's assurances. A restored old policy with a mismatched new wrapper should refuse the narrow digest exception, not grant broader access.

Actual refined console results, full runtime attack matrix, no-swap, core/crash suppression, canary leakage and all downstream storage/OpenBao/TDE/tenant/execution qualifications remain outstanding. No LUKS/OpenBao initialization, encryption keys, recovery material, project secret input, brokerage connectivity or LIVE capability was introduced. `secret_entry_authorized` and `runtime_crash_suppression_qualified` remain false. Gate 2 remains NOT PASSED; PR #14 must remain draft and unmerged.
