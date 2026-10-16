# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed first-pass characterization plan and OFFLINE replay. No ADB backend.

Replay exercises admission, stream bounds and provenance, not Sony access or
ADB wire behavior. A future live transport needs separate review and approval.
"""

import argparse
import base64
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time


class Refusal(ValueError):
    pass


@dataclass(frozen=True)
class Operation:
    id: str
    remote: str
    cap: int = 4096
    timeout_ms: int = 5000


PROPERTIES = (
    "ro.product.model", "ro.product.device", "ro.board.platform", "ro.soc.model",
    "ro.build.version.incremental", "ro.boot.slot_suffix",
    "ro.boot.verifiedbootstate", "ro.boot.flash.locked",
)
IDENTITY = (
    Operation("uid", "/system/bin/id -u"),
    Operation("context", "/system/bin/id -Z"),
    Operation("selinux", "/system/bin/getenforce"),
) + tuple(Operation(p, "/system/bin/getprop " + p) for p in PROPERTIES)
EVIDENCE = (
    Operation("kernel", "/system/bin/uname -r"),
    Operation("tree-link", "/system/bin/readlink /proc/device-tree"),
    Operation("compatible", "/system/bin/toybox head -c 4097 /proc/device-tree/compatible"),
    Operation("model", "/system/bin/toybox head -c 4097 /proc/device-tree/model"),
    Operation("updater-candidates", "/system/bin/pm list packages --user 0 -s systemupdat", 16384),
    Operation("unlock-report", "/system/bin/getprop ro.oem_unlock_supported"),
    Operation("raw-fdt-mode", "/system/bin/toybox ls -ld /sys/firmware/fdt"),
)
OPERATIONS = IDENTITY + EVIDENCE + tuple(
    Operation("end:" + p.id, p.remote, p.cap, p.timeout_ms) for p in IDENTITY
)
TOTAL_CAP = 2 * 1024 * 1024
SESSION_MS = 300000
PRIVATE_ROOT = Path(__file__).resolve().parents[1] / "build" / "m10"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def plan():
    return {
        "mode": "offline-only", "live_backend": False,
        "operations": [asdict(o) for o in OPERATIONS],
        "stdout_and_stderr_cap_each": True,
        "total_cap": TOTAL_CAP, "session_ms": SESSION_MS,
        "adb_requirements": ["explicit reviewed transport", "shell-v2 required",
                             "shell -n -T", "no -x", "no host shell", "no retries"],
    }


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise Refusal("unexpected or missing fields")


def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Refusal("duplicate JSON key")
            result[key] = value
        return result

    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise Refusal("input must be an ordinary file")
    with path.open("rb") as stream:
        data = stream.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise Refusal("input size limit")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite JSON")))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refusal("invalid JSON input") from exc


def expected_profile(profile):
    exact_keys(profile, ("binding", "identity"))
    exact_keys(profile["binding"], ("serial", "transport_id", "state", "device_count"))
    binding = profile["binding"]
    if (not isinstance(binding["serial"], str) or not 0 < len(binding["serial"]) <= 256
            or not isinstance(binding["transport_id"], str)
            or not re.fullmatch(r"[1-9][0-9]{0,19}", binding["transport_id"])
            or int(binding["transport_id"]) > 2**64 - 1
            or binding["state"] != "device" or type(binding["device_count"]) is not int
            or binding["device_count"] != 1):
        raise Refusal("ambiguous or unavailable transport")
    exact_keys(profile["identity"], (o.id for o in IDENTITY))
    identity = profile["identity"]
    if any(not isinstance(v, str) or not v or len(v) > 4095 or "\n" in v
           or "\r" in v or "\0" in v for v in identity.values()):
        raise Refusal("invalid expected identity")
    required = {"uid": "2000", "context": "u:r:shell:s0", "selinux": "Enforcing",
                "ro.product.device": "icx1301", "ro.board.platform": "bengal",
                "ro.soc.model": "QCS2290", "ro.boot.verifiedbootstate": "green",
                "ro.boot.flash.locked": "1"}
    if any(identity[k] != v for k, v in required.items()):
        raise Refusal("profile is outside the normal locked Sony shell scope")


def string_list(data):
    """DT strings are NUL terminated; retain original bytes separately."""
    if not data or not data.endswith(b"\0"):
        raise Refusal("unterminated DT string property")
    try:
        values = data[:-1].decode("utf-8").split("\0")
    except UnicodeError as exc:
        raise Refusal("invalid DT string encoding") from exc
    if any(not v or any(ord(c) < 32 or ord(c) == 127 for c in v) for v in values):
        raise Refusal("invalid DT string value")
    return values


def validate(operation, data, profile):
    key = operation.id.removeprefix("end:")
    if key in profile["identity"]:
        if data != (profile["identity"][key] + "\n").encode():
            raise Refusal("identity mismatch: " + key)
    elif key == "tree-link":
        if data != b"/sys/firmware/devicetree/base\n":
            raise Refusal("unreviewed live-tree alias")
    elif key in ("compatible", "model"):
        values = string_list(data)
        if key == "model" and len(values) != 1:
            raise Refusal("model must be one DT string")
    elif key == "updater-candidates":
        if any(not re.fullmatch(rb"package:[A-Za-z0-9_.]*systemupdat[A-Za-z0-9_.]*", line)
               for line in data.splitlines()):
            raise Refusal("unexpected package-query output")
    elif key == "unlock-report":
        if data not in (b"\n", b"0\n", b"1\n"):
            raise Refusal("unexpected unlock property")
    elif not data or b"\0" in data:
        raise Refusal("unexpected metadata output")


def private_directory(output):
    """Keep all raw replay inputs/results in the repository's ignored build area."""
    output = Path(output).absolute()
    if any(p.is_symlink() or getattr(p, "is_junction", lambda: False)()
           for p in (output, *output.parents)):
        raise Refusal("output has a symlink component")
    output = output.resolve()
    if not output.is_relative_to(PRIVATE_ROOT) or output == PRIVATE_ROOT:
        raise Refusal("output must be a new directory under build/m10")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)
    return output


