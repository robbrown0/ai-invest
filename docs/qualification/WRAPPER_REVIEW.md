# Independent Review — Human-Console Preflight Wrapper

**Status:** Source/test review complete; NOT runtime qualification; Gate 2 NOT PASSED.
**Date:** 2026-09-08.
**Reviewer:** Separate adversarial-review agent; not the implementation author.
**Scope:** Non-secret wrapper, unchanged approved helper, tests and operator trust boundaries.

## Reviewed identities and evidence

- Wrapper: `scripts/qualification/run_operator_preflight.py`, SHA-256 `82d6d8ec35cf7d46dfd02e76f17f9dbddae4ac7eb00ab0d8972a833484716c42`.
- Original helper: approved commit `ff75739e4bd420cd17104e34e1eb2b1cdcd54e22`, SHA-256 `a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd`.
- Independent command: `python3 -I -B -m unittest discover -s tests/qualification -v`.
- Expected: all source-level regressions pass without installing the wrapper, launching a privileged scope or entering secrets.
- Actual: **45 tests passed** in the final independent run, including existing preflight tests, wrapper regressions and added trust/host-enrollment negative cases. The earlier independent 39-test run also passed.
- Additional independent non-mutating probes rejected PTYs, SSH/GUI/multiplexer markers, unapproved JSON fields and either authorization flag set to true. Required systemd, mount-isolation, clean-environment and core-limit arguments were present.
- Six independent synthetic filesystem/trust negative probes passed: group-writable source, symlink source, hardlinked source, non-root installed ancestry, changed pinned helper and changed checkout wrapper all rejected. Temporary fixtures were removed; no real runtime state was touched.

## Findings and resolutions

| Finding | Resolution / regression |
|---|---|
| Internal scoped entry could otherwise skip the mandatory plan check. | Scoped entry now rechecks the plan before invoking operator mode. `FlowTests.test_scoped_entry_also_requires_plan`. |
| Failure while publishing a fallback could emit an exception traceback. | Fallback publication failures receive a fixed diagnostic. `FlowTests.test_output_io_error_does_not_disclose_diagnostics`. |
| Successful candidate JSON must not override a failed scope exit. | Parent validates exit status against the report and substitutes failure on disagreement. `FlowTests.test_scope_failure_invalidates_success_json_reg_wrapper_status_01`. |
| PTY descriptors or a reopened console must not disguise the controlling terminal. | Device metadata and controlling-terminal identity supplement pathname checks. `ConsoleTests` and independent negative probes. |
| The actual checkout has group-writable directories/files, so strict provenance checks currently refuse it. | Reviewed human installation instructions remove group/other write only from the specifically checked project paths. No permission changes were performed by this reviewer; this is a real prerequisite, not a reason to weaken validation. |

The final [operator installation block](OPERATOR_CHECKPOINT.md) was independently reviewed: it checks a clean expected branch, rejects inappropriate symlinks and existing installation targets, checks root-owned shared parents, installs root-owned snapshots, enrolls a root-only local host identifier without printing it and verifies both source checksums before execution. Partial installation is explicitly not permission to run. The physical-console command remains fail-closed under sudo PTY allocation. Result retries are only for known prior wrapper metadata after confirming no active run; unexpected existing targets require investigation, not reading their contents or assuming that they are safe evidence.

The final notification/retrieval amendment was also reviewed and the 45-test suite rerun successfully. The fixed fresh-result notification occurs only after allowlisted publication and synchronization. Retrieval requires that notification from the current console invocation, then checks for a regular non-symlink root-owned mode 0644 single-link file before reading. A refused invocation without a new publication message does not authorize reading an unknown existing target.

## Top five concerns and residual limits

1. **Root installation provenance:** root-owned snapshots, safe ancestry, exact helper pin and checkout byte comparisons are necessary. Human review and a stable checkout remain assumptions; this is not protection against a malicious root user or compromised operating system.
2. **Console/relay assurance:** `sudo` may introduce a PTY even at the physical console. Refusal is expected in that case. Do not disable global sudo protections or substitute SSH. Actual direct-console execution remains outstanding.
3. **Result integrity:** the fixed output is exclusively created, kept root-only during execution and made readable only after allowlisted publication. Existing targets are refused, not replaced. A prior result or interrupted/private file must not be mistaken for a new completed run; heed the command exit status and documented stale-file handling.
4. **Runtime protection evidence:** unit tests and command construction do not prove cgroup limits, namespace propagation, kernel crash suppression or absence of secret-bearing relays. The original helper and wrapper keep both `secret_entry_authorized` and `runtime_crash_suppression_qualified` false.
5. **Host/operator assumptions:** the human must enroll and identify the intended physical host. The local root-only host identifier must never be returned or committed. Host comparison is not cryptographic remote attestation. Exact source/handler changes and installed-file/checkout changes require fresh review.

## Missing work and simplifications

No LUKS/OpenBao initialization, container launch, host-wide configuration changes, broker connectivity or real secret entry was exercised or authorized. Memory/core/TTY checks must still be demonstrated by the human-run non-secret checkpoint; later crash-suppression and service qualifications remain separate gates.

Keep this wrapper metadata-only. Do not turn it into a generic root command runner, a bootstrap dispatcher or a secret-entry session. A future need to handle keys warrants a separately reviewed design, not additional arguments to this wrapper.

**Disposition:** The reviewed changes are suitable to commit for human installation/review of a non-secret checkpoint. This is not approval to initialize encrypted storage or OpenBao and does not pass Qualification Gate 2.
