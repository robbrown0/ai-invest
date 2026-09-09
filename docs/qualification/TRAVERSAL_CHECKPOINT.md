# Human Checkpoint — Bounded Journal Traversal Correction

**Status:** Prepared, not installed or run by agents. Gate 2 NOT PASSED. Both authorization flags remain false.

Read [the confirmed condition, before/after evidence and supported traversal argument](TRAVERSAL_QUALIFICATION.md) and [independent review](TRAVERSAL_REVIEW.md). This replaces the next-run instructions in BOOT_TIME_CHECKPOINT.md, which remains historical evidence.

## This tests the correction, not another diagnostic refinement

The existing protected crash test now advances once past same-boot out-of-window metadata without extracting excluded payloads. It keeps the original inclusive interval and all selectors. Every visited record spends the existing time/record budget. There is one seek, no retry and no upper-bound early PASS: absence requires iterator EOF, stable final change state and completed bounds. Visible timestamp regression, wrong header boot, API errors or limits remain incomplete.

The unchanged native multi-file case that previously stopped at record_before_window now detects its genuine in-window positive. Native success is not a protected-host trial. This checkpoint tests that compatibility correction on the actual host, not merely another subdivision of the known reason.

The human-tested 99dc9d5 result established a valid-interval, correctly typed, same-boot pre-window record; it did not identify the record/process or exact library branch. Preserve its entire /var/tmp/ai-invest-crash-boot-time.json artifact untouched.

Overall coverage_incomplete is still expected even when all implemented finite checks pass. Both secret_entry_authorized and runtime_crash_suppression_qualified remain false. First-value/duplicate-field, malformed-record, trusted-library/kernel/logging and finite-channel limitations remain; future human input and service qualification remain outstanding. No real-secret/bootstrap authorization follows.

Use the one guarded upgrade below from SSH, then the same short physical-console command. It changes only the project wrapper/helper and digest-pinned policy. Console/sudo/PATH/log-directory/resource/crash protections and ordinary sudo behavior are unchanged. No test fixture is installed.

## Exact reviewed artifacts

Previously human-tested source: **99dc9d518470bd54db81d6e6a4e26780947db511**. Compare the current clean checkout commit with the full amendment SHA in the completion report before proceeding. Exact hashes below protect the executable inputs, independent of a moving branch name.

| Artifact | Expected installed SHA-256 | New SHA-256 |
| --- | --- | --- |
| wrapper | 7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f | 17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5 |
| harness | d2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595 | 688b64b9c0659a34e7926091345c5734763bb2d8a53f75ed3a05edde3f749377 |
| policy | a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06 | 92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832 |
| Existing metadata helper | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c | Unchanged |

Policy change is **digest only**. Same executable, exact --diagnostic or --crash-test only; PASSWD/NOSETENV/authentication, command-specific !use_pty, fixed secure_path and all other Defaults remain unchanged. No sudo grant to the helper, installer, shell, observation library or arbitrary command. No host policy installation is performed by the agent.

## One guarded upgrade from the human's SSH terminal

