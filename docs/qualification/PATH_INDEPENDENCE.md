# Inherited PATH Independence Qualification

Subsequent evidence: the human installed this snapshot and reported a successful metadata diagnostic. See [current precise runtime evidence](CRASH_QUALIFICATION.md) and [next crash checkpoint](CRASH_CHECKPOINT.md). The pending wording and installation block below describe the earlier handoff and are historical, not current instructions.

**Status:** Source correction prepared; human upgrade/runtime checkpoint pending. Gate 2 NOT PASSED.

## Confirmed evidence and root cause

Historical sequence remains intact: physical VT3 -> ordinary sudo PTY3 -> exact-command PTY exception -> operator_environment -> environment_path. The latest human result is:

```json
{"checks_passed":false,"failed_checks":["environment_path"],"mode":"diagnostic","runtime_crash_suppression_qualified":false,"secret_entry_authorized":false}
```

TTY, installed-code integrity, operator identity and environment keyset passed far enough to reach this predicate. No later check is thereby qualified. The human supplied bounded configuration evidence: global sudo secure_path differs from the command-specific fixed path, /etc/environment defines another path, and sudo PAM uses pam_env with readenv=1 and user_readenv=0, including its locale-file invocation. No raw environment or host log was requested.

**Conclusion:** The application asserted an unnecessary exact inherited-PATH invariant. This is an over-specified application assumption, not evidence that the authenticated command grant failed. Configuration and version source establish a legitimate PAM replacement mechanism, but do not prove which source provided this individual process's PATH. No additional PATH diagnostic or accepted host-path list is needed.

## Version-specific analysis

Installed packages inspected without environment disclosure: sudo **1.9.15p5-3ubuntu5.24.04.2**, libpam-modules **1.5.3-5ubuntu5.7**; local sudoers(5) and pam_env(8). Installed strict visudo grammar validation is part of regression testing.

