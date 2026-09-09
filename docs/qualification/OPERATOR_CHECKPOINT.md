# Human Operator Checkpoint — Command-Specific Console Qualification

## Current direction: synthetic IO deferred

The owner declined implementing/installing --io-test for now. Its candidate, tests and documentation remain preserved. Follow the [working V0 implementation direction](../V0_IMPLEMENTATION.md); no console action or IO-policy approval is requested. Both authorization flags remain false and Gate 2 NOT PASSED. Revisit this path only if genuinely needed for safe credential provisioning or later secret-infrastructure work.

## Deferred checkpoint: synthetic IO policy-scope approval

The traversal trial passed its finite observer milestone. Read [the recorded success and IO acceptance criteria](INPUT_OUTPUT_QUALIFICATION.md), [independent candidate review](INPUT_OUTPUT_REVIEW.md), and [the approval checkpoint](INPUT_OUTPUT_CHECKPOINT.md). The synthetic IO candidate is unwired; adding its exact command requires explicit policy-scope approval before integration/installation. Do not rerun the successful traversal test or use historical installation blocks. Both flags remain false and Gate 2 NOT PASSED.

## Previous checkpoint: bounded traversal compatibility correction

Use only the **[guarded traversal upgrade and console run](TRAVERSAL_CHECKPOINT.md)** after [the confirmed condition and correction evidence](TRAVERSAL_QUALIFICATION.md) and [independent review](TRAVERSAL_REVIEW.md). This tests the actual correction, not another diagnostic-only run. Original bounds/selectors remain; excluded metadata consumes existing budgets and never supplies payload evidence. Both flags remain false and Gate 2 NOT PASSED. Prior installation blocks are historical.

## Previous checkpoint: distinct boot/time predicates

Use only the **[guarded boot/time upgrade and one console run](BOOT_TIME_CHECKPOINT.md)** after reading [the protected-host excerpt and native reproduction](BOOT_TIME_QUALIFICATION.md) and [independent review](BOOT_TIME_REVIEW.md). The human's shared attribution_mismatch does not identify which boot/time condition failed. The next run distinguishes all three without weakening checks. Earlier installation blocks below are historical; both flags remain false and Gate 2 NOT PASSED.

## Previous checkpoint: focused journal observation

Use only the **[guarded journal upgrade and one console run](JOURNAL_CHECKPOINT.md)** after reviewing [new human evidence and bounded diagnostics](JOURNAL_QUALIFICATION.md) and [independent review](JOURNAL_REVIEW.md). All setup/local checks and the log/store/window categories passed in the owner's last trial, but the journal cause remains unresolved. The next run reports journal_stage/journal_reason without raw data. No working trust mechanism is redesigned; both flags remain false. All installation sections below are historical.

## Previous checkpoint: log-source policy and setup readiness

Use the **[guarded log-source upgrade and one console run](LOG_SOURCE_CHECKPOINT.md)** after reviewing the [confirmed mismatch and trust boundary](LOG_SOURCE_QUALIFICATION.md) and [independent review](LOG_SOURCE_REVIEW.md). The observer will collect fixed setup outcomes before any canary/crash, preserving all old results. Actual corrected host readiness remains unverified. All installation sections below are historical; Gate 2 and both authorization flags remain unchanged.

## Previous checkpoint: one narrow crash trial passed; observation pending

The owner reports 11 implemented local PASS checks and no FAIL at commit **5975603575b6761fb44932b84dc1519676639584**. See [the unchanged result, precise meanings and coverage matrix](OBSERVATION_QUALIFICATION.md). Use only the new **[guarded observation upgrade and console checkpoint](OBSERVATION_CHECKPOINT.md)** for the next run. It preserves the original result and still expects overall coverage_incomplete. Secret-entry and runtime-crash-qualification flags remain false. All sections below preserve earlier checkpoints; do not reuse their installation blocks.

## Previous checkpoint: metadata PASS; bounded crash trial pending

The human's latest reviewed PATH-snapshot diagnostic returned checks_passed=true with no failures and both authorization flags false. See [exact runtime-qualified predicates and limits](CRASH_QUALIFICATION.md). Next is the **[guarded synthetic crash checkpoint](CRASH_CHECKPOINT.md)**, not secret bootstrap. That interim trial cannot claim complete collector/leakage qualification. Gate 2 remains NOT PASSED. Earlier [PATH correction](PATH_INDEPENDENCE.md), [environment refinement](ENVIRONMENT_DIAGNOSTICS.md) and all blocks below remain historical evidence, not current installation instructions.

## Historical command-specific installation record

**Current status:** Confirmed sudo PTY trust-boundary failure; proposed correction is NON-SECRET ONLY. Gate 2 NOT PASSED. Neither host policy nor wrapper upgrade below has been installed by agents.

Read [the confirmed evidence, alternatives and limitations](CONSOLE_TRUST_BOUNDARY.md) and [independent review](CONSOLE_BOUNDARY_REVIEW.md). The owner confirmed `/dev/tty3` before sudo and `/dev/pts/3` through sudo. The previous `tty_identity` refusal was correct. The historical instructions later in this file are retained for audit, **not for reuse**.

