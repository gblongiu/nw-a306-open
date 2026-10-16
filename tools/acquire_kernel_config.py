# SPDX-License-Identifier: GPL-2.0-or-later
"""KC1: one separately approved /proc/config.gz read; default CLI is inert.

Reuses the guarded existing-server adapter. No arbitrary path, subprocess,
privilege change, syscall probe, lifecycle request or retry. Approval records
are accidental-execution guards, not substitutes for direct human consent.
"""
import argparse
import json
from pathlib import Path
import re
import threading
import zlib

import adb_readonly as ar
import characterization_plan as cp
import characterization_transport as ct

MAX_COMPRESSED = 256 * 1024
MAX_EXPANDED = 2 * 1024 * 1024
READ = cp.Operation("kernel-config", "/system/bin/toybox head -c 262145 /proc/config.gz",
                    MAX_COMPRESSED, 5000)
OPERATIONS = cp.IDENTITY + (READ,) + cp.OPERATIONS[-len(cp.IDENTITY):]
SYMBOLS = ("KEXEC", "KEXEC_FILE", "IKCONFIG", "IKCONFIG_PROC")


def plan():
    return {"stage": "KC1", "endpoint": list(ar.ENDPOINT), "protocol_version": ar.VERSION.decode(),
            "operations": [ct.asdict(o) for o in OPERATIONS],
            "wire_cap": cp.TOTAL_CAP, "session_ms": 180000, "shell_frame_cap": 4096,
            "compressed_cap": MAX_COMPRESSED, "overflow_sentinel_bytes": 1,
            "expanded_cap": MAX_EXPANDED, "gzip_members": 1,
            "transport_binding": "P1 binding rule: original serial/identities; one initial current USB ID; no later rebinding",
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes()) for p in
                            (__file__, ar.__file__, cp.__file__, ct.__file__, ar.p1.__file__,
                             ar.c1.__file__, ar.b2.__file__, ar.sr.__file__)}}


def inspect_config(data):
    """Bound expansion before allocation; zlib verifies gzip CRC32 and ISIZE.

    Exactly one member with no trailing bytes is accepted. This inspects supplied
    bytes, not image signatures, effective privileges or syscall accessibility.
    """
    if not 0 < len(data) <= MAX_COMPRESSED:
        raise cp.Refusal("compressed_config_byte_limit")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        raw = decoder.decompress(data, MAX_EXPANDED + 1)
    except zlib.error as exc:
        raise cp.Refusal("invalid_gzip_or_crc") from exc
    if len(raw) > MAX_EXPANDED or decoder.unconsumed_tail:
        raise cp.Refusal("expanded_config_byte_limit")
    if not decoder.eof:
        raise cp.Refusal("truncated_gzip")
    if decoder.unused_data:
        raise cp.Refusal("trailing_gzip_data_or_members")
    if not raw or not raw.endswith(b"\n") or any(c < 32 and c != 10 or c == 127 for c in raw):
        raise cp.Refusal("malformed_config_text")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeError as exc:
        raise cp.Refusal("unsupported_config_encoding") from exc
    headers = [line for line in lines if re.fullmatch(r"# Linux/arm64 [A-Za-z0-9.+_~\-]+ Kernel Configuration", line)]
    if len(headers) != 1 or "# Automatically generated file; DO NOT EDIT." not in lines:
        raise cp.Refusal("missing_arm64_config_header")
    values = {}
    for line in lines:
        off = re.fullmatch(r"# CONFIG_([A-Za-z0-9_]+) is not set", line)
        entry = re.fullmatch(r"CONFIG_([A-Za-z0-9_]+)=(y|m|n|-?[0-9]+|0[xX][0-9a-fA-F]+|\"(?:[^\"\\]|\\.)*\")", line)
        if off or entry:
            key, value = (off[1], "n") if off else (entry[1], entry[2])
            if key in values:
                raise cp.Refusal("duplicate_config_symbol")
            values[key] = value
        elif line and (not line.startswith("#") or line.startswith("# CONFIG_")):
            raise cp.Refusal("malformed_config_entry")
    if not values:
        raise cp.Refusal("empty_configuration")
    for key in SYMBOLS:
        if key in values and values[key] not in (("y", "m", "n") if key == "IKCONFIG" else ("y", "n")):
            raise cp.Refusal("invalid_target_symbol_value")
    state = values.get("KEXEC")
    action = {"n": "stop_ordinary_stock_kernel_kexec; prioritize_Sony_boot_acceptance",
              "y": "assess_legitimate_privilege_policy_and_hardware_prerequisites_before_any_handoff"}.get(
                  state, "unresolved; missing_symbol_is_not_disabled")
    return {"compressed_bytes": len(data), "compressed_sha256": cp.sha(data),
            "expanded_bytes": len(raw), "expanded_sha256": cp.sha(raw),
            "gzip_crc_and_size_valid": True, "config_header": headers[0][2:],
            "symbols": {"CONFIG_" + key: values.get(key, "not_present") for key in SYMBOLS},
            "next_action": action, "privilege_or_execution_proved": False,
            "file_loader_note": "KEXEC_FILE=y would require reconciling the supplied config with missing ARM64 support in published Sony source; absence does not prove unavailable"}


