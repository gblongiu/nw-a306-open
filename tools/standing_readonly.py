# SPDX-License-Identifier: GPL-2.0-or-later
"""Exact U1/H1 scope, payload validation and append-only standing admission.

No connector or command executor. The existing adapter supplies acquisition.
An exclusive lease prevents concurrent sessions and unfinished attempts block
admission. Grant files record human consent; they do not establish it themselves.
"""

from pathlib import Path
import re

import characterization_plan as cp
import characterization_transport as ct

POLICY = Path(__file__).resolve().parents[1] / "docs/m10-readonly-standing-authorization.md"
POLICY_SHA256 = "4ebcc03041fcf1987eec2a0321848ce3937d86908372974595c0051cc629776a"
UPDATER = cp.Operation("updater-path", "/system/bin/pm path --user 0 com.sony.walkman.systemupdater", 16384)
U1 = cp.IDENTITY + (UPDATER,) + cp.OPERATIONS[-len(cp.IDENTITY):]
H1 = cp.IDENTITY + tuple(ct.REGISTRY[k] for k in
     ("sound-cards", "sound-pcm", "input-devices", "graphics-names", "power-names", "block-names")) + cp.OPERATIONS[-len(cp.IDENTITY):]


def operations(stage):
    if stage == "U1": return U1
    if stage == "H1": return H1
    raise cp.Refusal("unknown standing plan")


def validate(operation, data, profile):
    if operation.id != "updater-path":
        cp.validate(operation, data, profile)
        return
    if not data or len(data) > operation.cap or not data.endswith(b"\n"):
        raise cp.Refusal("invalid package-path output")
    lines = data[:-1].split(b"\n")
    if len(lines) > 128 or len(lines) != len(set(lines)):
        raise cp.Refusal("invalid package-path list")
    for line in lines:
        if not re.fullmatch(rb"package:/[A-Za-z0-9._+@=/~-]+\.apk", line):
            raise cp.Refusal("invalid package path")
        if any(part in (b"", b".", b"..") for part in line.removeprefix(b"package:/").split(b"/")):
            raise cp.Refusal("noncanonical package path")


def authorized_run(grant, turn_id, stage, policy, profile, output, acquire):
    """Validate fixed scope, reserve once, acquire, then journal the outcome.

Admission errors never acquire. Any acquisition failure consumes the turn and
quarantines the failed operation. A crash leaves an unmatched reservation and
requires review. No stale lock removal, retry, reset or quarantine clearing API.
"""
    cp.exact_keys(grant, ("approved", "version", "policy_sha256", "profile_sha256", "plans", "state_directory"))
    cp.exact_keys(grant["plans"], ("U1", "H1"))
    cp.expected_profile(profile)
    if (grant["approved"] is not True or type(grant["version"]) is not int or grant["version"] != 1
            or grant["policy_sha256"] != POLICY_SHA256 or cp.sha(POLICY.read_bytes()) != POLICY_SHA256
            or grant["profile_sha256"] != cp.sha(cp.canonical(profile))
            or grant["plans"].get(stage) != cp.sha(cp.canonical(policy))
            or policy["operations"] != [ct.asdict(o) for o in operations(stage)]
            or not isinstance(turn_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", turn_id)):
        raise cp.Refusal("standing grant scope mismatch")
    state = Path(grant["state_directory"])
    if (not state.is_absolute() or not state.is_dir() or not state.resolve().is_relative_to(cp.PRIVATE_ROOT.resolve())
            or state.resolve() == cp.PRIVATE_ROOT.resolve()
            or any(p.is_symlink() or getattr(p, "is_junction", lambda: False)() for p in (state, *state.parents))):
        raise cp.Refusal("invalid standing state directory")
    lock = state / "session.lock"
    with lock.open("x", encoding="ascii") as stream: stream.write(turn_id)
    try:
        files = sorted(state.glob("*.json"))
        records, previous = [], None
        grant_sha = cp.sha(cp.canonical(grant))
        for i, path in enumerate(files):
            if path.name != f"{i:04d}.json": raise cp.Refusal("standing journal gap")
            record = cp.load_json(path)
            keys = ("kind", "turn", "stage", "output", "grant_sha256", "previous_sha256")
            cp.exact_keys(record, keys if i % 2 == 0 else keys + ("complete", "stop", "failed_operation", "manifest_sha256"))
            if (record["previous_sha256"] != previous or record["grant_sha256"] != grant_sha
                    or record["kind"] != ("start" if i % 2 == 0 else "result")
                    or record["stage"] not in ("U1", "H1")):
                raise cp.Refusal("standing journal integrity mismatch")
            if i % 2:
                if (any(record[k] != records[-1][k] for k in ("turn", "stage", "output"))
                        or type(record["complete"]) is not bool):
                    raise cp.Refusal("standing result mismatch")
                recorded_output = Path(record["output"])
                if not recorded_output.is_absolute() or not recorded_output.resolve().is_relative_to(cp.PRIVATE_ROOT.resolve()):
                    raise cp.Refusal("standing evidence path mismatch")
                if record["manifest_sha256"] is not None:
                    manifest = recorded_output / "manifest.json"
                    if not manifest.is_file() or cp.sha(manifest.read_bytes()) != record["manifest_sha256"]:
                        raise cp.Refusal("standing evidence integrity mismatch")
            records.append(record)
            previous = cp.sha(cp.canonical(record))
        if len(records) % 2: raise cp.Refusal("unfinished standing attempt requires review")
        results = records[1::2]
        current = [r for r in results if r["turn"] == turn_id]
        if any(not r["complete"] for r in current): raise cp.Refusal("standing turn stopped")
        if len(current) >= 2 or any(r["stage"] == stage for r in current):
            raise cp.Refusal("standing turn session limit")
        quarantined = {"compatible", "partitions"} | {r["failed_operation"] for r in results if not r["complete"]}
        if any(o.id in quarantined for o in operations(stage)):
            raise cp.Refusal("standing operation quarantined")
        reservation = {"kind": "start", "turn": turn_id, "stage": stage, "output": str(Path(output).absolute()),
                       "grant_sha256": grant_sha, "previous_sha256": previous}
        def append(index, record):
            with (state / f"{index:04d}.json").open("x", encoding="utf-8") as stream:
                stream.write(cp.canonical(record).decode() + "\n")
        append(len(records), reservation)
        result = {"complete": False, "stop": "acquisition_exception", "observations": []}
        try:
            result = acquire()
            return result
        finally:
            observations = result.get("observations", [])
            failed = observations[-1]["id"] if observations and not result["complete"] else None
            manifest = Path(output) / "manifest.json"
            finished = {**reservation, "kind": "result", "previous_sha256": cp.sha(cp.canonical(reservation)),
                        "complete": result["complete"], "stop": result["stop"], "failed_operation": failed,
                        "manifest_sha256": cp.sha(manifest.read_bytes()) if manifest.is_file() else None}
            append(len(records) + 1, finished)
    finally:
        lock.unlink()
