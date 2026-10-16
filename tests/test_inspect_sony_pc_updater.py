# SPDX-License-Identifier: GPL-2.0-or-later
import pathlib
import struct
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
from inspect_sony_pc_updater import Invalid, Pe32, inspect


def fixture():
    b = bytearray(0x600)
    b[:2] = b'MZ'
    struct.pack_into('<I', b, 0x3c, 0x80)
    b[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', b, 0x84, 0x14c, 1, 0, 0, 0, 0xe0, 0)
    struct.pack_into('<H', b, 0x98, 0x10b)
    struct.pack_into('<I', b, 0x98 + 28, 0x10000000)
    struct.pack_into('<8sIIII', b, 0x178, b'.text', 0x300, 0x1000, 0x200, 0x400)
    struct.pack_into('<I', b, 0x178 + 36, 0x60000020)
    b[0x410:0x415] = b'\xe8' + struct.pack('<i', 0x1005 - 0x1015)
    b[0x405] = 0xc3
    return b


class EvidenceMappingTests(unittest.TestCase):
    def test_distinct_file_rva_and_virtual_address(self):
        image = Pe32(fixture())
        self.assertEqual(image.base, 0x10000000)
        self.assertEqual(image.at(0x1005, 1), b'\xc3')

    def test_signed_backward_call(self):
        self.assertEqual(Pe32(fixture()).call_target(0x1010), 0x1005)

    def test_zero_fill_and_cross_boundary_rejected(self):
        image = Pe32(fixture())
        for rva, size in [(0x1200, 1), (0x11ff, 2), (-1, 1), (0x1000, 0)]:
            with self.subTest(rva=rva, size=size), self.assertRaises(Invalid):
                image.at(rva, size)

    def test_noncall_and_unmapped_call_target_rejected(self):
        with self.assertRaises(Invalid):
            Pe32(fixture()).call_target(0x1005)
        b = fixture()
        struct.pack_into('<i', b, 0x411, 0x1200 - 0x1015)
        with self.assertRaises(Invalid):
            Pe32(b).call_target(0x1010)

    def test_nonexecutable_call_rejected(self):
        b = fixture()
        struct.pack_into('<I', b, 0x178 + 36, 0x40000040)
        with self.assertRaises(Invalid):
            Pe32(b).call_target(0x1010)

    def test_wrong_machine_truncation_and_header_overlap(self):
        for mutation in ['machine', 'truncated', 'overlap']:
            b = fixture()
            if mutation == 'machine':
                struct.pack_into('<H', b, 0x84, 0xaa64)
            elif mutation == 'truncated':
                b = b[:0x450]
            else:
                struct.pack_into('<I', b, 0x178 + 20, 0x100)
            with self.subTest(mutation=mutation), self.assertRaises(Invalid):
                Pe32(b)

    def test_unpinned_input_cannot_yield_sony_findings(self):
        with self.assertRaises(Invalid):
            inspect(fixture())


if __name__ == '__main__':
    unittest.main()
