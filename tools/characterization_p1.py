# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed P1 inode metadata only. Never open partitions or discover new commands."""
from datetime import datetime
import json
import re

import characterization_plan as cp
import characterization_c1 as c1

PARENT = '/dev/block/by-name'
EVIDENCE = (
    cp.Operation('block-directory', '/system/bin/toybox ls -ldZ ' + PARENT),
    cp.Operation('block-node-metadata', '/system/bin/toybox ls -lZL ' + PARENT, 65536),
)
OPERATIONS = cp.IDENTITY + EVIDENCE + cp.OPERATIONS[-len(cp.IDENTITY):]
OUTPUT_CAP = 319488
BLOCK_MODE = re.compile(r'b[r-][w-][xSs-][r-][w-][xSs-][r-][w-][xTt-]')


def current_profile(original, binding, attributes):
    """Only P1 may resolve a fresh ID once. The original identity stays immutable.

    Caller must obtain one online inventory and confirm USB selection, then use
    same-connection serial/ID checks and original identities before metadata.
    This function neither contacts a server nor authorizes later rebinding.
    """
    cp.expected_profile(original)
    current = json.loads(cp.canonical(original))
    current['binding']['transport_id'] = binding.get('transport_id')
    cp.expected_profile(current)  # Includes nonzero, bounded transport-ID syntax.
    if (current['binding'] != binding
            or attributes.get('device') != original['identity']['ro.product.device']):
        raise cp.Refusal('P1 current target differs from original approved device')
    return current


def number(value, maximum=2**63 - 1):
    if not c1.NUMBER.fullmatch(value) or int(value) > maximum:
        raise cp.Refusal('invalid P1 numeric field')
    return int(value)


def common(mode, links, owner, group, label, date, clock):
    if (number(links) == 0 or not c1.NAME.fullmatch(owner)
            or not c1.NAME.fullmatch(group) or not c1.LABEL.fullmatch(label)):
        raise cp.Refusal('unsupported P1 metadata fields')
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date) or not re.fullmatch(r'[0-9]{2}:[0-9]{2}', clock):
        raise cp.Refusal('unsupported P1 timestamp')
    try:
        datetime.strptime(date + ' ' + clock, '%Y-%m-%d %H:%M')
    except ValueError as exc:
        raise cp.Refusal('invalid P1 timestamp') from exc
    return dict(mode=mode, links=int(links), owner=owner, group=group,
                selinux_label=label, mtime_display=date + ' ' + clock,
                content_read=False, read_access_established=False)


def metadata(operation, data):
    if operation not in EVIDENCE or not 0 < len(data) <= operation.cap:
        raise cp.Refusal('P1 metadata scope or size mismatch')
    if not data.endswith(b'\n') or any(x < 32 and x != 10 for x in data) or b'\x7f' in data:
        raise cp.Refusal('ambiguous P1 metadata')
    try:
        lines = data[:-1].decode('ascii').split('\n')
    except UnicodeError as exc:
        raise cp.Refusal('unsupported P1 encoding') from exc
    if operation == EVIDENCE[0]:
        fields = lines[0].split()
        if len(lines) != 1 or len(fields) != 9:
            raise cp.Refusal('unsupported P1 directory format')
        mode, links, owner, group, label, size, date, clock, path = fields
        if path != PARENT or not c1.MODE.fullmatch(mode) or mode[0] != 'd':
            raise cp.Refusal('P1 requires the exact ordinary directory; no symlink')
        result = common(mode, links, owner, group, label, date, clock)
        result.update(path=path, bytes=number(size))
        return result
    # Android toybox long directory listings include a block-count header.
    if not re.fullmatch(r'total (?:0|[1-9][0-9]{0,18})', lines[0]) or len(lines) < 2:
        raise cp.Refusal('unsupported or empty P1 inventory')
    number(lines[0].split()[1])
    nodes, names = [], set()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) != 10:
            raise cp.Refusal('unsupported P1 node format')
        mode, links, owner, group, label, major, minor, date, clock, name = fields
        if (not BLOCK_MODE.fullmatch(mode) or not major.endswith(',')
                or not c1.NAME.fullmatch(name) or name in ('.', '..') or name in names):
            raise cp.Refusal('unexpected P1 node type, name or duplicate')
        result = common(mode, links, owner, group, label, date, clock)
        result.update(name=name, major=number(major[:-1], 2**32-1), minor=number(minor, 2**32-1))
        nodes.append(result)
        names.add(name)
    return nodes


def validate(operation, data, profile):
    if operation in EVIDENCE:
        metadata(operation, data)
    else:
        if operation not in OPERATIONS:
            raise cp.Refusal('operation outside P1')
        cp.validate(operation, data, profile)
