# SPDX-License-Identifier: GPL-2.0-or-later
"""Only local Python pipe fixtures and in-memory fakes; never launch ADB."""

import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import characterization_plan as cp
import characterization_transport as ct
from test_characterization_plan import fixtures


class Process:
    def __init__(self, stdout=b"", stderr=b"", code=0):
        self.stdout, self.stderr = io.BytesIO(stdout), io.BytesIO(stderr)
        self.code, self.kills = code, 0

    def poll(self): return self.code
    def kill(self): self.kills += 1
    def wait(self, timeout): return self.code


class FakeTransport:
    mode = "simulation"

    def __init__(self, fixture, profile):
        self.profile = copy.deepcopy(profile)
        self.outputs = {r["id"]: cp.base64.b64decode(r["events"][0]["base64"])
                        for r in fixture["responses"]}
        self.outputs.update({op.id: b"synthetic metadata\n" for op in ct.EXTRA})
        self.calls = []
        self.state = {"binding": copy.deepcopy(profile["binding"]), "shell_v2": True,
                      "server_epoch": "fixture-server-epoch", "usb": True}
        self.on_start = None

    def snapshot(self): return copy.deepcopy(self.state)

    def start(self, id, argv):
        # This tuple must NEVER be passed to a subprocess API.
        if argv != ct.future_argv(id, self.profile): raise AssertionError("mutated argv")
        self.calls.append(id)
        if self.on_start: return self.on_start(id)
        return Process(self.outputs[id])


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        patch = mock.patch.object(cp, "PRIVATE_ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        self.fixture, self.profile = fixtures()
        self.fake = FakeTransport(self.fixture, self.profile)
        self.output = self.root / "capture"

    def run_simulation(self, selected=None, **kwargs):
        digest = cp.sha(cp.canonical(ct.plan(selected)))
        with mock.patch("subprocess.Popen", side_effect=AssertionError("no live launcher")):
            return ct.simulate(self.fake, self.profile, self.output, digest, selected, **kwargs)

    def capture(self, process, cap=4096, remaining=1000000, timeout=.5, cancel=None):
        return ct.capture(process, cap, remaining, time.monotonic() + timeout,
                          cancel or threading.Event())

    def test_complete_simulation_has_fixed_order_exact_hashes_and_private_provenance(self):
        result = self.run_simulation()
        self.assertTrue(result["complete"])
        self.assertFalse(result["physical_evidence"])
        self.assertEqual(self.fake.calls, [o.id for o in ct.schedule()])
        for record in result["records"]:
            for name in ("stdout", "stderr"):
                item = record[name]
                data = (self.output / item["file"]).read_bytes()
                self.assertEqual(cp.sha(data), item["sha256"])
                self.assertEqual(len(data), item["bytes"])
        self.assertEqual(result["records"][0]["stdout"]["file"], "00-stdout.bin")
        self.assertEqual(json.loads((self.output / "manifest.json").read_text())["mode"], "simulation")

    def test_no_default_or_live_backend_and_changed_digest_refused_before_dispatch(self):
        digest = cp.sha(cp.canonical(ct.plan()))
        for mode, approved in (("live", digest), (None, digest), ("simulation", "wrong")):
            self.fake.mode = mode
            with self.subTest(mode=mode), self.assertRaises(cp.Refusal):
                ct.simulate(self.fake, self.profile, self.output, approved)
        self.assertFalse(self.fake.calls)
        self.assertFalse(self.output.exists())

    def test_strict_binding_protocol_usb_and_server_guards(self):
        variants = []
        for key, value in (("serial", "other"), ("transport_id", "8"), ("device_count", 2),
                           ("device_count", True), ("state", "offline"), ("state", "unauthorized")):
            state = copy.deepcopy(self.fake.state)
            state["binding"][key] = value
            variants.append(state)
        for key, value in (("shell_v2", False), ("shell_v2", 1), ("usb", False), ("server_epoch", "")):
            state = copy.deepcopy(self.fake.state)
            state[key] = value
            variants.append(state)
        variants.extend(({}, {"binding": None}))
        for state in variants:
            self.fake.state = state
            with self.subTest(state=state), self.assertRaises(cp.Refusal): self.run_simulation()
        self.assertFalse(self.fake.calls)

    def test_identity_failure_prevents_any_evidence_capture(self):
        self.fake.outputs["uid"] = b"0\n"
        result = self.run_simulation()
        self.assertFalse(result["complete"])
        self.assertEqual(self.fake.calls, ["uid"])
        self.assertEqual(result["records"][0]["capture_status"], "invalid_output")

    def test_disconnect_or_epoch_replacement_after_capture_stops_with_raw_bytes(self):
        for key, value in (("server_epoch", "different"), ("shell_v2", False)):
            self.fake = FakeTransport(self.fixture, self.profile)
            self.output = self.root / key
            def replace(id):
                self.fake.state[key] = value
                return Process(b"2000\n")
            self.fake.on_start = replace
            result = self.run_simulation()
            self.assertFalse(result["complete"])
            self.assertEqual(self.fake.calls, ["uid"])
            self.assertEqual((self.output / "00-stdout.bin").read_bytes(), b"2000\n")

    def test_allowlist_injection_missing_identity_and_order(self):
        for ids in (("reboot",), ("kernel", "kernel"), ("model",), ("model", "tree-link"), ([],)):
            with self.subTest(ids=ids), self.assertRaises(cp.Refusal): ct.schedule(ids)
        for serial in ("", "owner;reboot", "$(reboot)", "192.0.2.1:5555", "owner\n"):
            p = copy.deepcopy(self.profile)
            p["binding"]["serial"] = serial
            with self.subTest(serial=serial), self.assertRaises(cp.Refusal): ct.future_argv("kernel", p)
        for id in ("kernel;reboot", "../kernel", [], None):
            with self.subTest(id=id), self.assertRaises(cp.Refusal): ct.future_argv(id, self.profile)
        p = copy.deepcopy(self.profile)
        del p["identity"]["ro.soc.model"]
        with self.assertRaises(cp.Refusal): ct.future_argv("kernel", p)
        for transport_id in ("0", "00", "07", "-1", str(2**64)):
            p = copy.deepcopy(self.profile)
            p["binding"]["transport_id"] = transport_id
            with self.subTest(transport_id=transport_id), self.assertRaises(cp.Refusal):
                ct.future_argv("kernel", p)
        argv = ct.future_argv("compatible", self.profile)
        self.assertEqual(argv[1:-1], ("-H", "127.0.0.1", "-P", "5037", "-t", "7", "shell", "-n", "-T"))
        self.assertEqual(argv[-1], "/system/bin/toybox head -c 4097 /proc/device-tree/compatible")

    def test_selected_subset_cannot_expand_itself_from_captured_output(self):
        result = self.run_simulation(("kernel",))
        self.assertTrue(result["complete"])
        self.assertEqual(self.fake.calls, [o.id for o in cp.IDENTITY] + ["kernel"]
                         + [o.id for o in cp.OPERATIONS[-len(cp.IDENTITY):]])

    def test_nonzero_exit_stderr_unsupported_and_permission_categories(self):
        for code, err, category in ((3, b"failed", "command_failed"), (127, b"not found", "unsupported"),
                                    (1, b"Permission denied", "inaccessible"), (0, b"warning", "unexpected_stderr")):
            process = Process(b"partial\0\xff", err, code)
            result = self.capture(process)
            self.assertEqual(result.status, category)
            self.assertEqual(result.stdout, b"partial\0\xff")
            self.assertEqual(result.stderr, err)
            self.assertEqual(result.exit, code)

    def test_malformed_pipe_and_disconnection(self):
        for data in ("text", b"x" * 4097):
            process = Process()
            process.stdout = mock.Mock(read1=mock.Mock(return_value=data))
            result = self.capture(process)
            self.assertEqual(result.status, "invalid_transport")
        process = Process()
        process.stderr = mock.Mock(read1=mock.Mock(side_effect=OSError("disconnected")))
        self.assertEqual(self.capture(process).status, "disconnected")

    def test_overflow_each_channel_and_total_preserves_only_bounded_prefix(self):
        for channel in ("stdout", "stderr"):
            process = Process(**{channel: b"a" * 100000})
            result = self.capture(process, cap=32)
            self.assertEqual(result.status, "data_limit")
            self.assertLessEqual(len(getattr(result, channel)), 33)
            self.assertEqual(process.kills, 1)
        result = self.capture(Process(b"x" * 10, b"y" * 10), cap=32, remaining=12)
        self.assertEqual(result.status, "data_limit")
        self.assertLessEqual(len(result.stdout) + len(result.stderr), 13)

    def test_missing_exit_and_cleanup_failure_never_complete(self):
        result = self.capture(Process(b"partial", code=None), timeout=.05)
        self.assertEqual(result.status, "timeout")
        self.assertEqual(result.stdout, b"partial")
        process = Process(b"ok")
        process.wait = mock.Mock(side_effect=subprocess.TimeoutExpired("fixture", .5))
        result = self.capture(process)
        self.assertFalse(result.cleanup_complete)
        self.assertEqual(result.status, "cleanup_failed")

    def test_cancellation_and_keyboard_interrupt_keep_partial_bytes(self):
        cancel = threading.Event()
        cancel.set()
        process = Process()
        self.assertEqual(self.capture(process, cancel=cancel).status, "cancelled")
        self.assertEqual(process.kills, 1)
        process = Process(b"partial\0")
        process.poll = mock.Mock(side_effect=KeyboardInterrupt)
        result = self.capture(process)
        self.assertEqual(result.status, "interrupted")
        self.assertEqual(result.stdout, b"partial\0")

    def test_timeout_stops_session_without_retries(self):
        self.fake.on_start = lambda id: Process(b"partial", code=None)
        with mock.patch.object(cp, "SESSION_MS", 60):
            result = self.run_simulation()
        self.assertFalse(result["complete"])
        self.assertEqual(self.fake.calls, ["uid"])
        self.assertEqual(result["records"][0]["capture_status"], "timeout")
        self.assertEqual((self.output / "00-stdout.bin").read_bytes(), b"partial")

    def test_exact_total_budget_prevents_next_dispatch(self):
        with mock.patch.object(cp, "TOTAL_CAP", 5):
            result = self.run_simulation()
        self.assertFalse(result["complete"])
        self.assertEqual(self.fake.calls, ["uid"])
        self.assertEqual(result["stop"], "session byte budget exhausted")

    def test_blocked_reader_cleanup_cannot_hang_or_be_accepted(self):
        release = threading.Event()
        self.addCleanup(release.set)
        process = Process()
        process.stdout = mock.Mock(read1=mock.Mock(side_effect=lambda n: release.wait(3) and b""))
        started = time.monotonic()
        result = self.capture(process, timeout=.05)
        self.assertEqual(result.status, "timeout")
        self.assertFalse(result.cleanup_complete)
        process.stdout.close.assert_not_called()
        self.assertLess(time.monotonic() - started, 1)
        release.set()

    def test_private_paths_exclusive_and_host_write_failure_stops(self):
        self.run_simulation(("kernel",))
        original = (self.output / "manifest.json").read_bytes()
        with self.assertRaises(FileExistsError): self.run_simulation(("kernel",))
        self.assertEqual((self.output / "manifest.json").read_bytes(), original)
        self.output = self.root / ".." / "outside"
        with self.assertRaises(cp.Refusal): self.run_simulation()
        self.output = self.root / "failed"
        original_open = Path.open
        def fail(path, *args, **kwargs):
            if path.name == "00-stdout.bin": raise OSError("disk full")
            return original_open(path, *args, **kwargs)
        self.fake.calls = []
        with mock.patch.object(Path, "open", fail), self.assertRaises(OSError): self.run_simulation()
        result = json.loads((self.output / "manifest.json").read_text())
        self.assertFalse(result["complete"])
        self.assertEqual(self.fake.calls, ["uid"])

    def test_local_python_pipes_preserve_binary_and_drain_both_channels(self):
        # Only this fixed local Python command is executed, never future_argv().
        code = ("import sys; d=bytes(range(256))*256; "
                "sys.stdout.buffer.write(d); sys.stdout.buffer.flush(); "
                "sys.stderr.buffer.write(d); sys.stderr.buffer.flush()")
        process = subprocess.Popen([sys.executable, "-I", "-c", code], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        result = self.capture(process, cap=100000, timeout=5)
        self.assertEqual(result.stdout, bytes(range(256)) * 256)
        self.assertEqual(result.stderr, bytes(range(256)) * 256)
        self.assertEqual(result.status, "unexpected_stderr")
        self.assertEqual(result.exit, 0)
        self.assertTrue(result.cleanup_complete)

    def test_local_hung_python_child_is_killed_within_bound(self):
        code = "import time,sys; sys.stdout.buffer.write(b'partial'); sys.stdout.buffer.flush(); time.sleep(60)"
        process = subprocess.Popen([sys.executable, "-I", "-c", code], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        started = time.monotonic()
        result = self.capture(process, timeout=1)
        self.assertEqual(result.status, "timeout")
        self.assertEqual(result.stdout, b"partial")
        self.assertIsNotNone(process.poll())
        self.assertTrue(result.cleanup_complete)
        self.assertLess(time.monotonic() - started, 3)


if __name__ == "__main__":
    unittest.main()
