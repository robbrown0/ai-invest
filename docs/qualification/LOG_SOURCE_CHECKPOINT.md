# Human Checkpoint — Read-only Log Source and Setup Gate

**Status:** Prepared, NOT installed/run by agents. Gate 2 NOT PASSED.

Read [the exact scope, matrix and historical trial](LOG_SOURCE_QUALIFICATION.md) and [independent review](LOG_SOURCE_REVIEW.md) before installation. This supersedes the next-run instructions in OBSERVATION_CHECKPOINT.md, whose old bytes/results remain historical evidence.

## What one new checkpoint can and cannot prove

The same short --crash-test command repeats its necessary prechecks and collects all independent setup stages. It proceeds to a **new** random-canary/crash trial only if setup_journal, setup_log_directory, setup_log_file and setup_crash_store all PASS. The canary then stays in protected memory for the existing ten-second post-crash observation. It can test the existing local controls and the defined journal fields/new Apport interval/crash-store event window. It does not read historical crash contents or broad unrelated logs; new Apport interval headers can be parsed transiently for attribution, as explicitly scoped in the design.

It cannot prove absence under a compromised kernel/root, unlimited collector/log delay, unstructured unattributable logging, raw swap-byte forensics, or future typed secret input/services. It never authorizes a secret. **Overall checks_passed=false / coverage_incomplete is still expected even when every implemented finite check passes.** Actual leak/local-control failure is different: crash_trial_failed. Both flags stay false.

A failed required setup emits only fixed failed stage identifiers; a dependent unattempted file stage is NOT_TESTED. No new canary or deliberately crashing child is created on setup failure. API presence alone never means journal setup PASS. The log-directory policy includes fixed account-group lookup, descriptor-relative path checks, access-ACL absence and a mutation watch; these actual-host checks remain unverified.

No extra standalone metadata run is needed. Routine administration remains SSH-based; the one synthetic crash run remains physical-console-only.

## Exact reviewed artifacts

Previously human-tested source: **531671a5e6e3bf8c7efc3bddb899c53d53cd1c27**. Compare the current clean checkout commit with the full amendment SHA in the completion report before proceeding. Exact hashes below protect the executable inputs, independent of a moving branch name.

| Artifact | Expected installed SHA-256 | New SHA-256 |
| --- | --- | --- |
| wrapper | f339e600891fcb864d50014e684c7f63d90d7dcba04612ef20336ad10644eecd | 0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf |
| harness | 68fc9bcea6fecb98a2436992f3cc13c4a4b582a39ac867d025b5bc0fc3f66927 | 8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420 |
| policy | 3864c8d21dfad3efbb6c90dc56eba55f33788a5f79329fbb6f5e99b5224a7913 | 0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8 |
| Existing metadata helper | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c | Unchanged |

Policy change is **digest only**. Same executable, exact --diagnostic or --crash-test only; PASSWD/NOSETENV/authentication, command-specific !use_pty, fixed secure_path and all other Defaults remain unchanged. No sudo grant to the helper, installer, shell, observation library or arbitrary command. No host policy installation is performed by the agent.

## One guarded upgrade from the human's SSH terminal

