# Initial protected Alpaca PAPER provisioning

Status: SSH-capable in-place upgrade prepared and independently reviewed; it is
**not installed or run with credentials**.
The owner authorized this narrow PAPER bootstrap. Gate 2 and the historical
qualification flags remain false; this is not LIVE authorization or a claim that
the deferred recovery-output/--io-test qualification passed.

## One human procedure

Keep an existing administrator SSH session open. The original physical-console
installer has already run, so do not use the fresh-install mode. Review the
completion commit and [security review](reviews/PAPER_PROVISION_REVIEW.md). Do
not run concurrent root configuration changes. The upgrade verifies the exact
old helper/policy hashes, ownership, modes, link counts and non-symlink state;
it stages the new fixed files, validates the candidate and a replacement-aware aggregate sudo configuration (the old policy is substituted exactly once),
keeps exact version-qualified rollback copies (while validating and preserving any prior legacy rollback set), writes a root-owned integrity-checked installed-version manifest, and does not read or create credentials.

From your own SSH terminal:

```bash
cd /home/rob/ai-invest &&
test "$(git branch --show-current)" = phase3/synthetic-qualification &&
test "$(git remote get-url origin)" = https://github.com/robbrown0/ai-invest.git &&
test -z "$(git status --porcelain)" &&
printf '%s
' '1f402de3d868e3f22dfef625467f9bb56a2aa43c683bbb1c1f0a6d7ba55a97dd  scripts/install_paper_provision.py' | sha256sum --check - &&
sudo /usr/bin/python3 -I -B /home/rob/ai-invest/scripts/install_paper_provision.py --upgrade &&
sudo /usr/local/sbin/ai-invest-paper-provision --ssh
```

Expected non-secret installer state: `upgraded_not_provisioned`, followed by the
hidden SSH prompts. If it refuses, the sanitized JSON includes only a bounded `failure_stage` identifier, including the pre-credential runtime stages (for example `ssh_session`, `worker_host_binding` or `input_ready`); stop and report that stage. Do not delete files or retry with a different command. No privileged change has been performed by the assistant.
Ordinary sudo retains its existing PTY policy, and the no-argument physical
command remains available.

At your normal SSH terminal, with a PTY allocated (`ssh -t`), use the existing
approved local operator login. Do not use a GUI relay, tmux, screen, recording,
redirection or a pipe. Use normal SSH host-key verification; do not disable
known-host checking or use a terminal/session recorder:

```bash
sudo /usr/local/sbin/ai-invest-paper-provision --ssh
```

Enter the ordinary sudo password only at sudo's prompt. The protected helper validates the SSH logind session before entering its bounded systemd scope; the scoped worker retains terminal and resource checks but does not repeat logind `show-session self` after systemd has moved it into a scope. The protected helper
then asks for the literal disposable **PAPER-CHECK** with echo disabled. Only
after that succeeds, enter the **Alpaca PAPER API key and secret** at its two
hidden prompts. Never put them in a shell command, clipboard relay, browser
form on HTTP, chat, screenshot, environment file or diagnostic output. No LIVE
key belongs here. Input is bounded to 180 seconds; Ctrl-C/EOF cancels. Catchable
interruptions restore terminal settings. If killed or the terminal is left
unusable, stop typing credentials; use the still-open trusted administrator
session to recover the console/login and restore terminal settings before reuse.
SIGKILL, host loss and terminal/kernel buffers are not magically cleaned up.

Successful fixed result:

```json
{"mode":"paper-credential-stage","staged":true,"connected":false,"gate2_passed":false,"secret_entry_authorized":false,"runtime_crash_suppression_qualified":false}
```

Return **only that non-secret status**, never the credentials. UNKNOWN/refusal
does not mean nothing was written: preserve the protected files for scoped
recovery. This command is initial-only; it cannot overwrite a previous candidate
or rotate an existing connection. Never print or inspect the candidate contents.

After successful staging, the prepared execution worker can perform validation
back in the SSH terminal from `/home/rob/ai-invest` (or leave this to the assistant
after reporting `staged=true`):

```bash
docker compose -f infrastructure/web/paper-bootstrap.yaml run --rm --no-deps activate
```

It returns only bounded connection/read booleans, never account values or secrets.
No automatic retry is permitted after an ambiguous result. The assistant can run
this next step once the human reports successful staging. Connected is recorded
only after actual fixed PAPER account, positions, recent orders and market-clock
reads; an optional SPY IEX quote may be unavailable. This is **not** order/fill
reconciliation or order submission. Current HTTP still cannot display private
financial data or approve trades: protected, authenticated browser access remains
a separate prerequisite, with TLS automation still deferred.

## Exact scope and protection

