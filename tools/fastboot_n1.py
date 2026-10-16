# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed supervised N1 phases. Import/default CLI never communicates.

No automatic phase progression, retries, ADB executable, software return or
payload command. Human readiness, USB-port matching and return are external
supervision gates, not facts inferred from a successful command.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import re
import subprocess
import threading
import time

import adb_readonly as ar
import characterization_plan as cp
import characterization_transport as ct

FASTBOOT = str(Path(ct.ADB).with_name("fastboot.exe"))
FASTBOOT_SHA256 = "561bec25f791d2ee75ed57ac84a09960c9fadb62f531240a6896fba1cb091d1d"
VARIABLES = ("product", "unlocked", "secure", "current-slot", "version-bootloader", "is-userspace")
GUARDS = {"product": "icx1301", "unlocked": "no", "secure": "yes", "current-slot": "b"}
CAP, SESSION_MS, OUTPUT_CAP = 4096, 450000, 262144


def plan():
    return {"stage": "N1", "entry": "reboot:bootloader", "entry_count": 1,
            "pre_identity": [asdict(o) for o in cp.IDENTITY],
            "enumeration": [FASTBOOT, "devices", "-l"],
            "getvars": [[FASTBOOT, "-s", "S", "getvar", v] for v in VARIABLES],
            "guards": GUARDS, "native_sha256": FASTBOOT_SHA256,
            "per_stream_cap": CAP, "operation_ms": 5000, "session_ms": SESSION_MS,
            "output_cap": OUTPUT_CAP, "wire_cap": cp.TOTAL_CAP, "arrival_ms": 30000,
            "post_identity": [asdict(o) for o in cp.IDENTITY],
            "post_discovery": ["host:version", "host:devices-l", "host:tport:usb"],
            "failure": "stop diagnostics; owner physical return only; no post-return requests",
            "return": "owner Power-only hold about ten seconds once; wait up to two minutes; do not interrupt updates",
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes())
                            for p in (__file__, ar.__file__, cp.__file__, ct.__file__)}}


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2); stream.write("\n")


def admit(approval, profile, output):
    cp.expected_profile(profile)
    ct.future_argv("uid", profile)
    cp.exact_keys(approval, ("approved", "stage", "plan_sha256", "profile_sha256", "output"))
    if (approval["approved"] is not True or approval["stage"] != "N1"
            or approval["plan_sha256"] != cp.sha(cp.canonical(plan()))
            or approval["profile_sha256"] != cp.sha(cp.canonical(profile))
            or approval["output"] != str(Path(output).absolute())):
        raise cp.Refusal("N1 approval/code/profile/output mismatch")


def deadline(start):
    limit = start + SESSION_MS / 1000
    if time.monotonic() >= limit:
        raise cp.Refusal("N1 session deadline")
    return limit


class IdentitySession(ar.Session):
    def __init__(self, stage, output, connector, cancel, start):
        self.transition = False
        self.entry_used = False
        super().__init__(stage, output, connector, cancel)
        self.deadline = deadline(start)

    def make_policy(self, stage):
        return {"stage": stage, "wire_cap": cp.TOTAL_CAP, "session_ms": SESSION_MS,
                "strict_stream_cap": True, "operations": [asdict(o) for o in cp.IDENTITY],
                "N1_plan": plan()}

    def allowed_operations(self):
        return cp.IDENTITY

    def allow(self, service):
        if service == "reboot:bootloader":
            if self.stage != "N1-pre" or not self.transition or self.entry_used:
                raise cp.Refusal("N1 entry not admitted or already attempted")
            self.entry_used = True
        else:
            super().allow(service)

    def check(self):
        if not self.transition:
            return super().check()
        # Only after the last guard and immediately before the one dispatch:
        # expected USB loss is recorded, never used to admit a second request.
        if self.cancel.is_set() or self.stopping.is_set(): raise cp.Refusal("cancelled")
        if time.monotonic() >= self.deadline: raise cp.Refusal("session_timeout")
        if self.wire_bytes > self.cap: raise cp.Refusal("session_byte_limit")


