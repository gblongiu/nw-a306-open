# SPDX-License-Identifier: GPL-2.0-or-later
"""One-shot acquisition of only the APK registered in preserved U1 evidence.

No arbitrary target argument, APK execution, extraction, root or retry. Uses the
existing direct-server wire, tracker and identity guards. Default CLI is inert.
"""
import argparse
import io
import json
from pathlib import Path
import re
import threading
import zipfile

import adb_readonly as ar
import characterization_plan as cp
import characterization_transport as ct
import standing_readonly as sr

MAX_APK = 16 * 1024 * 1024
U1 = cp.PRIVATE_ROOT / "device-u1-20261014-01"


def target_from_u1(directory):
    directory = Path(directory)
    manifest = cp.load_json(directory / "manifest.json")
    if manifest["stage"] != "U1" or not manifest["complete"] or manifest["stop"] is not None:
        raise cp.Refusal("U1 evidence is not complete")
    cp.expected_profile(manifest["expected_profile"])
    record = manifest["observations"][11]
    if record["id"] != "updater-path" or not record["complete"] or record["exit"] != 0:
        raise cp.Refusal("unverified U1 path record")
    item = record["stdout"]
    if item["file"] != "11-stdout.bin": raise cp.Refusal("unexpected U1 path file")
    source = directory / item["file"]
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 16384:
        raise cp.Refusal("invalid U1 path file")
    data = source.read_bytes()
    if len(data) != item["bytes"] or cp.sha(data) != item["sha256"]:
        raise cp.Refusal("U1 path integrity mismatch")
    sr.validate(sr.UPDATER, data, manifest["expected_profile"])
    if len(data.splitlines()) != 1: raise cp.Refusal("ambiguous updater target")
    return data.removeprefix(b"package:").rstrip(b"\n").decode("ascii"), manifest["expected_profile"]


def operations(target):
    return cp.IDENTITY + (
        cp.Operation("registered-path", sr.UPDATER.remote, 16384),
        cp.Operation("file-before", "/system/bin/toybox ls -ld " + target),
        cp.Operation("apk-bytes", f"/system/bin/toybox head -c {MAX_APK + 1} " + target, MAX_APK, 30000),
        cp.Operation("file-after", "/system/bin/toybox ls -ld " + target),
        cp.Operation("registered-after", sr.UPDATER.remote, 16384),
    ) + cp.OPERATIONS[-11:]


def plan(target):
    # Validate shell-safe syntax even for pure synthetic plan construction.
    sr.validate(sr.UPDATER, ("package:" + target + "\n").encode("ascii"), {})
    return {"stage": "APK1", "target": target, "operations": [ct.asdict(o) for o in operations(target)],
            "wire_cap": 40 * 1024 * 1024, "session_ms": 300000, "shell_frame_cap": 8192,
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes())
                            for p in (__file__, ar.__file__, cp.__file__, ct.__file__, sr.__file__)}}


def apk_structure(data):
    if not 0 < len(data) <= MAX_APK or not data.startswith(b"PK\x03\x04"):
        raise cp.Refusal("invalid bounded APK")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            members = z.infolist()
            names = [m.filename for m in members]
            if (not 1 <= len(members) <= 4096 or len(set(names)) != len(names)
                    or "AndroidManifest.xml" not in names or "classes.dex" not in names
                    or sum(m.file_size for m in members) > 64 * 1024 * 1024):
                raise cp.Refusal("unexpected APK member inventory")
            for member in members:
                name = member.filename
                if (name != member.orig_filename or name.startswith("/") or "\\" in name or any(ord(c) < 32 for c in name)
                        or any(p in (".", "..") for p in name.split("/"))
                        or member.flag_bits & 1 or member.compress_type not in (0, 8)
                        or member.file_size > 32 * 1024 * 1024
                        or (member.external_attr >> 16) & 0o170000 == 0o120000):
                    raise cp.Refusal("unsafe APK member")
                count = 0
                with z.open(member) as stream:
                    while chunk := stream.read(1024 * 1024):
                        count += len(chunk)
                        if count > member.file_size: raise cp.Refusal("APK expansion mismatch")
                if count != member.file_size: raise cp.Refusal("APK member size mismatch")
            return {"members": len(members), "uncompressed_bytes": sum(m.file_size for m in members),
                    "all_zip_crc_checks_passed": True, "sha256": cp.sha(data), "bytes": len(data)}
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError) as exc:
        raise cp.Refusal("invalid APK ZIP structure") from exc


