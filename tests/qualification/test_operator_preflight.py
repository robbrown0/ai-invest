"""Synthetic regression cases; no keys, services, crashes or host changes."""
import ast
import hashlib
import importlib.util
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "operator_preflight", ROOT / "scripts/qualification/operator_preflight.py"
)
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


class CapacityTests(unittest.TestCase):
    def test_local_sata_ancestry_reg_storage_01(self):
        self.assertTrue(PREFLIGHT.local_sata_backing(["part 0 ", "disk 0 sata"]))

    def test_remote_unknown_or_rotational_ancestry_rejected_reg_storage_01(self):
        for rows in ([], ["disk 0"], ["part 0", "disk 0 iscsi"],
                     ["disk 0 tcp"], ["disk 0 nvme"], ["disk 1 sata"],
                     ["disk 0 sata", "crypt 0"], ["disk 0 sata", "disk 0 iscsi"]):
            with self.subTest(rows=rows):
                self.assertFalse(PREFLIGHT.local_sata_backing(rows))

    def test_observed_capacity_allows_64_gib(self):
        self.assertTrue(PREFLIGHT.capacity_ok(1005867986944, 464786509824))

    def test_insufficient_200_gib_reserve_rejected(self):
        self.assertFalse(PREFLIGHT.capacity_ok(1000 * PREFLIGHT.GIB, 263 * PREFLIGHT.GIB))

    def test_insufficient_twenty_percent_reserve_rejected(self):
        self.assertFalse(PREFLIGHT.capacity_ok(2000 * PREFLIGHT.GIB, 300 * PREFLIGHT.GIB))

    def test_exact_reserve_boundary(self):
        self.assertTrue(PREFLIGHT.capacity_ok(1000 * PREFLIGHT.GIB, 264 * PREFLIGHT.GIB))

    def test_invalid_inputs_rejected(self):
        for total, available, size in [
            (0, 500, PREFLIGHT.VOLUME_BYTES), (500, 501, PREFLIGHT.VOLUME_BYTES),
            (True, 1, PREFLIGHT.VOLUME_BYTES),
            (1000 * PREFLIGHT.GIB, 500 * PREFLIGHT.GIB, 32 * PREFLIGHT.GIB),
        ]:
            with self.subTest(total=total, available=available, size=size):
                self.assertFalse(PREFLIGHT.capacity_ok(total, available, size))

    def test_every_plan_predicate_is_required(self):
        snapshot = dict.fromkeys((
            "local_nonrotational_block_backing", "capacity_margin_pass",
            "root_owned_nonwritable_ancestors", "targets_absent", "mount_parent_same_filesystem"
        ), True)
        self.assertTrue(PREFLIGHT.plan_ok(snapshot))
        for key in snapshot:
            for invalid in (False, None, 1, "true"):
                with self.subTest(key=key, invalid=invalid):
                    self.assertFalse(PREFLIGHT.plan_ok({**snapshot, key: invalid}))


class OperatorTests(unittest.TestCase):
    def valid(self):
        snapshot = dict.fromkeys((
            "root_operator", "direct_virtual_console", "cpu_limit_bounded",
            "core_soft_zero", "core_hard_zero", "mount_namespace_differs_from_visible_pid1",
            "pid_namespace_matches_visible_pid1", "reviewed_apport_handler", "reviewed_core_pattern",
        ), True)
        return dict(snapshot, memory_max=str(PREFLIGHT.MAX_MEMORY), pids_max="32",
                    memory_swap_max="0", memory_swap_current="0")

    def test_valid_metadata_passes_only_predicates(self):
        self.assertTrue(PREFLIGHT.operator_ok(self.valid()))

    def test_each_missing_protection_denies(self):
        for key in self.valid():
            with self.subTest(key=key):
                snapshot = self.valid()
                del snapshot[key]
                self.assertFalse(PREFLIGHT.operator_ok(snapshot))

    def test_unbounded_or_invalid_limits_deny(self):
        for key, values in {
            "memory_max": ("max", "0", "-1", str(PREFLIGHT.MAX_MEMORY + 1)),
            "pids_max": ("max", "0", "65"),
            "memory_swap_max": ("max", "1", None),
            "memory_swap_current": ("1", None),
        }.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    self.assertFalse(PREFLIGHT.operator_ok({**self.valid(), key: value}))

    def test_zero_core_limit_alone_is_insufficient_reg_core_01(self):
        snapshot = self.valid()
        snapshot["mount_namespace_differs_from_visible_pid1"] = False
        self.assertFalse(PREFLIGHT.operator_ok(snapshot))

    def test_pty_relay_denied_reg_tty_01(self):
        self.assertFalse(PREFLIGHT.operator_ok({**self.valid(), "direct_virtual_console": False}))

    def test_unreviewed_handler_denied(self):
        self.assertFalse(PREFLIGHT.operator_ok({**self.valid(), "reviewed_apport_handler": False}))


