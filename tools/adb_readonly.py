# SPDX-License-Identifier: GPL-2.0-or-later
"""Explicitly invoked, fixed-service client of an EXISTING loopback ADB server.

Default CLI prints a plan. No subprocess, daemon lifecycle, USB discovery on
import, reconnect or retry. Tests inject sockets; they never use the connector.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import struct
import sys
import threading
import time

import characterization_plan as cp
import characterization_transport as ct
import characterization_b2 as b2
import characterization_c1 as c1
import characterization_p1 as p1
import standing_readonly as sr

ENDPOINT = ("127.0.0.1", 5037)
HOST_CAP = 16384
VERSION = b"0029"  # ADB_SERVER_VERSION 41, not the SDK release number.


class Fault(cp.Refusal):
    pass


def inventory(data):
    try:
        lines = data.decode("ascii").splitlines()
    except UnicodeError as exc:
        raise Fault("invalid_inventory") from exc
    if len(lines) != 1:
        raise Fault("ambiguous_or_absent_device")
    fields = lines[0].split()
    if (len(fields) < 3 or not re.fullmatch(r"[A-Za-z0-9_.-]{1,256}", fields[0])
            or fields[1] != "device" or not fields[-1].startswith("transport_id:")):
        raise Fault("unavailable_or_invalid_device")
    tid = fields[-1].removeprefix("transport_id:")
    if not re.fullmatch(r"[1-9][0-9]{0,19}", tid) or int(tid) > 2**64 - 1:
        raise Fault("invalid_transport_id")
    attrs = {}
    for value in fields[2:-1]:
        key, separator, text = value.partition(":")
        if not separator or not text or key in attrs or key not in ("usb", "product", "model", "device"):
            raise Fault("invalid_inventory_attribute")
        attrs[key] = text
    return {"serial": fields[0], "transport_id": tid, "state": "device", "device_count": 1}, attrs


def operations(stage):
    if stage == "A": return ()
    if stage == "B": return ct.schedule()
    if stage == "B2": return b2.OPERATIONS
    if stage == "C1": return c1.OPERATIONS
    if stage == "P1": return p1.OPERATIONS
    if stage in ("U1", "H1"): return sr.operations(stage)
    raise Fault("invalid_stage")


def plan(stage):
    if stage not in ("A", "B", "B2", "C1", "P1", "U1", "H1"):
        raise Fault("invalid_stage")
    return {"stage": stage, "endpoint": list(ENDPOINT), "protocol_version": VERSION.decode(),
            "host_cap": HOST_CAP, "wire_cap": 65536 if stage == "A" else cp.TOTAL_CAP,
            "session_ms": 20000 if stage == "A" else cp.SESSION_MS,
            **({"output_cap": c1.OUTPUT_CAP, "strict_stream_cap": True} if stage == "C1" else {}),
            **({"output_cap": p1.OUTPUT_CAP, "strict_stream_cap": True} if stage == "P1" else {}),
            **({"transport_binding": "P1 resolves one current online USB transport for the original serial; only its ID is session-local; original identities precede metadata; no mid-session rebinding"} if stage == "P1" else {}),
            "operations": [ct.asdict(o) for o in operations(stage)],
            "services": ["host:version", "host:devices-l", "host:tport:usb"] +
                        ([] if stage == "A" else ["host:track-devices", "host-transport-id:T:features",
                                                   "host:tport:serial:S", "shell,v2,raw:R"]),
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes())
                             for p in (__file__, cp.__file__, ct.__file__) +
                                      ((b2.__file__,) if stage == "B2" else ()) +
                                      ((c1.__file__,) if stage == "C1" else ()) +
                                      ((p1.__file__, c1.__file__) if stage == "P1" else ()) +
                                      ((sr.__file__,) if stage in ("U1", "H1") else ())}}


def connect_existing(deadline):
    """Only explicit run() reaches this. No DNS, executable or retry path."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        left = deadline - time.monotonic()
        if left <= 0:
            raise Fault("timeout")
        sock.settimeout(min(left, 1.0))
        sock.connect(ENDPOINT)
        return sock
    except BaseException:
        sock.close()
        raise