In the upstream matching sudo tag, command defaults are applied during set_cmnd before rebuild_env. The latter installs def_secure_path; later PAM session setup collects PAM environment and calls env_merge. With env_reset, that merge can overwrite variables not preserved by env_should_keep. The reviewed empty env_keep/env_check therefore does not make exported PATH immutable. Local manual documentation likewise describes PAM environment merging. This is version-matched source analysis, not execution tracing of the Ubuntu binary or a claim to have audited every downstream patch. See [sudoers command setup](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/sudoers.c), [environment construction and merge](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/env.c), and [PAM session integration](https://github.com/sudo-project/sudo/blob/SUDO_1_9_15p5/plugins/sudoers/auth/pam.c).

secure_path still applies during sudo's relevant command-resolution/environment construction steps. It does **not** supply the exact final exported-environment invariant this application assumed across later PAM processing. Retain it as defense in depth, not authentication evidence.

## Executable and trust-boundary trace

| Question | Source finding / decision |
| --- | --- |
| Inherited PATH executable resolution before cleanup? | None. Initial installed command is an exact absolute path with a SHA-256 sudo command digest. |
| Interpreter selection? | Kernel shebang is /usr/bin/python3 -I; the scoped invocation is /usr/bin/python3 -I -B. Neither uses env/python lookup. |
| Pre-cleanup subprocess? | Only /usr/bin/loginctl, fixed argument list, explicit CLEAN_ENV, close_fds=True; no shell. |
| Other wrapper subprocesses? | /usr/bin/systemd-detect-virt and /usr/bin/systemd-run; explicit CLEAN_ENV. Scope tools and interpreter are absolute. |
| Shell? | None before cleanup. Later fixed /bin/bash --noprofile --norc uses builtins and absolute exec; env -i supplies only fixed PATH/LANG/LC_ALL. No evaluated caller command text. |
| Python imports? | Standard-library imports; -I ignores Python environment, user-site and unsafe script/current-directory search. Inherited PATH does not select modules. Trusted system Python/NSS/root configuration remains in the host TCB. |
| Loader/Python/shell variables? | Existing exact keyset rejects LD_PRELOAD, LD_LIBRARY_PATH, PYTHONPATH, PYTHONHOME, PYTHONSTARTUP, shell startup variables and every unknown key. No expansion of that set. |
| Cleanup timing? | Kernel console, installed bytes, sudo/loginuid identity, environment predicates and local logind provenance are checked first; then os.environ is cleared/replaced before host/plan/helper work. loginctl already receives CLEAN_ENV. |
| Helper resolution? | Wrapper compiles verified installed helper bytes only after cleanup. Its former bare findmnt/lsblk names used CLEAN_ENV, not inherited PATH; now both are absolute /usr/bin paths. Its standalone shebang is also absolute isolated Python. |
| Incremental security from exact inherited PATH equality? | None for this closed execution graph. It rejected incidental state without protecting an executable selection. Removing that predicate introduces no new lookup or shell capability. |

Dynamic-loader variables act before Python's keyset test. Set-ID sudo loader filtering and trusted sudo/PAM/root configuration remain necessary startup protections; Python -I is not a loader defense. NOSETENV prevents policy bypass through authorized environment setting; env_reset is not by itself a proof of arbitrary PAM-output safety. Regression fixtures reject dangerous keys without executing a real preload. Compromised root/PAM/system interpreter and a compromised authenticated physical login remain explicit residual risks.

**Decision A (functional source correction):** remove only exact inherited PATH equality. Policy settings are unchanged; its command digest necessarily changes. Incidental inherited PATH may be absent, relative or hostile because it is never used and is discarded. Do not add host PATH values to an allowlist. Other environment predicates remain unchanged; a future mismatch requires its own evidence/review. environment_path remains a historical report identifier, not an active predicate.

Both metadata authorization flags remain false, even after all metadata checks pass. No new authorization token, privilege service or secret path is introduced.

## Guarded human-only upgrade

Old reviewed commit: **3ff68b2c91389052a7e743fe3ba5a2ef44184abe**. Confirm the clean checkout matches the new exact commit in the completion report before running this block. Root policy remains host-specific qualification infrastructure.

| Artifact | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| Wrapper | 9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb | f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719 |
| Helper | a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6 | e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c |
| Policy | 0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698 | 04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f |

Use your own SSH terminal for review/installation and ordinary sudo authentication, never an assistant-connected terminal. No project secret is requested. Do not run the diagnostic or concurrently modify root programs/policy during upgrade. Stop on any mismatch. Existing environment-* recovery snapshots are preserved; new path-* files must be absent. This block uses your pre-existing administrative permission, NOT the narrow diagnostic grant.

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
  for path in /usr/local/libexec/ai-invest/path-helper.previous \
    /usr/local/libexec/ai-invest/path-helper.candidate \
    /usr/local/libexec/ai-invest/.operator-path.pending \
    /usr/local/libexec/ai-invest/path-wrapper.previous \
    /usr/local/libexec/ai-invest/path-policy.previous \
    /usr/local/libexec/ai-invest/path-wrapper.candidate \
    /usr/local/libexec/ai-invest/path-policy.candidate \
    /usr/local/sbin/.ai-invest-path.pending /etc/sudoers.d/.ai-invest-path.pending; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  printf '%s\n' \
    '9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb  /usr/local/sbin/ai-invest-operator-preflight' \
    '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  /etc/sudoers.d/ai-invest-operator-qualification' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
  printf '%s\n' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  scripts/qualification/operator_preflight.py' \
    'f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719  scripts/qualification/run_operator_preflight.py' \
    '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  infrastructure/qualification/ai-invest-operator.sudoers' \
    | sha256sum --check -
  sudo /usr/sbin/visudo -c -s
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-operator.sudoers
  sudo install -o root -g root -m 0600 /usr/local/libexec/ai-invest/operator_preflight.py /usr/local/libexec/ai-invest/path-helper.previous
  sudo install -o root -g root -m 0600 scripts/qualification/operator_preflight.py /usr/local/libexec/ai-invest/path-helper.candidate
  sudo install -o root -g root -m 0600 /usr/local/sbin/ai-invest-operator-preflight /usr/local/libexec/ai-invest/path-wrapper.previous
  sudo install -o root -g root -m 0600 /etc/sudoers.d/ai-invest-operator-qualification /usr/local/libexec/ai-invest/path-policy.previous
  sudo install -o root -g root -m 0600 scripts/qualification/run_operator_preflight.py /usr/local/libexec/ai-invest/path-wrapper.candidate
  sudo install -o root -g root -m 0600 infrastructure/qualification/ai-invest-operator.sudoers /usr/local/libexec/ai-invest/path-policy.candidate
  printf '%s\n' \
    'a47681dbf53676d85d9e4d4c228d61b8eb337ede30082dea9e9b6891d527cfe6  /usr/local/libexec/ai-invest/path-helper.previous' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/path-helper.candidate' \
    '9cb93f000529cea003c971d8a9821773cd46ba8f359cf587d824c203d85ae7cb  /usr/local/libexec/ai-invest/path-wrapper.previous' \
    '0a57eafa0a536356f8533990f9b708396d57b5ef54b20bdb214829045bb94698  /usr/local/libexec/ai-invest/path-policy.previous' \
    'f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719  /usr/local/libexec/ai-invest/path-wrapper.candidate' \
    '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  /usr/local/libexec/ai-invest/path-policy.candidate' \
    | sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    rollback() {
      trap - EXIT HUP INT TERM
      set +e
      policy_restored=0
      wrapper_restored=0
      helper_restored=0
      if /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/path-policy.previous /etc/sudoers.d/.ai-invest-path.pending &&
         /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-path.pending /etc/sudoers.d/ai-invest-operator-qualification &&
         /usr/sbin/visudo -c -s; then
        policy_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/path-helper.previous /usr/local/libexec/ai-invest/.operator-path.pending &&
         /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.operator-path.pending /usr/local/libexec/ai-invest/operator_preflight.py; then
        helper_restored=1
      fi
      if /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/path-wrapper.previous /usr/local/sbin/.ai-invest-path.pending &&
         /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-path.pending /usr/local/sbin/ai-invest-operator-preflight; then
        wrapper_restored=1
      fi
      if test "$policy_restored:$helper_restored:$wrapper_restored" = 1:1:1; then
        printf "Upgrade refused; prior reviewed snapshots restored. No secret entry.\\n" >&2
      else
        printf "Upgrade refused; recovery requires human review. No secret entry.\\n" >&2
      fi
      exit 1
    }
    trap rollback EXIT HUP INT TERM
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/path-policy.candidate /etc/sudoers.d/.ai-invest-path.pending
    /usr/sbin/visudo -c -s -f /etc/sudoers.d/.ai-invest-path.pending
    /usr/bin/install -o root -g root -m 0644 /usr/local/libexec/ai-invest/path-helper.candidate /usr/local/libexec/ai-invest/.operator-path.pending
    /usr/bin/mv -T -- /usr/local/libexec/ai-invest/.operator-path.pending /usr/local/libexec/ai-invest/operator_preflight.py
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/path-wrapper.candidate /usr/local/sbin/.ai-invest-path.pending
    /usr/bin/mv -T -- /usr/local/sbin/.ai-invest-path.pending /usr/local/sbin/ai-invest-operator-preflight
    /usr/bin/mv -T -- /etc/sudoers.d/.ai-invest-path.pending /etc/sudoers.d/ai-invest-operator-qualification
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-operator-preflight)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /usr/local/libexec/ai-invest/operator_preflight.py)" = 0:644:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' \
    'f3e0b9bfaef110882278443f184f31501539f96b07341d0cae3fb85a2a437719  /usr/local/sbin/ai-invest-operator-preflight' \
    '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  /etc/sudoers.d/ai-invest-operator-qualification' \
    | sudo sha256sum --check -
)
```

No automatic host installation was performed. Previous/candidate copies are reviewed non-secret code, root-only and retained for recovery. This is NOT an atomic three-file transaction. Caught activation failures restore policy first, then independently attempt helper and wrapper; complete recovery is reported only when all three succeed. Power loss, I/O failure or concurrent root modification can require manual recovery. Mixed wrapper/helper/policy snapshots fail integrity/digest checks, not open a broader grant. Restoring old installed bytes against a newer checkout may also fail closed; do not edit digests to bypass that check.

## Rollback

Automatic rollback is in the guarded block. For deliberate rollback after successful installation, remove only the verified project exception using the block below; ordinary sudo remains available and the diagnostic again encounters ordinary PTY handling. Root-owned recovery snapshots remain. Do not delete global sudo configuration.

```bash
(
  set -eu
  sudo test ! -L /etc/sudoers.d/ai-invest-operator-qualification
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-operator-qualification)" = 0:440:1
  printf '%s\n' '04ab9e267cb2f632dec75b6fe19eae408b0dfec997eef4e199e3a0a68a86382f  /etc/sudoers.d/ai-invest-operator-qualification' | sudo sha256sum --check -
  sudo unlink -- /etc/sudoers.d/ai-invest-operator-qualification
  sudo /usr/sbin/visudo -c -s
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