Use the owner's existing administrator authority, not an assistant terminal. No project secret is requested. Keep an existing administration session open. Do not run qualification or change root code/policy/packages concurrently. Stop on any discrepancy; do not blindly rerun a partial transaction. The new log-source-* recovery/candidate files and result must be absent. Prior observation-*, crash-*, path-*, environment-* copies and all old result artifacts are untouched.

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
  for path in /usr/local/libexec/ai-invest/log-source-wrapper.previous \
    /usr/local/libexec/ai-invest/log-source-wrapper.candidate \
    /usr/local/sbin/.ai-invest-log-source.pending \
    /usr/local/libexec/ai-invest/log-source-harness.previous \
    /usr/local/libexec/ai-invest/log-source-harness.candidate \
    /usr/local/libexec/ai-invest/.log-source-harness.pending \
    /usr/local/libexec/ai-invest/log-source-policy.previous \
    /usr/local/libexec/ai-invest/log-source-policy.candidate \
    /etc/sudoers.d/.ai-invest-log-source.pending \
    /var/tmp/ai-invest-crash-log-source.json; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    'f339e600891fcb864d50014e684c7f63d90d7dcba04612ef20336ad10644eecd  /usr/local/sbin/ai-invest-operator-preflight' \
    '68fc9bcea6fecb98a2436992f3cc13c4a4b582a39ac867d025b5bc0fc3f66927  /usr/local/libexec/ai-invest/crash_canary.py' \
    '3864c8d21dfad3efbb6c90dc56eba55f33788a5f79329fbb6f5e99b5224a7913  /etc/sudoers.d/ai-invest-operator-qualification' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' |
    sudo sha256sum --check -
  printf '%s\n' \
    '0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf  scripts/qualification/run_operator_preflight.py' \
    '8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420  scripts/qualification/crash_canary.py' \
    '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  infrastructure/qualification/ai-invest-operator.sudoers' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  scripts/qualification/operator_preflight.py' |
    sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/log-source-wrapper.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/log-source-wrapper.candidate
  sudo install -o root -g root -m 0600 /usr/local/libexec/ai-invest/crash_canary.py /usr/local/libexec/ai-invest/log-source-harness.previous
  sudo install -o root -g root -m 0600 scripts/qualification/crash_canary.py /usr/local/libexec/ai-invest/log-source-harness.candidate
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/log-source-policy.previous
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/log-source-policy.candidate
  printf '%s\n' \
    'f339e600891fcb864d50014e684c7f63d90d7dcba04612ef20336ad10644eecd  /usr/local/libexec/ai-invest/log-source-wrapper.previous' \
    '0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf  /usr/local/libexec/ai-invest/log-source-wrapper.candidate' \
    '68fc9bcea6fecb98a2436992f3cc13c4a4b582a39ac867d025b5bc0fc3f66927  /usr/local/libexec/ai-invest/log-source-harness.previous' \
    '8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420  /usr/local/libexec/ai-invest/log-source-harness.candidate' \
    '3864c8d21dfad3efbb6c90dc56eba55f33788a5f79329fbb6f5e99b5224a7913  /usr/local/libexec/ai-invest/log-source-policy.previous' \
    '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  /usr/local/libexec/ai-invest/log-source-policy.candidate' |
    sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      harness_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/log-source-policy.previous /etc/sudoers.d/.ai-invest-log-source.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-log-source.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/log-source-wrapper.previous /usr/local/sbin/.ai-invest-log-source.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-log-source.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/log-source-harness.previous /usr/local/libexec/ai-invest/.log-source-harness.pending &&
         /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.log-source-harness.pending /usr/local/libexec/ai-invest/crash_canary.py; then
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
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/log-source-policy.candidate /etc/sudoers.d/.ai-invest-log-source.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-log-source.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/log-source-harness.candidate /usr/local/libexec/ai-invest/.log-source-harness.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.log-source-harness.pending /usr/local/libexec/ai-invest/crash_canary.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/log-source-wrapper.candidate /usr/local/sbin/.ai-invest-log-source.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-log-source.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-log-source.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  printf '%s\n' \
    '0d5af4a077b54a132bad97aefcf148bfa8e54935cfee826a5f8bc626bfb1fcbf  /usr/local/sbin/ai-invest-operator-preflight' \
    '8f981bbf5156bae35309f991eb2239d95b1115fd0bd56c3bb8b50a55eeb87420  /usr/local/libexec/ai-invest/crash_canary.py' \
    '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  /etc/sudoers.d/ai-invest-operator-qualification' |
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

New exclusive result: **/var/tmp/ai-invest-crash-log-source.json**. Both earlier **/var/tmp/ai-invest-crash-qualification.json** and **/var/tmp/ai-invest-crash-observation.json** are never overwritten or deleted. An existing target (including symlink) refuses publication/run; do not delete it to force a rerun. Ask for an explicitly reviewed next result handling procedure instead.

Back over SSH, retrieve only the fixed sanitized artifact after checks:

```bash
test ! -L /var/tmp/ai-invest-crash-log-source.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-crash-log-source.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-crash-log-source.json
```

No canary/hash, raw record, PID, hostname, environment contents or exception text is published. An earlier-stage refusal may use diagnostic shape. Report the new JSON once and stop; retrieval is not another trial.

## Deliberate rollback

Remove only the exact known project sudo exception after checking it. Global sudo policy/access remains; installed code and root-only recovery copies remain for review. Normal sudo PTY behavior applies again to these commands too. This does not authorize a broad command runner.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '0229a4230a7f9850fa8dcfbc85d4fc328d4d2b66ac52f1aaa4ae9755850c3ad8  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

No chmod/chown or membership/ACL changes to host log/crash directories, no log contents executed/imported, and no LUKS/OpenBao initialization, real secret/recovery generation, brokerage connectivity, production services, global swap/crash changes or reboot. Do not prepare real-secret bootstrap from this still-incomplete checkpoint. PR #14 stays draft and unmerged.
