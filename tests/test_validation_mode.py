# SPDX-License-Identifier: GPL-2.0-or-later
"""Prevent optimized Python from silently disabling regression checks."""

from pathlib import Path
import subprocess
import sys
import unittest


class ValidationModeTests(unittest.TestCase):
    def test_validators_refuse_disabled_assertions(self):
        for name in ("codec_regression.py", "playback_validation.py",
                     "linux_vm_validation.py", "linux_drm_validation.py"):
            with self.subTest(script=name):
                result = subprocess.run(
                    [sys.executable, "-O", str(Path(__file__).with_name(name)), "--help"],
                    capture_output=True, timeout=10,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"validation requires assertions", result.stderr)
                self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
