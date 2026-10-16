# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounded, read-only ELF and Qualcomm MBN v6 envelope inspection.

Format references (not imported implementations): ELF gABI; Qualcomm Secure
Boot and Image Authentication; coreboot mbn_tools.py at
812d0e2f626dfea7e7deb960a8dc08ff0e026bc1 (Boot_Hdr); Linux qcom_mdt_loader.
Region accounting was checked against the public RB1 23.12 rescue package.
This tool neither authenticates a signer nor establishes device acceptance.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import struct

MAX_FILE = 32 * 1024 * 1024
MAX_PHDRS = 128
HASH_TYPE_MASK = 0x07000000
HASH_TYPE = 0x02000000
PAGE_MODE = 0x00100000


class InspectionError(ValueError):
    pass


def region(data, offset, length):
    if offset < 0 or length < 0 or offset > len(data) or length > len(data) - offset:
        raise InspectionError("region exceeds input bounds")
    return data[offset:offset + length]


def mbn_v6(data, offset, length, phdrs):
    blob = region(data, offset, length)
    if len(blob) < 48:
        raise InspectionError("truncated MBN v6 header")
    words = struct.unpack_from("<12I", blob)
    if words[1] != 6:
        raise InspectionError("unsupported MBN version; only v6 is implemented")
    sizes = [48, words[10], words[11], words[5], words[2], words[3], words[7], words[9]]
    names = ["header", "qti_metadata", "oem_metadata", "hash_table",
             "qti_signature", "qti_certificates", "oem_signature", "oem_certificates"]
    cursor = 0
    regions = {}
    for name, size in zip(names, sizes):
        content = region(blob, cursor, size)
        regions[name] = {"offset": offset + cursor, "size": size,
                         "sha256": hashlib.sha256(content).hexdigest()}
        cursor += size
    # Published tools and reference images differ in metadata size accounting.
    signed_parts = sum(sizes[3:])
    if words[4] == signed_parts:
        accounting = "excludes_metadata"
    elif words[4] == signed_parts + words[10] + words[11]:
        accounting = "includes_metadata"
    else:
        raise InspectionError("inconsistent declared MBN image size")
    padding = blob[cursor:]
    if any(byte not in (0, 255) for byte in padding):
        raise InspectionError("unaccounted non-padding bytes in hash segment")
    table = region(data, regions["hash_table"]["offset"], regions["hash_table"]["size"])
    hashes = []
    supported = len(table) == 48 * len(phdrs) and not any(p["flags"] & PAGE_MODE for p in phdrs)
    if supported:
        for i, p in enumerate(phdrs):
            stored = table[i * 48:(i + 1) * 48]
            if p["flags"] & HASH_TYPE_MASK == HASH_TYPE or not p["file_size"]:
                expected = bytes(48)
                rule = "zero_hash_segment_or_empty"
            else:
                expected = hashlib.sha384(region(data, p["offset"], p["file_size"])).digest()
                rule = "sha384_file_region"
            hashes.append({"segment": i, "rule": rule, "matches": stored == expected})
    return {"version": 6, "image_id": words[0], "declared_image_size": words[4],
            "image_size_accounting": accounting, "regions": regions,
            "padding_bytes": len(padding),
            "segment_hashes": hashes,
            "segment_hash_check": ("match" if all(x["matches"] for x in hashes) else "mismatch")
            if supported else "not_checked_unsupported_hash_layout",
            "signature_verification": "not_performed",
            "device_acceptance": "not_established"}


def inspect_bytes(data):
    if len(data) > MAX_FILE:
        raise InspectionError("input exceeds 32 MiB limit")
    if len(data) < 16 or data[:4] != b"\x7fELF":
        raise InspectionError("not an ELF image")
    if data[5] != 1 or data[6] != 1:
        raise InspectionError("only ELF version 1 little-endian inputs are supported")
    if data[4] == 1:
        hdr, ph, bits = struct.Struct("<HHIIIIIHHHHHH"), struct.Struct("<8I"), 32
    elif data[4] == 2:
        hdr, ph, bits = struct.Struct("<HHIQQQIHHHHHH"), struct.Struct("<IIQQQQQQ"), 64
    else:
        raise InspectionError("unsupported ELF class")
    fields = hdr.unpack(region(data, 16, hdr.size))
    elf_type, machine, version, entry, phoff = fields[:5]
    ehsize, phsize, count = fields[7:10]
    if version != 1 or ehsize != 16 + hdr.size or phsize != ph.size:
        raise InspectionError("unsupported ELF header/program-header profile")
    if not 1 <= count <= MAX_PHDRS or phoff < ehsize:
        raise InspectionError("invalid or excessive program-header count/offset")
    region(data, phoff, count * phsize)
    phdrs = []
    for i in range(count):
        values = ph.unpack_from(data, phoff + i * phsize)
        if bits == 32:
            kind, off, va, pa, size, mem, flags, align = values
        else:
            kind, flags, off, va, pa, size, mem, align = values
        content = region(data, off, size)
        if kind == 1 and size > mem:
            raise InspectionError("load segment file size exceeds memory size")
        phdrs.append({"index": i, "type": kind, "flags": flags, "offset": off,
                      "file_size": size, "memory_size": mem,
                      "virtual_address": va, "physical_address": pa,
                      "alignment": align, "sha256": hashlib.sha256(content).hexdigest()})
    hashes = [p for p in phdrs if p["flags"] & HASH_TYPE_MASK == HASH_TYPE]
    if len(hashes) > 1:
        raise InspectionError("multiple Qualcomm hash segments; ambiguous image")
    envelope = None
    if hashes:
        p = hashes[0]
        if p["type"] != 0:
            raise InspectionError("unsupported hash-segment program-header type")
        envelope = mbn_v6(data, p["offset"], p["file_size"], phdrs)
    return {"file_size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "elf_bits": bits, "machine": machine, "elf_type": elf_type,
            "entry": entry, "program_headers": phdrs, "qualcomm_envelope": envelope,
            "limitations": "Structure/hash consistency only; no signature trust, device compatibility or execution claim."}


def inspect_file(path):
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or path.is_symlink() or getattr(before, "st_file_attributes", 0) & 0x400:
        raise InspectionError("input must be an ordinary file, not a link/device/reparse point")
    if before.st_size > MAX_FILE:
        raise InspectionError("input exceeds 32 MiB limit")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino, before.st_size) != (opened.st_dev, opened.st_ino, opened.st_size):
            raise InspectionError("input identity/type changed before read")
        data = stream.read(MAX_FILE + 1)
    after = path.lstat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise InspectionError("input changed during inspection")
    if len(data) != before.st_size:
        raise InspectionError("input length changed during inspection")
    return inspect_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_file(args.image)
    except (InspectionError, OSError) as exc:
        parser.exit(1, f"inspection failed: {exc}\n")
    print(json.dumps(result, indent=2))
    envelope = result["qualcomm_envelope"]
    return int(envelope is not None and envelope["segment_hash_check"] == "mismatch")


if __name__ == "__main__":
    raise SystemExit(main())
