# Human Checkpoint — Focused Journal Observation

**Status:** Prepared, not installed/run by agents. Gate 2 NOT PASSED. Both authorization flags remain false.

Read [the journal evidence and API limits](JOURNAL_QUALIFICATION.md) and [independent review](JOURNAL_REVIEW.md). This replaces the next-run instructions in LOG_SOURCE_CHECKPOINT.md; earlier documents, installed recovery copies and results remain historical evidence.

## One checkpoint: scope and expected result

The existing short crash-test command repeats required protections/setup and then performs one new synthetic trial with the comparison bytes retained only in protected memory. It adds journal_stage and journal_reason to the fixed sanitized result. A missing journal observation now identifies the precise attempted operation and a fixed reason; no raw error, record, boot/cursor/PID or environment data is returned. If setup fails, no canary or deliberate crash occurs.

This checkpoint can supply actual protected-context journal evidence or an actionable bounded refusal. The human-tested 55339d0 result already passed all setup/local checks, observation_window, apport_log and crash_store; the separate empty SSH probe is not matching-record or protected-context evidence. Neither is counted as a new trial.

Overall checks_passed=false and coverage_incomplete remain expected even if all implemented finite checks pass. A positive or failed control instead yields crash_trial_failed. Both secret_entry_authorized and runtime_crash_suppression_qualified stay false. Journal PASS means only the finite, attributed, API-visible first values of the fixed fields. Duplicate fields, malformed backing objects silently skipped by libsystemd, unknown/unattributable or delayed channels and future human secret input remain outside that claim. No real-secret bootstrap follows.

The guarded SSH upgrade below changes only the three reviewed project artifacts, including a digest-only sudo policy update. It does not install test fixtures or change console/identity/environment/log-directory/crash-protection mechanisms. There is no standalone generic probe and no shared-journal injection.

## Exact reviewed artifacts

Previously human-tested source: **55339d0a222d95f8b58cf373d1de14f4a51bea88**. Compare the current clean checkout commit with the full amendment SHA in the completion report before proceeding. Exact hashes below protect the executable inputs, independent of a moving branch name.

| Artifact | Expected installed SHA-256 | New SHA-256 |
| --- | --- | --- |
| wrapper | 0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf | 93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52 |
| harness | 8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420 | e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3 |
| policy | 0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8 | 7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545 |
| Existing metadata helper | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c | Unchanged |

Policy change is **digest only**. Same executable, exact --diagnostic or --crash-test only; PASSWD/NOSETENV/authentication, command-specific !use_pty, fixed secure_path and all other Defaults remain unchanged. No sudo grant to the helper, installer, shell, observation library or arbitrary command. No host policy installation is performed by the agent.

## One guarded upgrade from the human's SSH terminal

