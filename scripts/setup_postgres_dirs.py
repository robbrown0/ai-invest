#!/usr/bin/python3 -I
"""Fixed NON-SECRET host directory setup. No database, keys, sudo or Docker calls."""
import json
import os
from pathlib import Path
import re
import stat
import sys

BASE = Path('/srv/ai-invest-secure')
# UID/GID 26 is postgres in the inspected, digest-pinned Percona image.
# Root-only ancestors remain unchanged. Only these initially empty leaves change.
TARGETS = (
    ('postgresql', 'data', 0o700),
    ('runtime', 'tde-keys', 0o700),
    ('runtime', 'postgres-socket', 0o770),
    ('runtime', 'postgres-tmp', 0o700),
    ('runtime', 'postgres-logs', 0o700),
    ('qualification-backups', 'tde-recovery-a', 0o700),
    ('qualification-backups', 'tde-recovery-b', 0o700),
)
FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def require(condition):
    if not condition:
        raise RuntimeError('setup_refused')


def directory(fd, owner, mode, device=None):
    info = os.fstat(fd)
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == owner and info.st_gid == owner
            and stat.S_IMODE(info.st_mode) == mode)
    if device is not None:
        require(info.st_dev == device)
    return info


def mounted_device():
    rows = [line.split() for line in Path('/proc/self/mountinfo').read_text().splitlines()
            if line.split()[4] == str(BASE)]
    require(len(rows) == 1)
    row = rows[0]
    separator = row.index('-')
    require(row[separator+1] == 'ext4' and row[separator+2] == '/dev/mapper/ai-invest-qualification')
    require({'rw', 'nosuid', 'nodev', 'noexec'} <= set(row[5].split(',')))
    major, minor = (int(value) for value in row[2].split(':'))
    device = os.makedev(major, minor)
    mapper = Path('/sys/dev/block') / row[2] / 'dm'
    require((mapper/'name').read_text().strip() == 'ai-invest-qualification')
    require(re.fullmatch(r'CRYPT-LUKS2-[0-9a-f]{32}-ai-invest-qualification',
                        (mapper/'uuid').read_text().strip()))
    slaves = list((mapper.parent/'slaves').iterdir())
    require(len(slaves) == 1 and re.fullmatch(r'loop[0-9]+', slaves[0].name))
    require((slaves[0]/'loop/backing_file').read_text().strip() == '/var/lib/ai-invest/qualification.luks')
    for parent in ('/var', '/var/lib', '/var/lib/ai-invest'):
        info = Path(parent).lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022)
    image = Path('/var/lib/ai-invest/qualification.luks').lstat()
    require(stat.S_ISREG(image.st_mode) and image.st_uid == 0 and image.st_nlink == 1
            and stat.S_IMODE(image.st_mode) == 0o600 and image.st_size == 68719476736)
    return device


def empty(fd):
    with os.scandir(fd) as entries:
        require(next(entries, None) is None)


def setup():
    require(os.geteuid() == 0 and len(sys.argv) == 1)
    device = mounted_device()
    descriptors = []
    try:
        root = os.open('/', FLAGS)
        descriptors.append(root)
        srv = os.open('srv', FLAGS, dir_fd=root)
        descriptors.append(srv)
        directory(srv, 0, 0o755)
        base = os.open('ai-invest-secure', FLAGS, dir_fd=srv)
        descriptors.append(base)
        directory(base, 0, 0o700, device)
        parents = {}
        for name in sorted({parent for parent, _, _ in TARGETS}):
            fd = os.open(name, FLAGS, dir_fd=base)
            descriptors.append(fd)
            directory(fd, 0, 0o700, device)
            parents[name] = fd
        # Validate every existing leaf before changing anything; never read files.
        for parent, name, mode in TARGETS:
            try:
                fd = os.open(name, FLAGS, dir_fd=parents[parent])
            except FileNotFoundError:
                continue
            try:
                directory(fd, 26, mode, device)
                empty(fd)
            finally:
                os.close(fd)
        for parent, name, mode in TARGETS:
            created = False
            try:
                os.mkdir(name, 0o700, dir_fd=parents[parent])
                created = True
            except FileExistsError:
                pass
            fd = os.open(name, FLAGS, dir_fd=parents[parent])
            try:
                if created:
                    directory(fd, 0, 0o700, device)
                    empty(fd)
                    os.fchmod(fd, mode)
                    os.fchown(fd, 26, 26)
                directory(fd, 26, mode, device)
                empty(fd)
            finally:
                os.close(fd)
        require(mounted_device() == device)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def main():
    ready = False
    try:
        setup()
        ready = True
    except Exception:
        pass  # Fixed status only; no paths, exception values or file contents.
    print(json.dumps({'mode': 'postgres-directory-setup', 'directories_ready': ready,
        'keys_created': False, 'database_started': False, 'gate2_passed': False}, sort_keys=True))
    return 0 if ready else 1


if __name__ == '__main__':
    raise SystemExit(main())