class Wire:
    def __init__(self, session, label, deadline):
        self.session, self.deadline, self.sock = session, deadline, None
        self.record = {"index": len(session.manifest["connections"]), "label": label,
                       "utc": datetime.now(timezone.utc).isoformat(), "monotonic_start": time.monotonic(),
                       "requests": [], "complete": False}
        session.manifest["connections"].append(self.record)
        self.files, self.hashes, self.counts = {}, {}, {}
        try:
            for direction in ("tx", "rx"):
                name = f"{self.record['index']:03d}-{label}.{direction}.bin"
                self.record[direction] = {"file": name}
                self.files[direction] = (session.output / name).open("xb")
                self.hashes[direction] = hashlib.sha256()
                self.counts[direction] = 0
            session.check()
            self.sock = session.connector(deadline)
        except BaseException:
            self.close()
            raise

    def log(self, direction, data):
        with self.session.lock:
            self.session.wire_bytes += len(data)
            self.files[direction].write(data)
            self.hashes[direction].update(data)
            self.counts[direction] += len(data)
            if self.session.wire_bytes > self.session.cap:
                raise Fault("session_byte_limit")

    def remaining(self):
        with self.session.lock:
            return self.session.cap - self.session.wire_bytes

    def recv(self, count):
        self.session.check()
        left = self.deadline - time.monotonic()
        if left <= 0:
            raise Fault("timeout")
        self.sock.settimeout(min(.1, left))
        data = self.sock.recv(min(count, 4096, max(1, self.remaining() + 1)))
        if not isinstance(data, bytes) or len(data) > min(count, 4096):
            raise Fault("invalid_socket")
        self.log("rx", data)
        return data

    def exact(self, count):
        result = bytearray()
        while len(result) < count:
            try:
                data = self.recv(count - len(result))
            except socket.timeout:
                continue
            if not data:
                raise Fault("truncated_protocol")
            result.extend(data)
        return bytes(result)

    def send(self, data):
        # Refuse the whole request before sending if its budget is unavailable.
        if len(data) > self.remaining():
            raise Fault("session_byte_limit")
        offset = 0
        while offset < len(data):
            self.session.check()
            left = self.deadline - time.monotonic()
            if left <= 0:
                raise Fault("timeout")
            self.sock.settimeout(min(.1, left))
            try:
                sent = self.sock.send(data[offset:])
            except socket.timeout as exc:
                # A send timeout has uncertain completion; never resend it.
                raise Fault("uncertain_send") from exc
            if type(sent) is not int or not 0 < sent <= len(data) - offset:
                raise Fault("connection_lost")
            self.log("tx", data[offset:offset + sent])
            offset += sent  # Remaining bytes of this request, not a retry.

    def length(self, cap):
        header = self.exact(4)
        if not re.fullmatch(rb"[0-9a-fA-F]{4}", header):
            raise Fault("invalid_length")
        size = int(header, 16)
        if size > cap:
            raise Fault("host_byte_limit")
        return self.exact(size)

    def request(self, service):
        self.session.allow(service)
        self.record["requests"].append(service)
        data = service.encode("ascii")
        if len(data) > 65535:
            raise Fault("invalid_request")
        self.send(f"{len(data):04x}".encode() + data)
        status = self.exact(4)
        if status == b"FAIL":
            self.length(HOST_CAP)  # Private raw log retains the server's reason.
            raise Fault("server_FAIL")
        if status != b"OKAY":
            raise Fault("invalid_status")

    def eof(self):
        while True:
            try:
                if self.recv(1):
                    raise Fault("trailing_protocol_data")
                return
            except socket.timeout:
                continue

    def close(self):
        if self.sock is not None:
            self.sock.close()
        for direction, stream in self.files.items():
            stream.close()
            self.record[direction].update(bytes=self.counts[direction], sha256=self.hashes[direction].hexdigest())
        self.record["monotonic_end"] = time.monotonic()

    def __enter__(self): return self

    def __exit__(self, kind, value, trace):
        self.record["complete"] = kind is None
        self.close()


