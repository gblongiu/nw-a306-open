# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate/evaluate the M9 minimum-userspace dependency contract on the host.

States are externally asserted or synthetic, never device observations collected
by this tool. A ready model proves no boot acceptance, safe mute, calibration or
recovery. No subprocess, device I/O, service control or firmware-writing support.
"""

import argparse
import json
import os
from pathlib import Path
import stat
import sys


ROLES = frozenset((
    "handoff", "board", "early_protection", "bootstrap", "storage",
    "firmware_delivery", "modules", "peripherals", "display_input",
    "audio_muted", "protection", "watchdog", "rockbox",
))
MAX_BYTES = 65536


class ContractError(ValueError):
    """Unsupported, incomplete or inconsistent contract/input."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ContractError("nonstandard JSON constant: " + value)


def read_json(path):
    """Bounded read of an existing regular host file; no device acquisition."""
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_BYTES:
        raise ContractError("expected a non-symlink regular JSON file, 1..65536 bytes")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or not 0 < opened.st_size <= MAX_BYTES:
            raise ContractError("input replaced or not a bounded regular file")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ContractError("input replaced before opening")
        data = stream.read(MAX_BYTES + 1)
        after = os.fstat(stream.fileno())
    if len(data) > MAX_BYTES or (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ContractError("input changed or exceeded bounds")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except ContractError:
        raise
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid bounded UTF-8 JSON") from exc


def validate(spec):
    if not isinstance(spec, dict) or set(spec) != {"version", "context", "nodes"}:
        raise ContractError("unsupported contract fields")
    if type(spec["version"]) is not int or spec["version"] != 1 or spec["context"] != "unselected-source-contract":
        raise ContractError("unsupported contract version or applicability")
    nodes = spec["nodes"]
    if not isinstance(nodes, list) or len(nodes) != len(ROLES):
        raise ContractError("all minimum roles must be represented exactly once")
    graph = {}
    for node in nodes:
        if not isinstance(node, dict) or set(node) != {"id", "requires", "basis", "source"}:
            raise ContractError("unsupported node fields")
        name = node["id"]
        if not isinstance(name, str) or name not in ROLES or name in graph:
            raise ContractError("unknown or duplicate role")
        deps = node["requires"]
        if not isinstance(deps, list) or len(deps) > len(ROLES):
            raise ContractError("invalid dependency list")
        if any(not isinstance(dep, str) or dep not in ROLES for dep in deps):
            raise ContractError("unknown dependency")
        if len(deps) != len(set(deps)) or name in deps:
            raise ContractError("duplicate dependency or self-dependency")
        if node["basis"] not in ("requirement", "published-source"):
            raise ContractError("unsupported evidence classification")
        if not isinstance(node["source"], str) or not 1 <= len(node["source"].strip()) <= 512:
            raise ContractError("bounded source locator required")
        graph[name] = set(deps)
    order = []
    remaining = set(graph)
    while remaining:
        available = sorted(name for name in remaining if graph[name] <= set(order))
        if not available:
            raise ContractError("dependency cycle")
        order.extend(available)
        remaining.difference_update(available)
    ancestors = {}
    for name in order:
        ancestors[name] = set(graph[name])
        for dep in graph[name]:
            ancestors[name].update(ancestors[dep])
    if ancestors["rockbox"] != ROLES - {"rockbox"}:
        raise ContractError("Rockbox startup bypasses a minimum role")
    # These ordering invariants resolve concrete init/firmware/safety hazards.
    for before, after in (("handoff", "board"), ("board", "early_protection"),
                          ("early_protection", "bootstrap"), ("bootstrap", "storage"),
                          ("storage", "firmware_delivery"), ("firmware_delivery", "modules"),
                          ("modules", "peripherals"), ("protection", "watchdog")):
        if before not in ancestors[after]:
            raise ContractError("required startup precedence missing")
    return graph, order


def evaluate(spec, states):
    graph, order = validate(spec)
    if not isinstance(states, dict) or any(name not in graph for name in states):
        raise ContractError("unknown state role")
    if any(type(value) is not str or value not in ("ready", "missing", "failed") for value in states.values()):
        raise ContractError("states must be ready, missing or failed")
    ready = set()
    blocked = {}
    for name in order:
        reasons = []
        if states.get(name, "missing") != "ready":
            reasons.append("state:" + states.get(name, "missing"))
        reasons.extend("requires:" + dep for dep in sorted(graph[name] - ready))
        if reasons:
            blocked[name] = reasons
        else:
            ready.add(name)
    return {
        "startup_order": order,
        "ready": sorted(ready),
        "blocked": blocked,
        "rockbox_may_start_in_model": "rockbox" in ready,
        "deployment_authorized": False,
        "on_loss": ["request_verified_mute", "stop_application", "quiesce_peripherals",
                    "release_display_input", "synchronize_owned_storage", "request_reviewed_poweroff"],
        "limits": "Model only: keep protection/watchdog ownership until verified shutdown; no action is executed, and successful muting or poweroff is not established.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--states", type=Path, help="existing host JSON, synthetic or externally reviewed states")
    args = parser.parse_args()
    try:
        result = evaluate(read_json(args.contract), read_json(args.states) if args.states else {})
    except (OSError, ContractError) as exc:
        print(f"contract failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["rockbox_may_start_in_model"] else 1


if __name__ == "__main__":
    sys.exit(main())
