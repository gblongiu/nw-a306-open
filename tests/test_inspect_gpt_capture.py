# SPDX-License-Identifier: GPL-2.0-or-later
"""CRC-valid malformed geometry must not become a restoration claim."""
import struct
import unittest
import zlib

from tools.inspect_gpt_capture import HEADER, InspectionError, inspect_bytes


def fixture(partitions=((34, 100), (101, 150)), last=200, alternate=255):
    result = bytearray(4096)
    entries = bytearray(128 * 4)
    for index, (start, end) in enumerate(partitions):
        off = index * 128
        entries[off:off + 16] = b"T" * 16
        entries[off + 16:off + 32] = bytes([index + 1]) * 16
        struct.pack_into("<QQQ", entries, off + 32, start, end, 0)
        name = f"part{index}".encode("utf-16le")
        entries[off + 56:off + 56 + len(name)] = name
    header = bytearray(HEADER.pack(b"EFI PART", 0x10000, 92, 0, 0, 1, alternate,
                                  34, last, bytes(16), 2, 4, 128, zlib.crc32(entries)))
    struct.pack_into("<I", header, 16, zlib.crc32(header))
    result[512:512 + len(header)] = header
    result[1024:1024 + len(entries)] = entries
    return result


class GptCaptureTests(unittest.TestCase):
    def inspect(self, data, **kwargs):
        return inspect_bytes(data, 512, 1024, **kwargs)

    def test_valid_fragment_is_not_restore_proof(self):
        result = self.inspect(fixture(), capture_start_lba=0)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["restoration_capability"], "not_established")

    def test_crc_valid_template_rejected_as_geometry(self):
        result = self.inspect(fixture(((34, 100), (101, 100)), last=0, alternate=0))
        self.assertTrue(result["checks"]["header_crc_matches"])
        self.assertTrue(result["checks"]["array_crc_matches"])
        self.assertFalse(result["checks"]["geometry_consistent"])

    def test_overlapping_partitions(self):
        result = self.inspect(fixture(((34, 180), (100, 150))))
        self.assertTrue(any("overlapping" in p for p in result["problems"]))

    def test_outside_usable_range(self):
        self.assertFalse(self.inspect(fixture(((33, 100),)))["checks"]["geometry_consistent"])

    def test_crc_valid_array_overlapping_header_rejected(self):
        data = fixture()
        struct.pack_into("<Q", data, 512 + 72, 1)
        struct.pack_into("<I", data, 512 + 16, 0)
        struct.pack_into("<I", data, 512 + 16, zlib.crc32(data[512:604]))
        result = self.inspect(data)
        self.assertTrue(result["checks"]["header_crc_matches"])
        self.assertTrue(result["checks"]["array_crc_matches"])
        self.assertIn("entry array overlaps a GPT header", result["problems"])

    def test_capture_origin_is_checked(self):
        result = self.inspect(fixture(), capture_start_lba=1)
        self.assertFalse(result["checks"]["geometry_consistent"])
        self.assertTrue(result["capture_origin_checked"])

    def test_header_corruption(self):
        data = fixture()
        data[512 + 56] ^= 1
        self.assertFalse(self.inspect(data)["checks"]["header_crc_matches"])

    def test_array_corruption(self):
        data = fixture()
        data[1024 + 16] ^= 1
        self.assertFalse(self.inspect(data)["checks"]["array_crc_matches"])

    def test_huge_entry_count_stops_before_allocation(self):
        data = fixture()
        struct.pack_into("<I", data, 512 + 80, 2**32 - 1)
        with self.assertRaises(InspectionError):
            self.inspect(data)

    def test_truncated_and_negative_regions(self):
        for data, ho, ao in [(b"", 512, 1024), (fixture()[:1200], 512, 1024), (fixture(), -1, 1024)]:
            with self.subTest(ho=ho), self.assertRaises(InspectionError):
                inspect_bytes(data, ho, ao)


if __name__ == "__main__":
    unittest.main()
