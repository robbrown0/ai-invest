# Host Inventory — Sanitized Qualification Evidence

**Status:** Inventory collected; runtime/security qualification blocked.
**Purpose:** Record observed host capability and limitations without publishing identifying home-lab details.
**Observed:** 2026-09-09 around 01:01 UTC; transient measurements are snapshots.
**Configuration:** Existing shared local Ubuntu host; no ai-invest runtime provisioned.

## Disclosure and procedure limits

Only system capability/metadata and selected read-only Docker fields were queried. No environment dump, container environment/command inspection, credential files, private keys, workload logs or secret-store contents were read. Public evidence omits hostnames, IP/MAC addresses, serial numbers, unrelated workload names/mount paths, listening port numbers and process identities. Observations below are selected/redacted output, not a raw forensic capture.

No network attack, remote port scan, disk write benchmark, reboot, workload restart, swap change, firewall change or installation occurred. Docker connects through an existing local Unix endpoint, with no DOCKER_HOST/DOCKER_CONTEXT override. Access to that daemon is powerful; it was not used to bypass missing host-administration authorization.

## Exact observed versions

| Component | Version / observation |
| --- | --- |
| Operating system | Ubuntu 24.04.3 LTS, x86_64 |
| Kernel | Linux 6.11.0-26-generic |
| Docker client / server | 28.3.3; client build 980b856 |
| Docker Compose | v2.39.1 |
| Docker storage / cgroups | overlay2 / cgroup v2 |
| GPU driver | 580.173.02 |
| cryptsetup | 2.7.0 |
| OpenSSL | 3.0.13, 30 Jan 2024 |
| Python | 3.12.3 |
| findmnt / lsblk | util-linux 2.39.3 |
| free | procps-ng 4.0.4 |
| ss | iproute2-6.1.0 |
| git | 2.43.0 |
| gh | 2.45.0; Ubuntu package 2.45.0-1ubuntu0.3+esm3 |
| Percona PostgreSQL / pg_tde / OpenBao / backup tooling | NOT SELECTED OR RUN for qualification; no installed-version or compatibility claim |

Version strings are not security-patch attestations. No package/advisory audit was completed.

## Capacity observations

| Surface | Selected actual output | Interpretation |
| --- | --- | --- |
| CPU | Intel Core i7-10700F; 16 logical CPUs; x86_64; VT-x | CPU capability observed; no stress benchmark |
| RAM | 15913 MiB total; 11150 MiB available in initial snapshot | No qualified reservation or sustained headroom guarantee |
| GPU | NVIDIA GPU, 8192 MiB VRAM; 310 MiB used; 36% instantaneous utilization | Shared GPU is not assumed idle; no model or GPU test job started |
| Project filesystem | ext4; 1005867986944 bytes usable filesystem size; 489893855232 used; 464803360768 available; 52% used | Local storage capacity observed, not encryption/durability proof |
| Physical storage | Approximately 1 TB, nonrotational reported; ordinary partition backs project root | No crypt ancestor observed for this filesystem |
| Swap | File-backed; 4294963200 bytes total; 2171338752 bytes used | Backing filesystem is the same root ext4 partition; future secret-process exclusion unproved |
| Other encrypted storage | A LUKS/ext4 mount exists for an unrelated workload | Not approved for ai-invest; not inspected internally or reused |
| Existing Docker workloads | Six running containers | No restart, stop, inspect-config or modification |
| Docker memory snapshot | One existing workload about 3.225 GiB; five others about 621 MiB combined | Illustrative snapshot only; several reported host-scale memory limits; no changes made |

Hardware names unrelated to compatibility are generalized in public evidence. The architecture retains bare-metal Ubuntu, local nonrotational storage and NVIDIA 8 GB VRAM constraints.

## Reproducible read-only checks and outcomes

Run only on an owner-authorized host; review output before public sharing. Replace WORKTREE and DEVICE below with locally resolved paths; do not publish unrelated mount identities. None of these commands reads secret values.

