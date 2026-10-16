# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounded capture and simulation boundary. No ADB launcher or live backend.

An injected simulation supplies already-created binary pipe processes. Future
ADB argv are DATA ONLY. No function in this module executes those arguments.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import queue
import re
import subprocess
import threading
import time
import json

import characterization_plan as cp

ADB = r"C:\Users\dante\AppData\Local\Android\platform-tools\adb.exe"
ADB_SHA256 = "56656270da132f44e9cb4fb86a12ba965635c80423d43dcdd944d9fec4ab4622"
EXTRA = (
    cp.Operation("android-release", "/system/bin/getprop ro.build.version.release"),
    cp.Operation("bootloader-report", "/system/bin/getprop ro.bootloader"),
    cp.Operation("partitions", "/system/bin/toybox head -c 65537 /proc/partitions", 65536),
    cp.Operation("block-names", "/system/bin/toybox ls -l /dev/block/by-name", 65536),
    cp.Operation("sound-cards", "/system/bin/toybox head -c 65537 /proc/asound/cards", 65536),
    cp.Operation("sound-pcm", "/system/bin/toybox head -c 65537 /proc/asound/pcm", 65536),
    cp.Operation("input-devices", "/system/bin/toybox head -c 65537 /proc/bus/input/devices", 65536),
    cp.Operation("graphics-names", "/system/bin/toybox ls -l /sys/class/graphics", 16384),
    cp.Operation("power-names", "/system/bin/toybox ls -l /sys/class/power_supply", 16384),
    cp.Operation("regulator-names", "/system/bin/toybox ls -l /sys/class/regulator", 16384),
)
EVIDENCE = cp.EVIDENCE[:-1] + EXTRA + cp.EVIDENCE[-1:]
REGISTRY = {o.id: o for o in cp.IDENTITY + EVIDENCE + cp.OPERATIONS[-len(cp.IDENTITY):]}


def schedule(selected=None):
    selected = tuple(o.id for o in EVIDENCE) if selected is None else tuple(selected)
    if (not selected or any(not isinstance(id, str) for id in selected)
            or len(selected) != len(set(selected))
            or selected != tuple(o.id for o in EVIDENCE if o.id in selected)):
        raise cp.Refusal("unknown, duplicate or reordered operation selection")
    if any(p in selected for p in ("model", "compatible")) and "tree-link" not in selected:
        raise cp.Refusal("tree properties require reviewed alias check")
    return cp.IDENTITY + tuple(REGISTRY[id] for id in selected) + cp.OPERATIONS[-len(cp.IDENTITY):]


def plan(selected=None):
    return {"mode": "simulation-only", "live_backend": False,
            "operations": [asdict(o) for o in schedule(selected)],
            "total_cap": cp.TOTAL_CAP, "session_ms": cp.SESSION_MS,
            "adb_path": ADB, "adb_sha256": ADB_SHA256,
            "server": "127.0.0.1:5037", "shell_v2_required": True,
            "guard_before_and_after_every_operation": True}


def future_argv(operation_id, profile):
    """Pure construction; never launch this tuple in simulation."""
    cp.expected_profile(profile)
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,256}", profile["binding"]["serial"]):
        raise cp.Refusal("unreviewed serial syntax")
    if not isinstance(operation_id, str) or operation_id not in REGISTRY:
        raise cp.Refusal("operation not allowed")
    return (ADB, "-H", "127.0.0.1", "-P", "5037", "-t",
            profile["binding"]["transport_id"], "shell", "-n", "-T", REGISTRY[operation_id].remote)


@dataclass
class Capture:
    stdout: bytes
    stderr: bytes
    exit: int | None
    status: str
    elapsed_ms: int
    cleanup_complete: bool


def capture(process, cap, remaining, deadline, cancel):
    """Drain binary stdout/stderr concurrently under a real monotonic deadline.

    Process is supplied by a trusted simulator, not launched here. Readers use
    bounded chunks/queue. On failure kill once, reap with a bound and stop. Child
    descendants/remote work are not guaranteed cancelled by killing the client.
    """
    started = time.monotonic()
    pending = queue.Queue(maxsize=8)
    stop = threading.Event()
    buffers = {name: bytearray() for name in ("stdout", "stderr")}

    def put(item):
        while not stop.is_set():
            try:
                pending.put(item, timeout=.02)
                return
            except queue.Full:
                pass

    def read(name, stream):
        try:
            reader = getattr(stream, "read1", stream.read)
            while not stop.is_set():
                data = reader(4096)
                if not isinstance(data, bytes) or len(data) > 4096:
                    raise ValueError("invalid binary pipe chunk")
                put((name, data, None))
                if not data:
                    return
        except OSError:
            put((name, b"", "disconnected"))
        except Exception:
            put((name, b"", "invalid_transport"))

    readers = [threading.Thread(target=read, args=(name, getattr(process, name)), daemon=True)
               for name in buffers]
    status, code, eof, cleanup = "ok", None, set(), True
    try:
        for thread in readers:
            thread.start()
        while True:
            if cancel.is_set():
                status = "cancelled"
                break
            left = deadline - time.monotonic()
            if left <= 0:
                status = "timeout"
                break
            if len(eof) == 2:
                code = process.poll()
                if code is not None:
                    if type(code) is not int:
                        status = "invalid_exit"
                    elif code == 127:
                        status = "unsupported"
                    elif b"permission denied" in bytes(buffers["stderr"]).lower():
                        status = "inaccessible"
                    elif code != 0:
                        status = "command_failed"
                    elif buffers["stderr"]:
                        status = "unexpected_stderr"
                    break
            try:
                name, data, error = pending.get(timeout=min(left, .02))
            except queue.Empty:
                continue
            if error:
                status = error
                break
            if not data:
                eof.add(name)
                continue
            room = min(cap + 1 - len(buffers[name]), remaining + 1)
            buffers[name].extend(data[:room])
            remaining -= len(data)
            if len(data) > room or len(buffers[name]) > cap or remaining < 0:
                status = "data_limit"
                break
    except KeyboardInterrupt:
        status = "interrupted"
    except OSError:
        status = "disconnected"
    finally:
        stop.set()
        if status != "ok" or code is None:
            try:
                process.kill()
            except OSError:
                pass
        try:
            if type(process.wait(timeout=.5)) is not int:
                cleanup = False
        except (subprocess.TimeoutExpired, OSError):
            cleanup = False
        for thread in readers:
            thread.join(timeout=.1)
        for name, thread in zip(buffers, readers):
            if thread.is_alive():
                # Closing a BufferedReader held by another thread can itself hang.
                cleanup = False
            else:
                getattr(process, name).close()
    if not cleanup and status == "ok":
        status = "cleanup_failed"
    return Capture(bytes(buffers["stdout"]), bytes(buffers["stderr"]), code, status,
                   round((time.monotonic() - started) * 1000), cleanup)


