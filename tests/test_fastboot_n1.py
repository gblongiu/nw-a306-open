# SPDX-License-Identifier: GPL-2.0-or-later
"""N1 injected-socket/process integration; never run Android host tools."""
import copy
from datetime import datetime, timezone, timedelta
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest import mock

import test_adb_readonly as af
from test_characterization_transport import Process
import fastboot_n1 as n1


class N1Tests(unittest.TestCase):
    def setUp(self):
        af.AdapterTests.setUp(self)
        self.server.fragment = 65536
        self.server.override = lambda req, sock: b"OKAY" if req == "reboot:bootloader" else None
        self.exe = self.root / "fixture-fastboot.exe"
        self.exe.write_bytes(b"synthetic not executable")
        for key, val in [("FASTBOOT", str(self.exe)), ("FASTBOOT_SHA256", af.cp.sha(self.exe.read_bytes()))]:
            p = mock.patch.object(n1, key, val); p.start(); self.addCleanup(p.stop)
        self.out = self.root / "n1"
        self.approval = {"approved": True, "stage": "N1", "plan_sha256": af.cp.sha(af.cp.canonical(n1.plan())),
                         "profile_sha256": af.cp.sha(af.cp.canonical(self.profile)), "output": str(self.out)}
        self.ready = {"confirmed": True, "utc": datetime.now(timezone.utc).isoformat(),
                      "profile_sha256": self.approval["profile_sha256"], "normal_idle": True,
                      "power_ready": True, "battery_ready": True, "backups_ready": True}
        self.supervised = {"same_unit_fastboot_screen": True, "same_physical_usb_port": True}
        self.calls = []
        self.values = dict(n1.GUARDS, **{"version-bootloader": "SONY.fixture.1", "is-userspace": "no"})
        self.guard = mock.Mock()

    def start(self):
        return n1.start(self.approval, self.profile, self.out, self.ready, self.guard, connector=self.server)

    def launcher(self, args):
        self.calls.append(args)
        if args == [str(self.exe), "devices", "-l"]:
            return Process((self.profile["binding"]["serial"] + " fastboot\n").encode())
        key = args[-1]
        return Process(stderr=(key + ": " + self.values[key] + "\r\nFinished. Total time: 0.001s\r\n").encode())

    def diagnose(self, launcher=None):
        return n1.diagnose(self.approval, self.profile, self.out, self.supervised, self.guard,
                           launcher=launcher or self.launcher)

    def test_exact_reordered_scope_and_inert_import_plan(self):
        self.assertEqual(n1.VARIABLES, ("product", "unlocked", "secure", "current-slot", "version-bootloader", "is-userspace"))
        self.assertEqual(n1.plan()["entry"], "reboot:bootloader")
        self.assertEqual(len(n1.plan()["pre_identity"]), 11)
        self.assertEqual(n1.plan()["post_identity"], n1.plan()["pre_identity"])
        self.assertEqual(n1.plan()["operation_ms"], 5000)
        self.assertEqual(n1.plan()["per_stream_cap"], 4096)
        self.assertEqual(n1.plan()["session_ms"], 450000)
        self.assertFalse(self.server.requests)
        for key in ["all", "flashing get_unlock_ability", "boot", "reboot"]:
            with self.assertRaises(af.cp.Refusal): n1.argv("fixture", key)

    def test_entry_exact_identities_atomic_transport_and_one_service(self):
        result = self.start()
        self.assertTrue(result["complete"], result["stop"])
        self.assertTrue(result["entry_acknowledged"])
        self.assertEqual(len(result["observations"]), 11)
        self.assertEqual(self.server.commands, ["shell,v2,raw:" + o.remote for o in af.cp.IDENTITY])
        self.assertEqual(self.server.requests.count("reboot:bootloader"), 1)
        af.AdapterTests.check_hashes(self, result, self.out / "pre-entry")
        with self.assertRaises(FileExistsError): self.start()
        self.assertEqual(self.server.requests.count("reboot:bootloader"), 1)

    def test_changed_approval_profile_readiness_refused_before_connection(self):
        for key, val in [("approved", False), ("stage", "C1"), ("plan_sha256", "old"), ("profile_sha256", "changed"), ("output", "elsewhere")]:
            a = self.approval.copy(); a[key] = val
            with self.subTest(key=key), self.assertRaises(af.cp.Refusal):
                n1.start(a, self.profile, self.out, self.ready, self.guard, connector=self.server)
        for key in ["power_ready", "normal_idle", "battery_ready", "backups_ready"]:
            r = self.ready.copy(); r[key] = False
            with self.subTest(key=key), self.assertRaises(af.cp.Refusal):
                n1.start(self.approval, self.profile, self.out, r, self.guard, connector=self.server)
        r = self.ready.copy(); r["utc"] = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()
        with self.assertRaises(af.cp.Refusal): n1.start(self.approval, self.profile, self.out, r, self.guard, connector=self.server)
        self.assertFalse(self.server.requests)

    def test_identity_failure_never_enters_bootloader(self):
        self.server.values[af.cp.IDENTITY[0].remote] = b"0\n"
        result = self.start()
        self.assertFalse(result["complete"])
        self.assertFalse(result["entry_attempted"])
        self.assertNotIn("reboot:bootloader", self.server.requests)

    def test_wrong_atomic_transport_prevents_entry(self):
        original = self.server.override
        def override(req, sock):
            if req.startswith("host:tport:serial:"):
                return b"OKAY" + af.struct.pack("<Q", self.server.tid + 1)
            return original(req, sock)
        self.server.override = override
        result = self.start()
        self.assertFalse(result["complete"])
        self.assertNotIn("reboot:bootloader", self.server.requests)

    def test_entry_failure_preserved_and_not_retried_or_diagnosed(self):
        self.server.override = lambda req, sock: b"FAIL" + af.string(b"fixture denied") if req == "reboot:bootloader" else None
        result = self.start()
        self.assertFalse(result["complete"])
        self.assertTrue(result["entry_attempted"])
        self.assertFalse(result["entry_acknowledged"])
        self.assertEqual(self.server.requests.count("reboot:bootloader"), 1)
        with self.assertRaises(af.cp.Refusal): self.diagnose()
        self.assertFalse(self.calls)

    def test_complete_order_successful_stderr_and_private_hashes(self):
        self.start()
        result = self.diagnose()
        self.assertTrue(result["complete"], result["stop"])
        self.assertEqual([a[-1] for a in self.calls[1:]], list(n1.VARIABLES))
        self.assertTrue(all(a[1:3] == ["-s", self.profile["binding"]["serial"]] for a in self.calls[1:]))
        self.assertEqual(self.guard.call_count, 16)
        for rec in result["records"]:
            for stream in ["stdout", "stderr"]:
                raw = (self.out / "fastboot" / rec[stream]["file"]).read_bytes()
                self.assertEqual(len(raw), rec[stream]["bytes"])
                self.assertEqual(af.cp.sha(raw), rec[stream]["sha256"])
        with self.assertRaises(FileExistsError): self.diagnose()
        self.assertEqual(len(self.calls), 7)

    def test_supervision_and_changed_native_file_block_before_launch(self):
        self.start()
        self.supervised["same_unit_fastboot_screen"] = False
        with self.assertRaises(af.cp.Refusal): self.diagnose()
        self.supervised["same_unit_fastboot_screen"] = True
        self.exe.write_bytes(b"changed")
        result = self.diagnose()
        self.assertFalse(result["complete"])
        self.assertFalse(self.calls)

    def test_unknown_version_stops_before_is_userspace_and_forbids_post_queries(self):
        self.start()
        def bad(args):
            if args[-1] == "version-bootloader":
                self.calls.append(args)
                return Process(stderr=b"FAILED (remote: 'unknown variable')\n", code=1)
            return self.launcher(args)
        result = self.diagnose(bad)
        self.assertFalse(result["complete"])
        self.assertEqual(self.calls[-1][-1], "version-bootloader")
        self.assertEqual(len(self.calls), 6)
        before = len(self.server.requests)
        with self.assertRaises(af.cp.Refusal):
            n1.verify_return(self.approval, self.profile, self.out, True, connector=self.server)
        self.assertEqual(before, len(self.server.requests))

    def test_ambiguous_enumeration_stops_before_getvars(self):
        self.start()
        def ambiguous(args):
            self.calls.append(args)
            return Process(b"fixture fastboot\nother fastboot\n")
        result = self.diagnose(ambiguous)
        self.assertFalse(result["complete"])
        self.assertEqual(len(self.calls), 1)

    def test_output_grammar_refuses_ambiguity_fail_data_unknown_and_mismatch(self):
        good = b"version-bootloader: SONY.fixture\nFinished. Total time: 0.001s\n"
        self.assertEqual(n1.value("version-bootloader", b"", good), "SONY.fixture")
        for raw in [b"", good + good, b"version-bootloader: \n", good + b"INFOextra\n", b"version-bootloader: unknown\n", good + b"\0", b"DATA00000001", b"\xff"]:
            with self.subTest(raw=raw), self.assertRaises(af.cp.Refusal): n1.value("version-bootloader", b"", raw)
        with self.assertRaises(af.cp.Refusal): n1.value("product", b"product: different\n", b"")
        with self.assertRaises(af.cp.Refusal): n1.value("is-userspace", b"is-userspace: \n", b"")

    def test_strict_stream_caps_and_native_failure(self):
        for proc, status in [(Process(stdout=b"x" * 4096), "ok"), (Process(stdout=b"x" * 4097), "data_limit"),
                             (Process(stderr=b"x" * 5000), "data_limit"), (Process(code=1), "command_failed")]:
            raw = n1.capture(proc, time.monotonic() + 1)
            self.assertEqual(raw["status"], status)
            self.assertLessEqual(len(raw["stdout"]), 4096)
            self.assertLessEqual(len(raw["stderr"]), 4096)

    def test_post_return_new_transport_is_session_local_and_original_unchanged(self):
        self.start(); self.diagnose()
        old = copy.deepcopy(self.profile)
        self.server.tid += 1
        self.server.listing = self.server.listing.replace(("transport_id:" + old["binding"]["transport_id"]).encode(), ("transport_id:" + str(self.server.tid)).encode())
        result = n1.verify_return(self.approval, self.profile, self.out, True, connector=self.server)
        self.assertTrue(result["complete"], result["stop"])
        self.assertEqual(len(result["observations"]), 11)
        self.assertEqual(result["session_return_profile"]["binding"]["transport_id"], str(self.server.tid))
        self.assertEqual(self.profile, old)
        af.AdapterTests.check_hashes(self, result, self.out / "post-return")

    def test_host_guard_failure_stops_without_launch(self):
        self.start()
        self.guard.side_effect = af.cp.Refusal("USB changed")
        result = self.diagnose()
        self.assertFalse(result["complete"])
        self.assertFalse(self.calls)

    def test_windows_enumeration_detail_is_one_bounded_token(self):
        self.start()
        def windows(args):
            if args[-1] == "-l":
                self.calls.append(args)
                return Process((self.profile["binding"]["serial"] + "  fastboot \\\\?\\usb#vid_fixture#fixture\r\n").encode())
            return self.launcher(args)
        self.assertTrue(self.diagnose(windows)["complete"])

    def test_host_change_at_last_pre_entry_gate_prevents_dispatch(self):
        self.guard.side_effect = [None, af.cp.Refusal("host changed")]
        result = self.start()
        self.assertFalse(result["entry_attempted"])
        self.assertNotIn("reboot:bootloader", self.server.requests)

    def test_native_launcher_refuses_nonallowlisted_arrays_before_process_start(self):
        for args in [[str(self.exe), "reboot"], [str(self.exe), "-s", "fixture", "boot", "image"],
                     [str(self.exe), "-s", "tcp:host", "getvar", "product"],
                     [str(self.exe), "-s", "fixture", "getvar", "all"]]:
            with self.assertRaises(af.cp.Refusal): n1.launch(args)


class NativePipeTests(unittest.TestCase):
    def test_real_local_child_binary_overflow_preserves_strict_prefix_and_reaps(self):
        p = subprocess.Popen([sys.executable, "-c", "import os; os.write(1,b'x'*65536)"],
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = n1.capture(p, time.monotonic() + 2)
        self.assertEqual(result["status"], "data_limit")
        self.assertEqual(result["stdout"], b"x" * 4096)
        self.assertTrue(result["cleanup_complete"])
        self.assertIsNotNone(p.poll())

    def test_real_local_hung_child_timeout_keeps_partial_stderr_and_reaps(self):
        p = subprocess.Popen([sys.executable, "-c", "import os,time; os.write(2,b'partial'); time.sleep(10)"],
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        started = time.monotonic()
        result = n1.capture(p, started + .5)
        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["stderr"], b"partial")
        self.assertTrue(result["cleanup_complete"])
        self.assertLess(time.monotonic() - started, 2)
        self.assertIsNotNone(p.poll())


if __name__ == "__main__": unittest.main()
