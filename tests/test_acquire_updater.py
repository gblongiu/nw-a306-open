# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic one-artifact acquisition with real network/process paths blocked."""
import io
import json
import zipfile
import unittest
from unittest import mock

import test_adb_readonly as af
import acquire_updater as au

cp, ar = af.cp, af.ar


def fixture_apk():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr("AndroidManifest.xml", b"synthetic XML")
        z.writestr("classes.dex", bytes(range(256)) * 16)
    return stream.getvalue()


class AcquisitionTests(unittest.TestCase):
    setUp = af.AdapterTests.setUp
    check_hashes = af.AdapterTests.check_hashes

    def prepare(self):
        self.target = "/system_ext/priv-app/Synthetic/fixture.apk"
        self.u1 = self.root / "u1"; self.u1.mkdir()
        raw = ("package:" + self.target + "\n").encode()
        (self.u1 / "11-stdout.bin").write_bytes(raw)
        manifest = {"stage": "U1", "complete": True, "stop": None, "expected_profile": self.profile,
                    "observations": [None] * 11 + [{"id": "updater-path", "complete": True, "exit": 0,
                    "stdout": {"file": "11-stdout.bin", "bytes": len(raw), "sha256": cp.sha(raw)}}]}
        (self.u1 / "manifest.json").write_text(json.dumps(manifest))
        self.apk = fixture_apk()
        self.server.fragment = 4096
        self.server.values[au.sr.UPDATER.remote] = raw
        self.metadata = f"-rw-r--r-- 1 root root {len(self.apk)} 2026-01-01 00:00 {self.target}\n".encode()
        self.server.values[au.operations(self.target)[12].remote] = self.metadata
        self.server.values[au.operations(self.target)[13].remote] = self.apk

    def approval(self, output):
        return {"approved": True, "plan_sha256": cp.sha(cp.canonical(au.plan(self.target))),
                "profile_sha256": cp.sha(cp.canonical(self.profile)),
                "u1_manifest_sha256": cp.sha((self.u1 / "manifest.json").read_bytes()), "output": str(output)}

    def run_apk(self):
        self.counter += 1; out = self.root / f"apk-{self.counter}"
        result = au.run(self.u1, self.approval(out), out, connector=self.server)
        return result, out

    def test_fixed_scope_bounds_success_byte_identity_and_hashes(self):
        self.prepare()
        ops = au.operations(self.target)
        self.assertEqual(len(ops), 27)
        self.assertEqual(ops[:11], cp.IDENTITY)
        self.assertEqual(ops[-11:], cp.OPERATIONS[-11:])
        self.assertEqual(ops[13].remote, "/system/bin/toybox head -c 16777217 " + self.target)
        self.assertEqual(ops[13].cap, 16777216)
        self.assertEqual(ops[13].timeout_ms, 30000)
        result, out = self.run_apk()
        self.assertTrue(result["complete"], result["stop"])
        self.assertEqual(len(result["connections"]), 138)
        self.assertEqual(self.server.commands.count("shell,v2,raw:" + ops[13].remote), 1)
        self.assertEqual((out / "automagic.apk").read_bytes(), self.apk)
        self.assertEqual(result["artifact"]["sha256"], cp.sha(self.apk))
        self.check_hashes(result, out)

    def test_false_stale_wrong_profile_and_changed_U1_evidence_never_connect(self):
        self.prepare()
        for key, value in (("approved", False), ("plan_sha256", "bad"), ("profile_sha256", "bad"),
                           ("u1_manifest_sha256", "bad"), ("output", "elsewhere")):
            out = self.root / key; approval = self.approval(out); approval[key] = value
            with self.assertRaises(cp.Refusal): au.run(self.u1, approval, out, connector=self.server)
        (self.u1 / "11-stdout.bin").write_bytes(b"package:/system/other.apk\n")
        with self.assertRaises(cp.Refusal): self.run_apk()
        self.assertFalse(self.server.requests)

    def test_denial_stops_before_transfer_no_retry(self):
        self.prepare()
        def denied(service, sock):
            if service == "shell,v2,raw:" + au.operations(self.target)[12].remote:
                sock.shell = True; self.server.commands.append(service)
                return b"OKAY" + af.frame(2, b"Permission denied\n") + af.frame(3, b"\1")
            return None
        self.server.override = denied
        result, out = self.run_apk()
        self.assertEqual(result["stop"], "inaccessible")
        self.assertEqual(len(result["observations"]), 13)
        self.assertFalse((out / "automagic.apk").exists())
        self.assertNotIn("shell,v2,raw:" + au.operations(self.target)[13].remote, self.server.commands)

    def test_nonregular_zero_and_oversized_files_stop_before_content(self):
        self.prepare()
        for data in (self.metadata.replace(b"-rw-r--r--", b"lrwxrwxrwx"),
                     self.metadata.replace(str(len(self.apk)).encode(), b"0"),
                     self.metadata.replace(str(len(self.apk)).encode(), b"16777217")):
            self.server.values[au.operations(self.target)[12].remote] = data
            before = len(self.server.commands)
            result, _ = self.run_apk()
            self.assertFalse(result["complete"])
            self.assertEqual(len(result["observations"]), 13)
            self.assertEqual(len(self.server.commands) - before, 13)

    def test_short_or_invalid_zip_content_preserved_without_artifact_promotion(self):
        self.prepare()
        for data in (self.apk[:-1], b"x" * len(self.apk)):
            self.server.values[au.operations(self.target)[13].remote] = data
            result, out = self.run_apk()
            self.assertFalse(result["complete"])
            self.assertEqual((out / "13-stdout.bin").read_bytes(), data)
            self.assertFalse((out / "automagic.apk").exists())
            self.assertEqual(len(result["observations"]), 14)

    def test_changed_path_and_metadata_stop_without_further_reads(self):
        self.prepare()
        self.server.values[au.sr.UPDATER.remote] = b"package:/system/other.apk\n"
        result, _ = self.run_apk()
        self.assertEqual(result["stop"], "registered target changed")
        self.assertEqual(len(result["observations"]), 12)
        self.server.values[au.sr.UPDATER.remote] = ("package:" + self.target + "\n").encode()
        calls = 0
        def changed(service, sock):
            nonlocal calls
            if service == "shell,v2,raw:" + au.operations(self.target)[12].remote:
                calls += 1
                if calls == 2:
                    sock.shell = True; self.server.commands.append(service)
                    return b"OKAY" + af.frame(1, self.metadata.replace(b"00:00", b"00:01")) + af.frame(3, b"\0")
            return None
        self.server.override = changed
        result, out = self.run_apk()
        self.assertEqual(result["stop"], "target metadata changed")
        self.assertFalse((out / "automagic.apk").exists())

    def test_identity_and_transport_change_stop(self):
        self.prepare()
        self.server.tid = 8
        result, _ = self.run_apk()
        self.assertEqual(result["stop"], "usb_transport_mismatch")
        self.assertFalse(self.server.commands)
        self.server.tid = 7
        self.server.values[cp.IDENTITY[0].remote] = b"0\n"
        result, _ = self.run_apk()
        self.assertEqual(result["stop"], "identity mismatch: uid")

    def test_zip_crc_duplicate_traversal_and_expansion_limits(self):
        self.assertTrue(au.apk_structure(fixture_apk())["all_zip_crc_checks_passed"])
        bad = bytearray(fixture_apk()); at = bad.index(b"synthetic XML"); bad[at] ^= 1
        with self.assertRaises(cp.Refusal): au.apk_structure(bytes(bad))
        for name in ("../outside", "/absolute", "link/target"):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, "w") as z:
                z.writestr("AndroidManifest.xml", b"x"); z.writestr("classes.dex", b"x"); z.writestr(name, b"x")
            data = stream.getvalue()
            if name == "link/target": data = data.replace(b"link/target", b"link\\target")
            with self.assertRaises(cp.Refusal): au.apk_structure(data)

    def test_partial_binary_interruption_preserved_and_no_retry(self):
        self.prepare()
        original = af.FakeSocket.recv
        def interrupted(sock, count):
            if sock.shell and not sock.incoming and self.server.commands[-1].endswith(au.operations(self.target)[13].remote):
                raise KeyboardInterrupt()
            return original(sock, count)
        def partial(service, sock):
            if service == "shell,v2,raw:" + au.operations(self.target)[13].remote:
                sock.shell = True; self.server.commands.append(service)
                return b"OKAY" + af.frame(1, b"partial\0\xff")
            return None
        self.server.override = partial
        with mock.patch.object(af.FakeSocket, "recv", interrupted): result, out = self.run_apk()
        self.assertEqual(result["stop"], "KeyboardInterrupt")
        self.assertEqual((out / "13-stdout.bin").read_bytes(), b"partial\0\xff")
        self.assertEqual(len(result["observations"]), 14)

    def test_unknown_services_outputs_and_attempt_reuse_refused(self):
        self.prepare()
        session = au.Acquisition(self.target, self.root, self.server, af.threading.Event()); session.profile = self.profile
        for command in ("shell,v2,raw:/system/bin/id -u; reboot", "shell,v2,raw:/system/bin/toybox cat " + self.target,
                        "shell,v2,raw:/system/bin/toybox head -c 16777217 /system/other.apk", "host:kill"):
            with self.assertRaises(cp.Refusal): session.allow(command)
        result, out = self.run_apk()
        original = (out / "manifest.json").read_bytes(); before = len(self.server.requests)
        with self.assertRaises(FileExistsError): au.run(self.u1, self.approval(out), out, connector=self.server)
        self.assertEqual(len(self.server.requests), before)
        self.assertEqual((out / "manifest.json").read_bytes(), original)


if __name__ == "__main__": unittest.main()
