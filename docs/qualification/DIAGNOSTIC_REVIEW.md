# Independent Review — Non-Secret Operator Diagnostics

**Status:** Diagnostic amendment reviewed; runtime prerequisites remain unqualified; Gate 2 NOT PASSED.
**Date:** 2026-09-09.
**Reviewer:** Independent adversarial-review agent, separate from the implementation author.

## Reviewed scope and evidence

The human reported an ordinary `metadata_unavailable` result from the intended physical console, with both authorization flags false and no project secret entered. This is valid historical failure evidence, not proof that a particular host control failed. The amendment adds an explicit diagnostic mode to identify a fixed metadata source or wrapper stage without returning its value.

Reviewed [helper](../../scripts/qualification/operator_preflight.py) SHA-256: `a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6`.

Reviewed [wrapper](../../scripts/qualification/run_operator_preflight.py) SHA-256: `8a490c2345b37266da7d8ec2d295247f6acc6c04f02a45a329f4532b5f45f29d`.

The original helper baseline remains commit `ff75739e4bd420cd17104e34e1eb2b1cdcd54e22`. The current helper is intentionally changed and pinned by its new digest; the baseline is not misrepresented as containing this amendment. The review followed [AGENTS.md](../../AGENTS.md) and examined implementation, tests and the operator trust boundary. It did not install or invoke a privileged wrapper, inspect secret material, initialize storage/OpenBao or operate any brokerage connection.

## Adversarial findings and disposition

1. **An unavailable source must not become an opaque evaluation failure.** Initial review identified that numeric metadata could pass `isdigit()` yet fail integer conversion, losing the source-specific label. The implementation now evaluates diagnostic predicates through the fixed metadata wrapper. Regression cases cover Unicode digits and oversized decimal strings for memory and PID limits. Resolved without relaxing acceptance criteria.
2. **The original failure may precede the helper.** Console, integrity, host, plan, launch, result and validation guards now have fixed symbolic diagnostic identifiers. An early rejection still stops processing; the diagnostic does not bypass a failing guard to gather more information. No unsupported root-cause conclusion is made from the historical result.
3. **A diagnostic payload is an output boundary, not arbitrary debug output.** The wrapper requires exactly five report fields, an actual boolean success flag, zero or one allowlisted string identifier, consistency between success and an empty failure list, and literal false authorization flags. Unknown keys, arbitrary text, extra observations, multiple failures, incorrect types and inconsistent scope results are rejected. No exception string, path, environment or raw metadata value is included in diagnostic JSON.
4. **Preserve existing evidence and execution protections.** The diagnostic uses a separate fixed output filename with the same exclusive creation, ownership, permission, inode and publication protections. The ordinary result file is not replaced. Scope arguments differ only by a fixed internal diagnostic flag: memory, swap, PID, CPU, mount, core-limit, clean-environment and TTY protections are unchanged.
5. **The human must upgrade the installed snapshot before retrying.** Previously installed bytes cannot accept the new option. The final operator procedure verifies known old and reviewed new snapshots before replacing exactly the two intended programs, verifies the installed result afterward, retains host enrollment and preserves the prior ordinary result. Ownership, permission, link and canonical-parent guards remain mandatory. An unknown or partially upgraded installation requires investigation, not a hash or permission bypass. This is a human-only installation step, not an action performed by this review.

The final bounded stdout fallback also received review: if no safe result file can be created or published, diagnostic mode can print the same fixed-schema report without overwriting an existing artifact or claiming a new file exists. Regression cases cover non-root invocation, unsupported arguments and existing-file refusal. Ordinary-mode output behavior remains unchanged.

No unresolved High or Critical finding was identified in the bounded diagnostic amendment. This is not approval of the underlying host secret-entry protections or Gate 2.

## Independently executed tests

Procedure: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/qualification -v`, Python 3.12.3.

Expected: all existing checks remain fail-closed; diagnostic fault injection returns only fixed identifiers; ordinary valid/error outputs match the original helper; authorization flags remain false.

Actual: **59 tests passed**, including 14 diagnostic test methods with parameterized cases. The final complete suite was independently rerun against the exact source hashes above. See [diagnostic regressions](../../tests/qualification/test_operator_diagnostics.py), [operator regressions](../../tests/qualification/test_operator_preflight.py) and [wrapper regressions](../../tests/qualification/test_operator_wrapper.py).

The reviewer also independently executed 14 additional synthetic assertions covering numeric evaluation failures and malformed diagnostic reports, a comparison proving the scope command differs only in its fixed internal mode flag, and a bounded non-root stdout-fallback assertion. All passed. Only synthetic metadata and non-secret source code were used; no privileged service, cryptographic bootstrap or actual secret was involved.

## Residual limitations and next evidence

- The original physical-console failure remains unexplained until the human returns a new diagnostic artifact. A reported identifier narrows the failing stage; it does not disclose the underlying value or establish remediation.
- Diagnostic output is intentionally first-failure only. Later checks may remain untested when an earlier source or guard fails.
- `checks_passed: true` only means metadata predicates passed. Both `secret_entry_authorized` and `runtime_crash_suppression_qualified` remain false even on diagnostic success.
- Unit tests and source review do not prove runtime no-swap, crash suppression, LUKS/OpenBao lifecycle, TDE, recovery, tenant isolation or execution reliability.
- Physical-console execution, sudo PTY behavior and the guarded human installation/upgrade remain outside these mocked regression tests. Do not weaken those boundaries to obtain a passing result.

Follow the [operator checkpoint](OPERATOR_CHECKPOINT.md) for the human-only retry. PR #14 must remain draft and unmerged; no secret entry or project initialization is authorized by this amendment.
