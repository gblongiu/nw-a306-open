# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed C1 cache inode metadata. No contents, alternate paths or mode changes."""

from datetime import datetime
import re

import characterization_plan as cp

PARENT = "/mnt/icx_cache"
TARGET = PARENT + "/NW_WM_FW.zip"
EVIDENCE = (
    cp.Operation("cache-parent-metadata", "/system/bin/toybox ls -ldZ " + PARENT),
    cp.Operation("cache-zip-metadata", "/system/bin/toybox ls -ldZ " + TARGET),
)
OPERATIONS = cp.IDENTITY + EVIDENCE + cp.OPERATIONS[-len(cp.IDENTITY):]
OUTPUT_CAP = 196608

# AOSP Android 14 toybox ls.c:473-519: mode, links, owner, group, label,
# decimal size, long-ISO date/time, literal name. Unsupported output stops.
MODE = re.compile(r"[d-][r-][w-][xSs-][r-][w-][xSs-][r-][w-][xTt-]")
NAME = re.compile(r"[A-Za-z0-9_.-]{1,64}")
LABEL = re.compile(r"[A-Za-z0-9_]+:[A-Za-z0-9_]+:[A-Za-z0-9_]+:s[0-9]+(?:[-:,A-Za-z0-9_.]+)?")
NUMBER = re.compile(r"(?:0|[1-9][0-9]{0,18})")


def metadata(operation, data):
    if operation not in EVIDENCE or not 0 < len(data) <= operation.cap:
        raise cp.Refusal("C1 metadata scope or size mismatch")
    if not data.endswith(b"\n") or data.count(b"\n") != 1 or any(c < 32 for c in data[:-1]):
        raise cp.Refusal("ambiguous C1 metadata line")
    try:
        text = data[:-1].decode("ascii")
    except UnicodeError as exc:
        raise cp.Refusal("unsupported C1 metadata encoding") from exc
    fields = text.split()
    if len(fields) != 9:
        raise cp.Refusal("unsupported C1 metadata format")
    mode, links, owner, group, label, size, date, clock, path = fields
    expected_path = PARENT if operation == EVIDENCE[0] else TARGET
    expected_type = "d" if operation == EVIDENCE[0] else "-"
    if path != expected_path or not MODE.fullmatch(mode) or mode[0] != expected_type:
        raise cp.Refusal("unexpected C1 object type or path")
    if (not NUMBER.fullmatch(links) or not 0 < int(links) <= 2**63-1
            or not NUMBER.fullmatch(size) or int(size) > 2**63-1
            or not NAME.fullmatch(owner) or not NAME.fullmatch(group)
            or not LABEL.fullmatch(label)):
        raise cp.Refusal("unsupported C1 metadata fields")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", clock):
        raise cp.Refusal("unsupported C1 metadata timestamp")
    try:
        datetime.strptime(date + " " + clock, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise cp.Refusal("invalid C1 metadata timestamp") from exc
    if operation == EVIDENCE[1] and int(size) == 0:
        raise cp.Refusal("empty C1 OTA candidate")
    return {"path": path, "mode": mode, "links": int(links), "owner": owner,
            "group": group, "selinux_label": label, "bytes": int(size),
            "mtime_display": date + " " + clock,
            "content_read": False, "read_access_established": False}


def validate(operation, data, profile):
    if operation in EVIDENCE:
        metadata(operation, data)
    else:
        if operation not in OPERATIONS:
            raise cp.Refusal("operation outside C1")
        cp.validate(operation, data, profile)