class Acquisition(ar.Session):
    def __init__(self, target, *args):
        self.target, self.metadata, self.size, self.structure = target, None, None, None
        super().__init__("APK1", *args)

    def make_policy(self, stage): return plan(self.target)
    def allowed_operations(self): return operations(self.target)

    def validate_payload(self, operation, data, profile):
        if operation.id in ("registered-path", "registered-after"):
            if data != ("package:" + self.target + "\n").encode():
                raise cp.Refusal("registered target changed")
        elif operation.id == "file-before":
            match = re.fullmatch(rb"-[rwxStTs-]{9}\s+[1-9][0-9]*\s+\S+\s+\S+\s+([0-9]+)\s+(.+)\n", data)
            if not match or not match[2].endswith(b" " + self.target.encode()):
                raise cp.Refusal("target is not reviewed regular file metadata")
            self.size = int(match[1])
            if not 0 < self.size <= MAX_APK: raise cp.Refusal("APK size outside bound")
            self.metadata = data
        elif operation.id == "file-after":
            if data != self.metadata: raise cp.Refusal("target metadata changed")
        elif operation.id == "apk-bytes":
            if self.size is None or len(data) != self.size: raise cp.Refusal("APK transfer size mismatch")
            self.structure = apk_structure(data)
        else:
            cp.validate(operation, data, profile)


def run(u1, approval, output, *, connector=None, cancel=None):
    target, profile = target_from_u1(u1)
    policy = plan(target)
    cp.exact_keys(approval, ("approved", "plan_sha256", "profile_sha256", "u1_manifest_sha256", "output"))
    if (approval["approved"] is not True or approval["plan_sha256"] != cp.sha(cp.canonical(policy))
            or approval["profile_sha256"] != cp.sha(cp.canonical(profile))
            or approval["u1_manifest_sha256"] != cp.sha((Path(u1) / "manifest.json").read_bytes())
            or approval["output"] != str(Path(output).absolute())):
        raise cp.Refusal("APK acquisition approval mismatch")
    if ar.sys.byteorder != "little": raise cp.Refusal("unsupported host endianness")
    output = cp.private_directory(output)  # Exclusive: failed attempts cannot be reused.
    session = Acquisition(target, output, connector if connector is not None else ar.connect_existing,
                          cancel if cancel is not None else threading.Event())
    session.profile = profile
    session.manifest.update(expected_profile=profile, approval_sha256=cp.sha(cp.canonical(approval)),
                            profile_sha256=approval["profile_sha256"], u1_manifest_sha256=approval["u1_manifest_sha256"])
    try:
        if session.query("host:version", "version") != ar.VERSION: raise cp.Refusal("incompatible server")
        session.track(profile["binding"]["serial"])
        session.usb(profile["binding"]["transport_id"])
        for index, op in enumerate(operations(target)):
            session.guard(profile)
            session.shell(op, profile, index)
            session.guard(profile)
            session.manifest["observations"][-1]["complete"] = True
        session.check()
        session.manifest["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        session.manifest["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        session.close()
        if session.manifest["complete"]:
            raw = (output / "13-stdout.bin").read_bytes()
            with (output / "automagic.apk").open("xb") as stream: stream.write(raw)
            session.manifest["artifact"] = {"file": "automagic.apk", **session.structure}
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(session.manifest, stream, indent=2); stream.write("\n")
    return session.manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-approved", action="store_true")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if not args.run_approved:
            if args.approval or args.out: raise cp.Refusal("unapproved inputs")
            target, _ = target_from_u1(U1)
            policy = plan(target)
            print(json.dumps({**policy, "plan_sha256": cp.sha(cp.canonical(policy))}, indent=2))
            return 0
        if not args.approval or not args.out: raise cp.Refusal("approval and output required")
        result = run(U1, cp.load_json(args.approval), args.out)
        print(json.dumps({"complete": result["complete"], "stop": result["stop"]}))
        return 0 if result["complete"] else 1
    except (cp.Refusal, OSError) as exc:
        print("acquisition refused: " + str(exc))
        return 2


if __name__ == "__main__": raise SystemExit(main())