## Current human-only guarded installation

This changes only the reviewed installed metadata wrapper and adds `/etc/sudoers.d/ai-invest-operator-qualification`. It does not enable secret entry. The helper and root-only host marker stay unchanged. The exception applies ONLY to the exact reviewed wrapper with exactly `--diagnostic`; ordinary invocation and all unrelated commands retain existing sudo policy.

Review the pushed commit shown in the handoff and verify the clean branch/head locally. Stop all project preflight runs before upgrading; do not concurrently replace root-owned programs/policy. Keep a separate working ordinary sudo session for rollback. Run this complete block from **your own SSH terminal**, never an assistant-connected session. Sudo passwords stay with you. Do not paste terminal transcripts or the host marker into chat.

The block stages only inert root-owned candidate files, verifies their pinned hashes before replacing the executable/policy, checks local syntax before installing policy, and validates the complete installed sudo configuration afterward. Final activation/validation/rollback is one fixed already-authenticated transaction, so removal of a rejected policy does not need sudo to parse that rejected policy again. This literal installation transaction uses the human's existing administration authority; the drop-in grants no shell or installer permission. It refuses existing policy/candidates, symlinks, hardlinks or unexpected old snapshots. A mismatch is a stop, not permission to edit a digest. Partial failure leaves no authority to run; inspect only these fixed project paths.

```bash
(
  set -eu
  cd /home/rob/ai-invest
  test "$(pwd -P)" = /home/rob/ai-invest
  test "$(id -u)" = 1000
  test "$(git branch --show-current)" = phase3/synthetic-qualification
  test -z "$(git status --porcelain)"
  /usr/sbin/visudo -V | head -n 1 | /usr/bin/grep -Fx 'visudo version 1.9.15p5'
  test "$(systemctl show ai-invest-operator-preflight.scope -p ActiveState --value)" = inactive
  for path in . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py scripts/qualification/run_operator_preflight.py \
    infrastructure infrastructure/qualification infrastructure/qualification/ai-invest-operator.sudoers; do
    test ! -L "$path"
    chmod go-w "$path"
  done
  for path in /usr /usr/local /usr/local/sbin /usr/local/libexec /etc; do
    test ! -L "$path"
    test "$(stat -c '%u:%a' "$path")" = 0:755
  done
  sudo test ! -L /etc/sudoers.d
  test "$(sudo stat -c '%u:%a' /etc/sudoers.d)" = 0:755
  sudo test ! -L /usr/local/libexec/ai-invest
  test "$(sudo stat -c '%u:%a' /usr/local/libexec/ai-invest)" = 0:700
  for path in /usr/local/sbin/ai-invest-operator-preflight \
    /usr/local/libexec/ai-invest/operator_preflight.py /usr/local/libexec/ai-invest/host-id; do
    sudo test ! -L "$path"
    sudo test -f "$path"
  done
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/operator_preflight.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/host-id)" = 0:600:1
  for path in /etc/sudoers.d/ai-invest-operator-qualification \
    /etc/sudoers.d/.ai-invest-operator-qualification.pending \
    /usr/local/libexec/ai-invest/operator-candidate /usr/local/libexec/ai-invest/policy-candidate; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    '8a490c2345b37266da7d8ec2d295247f6acc6c04f02a45a329f4532b5f45f29d  /usr/local/sbin/ai-invest-operator-preflight' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
  printf '%s\n' \
    'a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8  scripts/qualification/run_operator_preflight.py' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  scripts/qualification/operator_preflight.py' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  infrastructure/qualification/ai-invest-operator.sudoers' \
    | sha256sum --check -
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py \
    /usr/local/libexec/ai-invest/operator-candidate
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers \
    /usr/local/libexec/ai-invest/policy-candidate
  printf '%s\n' \
    'a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8  /usr/local/libexec/ai-invest/operator-candidate' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  /usr/local/libexec/ai-invest/policy-candidate' \
    | sudo sha256sum --check -
  sudo /usr/sbin/visudo -c -s -f /usr/local/libexec/ai-invest/policy-candidate
  sudo install -o root -g root -m 0755 /usr/local/libexec/ai-invest/operator-candidate \
    /usr/local/sbin/ai-invest-operator-preflight
  printf '%s\n' \
    'a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8  /usr/local/sbin/ai-invest-operator-preflight' \
    | sudo sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  sudo /bin/sh -c '
    set -eu
    test ! -e /etc/sudoers.d/ai-invest-operator-qualification
    test ! -L /etc/sudoers.d/ai-invest-operator-qualification
    test ! -e /etc/sudoers.d/.ai-invest-operator-qualification.pending
    test ! -L /etc/sudoers.d/.ai-invest-operator-qualification.pending
    if ! /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/policy-candidate /etc/sudoers.d/.ai-invest-operator-qualification.pending; then
      if test -e /etc/sudoers.d/.ai-invest-operator-qualification.pending; then
        /usr/bin/unlink -- /etc/sudoers.d/.ai-invest-operator-qualification.pending
      fi
      exit 1
    fi
    if ! /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-operator-qualification.pending; then
      /usr/bin/unlink -- /etc/sudoers.d/.ai-invest-operator-qualification.pending
      exit 1
    fi
    if ! /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-operator-qualification.pending /etc/sudoers.d/ai-invest-operator-qualification; then
      /usr/bin/unlink -- /etc/sudoers.d/.ai-invest-operator-qualification.pending
      exit 1
    fi
    if ! /usr/sbin/visudo -c -s; then
      /usr/bin/unlink -- /etc/sudoers.d/ai-invest-operator-qualification
      /usr/sbin/visudo -c -s
      exit 1
    fi
  '
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  /etc/sudoers.d/ai-invest-operator-qualification' \
    | sudo sha256sum --check -
  sudo unlink -- /usr/local/libexec/ai-invest/operator-candidate
  sudo unlink -- /usr/local/libexec/ai-invest/policy-candidate
)
```

