#!/usr/bin/env python3
"""Read-only, non-secret prerequisite checks. Never authorizes secret entry."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import stat
import subprocess

GIB = 1024 ** 3
VOLUME_BYTES = 64 * GIB
MAX_MEMORY = 2 * GIB
APPORT_SHA256 = "1b8b5e2c53e8970dd2f47c9a0892030d1ebad57cae1f7242c43a6252f1f6dff2"
CORE_PATTERN = "|/usr/share/apport/apport -p%p -s%s -c%c -d%d -P%P -u%u -g%g -F%F -- %E"
TARGETS = (
    "/var/lib/ai-invest",
    "/srv/ai-invest-secure",
    "/dev/mapper/ai-invest-qualification",
)


def command(*args: str) -> str:
    result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=10)
    return result.stdout.strip()


def secure_ancestors(path: Path) -> bool:
    for item in (path, *path.parents):
        info = item.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            return False
    return True


def capacity_ok(total: int, available: int, volume: int = VOLUME_BYTES) -> bool:
    if any(type(value) is not int or value <= 0 for value in (total, available, volume)):
        return False
    if available > total or volume != VOLUME_BYTES:
        return False
    remaining = available - volume
    return remaining >= 200 * GIB and remaining * 5 >= total


def plan_snapshot() -> dict:
    info = os.statvfs("/var/lib")
    total = info.f_blocks * info.f_frsize
    available = info.f_bavail * info.f_frsize
    mount = command("findmnt", "-n", "-o", "SOURCE,FSTYPE", "--target", "/var/lib").split()
    if len(mount) != 2:
        raise ValueError("unexpected mount metadata")
    source, fs_type = mount
    local_block = False
    if source.startswith("/dev/") and fs_type == "ext4":
        rows = command("lsblk", "-s", "-n", "-r", "-o", "TYPE,ROTA,TRAN", source).splitlines()
        local_block = local_sata_backing(rows)
    return {
        "filesystem_type": fs_type,
        "total_bytes": total,
        "available_bytes": available,
        "proposed_volume_bytes": VOLUME_BYTES,
        "remaining_bytes": available - VOLUME_BYTES,
        "local_nonrotational_block_backing": local_block,
        "capacity_margin_pass": capacity_ok(total, available),
        "root_owned_nonwritable_ancestors": all(
            secure_ancestors(Path(path)) for path in ("/var/lib", "/srv")
        ),
        "targets_absent": all(not os.path.lexists(path) for path in TARGETS),
        "mount_parent_same_filesystem": os.stat("/srv").st_dev == os.stat("/var/lib").st_dev,
    }


def local_sata_backing(rows: list[str]) -> bool:
    """Narrow host-specific transport check; reject unknown/remote ancestry."""
    pairs = [row.split() for row in rows]
    return (
        pairs.count(["disk", "0", "sata"]) == 1
        and all(pair in (["disk", "0", "sata"], ["part", "0"]) for pair in pairs)
    )


def plan_ok(snapshot: dict) -> bool:
    checks = (
        "local_nonrotational_block_backing", "capacity_margin_pass",
        "root_owned_nonwritable_ancestors", "targets_absent", "mount_parent_same_filesystem",
    )
    return all(snapshot.get(key) is True for key in checks)


def operator_snapshot() -> dict:
    cgroups = Path("/proc/self/cgroup").read_text().splitlines()
    paths = [line[3:] for line in cgroups if line.startswith("0::")]
    if len(paths) != 1:
        raise ValueError("cgroup v2 membership unavailable")
    root = Path("/sys/fs/cgroup").resolve()
    group = (root / paths[0].lstrip("/")).resolve()
    if not group.is_relative_to(root):
        raise ValueError("cgroup outside expected hierarchy")
    soft, hard = resource.getrlimit(resource.RLIMIT_CORE)
    ttys = [os.ttyname(fd) if os.isatty(fd) else "" for fd in (0, 1, 2)]
    quota = (group / "cpu.max").read_text().split()
    finite_cpu = len(quota) == 2 and quota[0].isdigit() and quota[1].isdigit()
    return {
        "root_operator": os.geteuid() == 0,
        "direct_virtual_console": len(set(ttys)) == 1 and bool(re.fullmatch(r"/dev/tty[1-9][0-9]*", ttys[0])),
        "memory_max": (group / "memory.max").read_text().strip(),
        "memory_swap_max": (group / "memory.swap.max").read_text().strip(),
        "memory_swap_current": (group / "memory.swap.current").read_text().strip(),
        "pids_max": (group / "pids.max").read_text().strip(),
        "cpu_limit_bounded": finite_cpu and 0 < int(quota[0]) <= 2 * int(quota[1]),
        "core_soft_zero": soft == 0,
        "core_hard_zero": hard == 0,
        "mount_namespace_differs_from_visible_pid1": os.stat("/proc/self/ns/mnt").st_ino != os.stat("/proc/1/ns/mnt").st_ino,
        "pid_namespace_matches_visible_pid1": os.stat("/proc/self/ns/pid").st_ino == os.stat("/proc/1/ns/pid").st_ino,
        "reviewed_apport_handler": hashlib.sha256(Path("/usr/share/apport/apport").read_bytes()).hexdigest() == APPORT_SHA256,
        "reviewed_core_pattern": Path("/proc/sys/kernel/core_pattern").read_text().strip() == CORE_PATTERN,
    }


def operator_ok(snapshot: dict) -> bool:
    checks = (
        "root_operator", "direct_virtual_console", "cpu_limit_bounded",
        "core_soft_zero", "core_hard_zero", "mount_namespace_differs_from_visible_pid1",
        "pid_namespace_matches_visible_pid1", "reviewed_apport_handler", "reviewed_core_pattern",
    )
    memory = str(snapshot.get("memory_max", ""))
    pids = str(snapshot.get("pids_max", ""))
    return (
        all(snapshot.get(key) is True for key in checks)
        and memory.isdigit() and 0 < int(memory) <= MAX_MEMORY
        and pids.isdigit() and 0 < int(pids) <= 64
        and snapshot.get("memory_swap_max") == "0"
        and snapshot.get("memory_swap_current") == "0"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "operator"))
    args = parser.parse_args()
    try:
        snapshot = plan_snapshot() if args.mode == "plan" else operator_snapshot()
        passed = plan_ok(snapshot) if args.mode == "plan" else operator_ok(snapshot)
        report = {
            "mode": args.mode, "checks_passed": passed, "observations": snapshot,
            "secret_entry_authorized": False,
            "runtime_crash_suppression_qualified": False,
        }
    except (OSError, ValueError, subprocess.SubprocessError):
        # Never emit raw subprocess output, paths, environment or exception details.
        report = {"mode": args.mode, "checks_passed": False, "error": "metadata_unavailable",
                  "secret_entry_authorized": False, "runtime_crash_suppression_qualified": False}
    print(json.dumps(report, sort_keys=True))
    return 0 if report["checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
