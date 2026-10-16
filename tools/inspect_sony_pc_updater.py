# SPDX-License-Identifier: GPL-2.0-or-later
"""Verify selected static locators in the acquired Sony PC updater, without loading it.

This is an exact-artifact evidence check, not an updater, command sender or proof
of Sony bootloader behavior. See docs/m10-sony-host-evidence.md for provenance,
the independent disassembly and the limits of these instruction checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from inspect_arm64_pe import Invalid, Section, region

LIMIT = 2 * 1024 * 1024
SHA256 = '7c31378ed74d11d3eb49c91994675a632f5e911908cf52fe9134912575bf47a6'


class Pe32:
    def __init__(self, data):
        if not 64 <= len(data) <= LIMIT or data[:2] != b'MZ':
            raise Invalid('bounded PE32 required')
        self.data = data
        pe = struct.unpack('<I', region(data, 0x3c, 4))[0]
        if region(data, pe, 4) != b'PE\0\0':
            raise Invalid('PE signature')
        machine, count, _, _, _, size, _ = struct.unpack('<HHIIIHH', region(data, pe + 4, 20))
        if machine != 0x14c or not 1 <= count <= 16 or size < 96:
            raise Invalid('x86 PE32 required')
        optional = region(data, pe + 24, size)
        if struct.unpack_from('<H', optional)[0] != 0x10b:
            raise Invalid('PE32 optional header')
        self.base = struct.unpack_from('<I', optional, 28)[0]
        table = pe + 24 + size
        region(data, table, count * 40)
        self.sections = []
        for index in range(count):
            row = region(data, table + index * 40, 40)
            name, virtual, rva, raw, offset = struct.unpack_from('<8sIIII', row)
            flags = struct.unpack_from('<I', row, 36)[0]
            region(data, offset, raw)
            if raw and offset < table + count * 40:
                raise Invalid('raw section overlaps headers')
            if self.base + rva + max(virtual, raw) > 2**32:
                raise Invalid('PE32 address overflow')
            s = Section(name.rstrip(b'\0').decode('ascii'), rva, virtual, offset, raw, flags)
            for old in self.sections:
                if raw and old.raw_size and max(offset, old.offset) < min(offset + raw, old.offset + old.raw_size):
                    raise Invalid('raw section overlap')
                if max(rva, old.rva) < min(rva + max(virtual, raw), old.rva + max(old.virtual_size, old.raw_size)):
                    raise Invalid('virtual section overlap')
            self.sections.append(s)

    def at(self, rva, size, executable=False):
        if rva < 0 or size <= 0:
            raise Invalid('invalid range')
        for s in self.sections:
            if s.rva <= rva and rva + size <= s.rva + s.raw_size:
                if executable and not s.flags & 0x20000000:
                    raise Invalid('non-executable section')
                return region(self.data, s.offset + rva - s.rva, size)
        raise Invalid('range not backed by one section')

    def call_target(self, rva):
        raw = self.at(rva, 5, executable=True)
        if raw[0] != 0xe8:
            raise Invalid('not an x86 direct relative call')
        target = rva + 5 + struct.unpack_from('<i', raw, 1)[0]
        self.at(target, 1, executable=True)
        return target


def inspect(data):
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise Invalid('not the pinned Sony PC updater; no policy inference permitted')
    image = Pe32(data)
    checks = []
    for rva, expected, label in [
        (0x24903, bytes.fromhex('be78710610'), 'GetDevInfo diagnostic address'),
        (0x24bcd, bytes.fromhex('6801940000'), 'GetDevInfo operation 0x9401'),
        (0x28dad, bytes.fromhex('be408a0610'), 'StartFWUpdate diagnostic address'),
        (0x28fd3, bytes.fromhex('6802940000'), 'StartFWUpdate operation 0x9402'),
        (0x21707, bytes.fromhex('c745cc01940000'), 'eligibility checks operation 0x9401'),
        (0x21719, bytes.fromhex('c745cc02940000'), 'eligibility checks operation 0x9402'),
        (0x27b07, bytes.fromhex('68408d0610'), 'default-capability.xml address'),
        (0x27d18, bytes.fromhex('68f08e0610'), 'firmware-capable storage XPath address'),
    ]:
        if image.at(rva, len(expected), executable=True) != expected:
            raise Invalid('instruction locator mismatch: ' + label)
        checks.append({'rva': rva, 'check': label})
    for rva, target, label in [
        (0x2175a, 0x24877, 'eligible-device path calls GetDevInfo'),
        (0x29be8, 0x2451a, 'MTP worker calls DeleteFile'),
        (0x29d60, 0x23977, 'MTP worker calls CopyFile'),
        (0x23e96, 0x293fe, 'CopyFile calls StreamCopy'),
        (0x2a48f, 0x28d4b, 'update-start worker calls StartFWUpdate'),
    ]:
        if image.call_target(rva) != target:
            raise Invalid('call locator mismatch: ' + label)
        checks.append({'rva': rva, 'target_rva': target, 'check': label})
    for rva, text, encoding in [
        (0x67178, 'CWmFwPortableDevice::GetDevInfo', 'utf-16-le'),
        (0x68a40, 'CWmFwPortableDevice::StartFWUpdate', 'utf-16-le'),
        (0x68d40, 'default-capability.xml', 'utf-16-le'),
        (0x68ef0, '/devices/device/storage/fw-update-supported[text()="true"]', 'ascii'),
    ]:
        expected = (text + '\0').encode(encoding)
        if image.at(rva, len(expected)) != expected:
            raise Invalid('data locator mismatch')
        checks.append({'rva': rva, 'check': text})
    return {'sha256': SHA256, 'machine': 'x86 PE32', 'image_base': image.base,
            'checks': checks, 'input_executed': False,
            'sony_loader_policy_established': False,
            'limits': 'Selected exact instruction/data locators; not a complete CFG or device implementation proof.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    args = parser.parse_args()
    with args.image.open('rb') as stream:
        data = stream.read(LIMIT + 1)
    print(json.dumps(inspect(data), indent=2))


if __name__ == '__main__':
    main()
