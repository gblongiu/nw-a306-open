# SPDX-License-Identifier: GPL-2.0-or-later
"""Offline-only N2 registry and optional-variable interpretation; no executor."""
from dataclasses import asdict
from pathlib import Path
import json
import re

import characterization_plan as cp
import fastboot_n1 as n1

OPTIONAL = ("version-bootloader", "is-userspace")
TIMING = re.compile(r"(?:Finished\. Total time:|finished\. total time:|total time:) [0-9]+\.[0-9]+s")


def plan():
    return {"stage": "N2-proposal", "approved": False, "live_backend": False,
            "pre_identity": [asdict(o) for o in cp.IDENTITY],
            "entry": {"service": "reboot:bootloader", "count": 1, "serial_transport_bound": True},
            "native_commands": [[n1.FASTBOOT, "devices", "-l"],
                                [n1.FASTBOOT, "-s", "S", "getvar", "product"],
                                [n1.FASTBOOT, "-s", "S", "getvar", "is-userspace"]],
            "product_guard": "icx1301", "optional_variable": "is-userspace",
            "native_sha256": n1.FASTBOOT_SHA256, "per_stream_cap": 4096,
            "operation_ms": 5000, "session_ms": 450000, "arrival_ms": 30000,
            "output_cap": 262144, "adb_wire_cap": cp.TOTAL_CAP, "retries": 0,
            "return": "owner Power-only hold approximately ten seconds once; wait up to two minutes; no update interruption",
            "post_discovery": ["host:version", "host:devices-l", "host:tport:usb"],
            "post_identity": [asdict(o) for o in cp.IDENTITY],
            "post_return_rule": "only explicit yes/no or empty named success plus owner-confirmed normal Android; no queries after remote FAIL or other error",
            "classification_rule": "explicit yes=fastbootd; explicit no=bootloader fastboot; empty/unsupported=inconclusive",
            "code_sha256": {Path(p).name: cp.sha(Path(p).read_bytes())
                            for p in (__file__, cp.__file__, n1.__file__, n1.ar.__file__, n1.ct.__file__)}}


def classify_optional(variable, stdout, stderr, return_code, capture_status="ok"):
    """Interpret saved native streams, never infer an unknown response is 'no'.

    Native output is not raw USB OKAY/FAIL framing. Recognized remote unsupported
    messages can have exit 0 with some clients; inspect content as well as exit.
    Malformed captures raise a protocol/capture refusal, not a hardware diagnosis.
    """
    if variable not in OPTIONAL: raise cp.Refusal("not an optional N2 analysis variable")
    if type(return_code) is not int or not 0 <= return_code <= 255:
        raise cp.Refusal("missing/invalid native exit status")
    if capture_status not in ("ok", "command_failed"):
        raise cp.Refusal("incomplete/failed capture")
    if any(not isinstance(b, bytes) or len(b) > 4096 for b in (stdout, stderr)):
        raise cp.Refusal("optional-variable stream limit/type")
    lines = []
    for raw in (stdout, stderr):
        try: text = raw.decode("ascii")
        except UnicodeError as exc: raise cp.Refusal("unsupported output encoding") from exc
        if any(ord(c) < 32 and c not in "\r\n" or ord(c) == 127 for c in text):
            raise cp.Refusal("unexpected output controls")
        lines.extend(l.strip() for l in text.splitlines() if l.strip())
    values, failures = [], []
    for line in lines:
        if TIMING.fullmatch(line): continue
        if line == "getvar:" + variable: continue  # AOSP separate status line.
        match = re.fullmatch(r"(?:\(bootloader\) )?" + re.escape(variable) + r":[ ]?(.*)", line)
        if match:
            values.append(match[1]); continue
        fail = re.fullmatch(r"(?:getvar:" + re.escape(variable) + r"[ ]+)?FAILED \(remote: '(unknown variable|unknown command|unsupported variable|GetVar Variable Not found)'\)", line, re.I)
        if fail:
            failures.append(fail[1]); continue
        raise cp.Refusal("unrecognized optional-variable output")
    if len(values) == 1 and not failures:
        if return_code != 0 or capture_status != "ok":
            raise cp.Refusal("named success contradicts native failure")
        val = values[0]
        if val.strip() != val or len(val) > 256:
            raise cp.Refusal("ambiguous optional-variable value")
        state = "unavailable" if val == "" else "available"
        classification = "inconclusive"
        post = val == ""
        if variable == "is-userspace":
            if val in ("yes", "no"):
                classification = "fastbootd" if val == "yes" else "bootloader-fastboot"
                post = True
            elif val != "":
                state = "unrecognized-value"
        return {"state": state, "value": val, "classification": classification,
                "hardware_failure_inferred": False, "post_return_guards_permitted": post}
    if len(failures) == 1 and not values:
        return {"state": "unsupported", "value": None, "classification": "inconclusive",
                "hardware_failure_inferred": False, "post_return_guards_permitted": False}
    raise cp.Refusal("missing/duplicate/contradictory optional-variable response")


if __name__ == "__main__":
    p = plan()
    print(json.dumps({**p, "plan_sha256": cp.sha(cp.canonical(p))}, indent=2))
