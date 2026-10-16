# SPDX-License-Identifier: GPL-2.0-or-later
"""Standing admission and exact U1/H1 plans on the existing fake transport."""
import copy
import io
import unittest
from unittest import mock

import test_adb_readonly as af

ar, cp, ct = af.ar, af.cp, af.ct
sr = ar.sr


class StandingTests(unittest.TestCase):
    setUp = af.AdapterTests.setUp
    check_hashes = af.AdapterTests.check_hashes

    def grant(self, name="state"):
        state = self.root / name
        state.mkdir()
        return {"approved": True, "version": 1, "policy_sha256": sr.POLICY_SHA256,
                "profile_sha256": cp.sha(cp.canonical(self.profile)),
                "plans": {k: cp.sha(cp.canonical(ar.plan(k))) for k in ("U1", "H1")},
                "state_directory": str(state)}

    def approval(self, stage, out):
        return {"approved": True, "stage": stage, "plan_sha256": cp.sha(cp.canonical(ar.plan(stage))),
                "profile_sha256": cp.sha(cp.canonical(self.profile)), "output": str(out)}

    def run_plan(self, grant, stage="U1", turn="fixture-turn"):
        self.counter += 1
        out = self.root / f"standing-{self.counter}"
        self.server.values[sr.UPDATER.remote] = b"package:/system/priv-app/Fixture/base.apk\n"
        result = ar.run(stage, self.approval(stage, out), out, self.profile, connector=self.server,
                        standing_grant=grant, turn_id=turn)
        return result, out

    def test_exact_approved_scopes_bookends_caps_and_exclusions(self):
        self.assertEqual(sr.U1, cp.IDENTITY + (cp.Operation("updater-path", "/system/bin/pm path --user 0 com.sony.walkman.systemupdater", 16384),) + cp.OPERATIONS[-11:])
        self.assertEqual(sr.H1[11:-11], tuple(ct.REGISTRY[k] for k in
                         ("sound-cards", "sound-pcm", "input-devices", "graphics-names", "power-names", "block-names")))
        for stage, count in (("U1", 23), ("H1", 28)):
            self.assertEqual(len(ar.operations(stage)), count)
            self.assertEqual(ar.operations(stage)[:11], cp.IDENTITY)
            self.assertEqual(ar.operations(stage)[-11:], cp.OPERATIONS[-11:])
            self.assertIn("standing_readonly.py", ar.plan(stage)["code_sha256"])
            session = ar.Session(stage, self.root, self.server, af.threading.Event())
            session.profile = self.profile
            for key in ("compatible", "model", "partitions", "raw-fdt-mode", "regulator-names"):
                with self.assertRaises(cp.Refusal): session.allow("shell,v2,raw:" + ct.REGISTRY[key].remote)
        self.assertFalse(self.server.requests)

    def test_package_paths_valid_base_and_splits_reject_malformed_unbounded_and_duplicate(self):
        for data in (b"package:/system/priv-app/Fixture/base.apk\n",
                     b"package:/data/app/~~abc=/fixture-X+/base.apk\npackage:/data/app/~~abc=/fixture-X+/split_config.apk\n"):
            sr.validate(sr.UPDATER, data, self.profile)
        bad = (b"", b"\n", b"package:/system/base.apk", b"package:relative.apk\n",
               b"package:/system/../base.apk\n", b"package:/system//base.apk\n",
               b"package:/system/./base.apk\n", b"package:/system/base.apk\r\n",
               b"package:/system/base.apk\0\n", b"package:/system/base.apk;reboot\n",
               b"package:/system/base.apk\n" * 2,
               b"package:/" + b"x" * 16384 + b".apk\n",
               b"".join(f"package:/system/split{i}.apk\n".encode() for i in range(129)))
        for data in bad:
            with self.subTest(data=data[:80]), self.assertRaises(cp.Refusal):
                sr.validate(sr.UPDATER, data, self.profile)

    def test_both_complete_fixed_plans_integrity_and_per_turn_limit(self):
        grant = self.grant()
        for stage, count, connections in (("U1", 23, 118), ("H1", 28, 143)):
            before = len(self.server.commands)
            result, out = self.run_plan(grant, stage)
            self.assertTrue(result["complete"], result["stop"])
            self.assertEqual(len(result["connections"]), connections)
            self.assertEqual(self.server.commands[before:], ["shell,v2,raw:" + o.remote for o in ar.operations(stage)])
            self.assertEqual(len(result["observations"]), count)
            self.assertFalse(result["live_server_acquisition"])
            self.check_hashes(result, out)
        before = len(self.server.requests)
        with self.assertRaisesRegex(cp.Refusal, "session limit"): self.run_plan(grant)
        self.assertEqual(len(self.server.requests), before)
        events = sorted((self.root / "state").glob("*.json"))
        self.assertEqual(len(events), 4)
        self.assertTrue(all(cp.load_json(p)["complete"] for p in events[1::2]))

    def test_no_grant_false_scope_profile_policy_and_stale_plan_fail_before_connect(self):
        grant = self.grant()
        for key, value in (("approved", False), ("version", True), ("policy_sha256", "bad"),
                           ("profile_sha256", "bad"), ("plans", {"U1": "old", "H1": "old"})):
            changed = copy.deepcopy(grant); changed[key] = value
            with self.subTest(key=key), self.assertRaises(cp.Refusal): self.run_plan(changed)
        out = self.root / "missing-grant"
        with self.assertRaises(cp.Refusal): ar.run("U1", self.approval("U1", out), out, self.profile, connector=self.server)
        with mock.patch.object(sr, "POLICY_SHA256", "bad"), self.assertRaises(cp.Refusal): self.run_plan(grant)
        old = copy.deepcopy(grant)
        with mock.patch.object(sr, "U1", sr.U1[:-1]), self.assertRaises(cp.Refusal): self.run_plan(old)
        self.assertFalse(self.server.requests)
        self.assertFalse(list((self.root / "state").glob("*.json")))

    def test_failed_u1_stops_turn_and_quarantines_only_its_plan_across_turns(self):
        grant = self.grant()
        def denied(service, sock):
            if service == "shell,v2,raw:" + sr.UPDATER.remote:
                sock.shell = True; self.server.commands.append(service)
                return b"OKAY" + af.frame(2, b"Permission denied\n") + af.frame(3, b"\1")
            return None
        self.server.override = denied
        result, out = self.run_plan(grant)
        self.assertEqual(result["stop"], "inaccessible")
        self.assertEqual(len(result["observations"]), 12)
        self.check_hashes(result, out)
        before = len(self.server.requests)
        with self.assertRaisesRegex(cp.Refusal, "turn stopped"): self.run_plan(grant, "H1")
        with self.assertRaisesRegex(cp.Refusal, "quarantined"): self.run_plan(grant, turn="later-human-turn")
        self.assertEqual(len(self.server.requests), before)
        self.server.override = None
        result, _ = self.run_plan(grant, "H1", "later-human-turn")
        self.assertTrue(result["complete"])

    def test_each_h1_denial_ends_sequence_with_no_end_checks_or_retry(self):
        for index, op in enumerate(sr.H1[11:-11], 11):
            grant = self.grant(f"state-{index}")
            self.server = af.FakeServer(self.profile)
            self.server.fragment = 65536
            def denied(service, sock, remote=op.remote):
                if service == "shell,v2,raw:" + remote:
                    sock.shell = True; self.server.commands.append(service)
                    return b"OKAY" + af.frame(2, b"Permission denied\n") + af.frame(3, b"\1")
                return None
            self.server.override = denied
            result, _ = self.run_plan(grant, "H1")
            self.assertEqual(result["stop"], "inaccessible")
            self.assertEqual(len(result["observations"]), index + 1)
            self.assertEqual(len(self.server.commands), index + 1)
            before = len(self.server.requests)
            with self.assertRaisesRegex(cp.Refusal, "quarantined"):
                self.run_plan(grant, "H1", "later-human-turn")
            self.assertEqual(len(self.server.requests), before)

    def test_existing_lock_unfinished_or_corrupt_journal_blocks_without_network(self):
        grant = self.grant()
        lock = self.root / "state/session.lock"
        lock.write_text("other")
        with self.assertRaises(FileExistsError): self.run_plan(grant)
        lock.unlink()
        def failed_append(path, *args, **kwargs):
            if path.name == "0001.json": raise OSError("simulated result-write failure")
            return original(path, *args, **kwargs)
        original = af.Path.open
        with mock.patch.object(af.Path, "open", failed_append), self.assertRaises(OSError): self.run_plan(grant)
        before = len(self.server.requests)
        with self.assertRaisesRegex(cp.Refusal, "unfinished"): self.run_plan(grant, "H1", "later-human-turn")
        self.assertEqual(len(self.server.requests), before)
        event = self.root / "state/0000.json"
        event.write_text('{"bad":1}')
        with self.assertRaises(cp.Refusal): self.run_plan(grant)
        self.assertEqual(len(self.server.requests), before)

    def test_identity_and_transport_failure_stop_before_metadata(self):
        grant = self.grant()
        self.server.values[cp.IDENTITY[0].remote] = b"0\n"
        result, _ = self.run_plan(grant)
        self.assertEqual(result["stop"], "identity mismatch: uid")
        self.assertEqual(len(self.server.commands), 1)
        grant = self.grant("other-state")
        self.server = af.FakeServer(self.profile)
        self.server.override = lambda s, sock: b"OKAY" + af.struct.pack("<Q", 8) if s.startswith("host:tport:serial:") else None
        result, _ = self.run_plan(grant)
        self.assertEqual(result["stop"], "selected_transport_mismatch")
        self.assertFalse(self.server.commands)

    def test_malformed_package_payload_and_stream_cap_stop_without_ending_identity(self):
        for index, data in enumerate((b"package:relative.apk\n", b"x" * 16385)):
            grant = self.grant(f"state-{index}")
            self.server = af.FakeServer(self.profile)
            self.server.fragment = 65536
            def malformed(service, sock, payload=data):
                if service == "shell,v2,raw:" + sr.UPDATER.remote:
                    sock.shell = True; self.server.commands.append(service)
                    return b"OKAY" + af.frame(1, payload) + af.frame(3, b"\0")
                return None
            self.server.override = malformed
            result, _ = self.run_plan(grant)
            self.assertFalse(result["complete"])
            self.assertEqual(result["stop"], "invalid package path" if index == 0 else "stream_byte_limit")
            self.assertEqual(len(result["observations"]), 12)

    def test_default_cli_inert_and_extraneous_standing_args_refused(self):
        with mock.patch.object(ar, "connect_existing", side_effect=AssertionError("offline")):
            for stage in ("U1", "H1"):
                with mock.patch("sys.stdout", io.StringIO()): self.assertEqual(ar.main(["--stage", stage]), 0)
            with mock.patch("sys.stderr", io.StringIO()):
                self.assertEqual(ar.main(["--stage", "U1", "--turn-id", "no-approval"]), 2)
        self.assertFalse(self.server.requests)

    def test_changed_previous_manifest_blocks_following_plan(self):
        grant = self.grant()
        result, out = self.run_plan(grant)
        self.assertTrue(result["complete"])
        (out / "manifest.json").write_text("{}")
        before = len(self.server.requests)
        with self.assertRaisesRegex(cp.Refusal, "evidence integrity"):
            self.run_plan(grant, "H1")
        self.assertEqual(len(self.server.requests), before)


if __name__ == "__main__": unittest.main()
