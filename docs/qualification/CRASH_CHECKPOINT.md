# Human Checkpoint — Bounded Synthetic Crash Trial

**Historical checkpoint, now executed once by the human:** Source 5975603575b6761fb44932b84dc1519676639584 produced 11 local PASS and zero FAIL, with incomplete coverage. [Exact evidence](OBSERVATION_QUALIFICATION.md). Preserve this original block and result; do not reinstall it for the next run. Use the [current observation checkpoint](OBSERVATION_CHECKPOINT.md) instead. The prepared/unrun wording below describes its original handoff.

**Status:** Prepared, not installed/run by agents. Gate 2 NOT PASSED. No secret input authorized.

Read [scope, evidence and limitations](CRASH_QUALIFICATION.md) and [independent review](CRASH_REVIEW.md) first. This is an interim kernel/crash trial, NOT a complete collector/leakage qualification. Even a locally successful trial returns overall checks_passed=false / coverage_incomplete. Do not treat that as authorization to bootstrap.

## Exact reviewed artifacts

Installed baseline is commit **f1dfe6cf10f22d0d5da3e39f2b49dc12ee286181**. Confirm the clean checkout equals the new exact commit in the completion report. Existing helper stays unchanged.

| Artifact | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| Wrapper | f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719 | c95e4d462070e6577ceeba77051be504e67fe5d3f4cb62dc9125654e1b03e461 |
| Policy | 04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f | 034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae |
| Crash helper | MUST BE ABSENT | 781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415 |
| Existing metadata helper | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c | Unchanged |

The existing alias now contains precisely two digest-pinned commands: the same fixed installed executable with either --diagnostic or --crash-test. No wildcard, argument payload, arbitrary executable or internal scoped invocation is granted. All Defaults/authentication/environment/PTY settings remain command-scoped and unchanged. Ordinary sudo still uses its ordinary PTY behavior; verify sudo /usr/bin/tty separately if checking policy behavior. A third/root-owned crash helper is never an authorized standalone sudo command.

## Guarded human upgrade from your own SSH terminal

Use your pre-existing administrator authority, not an assistant-connected terminal. The block does not grant installer or root-shell permission through the operator policy. No project secret is requested. Do not concurrently run the diagnostic, change policy/programs or upgrade packages. Stop on any discrepancy; never blindly rerun a partially completed upgrade.

The block checks exact old/new hashes, parent ownership/permissions/symlinks, absent staging/new targets, candidate syntax and aggregate configuration. New root-only recovery copies use crash-* names; prior path-* and environment-* history remains untouched.

```bash
(
  set -eu
  cd /home/rob/ai-invest
  test "$(pwd -P)" = /home/rob/ai-invest
  test "$(id -u)" = 1000
  test "$(git branch --show-current)" = phase3/synthetic-qualification
  test -z "$(git status --porcelain)"
  test "$(git remote get-url origin)" = https://github.com/robbrown0/ai-invest.git
  /usr/sbin/visudo -V | head -n 1 | /usr/bin/grep -Fx 'visudo version 1.9.15p5'
  test "$(systemctl show ai-invest-operator-preflight.scope -p ActiveState --value)" = inactive
  for path in . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py scripts/qualification/run_operator_preflight.py \
    scripts/qualification/crash_canary.py \
    infrastructure infrastructure/qualification infrastructure/qualification/ai-invest-operator.sudoers; do
    test ! -L "$path"
    chmod go-w "$path"
  done
  for path in /usr /usr/local /usr/local/sbin /usr/local/libexec /etc /etc/sudoers.d; do
    sudo test ! -L "$path"
    test "$(sudo stat -c '%u:%a' "$path")" = 0:755
  done
  sudo test ! -L /usr/local/libexec/ai-invest
  test "$(sudo stat -c '%u:%a' /usr/local/libexec/ai-invest)" = 0:700
  for path in /usr/local/sbin/ai-invest-operator-preflight \
    /usr/local/libexec/ai-invest/operator_preflight.py /usr/local/libexec/ai-invest/host-id \
    /etc/sudoers.d/ai-invest-operator-qualification; do
    sudo test ! -L "$path"
    sudo test -f "$path"
  done
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/operator_preflight.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/host-id)" = 0:600:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  for path in /usr/local/libexec/ai-invest/crash_canary.py \
    /usr/local/libexec/ai-invest/crash-harness.candidate \
    /usr/local/libexec/ai-invest/.crash-harness.pending \
    /usr/local/libexec/ai-invest/crash-wrapper.previous \
    /usr/local/libexec/ai-invest/crash-policy.previous \
    /usr/local/libexec/ai-invest/crash-wrapper.candidate \
    /usr/local/libexec/ai-invest/crash-policy.candidate \
    /usr/local/sbin/.ai-invest-crash.pending /etc/sudoers.d/.ai-invest-crash.pending; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    'f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719  /usr/local/sbin/ai-invest-operator-preflight' \
    '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  /etc/sudoers.d/ai-invest-operator-qualification' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
  printf '%s\n' \
    '781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415  scripts/qualification/crash_canary.py' \
    'c95e4d462070e6577ceeba77051be504e67fe5d3f4cb62dc9125654e1b03e461  scripts/qualification/run_operator_preflight.py' \
    '034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae  infrastructure/qualification/ai-invest-operator.sudoers' \
    | sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/crash-wrapper.previous
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/crash-policy.previous
  sudo install -o root -g root -m 0600 scripts/qualification/crash_canary.py /usr/local/libexec/ai-invest/crash-harness.candidate
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/crash-wrapper.candidate
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/crash-policy.candidate
  printf '%s\n' \
    'f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719  /usr/local/libexec/ai-invest/crash-wrapper.previous' \
    '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  /usr/local/libexec/ai-invest/crash-policy.previous' \
    '781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415  /usr/local/libexec/ai-invest/crash-harness.candidate' \
    'c95e4d462070e6577ceeba77051be504e67fe5d3f4cb62dc9125654e1b03e461  /usr/local/libexec/ai-invest/crash-wrapper.candidate' \
    '034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae  /usr/local/libexec/ai-invest/crash-policy.candidate' \
    | sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      harness_absent=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/crash-policy.previous /etc/sudoers.d/.ai-invest-crash.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-crash.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/crash-wrapper.previous /usr/local/sbin/.ai-invest-crash.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-crash.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if /usr/bin/test ! -e /usr/local/libexec/ai-invest/crash_canary.py &&
         /usr/bin/test ! -L /usr/local/libexec/ai-invest/crash_canary.py; then
        harness_absent=1
      elif /usr/bin/test ! -L /usr/local/libexec/ai-invest/crash_canary.py &&
           /usr/bin/test -f /usr/local/libexec/ai-invest/crash_canary.py &&
           printf "%s\\n" "781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415  /usr/local/libexec/ai-invest/crash_canary.py" | /usr/bin/sha256sum --check --status -; then
        if /usr/bin/unlink -- /usr/local/libexec/ai-invest/crash_canary.py; then
          harness_absent=1
        fi
      fi
      if test "$policy_restored:$wrapper_restored:$harness_absent" = 1:1:1; then
        printf "Upgrade refused; prior reviewed pair and harness absence restored. No secret entry.\\n" >&2
      else
        printf "Upgrade refused; recovery requires human review. No secret entry.\\n" >&2
      fi
      exit 1
    }
    trap rollback EXIT HUP INT TERM
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/crash-policy.candidate /etc/sudoers.d/.ai-invest-crash.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-crash.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/crash-harness.candidate /usr/local/libexec/ai-invest/.crash-harness.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.crash-harness.pending /usr/local/libexec/ai-invest/crash_canary.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/crash-wrapper.candidate /usr/local/sbin/.ai-invest-crash.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-crash.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-crash.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/crash_canary.py)" = 0:644:1
  printf '%s\n' \
    '781084d0a524347e81e5f241cbf349e3404c931cba5082ee27f48a02b2475415  /usr/local/libexec/ai-invest/crash_canary.py' \
    'c95e4d462070e6577ceeba77051be504e67fe5d3f4cb62dc9125654e1b03e461  /usr/local/sbin/ai-invest-operator-preflight' \
    '034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae  /etc/sudoers.d/ai-invest-operator-qualification' \
    | sudo sha256sum --check -
)
```