| Check / procedure | Expected qualification result | Actual selected output | Result |
| --- | --- | --- | --- |
| uname -srm; lsb_release -ds; selected lscpu fields; free -m | Supported host/capacity facts available | Versions and capacity above | PASS: inventory only |
| nvidia-smi with name,memory.total,memory.used,driver_version,utilization.gpu | Driver/GPU facts available without process details | 8192 MiB / 310 MiB / 580.173.02 / 36% | PASS: inventory only |
| findmnt -n -o SOURCE,FSTYPE --target WORKTREE; lsblk -s -o TYPE,FSTYPE DEVICE | Approved encrypted local backing for future runtime/spill | Project filesystem resolves directly to disk/ordinary ext4 partition; no crypt ancestor | NOT QUALIFIED |
| df -B1 --output=fstype,size,used,avail,pcent WORKTREE | Sufficient space and measured future budget | 464803360768 bytes available in initial snapshot | Inventory only; budget not accepted |
| swapon selected TYPE,SIZE,USED; findmnt on swap backing path | Secret-bearing processes protected from disk swap | Active file swap on ordinary root ext4; no project cgroup/helper controls exist | NOT QUALIFIED |
| ulimit -c | Core dumps prohibited for secret-bearing services/helpers | 0 for this shell | Narrow observation only; NOT QUALIFIED for future processes |
| docker --version; docker compose version; selected docker info | Local daemon supports baseline qualification | 28.3.3 / v2.39.1 / cgroup v2; daemon read succeeds | PASS: availability only |
| docker info selected SecurityOptions; AppArmor enabled flag | Relevant isolation mechanisms available | AppArmor, builtin seccomp, cgroup namespaces; AppArmor Y | Availability only; negative runtime tests NOT RUN |
| sudo -n true | Noninteractive host administration available if approved changes require it | Exit 1: password required | Prerequisite unavailable; no password requested or workaround attempted |
| ss -H -lntu aggregated by protocol/address category | Identify potential exposure without publishing endpoint inventory | Counts below | NOT QUALIFIED for network isolation |

### Listener category snapshot

| Protocol | Loopback | Explicit non-loopback | Wildcard |
| --- | --- | --- | --- |
| TCP | 13 | 2 | 21 |
| UDP | 4 | 21 | 14 |

A wildcard listener is not proof of Internet reachability; firewalls, NAT and address scope were not assessed. Existing listeners are not an ai-invest deployment. No project endpoint was created. Firewall effectiveness and ingress/egress denial need explicit scoped tests after an approved environment exists.

## Findings and residual limits

### Existing GitHub controls (read-only verification)

Repository robbrown0/ai-invest remains public. Dependency vulnerability alerts respond successfully (204); Dependabot security updates are enabled/not paused; secret scanning, secret push protection and private vulnerability reporting are enabled. Main retains administrator-enforced linear-history protection. Required status checks are null. Generic/non-provider scanning and optional validity checks remain disabled as documented in the prior Phase 2 amendment.

No Phase 3 GitHub Actions workflow, SAST job, dependency scan run or container scan run was added or executed. Existing repository feature enablement does not satisfy QS-01's functioning CI/security-pipeline requirement. No repository setting was changed during this qualification attempt.

QH-02: encrypted project runtime/storage is not demonstrated. Existing ciphertext for a different workload is neither permission nor proof for this project. Filesystem ancestry does not exclude every possible hardware/external encryption layer; no such layer was attested. Supplemental encrypted storage is required because pg_tde does not cover internal metadata and query spill files. [Percona limitations](https://docs.percona.com/pg-tde/index/tde-limitations.html)

QH-03: active host swap is not proof that every future container will swap. Qualify project-only prevention rather than disabling shared-host swap implicitly. Docker documents that equal positive memory and memory-swap limits prevent container swap; verify actual cgroup settings, helper/bootstrap memory and core-dump behavior. [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)

No claim is made about disk hardware health, encrypted backups, cold recovery, firewall rules, patch completeness, acceptable sustained load or existing workload security. Those require additional authorized evidence. There is no failed TDE test: no test stack was started.
