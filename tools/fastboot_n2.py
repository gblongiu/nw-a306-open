# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed supervised N2 integration. Default CLI is inert plan output only."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import threading
import time

import fastboot_n1 as n1
import fastboot_n2_plan as scope

cp, ar = n1.cp, n1.ar
VARIABLES = ("product", "is-userspace")


def plan():
    p = scope.plan()
    p.update(stage="N2", live_backend=True,
             pre_transport_rule="same approved serial/physical USB; current server ID session-local; original profile immutable")
    p["code_sha256"][Path(__file__).name] = cp.sha(Path(__file__).read_bytes())
    return p


def admit(approval, profile, output):
    cp.expected_profile(profile)
    n1.ct.future_argv("uid", profile)
    cp.exact_keys(approval, ("approved", "stage", "plan_sha256", "profile_sha256", "output"))
    if (approval["approved"] is not True or approval["stage"] != "N2"
            or approval["plan_sha256"] != cp.sha(cp.canonical(plan()))
            or approval["profile_sha256"] != cp.sha(cp.canonical(profile))
            or approval["output"] != str(Path(output).absolute())):
        raise cp.Refusal("N2 approval/code/profile/output mismatch")


class IdentitySession(n1.IdentitySession):
    def make_policy(self, stage):
        return {"stage": stage, "wire_cap": cp.TOTAL_CAP, "session_ms": n1.SESSION_MS,
                "strict_stream_cap": True, "N2_plan": plan()}

    def allow(self, service):
        if service == "reboot:bootloader":
            if self.stage != "N2-pre" or not self.transition or self.entry_used:
                raise cp.Refusal("N2 entry not admitted or already attempted")
            self.entry_used = True
        else:
            ar.Session.allow(self, service)


def bind_current(session, approved):
    """Only ephemeral ID may change; serial/identity policy cannot change."""
    if session.query("host:version", "version") != ar.VERSION:
        raise cp.Refusal("incompatible_server")
    binding, attrs = ar.inventory(session.query("host:devices-l", "inventory"))
    if binding["serial"] != approved["binding"]["serial"] or attrs.get("device") != "icx1301":
        raise cp.Refusal("N2 current target mismatch")
    session.usb(binding["transport_id"])
    current = json.loads(cp.canonical(approved))
    current["binding"] = binding
    cp.expected_profile(current)
    session.profile = current
    session.manifest["session_profile"] = current
    session.track(binding["serial"])
    return current


def start(approval, profile, output, readiness, host_guard, *, connector=None):
    admit(approval, profile, output)
    cp.exact_keys(readiness, ("confirmed", "utc", "profile_sha256", "normal_idle", "power_ready", "battery_ready", "backups_ready"))
    if (any(readiness[k] is not True for k in ("confirmed", "normal_idle", "power_ready", "battery_ready", "backups_ready"))
            or readiness["profile_sha256"] != approval["profile_sha256"]):
        raise cp.Refusal("N2 owner prerequisites missing")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(readiness["utc"])).total_seconds()
    if not 0 <= age <= 120: raise cp.Refusal("N2 readiness not fresh")
    host_guard()
    out = cp.private_directory(output)
    for name, obj in (("approval.json", approval), ("owner-readiness.json", readiness), ("plan.json", plan())):
        n1.write_json(out / name, obj)
    sub = out / "pre-entry"; sub.mkdir()
    s = IdentitySession("N2-pre", sub, connector or ar.connect_existing, threading.Event(), time.monotonic())
    m = s.manifest
    m.update(expected_profile=profile, N2_plan_sha256=approval["plan_sha256"],
             profile_sha256=approval["profile_sha256"], approval_sha256=cp.sha(cp.canonical(approval)),
             entry_attempted=False, entry_acknowledged=False)
    try:
        current = bind_current(s, profile)
        n1.identity_loop(s, current)
        s.guard(current)
        host_guard()
        admit(approval, profile, output)
        if (datetime.now(timezone.utc) - datetime.fromisoformat(readiness["utc"])).total_seconds() > 120:
            raise cp.Refusal("N2 readiness expired before entry")
        with s.wire("bootloader-entry") as w:
            w.request("host:tport:serial:" + current["binding"]["serial"])
            if int.from_bytes(w.exact(8), "little") != int(current["binding"]["transport_id"]):
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
        s.close(); n1.write_json(sub / "manifest.json", m)
    return m


def argv(serial, variable=None):
    if variable is not None and variable not in VARIABLES:
        raise cp.Refusal("N2 variable not allowlisted")
    return n1.argv(serial, variable)


def launch(args):
    if args != [n1.FASTBOOT, "devices", "-l"]:
        if (not isinstance(args, list) or len(args) != 5
                or args != argv(args[2], args[4])):
            raise cp.Refusal("native command outside N2")
    return n1.launch(args)


