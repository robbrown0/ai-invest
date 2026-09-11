# Human Checkpoint — Boot/Time Predicate Qualification

**Status:** Prepared, not installed or run by agents. Gate 2 NOT PASSED. Both authorization flags remain false.

Review [the new evidence, reproduction and strict diagnostic decision](BOOT_TIME_QUALIFICATION.md) and [independent review](BOOT_TIME_REVIEW.md). This supersedes the next-run instructions in JOURNAL_CHECKPOINT.md. All earlier documents, results and recovery copies remain historical.

## Scope and expected outcome

The same protected crash-test command runs necessary setup/controls and one synthetic trial. It now distinguishes record_boot_mismatch, record_before_window and invalid_observation_interval. Original boot/time values, record bodies and exception messages are never published. Genuine field attribution still uses attribution_mismatch separately.

Native fixtures reproduced a systemd v255 seek fallback to a pre-window record. That is not proof of which condition occurred on the human host. **This amendment does not skip such records or fix the library fallback.** A pre-window record remains NOT_TESTED with its precise reason. No payload is read for a rejected boot/time record; an unseen later positive is not claimed searched.

The next run can complete finite journal observation or identify the exact boot/time condition preventing it. An overall incomplete result is still expected even if every implemented finite check passes. Existing final invalidation/append checks, resource bounds and positive preservation remain. Both authorization flags always stay false. No secret input, LUKS/OpenBao bootstrap or future service qualification follows.

Use one guarded SSH upgrade below, then the short physical-console command. No standalone journal probe, raw log inspection or shared-journal injection is needed. Policy changes are digest-only; working console/sudo/PATH/environment/log-source/crash protections are unchanged.

## Exact reviewed artifacts

Previously human-tested source: **24310834bf00b66273eb89c04cf88d41e8d97758**. Compare the current clean checkout commit with the full amendment SHA in the completion report before proceeding. Exact hashes below protect the executable inputs, independent of a moving branch name.

| Artifact | Expected installed SHA-256 | New SHA-256 |
| --- | --- | --- |
| wrapper | 93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52 | 7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f |
| harness | e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3 | d2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595 |
| policy | 7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545 | a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06 |
| Existing metadata helper | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c | Unchanged |

Policy change is **digest only**. Same executable, exact --diagnostic or --crash-test only; PASSWD/NOSETENV/authentication, command-specific !use_pty, fixed secure_path and all other Defaults remain unchanged. No sudo grant to the helper, installer, shell, observation library or arbitrary command. No host policy installation is performed by the agent.

## One guarded upgrade from the human's SSH terminal

