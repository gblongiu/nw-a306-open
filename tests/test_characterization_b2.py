# SPDX-License-Identifier: GPL-2.0-or-later
"""B2 registry/approval integration using the existing fake smart-socket server."""

import copy
import io
import threading
import unittest
from unittest import mock

import test_adb_readonly as af

ar, cp, ct = af.ar, af.cp, af.ct
b2 = ar.b2


class B2Tests(unittest.TestCase):
    setUp = af.AdapterTests.setUp
    check_hashes = af.AdapterTests.check_hashes

    def approval(self, out):
        return {"approved": True, "stage": "B2",
                "plan_sha256": cp.sha(cp.canonical(ar.plan("B2"))),
                "profile_sha256": cp.sha(cp.canonical(self.profile)),
                "output": str(out.absolute())}

    def run_b2(self):
        self.counter += 1
        out = self.root / f"b2-{self.counter}"
        result = ar.run("B2", self.approval(out), out, self.profile, connector=self.server)
        return result, out

    def test_exact_scope_order_limits_and_identity_bookends(self):
        expected = (
            ("bootloader-report", "/system/bin/getprop ro.bootloader", 4096),
            ("unlock-report", "/system/bin/getprop ro.oem_unlock_supported", 4096),
            ("android-release", "/system/bin/getprop ro.build.version.release", 4096),
            ("updater-candidates", "/system/bin/pm list packages --user 0 -s systemupdat", 16384),
            ("partitions", "/system/bin/toybox head -c 65537 /proc/partitions", 65536),
            ("sound-cards", "/system/bin/toybox head -c 65537 /proc/asound/cards", 65536),
            ("sound-pcm", "/system/bin/toybox head -c 65537 /proc/asound/pcm", 65536),
            ("input-devices", "/system/bin/toybox head -c 65537 /proc/bus/input/devices", 65536),
            ("graphics-names", "/system/bin/toybox ls -l /sys/class/graphics", 16384),
            ("power-names", "/system/bin/toybox ls -l /sys/class/power_supply", 16384),
            ("block-names", "/system/bin/toybox ls -l /dev/block/by-name", 65536),
        )
        self.assertEqual(tuple((o.id, o.remote, o.cap) for o in b2.EVIDENCE), expected)
        self.assertEqual(tuple(o.id for o in b2.EVIDENCE), b2.EVIDENCE_IDS)
        self.assertEqual(len(ar.operations("B2")), 33)
        self.assertEqual(b2.OPERATIONS[:11], cp.IDENTITY)
        self.assertEqual(b2.OPERATIONS[-11:], cp.OPERATIONS[-11:])
        self.assertTrue(all(o.timeout_ms == 5000 for o in b2.OPERATIONS))

    def test_complete_fragmented_fake_session_guard_counts_and_integrity(self):
        result, out = self.run_b2()
        self.assertTrue(result["complete"], result["stop"])
        self.assertEqual(result["mode"], "injected")
        self.assertFalse(result["live_server_acquisition"])
        self.assertFalse(result["physical_evidence"])
        self.assertEqual([o["id"] for o in result["observations"]], [o.id for o in b2.OPERATIONS])
        self.assertEqual(self.server.commands, ["shell,v2,raw:" + o.remote for o in b2.OPERATIONS])
        self.assertEqual(len(result["connections"]), 168)
        self.assertEqual(self.server.requests.count("host:devices-l"), 66)
        self.assertEqual(self.server.stdin_closes, 33)
        self.assertTrue(all(o["complete"] for o in result["observations"]))
        self.assertTrue(all(s.closed for s in self.server.sockets))
        self.check_hashes(result, out)

    def test_excluded_services_and_registry_objects_never_dispatch(self):
        session = ar.Session("B2", self.root, self.server, threading.Event())
        session.profile = self.profile
        for key in ("compatible", "model", "tree-link", "raw-fdt-mode", "regulator-names", "kernel"):
            operation = ct.REGISTRY[key]
            with self.subTest(key=key), self.assertRaises(cp.Refusal):
                session.allow("shell,v2,raw:" + operation.remote)
            with self.subTest(key=key), self.assertRaises(cp.Refusal):
                session.shell(operation, self.profile, 0)
        with self.assertRaises(cp.Refusal):
            session.shell(cp.Operation("bootloader-report", "/system/bin/reboot"), self.profile, 0)
        self.assertFalse(self.server.requests)
        self.assertFalse(session.manifest["observations"])

    def test_unapproved_stale_cross_stage_and_profile_authorizations_fail_before_connect(self):
        variants = [("approved", False), ("stage", "B"), ("output", "elsewhere"),
                    ("profile_sha256", "0" * 64),
                    ("plan_sha256", cp.sha(cp.canonical(ar.plan("B")))),
                    ("plan_sha256", "9a2a9b54b78a681021ab516ac340466b941c0f472240010353063f8bcae6418e")]
        for i, (key, value) in enumerate(variants):
            out = self.root / f"rejected-{i}"
            approval = self.approval(out); approval[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(cp.Refusal):
                ar.run("B2", approval, out, self.profile, connector=self.server)
            self.assertFalse(out.exists())
        self.assertFalse(self.server.requests)

    def test_plan_pins_registry_sources_and_schedule_mutation_invalidates_approval(self):
        policy = ar.plan("B2")
        self.assertEqual(set(policy["code_sha256"]),
                         {"adb_readonly.py", "characterization_plan.py", "characterization_transport.py",
                          "characterization_b2.py"})
        self.assertEqual(policy["wire_cap"], 2 * 1024 * 1024)
        self.assertEqual(policy["session_ms"], 300000)
        out = self.root / "changed"
        approval = self.approval(out)
        with mock.patch.object(b2, "OPERATIONS", b2.OPERATIONS[:-1]), self.assertRaises(cp.Refusal):
            ar.run("B2", approval, out, self.profile, connector=self.server)
        self.assertFalse(self.server.requests)

    def test_default_b2_cli_is_inert_and_has_no_operation_selector(self):
        with mock.patch.object(ar, "connect_existing", side_effect=AssertionError("must stay offline")):
            with mock.patch("sys.stdout", io.StringIO()) as stream:
                self.assertEqual(ar.main(["--stage", "B2"]), 0)
            policy = cp.json.loads(stream.getvalue())
            digest = policy.pop("plan_sha256")
            self.assertEqual(digest, cp.sha(cp.canonical(policy)))
            self.assertEqual(policy, ar.plan("B2"))
            with mock.patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit):
                ar.main(["--stage", "B2", "--select", "compatible"])
        self.assertFalse(self.server.requests)

    def test_each_evidence_denial_stops_without_skip_retry_or_end_checks(self):
        for index, operation in enumerate(b2.EVIDENCE, 11):
            self.server = af.FakeServer(self.profile)
            self.server.fragment = 65536
            def denied(service, sock, remote=operation.remote):
                if service == "shell,v2,raw:" + remote:
                    sock.shell = True
                    self.server.commands.append(service)
                    return b"OKAY" + af.frame(2, b"Permission denied\n") + af.frame(3, b"\1")
                return None
            self.server.override = denied
            result, out = self.run_b2()
            with self.subTest(operation=operation.id):
                self.assertEqual(result["stop"], "inaccessible")
                self.assertFalse(result["complete"])
                self.assertEqual(len(result["observations"]), index + 1)
                self.assertEqual(len(self.server.commands), index + 1)
                self.assertEqual(result["observations"][-1]["id"], operation.id)
                self.assertFalse(result["observations"][-1]["complete"])
                self.check_hashes(result, out)

    def test_initial_and_ending_identity_mismatch_stops(self):
        self.server.values[cp.IDENTITY[0].remote] = b"0\n"
        result, _ = self.run_b2()
        self.assertEqual(result["stop"], "identity mismatch: uid")
        self.assertEqual(len(self.server.commands), 1)
        self.server = af.FakeServer(self.profile)
        seen = 0
        def change(service, sock):
            nonlocal seen
            if service == "shell,v2,raw:" + cp.IDENTITY[0].remote:
                seen += 1
                if seen == 2:
                    sock.shell = True
                    self.server.commands.append(service)
                    return b"OKAY" + af.frame(1, b"0\n") + af.frame(3, b"\0")
            return None
        self.server.override = change
        result, _ = self.run_b2()
        self.assertEqual(result["stop"], "identity mismatch: uid")
        self.assertEqual(result["observations"][-1]["id"], "end:uid")
        self.assertEqual(len(result["observations"]), 23)

    def test_b2_binding_and_atomic_selection_mismatch_prevent_commands(self):
        self.server.listing = self.server.listing.replace(b"PRIVATE-SYNTHETIC-OWNER", b"different")
        result, _ = self.run_b2()
        self.assertEqual(result["stop"], "binding_mismatch")
        self.assertFalse(self.server.commands)
        self.server = af.FakeServer(self.profile)
        self.server.override = lambda s, sock: b"OKAY" + af.struct.pack("<Q", 8) if s.startswith("host:tport:serial:") else None
        result, _ = self.run_b2()
        self.assertEqual(result["stop"], "selected_transport_mismatch")
        self.assertFalse(self.server.commands)


if __name__ == "__main__": unittest.main()