## Next human checkpoint

The prior environment_path result above is preserved. After confirming the old probe has finished, remove only its known published non-secret diagnostic artifact. First verify it is a regular non-symlink root-owned mode 0644 single-link file; then use sudo unlink -- /var/tmp/ai-invest-operator-diagnostic.json. Stop for unknown/mismatching targets. Never remove the ordinary result. Existing files are not overwritten.

At the physical Linux console, without SSH/GUI/tmux/screen, pipes, redirects or environment assignments:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight --diagnostic
```

Only ordinary sudo may request its authentication password. The project program requests no input. Successful environment validation continues to the existing session/host/plan/scope checks; another fixed failure identifier may be returned. No success is predicted. Both flags remain false, even with checks_passed=true.

After the fresh-result notification, retrieve only the bounded artifact over SSH:

```bash
test ! -L /var/tmp/ai-invest-operator-diagnostic.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-operator-diagnostic.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-operator-diagnostic.json
```

Unrelated sudo /usr/bin/tty must still observe the ordinary PTY; no global use_pty change, authentication relaxation or alternate argument is proposed.

## Evidence, review and remaining limits

Regression procedures: /usr/bin/python3 -I -B -m unittest discover -s tests/qualification -q; strict candidate visudo parsing; inert shell transaction failure injection; documentation and bounded secret-pattern validation. See [independent adversarial review](PATH_REVIEW.md). Final measured totals are recorded below after validation.

This task does not claim a privileged runtime pass. Physical requalification, cgroup effective no-swap/current-swap checks, bounded crash-suppression tests and synthetic input-canary leakage qualification remain pending. No unrelated logs, environment, process lists, crash artifacts or real secrets were inspected. Full encrypted storage/TDE/OpenBao recovery, tenant isolation, financial simulator and functioning CI/security scanner qualifications remain Gate 2 blockers. No LUKS/OpenBao initialization, real keys, brokerage connectivity, LIVE capability or production application code is introduced. Source stays public; application stays private/LAN-only.

## Completion validation

Lead and independent reviewer each ran **109 unique automated tests**, zero skips, all PASS. The 11 new methods cover nine inherited-PATH variants, actual isolated Python startup, complete wrapper subprocess selectors, helper absolute callsites, dangerous keys, unchanged cleanup order and false flags, historical reports, nine inert activation outcomes and seven injected rollback failures. Existing tests retain policy scope, authorization, resource/result defenses and non-PATH baseline comparisons. Tests execute no privileged installer or secret operation.

The independent reviewer also successfully ran the actual read-only helper with an unusable synthetic PATH, returning only a fixed pass/fail identifier and false flags. This is unprivileged executable-resolution evidence, not protected-runtime evidence. Review disposition: suitable for the guarded non-secret human checkpoint only; no blocking source/policy finding remains.

Candidate strict visudo parsing PASS. All **16 Bash instruction blocks** across the current and historical operator documents pass bash -n without execution. Markdown validation: **57 documents**, **227 local links**, nine unchanged Mermaid declaration/fence checks PASS; no full renderer is available. git diff --check PASS.

Bounded common-secret-pattern validation PASS over **78 tracked/non-ignored working files**, index content and **120 pre-commit reachable history blobs**; matching values are suppressed. Repeat after staging/commit. PAPER/false placeholders and .env ignore remain unchanged. This is bounded pattern evidence, not a guarantee covering unrelated host logs or every possible secret.

No gitleaks, trufflehog, bandit, semgrep, trivy, shellcheck or mmdc executable is available on PATH. GitHub Actions queries returned zero runs and zero artifacts. No functioning CI/security pipeline or synthetic-canary leakage qualification is claimed. No host installation or privileged diagnostic was run by the lead/reviewer; no application production code or real credential was introduced. PR #14 remains draft and unmerged.
