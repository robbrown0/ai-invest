# PostgreSQL V0 — Directory Handoff

The owner reports successful dedicated storage initialization and explicitly approves the local pg_tde file provider for private single-host V0 PAPER development. The keyring stays at `/srv/ai-invest-secure/runtime/tde-keys`, outside PGDATA. No OpenBao, LIVE, commercial or Gate 2 approval follows. This development exception must be replaced/reviewed before production; provider APIs preserve a later supported KMS migration path.

## One human step now — ordinary SSH terminal is sufficient

Review the committed [fixed helper](../scripts/setup_postgres_dirs.py) and [independent review](reviews/POSTGRES_SETUP_REVIEW.md). Do not run concurrent storage/repository changes. No project secret is requested; only ordinary sudo authentication happens locally. Run:

```bash
cd /home/rob/ai-invest
printf '%s\n' 'e9a0bd4e7d6405f4df79ca45f1982d01b8c500a21808195d7632729f02009706  scripts/setup_postgres_dirs.py' | sha256sum --check - && \
  sudo /usr/bin/python3 -I -B /home/rob/ai-invest/scripts/setup_postgres_dirs.py
```

Expected: `{"database_started": false, "directories_ready": true, "gate2_passed": false, "keys_created": false, "mode": "postgres-directory-setup"}`. Share only this result. No new sudoers grant/installed wrapper is needed. The old physical-console/--io-test paths are not involved.

The helper verifies the exact mounted LUKS2 mapper/single-loop/backing file, mount options, root-only parents and empty leaves using fd-relative no-follow operations. It creates only seven named leaves for data, keyring, socket, temporary files, logs and two recovery-copy staging locations. Leaves use the pinned image's postgres UID/GID 26, mode0700 except socket0770. Parents remain root0700. Existing content/unsafe metadata is refused; no recursion, deletion, file-content read or credential/key creation. Partial failure preserves created directories. Do not delete content or rerun after PostgreSQL/key initialization to force a PASS. No rollback is necessary for these empty directories; preserve them if setup fails for targeted inspection.

## Ready for the next engineering action

Downloaded official image: `percona/percona-distribution-postgresql@sha256:d37e949abdbb4f8b1e0ea2cb6961dd70dcba13738c05142978f616da835a79a8`. Isolated no-network metadata execution confirmed PostgreSQL17.11 / Percona Server17.11.1, pg_tde2.2.2 and UID/GID26. That metadata process observed swap.max=0/current=0 and core soft/hard=0; this is NOT future PostgreSQL crash/retention proof.

[Compose candidate](../infrastructure/postgres/compose.yaml) pins that image, no network/ports, non-root user, dropped capabilities, read-only root, 2GiB/no-swap limit, one CPU, 64PIDs and zero core limits. Image-declared extra volumes are overridden by read-only tmpfs; all writable persistent mounts are explicit encrypted leaves with automatic host-path creation disabled. Key recovery leaves are NOT mounted into PostgreSQL. The candidate is manual-profile-only, unstarted and not a self-initializing deployment command. Root/kernel/host administrator and reviewed source files remain trusted.

After directory setup, continue directly with isolated cluster initialization, effective process-protection validation before key generation, pg_tde internal principal/WAL-key creation without returning bytes, WAL-encrypted restart, both migrations, tenant-role application wiring and durable restart tests. No application data may precede TDE/WAL readiness. `wal_encrypt=on` is the final required setting; the candidate cannot safely bootstrap itself before its key exists. Runtime no-swap/crash checks remain necessary and are not replaced by Compose syntax or RLIMIT_CORE alone.

Create two separately mounted protected key-recovery copies and byte-compare internally without displaying contents/digests. These on-volume staging copies are not independent disaster recovery: the owner must retain protected offline copies separately from database backups before relying on recovery. Neither keys nor copies have been created in this handoff. The owner must never supply recovery material to this assistant.

The host mount was independently observed as ext4 on the approved mapper, nosuid/nodev/noexec, about63GiB free. Noninteractive sudo requires a password, so the agent did not change root-only directories via Docker. No database started, migration applied, application connected, real credential entered or key initialized yet. Existing storage-init result/evidence remains unchanged. Gate 2 remains NOT PASSED.
