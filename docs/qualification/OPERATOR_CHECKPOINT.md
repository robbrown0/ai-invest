# Human Operator Checkpoint — No Secret Entry Yet

**Status:** Required non-secret operator action; Gate 2 NOT PASSED.
**Purpose:** Verify the candidate protected execution context before designing/running any secret-bearing operation.

This checkpoint does not format disks, create a volume, generate a key, prompt for a LUKS/OpenBao secret, start containers or change global swap/core handling. Do not enter or return any project secret. The only possible authentication prompt is local sudo, handled directly by the human and never through the assistant.

## Prerequisites

- Use a physical host virtual console (`/dev/ttyN`) directly on the local Ubuntu development host, not SSH, a GUI terminal, tmux/screen, `script`, an assistant terminal or other recorder/PTY relay. Confirm you are on the host, not in a container/chroot. Do not send passwords or recovery material to the assistant.
- Review the committed [preflight](../../scripts/qualification/operator_preflight.py), [regression tests](../../tests/qualification/test_operator_preflight.py) and [approved plan](APPROVED_PREREQUISITES.md). Use the clean reviewed checkout with no concurrent edits; the command executes that source as root. It is read-only and outputs selected non-secret metadata only.
- Run from the repository root. This run is NOT the future LUKS/OpenBao bootstrap session. It ends immediately after the probe. Its results do not protect any later terminal or authorize secrets.

## Human-run non-secret probe

Run the unprivileged capacity probe first:

```bash
python3 -B scripts/qualification/operator_preflight.py plan
```

If it fails, stop. If it passes, the human may run this bounded transient scope from the direct virtual console:

```bash
sudo systemd-run --scope --unit=ai-invest-operator-preflight \
  -p MemoryMax=2G -p MemorySwapMax=0 -p TasksMax=32 -p CPUQuota=100% \
  /usr/bin/unshare --mount --propagation private \
  /usr/bin/env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin \
  /bin/bash --noprofile --norc -c \
  'set -eu; ulimit -Sc 0; ulimit -Hc 0; exec /usr/bin/python3 -I -B "$1" operator' \
  ai-invest-preflight "$PWD/scripts/qualification/operator_preflight.py"
```

No `--pty` is used. The human must not substitute an SSH/PTY session when the direct-console check fails. No global sysctl, swap, Docker daemon or workload setting is changed. If sudo/systemd denies the command, stop and report the non-secret error category; do not grant blanket sudo or escalate through Docker. An existing unit with the same name also requires investigation, not automatic termination.

**Known candidate limitation:** sudo policy may itself allocate a PTY (`use_pty`), even when invoked from a physical console. In that case the direct-console predicate should fail; a passing result is not guaranteed. Do not disable global sudo protections to force a pass. Return the non-secret failure so that a direct-host operator service/input-path design can be reviewed instead. This is why the first checkpoint contains no secrets and grants no bootstrap authorization.

## Expected result and return boundary

The single JSON report should show `checks_passed: true`, memory limit 2147483648, `memory_swap_max: "0"`, `memory_swap_current: "0"`, a bounded CPU and PID limit, zero hard/soft core limits, direct virtual-console identity, namespace comparisons and a matching reviewed handler/core pattern.

Crucially, `secret_entry_authorized` and `runtime_crash_suppression_qualified` MUST both remain `false`, even on success. The probe is not a launcher or complete startup guard. It does not verify private mount propagation, prove host identity against a malicious host, qualify terminal/kernel memory, or test a kernel crash. If metadata is unreadable it returns a sanitized `metadata_unavailable`, not a success.

Return only this probe's non-secret JSON result and whether the direct-host/no-recording prerequisites were met. Never return terminal history, environment dumps, unrelated service logs, crash dumps, credentials, passphrases, shares or tokens. Do not perform LUKS/OpenBao initialization yet.

## Next dependent qualification

After a successful probe, independently review and run a separate bounded non-secret crash-suppression/propagation test in the same candidate context. It must prove the host collector cannot retain the synthetic process memory, without reading unrelated crash artifacts or changing the global collector. Source inspection is insufficient. If it fails, stop and recommend a safer operator design; do not weaken the no-core requirement.

Only after that actual proof may a guarded human-only LUKS creation/unlock procedure be finalized. Capacity/target checks and effective protections must be rechecked in the exact future secret-bearing session, not inherited as assurance from this exited probe. Container PID namespaces and crash-handler routing differ from this host-PID operator scope and require separate tests for every service/helper.
