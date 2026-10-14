# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only inspection of the NWWM header profile observed during M2.

This is not a general Sony UPG decoder. Field meanings, authentication and
payload contents remain unverified; see docs/m2-firmware-analysis.md.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


HEADER_SIZE = 128
CHUNK_SIZE = 1024 * 1024


class InspectionError(ValueError):
    """Malformed input or a structure outside the observed profile."""


def read_exact_at(stream, offset, length, file_size):
    """Read a bounded region, rejecting offsets before seeking or allocating."""
    if offset < 0 or length < 0 or length > CHUNK_SIZE:
        raise InspectionError("invalid offset or bounded-read length")
    if offset > file_size or length > file_size - offset:
        raise InspectionError("region exceeds file bounds")
    stream.seek(offset)
    data = stream.read(length)
    if len(data) != length:
        raise InspectionError("truncated region")
    return data


def inspect_header(header, file_size):
    """Validate only the fixed profile, without interpreting payload bytes."""
    if len(header) != HEADER_SIZE or file_size < HEADER_SIZE:
        raise InspectionError("truncated or invalid 128-byte header")
    if header[:4] != b"NWWM":
        raise InspectionError("unsupported container magic")
    if not re.fullmatch(rb"[0-9a-fA-F]{56}", header[4:60]):
        raise InspectionError("invalid 56-character hexadecimal field")
    if header[60:96] != b"0" * 36 or header[108:128] != b"f" * 20:
        raise InspectionError("unsupported reserved-field profile")
    if not re.fullmatch(rb"[0-9]{12}", header[96:108]):
        raise InspectionError("invalid 12-character decimal field")
    decimal = int(header[96:108])
    body_size = file_size - HEADER_SIZE
    difference = body_size - decimal
    if body_size == 0 or body_size % 16:
        raise InspectionError("body length is outside the observed block profile")
    if decimal == 0 or not 1 <= difference <= 16:
        raise InspectionError("decimal field and body length are inconsistent")
    return {
        "profile": "m2-observed-nwwm-128",
        "file_size": file_size,
        "header_size": HEADER_SIZE,
        "magic": "NWWM",
        "hex_field_4_60": header[4:60].decode("ascii"),
        "decimal_field_96_108": decimal,
        "body_offset": HEADER_SIZE,
        "body_size": body_size,
        "body_minus_decimal": difference,
        "payload_status": "opaque; no images decoded",
        "authentication_status": "not verified",
    }


def inspect_file(path, hash_contents=False):
    path = Path(path)
    original = path.lstat()
    if not stat.S_ISREG(original.st_mode):
        raise InspectionError("input must be a regular, non-symlink file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise InspectionError("input must be a regular file")
        if (original.st_dev, original.st_ino) != (before.st_dev, before.st_ino):
            raise InspectionError("input replaced before opening")
        result = inspect_header(
            read_exact_at(stream, 0, HEADER_SIZE, before.st_size), before.st_size
        )
        if hash_contents:
            sha256 = hashlib.sha256()
            md5 = hashlib.md5(usedforsecurity=False)
            stream.seek(0)
            remaining = before.st_size
            while remaining:
                chunk = stream.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    raise InspectionError("input truncated while hashing")
                sha256.update(chunk)
                md5.update(chunk)
                remaining -= len(chunk)
            if stream.read(1):
                raise InspectionError("input grew while hashing")
            result["sha256"] = sha256.hexdigest()
            result["md5"] = md5.hexdigest()
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns) != (
            after.st_size, after.st_mtime_ns
        ):
            raise InspectionError("input changed during inspection")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--hash", action="store_true", help="stream full-file SHA-256 and MD5"
    )
    args = parser.parse_args()
    try:
        result = inspect_file(args.input, args.hash)
    except (OSError, InspectionError) as exc:
        print(f"inspection failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
