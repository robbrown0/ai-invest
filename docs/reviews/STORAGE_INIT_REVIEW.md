# Independent Review — Human-Only Storage Initialization

**Scope:** The owner-authorized, fixed-target LUKS2 initialization procedure. No initializer, cryptographic operation, privileged installation or secret entry was performed by this reviewer. The reviewer did not author the implementation, tests, policy or checkpoint; this review is the reviewer's only repository edit.

**Disposition:** No blocking finding remains for the reviewed human-only preparation and handoff under the stated trust assumptions. Actual initialization and runtime success remain unperformed, not approved by passing unit tests. This disposition does not approve OpenBao, credentials, future processes or Gate 2.

## Findings and disposition

The review challenged destructive target selection, executable/argument scope, inherited protections across exec, terminal cleanup and host mount publication. It did not reopen the working console, PATH, journal or deferred IO candidate.

| Finding | Resolution |
| --- | --- |
| ST-01: cryptsetup exec does not inherit Python's non-dumpability. | Documentation distinguishes inherited cgroup/rlimit/namespace controls from PR_SET_DUMPABLE. The unchanged pinned Apport namespace branch is the cross-exec defense; no new cryptsetup crash trial is claimed. |
| ST-02: upstream cryptsetup 2.7.0 does not check its terminal echo-setting return value. | Supervisor disables and reads back ECHO/ECHONL before launching the tool. It never reads or relays passphrase bytes. |
| ST-03: child termination errors could skip terminal restoration; returning launcher failure could leave scope cleanup ownership prematurely cleared. | Bounded terminate/kill/reap attempts, independently attempted terminal cleanup, no echo restoration while a reader may survive, and scope idle/populated verification before releasing ownership. Permanent regression cases cover these defects. |
| ST-04: a stale RAM observation did not protect current unrelated workloads. | At least 4 GiB MemAvailable is checked before allocation and each protected cryptsetup invocation; the 2 GiB cgroup ceiling remains. No swap or other workload settings change. |
| ST-05: installer signal between policy rename and rollback-ownership assignment. | Final checkpoint marks rollback ownership before rename and checks the known target before moving it. Permanent regression ST-05 checks that ordering. Installation remains non-atomic against power loss/SIGKILL. |

The fixed image is exclusive-created and fully allocated; owner/mode/link/size/block/inode checks and capacity/local ancestry checks precede destruction. The mapper is bound through device-mapper name/type and its sole loop backing to the held image identity before ext4 formatting or host mounting. Installed-code validation remains strict; the expected udev mapper symlink is a separate device-resolution case. Root-controlled ancestry and a trusted root/kernel/device stack are assumptions, not protection against a malicious administrator.

The new sudo policy grants only the digest-pinned installed command with exact `--initialize`, PASSWD and NOSETENV. It neither grants the internal worker nor arbitrary commands/arguments. Existing operator policy is unchanged. No shell executes in the runtime initializer, all subprocess paths are absolute, and cryptsetup receives the fixed clean environment with no extra inherited descriptors. The host supervisor mounts only after the protected worker has ended. Failed or partial images/mappings are preserved, never automatically deleted or reformatted.

## Independent validation actually executed

- **78 V0 tests and 282 preserved qualification tests: PASS (360 total).** Nineteen storage preparation cases use source checks and isolated mocked metadata/process/terminal fixtures. They do not exercise cryptsetup or an actual mounted volume.
- Candidate sudoers strict parsing with installed visudo: PASS. This is not an installed aggregate-policy or authentication test.
- New checkpoint Bash-fence syntax: PASS. No installation, rollback or console block was executed.
- Read-only lookup of the exact unused project scope returned inactive; no unit was created or changed.

Reviewed source SHA-256: `12e0b405ce7c9b1d935e5ba247c96ec71e25fe7ef8e6ed23a782f7589790d0ff`.
Reviewed policy SHA-256: `a6e629f355a0cb8a49c414fb2740df2eb7af57b822ce89fbc326cdfbc3e33dd8`.

## Residual limits

This is preparation for the newly authorized human operation, not evidence that storage has been created or that real-tool secret handling was crash-tested. The prior finite synthetic observer milestone retains its original scope. The direct console/login session, root, kernel, installed libraries and pinned collector behavior must be trusted. No claim covers another reader with console access, compromised root, kernel buffers, universal memory erasure, global mlockall, or cleanup after uncatchable termination. Cryptsetup and its in-process dependencies receive plaintext; Python, sudo and systemd do not receive passphrase input.

The human block must validate candidate and aggregate sudo configuration, exact installed hashes, and ordinary sudo behavior. It must preserve existing result/recovery artifacts. Only the sanitized fixed storage result should return to the agent. Future unlock/recovery requires an unlock-only guarded path, never rerunning initialization. Header export, OpenBao initialization and Alpaca credentials are outside this authorization.

The final checkpoint was reviewed in full. It installs only the new fixed command and separate command-specific policy, preserves the old wrapper/policy and result files, checks candidate and aggregate policy before activation, and validates the installed aggregate afterward. Caught-failure rollback removes only the newly activated grant into a retained root-only recovery copy. Terminal recovery now requires both inactive/failed scope state and no populated project cgroup before stty; state alone is not presented as proof that no reader survives.

Gate 2 remains NOT PASSED; existing qualification authorization flags are not changed. The separate storage-ready report means only the listed initialization/mount checks completed. PostgreSQL/TDE, backup recovery and the PAPER-connected application still require implementation and runtime evidence.