The new command-only sudoers file is
`/etc/sudoers.d/ai-invest-paper-provision`; its grant is one digest-pinned
`/usr/local/sbin/ai-invest-paper-provision` with either no arguments (physical
console) or exactly `--ssh`, PASSWD/NOSETENV, fresh authentication and
command-scoped PTY/I/O-log exceptions. No global sudo,
swap, crash, logging or existing operator policy changes. No --io-test grant.
Root-owned pinned terminal/storage helper copies are under the existing protected
`/usr/local/libexec/ai-invest` directory. No user-selected executable/path/tenant.

The root input worker reuses current SSH-PTY (or physical-console), login/session, operator,
environment and host checks. SSH mode binds the foreground `/dev/pts/N` to the
active remote logind session's same TTY, UID, service (`ssh`/`sshd`) and remote
state; it rejects GUI/tmux/screen indicators and malformed duplicate metadata.
Before plaintext input it checks effective 512MiB
memory, zero swap.max/current, 32 tasks, half a CPU, core0, private mounts and
non-dumpable state. It repeats applicable controls before publication. It does
not exec, fork, network, invoke Docker or relay plaintext to its parent after
input. The approved SSH exception necessarily adds the local SSH client, encrypted
SSH transport, server sshd/session path and terminal buffers as trusted plaintext
holders; their recording, kernel-buffer, swap and crash/core-retention behavior is
outside the worker cgroup checks and is **not qualified by this procedure**. The
pre-input parent and application/model processes contain no credential bytes. No
claim of reliable Python memory zeroization is made.

Only `/srv/ai-invest-secure/runtime/paper-credentials` is created: UID10003/GID26,
0700, on the verified dedicated LUKS2 filesystem. Exclusive 0600 initial staging
is fixed to `ai_web_a` and PAPER. The keyring/PGDATA remain separate and unchanged.
File descriptors, no-follow opens, inode/link checks and fsync protect publication;
the credential-owning execution UID remains a trusted writer, not an adversary
these checks can defeat after full compromise.

The separate non-root execution worker gets the file through its encrypted mount,
not Docker stdin/argv/environment. Its pre-main native guard, no-swap/core controls,
encrypted mounts and PostgreSQL peer/TDE/FORCE-RLS checks precede file reading.
HTTP/TLS libraries and DNS threads run inside that same protected process/cgroup;
no child process receives credential plaintext. Only fixed HTTPS PAPER/data GET
URLs are available; no proxy, redirects, shell or order API. Credentials never
enter SQL or research. Validated snapshots and an immutable credential reference
are saved with an audit event; the fixed authenticated-operator actor is a
namespaced SHA256 marker, **not** an impersonated browser/client-certificate or
physical-presence identity. Ambiguous
commits preserve candidate/version files and stop. Initial staging remains a
protected local recovery copy, not an independent/off-host backup.

This is the explicitly approved single-host PAPER file-vault direction, not
OpenBao, external KMS, future production secret-management approval, or a new
universal crash-retention qualification. Actual tools, independent recovery,
credential rotation/revocation and future deployments require their own controls.
The current prompt accepts no real encryption/unseal/recovery material.

## Upgrade rollback

Before disabling the new grant, keep the administrator session open and recheck
the installer hash above. Run from that human SSH terminal:

```bash
sudo /usr/bin/python3 -I -B /home/rob/ai-invest/scripts/install_paper_provision.py --rollback-upgrade
sudo /usr/sbin/visudo -c -s
sudo /usr/bin/tty
```

Rollback verifies the current new artifacts and exact protected rollback copies,
then atomically restores only the previous helper/policy files and validates
aggregate policy. It never opens the credential directory. It leaves all
credentials, unrelated policies and historical artifacts intact. The last
ordinary sudo call over SSH must still observe a PTY; this checks ordinary sudo
usability, not independent proof of use_pty (SSH already supplies a PTY).
Rollback is **not broker-key revocation**; revoke
compromised keys through Alpaca's own authenticated dashboard. Partial installation
or unexpected file replacement requires inspection, not destructive automatic
cleanup or a broadened grant.

## Evidence for this slice

- 129 V0, 282 preserved qualification, 30 protected-container web and 11 LAN
  regression tests passed (452 total). New tests use synthetic values only.
- Independent review reran 20 provisioning/installer and 30 web/activation tests;
  separate substitution fixtures and installed visudo grammar validation passed.
- Real encrypted PostgreSQL accepted the corrected actor, rejected the old invalid
  actor, and rolled back all synthetic rows (`tests/web/runtime_actor.py`).
- Frontend real Chromium fixture tests passed 66 assertions across desktop,
  tablet and phone sizes. This is not actual Safari/device or broker evidence.
- No privileged credential-entry trial or actual Alpaca request has occurred.
  No source/news/scanner/strategy performance capability is implied by the UI.

Clock read semantics follow the [official Alpaca PAPER clock reference](https://docs.alpaca.markets/us/v1.1/reference/getclock-1).
