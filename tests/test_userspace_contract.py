# SPDX-License-Identifier: GPL-2.0-or-later
"""Dependency logic only; no test states claim actual Sony readiness."""

import copy
import json
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from userspace_contract import ContractError, ROLES, evaluate, read_json, validate

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "tools/m9-userspace-contract.json"


class UserspaceContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = read_json(SPEC)
        self.states = dict.fromkeys(ROLES, "ready")

    def node(self, name):
        return next(n for n in self.spec["nodes"] if n["id"] == name)

    def test_all_ready_is_only_model_readiness(self):
        r = evaluate(self.spec, self.states)
        self.assertTrue(r["rockbox_may_start_in_model"])
        self.assertFalse(r["deployment_authorized"])
        self.assertEqual(r["blocked"], {})
        positions = {name: i for i, name in enumerate(r["startup_order"])}
        self.assertLess(positions["firmware_delivery"], positions["modules"])
        self.assertLess(positions["early_protection"], positions["storage"])

    def test_each_lost_role_blocks_startup(self):
        for name in sorted(ROLES):
            for state in ["missing", "failed"]:
                states = dict(self.states, **{name: state})
                with self.subTest(name=name, state=state):
                    r = evaluate(self.spec, states)
                    self.assertFalse(r["rockbox_may_start_in_model"])
                    self.assertIn(name, r["blocked"])

    def test_empty_states_and_independent_branch(self):
        self.assertEqual(evaluate(self.spec, {})["ready"], [])
        states = dict(self.states, display_input="failed")
        r = evaluate(self.spec, states)
        self.assertIn("audio_muted", r["ready"])
        self.assertIn("watchdog", r["ready"])
        self.assertIn("rockbox", r["blocked"])

    def test_duplicate_missing_unknown_roles(self):
        for kind in ["duplicate", "missing", "unknown"]:
            spec = copy.deepcopy(self.spec)
            if kind == "duplicate":
                spec["nodes"][-1] = spec["nodes"][0]
            elif kind == "missing":
                spec["nodes"].pop()
            else:
                spec["nodes"][0]["id"] = "invented"
            with self.assertRaises(ContractError):
                validate(spec)

    def test_cycles_unknown_and_duplicate_dependencies(self):
        for deps in [["rockbox"], ["invented"], ["board"], ["handoff", "handoff"]]:
            self.node("board")["requires"] = deps
            with self.assertRaises(ContractError):
                validate(self.spec)

    def test_cannot_bypass_safety_or_firmware_order(self):
        self.node("rockbox")["requires"] = ["audio_muted", "display_input"]
        with self.assertRaises(ContractError):
            validate(self.spec)
        self.spec = read_json(SPEC)
        self.node("modules")["requires"] = ["storage"]
        self.node("peripherals")["requires"] = ["modules", "firmware_delivery"]
        with self.assertRaises(ContractError):
            validate(self.spec)

    def test_invalid_schema_states_and_evidence(self):
        for states in [{"invented": "ready"}, {"handoff": True}, {"board": "verified"}, []]:
            with self.assertRaises(ContractError):
                evaluate(self.spec, states)
        for key, value in [("version", True), ("context", "selected-sony-board")]:
            spec = dict(self.spec, **{key: value})
            with self.assertRaises(ContractError):
                validate(spec)
        self.node("handoff")["source"] = ""
        with self.assertRaises(ContractError):
            validate(self.spec)

    def test_json_bounds_duplicates_and_unchanged_inputs(self):
        for mode in [stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO, stat.S_IFLNK]:
            with mock.patch("userspace_contract.Path.lstat", return_value=SimpleNamespace(st_mode=mode, st_size=10)), mock.patch("userspace_contract.os.open") as opener:
                with self.assertRaises(ContractError):
                    read_json("synthetic-nonregular")
                opener.assert_not_called()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "input.json"
            for data in [b"", b"{}" * 40000, b'{"a":1,"a":2}', b"\xff", b"{", b"[" * 3000, b"NaN", b"Infinity"]:
                p.write_bytes(data)
                with self.assertRaises(ContractError):
                    read_json(p)
                self.assertEqual(p.read_bytes(), data)
            with self.assertRaises(ContractError):
                read_json(tmp)
            before = SPEC.read_bytes()
            read_json(SPEC)
            self.assertEqual(SPEC.read_bytes(), before)
            # Python's integer digit limit raises ValueError, not JSONDecodeError.
            # Model it explicitly so the test also works when that limit is disabled.
            with mock.patch("userspace_contract.json.loads", side_effect=ValueError("integer digit limit")):
                with self.assertRaises(ContractError):
                    read_json(SPEC)

    def test_cli_blocked_invalid_and_synthetic_ready(self):
        tool = ROOT / "tools/userspace_contract.py"
        with tempfile.TemporaryDirectory() as tmp:
            states = Path(tmp) / "states.json"
            states.write_text(json.dumps(self.states), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(tool), str(SPEC), "--states", str(states)], capture_output=True)
            self.assertEqual(proc.returncode, 0)
            self.assertFalse(json.loads(proc.stdout)["deployment_authorized"])
            proc = subprocess.run([sys.executable, str(tool), str(SPEC)], capture_output=True)
            self.assertEqual(proc.returncode, 1)
            states.write_text('{"handoff":true}', encoding="utf-8")
            proc = subprocess.run([sys.executable, str(tool), str(SPEC), "--states", str(states)], capture_output=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, b"")


if __name__ == "__main__":
    unittest.main()
