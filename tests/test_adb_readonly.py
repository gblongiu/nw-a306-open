# SPDX-License-Identifier: GPL-2.0-or-later
"""Smart-socket integration fixtures only. All real network/process paths blocked."""

import contextlib
import copy
import io
import importlib
import json
from pathlib import Path
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import adb_readonly as ar
import characterization_plan as cp
import characterization_transport as ct
from test_characterization_plan import fixtures


def frame(channel, data): return struct.pack("<BI", channel, len(data)) + data
def string(data): return f"{len(data):04x}".encode() + data


class FakeSocket:
    def __init__(self, server):
        self.server, self.pending, self.incoming = server, bytearray(), bytearray()
        self.closed, self.watch, self.shell = False, False, False
        self.watch_initial_done = False

    def settimeout(self, timeout): self.timeout = timeout

    def send(self, data):
        if self.server.send_error: raise socket.timeout()
        size = min(len(data), self.server.fragment)
        self.pending.extend(data[:size])
        while self.pending:
            if self.shell:
                if len(self.pending) < 5: break
                if bytes(self.pending[:5]) != b"\4\0\0\0\0": raise AssertionError("only close-stdin allowed")
                del self.pending[:5]
                self.server.stdin_closes += 1
                continue
            if len(self.pending) < 4: break
            length = int(self.pending[:4], 16)
            if len(self.pending) < 4 + length: break
            service = bytes(self.pending[4:4 + length]).decode()
            del self.pending[:4 + length]
            self.server.requests.append(service)
            self.incoming.extend(self.server.respond(service, self))
        return size

    def recv(self, count):
        if self.closed: return b""
        if self.incoming:
            size = min(count, self.server.fragment, len(self.incoming))
            result = bytes(self.incoming[:size]); del self.incoming[:size]
            if self.watch and not self.incoming: self.watch_initial_done = True
            return result
        if self.watch or self.server.hang:
            time.sleep(.002)
            raise socket.timeout()
        return b""

    def close(self): self.closed = True