def diagnose(approval, profile, output, supervision, host_guard, *, launcher=launch):
    admit(approval, profile, output)
    out = Path(output)
    pre = cp.load_json(out / "pre-entry/manifest.json")
    if not pre["complete"] or not pre["entry_acknowledged"] or pre["N2_plan_sha256"] != approval["plan_sha256"]:
        raise cp.Refusal("N2 entry failed or scope changed")
    limit = n1.deadline(pre["monotonic_start"])
    if supervision != {"same_unit_fastboot_screen": True, "same_physical_usb_port": True}:
        raise cp.Refusal("N2 fastboot physical match not confirmed")
    sub = out / "fastboot"; sub.mkdir(exist_ok=False)
    n1.write_json(sub / "supervision.json", supervision)
    result = {"complete": False, "stop": None, "records": [], "plan_sha256": approval["plan_sha256"],
              "profile_sha256": approval["profile_sha256"], "monotonic_start": time.monotonic(),
              "utc": datetime.now(timezone.utc).isoformat(), "native_sha256": n1.FASTBOOT_SHA256,
              "classification": "inconclusive", "post_return_guards_permitted": False}
    try:
        for i, variable in enumerate((None,) + VARIABLES):
            n1.deadline(pre["monotonic_start"])
            host_guard()
            if cp.sha(Path(n1.FASTBOOT).read_bytes()) != n1.FASTBOOT_SHA256:
                raise cp.Refusal("fastboot executable changed")
            args = argv(profile["binding"]["serial"], variable)
            rec = {"argv": args, "variable": variable, "utc": datetime.now(timezone.utc).isoformat(),
                   "monotonic_start": time.monotonic(), "complete": False}
            result["records"].append(rec)
            raw = n1.capture(launcher(args), min(limit, rec["monotonic_start"] + 5))
            rec.update({k: raw[k] for k in ("exit", "status", "cleanup_complete")})
            for name in ("stdout", "stderr"):
                filename = f"{i:02d}-{name}.bin"
                with (sub / filename).open("xb") as f: f.write(raw[name])
                rec[name] = {"file": filename, "bytes": len(raw[name]), "sha256": cp.sha(raw[name])}
            rec["monotonic_end"] = time.monotonic()
            if variable == "is-userspace":
                meaning = scope.classify_optional(variable, raw["stdout"], raw["stderr"], raw["exit"], raw["status"])
                rec["interpretation"] = meaning
                result["classification"] = meaning["classification"]
                if not meaning["post_return_guards_permitted"]:
                    rec["complete"] = meaning["state"] == "unsupported"
                    raise cp.Refusal("optional_" + meaning["state"])
                result["post_return_guards_permitted"] = True
            else:
                if raw["status"] != "ok": raise cp.Refusal(raw["status"])
                if variable is None:
                    serial = profile["binding"]["serial"]
                    if raw["stderr"] or not re.fullmatch(re.escape(serial.encode()) + rb"[ \t]+fastboot(?:[ \t]+[!-~]{1,512})?\r?\n", raw["stdout"]):
                        raise cp.Refusal("ambiguous/changed fastboot enumeration")
                else:
                    rec["value"] = n1.value("product", raw["stdout"], raw["stderr"])
            host_guard()
            rec["complete"] = True
        result["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        result["post_return_guards_permitted"] = False
        result["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        result["monotonic_end"] = time.monotonic()
        n1.write_json(sub / "manifest.json", result)
    return result


def verify_return(approval, profile, output, owner_normal, host_guard, *, connector=None):
    admit(approval, profile, output)
    out = Path(output)
    pre = cp.load_json(out / "pre-entry/manifest.json")
    fb = cp.load_json(out / "fastboot/manifest.json")
    if (not fb["complete"] or owner_normal is not True or not fb["post_return_guards_permitted"]
            or fb["plan_sha256"] != approval["plan_sha256"] or fb["profile_sha256"] != approval["profile_sha256"]
            or len(fb["records"]) != 3 or not all(r["complete"] for r in fb["records"])):
        raise cp.Refusal("N2 return queries not permitted")
    last = fb["records"][-1]
    expected = [argv(profile["binding"]["serial"])] + [argv(profile["binding"]["serial"], v) for v in VARIABLES]
    if [r["argv"] for r in fb["records"]] != expected:
        raise cp.Refusal("N2 captured scope mismatch")
    saved = {}
    for name in ("stdout", "stderr"):
        item = last[name]
        p = out / "fastboot" / f"02-{name}.bin"
        if item["file"] != p.name or p.is_symlink() or p.stat().st_size > 4096:
            raise cp.Refusal("N2 saved response path/size mismatch")
        saved[name] = p.read_bytes()
        if len(saved[name]) != item["bytes"] or cp.sha(saved[name]) != item["sha256"]:
            raise cp.Refusal("N2 saved response integrity mismatch")
    meaning = scope.classify_optional("is-userspace", saved["stdout"], saved["stderr"], last["exit"], last["status"])
    if not meaning["post_return_guards_permitted"]: raise cp.Refusal("N2 return outcome mismatch")
    n1.deadline(pre["monotonic_start"])
    host_guard()
    sub = out / "post-return"; sub.mkdir(exist_ok=False)
    s = IdentitySession("N2-post", sub, connector or ar.connect_existing, threading.Event(), pre["monotonic_start"])
    s.cap -= pre["wire_bytes"]
    m = s.manifest
    m.update(N2_plan_sha256=approval["plan_sha256"], original_profile_sha256=approval["profile_sha256"])
    try:
        current = bind_current(s, profile)
        n1.identity_loop(s, current)
        host_guard()
        m["complete"] = True
    except (cp.Refusal, OSError, KeyboardInterrupt) as exc:
        m["stop"] = str(exc) if isinstance(exc, cp.Refusal) else type(exc).__name__
    finally:
        s.close(); n1.write_json(sub / "manifest.json", m)
    return m


if __name__ == "__main__":
    p = plan()
    print(json.dumps({**p, "plan_sha256": cp.sha(cp.canonical(p))}, indent=2))
