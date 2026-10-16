# SPDX-License-Identifier: GPL-2.0-or-later
"""Pure N2 scope/interpretation tests. Real sockets/processes are blocked."""
import contextlib
import importlib
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fastboot_n2_plan as n2


class N2Tests(unittest.TestCase):
    def setUp(self):
        self.block = contextlib.ExitStack()
        self.block.enter_context(mock.patch("subprocess.Popen", side_effect=AssertionError("no executable")))
        self.block.enter_context(mock.patch("socket.socket", side_effect=AssertionError("no socket")))
        self.addCleanup(self.block.close)

    def classify(self, value, code=0, variable="is-userspace", status="ok"):
        return n2.classify_optional(variable, b"", value, code, status)

    def test_import_plan_fixed_minimal_scope_digest_and_no_backend(self):
        importlib.reload(n2)
        p = n2.plan()
        self.assertFalse(p["approved"])
        self.assertFalse(p["live_backend"])
        self.assertEqual([a[1:] for a in p["native_commands"]], [["devices", "-l"], ["-s", "S", "getvar", "product"], ["-s", "S", "getvar", "is-userspace"]])
        self.assertEqual(p["pre_identity"], p["post_identity"])
        self.assertEqual(len(p["pre_identity"]), 11)
        self.assertEqual(p["entry"]["count"], 1)
        self.assertEqual((p["per_stream_cap"], p["operation_ms"], p["session_ms"], p["retries"]), (4096, 5000, 450000, 0))
        digest = n2.cp.sha(n2.cp.canonical(p))
        p["native_commands"].append(["getvar", "all"])
        self.assertNotEqual(digest, n2.cp.sha(n2.cp.canonical(p)))

    def test_explicit_yes_no_classify(self):
        for val, meaning in [("yes", "fastbootd"), ("no", "bootloader-fastboot")]:
            r = self.classify(("is-userspace: " + val + "\r\nFinished. Total time: 0.001s\r\n").encode())
            self.assertEqual(r["classification"], meaning)
            self.assertTrue(r["post_return_guards_permitted"])

    def test_exact_n1_empty_version_is_unavailable_not_hardware_failure(self):
        raw = b"version-bootloader: \r\nFinished. Total time: 0.001s\r\n"
        r = self.classify(raw, variable="version-bootloader")
        self.assertEqual(r["state"], "unavailable")
        self.assertEqual(r["classification"], "inconclusive")
        self.assertFalse(r["hardware_failure_inferred"])

    def test_empty_userspace_is_never_assumed_no(self):
        r = self.classify(b"is-userspace: \n")
        self.assertEqual(r["state"], "unavailable")
        self.assertEqual(r["classification"], "inconclusive")
        self.assertTrue(r["post_return_guards_permitted"])

    def test_explicit_unsupported_inconclusive_even_native_exit_zero(self):
        for code in (0, 1):
            for raw in [b"getvar:is-userspace FAILED (remote: 'Unknown variable')\n", b"getvar:is-userspace\nFAILED (remote: 'unknown command')\nFinished. Total time: 0.001s\n"]:
                r = self.classify(raw, code, status="ok" if code == 0 else "command_failed")
                self.assertEqual(r["state"], "unsupported")
                self.assertEqual(r["classification"], "inconclusive")
                self.assertFalse(r["hardware_failure_inferred"])
                self.assertFalse(r["post_return_guards_permitted"])

    def test_other_named_value_inconclusive_and_no_post_requests(self):
        r = self.classify(b"is-userspace: unknown\n")
        self.assertEqual(r["classification"], "inconclusive")
        self.assertFalse(r["post_return_guards_permitted"])

    def test_ambiguous_malformed_transport_or_permission_errors_stop(self):
        for raw in [b"", b"is-userspace: no\nis-userspace: no\n", b"is-userspace: no\nFAILED (remote: 'unknown variable')\n", b"other: no\n", b"is-userspace: no\0\n", b"is-userspace: \xff\n", b"fastboot: error: Write to device failed (no link)\n", b"FAILED (remote: 'permission denied')\n", b"x" * 4097]:
            with self.subTest(raw=raw), self.assertRaises(n2.cp.Refusal): self.classify(raw)
        with self.assertRaises(n2.cp.Refusal): self.classify(b"is-userspace: no\n", code=1)
        with self.assertRaises(n2.cp.Refusal): self.classify(b"is-userspace: no\n", status="timeout")
        with self.assertRaises(n2.cp.Refusal): self.classify(b"is-userspace: no\n", code=True)


if __name__ == "__main__": unittest.main()
