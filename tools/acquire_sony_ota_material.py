# SPDX-License-Identifier: GPL-2.0-or-later
"""SK1 fixed acquisition adapter. CLI only prints the plan; live entry is frozen.

Uses the existing guarded ADB server protocol, never an adb subprocess. This
experiment writes one temporary helper and makes at most one HIDL business call.
It is not covered by any earlier read-only grant. No automatic recovery/retry.
"""
import json
from pathlib import Path
import re
import struct
import threading

import adb_readonly as ar
import characterization_plan as cp
import characterization_transport as ct

REPO = Path(__file__).resolve().parents[1]
PREP = REPO / "build/m10/sk1-preparation-20261015-01"
DEX = PREP / "key-probe-frozen/key-probe-dex/classes.dex"
DEX_SIZE = 4904
DEX_SHA256 = "2c65d860fc848640e8f46015b4600fa0adeffd3e4df7619575c2c75874af7c5b"
REMOTE = "/data/local/tmp/nwa306-sk1-20261015-01"
REMOTE_DEX = REMOTE + "/classes.dex"
PARENT = cp.Operation("temporary-parent", "/system/bin/toybox ls -ldZ /data/local/tmp")
APP = cp.Operation("runtime", "/system/bin/toybox ls -lZ /system/bin/app_process64")
MKDIR = cp.Operation("exclusive-mkdir", "/system/bin/toybox mkdir -m 700 " + REMOTE)
HASH = cp.Operation("helper-hash", "/system/bin/toybox sha256sum " + REMOTE_DEX)
HELPER = cp.Operation("material", "/system/bin/toybox env CLASSPATH=" + REMOTE_DEX +
                      " /system/bin/toybox timeout -s KILL 8 /system/bin/app_process64"
                      " /system/bin SonyOtaKeyProbe --run-approved", 64, 12000)
REMOVE = cp.Operation("remove-helper", "/system/bin/toybox rm " + REMOTE_DEX)
RMDIR = cp.Operation("remove-directory", "/system/bin/toybox rmdir " + REMOTE)
OPERATIONS = cp.IDENTITY + (PARENT, APP, MKDIR, HASH, HELPER, REMOVE, RMDIR) + cp.OPERATIONS[-11:]


def plan():
    return {"stage": "SK1", "endpoint": list(ar.ENDPOINT), "protocol_version": ar.VERSION.decode(),
            "operations": [ct.asdict(o) for o in OPERATIONS], "upload_after": MKDIR.id,
            "upload": {"service": "sync:", "protocol": "SEND/DATA/DONE/OKAY/QUIT v1",
                       "destination": REMOTE_DEX, "mode_decimal": 384, "mtime": 0,
                       "bytes": DEX_SIZE, "sha256": DEX_SHA256, "timeout_ms": 5000,
                       "maximum_attempts": 1, "failure_message_cap": 4096},
            "wire_cap": cp.TOTAL_CAP, "session_ms": 180000, "shell_frame_cap": 4096,
            "strict_stream_cap": True, "decoded_stream_cap": 512 * 1024,
            "helper_stdout_and_stderr_cap_each": 64, "maximum_business_calls": 1,
            "failure_policy": "stop all device requests immediately; no cleanup after failure; no retry",
            "transport_binding": "original serial and identity; one initial current USB ID; no later rebinding",
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes()) for p in
                            (__file__, ar.__file__, cp.__file__, ct.__file__, ar.p1.__file__,
                             ar.c1.__file__, ar.b2.__file__, ar.sr.__file__)}}


def inspect_material(data):
    if len(data) != 64 or data[:4] != b"SK1\0" or struct.unpack_from("<III", data, 4) != (0, 32, 16):
        raise cp.Refusal("invalid_material_record")
    if not any(data[16:48]): raise cp.Refusal("zero_material_key")
    # Never return key/IV encodings or their separate hashes in a summary.
    return {"format": "SK1-v1", "status": 0, "key_bytes": 32, "iv_bytes": 16,
            "authentic_OTA_decryption_verified": False}


def metadata(operation, data):
    try: text = data.decode("ascii")
    except UnicodeError as exc: raise cp.Refusal("invalid_metadata_encoding") from exc
    path = "/data/local/tmp" if operation == PARENT else "/system/bin/app_process64"
    kind = "d" if operation == PARENT else "-"
    # One ordinary entry, no aliases, control characters, extra lines or banners.
    if not text.endswith('\n') or any(ord(c) < 32 and c != '\n' or ord(c) > 126 for c in text):
        raise cp.Refusal("unexpected_metadata_entry")
    fields = text[:-1].split()
    if len(fields) != 9 or '\n' in text[:-1] or fields[-1] != path:
        raise cp.Refusal("unexpected_metadata_entry")
    mode, links, owner, group, label, size, date, clock, _ = fields
    if not re.fullmatch(kind + r"[r-][w-][xSs-][r-][w-][xSs-][r-][w-][xTt-]", mode):
        raise cp.Refusal("unexpected_metadata_mode")
    ar.p1.common(mode, links, owner, group, label, date, clock)
    ar.p1.number(size)
    if operation == APP and mode[9] != "x": raise cp.Refusal("runtime_not_other_executable")


