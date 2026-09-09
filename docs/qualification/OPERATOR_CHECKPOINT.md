# Human Operator Checkpoint — Bounded Non-Secret Diagnostics

**Status:** Diagnostic amendment prepared; human upgrade/runtime diagnostic NOT RUN by agents; Gate 2 NOT PASSED.
**Purpose:** Identify a failed metadata check without weakening controls or disclosing its underlying values.

## Recorded human result and scope

The owner reports running the previous wrapper at the intended physical Linux console without entering any project secret. The returned ordinary result was:

```json
{"checks_passed":false,"error":"metadata_unavailable","mode":"operator","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

This is preserved failed evidence, not a diagnosed cause. It may originate from a wrapper guard or helper metadata acquisition. We have not inferred which, inspected secret material, or remotely rerun a privileged operator session. Earlier records that say the wrapper was not installed describe the historical pre-handoff state, not the owner's subsequent action.

Ordinary invocation and its JSON shape are unchanged. New explicit diagnostic mode returns only fixed symbolic identifiers, never observations, file contents, identifiers, environment/process data, exception strings/types, credentials, secrets or command output. It retains all TTY, host, provenance, capacity, scope, no-swap and core-limit checks. Diagnostic mode does not repair failures, skip the plan, launch an arbitrary command, or authorize secret entry.

## Reviewed sources and human-only upgrade

Review the [helper](../../scripts/qualification/operator_preflight.py), [wrapper](../../scripts/qualification/run_operator_preflight.py), [diagnostic tests](../../tests/qualification/test_operator_diagnostics.py) and [independent diagnostic review](DIAGNOSTIC_REVIEW.md).

| Source | New reviewed SHA-256 |
| --- | --- |
| Helper | `a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6` |
| Wrapper | `8a490c2345b37266da7d8ec2d295247f6acc6c04f02a45a329f4532b5f45f29d` |

The old installed wrapper is expected to match commit `0c8eb0a04f8e31796c4d4f32f944818a478ede43`, wrapper hash `82d6d8ec35cf7d46dfd02e76f17f9dbddae4ac7eb00ab0d8972a833484716c42`, and original helper hash `a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd` (baseline helper commit `ff75739e4bd420cd17104e34e1eb2b1cdcd54e22`). The wrapper pins the new helper content; the old baseline remains for regression comparison, not as a claim that the amended helper is unchanged.

**Before console use, the human must upgrade both installed snapshots.** The existing installation intentionally refuses modified checkout/helper bytes. Do not run an old installed wrapper against the changed checkout and mistake its integrity refusal for a new metadata diagnosis.

After reviewing the pushed amendment, use your own SSH terminal for this complete guarded upgrade. Ensure the previous wrapper/scope has finished; do not upgrade concurrently with a run. No assistant-connected terminal may receive sudo authentication. The commands require the exact known old installation and stop on discrepancies. They preserve the root-only host marker and the ordinary result file; they do not re-enroll the host, initialize storage, or run the wrapper.

```bash
(
  set -eu
  cd /home/rob/ai-invest
  test "$(pwd -P)" = /home/rob/ai-invest
  test "$(git branch --show-current)" = phase3/synthetic-qualification
  test -z "$(git status --porcelain)"
  for path in . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py scripts/qualification/run_operator_preflight.py; do
    test ! -L "$path"
  done
  chmod go-w . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py scripts/qualification/run_operator_preflight.py

  for path in /usr /usr/local /usr/local/sbin /usr/local/libexec; do
    test ! -L "$path"
    test -d "$path"
    test "$(stat -c '%u:%a' "$path")" = 0:755
  done
  sudo test ! -L /usr/local/libexec/ai-invest
  sudo test -d /usr/local/libexec/ai-invest
  test "$(sudo stat -c '%u:%a' /usr/local/libexec/ai-invest)" = 0:700
  for path in /usr/local/sbin/ai-invest-operator-preflight \
    /usr/local/libexec/ai-invest/operator_preflight.py /usr/local/libexec/ai-invest/host-id; do
    sudo test ! -L "$path"
    sudo test -f "$path"
  done
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/operator_preflight.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/host-id)" = 0:600:1
  printf '%s\n' \
    '82d6d8ec35cf7d46dfd02e76f17f9dbddae4ac7eb00ab0d8972a833484716c42  /usr/local/sbin/ai-invest-operator-preflight' \
    'a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
  printf '%s\n' \
    '8a490c2345b37266da7d8ec2d295247f6acc6c04f02a45a329f4532b5f45f29d  scripts/qualification/run_operator_preflight.py' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  scripts/qualification/operator_preflight.py' \
    | sha256sum --check -

  sudo install -o root -g root -m 0644 scripts/qualification/operator_preflight.py \
    /usr/local/libexec/ai-invest/operator_preflight.py
  sudo install -o root -g root -m 0755 scripts/qualification/run_operator_preflight.py \
    /usr/local/sbin/ai-invest-operator-preflight
  printf '%s\n' \
    '8a490c2345b37266da7d8ec2d295247f6acc6c04f02a45a329f4532b5f45f29d  /usr/local/sbin/ai-invest-operator-preflight' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
)
```

Stop on any mismatch or partial upgrade; do not change the expected hashes to force acceptance. Never read, copy, print or return `host-id`. This is an upgrade of two reviewed metadata programs, not a secrets/key-management bootstrap. No installation/upgrade was performed by the agents.

## Short physical-console command

On the intended physical Linux `/dev/ttyN` console, with no recording, SSH, GUI terminal or multiplexer, run:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --diagnostic
```

