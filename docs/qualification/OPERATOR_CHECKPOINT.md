# Human Operator Checkpoint — Installed Non-Secret Wrapper

**Status:** Wrapper prepared and reviewed, NOT installed; runtime prerequisites unqualified; Gate 2 NOT PASSED.
**Purpose:** Replace the long console command with one reviewed local command while preserving every existing preflight check.

## Scope and trust boundary

The [wrapper](../../scripts/qualification/run_operator_preflight.py) is a standalone Python executable, not a shell script. It uses an isolated interpreter and invokes the unchanged [committed helper](../../scripts/qualification/operator_preflight.py) from a root-owned, hash-pinned installed snapshot. It does not duplicate its capacity/risk predicates. The approved helper comes from commit `ff75739e4bd420cd17104e34e1eb2b1cdcd54e22`, SHA-256 `a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd`.

Reviewed wrapper SHA-256: `82d6d8ec35cf7d46dfd02e76f17f9dbddae4ac7eb00ab0d8972a833484716c42`. Verify the installed copy against this value before executing it. See [independent wrapper review](WRAPPER_REVIEW.md) and [tests](../../tests/qualification/test_operator_wrapper.py). Review the current branch/PR and exact source before installation; hashes are evidence of an agreed snapshot, not a substitute for review.

No LUKS/OpenBao/broker secret is accepted or requested. No cryptographic initialization, key creation, service installation, global swap/crash-handler/Docker change or unrelated workload action exists in this wrapper. Local sudo authentication is handled only by the human, outside the assistant. Never share the sudo password or any other secret.

## 1. Human installation over SSH, after review

This is the only long step and may be pasted over SSH. Do NOT run it through an assistant-connected terminal. The checkout is intentionally fixed to `/home/rob/ai-invest` for this host-specific qualification. Changing location requires review, not a command-line override. Keep the checkout on `phase3/synthetic-qualification` and do not edit it concurrently with installation or execution.

The repository currently has group-writable paths. The commands below tighten only the exact project paths read by the wrapper, without recursion or changes to unrelated workloads. No group/other-writable exception is permitted. First installation refuses existing destination files/directories or symlinks; do not overwrite a previous installation without reviewing it. Shared installation parents must be canonical root-owned mode 0755. The project libexec directory is new and root-only.

Run this complete block from your SSH terminal after fetching/reviewing the pushed commit:

```bash
(
  set -eu
  cd /home/rob/ai-invest
  test "$(pwd -P)" = /home/rob/ai-invest
  test "$(git branch --show-current)" = phase3/synthetic-qualification
  test -z "$(git status --porcelain)"

  for path in . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py \
    scripts/qualification/run_operator_preflight.py; do
    test ! -L "$path"
  done
  chmod go-w . .git .git/config .git/HEAD scripts scripts/qualification \
    scripts/qualification/operator_preflight.py \
    scripts/qualification/run_operator_preflight.py

  for path in /usr /usr/local /usr/local/sbin; do
    test ! -L "$path"
    test "$(stat -c '%u:%a' "$path")" = 0:755
  done
  test ! -L /usr/local/libexec
  if test -e /usr/local/libexec; then
    test -d /usr/local/libexec
    test "$(stat -c '%u:%a' /usr/local/libexec)" = 0:755
  fi
  sudo test ! -e /usr/local/libexec/ai-invest
  sudo test ! -L /usr/local/libexec/ai-invest
  sudo test ! -e /usr/local/sbin/ai-invest-operator-preflight
  sudo test ! -L /usr/local/sbin/ai-invest-operator-preflight

  sudo install -d -o root -g root -m 0700 /usr/local/libexec/ai-invest
  sudo install -o root -g root -m 0644 scripts/qualification/operator_preflight.py \
    /usr/local/libexec/ai-invest/operator_preflight.py
  sudo install -o root -g root -m 0600 /etc/machine-id \
    /usr/local/libexec/ai-invest/host-id
  sudo install -o root -g root -m 0755 scripts/qualification/run_operator_preflight.py \
    /usr/local/sbin/ai-invest-operator-preflight

  printf '%s\n' \
    '82d6d8ec35cf7d46dfd02e76f17f9dbddae4ac7eb00ab0d8972a833484716c42  /usr/local/sbin/ai-invest-operator-preflight' \
    'a2914d3063c70f44f4c47d4a337a0dcd546cedc0618c1e61f424daeb3328c6bd  /usr/local/libexec/ai-invest/operator_preflight.py' \
    | sudo sha256sum --check -
)
```

Stop on any failure; a partially completed installation is not permission to run an unverified copy. Do not print/read/share `host-id`: it is a root-only local copy used to bind this installation to the host where the human performed enrollment. Neither its value nor its digest is included in the result file or Git. It is not a project encryption key, and it is not hardware attestation: cloned machine IDs or compromised host root remain outside this assurance.

## 2. At the physical Linux virtual console

Use the intended host's real `/dev/ttyN` console, with no recording, SSH, GUI terminal, tmux/screen or PTY relay. Then type only:

