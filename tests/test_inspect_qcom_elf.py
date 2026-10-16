# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounds and corruption tests; proprietary fixtures are never committed."""

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from tools.inspect_qcom_elf import InspectionError, MAX_FILE, inspect_bytes, inspect_file


def fixture(bits=64, metadata=True):
    ehsize, phsize = (64, 56) if bits == 64 else (52, 32)
    count = 3
    ident = b"\x7fELF" + bytes([2 if bits == 64 else 1, 1, 1]) + bytes(9)
    hdr_fmt = "<HHIQQQIHHHHHH" if bits == 64 else "<HHIIIIIHHHHHH"
    hdr = struct.pack(hdr_fmt, 2, 183 if bits == 64 else 40, 1, 0x1000,
                      ehsize, 0, 0, ehsize, phsize, count, 0, 0, 0)
    md = bytes(120 if metadata else 0)
    code_size = count * 48
    envelope_size = 48 + len(md) + code_size + 4 + 4
    segments = [(0, 0x07000000, 0, 0, 0, ehsize + count * phsize, 0, 0),
                (0, 0x02200000, 512, 0, 0, envelope_size, envelope_size, 0),
                (1, 5, 1024, 0x1000, 0x1000, 4, 4, 4)]
    phdrs = b""
    for kind, flags, off, va, pa, size, mem, align in segments:
        values = (kind, flags, off, va, pa, size, mem, align) if bits == 64 else (kind, off, va, pa, size, mem, flags, align)
        phdrs += struct.pack("<IIQQQQQQ" if bits == 64 else "<8I", *values)
    header = ident + hdr + phdrs
    table = hashlib.sha384(header).digest() + bytes(48) + hashlib.sha384(b"CODE").digest()
    mbn = struct.pack("<12I", 5, 6, 0, 0, code_size + 8, code_size,
                      0xffffffff, 4, 0xffffffff, 4, 0, len(md))
    result = bytearray(1028)
    result[:len(header)] = header
    result[512:512 + envelope_size] = mbn + md + table + b"SIGNCERT"
    result[1024:] = b"CODE"
    return result


class QualcommElfTests(unittest.TestCase):
    def test_mixed_architectures_and_regions(self):
        for bits in [32, 64]:
            with self.subTest(bits=bits):
                result = inspect_bytes(fixture(bits))
                self.assertEqual(result["elf_bits"], bits)
                envelope = result["qualcomm_envelope"]
                self.assertEqual(envelope["segment_hash_check"], "match")
                self.assertEqual(envelope["regions"]["oem_metadata"]["size"], 120)
                self.assertEqual(envelope["signature_verification"], "not_performed")
                self.assertEqual(envelope["device_acceptance"], "not_established")

    def test_modified_executable_data_detected(self):
        data = fixture()
        data[-1] ^= 1
        result = inspect_bytes(data)["qualcomm_envelope"]
        self.assertEqual(result["segment_hash_check"], "mismatch")
        self.assertFalse(result["segment_hashes"][2]["matches"])

    def test_modified_elf_header_detected(self):
        data = fixture()
        data[24] ^= 1  # entrypoint, covered by header-placeholder hash
        self.assertFalse(inspect_bytes(data)["qualcomm_envelope"]["segment_hashes"][0]["matches"])

    def test_signature_corruption_is_not_misreported_as_authenticated(self):
        data = fixture()
        envelope = inspect_bytes(data)["qualcomm_envelope"]
        data[envelope["regions"]["oem_signature"]["offset"]] ^= 1
        result = inspect_bytes(data)["qualcomm_envelope"]
        self.assertEqual(result["segment_hash_check"], "match")
        self.assertEqual(result["signature_verification"], "not_performed")

    def test_metadata_size_accounting_is_explicit(self):
        data = fixture()
        struct.pack_into("<I", data, 512 + 16, 272)
        envelope = inspect_bytes(data)["qualcomm_envelope"]
        self.assertEqual(envelope["image_size_accounting"], "includes_metadata")
        struct.pack_into("<I", data, 512 + 16, 271)
        with self.assertRaises(InspectionError):
            inspect_bytes(data)

    def test_adversarial_lengths_rejected(self):
        for offset, value, fmt in [(32, 2**64 - 1, "<Q"), (56, 65535, "<H"),
                                   (512 + 20, 2**32 - 1, "<I"), (512 + 44, 2**32 - 1, "<I")]:
            with self.subTest(offset=offset):
                data = fixture()
                struct.pack_into(fmt, data, offset, value)
                with self.assertRaises(InspectionError):
                    inspect_bytes(data)

    def test_out_of_bounds_segment_rejected(self):
        data = fixture()
        struct.pack_into("<Q", data, 64 + 2 * 56 + 8, 1027)
        with self.assertRaises(InspectionError):
            inspect_bytes(data)

    def test_truncated_headers_rejected(self):
        for size in [0, 4, 16, 51, 63, 100, 600]:
            with self.subTest(size=size), self.assertRaises(InspectionError):
                inspect_bytes(fixture()[:size])

    def test_unsupported_formats_not_guessed(self):
        for offset, value in [(4, 3), (5, 2), (6, 0), (516, 7)]:
            with self.subTest(offset=offset):
                data = fixture()
                data[offset] = value
                with self.assertRaises(InspectionError):
                    inspect_bytes(data)

    def test_ambiguous_hash_segments_rejected(self):
        data = fixture()
        struct.pack_into("<I", data, 64 + 2 * 56 + 4, 0x02000000)
        with self.assertRaises(InspectionError):
            inspect_bytes(data)

    def test_paged_layout_not_falsely_verified(self):
        data = fixture()
        struct.pack_into("<I", data, 64 + 2 * 56 + 4, 0x00100005)
        self.assertEqual(inspect_bytes(data)["qualcomm_envelope"]["segment_hash_check"],
                         "not_checked_unsupported_hash_layout")

    def test_oversized_regular_file_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "oversized.elf"
            with p.open("wb") as stream:
                stream.truncate(MAX_FILE + 1)
            with self.assertRaises(InspectionError):
                inspect_file(p)

    def test_ordinary_file_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample.elf"
            data = bytes(fixture(32))
            p.write_bytes(data)
            before = p.stat()
            self.assertEqual(inspect_file(p)["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(p.read_bytes(), data)
            self.assertEqual(p.stat().st_mtime_ns, before.st_mtime_ns)


if __name__ == "__main__":
    unittest.main()
