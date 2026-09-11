# Independent Review — Operator Prerequisite Probe

**Status:** Metadata-only implementation reviewed; secret-bearing operations remain blocked; Gate 2 NOT PASSED.
**Review date:** 2026-09-09 UTC.
**Reviewer perspective:** Independent security/adversarial reviewer, separate from the probe author.
**Purpose:** Challenge the proposed operator boundary and record narrow, reproducible regression evidence without implying runtime qualification.

## Scope and separation

The reviewer read `AGENTS.md`, the historical qualification records, Phase 2 security/operations guidance, the [approved prerequisites](APPROVED_PREREQUISITES.md), [operator checkpoint](OPERATOR_CHECKPOINT.md), [preflight implementation](../../scripts/qualification/operator_preflight.py) and [regression tests](../../tests/qualification/test_operator_preflight.py). The historical stop and its original independent review remain unchanged.

The reviewer independently ran synthetic unit tests and read-only unprivileged plan/operator probes. No privileged scope, crash, LUKS operation, mount, container, service, secret creation or secret-bearing command was run. This file is the reviewer's only repository edit. Other reviewers/agents are not independent human recovery custodians.

## Findings and dispositions

| Finding | Challenge | Disposition / evidence |
| --- | --- | --- |
| OR-01: core-limit assumption | Piped core handlers are not constrained by `RLIMIT_CORE`; zero limits alone cannot prove memory is excluded from crash reports | Installed Apport 2.28.1-0ubuntu3.8 was inspected. Its ordinary core-file writer honors zero, but its crash-report path can retain `CoreDump`. Probe requires the reviewed handler hash and namespace predicates in addition to zero limits. REG-CORE-01/02 pass only at predicate/source level. Actual suppression remains OPEN. |
| OR-02: terminal relay | `systemd-run --pty`, SSH and graphical terminals can buffer secret input outside a protected child cgroup | Probe rejects non-direct console descriptors; REG-TTY-01 passes. No secret entry is authorized. Complete operator input-path qualification remains OPEN. |
| OR-03: block storage is not necessarily local | Nonrotational disk/partition metadata also describes some network-backed block devices | Corrected parser requires the observed exact SATA disk ancestry and rejects unknown, network, rotational and encrypted/unexpected ancestry. REG-STORAGE-01 passes. This trusts host/kernel metadata and deliberately rejects other topologies pending review. |
| OR-04: namespace overclaim | Comparing a process with visible PID 1 does not establish that PID 1 belongs to the physical host | Fields now describe only observed namespace comparisons. Documentation requires direct-host verification and expressly disclaims host attestation and private-propagation proof. |
| OR-05: output/authorization regressions | Successful predicates or diagnostic errors must not authorize secrets or disclose raw diagnostics | Added REG-OUTPUT-01 success/error tests. Both authorization flags remain false; synthetic exception/subprocess diagnostics are excluded from the JSON report. |
| OR-06: sudo can introduce a PTY | Omitting `systemd-run --pty` does not eliminate a relay created by sudo policy | OPEN operator prerequisite; documentation corrected and independently reread. Sudo can allocate a PTY even on a physical console; the current probe should fail its direct-console predicate in that situation. The checkpoint now explains this expected failure and prohibits global sudo weakening or secret entry. |

For OR-01, installed handler source attaches a core stream around lines 1042–1053 and writes reports around lines 1160–1214. Its `_check_global_pid_and_forward` branch around lines 775–787 skips a different mount namespace sharing its PID namespace. The regression executes only this pinned function with mocked namespace observations, not a kernel-triggered collector. Future handler/library/policy changes and container routing require fresh review. [Linux core behavior](https://man7.org/linux/man-pages/man5/core.5.html)

For OR-06, upstream sudo documents that its PTY process model relays terminal input; `use_pty` became a default in sudo 1.9.14. The reviewer did not inspect privileged local sudo policy or change it. A physical console is a necessary candidate condition here, not sufficient assurance that no relay exists. [Sudo upgrade guidance](https://github.com/sudo-project/sudo/blob/main/docs/UPGRADE.md)

## Independently executed evidence

Exact interpreter: Python 3.12.3. Relevant installed source: Apport 2.28.1-0ubuntu3.8, pinned SHA-256 `1b8b5e2c53e8970dd2f47c9a0892030d1ebad57cae1f7242c43a6252f1f6dff2`.

Reviewed implementation SHA-256: `a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd`.

Reviewed test-file SHA-256: `de595230f87122d34d6388e817d052d54e980351dcb14c919f4483df5203f708`.

| Procedure / configuration | Expected result | Actual selected output | Result / limitation |
| --- | --- | --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests/qualification -p 'test_operator_preflight.py' -v` | Predicate/source and output regression cases pass, without host mutation | `Ran 17 tests in 0.009s`; `OK`; zero skips | PASS for these 17 tests only |
| `python3 -B scripts/qualification/operator_preflight.py plan` | Current approved topology/capacity/absence predicates pass without creating paths | `checks_passed: true`; available 464772927488 bytes; proposed 68719476736 bytes; projected remaining 396053450752 bytes | PASS for this transient metadata snapshot; repeat before any allocation |
| `python3 -B scripts/qualification/operator_preflight.py operator` from the assistant context | Fail closed outside a qualified operator context | Exit 1; `checks_passed: false`; `error: metadata_unavailable` | PASS for rejecting this context; NOT a successful operator qualification |
| Both actual probe outputs and mocked success/error reports | Never authorize secret entry or claim crash suppression | `secret_entry_authorized: false`; `runtime_crash_suppression_qualified: false` | PASS for this narrow invariant |

The reviewed plan requires 64 GiB allocation with at least 200 GiB and 20% filesystem free afterward. Operator predicates require root, direct console descriptors, finite memory at most 2 GiB, zero swap limit/current usage, at most 64 tasks, bounded CPU, zero hard/soft core limits and reviewed namespace/handler observations. The documented proposed scope is stricter on CPU/tasks: one CPU and 32 tasks. No scoped runtime values were obtained by this reviewer.

## Residual limitations and required next evidence

- No kernel crash test, collector-artifact inspection, private-propagation test or protected terminal-chain test has passed. These block all secret-bearing bootstrap operations.
- Metadata checks are not a launcher, durable mount guard, allocation transaction, authority against host root or continuing proof after the process exits. Reviewed root execution must use the agreed source snapshot without concurrent edits.
- The plan is deliberately host-specific. Porting to another filesystem/transport, changing the handler or using another PID namespace requires review and tests, not relaxed predicates.
- Synthetic validator tests do not cover every operating-system parser/error condition, nor do they qualify OpenBao, PostgreSQL, Docker no-swap behavior, recovery, TDE/WAL, tenancy or financial execution.
- Sudo authentication stays human-only. A failing direct-console check is a stop, not permission to change global policy or use Docker for host administration. A separately reviewed no-relay mechanism is still required if local policy inserts a PTY.
- No approval is given for volume creation, key generation, application exposure, brokerage connectivity, LIVE capability or Gate 2. The current code/documentation may be retained as failed-closed prerequisite evidence while the human supplies the next non-secret observations.

## Independent conclusion

The author corrected the identified storage-locality, namespace-description and output-test issues. The current preflight is acceptable as a narrowly scoped, non-secret metadata probe with explicit refusal to authorize secrets. The operator pathway, crash suppression and encrypted storage remain NOT QUALIFIED. Gate 2 remains NOT PASSED; do not merge the Phase 3 draft PR or infer authorization to continue into secret-bearing operations from these test results.
