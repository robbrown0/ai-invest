# Human-Only Dedicated Storage Initialization

**Current authorization:** The owner approves this fixed LUKS2 initialization to unblock the working V0. Prepared, not installed or executed by the agent. No OpenBao initialization, Alpaca credentials, LIVE capability or Gate 2 passage. The deferred --io-test candidate and earlier qualification evidence remain unchanged.

## Scope and safeguards

Only `/var/lib/ai-invest/qualification.luks` (fully allocated 64 GiB), `/dev/mapper/ai-invest-qualification` and `/srv/ai-invest-secure` are used. All must initially be absent, including the project parent. Runtime checks repeat local ext4/SATA/SSD ancestry, root-owned nonwritable ancestors, free-space reserve (200 GiB and 20%), allocation/size/link/inode identity, at least 4 GiB MemAvailable, and exact mapper-to-loop-to-backing-file identity before formatting/mounting. No repartition, existing encrypted storage, global swap/logging/crash change or unrelated workload is involved.

The fixed command reuses the reviewed physical-console, sudo identity/environment, login-session, host-binding and protected metadata checks. Its separate exact digest-pinned sudo exception leaves the old operator command and ordinary sudo PTY behavior unchanged. The worker has 2 GiB memory, zero effective swap/current swap, 32 tasks, one CPU, zero core limits, a private mount namespace, clean environment and a 15-minute scope ceiling. No additional descriptors enter cryptsetup. Each secret-bearing tool invocation is bounded to five minutes; failed/uncertain scope cleanup cannot publish success.

