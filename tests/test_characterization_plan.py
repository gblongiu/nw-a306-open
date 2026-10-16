# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic offline acquisition tests. No ADB, USB or Sony hardware."""

import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import characterization_plan as cp


def event(data, stream="stdout", at=1):
    return {"stream": stream, "base64": base64.b64encode(data).decode(), "at_ms": at}


def fixtures():
    identity = {
        "uid": "2000", "context": "u:r:shell:s0", "selinux": "Enforcing",
        "ro.product.model": "SYNTHETIC MODEL", "ro.product.device": "icx1301",
        "ro.board.platform": "bengal", "ro.soc.model": "QCS2290",
        "ro.build.version.incremental": "SYNTHETIC BUILD", "ro.boot.slot_suffix": "_b",
        "ro.boot.verifiedbootstate": "green", "ro.boot.flash.locked": "1",
    }
    profile = {"identity": identity, "binding": {
        "serial": "PRIVATE-SYNTHETIC-OWNER", "transport_id": "7", "state": "device", "device_count": 1}}
    metadata = {"kernel": b"synthetic-kernel\n", "tree-link": b"/sys/firmware/devicetree/base\n",
                "compatible": b"fixture,board\0fixture,soc\0", "model": b"Fixture board\0",
                "updater-candidates": b"package:fixture.systemupdater\n",
                "unlock-report": b"\n", "raw-fdt-mode": b"-r-------- root root 128 /sys/firmware/fdt\n"}
    responses = []
    for op in cp.OPERATIONS:
        key = op.id.removeprefix("end:")
        data = (identity[key] + "\n").encode() if key in identity else metadata[key]
        responses.append({"id": op.id, "binding": copy.deepcopy(profile["binding"]),
                          "events": [event(data)], "exit": 0, "elapsed_ms": 2})
    return {"synthetic": True, "plan_sha256": cp.sha(cp.canonical(cp.plan())),
            "responses": responses}, profile


class CharacterizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        patch = mock.patch.object(cp, "PRIVATE_ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        self.fixture, self.profile = fixtures()
        self.output = self.root / "run"

    def run_fixture(self):
        return cp.replay(self.fixture, self.profile, self.output)

    def index(self, id):
        return next(i for i, op in enumerate(cp.OPERATIONS) if op.id == id)

    def test_default_cli_is_plan_only_and_live_option_is_unavailable(self):
        tool = str(Path(cp.__file__).resolve())
        result = subprocess.run([sys.executable, tool], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        p = json.loads(result.stdout)
        self.assertFalse(p["live_backend"])
        digest = p.pop("plan_sha256")
        self.assertEqual(digest, cp.sha(cp.canonical(p)))
        result = subprocess.run([sys.executable, tool, "--live"], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 2)

    def test_complete_replay_hashes_exact_binary_and_checks_identity_twice(self):
        with mock.patch("subprocess.Popen", side_effect=AssertionError("no executable allowed")):
            result = self.run_fixture()
        self.assertTrue(result["complete"])
        self.assertFalse(result["physical_evidence"])
        self.assertEqual(len(result["records"]), len(cp.OPERATIONS))
        i = self.index("compatible")
        raw = (self.output / result["records"][i]["stdout_file"]).read_bytes()
        self.assertEqual(raw, b"fixture,board\0fixture,soc\0")
        self.assertEqual(result["records"][i]["stdout_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(cp.string_list(raw), ["fixture,board", "fixture,soc"])
        self.assertEqual(cp.OPERATIONS[-1].id, "end:ro.boot.flash.locked")
        self.assertEqual(json.loads((self.output / "manifest.json").read_text())["complete"], True)

    def test_profile_refuses_wrong_board_root_unlocked_and_ambiguous_transport(self):
        for key, value in [("uid", "0"), ("ro.product.device", "other"),
                           ("selinux", "Permissive"), ("ro.boot.flash.locked", "0")]:
            p = copy.deepcopy(self.profile)
            p["identity"][key] = value
            with self.subTest(key=key), self.assertRaises(cp.Refusal):
                cp.replay(self.fixture, p, self.output)
        for key, value in [("device_count", 2), ("device_count", True),
                           ("state", "unauthorized"), ("state", "offline"), ("transport_id", "")]:
            p = copy.deepcopy(self.profile)
            p["binding"][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(cp.Refusal):
                cp.replay(self.fixture, p, self.output)
        self.assertFalse(self.output.exists())

    def test_bad_identity_dispatches_no_evidence_requests(self):
        self.fixture["responses"][0]["events"] = [event(b"0\n")]
        result = self.run_fixture()
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["records"]), 1)
        self.assertIn("identity mismatch", result["stop"])

    def test_transport_replacement_at_evidence_group_stops_before_read(self):
        i = self.index("compatible")
        self.fixture["responses"][i]["binding"]["transport_id"] = "8"
        result = self.run_fixture()
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["records"]), i + 1)
        self.assertEqual(result["records"][-1]["stdout_bytes"], 0)

    def test_end_identity_change_invalidates_complete_run(self):
        self.fixture["responses"][-1]["events"] = [event(b"0\n")]
        result = self.run_fixture()
        self.assertFalse(result["complete"])
        self.assertIn("identity mismatch", result["stop"])

    def test_mutated_plan_order_and_remote_injection_are_refused(self):
        for mutation in ("digest", "synthetic", "id", "remote"):
            f = copy.deepcopy(self.fixture)
            if mutation == "digest": f["plan_sha256"] = "0" * 64
            elif mutation == "synthetic": f["synthetic"] = False
            elif mutation == "id": f["responses"][0]["id"] = "reboot"
            else: f["responses"][0]["remote"] = "id; reboot"
            out = self.root / mutation
            with self.subTest(mutation=mutation):
                if mutation in ("digest", "synthetic"):
                    with self.assertRaises(cp.Refusal): cp.replay(f, self.profile, out)
                    self.assertFalse(out.exists())
                else:
                    r = cp.replay(f, self.profile, out)
                    self.assertFalse(r["complete"])
                    self.assertEqual(len(r["records"]), 1)

    def test_stdout_and_stderr_overruns_stop_and_keep_sentinel(self):
        for name in ("stdout", "stderr"):
            f = copy.deepcopy(self.fixture)
            cap = cp.OPERATIONS[0].cap
            f["responses"][0]["events"] = [event(b"x" * cap, name), event(b"!", name, 2)]
            result = cp.replay(f, self.profile, self.root / name)
            self.assertFalse(result["complete"])
            self.assertEqual(result["stop"], "output byte limit")
            self.assertEqual(result["records"][0][name + "_bytes"], cap + 1)
            self.assertEqual(len(result["records"]), 1)

    def test_deadlines_missing_exit_and_permission_denial(self):
        for change in ("timeout", "event-timeout", "missing-exit", "denied", "missing-response"):
            f = copy.deepcopy(self.fixture)
            response = f["responses"][0]
            if change == "timeout": response["elapsed_ms"] = 5001
            elif change == "event-timeout": response["events"][0]["at_ms"] = 5001
            elif change == "missing-exit": response["exit"] = None
            elif change == "denied": response["events"] = [event(b"Permission denied\n", "stderr")]
            else: f["responses"] = []
            r = cp.replay(f, self.profile, self.root / change)
            self.assertFalse(r["complete"])
            self.assertEqual(len(r["records"]), 1)

    def test_total_and_session_bounds(self):
        with mock.patch.object(cp, "TOTAL_CAP", 1):
            f, p = fixtures()
            r = cp.replay(f, p, self.root / "total")
            self.assertEqual(r["stop"], "output byte limit")
        with mock.patch.object(cp, "SESSION_MS", 1):
            f, p = fixtures()
            r = cp.replay(f, p, self.root / "session")
            self.assertEqual(r["stop"], "session deadline")

    def test_malformed_dt_preserves_arbitrary_binary_without_text_conversion(self):
        i = self.index("compatible")
        data = bytes(range(256)) + b"\r\n\0"
        self.fixture["responses"][i]["events"] = [event(data[:100]), event(data[100:], at=2)]
        result = self.run_fixture()
        self.assertFalse(result["complete"])
        self.assertEqual((self.output / result["records"][i]["stdout_file"]).read_bytes(), data)
        for bad in (b"", b"no terminator", b"a\0\0", b"a\n\0", b"\xff\0"):
            with self.subTest(bad=bad), self.assertRaises(cp.Refusal): cp.string_list(bad)

    def test_discovered_link_and_package_output_cannot_become_commands(self):
        for id, data in [("tree-link", b"/dev/block/boot_a\n"),
                         ("updater-candidates", b"package:fixture.systemupdater;reboot\n")]:
            f = copy.deepcopy(self.fixture)
            i = self.index(id)
            f["responses"][i]["events"] = [event(data)]
            r = cp.replay(f, self.profile, self.root / id)
            self.assertFalse(r["complete"])
            self.assertEqual(len(r["records"]), i + 1)

    def test_output_must_be_private_exclusive_and_cannot_traverse(self):
        for out in (self.root, self.root / "child" / ".." / ".." / "outside"):
            with self.subTest(out=out), self.assertRaises(cp.Refusal):
                cp.replay(self.fixture, self.profile, out)
        self.run_fixture()
        original = (self.output / "manifest.json").read_bytes()
        with self.assertRaises(FileExistsError): self.run_fixture()
        self.assertEqual((self.output / "manifest.json").read_bytes(), original)

    def test_symlink_output_refusal(self):
        link = self.root / "link"
        try: link.symlink_to(self.root, target_is_directory=True)
        except OSError: self.skipTest("host does not permit symlinks")
        with self.assertRaises(cp.Refusal):
            cp.replay(self.fixture, self.profile, link / "run")

    def test_interrupted_or_failed_write_stops_without_retries(self):
        original_open = Path.open
        for error in (OSError("disk full"), KeyboardInterrupt()):
            out = self.root / type(error).__name__
            def failing_open(path, *args, **kwargs):
                if path.name == "00-stdout.bin": raise error
                return original_open(path, *args, **kwargs)
            with mock.patch.object(Path, "open", failing_open), self.assertRaises(type(error)):
                cp.replay(self.fixture, self.profile, out)
            r = json.loads((out / "manifest.json").read_text())
            self.assertFalse(r["complete"])
            self.assertEqual(len(r["records"]), 1)
            self.assertIn("host I/O", r["stop"])

    def test_json_bounds_duplicates_and_nonfinite_values(self):
        path = self.root / "input.json"
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b"[" * 2000, b"\xff", b"x" * (4 * 1024 * 1024 + 1)):
            path.write_bytes(data)
            with self.assertRaises(cp.Refusal): cp.load_json(path)

    def test_malformed_stream_and_encoded_chunk_refuse_without_crashing(self):
        for change in ("stream", "base64", "chunk", "time"):
            f = copy.deepcopy(self.fixture)
            e = f["responses"][0]["events"][0]
            if change == "stream": e["stream"] = []
            elif change == "base64": e["base64"] = "not base64!"
            elif change == "chunk": e["base64"] = "A" * 10000
            else: e["at_ms"] = True
            r = cp.replay(f, self.profile, self.root / change)
            self.assertFalse(r["complete"])
            self.assertEqual(len(r["records"]), 1)

    def test_cli_summary_excludes_private_identity(self):
        f, p = self.root / "fixture.json", self.root / "expected.json"
        f.write_text(json.dumps(self.fixture))
        p.write_text(json.dumps(self.profile))
        stdout = io.StringIO()
        with mock.patch("sys.stdout", stdout):
            status = cp.main(["--fixture", str(f), "--expected", str(p), "--out", str(self.output)])
        self.assertEqual(status, 0)
        self.assertNotIn("PRIVATE-SYNTHETIC-OWNER", stdout.getvalue())
        self.assertNotIn("SYNTHETIC BUILD", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
