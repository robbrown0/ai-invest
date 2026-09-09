# Bounded Environment Diagnostic Checkpoint

**Status:** Non-secret refinement prepared; human upgrade/refined runtime result pending; Gate 2 NOT PASSED.

## Evidence and limits

The human installed the command-specific policy and ran the physical-console diagnostic. The returned result was:

```json
{"checks_passed":false,"failed_checks":["operator_environment"],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

This is progress beyond TTY, installed-helper integrity and operator-identity validation in the current source order. It is NOT a successful environment, console-session, host, scope, no-swap or crash qualification. The first environment subpredicate remains **UNKNOWN**. No raw environment, sudo logs, session data or credentials were requested or inspected. The prior VT3 -> sudo PTY3, generic metadata and tty_identity failures remain historical evidence under this directory and in Git.

## Exact refinement and unchanged acceptance

The wrapper returns only the first failing identifier, in this order:

| Fixed identifier | Existing predicate, unchanged |
| --- | --- |
| environment_keyset | All inherited keys belong to the existing source allowlist; no extra-key name is returned |
| environment_path | PATH is present and exactly the reviewed fixed secure path |
| environment_locale | LANG then LC_ALL satisfy the existing ASCII/length pattern, including previous absent/empty behavior |
| environment_term | TERM satisfies that same existing pattern |
| environment_home | HOME is absent or equals the existing root-home expectation |
| environment_user | USER is absent or matches the existing target-user expectation |
| environment_logname | LOGNAME is absent or matches the existing target-user expectation |
| environment_mail | MAIL is absent or matches the existing target-mail expectation |
| environment_shell | SHELL is absent or one of the two existing fixed shell paths |
| environment_sudo_gid | SUDO_GID matches the existing account-database comparison |

No value, unknown key name, exception text, path, locale, username, group ID or terminal string enters diagnostic JSON. A metadata acquisition exception inside a predicate maps to that same fixed identifier. Other unexpected errors retain the coarse operator_environment label. Ordinary output and successful diagnostic shape are unchanged. If every predicate passes, execution continues to the existing console-session and later checks; both authorization flags remain false.

## Sudo behavior and clean-environment decision

Version-matched installed sudoers(5) documentation for sudo/visudo **1.9.15p5**, grammar **50**, describes env_reset as a minimal environment, not this application's exact key/value set. Target-user initialization, PAM environment and configured environment files may contribute entries. NOSETENV prevents using command-line environment-setting permission to bypass policy checks; it does not prove a particular inherited keyset. secure_path supplies the reviewed path under applicable policy. Actual secure-path behavior at this failed checkpoint is not yet known because keyset evaluation precedes it.

The diagnostic must precede remediation. If a returned symbol indicates a mismatch, compare only bounded booleans against the installed-version behavior and reviewed effective policy; classify it as an application assumption, policy error, platform behavior or unsafe input. Do not guess MAIL, PATH or an extra variable from this coarse report. Even a keyset symbol will not identify its unknown key; any further classification must itself be finite/reviewed, never a request for an environment dump.

No expectation is removed or relaxed in this amendment. HOME/MAIL/SHELL are incidental to the later fixed-command child, and target-account defaults may differ from hardcoded assumptions. Once bounded evidence identifies the mismatch, removing such unnecessary dependencies may be better than accepting more values. That is a future reviewed correction, not a hidden widening in a diagnostic change.

The existing trust transition remains: isolated Python at an absolute path -> kernel VT and installed-code checks -> sudo-bound identity/audit-login validation -> strict inherited-environment predicates -> current local logind session -> clear inherited environment -> fixed PATH/LANG/LC_ALL only -> host/plan -> fixed systemd/unshare child with env -i and isolated Python. The logind subprocess already receives that clean environment. Identity fields are validated before they are discarded. No additional re-exec or inherited authorization token is added; the bounded child already starts in a clean environment, so another launcher would add complexity without diagnosing this failure.

Python -I ignores PYTHON* settings and user-site imports; it is not an OS-environment sanitizer. Dynamic-loader variables act before Python can reject them: trusted sudo/set-ID loader handling and reviewed policy must protect startup. A later keyset refusal is defense in depth, not retroactive prevention of LD_PRELOAD execution. No real loader injection is attempted. The wrapper never executes a caller's shell, PATH lookup or Python module path. Existing root/kernel/PAM and compromised-console residuals still apply.

## Reviewed snapshots and guarded human-only upgrade

Old reviewed commit: `41d4721e7d4ffaceba1033f0bd45717281d22977`.
New reviewed commit: use the exact commit in this amendment's completion report; confirm the clean checkout matches it before running anything.

| Artifact | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| Wrapper | a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8 | 9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb |
| Sudoers policy | 9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184 | 0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698 |

Helper remains unchanged: `a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6`. The policy change is **digest only**: exact argument/path, authentication, environment controls, command-specific PTY settings and all unrelated sudo behavior are unchanged.

From your own SSH terminal after review, run the complete block below. Do not use an assistant-connected terminal for sudo authentication. Do not run project diagnostics or concurrently change root policy/programs during upgrade. The block requires the known installed old pair, preserves verified root-only source/policy recovery copies, stages the new pair, and uses one fixed authenticated activation/rollback transaction. It grants no shell/installer permission through the diagnostic policy. Old installation instructions expecting an absent policy are obsolete.

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
  for path in /usr/local/libexec/ai-invest/environment-wrapper.previous \
    /usr/local/libexec/ai-invest/environment-policy.previous \
    /usr/local/libexec/ai-invest/environment-wrapper.candidate \
    /usr/local/libexec/ai-invest/environment-policy.candidate \
    /usr/local/sbin/.ai-invest-environment.pending /etc/sudoers.d/.ai-invest-environment.pending; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    'a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8  /usr/local/sbin/ai-invest-operator-preflight' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  /etc/sudoers.d/ai-invest-operator-qualification' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
  printf '%s\n' \
    '9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb  scripts/qualification/run_operator_preflight.py' \
    '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  infrastructure/qualification/ai-invest-operator.sudoers' \
    | sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/environment-wrapper.previous
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/environment-policy.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/environment-wrapper.candidate
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/environment-policy.candidate
  printf '%s\n' \
    'a72e866e3c7a84d24ef7c2fbfd21f535c9c03e1eface455daa46204a1f4500d8  /usr/local/libexec/ai-invest/environment-wrapper.previous' \
    '9a69deefade661777bc70f232f9c45dc94931c133e02eda74267999e23c2f184  /usr/local/libexec/ai-invest/environment-policy.previous' \
    '9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb  /usr/local/libexec/ai-invest/environment-wrapper.candidate' \
    '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  /usr/local/libexec/ai-invest/environment-policy.candidate' \
    | sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/environment-policy.previous /etc/sudoers.d/.ai-invest-environment.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-environment.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/environment-wrapper.previous /usr/local/sbin/.ai-invest-environment.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-environment.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if test "$policy_restored:$wrapper_restored" = 1:1; then
        printf "Upgrade refused; prior reviewed pair restored. No secret entry.\\n" >&2
      else
        printf "Upgrade refused; recovery requires human review. No secret entry.\\n" >&2
      fi
      exit 1
    }
    trap rollback EXIT HUP INT TERM
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/environment-policy.candidate /etc/sudoers.d/.ai-invest-environment.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-environment.pending
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/environment-wrapper.candidate /usr/local/sbin/.ai-invest-environment.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-environment.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-environment.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' \
    '9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb  /usr/local/sbin/ai-invest-operator-preflight' \
    '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  /etc/sudoers.d/ai-invest-operator-qualification' \
    | sudo sha256sum --check -
)
```