Only cryptsetup/libcryptsetup and their in-process dependencies receive the passphrase; the helper, sudo and systemd do not read or relay it. The helper disables echo and verifies it **before** cryptsetup, which then reads directly from the physical terminal. Root/kernel/terminal and trusted installed libraries remain assumptions. Cgroup controls protect userspace swap, not kernel terminal/keyring buffers. PR_SET_DUMPABLE does not survive exec; the unchanged pinned Apport private-mount/same-PID ignore path plus inherited resource/core controls is the reviewed cross-exec crash defense, not a new cryptsetup crash-trial result. Prior finite canary evidence is not relabeled as cryptsetup/input qualification. [cryptsetup 2.7 input handling](https://gitlab.com/cryptsetup/cryptsetup/-/raw/v2.7.0/src/utils_password.c)

LUKS2 uses AES-XTS 512-bit combined key size, Argon2id 1 GiB/4 passes/one lane, without adaptive down-tuning. The new mapped device alone receives ext4; discard and lazy initialization are disabled. The host supervisor publishes the mount after the private worker exits, with nodev/nosuid/noexec. All six planned subdirectories are root-only initially; later service-specific ownership is separate. This is not PostgreSQL/TDE provisioning. [cryptsetup format options](https://man7.org/linux/man-pages/man8/cryptsetup-luksformat.8.html)

## 1. Install once from your SSH terminal

Keep an existing administrator session open. Review this file, [the source](../scripts/storage_init.py), [focused independent review](reviews/STORAGE_INIT_REVIEW.md) and the completion-report commit. Do not run concurrent project/package/root-configuration changes. No project secret is entered during installation. Run this complete guarded block from your own terminal, not an assistant-controlled session:

```bash
(
  set -eu
  cd /home/rob/ai-invest
  test "$(pwd -P)" = /home/rob/ai-invest
  test "$(git branch --show-current)" = phase3/synthetic-qualification
  test "$(git remote get-url origin)" = https://github.com/robbrown0/ai-invest.git
  test -z "$(git status --porcelain)"
  printf '%s\n' \
    '12e0b405ce7c9b1d935e5ba247c96ec71e25fe7ef8e6ed23a782f7589790d0ff  scripts/storage_init.py' \
    'a6e629f355a0cb8a49c414fb2740df2eb7af57b822ce89fbc326cdfbc3e33dd8  infrastructure/qualification/ai-invest-storage-init.sudoers' | sha256sum --check -
  /usr/sbin/visudo -c -s -f infrastructure/qualification/ai-invest-storage-init.sudoers
  sudo /usr/sbin/visudo -c -s
  for path in /usr /usr/local /usr/local/sbin /usr/local/libexec /etc /etc/sudoers.d; do
    sudo test ! -L "$path"
    test "$(sudo stat -c '%u:%a' "$path")" = 0:755
  done
  sudo test ! -L /usr/local/libexec/ai-invest
  test "$(sudo stat -c '%u:%a' /usr/local/libexec/ai-invest)" = 0:700
  for path in /usr/local/sbin/ai-invest-storage-init /etc/sudoers.d/ai-invest-storage-init \
    /usr/local/sbin/.ai-invest-storage-init.pending /etc/sudoers.d/.ai-invest-storage-init.pending \
    /usr/local/libexec/ai-invest/storage-init.candidate /usr/local/libexec/ai-invest/storage-policy.candidate \
    /usr/local/libexec/ai-invest/storage-aggregate.candidate /usr/local/libexec/ai-invest/storage-policy.rollback \
    /var/tmp/ai-invest-storage-init.json; do
    sudo test ! -e "$path"
    sudo test ! -L "$path"
  done
  sudo install -o root -g root -m 0600 scripts/storage_init.py /usr/local/libexec/ai-invest/storage-init.candidate
  sudo install -o root -g root -m 0440 infrastructure/qualification/ai-invest-storage-init.sudoers /usr/local/libexec/ai-invest/storage-policy.candidate
  printf '%s\n' \
    '12e0b405ce7c9b1d935e5ba247c96ec71e25fe7ef8e6ed23a782f7589790d0ff  /usr/local/libexec/ai-invest/storage-init.candidate' \
    'a6e629f355a0cb8a49c414fb2740df2eb7af57b822ce89fbc326cdfbc3e33dd8  /usr/local/libexec/ai-invest/storage-policy.candidate' \
    '17bca7540e9e27991b379568181969b9a63609c33a7183d7b6be76d07379f1e5  /usr/local/sbin/ai-invest-operator-preflight' \
    'e3f5e14813b66a216b84c23e9261d3c888a5eacd41a626a8250eba11d435a91c  /usr/local/libexec/ai-invest/operator_preflight.py' | sudo sha256sum --check -
  sudo /bin/sh -c '
    set -eu
    umask 077
    policy_active=0
    rollback() {
      trap - EXIT HUP INT TERM
      if test "$policy_active" = 1 && test -f /etc/sudoers.d/ai-invest-storage-init && test ! -L /etc/sudoers.d/ai-invest-storage-init; then
        /usr/bin/mv -T /etc/sudoers.d/ai-invest-storage-init /usr/local/libexec/ai-invest/storage-policy.rollback
      fi
      /usr/sbin/visudo -c -s
      exit 1
    }
    trap rollback EXIT HUP INT TERM
    printf "@include /etc/sudoers\n@include /usr/local/libexec/ai-invest/storage-policy.candidate\n" > /usr/local/libexec/ai-invest/storage-aggregate.candidate
    /usr/sbin/visudo -c -s -f /usr/local/libexec/ai-invest/storage-aggregate.candidate
    /usr/bin/install -o root -g root -m 0755 /usr/local/libexec/ai-invest/storage-init.candidate /usr/local/sbin/.ai-invest-storage-init.pending
    /usr/bin/install -o root -g root -m 0440 /usr/local/libexec/ai-invest/storage-policy.candidate /etc/sudoers.d/.ai-invest-storage-init.pending
    /usr/bin/mv -T /usr/local/sbin/.ai-invest-storage-init.pending /usr/local/sbin/ai-invest-storage-init
    policy_active=1
    /usr/bin/mv -T /etc/sudoers.d/.ai-invest-storage-init.pending /etc/sudoers.d/ai-invest-storage-init
    /usr/sbin/visudo -c -s
    trap - EXIT HUP INT TERM
  '
  printf '%s\n' \
    '12e0b405ce7c9b1d935e5ba247c96ec71e25fe7ef8e6ed23a782f7589790d0ff  /usr/local/sbin/ai-invest-storage-init' \
    'a6e629f355a0cb8a49c414fb2740df2eb7af57b822ce89fbc326cdfbc3e33dd8  /etc/sudoers.d/ai-invest-storage-init' | sudo sha256sum --check -
  test "$(sudo stat -c '%u:%a:%h' /usr/local/sbin/ai-invest-storage-init)" = 0:755:1
  test "$(sudo stat -c '%u:%a:%h' /etc/sudoers.d/ai-invest-storage-init)" = 0:440:1
  sudo /usr/bin/true
  sudo /usr/bin/tty
)
```

The final ordinary sudo tty over SSH must still be a PTY. Installation has not initialized any storage. If any check fails, stop; preserve candidate files and the prior administration session. Do not remove files merely to rerun the block. No existing operator policy or recovery copy is replaced. Power loss during installation can leave partial files; source/digest/TTY guards fail closed and manual inspection is required.

## 2. Initialize at the physical Linux console

Use the existing local operator login, no SSH/GUI/tmux/screen, recording, redirect, pipe or clipboard relay. Have a strong unique passphrase and protected offline recovery custody ready. Keep at least two protected offline copies separate from future database backups; the owner remains the sole custodian, not multi-person separation. Do not type secrets until cryptsetup's passphrase prompt. The YES confirmation is also hidden because echo is disabled in advance.

```bash
sudo /usr/local/sbin/ai-invest-storage-init --initialize
```

Authenticate to sudo normally. Cryptsetup then asks for format confirmation, a new passphrase twice and the same passphrase once to unlock. The helper never receives those characters. No keyfile, environment secret, automatic unlock, /etc/fstab or /etc/crypttab entry is installed. Native KDF/filesystem work may take a few minutes under the fixed resource ceilings.

## 3. Retrieve only the result over SSH

```bash
test ! -L /var/tmp/ai-invest-storage-init.json && \
  test "$(LC_ALL=C stat -c '%u:%a:%h:%F' /var/tmp/ai-invest-storage-init.json)" = '0:644:1:regular file' && \
  cat /var/tmp/ai-invest-storage-init.json
```

Successful result is exactly `{"gate2_passed": false, "mode": "storage-init", "stage": "complete", "storage_ready": true}`. Share only that JSON. It means the fixed LUKS2 volume unlocked, ext4 mounted on the host with required options, directory/marker write-read validation passed and the scope ended. It does not prove backup recovery, TDE, OpenBao, future process protection or Gate 2. This separate authorized initialization report does not repurpose the old diagnostic's false authorization flags.

On success, the next engineering action is deployment of the isolated PostgreSQL/TDE stack and validation/application of the prepared migrations. Service-specific ownership, TDE principal-key provisioning and real PAPER integration remain work; OpenBao initialization still needs separate authorization. Normal application restarts after safe bootstrap do not require a physical console merely because this rare storage initialization did.

## Failure, rollback and recovery

- On any refusal, stop typing. A failed result gives only a fixed stage. Keep all partial files, mapping and previous artifacts. **Never rerun initialization against an existing target, delete the image to force a retry, or use luksFormat/mke2fs to recover.** No automatic crypto rollback/deletion occurs.
- Catchable interruptions stop the exact project scope; echo restoration requires the reader to be gone. SIGKILL/power loss cannot guarantee cleanup. From the retained SSH administration session check only `sudo systemctl show ai-invest-storage-init.scope -p ActiveState --value`; if still active use `sudo systemctl stop ai-invest-storage-init.scope`. Before console recovery require inactive/failed **and** the fixed `/sys/fs/cgroup/system.slice/ai-invest-storage-init.scope/cgroup.events` is absent or `sudo grep -qx 'populated 0' /sys/fs/cgroup/system.slice/ai-invest-storage-init.scope/cgroup.events` succeeds. If neither condition can be established, stop; do not type. Then `stty sane` at that console can repair terminal state; it is not memory erasure or exact restoration. If uncertain, stop for targeted recovery.
- To withdraw the new command grant, verify the installed policy hash above, move only `/etc/sudoers.d/ai-invest-storage-init` to the unused root-only `/usr/local/libexec/ai-invest/storage-policy.rollback`, then run `sudo visudo -c -s` and `sudo true`. Ordinary sudo and the old qualification policy remain intact. Leave code/candidates for inspection.
- Do not unmount while project services are using it. After confirming the exact dedicated mounted source and no services/open files, ordinary `sudo umount /srv/ai-invest-secure` (no force/lazy) and `sudo cryptsetup close ai-invest-qualification` remove access, not encrypted data. Never detach another loop device. Preserve the image. A subsequent reboot/unlock needs an unlock/mount-only guarded path, not this initializer; no service may start on the unmounted directory.
- Losing every usable passphrase/recovery copy can make the data unrecoverable. Header backups also require protected offline handling, separate from data backups; this initializer does not export header/key material. Do not share headers, keyslots, passphrases or recovery contents in Git/GitHub/chat.

## Preparation evidence

Existing plan preflight passed with all targets absent and about 432 GiB available; no storage was allocated. Installed tool versions: cryptsetup 2.7.0, util-linux 2.39.3, mke2fs 1.47.0, systemd 255, sudo/visudo 1.9.15p5. Source pins include the exact helper and native executable hashes. Candidate sudo syntax and isolated preparation tests are checked; aggregate installed configuration is necessarily validated by the human block. No initializer main/worker, cryptographic command or privileged installation was executed by the agent. A proposed non-root entrypoint refusal check was blocked by the tool safety guard and was not retried; isolated tests never execute the initializer or root tools.
