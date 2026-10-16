# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic address-mapping and instruction-xref checks; no firmware execution."""
import importlib.util
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspect_arm64_pe import Image, Invalid, LIMIT


def fixture(base=0):
    b = bytearray(0x400)
    b[:4] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', b, 4, 0xaa64, 1, 0, 0, 0, 112, 0)
    struct.pack_into('<H', b, 24, 0x20b)
    struct.pack_into('<I', b, 40, 0x1000)
    struct.pack_into('<Q', b, 48, base)
    struct.pack_into('<8sIIII', b, 136, b'.text', 0x300, 0x1000, 0x200, 0x200)
    struct.pack_into('<I', b, 172, 0x60000020)
    # adrp x0, current page; add x0, x0, #0x100; ret.
    b[0x200:0x20c] = bytes.fromhex('0000009000000491c0035fd6')
    return b


class MappingTests(unittest.TestCase):
    def test_file_and_rva_are_distinct_and_zero_fill_not_readable(self):
        p = Image(fixture())
        self.assertEqual(p.mapped(0x1100), 0x300)
        self.assertEqual(p.file_rva(0x300), 0x1100)
        for value in [0, 0x1200, 0x12ff]:
            with self.assertRaises(Invalid): p.mapped(value)
        with self.assertRaises(Invalid): p.mapped(0x11ff, 2)

    def test_truncated_headers_wrong_architecture_and_elf_rejected(self):
        for data in [b'\x7fELF' + b'\0'*64, fixture()[:150], b'\0'*(LIMIT+1)]:
            with self.assertRaises(Invalid): Image(data)
        for offset, value in [(4, 0x14c), (6, 65), (24, 0x10b)]:
            b = fixture(); struct.pack_into('<H', b, offset, value)
            with self.assertRaises(Invalid): Image(b)

    def test_raw_outside_file_headers_and_overlap_rejected(self):
        for offset in [0, 0x3ff]:
            b = fixture(); struct.pack_into('<I', b, 156, offset)
            with self.assertRaises(Invalid): Image(b)
        b = fixture(); struct.pack_into('<H', b, 6, 2)
        b[176:216] = b[136:176]
        with self.assertRaises(Invalid): Image(b)

    def test_executable_bounds_alignment_and_address_overflow(self):
        b = fixture(); struct.pack_into('<I', b, 172, 0x40000040)
        p = Image(b)
        with self.assertRaises(Invalid): p.mapped(0x1000, executable=True)
        for a,z in [(0x1001,0x1008),(0x1000,0x1204),(0x1000,0x1000)]:
            with self.assertRaises(Invalid): Image(fixture()).disassemble(a,z)
        with self.assertRaises(Invalid): Image(fixture(2**64-1))


@unittest.skipUnless(importlib.util.find_spec('capstone'), 'optional Capstone 5 not installed')
class InstructionTests(unittest.TestCase):
    def test_adjacent_reference_and_nonzero_load_base(self):
        for base in [0, 0x400000]:
            p = Image(fixture(base))
            self.assertEqual(p.xrefs(0x1100), [{'rvas':[0x1000,0x1004], 'kind':'adjacent-adrp-add'}])
            i = p.instructions(0x1000,0x100c)
            self.assertEqual(i[0]['file_offset'],0x200)
            self.assertEqual(i[2]['mnemonic'],'ret')

    def test_intervening_clobber_not_promoted_to_reference(self):
        b = fixture(); b[0x204:0x210] = bytes.fromhex('000080d200000491c0035fd6')
        self.assertEqual(Image(b).xrefs(0x1100), [])

    def test_direct_adr_reference(self):
        b = fixture(); b[0x200:0x204] = bytes.fromhex('00080010')
        self.assertEqual(Image(b).xrefs(0x1100), [{'rvas':[0x1000], 'kind':'adr'}])


if __name__ == '__main__':
    unittest.main()