def replay(fixture, profile, output):
    """Replay timestamped synthetic stream events; never execute remote strings.

    Missing exit, transport replacement, cap/timeout or validation failure stops
    the sequence. Fixture elapsed times model deadlines; no real I/O watchdog
    or ADB transport behavior is claimed by these tests.
    """
    expected_profile(profile)
    exact_keys(fixture, ("synthetic", "plan_sha256", "responses"))
    digest = sha(canonical(plan()))
    if fixture["synthetic"] is not True or fixture["plan_sha256"] != digest:
        raise Refusal("only synthetic fixtures for the exact plan are admitted")
    if not isinstance(fixture["responses"], list) or len(fixture["responses"]) > len(OPERATIONS):
        raise Refusal("invalid response count")
    output = private_directory(output)
    manifest = {"mode": "offline-replay", "physical_evidence": False,
                "plan_sha256": digest, "tool_sha256": sha(Path(__file__).read_bytes()),
                "fixture_sha256": sha(canonical(fixture)),
                "profile_sha256": sha(canonical(profile)), "binding": profile["binding"],
                "utc": datetime.now(timezone.utc).isoformat(),
                "monotonic_start": time.monotonic(), "records": [],
                "complete": False, "stop": None}
    total = elapsed = 0
    try:
        for number, op in enumerate(OPERATIONS):
            record = {"operation": asdict(op), "complete": False, "exit": None,
                      "stdout_bytes": 0, "stderr_bytes": 0}
            manifest["records"].append(record)
            streams = {s: bytearray() for s in ("stdout", "stderr")}
            try:
                if number >= len(fixture["responses"]):
                    raise Refusal("missing response")
                response = fixture["responses"][number]
                exact_keys(response, ("id", "binding", "events", "exit", "elapsed_ms"))
                if response["id"] != op.id or response["binding"] != profile["binding"]:
                    raise Refusal("command order or transport continuity mismatch")
                if not isinstance(response["events"], list) or len(response["events"]) > 4096:
                    raise Refusal("invalid stream events")
                previous = 0
                for event in response["events"]:
                    exact_keys(event, ("stream", "base64", "at_ms"))
                    at = event["at_ms"]
                    if type(at) is not int or not previous <= at <= op.timeout_ms:
                        raise Refusal("event deadline or ordering violation")
                    previous = at
                    name = event["stream"]
                    if not isinstance(name, str) or name not in streams or not isinstance(event["base64"], str):
                        raise Refusal("invalid stream")
                    # Bound encoded chunks before decoding and preserve at most cap+1.
                    if len(event["base64"]) > 4 * ((op.cap + 3) // 3):
                        raise Refusal("encoded chunk size limit")
                    try:
                        chunk = base64.b64decode(event["base64"], validate=True)
                    except ValueError as exc:
                        raise Refusal("invalid base64 stream") from exc
                    room = op.cap + 1 - len(streams[name])
                    streams[name].extend(chunk[:room])
                    total += len(chunk)
                    if len(streams[name]) > op.cap or len(chunk) > room or total > TOTAL_CAP:
                        raise Refusal("output byte limit")
                duration = response["elapsed_ms"]
                if type(duration) is not int or not previous <= duration <= op.timeout_ms:
                    raise Refusal("command timeout or invalid duration")
                elapsed += duration
                record["elapsed_ms"] = duration
                if elapsed > SESSION_MS:
                    raise Refusal("session deadline")
                record["exit"] = response["exit"]
                if type(response["exit"]) is not int or response["exit"] != 0 or streams["stderr"]:
                    raise Refusal("missing/failed exit or stderr")
                validate(op, bytes(streams["stdout"]), profile)
                record["complete"] = True
            finally:
                for name, data in streams.items():
                    filename = f"{number:02d}-{name}.bin"
                    with (output / filename).open("xb") as stream:
                        stream.write(data)
                    record[name + "_file"] = filename
                    record[name + "_bytes"] = len(data)
                    record[name + "_sha256"] = sha(data)
        manifest["complete"] = True
    except Refusal as exc:
        manifest["stop"] = str(exc)
    except BaseException:
        manifest["stop"] = "host I/O failure or interrupted replay"
        raise
    finally:
        manifest["monotonic_end"] = time.monotonic()
        manifest["fixture_elapsed_ms"] = elapsed
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.fixture is None and args.expected is None and args.out is None:
            result = plan()
            result["plan_sha256"] = sha(canonical(result))
            print(json.dumps(result, indent=2))
            return 0
        if None in (args.fixture, args.expected, args.out):
            raise Refusal("replay requires --fixture, --expected and --out")
        manifest = replay(load_json(args.fixture), load_json(args.expected), args.out)
        # No identifiers, raw strings or private stop detail in public stdout.
        print(json.dumps({"mode": "offline-replay", "complete": manifest["complete"],
                          "physical_evidence": False, "records": len(manifest["records"])}))
        return 0 if manifest["complete"] else 1
    except (Refusal, OSError) as exc:
        print("characterization refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