No existing result is deleted by installation. Preserve the already-reported diagnostic as historical evidence. Only after confirming the old run has finished and the file is the known wrapper-generated result, check that it is a non-symlink regular root-owned mode 0644 single-link file, then remove that **one** obsolete diagnostic with `sudo unlink -- /var/tmp/ai-invest-operator-diagnostic.json` before the next run. Do not delete the ordinary result or inspect an unknown target. Failed/partial root-only files are not publishable evidence; stop rather than automatically retry.

## Physical-console checkpoint and effective-policy tests

Policy copy is staged under a dot-containing filename, ignored by sudoers directory inclusion, and activated by same-directory rename only after candidate syntax validation. Ordinary copy/rename/validation failures clean only the known new policy/candidate inside the existing root transaction. An uncatchable kill or power loss after activation can still interrupt aggregate validation; no host configuration transaction is claimed power-loss-qualified. Human recovery then inspects only these fixed paths using existing host recovery procedures. Do not enable root login as a workaround. A leftover ignored pending file grants no sudo permission; stop and investigate rather than overwrite it. No concurrent root policy edits are permitted during installation.

At a fresh physical VT login (not SSH, GUI, tmux or screen), locally check `tty` is `/dev/ttyN`. Check `sudo /usr/bin/tty` still returns `/dev/pts/N`. This authenticates an ordinary command and also populates any ordinary sudo cache. Then run:

```bash
sudo -n /usr/local/sbin/ai-invest-operator-preflight --diagnostic
```

Expected: sudo itself refuses because fresh authentication is required, without running the helper or publishing a new result. A nonzero status alone is insufficient: locally distinguish password-required refusal from a helper rejection. If it executes using cached auth, STOP and roll back; do not change the wrapper to accept that policy. Do not share authentication transcripts.

Then the single non-secret operator command is:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --diagnostic
```

Enter only your ordinary sudo password when sudo requests it; the project command never asks for any input or project secret. No pipe, redirect, `-E`, `-S`, askpass, extra environment assignment or extra arguments. Expected fresh password prompt, then a new sanitized diagnostic. If every metadata predicate passes:

```json
{"checks_passed":true,"failed_checks":[],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

Otherwise expect `checks_passed: false` and one fixed symbolic failure. Added symbols are `operator_identity`, `operator_environment`, `console_session`; the historical allowlist below remains valid. Return only that JSON. Do not return raw sudo/loginctl output, environment, host/session identifiers or logs. A success is metadata evidence only, never permission for secret entry.

Afterward repeat `sudo /usr/bin/tty`; unrelated sudo must still use PTY. Repeat the noninteractive exact-command test; it must demand authentication again. Actual SSH/GUI/tmux/screen, wrong-user, tampered-path/digest and reboot qualification remain pending: do not simulate attacks by replacing installed root files or modifying other accounts. Those require a separately bounded test harness/policy audit; current unit fixtures are not live-host results. Returning a diagnostic does not complete that attack matrix.

Back over SSH, only following the fresh-result console notification:

```bash
test ! -L /var/tmp/ai-invest-operator-diagnostic.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-operator-diagnostic.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-operator-diagnostic.json
```

## Rollback — policy removal only

Human-only; do not run concurrently with the project probe. Verify the exact known installed policy first; unexpected content/ownership requires investigation. Removing this drop-in removes only the additional exception/grant. It does not edit ordinary sudo policy or disable ordinary sudo access. The updated metadata wrapper may remain installed; without the exception it correctly refuses sudo-created PTYs. Do not restore an old wrapper while leaving a mismatched policy behind.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  /etc/sudoers.d/ai-invest-operator-qualification' \
    | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

Expected: ordinary sudo still works and retains PTY behavior. The only removed file is the new qualification policy; its reviewed template remains recoverable in Git. No automated rollback test on the actual host has run. If installation stopped before policy creation, leave it absent; remove only verified inert candidate files after review. No global swap, core collector, Docker daemon, root login or unrelated workload change is part of installation or rollback.

## Historical diagnostic checkpoint — preserved, superseded instructions

The following section records the previous amendment exactly as it stood. Its unknown-cause/not-run statements describe that earlier time and are superseded by the confirmed evidence above. **Do not execute its obsolete upgrade block.**

### Earlier record: Bounded Non-Secret Diagnostics

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