Stop on any discrepancy. The root-only previous/candidate files are non-secret reviewed program/policy copies retained for recovery, not permission to execute alternate paths. Do not rerun an absent-target upgrade blindly. The host marker/helper are not changed. Uncatchable termination/power failure can still interrupt the two-file upgrade; a mixed pair should deny the exact-command exception by digest, not grant broader access. Recovery remains human-only, and actual power-loss/rollback qualification is not claimed.

Rollback restores and validates the previous policy before attempting the previous wrapper, and attempts both independently. A wrapper-copy failure must not prevent policy recovery or conceal a partial recovery. If the old policy restores but the wrapper does not, ordinary sudo can remain available while the mismatched diagnostic digest refuses execution. An underlying I/O or policy-restoration failure still requires human recovery; no runtime recovery guarantee is inferred from mocked tests.

Even a fully restored old installed pair may refuse the newer checkout's bytes. That is the existing integrity boundary, not a reason to edit expected digests. Stop for reviewed snapshot recovery rather than trying to run an old wrapper against a changed checkout.

For normal rollback after successful installation, verify the new policy is the known root-owned mode 0440 single-link non-symlink file with the new hash above. Then use the exact removal procedure below in your own terminal; this removes only the project exception, leaving the diagnostic wrapper fail-closed under ordinary PTY behavior. Source and verified prior copies remain available. Do not delete global sudo configuration or manually edit digests.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