class Acquisition(ar.Session):
    def __init__(self, *args):
        self.inspection = None
        super().__init__("KC1", *args)

    def make_policy(self, stage): return plan()
    def allowed_operations(self): return OPERATIONS

    def validate_payload(self, operation, data, profile):
        if operation == READ:
            self.inspection = inspect_config(data)
        else:
            cp.validate(operation, data, profile)


def run(approval, output, profile, *, connector=None, cancel=None):
    policy = plan()
    cp.expected_profile(profile)
    ct.future_argv("uid", profile)  # Pure syntax check, never executes.
    cp.exact_keys(approval, ("approved", "stage", "plan_sha256", "profile_sha256", "output"))
    if (approval["approved"] is not True or approval["stage"] != "KC1"
            or approval["plan_sha256"] != cp.sha(cp.canonical(policy))
            or approval["profile_sha256"] != cp.sha(cp.canonical(profile))
            or approval["output"] != str(Path(output).absolute())):
        raise cp.Refusal("KC1_approval_code_profile_output_mismatch")
    if ar.sys.byteorder != "little": raise cp.Refusal("unsupported_host_endianness")
    original = json.loads(cp.canonical(profile))
    output = cp.private_directory(output)  # Consumes this exact approved destination once.
    session = Acquisition(output, connector if connector is not None else ar.connect_existing,
                          cancel if cancel is not None else threading.Event())
    session.manifest.update(expected_profile=original, profile_sha256=approval["profile_sha256"],
                            approval_sha256=cp.sha(cp.canonical(approval)),
                            session_binding_identity_verified=False)
    try:
        if session.query("host:version", "version") != ar.VERSION:
            raise cp.Refusal("incompatible_server")
        binding, attrs = ar.inventory(session.query("host:devices-l", "initial-inventory"))
        # Explicitly adopt the established P1 one-time binding rule for KC1.
        current = ar.p1.current_profile(original, binding, attrs)
        session.profile = current
        session.manifest["session_profile"] = current
        session.track(current["binding"]["serial"])
        session.usb(current["binding"]["transport_id"])
        for index, op in enumerate(OPERATIONS):
            session.guard(current)
            session.shell(op, current, index)
            session.guard(current)
            session.manifest["observations"][-1]["complete"] = True
            if index == len(cp.IDENTITY) - 1:
                session.manifest["session_binding_identity_verified"] = True
        session.check()
        session.manifest["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        session.manifest["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        session.close()
        # Include a tracker event observed during final watcher shutdown in the
        # decision; never promote a capture after that last continuity loss.
        if session.manifest["complete"] and session.changed.is_set():
            session.manifest.update(complete=False, stop="transport_watch_changed_or_lost")
        if session.manifest["complete"]:
            record = session.manifest["observations"][len(cp.IDENTITY)]["stdout"]
            # Raw capture is the artifact; avoid redundant copies or promotion on a failed bookend.
            session.manifest["artifact"] = {**record, "format": "config.gz", **session.inspection}
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(session.manifest, stream, indent=2); stream.write("\n")
    return session.manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-approved", action="store_true")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if not args.run_approved:
            if any(x is not None for x in (args.approval, args.profile, args.out)):
                raise cp.Refusal("execution_inputs_require_run_approved")
            p = plan()
            print(json.dumps({**p, "plan_sha256": cp.sha(cp.canonical(p))}, indent=2))
            return 0
        if args.approval is None or args.profile is None or args.out is None:
            raise cp.Refusal("approval_profile_output_required")
        result = run(cp.load_json(args.approval), args.out, cp.load_json(args.profile))
        print(json.dumps({"complete": result["complete"], "stop": result["stop"]}))
        return 0 if result["complete"] else 1
    except (cp.Refusal, OSError) as exc:
        print("KC1 refused: " + str(exc))
        return 2


if __name__ == "__main__": raise SystemExit(main())
