# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic metadata only; these fixtures describe no NW-A306 unit."""

import hashlib
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inspect_extcsd import InspectionError, inspect, inspect_file


def fixture():
    data = bytearray(512)
    data[192] = 8
    data[212:216] = (61071360).to_bytes(4, "little")
    data[168] = data[226] = 32
    return data


class ExtCsdTests(unittest.TestCase):
    def test_capacity_and_endian(self):
        r = inspect(fixture())
        self.assertEqual(r["user_capacity_bytes"], 31268536320)
        self.assertEqual(r["each_boot_region_bytes"], 4194304)
        self.assertEqual(r["rpmb_region_bytes"], 4194304)
        data = fixture()
        data[212:216] = bytes.fromhex("ffffffff")
        data[226] = data[168] = 255
        r = inspect(data)
        self.assertEqual(r["user_capacity_bytes"], 2199023255040)
        self.assertEqual(r["each_boot_region_bytes"], 33423360)

    def test_access_is_independent_of_boot_selection(self):
        data = fixture()
        data[179] = 0x40 | (2 << 3) | 3
        r = inspect(data)
        self.assertEqual(r["emmc_boot_selection"], "boot2")
        self.assertEqual(r["partition_access"], "rpmb")
        self.assertTrue(r["boot_ack_requested"])
        self.assertNotIn("slot", r)

    def test_supported_selection_and_access_values(self):
        data = fixture()
        for selection, name in [(0, "disabled"), (1, "boot1"), (2, "boot2"), (7, "user")]:
            for access in range(8):
                data[179] = selection << 3 | access
                r = inspect(data)
                self.assertEqual(r["emmc_boot_selection"], name)
                self.assertEqual(r["partition_access"], ("user", "boot1", "boot2", "rpmb", "gp1", "gp2", "gp3", "gp4")[access])

    def test_reserved_and_unsupported_values(self):
        for value in [24, 32, 40, 48, 128, 255]:
            data = fixture()
            data[179] = value
            with self.subTest(value=value), self.assertRaises(InspectionError):
                inspect(data)
        for rev in [0, 7, 9, 255]:
            data = fixture()
            data[192] = rev
            with self.assertRaises(InspectionError):
                inspect(data)

    def test_capacity_selection_consistency(self):
        for offset, config in [(226, 8), (226, 2), (168, 3)]:
            data = fixture()
            data[offset] = 0
            data[179] = config
            with self.assertRaises(InspectionError):
                inspect(data)
        data = fixture()
        data[168] = data[226] = 0
        self.assertEqual(inspect(data)["each_boot_region_bytes"], 0)
        data[212:216] = b"\0" * 4
        with self.assertRaises(InspectionError):
            inspect(data)

    def test_protection_and_reliability_are_distinct(self):
        data = fixture()
        data[174] = 9
        data[173] = 0x40
        data[167] = 1
        r = inspect(data)
        self.assertEqual(r["boot_write_protection_status"], [
            {"region": "boot1", "power_on": True, "permanent": False},
            {"region": "boot2", "power_on": False, "permanent": True},
        ])
        self.assertEqual(r["raw_registers"]["WR_REL_SET"]["value"], 1)
        self.assertIn("no Sony identity", r["limits"])

    def test_wrong_lengths(self):
        for length in [0, 1, 511, 513, 1024]:
            with self.subTest(length=length), self.assertRaises(InspectionError):
                inspect(bytes(length))

    def test_file_read_only_and_cli_errors(self):
        for mode in [stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO, stat.S_IFLNK]:
            with mock.patch("inspect_extcsd.Path.lstat", return_value=SimpleNamespace(st_mode=mode, st_size=512)), mock.patch("inspect_extcsd.os.open") as opener:
                with self.assertRaises(InspectionError):
                    inspect_file("synthetic-nonregular")
                opener.assert_not_called()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.bin"
            path.write_bytes(fixture())
            before = path.read_bytes()
            r = inspect_file(path)
            self.assertEqual(r["input_sha256"], hashlib.sha256(before).hexdigest())
            self.assertEqual(path.read_bytes(), before)
            with self.assertRaises(InspectionError):
                inspect_file(directory)
            path.write_bytes(before[:511])
            proc = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "tools/inspect_extcsd.py"), str(path)], capture_output=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, b"")
            self.assertEqual(path.read_bytes(), before[:511])


if __name__ == "__main__":
    unittest.main()