## Next physical-console checkpoint

First preserve the reported failed result as history and confirm the old probe is finished. For the known prior diagnostic artifact only, verify non-symlink, regular file, root owner, mode 0644 and one link before the human removes that exact obsolete file with `sudo unlink -- /var/tmp/ai-invest-operator-diagnostic.json`. Never read/delete an unknown target or remove the ordinary result.

At the physical Linux VT, with no SSH/GUI/multiplexer/recording, run:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --diagnostic
```

No extra arguments, environment assignments, pipes or redirects. Only sudo may ask for its ordinary human password; the project program never requests input. Expected failure shape (illustration, NOT the identified cause):

```json
{"checks_passed":false,"failed_checks":["environment_keyset"],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

A different fixed predicate or later boundary may be returned. All-pass metadata has checks_passed=true and an empty failed_checks list, with both authorization flags still false. Return only the newly published bounded JSON. Following the fresh-result notification, retrieve over SSH:

```bash
test ! -L /var/tmp/ai-invest-operator-diagnostic.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-operator-diagnostic.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-operator-diagnostic.json
```

Unrelated `sudo /usr/bin/tty` must still use a PTY; exact diagnostic still requires fresh authentication. No global use_pty change is proposed. No refined runtime result is available yet. [Independent review](ENVIRONMENT_REVIEW.md) and the regression suite distinguish synthetic tests from human runtime evidence. No LUKS/OpenBao initialization, keys, recovery material, real secret, Alpaca connection or LIVE capability is introduced. Gate 2 remains NOT PASSED; all original downstream qualification blockers remain.

## Completion validation

The lead and independent reviewer each passed **98 tests**, zero skips, using `python3 -I -B -m unittest discover -s tests/qualification -q` (the reviewer used the equivalent documented no-bytecode invocation). Twenty new methods extend the previous 78-test suite. Relevant evidence includes 107 baseline environment comparisons, first-failure/schema tests, isolated-Python synthetic startup, authorization-before-cleaning order, digest-only policy comparison, seven inert upgrade paths and five injected rollback failures. ER-01 was corrected after independent challenge; no runtime recovery pass is claimed.

The installed strict visudo parser passes the candidate. All **12 Bash instruction blocks** across current and historical checkpoint documents pass `bash -n` without execution. Markdown validation parsed **55 documents**, checked **223 local links** and the declarations/fences of **9 unchanged Mermaid blocks**; no full Mermaid renderer is available. `git diff --check` passes.

Common-secret-pattern validation passes over **75 tracked/non-ignored source files**, staged content and **111 pre-commit reachable history blobs**, without printing matching values. The same bounded scan is repeated after staging and commit. No real secret was introduced or found within that scope. Bootstrap PAPER/false placeholders remain unchanged, `.env` remains ignored, and edits remain qualification-only. These checks do not inspect unrelated host logs or prove universal secret absence.

No gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck or mmdc executable was available on PATH. GitHub Actions returned zero runs and zero artifacts. No scanner pipeline or canary leakage pass is claimed. Agents did not install the upgraded wrapper/policy, execute a privileged probe, initialize LUKS/OpenBao or connect to a brokerage. The source repository remains public; application access remains private/LAN-only.