def guard(snapshot, profile, epoch=None):
    cp.exact_keys(snapshot, ("binding", "shell_v2", "server_epoch", "usb"))
    cp.expected_profile({"binding": snapshot["binding"], "identity": profile["identity"]})
    if (snapshot["binding"] != profile["binding"] or snapshot["shell_v2"] is not True
            or snapshot["usb"] is not True
            or not isinstance(snapshot["server_epoch"], str)
            or not 0 < len(snapshot["server_epoch"]) <= 128
            or (epoch is not None and snapshot["server_epoch"] != epoch)):
        raise cp.Refusal("identity, protocol or server continuity mismatch")
    return snapshot["server_epoch"]


def simulate(transport, profile, output, reviewed_digest, selected=None, cancel=None):
    """Only an explicitly injected simulation is admitted. No live/default path.

    snapshot() and start() are trusted simulator interfaces and must return
    promptly. Future live implementations must bound these admission/start calls
    too; pipe tests alone cannot establish that property for an ADB launcher.
    """
    cp.expected_profile(profile)
    profile = json.loads(cp.canonical(profile))
    operations = schedule(selected)
    digest = cp.sha(cp.canonical(plan(selected)))
    if reviewed_digest != digest or getattr(transport, "mode", None) != "simulation":
        raise cp.Refusal("exact simulation plan required; live transport unavailable")
    for op in operations:
        future_argv(op.id, profile)
    epoch = guard(transport.snapshot(), profile)
    output = cp.private_directory(output)
    manifest = {"mode": "simulation", "physical_evidence": False, "complete": False,
                "plan_sha256": digest, "profile_sha256": cp.sha(cp.canonical(profile)),
                "tool_sha256": cp.sha(Path(__file__).read_bytes()),
                "policy_sha256": cp.sha(Path(cp.__file__).read_bytes()),
                "binding": profile["binding"], "server_epoch": epoch,
                "utc": datetime.now(timezone.utc).isoformat(), "records": [], "stop": None}
    cancel = cancel if cancel is not None else threading.Event()
    started = time.monotonic()
    deadline = started + cp.SESSION_MS / 1000
    manifest["monotonic_start"] = started
    total = 0
    try:
        for index, op in enumerate(operations):
            if cancel.is_set() or time.monotonic() >= deadline:
                raise cp.Refusal("cancelled or session deadline")
            if total >= cp.TOTAL_CAP:
                raise cp.Refusal("session byte budget exhausted")
            before = transport.snapshot()
            guard(before, profile, epoch)
            if cancel.is_set() or time.monotonic() >= deadline:
                raise cp.Refusal("cancelled or session deadline")
            argv = future_argv(op.id, profile)
            record = {"id": op.id, "operation": asdict(op), "argv_proposed_only": argv, "complete": False,
                      "guard_before": before, "capture_status": "not_started"}
            manifest["records"].append(record)
            process = transport.start(op.id, argv)
            captured = capture(process, op.cap, cp.TOTAL_CAP - total,
                               min(deadline, time.monotonic() + op.timeout_ms / 1000), cancel)
            record.update({"exit": captured.exit, "capture_status": captured.status,
                           "elapsed_ms": captured.elapsed_ms, "cleanup_complete": captured.cleanup_complete})
            for name in ("stdout", "stderr"):
                data = getattr(captured, name)
                filename = f"{index:02d}-{name}.bin"
                with (output / filename).open("xb") as stream:
                    stream.write(data)
                total += len(data)
                record[name] = {"file": filename, "bytes": len(data), "sha256": cp.sha(data)}
            after = transport.snapshot()
            record["guard_after"] = after
            guard(after, profile, epoch)
            if captured.status != "ok":
                raise cp.Refusal(captured.status)
            try:
                cp.validate(op, captured.stdout, profile)
            except cp.Refusal:
                record["capture_status"] = "invalid_output"
                raise
            record["complete"] = True
        manifest["complete"] = True
    except cp.Refusal as exc:
        manifest["stop"] = str(exc)
    except BaseException:
        manifest["stop"] = "host I/O failure or interruption"
        raise
    finally:
        manifest["monotonic_end"] = time.monotonic()
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
    return manifest
