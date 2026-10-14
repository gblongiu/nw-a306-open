# SPDX-License-Identifier: GPL-2.0-or-later
"""Inspect an existing 512-byte eMMC 5.1 EXT_CSD file, never a device.

Partial storage/boot metadata reader, not a complete EXT_CSD validator or a
Sony configuration detector. Register provenance and limits:
docs/m8-boot-storage-architecture.md. No ioctl, acquisition or writing support.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


class InspectionError(ValueError):
    """Unsupported or inconsistent metadata."""


def inspect(data):
    """Decode only the supported fields from a complete revision-8 register."""
    if len(data) != 512:
        raise InspectionError("EXT_CSD input must be exactly 512 bytes")
    if data[192] != 8:
        raise InspectionError("only EXT_CSD revision 8 (eMMC 5.1) is supported")
    config = data[179]
    enabled = (config >> 3) & 7
    if config & 0x80 or enabled not in (0, 1, 2, 7):
        raise InspectionError("reserved PARTITION_CONFIG boot selection")
    sectors = int.from_bytes(data[212:216], "little")
    if not sectors:
        raise InspectionError("zero sector count is outside this profile")
    boot_bytes = data[226] * 128 * 1024
    rpmb_bytes = data[168] * 128 * 1024
    access = config & 7
    if (enabled in (1, 2) or access in (1, 2)) and not boot_bytes:
        raise InspectionError("selected boot region has zero advertised capacity")
    if access == 3 and not rpmb_bytes:
        raise InspectionError("selected RPMB has zero advertised capacity")
    area_names = ("user", "boot1", "boot2", "rpmb", "gp1", "gp2", "gp3", "gp4")
    offsets = {
        "PARTITION_SETTING_COMPLETED": 155,
        "PARTITION_SUPPORT": 160,
        "WR_REL_PARAM": 166,
        "WR_REL_SET": 167,
        "RPMB_SIZE_MULT": 168,
        "USER_WP": 171,
        "BOOT_WP": 173,
        "BOOT_WP_STATUS": 174,
        "BOOT_CONFIG_PROT": 178,
        "PARTITION_CONFIG": 179,
        "BOOT_BUS_CONDITIONS": 177,
        "BOOT_SIZE_MULT": 226,
        "BOOT_INFO": 228,
        "REL_WR_SEC_C": 222,
    }
    return {
        "profile": "partial-extcsd-rev8",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "ext_csd_revision": 8,
        "user_sector_count_512": sectors,
        "user_capacity_bytes": sectors * 512,
        "each_boot_region_bytes": boot_bytes,
        "rpmb_region_bytes": rpmb_bytes,
        "emmc_boot_selection": {0: "disabled", 1: "boot1", 2: "boot2", 7: "user"}[enabled],
        "boot_ack_requested": bool(config & 0x40),
        "partition_access": area_names[access],
        "boot_write_protection_status": [
            {
                "region": area_names[i + 1],
                "power_on": bool(data[174] & (1 << (2 * i))),
                "permanent": bool(data[174] & (2 << (2 * i))),
            }
            for i in range(2)
        ],
        "raw_registers": {
            name: {"offset": offset, "value": data[offset]}
            for name, offset in offsets.items()
        },
        "limits": (
            "Partial register interpretation only; no Sony identity, ROM boot-source, "
            "GPT, Android slot, image authentication, RPMB provisioning or recovery proof. "
            "GP/enhanced layout and write-protection groups are not decoded."
        ),
    }


def inspect_file(path):
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size != 512:
        raise InspectionError("input must be a regular, non-symlink 512-byte file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_size != 512:
            raise InspectionError("input changed or is not a regular file")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise InspectionError("input replaced before opening")
        data = stream.read(513)
        after = os.fstat(stream.fileno())
        if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise InspectionError("input changed while reading")
    return inspect(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_file(args.input)
    except (OSError, InspectionError) as exc:
        print(f"inspection failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
