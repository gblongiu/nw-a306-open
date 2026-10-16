# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounded static PE/AArch64 address mapping, disassembly and adjacent xrefs.

Accepts an already extracted PE, not an ELF/FV container. Never loads or executes
the input. Xrefs are instruction candidates, not proof of runtime reachability.
Capstone 5 is optional and required only for instruction analysis.
"""
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct

LIMIT = 16 * 1024 * 1024


class Invalid(ValueError):
    pass


def region(data, offset, size):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise Invalid("region outside input")
    return data[offset:offset + size]


@dataclass(frozen=True)
class Section:
    name: str
    rva: int
    virtual_size: int
    offset: int
    raw_size: int
    flags: int


class Image:
    def __init__(self, data):
        if not 64 <= len(data) <= LIMIT:
            raise Invalid("input size bound")
        self.data = data
        pe = struct.unpack('<I', region(data, 0x3c, 4))[0] if data[:2] == b'MZ' else 0
        if region(data, pe, 4) != b'PE\0\0':
            raise Invalid("expected extracted PE image")
        machine, count, _, _, _, optional_size, _ = struct.unpack('<HHIIIHH', region(data, pe + 4, 20))
        if machine != 0xaa64 or not 1 <= count <= 64 or optional_size < 112:
            raise Invalid("expected bounded AArch64 PE32+")
        optional = region(data, pe + 24, optional_size)
        if struct.unpack_from('<H', optional)[0] != 0x20b:
            raise Invalid("expected PE32+")
        self.entry = struct.unpack_from('<I', optional, 16)[0]
        self.base = struct.unpack_from('<Q', optional, 24)[0]
        self.sections = []
        table = pe + 24 + optional_size
        region(data, table, count * 40)
        for i in range(count):
            row = region(data, table + i * 40, 40)
            name, virtual_size, rva, raw_size, offset = struct.unpack_from('<8sIIII', row)
            flags = struct.unpack_from('<I', row, 36)[0]
            try:
                label = name.rstrip(b'\0').decode('ascii')
            except UnicodeError as exc:
                raise Invalid("non-ASCII section name") from exc
            if rva + max(virtual_size, raw_size) > 2**32 or self.base + rva + max(virtual_size, raw_size) > 2**64:
                raise Invalid("address overflow")
            if raw_size:
                region(data, offset, raw_size)
                if offset < table + count * 40:
                    raise Invalid("section overlaps headers")
            section = Section(label, rva, virtual_size, offset, raw_size, flags)
            for old in self.sections:
                if raw_size and old.raw_size and max(offset, old.offset) < min(offset + raw_size, old.offset + old.raw_size):
                    raise Invalid("overlapping raw sections")
                if max(rva, old.rva) < min(rva + max(virtual_size, raw_size), old.rva + max(old.virtual_size, old.raw_size)):
                    raise Invalid("overlapping virtual sections")
            self.sections.append(section)

    def mapped(self, rva, size=1, executable=False):
        if rva < 0 or size <= 0:
            raise Invalid("invalid mapped range")
        for s in self.sections:
            if s.rva <= rva and rva + size <= s.rva + s.raw_size:
                if executable and not s.flags & 0x20000000:
                    raise Invalid("range is not executable")
                return s.offset + rva - s.rva
        raise Invalid("range not file-backed in one section")

    def file_rva(self, offset):
        for s in self.sections:
            if s.offset <= offset < s.offset + s.raw_size:
                return s.rva + offset - s.offset
        raise Invalid("offset not mapped by a section")

    def disassemble(self, start, end):
        if start % 4 or end % 4 or not 0 < end - start <= 1024 * 1024:
            raise Invalid("unaligned or oversized instruction range")
        offset = self.mapped(start, end - start, executable=True)
        try:
            from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
        except ImportError as exc:
            raise Invalid("Capstone 5 required for static instruction analysis") from exc
        md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
        md.detail = True
        md.skipdata = True
        return list(md.disasm(region(self.data, offset, end - start), self.base + start))

    def instructions(self, start, end):
        return [{'rva': i.address - self.base, 'file_offset': self.mapped(i.address - self.base, len(i.bytes)),
                 'bytes': bytes(i.bytes).hex(), 'mnemonic': i.mnemonic, 'operands': i.op_str}
                for i in self.disassemble(start, end)]

    def xrefs(self, target):
        """Direct ADR or immediately adjacent ADRP/ADD only; not a CFG solver."""
        from capstone.arm64 import ARM64_OP_REG, ARM64_OP_IMM
        self.mapped(target)
        out = []
        for s in self.sections:
            if not s.flags & 0x20000000 or not s.raw_size:
                continue
            ins = self.disassemble(s.rva, s.rva + s.raw_size)
            for index, a in enumerate(ins):
                if a.mnemonic not in ('adr', 'adrp'):
                    continue
                if a.mnemonic == 'adr' and a.operands[1].imm == self.base + target:
                    out.append({'rvas': [a.address - self.base], 'kind': 'adr'})
                if a.mnemonic != 'adrp' or index + 1 >= len(ins):
                    continue
                d = ins[index + 1]
                if (d.address == a.address + 4 and d.mnemonic == 'add' and len(d.operands) == 3
                        and d.operands[0].type == ARM64_OP_REG and d.operands[1].type == ARM64_OP_REG
                        and d.operands[1].reg == a.operands[0].reg and d.operands[2].type == ARM64_OP_IMM
                        and not d.operands[2].shift.value
                        and a.operands[1].imm + d.operands[2].imm == self.base + target):
                    out.append({'rvas': [a.address - self.base, d.address - self.base], 'kind': 'adjacent-adrp-add'})
        return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--start', type=lambda v: int(v, 0))
    parser.add_argument('--end', type=lambda v: int(v, 0))
    parser.add_argument('--xref', type=lambda v: int(v, 0))
    args = parser.parse_args()
    if (args.start is None) != (args.end is None):
        parser.error('start and end must be supplied together')
    with args.image.open('rb') as stream:
        data = stream.read(LIMIT + 1)
    image = Image(data)
    result = {'sha256': hashlib.sha256(data).hexdigest(), 'image_base': image.base,
              'entry_rva': image.entry, 'sections': [vars(s) for s in image.sections],
              'firmware_executed': False, 'reachability_proven': False}
    if args.start is not None:
        result['instructions'] = image.instructions(args.start, args.end)
    if args.xref is not None:
        result['xrefs'] = image.xrefs(args.xref)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