class Session:
    def __init__(self, stage, output, connector, cancel):
        self.stage, self.output, self.connector, self.cancel = stage, output, connector, cancel
        self.policy = self.make_policy(stage)
        self.cap, self.wire_bytes = self.policy["wire_cap"], 0
        self.deadline = time.monotonic() + self.policy["session_ms"] / 1000
        self.lock, self.changed, self.stopping = threading.Lock(), threading.Event(), threading.Event()
        self.monitor = self.watcher = None
        self.profile = None
        self.manifest = {"stage": stage, "mode": "injected" if connector is not connect_existing else "live",
                         "live_server_acquisition": connector is connect_existing,
                         "physical_evidence": False, "complete": False, "stop": None,
                         "utc": datetime.now(timezone.utc).isoformat(), "monotonic_start": time.monotonic(),
                         "plan_sha256": cp.sha(cp.canonical(self.policy)), "connections": [], "observations": []}

    def make_policy(self, stage):
        return plan(stage)

    def allowed_operations(self):
        return operations(self.stage)

    def validate_payload(self, operation, data, profile):
        if self.stage == "C1":
            c1.validate(operation, data, profile)
        elif self.stage == "P1":
            p1.validate(operation, data, profile)
        elif self.stage in ("U1", "H1"):
            sr.validate(operation, data, profile)
        else:
            cp.validate(operation, data, profile)

    def allow(self, service):
        allowed = {"host:version", "host:devices-l", "host:tport:usb"}
        if self.stage != "A" and self.profile is not None:
            b = self.profile["binding"]
            allowed.update(("host:track-devices", "host:tport:serial:" + b["serial"],
                            "host-transport-id:" + b["transport_id"] + ":features"))
            allowed.update("shell,v2,raw:" + o.remote for o in self.allowed_operations())
        if not isinstance(service, str) or service not in allowed:
            raise Fault("service_not_allowlisted")

    def check(self):
        if self.cancel.is_set() or self.stopping.is_set(): raise Fault("cancelled")
        if self.changed.is_set(): raise Fault("transport_watch_changed_or_lost")
        if time.monotonic() >= self.deadline: raise Fault("session_timeout")
        if self.wire_bytes > self.cap: raise Fault("session_byte_limit")

    def wire(self, label, timeout_ms=5000):
        return Wire(self, label, min(self.deadline, time.monotonic() + timeout_ms / 1000))

    def query(self, service, label):
        self.allow(service)
        with self.wire(label) as wire:
            wire.request(service)
            data = wire.length(HOST_CAP)
            wire.eof()
            return data

    def usb(self, tid):
        with self.wire("usb-selection") as wire:
            wire.request("host:tport:usb")
            if int.from_bytes(wire.exact(8), "little") != int(tid):
                raise Fault("usb_transport_mismatch")
            # This selects a server transport only; no daemon service is sent.

    def guard(self, profile):
        binding, _ = inventory(self.query("host:devices-l", "inventory"))
        if binding != profile["binding"]: raise Fault("binding_mismatch")
        data = self.query("host-transport-id:" + binding["transport_id"] + ":features", "features")
        if not re.fullmatch(rb"[A-Za-z0-9_]+(?:,[A-Za-z0-9_]+)*", data) or b"shell_v2" not in data.split(b","):
            raise Fault("shell_v2_unavailable")
        self.check()

    def track(self, serial):
        self.monitor = self.wire("transport-watch")
        self.monitor.request("host:track-devices")
        initial = self.monitor.length(HOST_CAP)
        if initial != (serial + "\tdevice\n").encode():
            raise Fault("watch_identity_mismatch")
        self.monitor.deadline = self.deadline

        def watch():
            # Any subsequent notification, EOF or malformed/partial message
            # invalidates the session. Do not consume/recover a changed state.
            try:
                while not self.stopping.is_set():
                    try:
                        data = self.monitor.recv(1)
                    except socket.timeout:
                        continue
                    self.changed.set()
                    return
            except (OSError, cp.Refusal):
                if not self.stopping.is_set(): self.changed.set()

        self.watcher = threading.Thread(target=watch, daemon=True)
        self.watcher.start()

    def shell(self, operation, profile, index):
        if operation not in self.allowed_operations():
            raise Fault("operation_not_allowlisted")
        out, err, code = bytearray(), bytearray(), None
        record = {"id": operation.id, "operation": ct.asdict(operation), "complete": False, "exit": None,
                  "utc": datetime.now(timezone.utc).isoformat(), "monotonic_start": time.monotonic()}
        self.manifest["observations"].append(record)
        try:
            with self.wire("shell-" + f"{index:02d}", operation.timeout_ms) as wire:
                # Serial selection and returned ID are on the SAME connection
                # as the shell service: ID reuse cannot select another serial.
                wire.request("host:tport:serial:" + profile["binding"]["serial"])
                if int.from_bytes(wire.exact(8), "little") != int(profile["binding"]["transport_id"]):
                    raise Fault("selected_transport_mismatch")
                self.check()
                wire.request("shell,v2,raw:" + operation.remote)
                wire.send(b"\x04\x00\x00\x00\x00")  # Close stdin, never send input.
                for _ in range(self.policy.get("shell_frame_cap", 4096)):
                    channel, size = struct.unpack("<BI", wire.exact(5))
                    if channel == 3:
                        if size != 1: raise Fault("invalid_exit_packet")
                        code = wire.exact(1)[0]
                        wire.eof()
                        break
                    if channel not in (1, 2): raise Fault("invalid_shell_channel")
                    target = out if channel == 1 else err
                    sentinel = 0 if self.policy.get("strict_stream_cap", False) else 1
                    if size > operation.cap + sentinel - len(target): raise Fault("stream_byte_limit")
                    # Incrementally preserve payload prefixes on interruption.
                    while size:
                        try:
                            chunk = wire.recv(min(size, 4096))
                        except socket.timeout:
                            continue
                        if not chunk: raise Fault("truncated_protocol")
                        target.extend(chunk)
                        size -= len(chunk)
                    if len(target) > operation.cap: raise Fault("stream_byte_limit")
                if code is None: raise Fault("missing_exit_or_frame_limit")
            record["exit"] = code
            if code == 127: raise Fault("unsupported")
            if b"permission denied" in bytes(err).lower(): raise Fault("inaccessible")
            if code != 0: raise Fault("command_failed")
            if err: raise Fault("unexpected_stderr")
            self.validate_payload(operation, bytes(out), profile)
            self.check()
            record["payload_valid"] = True
        finally:
            record["exit"] = code
            for name, data in (("stdout", out), ("stderr", err)):
                filename = f"{index:02d}-{name}.bin"
                with (self.output / filename).open("xb") as stream: stream.write(data)
                record[name] = {"file": filename, "bytes": len(data), "sha256": cp.sha(data)}
            record["monotonic_end"] = time.monotonic()

    def close(self):
        self.stopping.set()
        if self.watcher:
            self.watcher.join(timeout=.3)
            if self.watcher.is_alive():
                self.manifest["complete"] = False
                self.manifest["stop"] = "watch_cleanup_failed"
                self.monitor.sock.close()
                self.manifest["wire_bytes"] = self.wire_bytes
                self.manifest["monotonic_end"] = time.monotonic()
                return  # Do not close a log stream potentially held by the reader.
        if self.monitor:
            self.monitor.record["complete"] = self.manifest["complete"] and not self.changed.is_set()
            self.monitor.close()
        self.manifest["wire_bytes"] = self.wire_bytes
        self.manifest["monotonic_end"] = time.monotonic()