Use the owner's existing administrator authority, not an assistant terminal. No project secret is requested. Keep an existing administration session open. Do not run qualification or change root code/policy/packages concurrently. Stop on any discrepancy; do not blindly rerun a partial transaction. The new traversal-* recovery/candidate files and result must be absent. Prior boot-time-*, journal-*, log-source-*, observation-*, crash-*, path-*, environment-* copies and all old result artifacts are untouched.

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
  for path in /usr/local/libexec/ai-invest/traversal-wrapper.previous \
    /usr/local/libexec/ai-invest/traversal-wrapper.candidate \
    /usr/local/sbin/.ai-invest-traversal.pending \
    /usr/local/libexec/ai-invest/traversal-harness.previous \
    /usr/local/libexec/ai-invest/traversal-harness.candidate \
    /usr/local/libexec/ai-invest/.traversal-harness.pending \
    /usr/local/libexec/ai-invest/traversal-policy.previous \
    /usr/local/libexec/ai-invest/traversal-policy.candidate \
    /etc/sudoers.d/.ai-invest-traversal.pending \
    /var/tmp/ai-invest-crash-traversal.json; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    '7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f  /usr/local/sbin/ai-invest-operator-preflight' \
    'd2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595  /usr/local/libexec/ai-invest/crash_canary.py' \
    'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  /etc/sudoers.d/ai-invest-operator-qualification' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' |
    sudo sha256sum --check -
  printf '%s\n' \
    '17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5  scripts/qualification/run_operator_preflight.py' \
    '688b64b9c0659a34e7926091345c5734763bb2d8a53f75ed3a05edde3f749377  scripts/qualification/crash_canary.py' \
    '92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832  infrastructure/qualification/ai-invest-operator.sudoers' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  scripts/qualification/operator_preflight.py' |
    sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/traversal-wrapper.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/traversal-wrapper.candidate
  sudo install -o root -g root -m 0600 /usr/local/libexec/ai-invest/crash_canary.py /usr/local/libexec/ai-invest/traversal-harness.previous
  sudo install -o root -g root -m 0600 scripts/qualification/crash_canary.py /usr/local/libexec/ai-invest/traversal-harness.candidate
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/traversal-policy.previous
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/traversal-policy.candidate
  printf '%s\n' \
    '7d5d49ad818a318d164858d31576c8e6cd9dedd45e3de5741f152c728137863f  /usr/local/libexec/ai-invest/traversal-wrapper.previous' \
    '17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5  /usr/local/libexec/ai-invest/traversal-wrapper.candidate' \
    'd2b3c8a6feb7ef872b6c1fcf44d4ba454fe48cfe35701a069b7847ba8e890595  /usr/local/libexec/ai-invest/traversal-harness.previous' \
    '688b64b9c0659a34e7926091345c5734763bb2d8a53f75ed3a05edde3f749377  /usr/local/libexec/ai-invest/traversal-harness.candidate' \
    'a1d1e98a39b2ace8d287237f3eb89ec9dae44bcf3a127eb92ac424bacc695d06  /usr/local/libexec/ai-invest/traversal-policy.previous' \
    '92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832  /usr/local/libexec/ai-invest/traversal-policy.candidate' |
    sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      harness_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/traversal-policy.previous /etc/sudoers.d/.ai-invest-traversal.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-traversal.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/traversal-wrapper.previous /usr/local/sbin/.ai-invest-traversal.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-traversal.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/traversal-harness.previous /usr/local/libexec/ai-invest/.traversal-harness.pending &&
         /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.traversal-harness.pending /usr/local/libexec/ai-invest/crash_canary.py; then
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
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/traversal-policy.candidate /etc/sudoers.d/.ai-invest-traversal.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-traversal.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/traversal-harness.candidate /usr/local/libexec/ai-invest/.traversal-harness.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.traversal-harness.pending /usr/local/libexec/ai-invest/crash_canary.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/traversal-wrapper.candidate /usr/local/sbin/.ai-invest-traversal.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-traversal.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-traversal.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  printf '%s\n' \
    '17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5  /usr/local/sbin/ai-invest-operator-preflight' \
    '688b64b9c0659a34e7926091345c5734763bb2d8a53f75ed3a05edde3f749377  /usr/local/libexec/ai-invest/crash_canary.py' \
    '92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832  /etc/sudoers.d/ai-invest-operator-qualification' |
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

New exclusive result: **/var/tmp/ai-invest-crash-traversal.json**. Earlier **/var/tmp/ai-invest-crash-boot-time.json**, **/var/tmp/ai-invest-crash-journal.json**, **/var/tmp/ai-invest-crash-log-source.json**, **/var/tmp/ai-invest-crash-qualification.json** and **/var/tmp/ai-invest-crash-observation.json** are never overwritten or deleted. An existing target (including symlink) refuses publication/run; do not delete it to force a rerun. Ask for an explicitly reviewed next result handling procedure instead.

Back over SSH, retrieve only the fixed sanitized artifact after checks:

```bash
test ! -L /var/tmp/ai-invest-crash-traversal.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-crash-traversal.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-crash-traversal.json
```

No canary/hash, raw record, PID, hostname, environment contents or exception text is published. An earlier-stage refusal may use diagnostic shape. Report the new JSON once and stop; retrieval is not another trial.

## Deliberate rollback

Remove only the exact known project sudo exception after checking it. Global sudo policy/access remains; installed code and root-only recovery copies remain for review. Normal sudo PTY behavior applies again to these commands too. This does not authorize a broad command runner.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '92846784c93c7b40d1e3aaf61b9e76a1391b57c00109f65bc10095fb558dd832  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

No chmod/chown or membership/ACL changes to host log/crash directories, no log contents executed/imported, and no LUKS/OpenBao initialization, real secret/recovery generation, brokerage connectivity, production services, global swap/crash changes or reboot. Do not prepare real-secret bootstrap from this still-incomplete checkpoint. PR #14 stays draft and unmerged.