class Acquisition(ar.Session):
    def __init__(self, *args):
        self.upload_attempted = False
        super().__init__("SK1", *args)

    def make_policy(self, stage): return plan()
    def allowed_operations(self): return OPERATIONS

    def allow(self, service):
        if service == "sync:" and self.profile is not None and self.upload_attempted: return
        super().allow(service)

    def validate_payload(self, operation, data, profile):
        if operation in (PARENT, APP): metadata(operation, data)
        elif operation in (MKDIR, REMOVE, RMDIR):
            if data: raise cp.Refusal("unexpected_mutation_stdout")
        elif operation == HASH:
            if data != (DEX_SHA256 + "  " + REMOTE_DEX + "\n").encode():
                raise cp.Refusal("transferred_helper_hash_mismatch")
        elif operation == HELPER: inspect_material(data)
        else: cp.validate(operation, data, profile)

    def upload(self, profile, dex):
        if self.upload_attempted: raise cp.Refusal("upload_already_attempted")
        self.upload_attempted = True  # Consume even an interrupted first byte.
        self.manifest["upload_attempted"] = True
        with self.wire("helper-upload", 5000) as wire:
            wire.request("host:tport:serial:" + profile["binding"]["serial"])
            if int.from_bytes(wire.exact(8), "little") != int(profile["binding"]["transport_id"]):
                raise cp.Refusal("selected_transport_mismatch")
            self.check()
            wire.request("sync:")
            name = (REMOTE_DEX + ",384").encode("ascii")
            wire.send(b"SEND" + struct.pack("<I", len(name)) + name)
            wire.send(b"DATA" + struct.pack("<I", len(dex)) + dex)
            wire.send(b"DONE" + struct.pack("<I", 0))
            status, size = struct.unpack("<4sI", wire.exact(8))
            if status == b"FAIL":
                if size > 4096: raise cp.Refusal("sync_failure_message_limit")
                wire.exact(size)  # Only private raw evidence, never exception text.
                raise cp.Refusal("sync_denied")
            if status != b"OKAY" or size != 0: raise cp.Refusal("invalid_sync_response")
            # AOSP daemon stays in sync mode. QUIT, not a second smart-socket request.
            wire.send(b"QUIT" + struct.pack("<I", 0))
            wire.eof()
        self.manifest["upload_acknowledged"] = True


def run(approval, output, profile, *, connector=None, cancel=None):
    policy = plan()
    cp.expected_profile(profile)
    ct.future_argv("uid", profile)  # Syntax only.
    cp.exact_keys(approval, ("approved", "stage", "plan_sha256", "profile_sha256", "bundle_sha256", "output"))
    if (approval["approved"] is not True or approval["stage"] != "SK1"
            or approval["plan_sha256"] != cp.sha(cp.canonical(policy))
            or approval["profile_sha256"] != cp.sha(cp.canonical(profile))
            or not isinstance(approval["bundle_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", approval["bundle_sha256"])
            or approval["output"] != str(Path(output).absolute())):
        raise cp.Refusal("SK1_approval_code_profile_output_mismatch")
    if ar.sys.byteorder != "little": raise cp.Refusal("unsupported_host_endianness")
    if DEX.is_symlink() or not DEX.is_file(): raise cp.Refusal("helper_not_ordinary_file")
    with DEX.open("rb") as f: dex = f.read(16385)
    if len(dex) != DEX_SIZE or cp.sha(dex) != DEX_SHA256: raise cp.Refusal("frozen_helper_changed")
    original = json.loads(cp.canonical(profile))
    output = cp.private_directory(output)
    session = Acquisition(output, connector if connector is not None else ar.connect_existing,
                          cancel if cancel is not None else threading.Event())
    session.manifest.update(expected_profile=original, profile_sha256=approval["profile_sha256"],
                            bundle_sha256=approval["bundle_sha256"],
                            approval_sha256=cp.sha(cp.canonical(approval)),
                            session_binding_identity_verified=False, upload_attempted=False,
                            temporary_paths_may_remain=True, material_promoted=False)
    try:
        if session.query("host:version", "version") != ar.VERSION: raise cp.Refusal("incompatible_server")
        binding, attrs = ar.inventory(session.query("host:devices-l", "initial-inventory"))
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
            if index == 10: session.manifest["session_binding_identity_verified"] = True
            decoded = sum(r[s]["bytes"] for r in session.manifest["observations"] for s in ("stdout", "stderr"))
            if decoded > policy["decoded_stream_cap"]: raise cp.Refusal("decoded_stream_limit")
            if op == MKDIR:
                session.guard(current)
                session.upload(current, dex)
                session.guard(current)
            if op == RMDIR: session.manifest["temporary_paths_may_remain"] = False
        session.check()
        session.manifest["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        session.manifest["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        session.close()
        if session.manifest["complete"] and session.changed.is_set():
            session.manifest.update(complete=False, stop="transport_watch_changed_or_lost")
        # Raw stdout is always private, even after a later failure. No public key
        # output, no duplicate material file, and no promotion on failed bookends.
        if session.manifest["complete"]:
            record = session.manifest["observations"][15]["stdout"]
            session.manifest["candidate_artifact"] = {**record, **inspect_material((output / record["file"]).read_bytes())}
            session.manifest["host_guard_pending"] = True
        with (output / "manifest.json").open("x", encoding="utf-8") as f:
            json.dump(session.manifest, f, indent=2); f.write("\n")
    return session.manifest


def main(argv=None):
    import sys
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("SK1 requires the separately authorized frozen run_sony_ota_material_once.py entry")
        return 2
    p = plan()
    print(json.dumps({**p, "plan_sha256": cp.sha(cp.canonical(p)), "execution": False}, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