def run(stage, approval, output, profile=None, *, connector=None, cancel=None, standing_grant=None, turn_id=None):
    """No communication until all local approval/profile/output checks pass.

    Approval files prevent accidental invocation; they are not proof of human
    consent. The operator must separately obtain the human's explicit approval.
    """
    policy = plan(stage)
    if sys.byteorder != "little": raise Fault("unsupported_host_endianness")
    cp.exact_keys(approval, ("approved", "stage", "plan_sha256", "profile_sha256", "output"))
    if (approval["approved"] is not True or approval["stage"] != stage
            or approval["plan_sha256"] != cp.sha(cp.canonical(policy))
            or approval["output"] != str(Path(output).absolute())):
        raise Fault("approval_scope_mismatch")
    if stage != "A":
        cp.expected_profile(profile)
        ct.future_argv("uid", profile)  # Reuse strict serial syntax, no execution.
        if approval["profile_sha256"] != cp.sha(cp.canonical(profile)):
            raise Fault("profile_scope_mismatch")
        profile = json.loads(cp.canonical(profile))
    elif profile is not None or approval["profile_sha256"] is not None:
        raise Fault("unexpected_discovery_profile")
    if stage in ("U1", "H1"):
        if standing_grant is None or turn_id is None: raise Fault("standing grant and turn required")
        return sr.authorized_run(standing_grant, turn_id, stage, policy, profile, output,
                                 lambda: acquire(stage, approval, output, profile, connector, cancel))
    if standing_grant is not None or turn_id is not None: raise Fault("unexpected standing inputs")
    return acquire(stage, approval, output, profile, connector, cancel)