```bash
sudo /usr/local/sbin/ai-invest-operator-preflight
```

Do not redirect or pipe this command. It accepts no public arguments. It rejects non-root invocation, PTYs, SSH/GUI/session indicators, mismatched controlling-terminal devices, wrong host enrollment, containers/chroots/unexpected namespaces, wrong checkout/branch/origin, changed source/helper bytes, unsafe ownership/permissions and inappropriate symlinks.

The wrapper runs the existing plan check first and stops on failure. If it passes, it invokes the same dedicated systemd scope with `MemoryMax=2G`, `MemorySwapMax=0`, `TasksMax=32`, `CPUQuota=100%`, `unshare --mount --propagation private`, clean environment, isolated Python and zero soft/hard core limits. It rechecks plan inside the scope before running the operator helper. Private mount propagation is also checked from runtime mount metadata. No `--pty`, output pipe, privilege bypass or arbitrary command override is added.

**Sudo limitation:** local sudo policy may itself allocate a PTY. In that case this invocation MUST fail, even from a physical console. The wrapper does not disable `use_pty`, reopen descriptors to disguise a PTY, or weaken the existing checks. A failure is useful evidence and requires a separately reviewed input-path design, not forced success.

## 3. Back over SSH: retrieve only the sanitized result

Only after this console invocation prints `A new sanitized result is ready at /var/tmp/ai-invest-operator-preflight.json.`, retrieve its result. A refusal without that message does not establish a new safe artifact: do not read or return an unknown pre-existing file, symlink or hardlink. Before `cat`, verify that the path is a regular, root-owned mode 0644 file with one link:

```bash
test ! -L /var/tmp/ai-invest-operator-preflight.json && \
  test "$(stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-operator-preflight.json)" = '0:644:1:regular file' && \
cat /var/tmp/ai-invest-operator-preflight.json
```

The fixed path is created exclusively with no symlink following, initially root-owned mode 0600. The scoped writer must match the already-open inode, ownership, link count and private permissions. The parent validates the exact JSON schema and scope exit status before publishing only allowlisted non-secret metadata as root-owned mode 0644. A scope failure cannot publish successful metadata. No environment, history, terminal input, host identifier, arbitrary diagnostic string or unrelated service/process information is allowed into the report. Python-level stdout capture leaves the actual TTY descriptors unchanged for the helper's original checks.

Return only this JSON and whether you used the intended physical host console without recording. Both `secret_entry_authorized` and `runtime_crash_suppression_qualified` MUST remain `false`, including on successful metadata checks. An early prerequisite failure may contain only the existing sanitized `metadata_unavailable` report. Non-root invocation, an unsafe/existing output target or an I/O failure may produce no new readable file. Never substitute an old result for this run; permission denied or incomplete/private output is NOT success.

The wrapper never overwrites an existing result. For a later intentional retry, first verify that the target is a known prior wrapper metadata artifact (not an unexpected file/symlink/hardlink), preserve its non-secret result as evidence, ensure no preflight scope/process is running, and have the human remove only this exact old result. If its origin is unknown, stop and investigate without reading or returning its contents:

```bash
sudo unlink -- /var/tmp/ai-invest-operator-preflight.json
```

This removes the old local metadata file, not any project storage. Do not remove it during an active run or delete any broader directory. An interrupted run leaves no completed published assurance; investigate before retrying.

## What remains unqualified

Automated tests exercise predicates, command construction, tamper rejection, publication and mocked orchestration. They do not install/run this wrapper as root or prove actual scope memory/swap/core behavior. The historical prerequisite failure remains valid. The original [approved storage plan](APPROVED_PREREQUISITES.md) and [operator review](OPERATOR_REVIEW.md) remain historical evidence, not runtime proof.

Even a successful wrapper result does not authorize secret entry. A separate independently reviewed, bounded non-secret kernel crash/collector test must still prove that synthetic process memory is not retained. Scope existence alone does not qualify that mitigation. Only after actual runtime qualification may a guarded human-only LUKS/OpenBao procedure be finalized. No LUKS/OpenBao initialization is authorized by running this wrapper. Gate 2 remains NOT PASSED; PR #14 stays draft and unmerged.

## Repository validation evidence

All 45 qualification tests pass with Python 3.12.3; the independent reviewer also ran all 45 successfully. Four Bash instruction blocks pass `bash -n` syntax checks without execution. Wrapper hashes in these instructions and the independent review match the actual source. Read-only checks confirm the installed wrapper, project libexec directory and result path are absent: nothing was installed or run as a privileged operator.

Local validation parsed 50 Markdown files, checked 197 local links and checked declaration/fence structure for 9 unchanged Mermaid blocks (not full rendering). Common-secret-pattern scans passed across 66 source files, the index and 91 pre-amendment reachable Git-history blobs. A generic scanner initially flagged a test's false authorization boolean as a credential assignment; the fixture was rewritten as an explicit JSON-shaped dictionary and the unchanged scanner passed. No actual secret was found or introduced. Dedicated SAST/dependency/container scanning and runtime Gate 2 proof remain outstanding; these local checks do not substitute for them.