Activation is NOT an atomic three-file transaction. The caught-failure transaction restores/validates policy first, independently restores wrapper, and restores the new harness's prior absence only if its exact reviewed bytes are identified; unknown/symlink targets are not removed. Complete recovery requires all three legs. Root-only staging/candidate/previous code copies remain for recovery. The existing metadata helper and host marker are unchanged. Power loss, I/O failure, concurrent root modification or an uncatchable kill can require human recovery; no runtime rollback guarantee is claimed.

A restored old wrapper may refuse a newer checkout. That is the intended integrity check; do not edit a hash or weaken it. A mixed policy/wrapper/helper snapshot fails closed. Confirm ordinary sudo remains usable; do not alter global use_pty or /etc/sudoers.

## Run once at the physical Linux console

Leave prior metadata/diagnostic result files alone. This trial has a new fixed result path. It must be absent; stop if it already exists or is a symlink. Do not delete an unknown target to rerun.

At the direct Linux VT, no SSH/GUI/multiplexer, no redirects, pipes or environment assignments:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --crash-test
```

Only sudo may ask for its ordinary human authentication password. The project program never requests input. It creates its synthetic random material internally and never prints it. Do not attach a debugger, recorder or log collector to the worker.

The trial should complete in roughly seconds, with a 20-second collection deadline plus bounded cleanup; initial metadata checks have their existing timeouts. A stuck kernel task or failed cleanup is a failure, not permission to kill broad process groups or reboot. Do not interrupt unrelated workloads.

The fresh-result notification identifies a new bounded synthetic trial result. Return only this validated fixed artifact over SSH:

```bash
test ! -L /var/tmp/ai-invest-crash-qualification.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-crash-qualification.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-crash-qualification.json
```

Preliminary metadata refusal may retain diagnostic-mode shape. If the trial executes, mode is crash-test; results contain only fixed categories and PASS/FAIL/NOT_TESTED/NOT_APPLICABLE values. A successful narrow trial still returns exit **1**, checks_passed=false and failed_checks=[coverage_incomplete]. An observed failed local check returns crash_trial_failed. Both authorization flags are always false. No canary value, hash, PID, host identity, environment value, file content or raw error is returned.

## Deliberate rollback after successful installation

This removes only the known project policy exception, restoring normal sudo PTY behavior for both test commands. It does not remove global sudo access, reviewed source or root-only recovery copies. The installed code remains inactive under the extra grant and cannot bypass ordinary root/TTY checks. No new broad permission is introduced.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '034f04c6c18cbf2c1d4a84794b97d18e72553d02814b555bf5c671e302d12bae  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

## Stop boundary

No LUKS/OpenBao initialization, real encryption/recovery material, broker connection or production service is permitted. Do not prepare or execute secret bootstrap on the strength of this partial result. Review attributable collector/log observation and human input-path gaps separately. PR #14 remains DRAFT and unmerged.