class OutputTests(unittest.TestCase):
    def test_success_never_authorizes_secret_entry_reg_output_01(self):
        output = io.StringIO()
        with patch("sys.argv", ["preflight", "operator"]), \
             patch.object(PREFLIGHT, "operator_snapshot", return_value=OperatorTests().valid()), \
             patch("sys.stdout", output):
            self.assertEqual(PREFLIGHT.main(), 0)
        report = json.loads(output.getvalue())
        self.assertTrue(report["checks_passed"])
        self.assertIs(report["secret_entry_authorized"], False)
        self.assertIs(report["runtime_crash_suppression_qualified"], False)

    def test_error_diagnostics_not_disclosed_reg_output_01(self):
        diagnostic = "SYNTHETIC_DIAGNOSTIC_MUST_NOT_APPEAR"
        failures = [OSError(diagnostic), ValueError(diagnostic),
                    PREFLIGHT.subprocess.CalledProcessError(1, "probe", stderr=diagnostic)]
        for failure in failures:
            with self.subTest(kind=type(failure).__name__):
                output = io.StringIO()
                with patch("sys.argv", ["preflight", "operator"]), \
                     patch.object(PREFLIGHT, "operator_snapshot", side_effect=failure), \
                     patch("sys.stdout", output):
                    self.assertEqual(PREFLIGHT.main(), 1)
                self.assertNotIn(diagnostic, output.getvalue())
                report = json.loads(output.getvalue())
                self.assertFalse(report["checks_passed"])
                self.assertIs(report["secret_entry_authorized"], False)
                self.assertIs(report["runtime_crash_suppression_qualified"], False)


class InstalledApportSourceTests(unittest.TestCase):
    """Source-level regression only: not a kernel crash/collector runtime test."""
    def test_mount_namespace_skip_branch_reg_core_02(self):
        path = Path("/usr/share/apport/apport")
        if not path.exists():
            self.skipTest("installed Apport unavailable; no runtime qualification inferred")
        source = path.read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), PREFLIGHT.APPORT_SHA256,
                         "handler changed; independent re-review required")
        tree = ast.parse(source)
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "_check_global_pid_and_forward")
        function.returns = None
        for argument in function.args.args:
            argument.annotation = None
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        for same_mount, expected in ((False, True), (True, False)):
            forwarded = []
            namespace = {
                "is_same_ns": lambda proc, kind: same_mount if kind == "mnt" else True,
                "forward_crash_to_container": lambda *args: forwarded.append(True),
                "logging": logging,
            }
            exec(compile(module, "<pinned-apport-source-test>", "exec"), namespace)
            options = SimpleNamespace(global_pid=123456, pid=123456)
            with self.assertLogs(level="ERROR") if not same_mount else self.assertNoLogs(level="ERROR"):
                result = namespace["_check_global_pid_and_forward"](options, object())
            self.assertEqual(result, expected)
            self.assertEqual(forwarded, [])


if __name__ == "__main__":
    unittest.main()
