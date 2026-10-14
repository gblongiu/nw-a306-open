# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic safety and metadata tests; no private firmware fixture required."""

import hashlib
import io
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tools.inspect_upg import (
    CHUNK_SIZE,
    InspectionError,
    inspect_file,
    inspect_header,
    read_exact_at,
)


def fixture(decimal=20):
    body_size = (decimal // 16 + 1) * 16
    header = b"NWWM" + b"ab" * 28 + b"0" * 36
    header += f"{decimal:012d}".encode("ascii") + b"f" * 20
    return header + b"\xa5" * body_size


class InspectorTests(unittest.TestCase):
    def test_valid_metadata_and_hashes_without_modification(self):
        data = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.upg"
            path.write_bytes(data)
            original_mtime = path.stat().st_mtime_ns
            result = inspect_file(path, True)
            self.assertEqual(result["body_minus_decimal"], 12)
            self.assertEqual(result["decimal_field_96_108"], 20)
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["md5"], hashlib.md5(data).hexdigest())
            self.assertEqual(result["authentication_status"], "not verified")
            self.assertEqual(result, inspect_file(path, True))
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, original_mtime)

    def test_all_observed_length_differences(self):
        for decimal in range(1, 33):
            with self.subTest(decimal=decimal):
                data = fixture(decimal)
                result = inspect_header(data[:128], len(data))
                self.assertEqual(result["body_minus_decimal"], 16 - decimal % 16)

    def test_large_file_arithmetic_without_payload_allocation(self):
        decimal = 5 * 1024**3 + 4
        header = fixture()[:96] + f"{decimal:012d}".encode() + b"f" * 20
        result = inspect_header(header, 128 + decimal + 12)
        self.assertGreater(result["body_size"], 2**32)

    def test_truncated_headers(self):
        for length in (0, 4, 60, 96, 127):
            with self.subTest(length=length), self.assertRaises(InspectionError):
                inspect_header(fixture()[:length], length)

    def test_malformed_and_unsupported_fields(self):
        for offset, replacement in ((0, b"PK"), (4, b"g"), (60, b"1"),
                                    (96, b"-"), (107, b"\xff"), (108, b"0")):
            data = bytearray(fixture())
            data[offset:offset + len(replacement)] = replacement
            with self.subTest(offset=offset), self.assertRaises(InspectionError):
                inspect_header(data[:128], len(data))

    def test_invalid_body_lengths(self):
        for size in (127, 128, 129, 144, 159, 161, 176, 2**63):
            with self.subTest(size=size), self.assertRaises(InspectionError):
                inspect_header(fixture()[:128], size)
        data = fixture()[:96] + b"0" * 12 + b"f" * 20
        with self.assertRaises(InspectionError):
            inspect_header(data, 144)

    def test_invalid_offsets_rejected_before_io(self):
        for offset, length in ((-1, 1), (0, -1), (0, CHUNK_SIZE + 1),
                               (10, 1), (9, 2), (2**64, 16)):
            with self.subTest(offset=offset, length=length):
                stream = Mock()
                with self.assertRaises(InspectionError):
                    read_exact_at(stream, offset, length, 9)
                stream.seek.assert_not_called()
                stream.read.assert_not_called()

    def test_short_read_detected(self):
        with self.assertRaises(InspectionError):
            read_exact_at(io.BytesIO(b"short"), 0, 8, 8)

    def test_hash_stream_reads_are_bounded(self):
        data = fixture(CHUNK_SIZE * 2 + 4)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large-synthetic.upg"
            path.write_bytes(data)
            real_fdopen = os.fdopen
            lengths = []

            class CheckedReader:
                def __init__(self, stream):
                    self.stream = stream

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    self.stream.close()

                def read(self, size):
                    lengths.append(size)
                    self.assert_bounded(size)
                    return self.stream.read(size)

                @staticmethod
                def assert_bounded(size):
                    if not 0 <= size <= CHUNK_SIZE:
                        raise AssertionError("unbounded read")

                def __getattr__(self, name):
                    return getattr(self.stream, name)

            with patch("tools.inspect_upg.os.fdopen", lambda fd, mode: CheckedReader(real_fdopen(fd, mode))):
                result = inspect_file(path, True)
            self.assertGreater(len(lengths), 3)
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())

    def test_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(InspectionError):
                inspect_file(tmp)

    def test_nonregular_inputs_rejected_before_open(self):
        for mode in (stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO, stat.S_IFLNK):
            with self.subTest(mode=mode), patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=mode)), patch("tools.inspect_upg.os.open") as opener:
                with self.assertRaises(InspectionError):
                    inspect_file("synthetic-nonregular")
                opener.assert_not_called()

    def test_replaced_file_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.upg"
            path.write_bytes(fixture())
            original = path.stat()
            replacement = SimpleNamespace(st_mode=original.st_mode,
                                          st_dev=original.st_dev,
                                          st_ino=original.st_ino + 1)
            with patch("tools.inspect_upg.os.fstat", return_value=replacement):
                with self.assertRaisesRegex(InspectionError, "replaced"):
                    inspect_file(path)


if __name__ == "__main__":
    unittest.main()