Use the owner's existing administrator authority, not an assistant terminal. No project secret is requested. Keep an existing administration session open. Do not run qualification or change root code/policy/packages concurrently. Stop on any discrepancy; do not blindly rerun a partial transaction. The new journal-* recovery/candidate files and result must be absent. Prior log-source-*, observation-*, crash-*, path-*, environment-* copies and all old result artifacts are untouched.

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
    scripts/qualification/crash_canary.py infrastructure infrastructure/qualification \
    infrastructure/qualification/ai-invest-operator.sudoers; do
    test ! -L "$path"
    chmod go-w "$path"
  done
  for path in /usr /usr/local /usr/local/sbin /usr/local/libexec /etc /etc/sudoers.d; do
    sudo test ! -L "$path"
    test "$(sudo stat -c '%u:%a' "$path")" = 0:755
  done
  sudo test ! -L /usr/local/libexec/ai-invest
  test "$(sudo stat -c '%u:%a' /usr/local/libexec/ai-invest)" = 0:700
  sudo test ! -L /usr/local/sbin/ai-invest-operator-preflight
  sudo test -f /usr/local/sbin/ai-invest-operator-preflight
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  sudo test ! -L /usr/local/libexec/ai-invest/crash_canary.py
  sudo test -f /usr/local/libexec/ai-invest/crash_canary.py
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/crash_canary.py)" = 0:644:1
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  sudo test -f /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  for path in /usr/local/libexec/ai-invest/operator_preflight.py /usr/local/libexec/ai-invest/host-id; do
    sudo test ! -L "$path"
    sudo test -f "$path"
  done
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/operator_preflight.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/host-id)" = 0:600:1
  for path in /usr/local/libexec/ai-invest/journal-wrapper.previous \
    /usr/local/libexec/ai-invest/journal-wrapper.candidate \
    /usr/local/sbin/.ai-invest-journal.pending \
    /usr/local/libexec/ai-invest/journal-harness.previous \
    /usr/local/libexec/ai-invest/journal-harness.candidate \
    /usr/local/libexec/ai-invest/.journal-harness.pending \
    /usr/local/libexec/ai-invest/journal-policy.previous \
    /usr/local/libexec/ai-invest/journal-policy.candidate \
    /etc/sudoers.d/.ai-invest-journal.pending \
    /var/tmp/ai-invest-crash-journal.json; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    '0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf  /usr/local/sbin/ai-invest-operator-preflight' \
    '8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420  /usr/local/libexec/ai-invest/crash_canary.py' \
    '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  /etc/sudoers.d/ai-invest-operator-qualification' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' |
    sudo sha256sum --check -
  printf '%s\n' \
    '93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52  scripts/qualification/run_operator_preflight.py' \
    'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3  scripts/qualification/crash_canary.py' \
    '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  infrastructure/qualification/ai-invest-operator.sudoers' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  scripts/qualification/operator_preflight.py' |
    sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/journal-wrapper.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/journal-wrapper.candidate
  sudo install -o root -g root -m 0600 /usr/local/libexec/ai-invest/crash_canary.py /usr/local/libexec/ai-invest/journal-harness.previous
  sudo install -o root -g root -m 0600 scripts/qualification/crash_canary.py /usr/local/libexec/ai-invest/journal-harness.candidate
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/journal-policy.previous
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/journal-policy.candidate
  printf '%s\n' \
    '0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf  /usr/local/libexec/ai-invest/journal-wrapper.previous' \
    '93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52  /usr/local/libexec/ai-invest/journal-wrapper.candidate' \
    '8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420  /usr/local/libexec/ai-invest/journal-harness.previous' \
    'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3  /usr/local/libexec/ai-invest/journal-harness.candidate' \
    '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  /usr/local/libexec/ai-invest/journal-policy.previous' \
    '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  /usr/local/libexec/ai-invest/journal-policy.candidate' |
    sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      harness_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/journal-policy.previous /etc/sudoers.d/.ai-invest-journal.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-journal.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/journal-wrapper.previous /usr/local/sbin/.ai-invest-journal.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-journal.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/journal-harness.previous /usr/local/libexec/ai-invest/.journal-harness.pending &&
         /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.journal-harness.pending /usr/local/libexec/ai-invest/crash_canary.py; then
        harness_restored=1
      fi
      if test "$policy_restored:$wrapper_restored:$harness_restored" = 1:1:1; then
        printf "Upgrade refused; prior reviewed three-artifact state restored. No secret entry.\n" >&2
      else
        printf "Upgrade refused; recovery requires human review. No secret entry.\n" >&2
      fi
      exit 1
    }
    trap rollback EXIT HUP INT TERM
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/journal-policy.candidate /etc/sudoers.d/.ai-invest-journal.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-journal.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/journal-harness.candidate /usr/local/libexec/ai-invest/.journal-harness.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.journal-harness.pending /usr/local/libexec/ai-invest/crash_canary.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/journal-wrapper.candidate /usr/local/sbin/.ai-invest-journal.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-journal.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-journal.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  printf '%s\n' \
    '93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52  /usr/local/sbin/ai-invest-operator-preflight' \
    'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3  /usr/local/libexec/ai-invest/crash_canary.py' \
    '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  /etc/sudoers.d/ai-invest-operator-qualification' |
    sudo sha256sum --check -
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/crash_canary.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

The final ordinary sudo tty must still report a PTY through SSH; it must not inherit the command-specific exception. This is a human verification, not a result already obtained by the agent.

Candidate and baseline aggregate syntax are validated before activation; active aggregate is validated afterward. Three-file activation is not atomic. Caught activation failures independently restore the prior policy (with syntax validation), wrapper and helper. Root-only exact-hash-checked recovery copies remain. Mixed hashes fail closed. Power loss, uncatchable termination, I/O failure or concurrent root tampering requires manual recovery, not a promise of automatic rollback. A restored old installed helper may intentionally refuse a newer checkout. Never edit pins to bypass that check.

## One run at the physical Linux console

No SSH/GUI/tmux/screen, redirects, pipes, arguments beyond the fixed mode, or environment assignments:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --crash-test
```

Only ordinary sudo authentication may ask for its password. The project program accepts no input and generates only ephemeral synthetic bytes internally. Do not attach a debugger/recorder. The worker budget is 35 seconds plus bounded cleanup and existing metadata-precheck timeouts. Any unavailable library/sink, cap, rotation, unsupported record or activity requiring broader attribution leaves coverage incomplete. Do not read broad logs to explain it.

New exclusive result: **/var/tmp/ai-invest-crash-journal.json**. Earlier **/var/tmp/ai-invest-crash-log-source.json**, **/var/tmp/ai-invest-crash-qualification.json** and **/var/tmp/ai-invest-crash-observation.json** are never overwritten or deleted. An existing target (including symlink) refuses publication/run; do not delete it to force a rerun. Ask for an explicitly reviewed next result handling procedure instead.

Back over SSH, retrieve only the fixed sanitized artifact after checks:

```bash
test ! -L /var/tmp/ai-invest-crash-journal.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-crash-journal.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-crash-journal.json
```

No canary/hash, raw record, PID, hostname, environment contents or exception text is published. An earlier-stage refusal may use diagnostic shape. Report the new JSON once and stop; retrieval is not another trial.

## Deliberate rollback

Remove only the exact known project sudo exception after checking it. Global sudo policy/access remains; installed code and root-only recovery copies remain for review. Normal sudo PTY behavior applies again to these commands too. This does not authorize a broad command runner.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

No chmod/chown or membership/ACL changes to host log/crash directories, no log contents executed/imported, and no LUKS/OpenBao initialization, real secret/recovery generation, brokerage connectivity, production services, global swap/crash changes or reboot. Do not prepare real-secret bootstrap from this still-incomplete checkpoint. PR #14 stays draft and unmerged.