class FakeServer:
    def __init__(self, profile):
        self.profile = profile
        b = profile["binding"]
        self.listing = (b["serial"] + " device product:fixture model:Fixture device:icx1301 transport_id:"
                        + b["transport_id"] + "\n").encode()
        self.features, self.version = b"shell_v2,cmd", ar.VERSION
        self.tid = int(b["transport_id"])
        self.fragment, self.stdin_closes = 3, 0
        self.requests, self.sockets, self.commands = [], [], []
        self.send_error, self.hang = False, False
        self.override = None
        f, _ = fixtures()
        self.values = {o.remote: cp.base64.b64decode(f["responses"][i]["events"][0]["base64"])
                       for i, o in enumerate(cp.OPERATIONS)}
        self.values.update({o.remote: b"fixture metadata\n" for o in ct.EXTRA})
        self.shell_bytes = None

    def __call__(self, deadline):
        sock = FakeSocket(self)
        self.sockets.append(sock)
        return sock

    def respond(self, service, sock):
        if self.override:
            data = self.override(service, sock)
            if data is not None: return data
        if service == "host:version": return b"OKAY" + string(self.version)
        if service == "host:devices-l": return b"OKAY" + string(self.listing)
        if service == "host:track-devices":
            sock.watch = True
            return b"OKAY" + string((self.profile["binding"]["serial"] + "\tdevice\n").encode())
        if service.endswith(":features"): return b"OKAY" + string(self.features)
        if service.startswith("host:tport:"): return b"OKAY" + struct.pack("<Q", self.tid)
        if service.startswith("shell,v2,raw:"):
            self.commands.append(service)
            sock.shell = True
            data = self.shell_bytes
            if data is None: data = frame(1, self.values[service.removeprefix("shell,v2,raw:")]) + frame(3, b"\0")
            return b"OKAY" + data
        raise AssertionError("unexpected/lifecycle service: " + service)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        patch = mock.patch.object(cp, "PRIVATE_ROOT", self.root)
        patch.start(); self.addCleanup(patch.stop)
        self.block = contextlib.ExitStack()
        self.block.enter_context(mock.patch("socket.socket", side_effect=AssertionError("real socket forbidden")))
        self.block.enter_context(mock.patch("socket.create_connection", side_effect=AssertionError("real network forbidden")))
        self.block.enter_context(mock.patch("subprocess.Popen", side_effect=AssertionError("process forbidden")))
        self.addCleanup(self.block.close)
        _, self.profile = fixtures()
        self.server = FakeServer(self.profile)
        self.counter = 0

    def approval(self, stage, out):
        return {"approved": True, "stage": stage, "plan_sha256": cp.sha(cp.canonical(ar.plan(stage))),
                "profile_sha256": cp.sha(cp.canonical(self.profile)) if stage == "B" else None,
                "output": str(out.absolute())}

    def run_stage(self, stage="B", connector=None):
        self.counter += 1
        out = self.root / f"run-{self.counter}"
        result = ar.run(stage, self.approval(stage, out), out, self.profile if stage == "B" else None,
                        connector=connector if connector is not None else self.server)
        return result, out

    def test_import_plan_default_cli_and_unapproved_inputs_never_connect(self):
        importlib.reload(ar)  # Real network and subprocess constructors are blocked.
        with mock.patch.object(ar, "connect_existing", side_effect=AssertionError("must be inert")):
            with mock.patch("sys.stdout", io.StringIO()): self.assertEqual(ar.main([]), 0)
            with mock.patch("sys.stdout", io.StringIO()): self.assertEqual(ar.main(["--stage", "B"]), 0)
            with mock.patch("sys.stderr", io.StringIO()): self.assertEqual(ar.main(["--run-approved"]), 2)
        for field, value in (("approved", False), ("plan_sha256", "bad"), ("stage", "A"), ("output", "outside")):
            out = self.root / field
            a = self.approval("B", out); a[field] = value
            with self.subTest(field=field), self.assertRaises(cp.Refusal):
                ar.run("B", a, out, self.profile, connector=self.server)
        self.assertFalse(self.server.requests)

    def test_real_connector_uses_only_fixed_ipv4_endpoint_with_no_retry(self):
        sock = mock.Mock()
        with mock.patch("socket.socket", return_value=sock) as factory:
            self.assertIs(ar.connect_existing(time.monotonic() + 5), sock)
            factory.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect.assert_called_once_with(("127.0.0.1", 5037))
        sock = mock.Mock(); sock.connect.side_effect = ConnectionRefusedError()
        with mock.patch("socket.socket", return_value=sock) as factory, self.assertRaises(ConnectionRefusedError):
            ar.connect_existing(time.monotonic() + 5)
        self.assertEqual(factory.call_count, 1)
        sock.close.assert_called_once()

    def test_interrupted_socket_preserves_partial_raw_log_and_no_retry(self):
        original = FakeSocket.recv
        def interrupt(sock, count):
            if sock.shell and not sock.incoming: raise KeyboardInterrupt()
            return original(sock, count)
        self.server.shell_bytes = frame(1, b"partial\0\xff")
        with mock.patch.object(FakeSocket, "recv", interrupt):
            result, out = self.run_stage()
        self.assertEqual(result["stop"], "KeyboardInterrupt")
        self.assertEqual((out / "00-stdout.bin").read_bytes(), b"partial\0\xff")
        self.assertEqual(len(self.server.commands), 1)

    def test_discovery_version_inventory_and_atomic_usb_only(self):
        result, out = self.run_stage("A")
        self.assertTrue(result["complete"])
        self.assertFalse(result["physical_evidence"])
        self.assertEqual(result["candidate_binding"], self.profile["binding"])
        self.assertEqual(self.server.requests, ["host:version", "host:devices-l", "host:tport:usb"])
        self.assertEqual(result["observations"], [])
        self.check_hashes(result, out)

    def check_hashes(self, result, out):
        for record in result["connections"]:
            for direction in ("tx", "rx"):
                item = record[direction]
                raw = (out / item["file"]).read_bytes()
                self.assertEqual(cp.sha(raw), item["sha256"])
                self.assertEqual(len(raw), item["bytes"])
        for record in result["observations"]:
            for name in ("stdout", "stderr"):
                item = record[name]
                self.assertEqual(cp.sha((out / item["file"]).read_bytes()), item["sha256"])

    def test_full_characterization_fragmented_protocol_fixed_order_and_hashes(self):
        result, out = self.run_stage()
        self.assertTrue(result["complete"], result["stop"])
        self.assertEqual([r["id"] for r in result["observations"]], [o.id for o in ct.schedule()])
        self.assertEqual(self.server.stdin_closes, 39)
        self.assertEqual(len(result["connections"]), 198)
        self.assertEqual(len(self.server.commands), 39)
        self.assertTrue(all(s.closed for s in self.server.sockets))
        self.check_hashes(result, out)
        i = next(i for i, o in enumerate(ct.schedule()) if o.id == "compatible")
        self.assertEqual((out / f"{i:02d}-stdout.bin").read_bytes(), b"fixture,board\0fixture,soc\0")

    def test_unavailable_server_does_not_retry_or_fallback(self):
        connector = mock.Mock(side_effect=ConnectionRefusedError("not running"))
        result, _ = self.run_stage("A", connector)
        self.assertFalse(result["complete"])
        self.assertEqual(connector.call_count, 1)
        self.assertFalse(self.server.requests)

    def test_incompatible_malformed_fail_and_truncated_server(self):
        for response in (b"OKAY00040028", b"NOPE", b"OKAYzzzz", b"OKAYffff", b"OKAY000400", b"FAIL0004nope"):
            self.server.override = lambda service, sock, data=response: data
            result, _ = self.run_stage("A")
            self.assertFalse(result["complete"])
            self.assertEqual(len(result["connections"]), 1)

    def test_inventory_ambiguity_state_identity_and_invalid_transport_reject(self):
        good = self.server.listing
        for listing in (b"", good + good, good.replace(b" device ", b" unauthorized "),
                        good.replace(b"device:icx1301", b"device:other"),
                        good.replace(b"transport_id:7", b"transport_id:0"),
                        good.replace(b"transport_id:7", b"transport_id:18446744073709551616")):
            self.server.listing = listing
            result, _ = self.run_stage("A")
            self.assertFalse(result["complete"])
        self.server.listing = good.replace(b"PRIVATE-SYNTHETIC-OWNER", b"other")
        result, _ = self.run_stage()
        self.assertFalse(result["complete"])
        self.assertFalse(self.server.commands)

    def test_usb_and_atomic_serial_selection_id_mismatch_prevents_shell(self):
        self.server.tid = 8
        result, _ = self.run_stage("A")
        self.assertEqual(result["stop"], "usb_transport_mismatch")
        self.server.tid = 7
        self.server.override = lambda s, sock: b"OKAY" + struct.pack("<Q", 8) if s.startswith("host:tport:serial:") else None
        result, _ = self.run_stage()
        self.assertEqual(result["stop"], "selected_transport_mismatch")
        self.assertFalse(self.server.commands)

    def test_features_missing_or_invalid_prevent_shell(self):
        for features in (b"cmd", b"shell_v2;reboot", b"\xff"):
            self.server.features = features
            result, _ = self.run_stage()
            self.assertEqual(result["stop"], "shell_v2_unavailable")
        self.assertFalse(self.server.commands)

    def test_binary_stderr_exit_and_payload_validation_are_separate(self):
        data = bytes(range(256))
        self.server.shell_bytes = frame(1, data) + frame(2, b"err\0\xff") + frame(3, b"\7")
        result, out = self.run_stage()
        self.assertEqual((out / "00-stdout.bin").read_bytes(), data)
        self.assertEqual((out / "00-stderr.bin").read_bytes(), b"err\0\xff")
        self.assertEqual(result["observations"][0]["exit"], 7)
        self.assertEqual(result["stop"], "command_failed")
        self.assertEqual(len(self.server.commands), 1)

    def test_shell_truncation_invalid_frames_missing_exit_and_trailing_bytes(self):
        for payload in (frame(1, b"partial"), b"\1\0", frame(5, b""), frame(3, b""),
                        frame(3, b"\0\0"), frame(3, b"\0") + b"extra",
                        struct.pack("<BI", 1, 5) + b"abc"):
            self.server = FakeServer(self.profile)
            self.server.shell_bytes = payload
            result, out = self.run_stage()
            self.assertFalse(result["complete"])
            self.assertFalse(result["observations"][0]["complete"])
            self.assertEqual(len(self.server.commands), 1)
            if payload.endswith(b"abc"): self.assertEqual((out / "00-stdout.bin").read_bytes(), b"abc")

    def test_stream_and_session_byte_limits(self):
        self.server.shell_bytes = frame(1, b"x" * 4097) + frame(3, b"\0")
        result, _ = self.run_stage()
        self.assertEqual(result["stop"], "stream_byte_limit")
        with mock.patch.object(cp, "TOTAL_CAP", 40):
            result, _ = self.run_stage()
        self.assertEqual(result["stop"], "session_byte_limit")
        self.assertLessEqual(result["wire_bytes"], 41)

    def test_cancellation_timeout_uncertain_send_and_no_retries(self):
        cancel = threading.Event(); cancel.set()
        out = self.root / "cancel"
        result = ar.run("A", self.approval("A", out), out, connector=self.server, cancel=cancel)
        self.assertEqual(result["stop"], "cancelled")
        self.assertFalse(self.server.requests)
        self.server.send_error = True
        result, _ = self.run_stage("A")
        self.assertEqual(result["stop"], "uncertain_send")
        self.assertEqual(len(result["connections"]), 1)
        self.server.send_error = False
        self.server.hang = True
        with mock.patch.object(cp, "SESSION_MS", 40):
            result, _ = self.run_stage()
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop"], "session_timeout")

    def test_transport_watch_loss_or_notification_invalidates_session(self):
        def change(service, sock):
            if service.startswith("shell,v2,raw:"):
                watch = next(s for s in self.server.sockets if s.watch)
                watch.incoming.extend(b"0000")
                time.sleep(.02)  # Allow the fake watch notification to be consumed.
            return None
        self.server.override = change
        result, _ = self.run_stage()
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop"], "transport_watch_changed_or_lost")
        self.assertLessEqual(len(self.server.commands), 1)

    def test_transport_watch_eof_rejects_and_preserves_partial_record(self):
        def lose(service, sock):
            if service.startswith("shell,v2,raw:"):
                next(s for s in self.server.sockets if s.watch).close()
                time.sleep(.02)
            return None
        self.server.override = lose
        result, _ = self.run_stage()
        self.assertEqual(result["stop"], "transport_watch_changed_or_lost")
        self.assertFalse(result["complete"])
        self.assertLessEqual(len(self.server.commands), 1)

    def test_host_log_failure_stops_and_outside_output_never_connects(self):
        out = self.root / ".." / "escape"
        with self.assertRaises(cp.Refusal): ar.run("A", self.approval("A", out), out, connector=self.server)
        self.assertFalse(self.server.requests)
        real_open = Path.open
        def failing(path, *args, **kwargs):
            stream = real_open(path, *args, **kwargs)
            if path.name == "000-version.tx.bin":
                stream.close()
                return mock.Mock(write=mock.Mock(side_effect=OSError("disk full")))
            return stream
        with mock.patch.object(Path, "open", failing): result, _ = self.run_stage("A")
        self.assertFalse(result["complete"])
        self.assertEqual(result["stop"], "OSError")
        self.assertFalse(self.server.commands)

    def test_unknown_services_commands_profiles_and_overwrite_refused(self):
        session = ar.Session("B", self.root, self.server, threading.Event())
        session.profile = self.profile
        for request in ("host:kill", "host:start-server", "host:connect:example", "shell:reboot",
                        "shell,v2,raw:/system/bin/id -u; reboot"):
            with self.subTest(request=request), self.assertRaises(cp.Refusal): session.allow(request)
        for tid in ("0", "07", str(2**64)):
            p = copy.deepcopy(self.profile); p["binding"]["transport_id"] = tid
            out = self.root / tid
            with self.assertRaises(cp.Refusal): ar.run("B", self.approval("B", out), out, p, connector=self.server)
        result, out = self.run_stage("A")
        original = (out / "manifest.json").read_bytes()
        count = len(self.server.requests)
        with self.assertRaises(FileExistsError): ar.run("A", self.approval("A", out), out, connector=self.server)
        self.assertEqual(len(self.server.requests), count)
        self.assertEqual((out / "manifest.json").read_bytes(), original)


if __name__ == "__main__": unittest.main()