Use the owner's existing administrator authority, not an assistant terminal. No project secret is requested. Keep an existing administration session open. Do not run qualification or change root code/policy/packages concurrently. Stop on any discrepancy; do not blindly rerun a partial transaction. The new boot-time-* recovery/candidate files and result must be absent. Prior journal-*, log-source-*, observation-*, crash-*, path-*, environment-* copies and all old result artifacts are untouched.

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
  for path in /usr/local/libexec/ai-invest/boot-time-wrapper.previous \
    /usr/local/libexec/ai-invest/boot-time-wrapper.candidate \
    /usr/local/sbin/.ai-invest-boot-time.pending \
    /usr/local/libexec/ai-invest/boot-time-harness.previous \
    /usr/local/libexec/ai-invest/boot-time-harness.candidate \
    /usr/local/libexec/ai-invest/.boot-time-harness.pending \
    /usr/local/libexec/ai-invest/boot-time-policy.previous \
    /usr/local/libexec/ai-invest/boot-time-policy.candidate \
    /etc/sudoers.d/.ai-invest-boot-time.pending \
    /var/tmp/ai-invest-crash-boot-time.json; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    '93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52  /usr/local/sbin/ai-invest-operator-preflight' \
    'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3  /usr/local/libexec/ai-invest/crash_canary.py' \
    '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  /etc/sudoers.d/ai-invest-operator-qualification' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' |
    sudo sha256sum --check -
  printf '%s\n' \
    '7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f  scripts/qualification/run_operator_preflight.py' \
    'd2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595  scripts/qualification/crash_canary.py' \
    'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  infrastructure/qualification/ai-invest-operator.sudoers' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  scripts/qualification/operator_preflight.py' |
    sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/boot-time-wrapper.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/boot-time-wrapper.candidate
  sudo install -o root -g root -m 0600 /usr/local/libexec/ai-invest/crash_canary.py /usr/local/libexec/ai-invest/boot-time-harness.previous
  sudo install -o root -g root -m 0600 scripts/qualification/crash_canary.py /usr/local/libexec/ai-invest/boot-time-harness.candidate
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/boot-time-policy.previous
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/boot-time-policy.candidate
  printf '%s\n' \
    '93b9f97e9b145a30c271d2c9cce945e9c242da68ce536cccb764ccc8e26e9e52  /usr/local/libexec/ai-invest/boot-time-wrapper.previous' \
    '7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f  /usr/local/libexec/ai-invest/boot-time-wrapper.candidate' \
    'e7416c4068b753f030d7e0a456e42d8479960872bf3b44226a7d55c9a8fb50e3  /usr/local/libexec/ai-invest/boot-time-harness.previous' \
    'd2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595  /usr/local/libexec/ai-invest/boot-time-harness.candidate' \
    '7dc50252e79ccadad5e61217e7b727d3e4821192a957a9eddf4a381c9c57d545  /usr/local/libexec/ai-invest/boot-time-policy.previous' \
    'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  /usr/local/libexec/ai-invest/boot-time-policy.candidate' |
    sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      harness_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/boot-time-policy.previous /etc/sudoers.d/.ai-invest-boot-time.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-boot-time.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/boot-time-wrapper.previous /usr/local/sbin/.ai-invest-boot-time.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-boot-time.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/boot-time-harness.previous /usr/local/libexec/ai-invest/.boot-time-harness.pending &&
         /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.boot-time-harness.pending /usr/local/libexec/ai-invest/crash_canary.py; then
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
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/boot-time-policy.candidate /etc/sudoers.d/.ai-invest-boot-time.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-boot-time.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/boot-time-harness.candidate /usr/local/libexec/ai-invest/.boot-time-harness.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.boot-time-harness.pending /usr/local/libexec/ai-invest/crash_canary.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/boot-time-wrapper.candidate /usr/local/sbin/.ai-invest-boot-time.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-boot-time.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-boot-time.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  printf '%s\n' \
    '7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f  /usr/local/sbin/ai-invest-operator-preflight' \
    'd2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595  /usr/local/libexec/ai-invest/crash_canary.py' \
    'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  /etc/sudoers.d/ai-invest-operator-qualification' |
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

New exclusive result: **/var/tmp/ai-invest-crash-boot-time.json**. Earlier **/var/tmp/ai-invest-crash-journal.json**, **/var/tmp/ai-invest-crash-log-source.json**, **/var/tmp/ai-invest-crash-qualification.json** and **/var/tmp/ai-invest-crash-observation.json** are never overwritten or deleted. An existing target (including symlink) refuses publication/run; do not delete it to force a rerun. Ask for an explicitly reviewed next result handling procedure instead.

Back over SSH, retrieve only the fixed sanitized artifact after checks:

```bash
test ! -L /var/tmp/ai-invest-crash-boot-time.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-crash-boot-time.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-crash-boot-time.json
```

No canary/hash, raw record, PID, hostname, environment contents or exception text is published. An earlier-stage refusal may use diagnostic shape. Report the new JSON once and stop; retrieval is not another trial.

## Deliberate rollback

Remove only the exact known project sudo exception after checking it. Global sudo policy/access remains; installed code and root-only recovery copies remain for review. Normal sudo PTY behavior applies again to these commands too. This does not authorize a broad command runner.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' 'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

No chmod/chown or membership/ACL changes to host log/crash directories, no log contents executed/imported, and no LUKS/OpenBao initialization, real secret/recovery generation, brokerage connectivity, production services, global swap/crash changes or reboot. Do not prepare real-secret bootstrap from this still-incomplete checkpoint. PR #14 stays draft and unmerged.