def identity_loop(session, profile):
    for i, op in enumerate(cp.IDENTITY):
        session.guard(profile)
        session.shell(op, profile, i)
        session.guard(profile)
        session.manifest["observations"][-1]["complete"] = True


def start(approval, profile, output, readiness, host_guard, *, connector=None):
    admit(approval, profile, output)
    cp.exact_keys(readiness, ("confirmed", "utc", "profile_sha256", "normal_idle", "power_ready", "battery_ready", "backups_ready"))
    if (any(readiness[k] is not True for k in ("confirmed", "normal_idle", "power_ready", "battery_ready", "backups_ready"))
            or readiness["profile_sha256"] != approval["profile_sha256"]):
        raise cp.Refusal("N1 owner prerequisites missing")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(readiness["utc"])).total_seconds()
    if not 0 <= age <= 120: raise cp.Refusal("N1 readiness is not fresh")
    host_guard()
    out = cp.private_directory(output)
    write_json(out / "approval.json", approval)
    write_json(out / "owner-readiness.json", readiness)
    write_json(out / "plan.json", plan())
    sub = out / "pre-entry"; sub.mkdir()
    started = time.monotonic()
    s = IdentitySession("N1-pre", sub, connector or ar.connect_existing, threading.Event(), started)
    s.profile = json.loads(cp.canonical(profile))
    m = s.manifest
    m.update(expected_profile=profile, N1_plan_sha256=approval["plan_sha256"],
             profile_sha256=approval["profile_sha256"], approval_sha256=cp.sha(cp.canonical(approval)),
             entry_attempted=False, entry_acknowledged=False)
    try:
        if s.query("host:version", "version") != ar.VERSION: raise cp.Refusal("incompatible_server")
        s.track(profile["binding"]["serial"])
        s.usb(profile["binding"]["transport_id"])
        identity_loop(s, profile)
        s.guard(profile)
        host_guard()
        admit(approval, profile, output)
        if (datetime.now(timezone.utc) - datetime.fromisoformat(readiness["utc"])).total_seconds() > 120:
            raise cp.Refusal("N1 readiness expired before entry")
        with s.wire("bootloader-entry") as w:
            w.request("host:tport:serial:" + profile["binding"]["serial"])
            if int.from_bytes(w.exact(8), "little") != int(profile["binding"]["transport_id"]):
                raise cp.Refusal("entry transport mismatch")
            s.check()
            s.transition = True
            m["entry_attempted"] = True
            m["entry_dispatch_monotonic"] = time.monotonic()
            w.request("reboot:bootloader")
            w.eof()
            m["entry_acknowledged"] = True
        m["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        m["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        m["watch_signalled_at_transition"] = s.changed.is_set()
        s.close()
        write_json(sub / "manifest.json", m)
    return m


def argv(serial, variable=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,256}", serial): raise cp.Refusal("invalid serial")
    if variable is None: return [FASTBOOT, "devices", "-l"]
    if variable not in VARIABLES: raise cp.Refusal("N1 variable not allowlisted")
    return [FASTBOOT, "-s", serial, "getvar", variable]


def launch(args):
    # Only diagnose() constructs these arrays, after file/owner/USB checks.
    if args != [FASTBOOT, "devices", "-l"]:
        if (not isinstance(args, list) or len(args) != 5 or args[0] != FASTBOOT
                or args[1] != "-s" or args[3] != "getvar"
                or args != argv(args[2], args[4])):
            raise cp.Refusal("native command outside N1")
    if cp.sha(Path(FASTBOOT).read_bytes()) != FASTBOOT_SHA256:
        raise cp.Refusal("fastboot executable changed")
    return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=False, cwd=str(Path(FASTBOOT).parent),
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def capture(process, limit):
    """Strict bounded binary pipes; successful fastboot stderr is permitted."""
    pending, stop = queue.Queue(maxsize=8), threading.Event()
    data = {"stdout": bytearray(), "stderr": bytearray()}
    def read(name):
        stream = getattr(process, name)
        reader = getattr(stream, "read1", stream.read)
        try:
            while not stop.is_set():
                chunk = reader(CAP)
                if not isinstance(chunk, bytes) or len(chunk) > CAP: raise ValueError()
                while not stop.is_set():
                    try: pending.put((name, chunk, None), timeout=.02); break
                    except queue.Full: pass
                if not chunk: return
        except Exception:
            while not stop.is_set():
                try: pending.put((name, b"", "pipe_error"), timeout=.02); return
                except queue.Full: pass
    threads = [threading.Thread(target=read, args=(n,), daemon=True) for n in data]
    status, code, eof, cleanup = "ok", None, set(), True
    try:
        for t in threads: t.start()
        while True:
            left = limit - time.monotonic()
            if left <= 0: status = "timeout"; break
            if len(eof) == 2 and (code := process.poll()) is not None:
                if type(code) is not int or code != 0: status = "command_failed"
                break
            try: name, chunk, error = pending.get(timeout=min(.02, left))
            except queue.Empty: continue
            if error: status = error; break
            if not chunk: eof.add(name); continue
            room = CAP - len(data[name])
            data[name].extend(chunk[:room])
            if len(chunk) > room: status = "data_limit"; break
    except KeyboardInterrupt:
        status = "interrupted"
    finally:
        stop.set()
        if status != "ok" or code is None:
            try: process.kill()
            except OSError: pass
        try: process.wait(timeout=.5)
        except (subprocess.TimeoutExpired, OSError): cleanup = False
        for name, t in zip(data, threads):
            t.join(timeout=.1)
            if t.is_alive(): cleanup = False
            else: getattr(process, name).close()
    if not cleanup: status = "cleanup_failed"
    return {"stdout": bytes(data["stdout"]), "stderr": bytes(data["stderr"]),
            "exit": code, "status": status, "cleanup_complete": cleanup}


def value(variable, stdout, stderr):
    if variable not in VARIABLES: raise cp.Refusal("unknown variable")
    try: text = (stdout + stderr).decode("ascii")
    except UnicodeError as exc: raise cp.Refusal("non-ASCII fastboot output") from exc
    if any(ord(c) < 32 and c not in "\r\n" or ord(c) == 127 for c in text):
        raise cp.Refusal("invalid fastboot output controls")
    found = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        m = re.fullmatch(r"(?:\(bootloader\) )?" + re.escape(variable) + r": ([ -~]{1,256})", line)
        if m: found.append(m[1]); continue
        if re.fullmatch(r"(?:Finished\. Total time: [0-9]+\.[0-9]+s|finished\. total time: [0-9]+\.[0-9]+s|total time: [0-9]+\.[0-9]+s)", line): continue
        raise cp.Refusal("unexpected fastboot response line")
    if len(found) != 1 or found[0].strip() != found[0] or found[0].lower() in ("unknown", "unknown variable"):
        raise cp.Refusal("empty/unknown/ambiguous fastboot value")
    result = found[0]
    if variable in GUARDS and result != GUARDS[variable]: raise cp.Refusal("fastboot guard mismatch")
    if variable == "is-userspace" and result not in ("yes", "no"): raise cp.Refusal("invalid endpoint classification")
    return result


def diagnose(approval, profile, output, supervision, host_guard, *, launcher=launch):
    admit(approval, profile, output)
    out = Path(output)
    pre = cp.load_json(out / "pre-entry/manifest.json")
    if not pre["complete"] or not pre["entry_acknowledged"] or pre["N1_plan_sha256"] != approval["plan_sha256"]:
        raise cp.Refusal("N1 entry failed or scope changed")
    limit = deadline(pre["monotonic_start"])
    if supervision != {"same_unit_fastboot_screen": True, "same_physical_usb_port": True}:
        raise cp.Refusal("N1 fastboot physical match not confirmed")
    sub = out / "fastboot"; sub.mkdir(exist_ok=False)
    write_json(sub / "supervision.json", supervision)
    result = {"complete": False, "stop": None, "records": [], "plan_sha256": approval["plan_sha256"],
              "profile_sha256": approval["profile_sha256"], "monotonic_start": time.monotonic(),
              "utc": datetime.now(timezone.utc).isoformat(), "native_sha256": FASTBOOT_SHA256}
    try:
        for i, variable in enumerate((None,) + VARIABLES):
            deadline(pre["monotonic_start"])
            host_guard()  # Read-only host USB/server/native-image continuity.
            if cp.sha(Path(FASTBOOT).read_bytes()) != FASTBOOT_SHA256: raise cp.Refusal("fastboot executable changed")
            args = argv(profile["binding"]["serial"], variable)
            rec = {"argv": args, "variable": variable, "utc": datetime.now(timezone.utc).isoformat(),
                   "monotonic_start": time.monotonic(), "complete": False}
            result["records"].append(rec)
            raw = capture(launcher(args), min(limit, rec["monotonic_start"] + 5))
            rec.update({k: raw[k] for k in ("exit", "status", "cleanup_complete")})
            for name in ("stdout", "stderr"):
                filename = f"{i:02d}-{name}.bin"
                with (sub / filename).open("xb") as f: f.write(raw[name])
                rec[name] = {"file": filename, "bytes": len(raw[name]), "sha256": cp.sha(raw[name])}
            rec["monotonic_end"] = time.monotonic()
            if raw["status"] != "ok": raise cp.Refusal(raw["status"])
            if variable is None:
                serial = profile["binding"]["serial"]
                if raw["stderr"] or not re.fullmatch(re.escape(serial.encode()) + rb"[ \t]+fastboot(?:[ \t]+[!-~]{1,512})?\r?\n", raw["stdout"]):
                    raise cp.Refusal("ambiguous/changed fastboot enumeration")
            else:
                rec["value"] = value(variable, raw["stdout"], raw["stderr"])
            host_guard()
            rec["complete"] = True
        result["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        result["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        result["monotonic_end"] = time.monotonic()
        write_json(sub / "manifest.json", result)
    return result


def verify_return(approval, profile, output, owner_normal, *, connector=None):
    admit(approval, profile, output)
    out = Path(output)
    pre = cp.load_json(out / "pre-entry/manifest.json")
    fb = cp.load_json(out / "fastboot/manifest.json")
    if (not fb["complete"] or owner_normal is not True
            or fb["plan_sha256"] != approval["plan_sha256"]
            or fb["profile_sha256"] != approval["profile_sha256"]
            or len(fb["records"]) != 7 or not all(r["complete"] for r in fb["records"])):
        raise cp.Refusal("N1 return requests forbidden after failure or without owner confirmation")
    sub = out / "post-return"; sub.mkdir(exist_ok=False)
    s = IdentitySession("N1-post", sub, connector or ar.connect_existing, threading.Event(), pre["monotonic_start"])
    s.cap -= pre["wire_bytes"]
    m = s.manifest
    m.update(N1_plan_sha256=approval["plan_sha256"], original_profile_sha256=approval["profile_sha256"])
    try:
        if s.query("host:version", "version") != ar.VERSION: raise cp.Refusal("incompatible_server")
        binding, attrs = ar.inventory(s.query("host:devices-l", "inventory"))
        if binding["serial"] != profile["binding"]["serial"] or attrs.get("device") != "icx1301":
            raise cp.Refusal("returned identity mismatch")
        s.usb(binding["transport_id"])
        returned = json.loads(cp.canonical(profile)); returned["binding"] = binding
        cp.expected_profile(returned)
        s.profile = returned
        m["session_return_profile"] = returned
        s.track(binding["serial"])
        identity_loop(s, returned)
        m["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        m["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        s.close(); write_json(sub / "manifest.json", m)
    return m


if __name__ == "__main__":
    print(json.dumps({**plan(), "plan_sha256": cp.sha(cp.canonical(plan()))}, indent=2))