Do not redirect or pipe the invocation. Sudo may allocate a PTY: if so, `tty_identity` is an expected possible refusal, not a reason to disable sudo protections or reopen a console descriptor. It is an example, NOT the diagnosed cause of the owner's prior failure.

The diagnostic executes the same bounded scope: `MemoryMax=2G`, `MemorySwapMax=0`, `TasksMax=32`, `CPUQuota=100%`, private mount propagation, clean environment and zero hard/soft core limits. Both outside and inside the scope the plan must pass before dependent work. Underlying console descriptors stay intact for the original TTY checks. Systemd may display its own console status; none of that output enters the diagnostic JSON. Return only the bounded JSON, not terminal transcripts or command diagnostics.

## Sanitized result and retrieval

Diagnostic mode writes a separate fixed path, `/var/tmp/ai-invest-operator-diagnostic.json`, with the same exclusive/no-follow creation, inode/ownership/link checks, private working permissions and parent-validated publication used by ordinary mode. The old ordinary result is untouched. Existing targets are never overwritten. A maximum of one failed-check identifier is returned; zero identifiers means all executed metadata checks passed. First unavailable-source evidence takes precedence over later predicate evaluation, and a first failure does not assess every other check.

Example failure shape only; the actual identifier will depend on the human run:

```json
{"checks_passed":false,"failed_checks":["tty_identity"],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

A fully passing metadata diagnostic has `checks_passed: true` and `failed_checks: []`, with both authorization flags still false. Failure returns nonzero. No `observations`, raw `error`, exception text, paths, metadata values or arbitrary strings are permitted in this schema.

After the console prints `A new sanitized diagnostic result is ready.`, retrieve that new result over SSH:

```bash
test ! -L /var/tmp/ai-invest-operator-diagnostic.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-operator-diagnostic.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-operator-diagnostic.json
```

If safe creation/publication is impossible, the console can display the same bounded diagnostic JSON instead; no new file is claimed. Do not read an unknown/pre-existing target or treat a stale/private/incomplete file as a new result. For a later retry, preserve only a known prior diagnostic artifact, confirm the prior run is finished, and let the human remove that exact old diagnostic file with `sudo unlink -- /var/tmp/ai-invest-operator-diagnostic.json`. Never delete the ordinary result or a broader path as part of this amendment. Unknown files/symlinks/hardlinks require investigation without returning their contents.

## Complete symbolic allowlist

Helper source/evaluation identifiers: `cgroup_membership`, `memory_max`, `memory_swap_max`, `memory_swap_current`, `pids_max`, `cpu_max`, `rlimit_core`, `tty_identity`, `mount_namespace`, `pid_namespace`, `apport_handler`, `core_pattern`, `root_operator`, `operator_evaluation`.

Wrapper boundary identifiers: `arguments`, `result_file`, `helper_integrity`, `host_context`, `plan_preflight`, `scope_launch`, `report_validation`, `result_publication`, plus shared `root_operator`, `rlimit_core` and `tty_identity`.

`helper_integrity` groups installed/checkout provenance checks; `host_context` groups host-enrollment, container/root/namespace guards; `plan_preflight` groups the existing storage plan. These coarse identifiers deliberately disclose neither paths nor underlying values. They locate the failed boundary rather than proving its cause. No caller can supply additional identifiers, an output path or a generic command.

## Evidence and gate boundary

The diagnostic regression suite injects failures into all 13 helper acquisition sources, verifies numeric evaluation labeling, rejects unapproved schemas/payloads, checks false authorization flags, and compares ordinary successful/error results with the original committed helper. Independent review is recorded in [DIAGNOSTIC_REVIEW.md](DIAGNOSTIC_REVIEW.md). Earlier [wrapper review](WRAPPER_REVIEW.md), [approved prerequisite assessment](APPROVED_PREREQUISITES.md) and [original operator review](OPERATOR_REVIEW.md) remain historical evidence.

No secret input, LUKS/OpenBao initialization, Alpaca connection, LIVE capability or global configuration change was added. Actual protected operator/core-suppression/storage/service qualification remains outstanding. A diagnostic identifies a failure; it neither fixes it nor passes Gate 2. PR #14 stays draft and unmerged.