def acquire(stage, approval, output, profile, connector, cancel):
    output = cp.private_directory(output)
    session = Session(stage, output, connector if connector is not None else connect_existing,
                      cancel if cancel is not None else threading.Event())
    session.profile = profile
    session.manifest["expected_profile"] = profile
    session.manifest["approval_sha256"] = cp.sha(cp.canonical(approval))
    session.manifest["profile_sha256"] = approval["profile_sha256"]
    try:
        if session.query("host:version", "version") != VERSION: raise Fault("incompatible_server")
        if stage == "A":
            raw = session.query("host:devices-l", "inventory")
            binding, attrs = inventory(raw)
            if attrs.get("device") != "icx1301": raise Fault("unexpected_discovery_target")
            session.usb(binding["transport_id"])
            session.manifest["candidate_binding"] = binding
            session.manifest["requires_human_physical_match"] = True
        else:
            if stage == "P1":
                binding, attrs = inventory(session.query("host:devices-l", "initial-inventory"))
                profile = p1.current_profile(profile, binding, attrs)
                session.profile = profile
                session.manifest["session_profile"] = profile
                session.manifest["session_binding_identity_verified"] = False
            session.track(profile["binding"]["serial"])
            session.usb(profile["binding"]["transport_id"])
            for index, op in enumerate(operations(stage)):
                session.guard(profile)
                session.shell(op, profile, index)
                session.guard(profile)
                session.manifest["observations"][-1]["complete"] = True
                if stage == "P1" and index == len(cp.IDENTITY) - 1:
                    session.manifest["session_binding_identity_verified"] = True
        session.check()
        session.manifest["complete"] = True
        # Live-server data still needs human unit matching and evidence review.
        # Never promote success to a physical-verification claim automatically.
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        session.manifest["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        session.close()
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(session.manifest, stream, indent=2)
            stream.write("\n")
    return session.manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("A", "B", "B2", "C1", "P1", "U1", "H1"), default="A")
    parser.add_argument("--run-approved", action="store_true")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--standing-grant", type=Path)
    parser.add_argument("--turn-id")
    args = parser.parse_args(argv)
    try:
        if not args.run_approved:
            if any(v is not None for v in (args.approval, args.profile, args.out, args.standing_grant, args.turn_id)):
                raise Fault("execution_inputs_require_run_approved")
            p = plan(args.stage)
            print(json.dumps({**p, "plan_sha256": cp.sha(cp.canonical(p))}, indent=2))
            return 0
        if args.approval is None or args.out is None: raise Fault("approval_and_output_required")
        result = run(args.stage, cp.load_json(args.approval), args.out,
                     cp.load_json(args.profile) if args.profile else None,
                     standing_grant=cp.load_json(args.standing_grant) if args.standing_grant else None,
                     turn_id=args.turn_id)
        print(json.dumps({"stage": args.stage, "complete": result["complete"], "stop": result["stop"]}))
        return 0 if result["complete"] else 1
    except (cp.Refusal, OSError) as exc:
        print("adapter refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
