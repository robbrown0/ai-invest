# Independent Review — Physical Console Boundary

**Status:** Acceptable for the documented non-secret human checkpoint only; runtime qualification outstanding; Gate 2 NOT PASSED.
**Date:** 2026-09-09.
**Reviewer:** Independent adversarial agent, separate from the implementation author.

## Scope and independence

The reviewer read `AGENTS.md`, existing qualification/operator reviews, the relevant Phase 2 security architecture, the proposed wrapper/policy/tests, [boundary analysis](CONSOLE_TRUST_BOUNDARY.md) and [human checkpoint](OPERATOR_CHECKPOINT.md). The reviewer did not author the wrapper, policy or installation transaction. This review record is the reviewer's only repository edit. No sudo authentication, installed-policy modification, privileged probe, canary, crash, storage initialization or secret operation was performed.

The owner's confirmed physical `/dev/tty3` to sudo `/dev/pts/3` transition establishes the original design error. The old rejection was correct. Neither that failure nor the later failed diagnostic is rewritten as success.

## Challenges and findings

| ID | Independent challenge | Disposition |
| --- | --- | --- |
| CB-01 | Installing policy and then launching a second `sudo` for rollback can fail if the new aggregate configuration prevents sudo from running. A cached ordinary sudo session is not retained root authority. A failed copy can also leave a partial policy. | FIXED and independently re-reviewed: stage under a dot-containing ignored filename in the same directory, validate, atomically rename, and validate the aggregate policy inside one already-authenticated fixed transaction. Its cleanup never launches another sudo. REG-CB-01 exercises success and copy/candidate-validation/rename/aggregate-validation failures with inert command doubles. Power-loss/uncatchable-kill recovery remains unqualified. |
| CB-02 | Command Defaults cannot be both command- and user-scoped; existing broad administrator grants may independently authorize execution. | Documented. The policy grants only UID 1000 to root:root and the wrapper independently checks invoking and login/session UID. No claim is made to revoke prior administrator authority. |
| CB-03 | Default digest `fdexec` changes a script's path, conflicting with existing canonical-path guards; disabling it exposes a check/open interval. | Narrow `fdexec=never` is acceptable only for this non-secret checkpoint with root-owned non-writable ancestry, pinned bytes, one link, no symlinks and no concurrent updates. Malicious/concurrent root replacement remains a residual, not a solved race. |
| CB-04 | PTY allocation and recording can arise from I/O logging independently of `use_pty`. Password exemption/caching can undermine fresh authentication. | Exact-command-only logging flags, `authenticate`, `PASSWD`, `timestamp_timeout=0` and `!exempt_group` are present. Aggregate host policy, actual fresh-auth behavior and unchanged unrelated-command PTY behavior remain human runtime tests. |
| CB-05 | SSH can strip environment markers or reopen VT descriptors; a same-UID compromised console session can defeat a claim of physical intent. | Kernel controlling-TTY, all three device descriptors, audit login UID and current active local logind session are checked. Markers are supplementary. An already compromised physical login is explicitly not contained; stronger future secret-operation assurance remains unresolved. |
| CB-06 | A fabricated session token test might falsely claim replay, expiration and reboot protection. | No project authorization artifact exists. Fresh sudo authentication and current session checks are the proposed boundary. Actual cached-auth, expiration and reboot behavior are NOT RUN. |
| CB-07 | PATH, shell, extra arguments, modified files or result-file substitution could turn a narrow command into a generic runner. | No such primitive found in source review. Absolute executables, exact argument matching, strict retained-environment checks, isolated Python, pinned helper bytes and existing exclusive/no-follow result handling remain. Unit fixtures are not host attack results. |
| CB-08 | Metadata success, zero core limits or a checked Apport source branch could be mistaken for protected secret input. | Both authorization flags remain false. Effective no-swap, crash collection and canary leakage remain NOT RUN. Private propagation is not filesystem-access confinement. |

## Independently executed evidence

Installed sudo/visudo **1.9.15p5**, grammar **50**; Python **3.12.3**. The reviewer read the installed `sudoers(5)` and `loginctl(1)` manuals. `loginctl show-session self` denotes its own session; `auto` can fall back to a graphical session and is not used.

- An isolated synthetic policy passed the actual installed strict `visudo` parser without reading or changing host policy.
- `cvtsudoers -f JSON infrastructure/qualification/ai-invest-operator.sudoers` independently confirmed one digest-pinned exact `--diagnostic` command alias, alias-only Defaults and the numeric UID 1000 root:root grant.
- Baseline **59 tests passed**. The first expanded **77-test** run exposed one test assertion matching the text `Defaults ` in a comment; after that test-only correction, the independently repeated **77 tests passed**, zero skips. No security control was relaxed to pass it.
- Following the CB-01 correction and permanent regression, the reviewer independently repeated the final **78 tests**, all PASS, zero skips. The documented transaction's five control-flow paths were exercised without invoking install, unlink, sudo or root operations. Exact cleanup-target checks remain in those test doubles.
- The reviewer ran `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests/qualification -q`; no test installed host policy or invoked a privileged operator session.

| Reviewed source | SHA-256 |
| --- | --- |
| Wrapper | `a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8` |
| Existing metadata helper | `a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6` |
| Proposed sudoers policy | `9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184` |
| Console-boundary regression tests | `bb43c49275e1e3a252c250caeecfbca0d5de749fdc0543a90b57b65a3ea35727` |

The final human installation block stages root-owned candidates and checks pinned content before activation. It checks the baseline and candidate syntax, installs mode 0440, uses the fixed authenticated activation/rollback transaction, then verifies the installed file's ownership/mode/link count/hash. The installed sudoers manual confirms dot-containing files are ignored by directory inclusion. Removing the exact known final drop-in removes the added exception/grant without editing ordinary sudo policy. A partial ignored candidate cannot itself grant authority. No concurrent root update is permitted; actual host installation, interruption recovery and rollback have not been run. The fixed maintenance transaction uses the human's existing administration authority; the proposed policy does not grant a shell or generic installer.

## Gate and outstanding evidence

This review cannot establish that the replacement policy works on the host: it has not been installed by agents. Actual SSH/GUI/multiplexer rejection, fresh-auth/no-cache behavior, unchanged unrelated sudo PTY behavior, wrong-user/host/path/argument tests, restart/reboot tests and rollback remain unqualified. Root-owned candidate staging and hash checks do not attest a compromised host.

No synthetic canary exists in this amendment; absence of a canary is not leakage evidence. No effective protected cgroup result or kernel-triggered crash result has passed. Secret-bearing operations, LUKS/OpenBao initialization, real keys/recovery material and brokerage connectivity remain prohibited. `secret_entry_authorized` and `runtime_crash_suppression_qualified` remain false.

## Final disposition

CB-01 was corrected after independent challenge and regression-tested; no blocking source/policy issue remains for the documented NON-SECRET checkpoint. The reviewer recommends only human installation followed by the exact diagnostic, fresh-auth/no-cache and unrelated-sudo PTY comparisons in the checkpoint. This does not satisfy the user's stronger future requirement to resist an already-compromised console account, and does not approve secret entry or secret-bearing bootstrap. Runtime attack-matrix, swap, canary and crash evidence must be obtained separately. Qualification Gate 2 remains NOT PASSED; PR #14 must remain draft and unmerged.
