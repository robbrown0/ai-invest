# Independent Review — Inherited PATH Independence

**Status:** Acceptable for the documented non-secret human checkpoint only; Gate 2 NOT PASSED.
**Date:** 2026-09-09.
**Reviewer:** Independent adversarial agent, separate from the implementation and upgrade-procedure author.

## Scope and confirmed evidence

The reviewer read `AGENTS.md`, the current wrapper/helper, existing security and qualification reviews, the [PATH correction](PATH_INDEPENDENCE.md), policy, updated tests and human-only three-snapshot upgrade. The reviewer did not author the control or upgrade procedure. This review is the reviewer's only repository edit for this amendment.

The human-reported `environment_path` failure establishes that the previous equality predicate failed. The supplied sudo/PAM configuration supports investigating environment-construction ordering; it does not reveal or prove the source of the actual process value. No raw privileged environment, process/session list, logs, credentials or project secrets were inspected or requested by the reviewer. Previous failed attempts remain historical evidence.

## Version-source challenge

The reviewer independently examined upstream tag `SUDO_1_9_15p5`. Command Defaults are applied before environment reconstruction in [sudoers.c](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/sudoers.c). `rebuild_env` sets secure PATH, while `env_merge` permits replacement of non-preserved entries under environment reset in [env.c](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/env.c). The PAM session path subsequently merges its environment in [pam.c](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/auth/pam.c).

This supports a possible legitimate replacement mechanism, not a traced cause in the Ubuntu-patched binary. The reviewer specifically rejected the stronger unproven claim that PAM definitely overwrote this process's PATH. The established application defect is depending on an exact inherited string that the application does not need for execution.

## Adversarial findings and dispositions

| ID | Challenge | Disposition |
| --- | --- | --- |
| PR-01 | Removing a PATH guard could enable executable substitution before environment cleanup. | No such lookup found in the reviewed graph. The wrapper starts with absolute isolated Python. Its only pre-cleanup subprocess is absolute loginctl with explicit CLEAN_ENV and fixed arguments. Later wrapper subprocesses and scope executables are absolute. |
| PR-02 | Helper code contained hidden bare-command and interpreter lookups. | Identified during independent review. Bare findmnt/lsblk previously ran only after wrapper cleanup, so no inherited-PATH bypass was established. Both callsites and the helper shebang are now absolute as narrowly scoped hardening; helper content is repinned. |
| PR-03 | Python imports, shell startup or loader variables might bypass command-path reasoning. | Python uses `-I`; imports are standard-library/system paths, not inherited PATH selection. The only shell is a fixed absolute post-cleanup bash using no profile/rc and builtins/absolute exec. Unknown loader/Python/shell keys still fail the unchanged keyset check. Loader protection must already hold before Python starts; trusted sudo/PAM/system libraries and root configuration remain assumptions. |
| PR-04 | Predicate removal might silently relax identity, other environment checks or sudo policy. | Only inherited PATH equality is retired. The keyset, other value predicates, identity, VT/session, host, integrity, resource and result guards remain. Baseline comparison explicitly excludes only the retired PATH predicate. The sudoers change is digest only; no additional argument, executable, PTY exception or environment-setting permission is granted. |
| PR-05 | Hostile PATH text could reach a shell or published output. | Nine missing/empty/relative/hostile fixtures preserve exactly the same child command and CLEAN_ENV. No caller text is evaluated. The retired symbol remains valid for historical failed reports, not an active predicate or authorization. |
| PR-06 | Three-snapshot upgrade or rollback could leave broadened authority or prevent ordinary sudo recovery. | Verified old/new hashes, root-only snapshots, ignored staging and same-directory rename are documented. Rollback prioritizes old policy validation and independently attempts helper and wrapper restoration; complete recovery requires all three. No new sudo call is needed within that authenticated transaction. Mixed snapshots fail digest/helper/checkout checks; interrupted multi-file recovery remains explicitly unqualified. |

No blocking source/policy issue remains for this narrow correction. Retiring an unused input dependency is not accepting inherited PATH as trusted configuration: it is discarded, and the existing fixed clean environment remains the child boundary. Any future executable/import path change requires renewed review and regression coverage.

## Independently executed evidence

The reviewer ran:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q
Ran 109 tests
OK
```

All **109 unique tests passed**, zero skips. Coverage includes the nine PATH fixtures, real unprivileged isolated-interpreter executions, fixed loginctl/CLEAN_ENV behavior, AST execution-surface checks, dangerous-key refusal, historical identifier handling, unchanged non-PATH predicates, nine inert upgrade outcomes and seven rollback-failure legs. Transaction tests execute command doubles, not install, rename, sudo or privileged operations. Updated old tests now express the intentional PATH correction rather than pretending baseline acceptance is wholly unchanged.

The reviewer separately ran the real read-only helper plan through absolute `/usr/bin/python3 -I -B`, with only an unusable synthetic PATH and C locale values supplied. The plan passed and both authorization flags remained false. Its filesystem metadata was captured but never returned; the only returned evidence was a fixed test identifier, pass/fail and false flags. This demonstrates unprivileged helper execution without inherited search directories, not protected-scope or resource qualification.

The proposed policy independently passed the installed `visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers` parser. This is candidate syntax evidence, not aggregate installed-policy or privileged-runtime evidence.

| Reviewed artifact | SHA-256 |
| --- | --- |
| Wrapper | `f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719` |
| Helper | `e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c` |
| Digest-updated sudoers policy | `04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f` |
| New PATH regression tests | `e4ed90ee0bdf4bc5dcaee65fecf9d868dd5f85856382152b85531d1c775bdda2` |

## Final disposition and remaining gates

Recommend only the guarded human upgrade followed by the exact physical-console diagnostic in the current checkpoint. The reviewer installed nothing and performed no sudo authentication, privileged scope, canary, crash, storage or secret operation. Another later predicate may still fail; no runtime success is predicted.

Existing root/kernel/PAM/interpreter trust, compromised authorized-console sessions, concurrent root replacement and failed/power-interrupted recovery remain residuals. This is not an atomic three-file or power-loss-qualified transaction. The original effective no-swap, crash suppression, canary leakage, encrypted storage/TDE/OpenBao recovery, tenant and execution qualifications remain outstanding.

No LUKS/OpenBao initialization, real keys/recovery material, project-secret input, brokerage connectivity or LIVE capability was introduced. `secret_entry_authorized` and `runtime_crash_suppression_qualified` remain false. Qualification Gate 2 remains NOT PASSED; PR #14 must remain draft and unmerged.
