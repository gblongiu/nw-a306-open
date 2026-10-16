# SPDX-License-Identifier: GPL-2.0-or-later
"""Inspect a supplied GPT fragment; never opens a device or applies XML patches.

Offsets are explicit: a factory template and a physical capture are different
inputs. CRC agreement alone is not a valid disk layout or restoration proof.
Format: UEFI GPT header/entry specification, not a Sony partition assumption.
"""

import argparse
import hashlib
import json
from pathlib import Path
import stat
import struct
import zlib

MAX_CAPTURE = 8 * 1024 * 1024
HEADER = struct.Struct("<8sIIIIQQQQ16sQIII")


class InspectionError(ValueError):
    pass


def region(data, start, size):
    if start < 0 or size < 0 or start > len(data) or size > len(data) - start:
        raise InspectionError("region exceeds capture bounds")
    return data[start:start + size]


def inspect_bytes(data, header_offset, array_offset, sector_size=512, capture_start_lba=None):
    if len(data) > MAX_CAPTURE or sector_size not in (512, 4096):
        raise InspectionError("unsupported capture size or sector size")
    fields = HEADER.unpack(region(data, header_offset, HEADER.size))
    magic, revision, size, crc, reserved, current, alternate, first, last, _, entries_lba, count, stride, array_crc = fields
    if magic != b"EFI PART" or revision != 0x10000 or not HEADER.size <= size <= sector_size:
        raise InspectionError("unsupported GPT header")
    if not 1 <= count <= 4096 or stride not in (128, 256, 512, 1024):
        raise InspectionError("unsupported or excessive entry array")
    header = bytearray(region(data, header_offset, size))
    header[16:20] = bytes(4)
    array = region(data, array_offset, count * stride)
    problems = []
    if reserved:
        problems.append("nonzero reserved header field")
    if current == alternate or not current or not alternate:
        problems.append("invalid current/alternate header locations")
    if min(current, alternate) != 1:
        problems.append("neither header is at primary LBA 1")
    if not first or first > last:
        problems.append("invalid usable-LBA interval")
    disk_end = max(current, alternate)
    if first < 2 or last >= disk_end:
        problems.append("usable interval exceeds header-defined disk extent")
    if first <= current <= last or first <= alternate <= last:
        problems.append("header inside usable interval")
    array_sectors = (len(array) + sector_size - 1) // sector_size
    if not entries_lba or not (entries_lba + array_sectors - 1 < first or entries_lba > last):
        problems.append("invalid entry-array location")
    if entries_lba + array_sectors - 1 > disk_end:
        problems.append("entry array exceeds header-defined disk extent")
    if any(entries_lba <= location < entries_lba + array_sectors
           for location in (current, alternate)):
        problems.append("entry array overlaps a GPT header")
    if capture_start_lba is not None:
        if capture_start_lba < 0 or header_offset % sector_size or array_offset % sector_size:
            raise InspectionError("invalid capture origin/alignment")
        if current != capture_start_lba + header_offset // sector_size:
            problems.append("header LBA does not match capture origin")
        if entries_lba != capture_start_lba + array_offset // sector_size:
            problems.append("array LBA does not match capture origin")
    entries = []
    for index in range(count):
        raw = array[index * stride:(index + 1) * stride]
        if not any(raw[:16]):
            continue
        start, end, attributes = struct.unpack_from("<QQQ", raw, 32)
        try:
            name = raw[56:128].decode("utf-16le").split("\0", 1)[0]
        except UnicodeDecodeError as exc:
            raise InspectionError("invalid UTF-16 partition name") from exc
        if start > end:
            problems.append(f"entry {index}: inverted/empty LBA interval")
        elif start < first or end > last:
            problems.append(f"entry {index}: outside usable interval")
        entries.append({"index": index, "name": name, "first_lba": start,
                        "last_lba": end, "attributes": attributes})
    ordered = sorted((e for e in entries if e["first_lba"] <= e["last_lba"]), key=lambda e: e["first_lba"])
    furthest = None
    for entry in ordered:
        if furthest is not None and entry["first_lba"] <= furthest:
            problems.append(f"entry {entry['index']}: overlapping partition interval")
        furthest = max(furthest or 0, entry["last_lba"])
    checks = {"header_crc_matches": zlib.crc32(header) == crc,
              "array_crc_matches": zlib.crc32(array) == array_crc,
              "geometry_consistent": not problems}
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "sector_size": sector_size, "current_lba": current, "alternate_lba": alternate,
            "first_usable_lba": first, "last_usable_lba": last,
            "entry_array_lba": entries_lba, "entry_count": count, "entry_size": stride,
            "checks": checks, "problems": problems, "partitions": entries,
            "capture_origin_checked": capture_start_lba is not None,
            "restoration_capability": "not_established"}


def inspect_file(path, **kwargs):
    p = Path(path)
    before = p.lstat()
    if not stat.S_ISREG(before.st_mode) or p.is_symlink() or getattr(before, "st_file_attributes", 0) & 0x400:
        raise InspectionError("capture must be an ordinary file")
    if before.st_size > MAX_CAPTURE:
        raise InspectionError("capture exceeds 8 MiB limit")
    with p.open("rb") as stream:
        import os
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino, opened.st_size) != (before.st_dev, before.st_ino, before.st_size):
            raise InspectionError("capture identity changed before read")
        data = stream.read(MAX_CAPTURE + 1)
    after = p.lstat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns) or len(data) != before.st_size:
        raise InspectionError("capture changed during read")
    return inspect_bytes(data, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--header-offset", type=int, required=True)
    parser.add_argument("--array-offset", type=int, required=True)
    parser.add_argument("--sector-size", type=int, choices=(512, 4096), default=512)
    parser.add_argument("--capture-start-lba", type=int)
    args = vars(parser.parse_args())
    path = args.pop("capture")
    try:
        result = inspect_file(path, **args)
    except (InspectionError, OSError) as exc:
        parser.exit(1, f"inspection failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return int(not all(result["checks"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
