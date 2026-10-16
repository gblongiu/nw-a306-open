# M10 N2: one endpoint-classification observation

Execution update, 2026-10-15: the owner authorized this unchanged scope;
[N2 completed](m10-n2-results.md) with `is-userspace: no` and all eleven
post-return Android identity checks passing. The draft/preparation statements
below describe the preserved earlier checkpoint, not current execution status.
The command registry and execution guards were frozen throughout the session.

2026-10-15. **Proposed only; not authorized or executed.** No device, bootloader,
USB-transport or ADB-server request was issued in this preparation. The original
N1 raw capture, successful state observations, photographs and failure record
are preserved. The new registry has `approved:false` and no live backend.

Subsequent execution instruction: the owner explicitly authorized this N2 scope.
`tools/fastboot_n2.py` integrates it with the frozen N1 entry/capture mechanisms;
the original offline proposal remains unchanged. Execution requires completed
integration tests, current host checks and fresh owner readiness. ADB transport
IDs are ephemeral across N1's approved return: resolve the current ID only for
the same approved serial/physical USB unit, record it in N2's session profile,
and require atomic matching throughout. Preserve the original identity/profile
bytes. This clarifies transport revalidation; no diagnostic command is added.

## Reconciled N1 result and value of N2

**Physical evidence:** N1 reached FastBoot Mode, enumerated the bound unit and
returned product `icx1301`, unlocked `no`, secure `yes`, active slot `b`. Native
`version-bootloader` exited 0 with a named empty value. The owner subsequently
documented Android home-screen return following the approved physical procedure.
The nonempty-value policy caused N1's stop, not an observed loader malfunction.

**Reference source:** pinned AOSP `android-14.0.0_r1`
[`fastboot/README.md:121-130`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/README.md#121)
documents older empty OKAY behavior for unknown variables. Native output is
compatible with that or an unset version. It does not prove an unknown variable,
the loader's age, or raw OKAY bytes; no USB packet trace was acquired. Record
**version unavailable**. Neither the N1 validator nor its manifests are changed
to retroactively continue the experiment.

**Decision:** N2 is justified as one bounded classification observation. AOSP
[defines](https://source.android.com/docs/core/architecture/bootloader/fastbootd#fastboot_commands)
`is-userspace=yes` for fastbootd and `no` for bootloader fastboot. Pinned
[`variables.cpp:376-380`](https://raw.githubusercontent.com/aosp-mirror/platform_system_core/android-14.0.0_r1/fastboot/device/variables.cpp)
returns yes in standard fastbootd. Its
[`FastbootDevice` command map, lines 91-113](https://raw.githubusercontent.com/aosp-mirror/platform_system_core/android-14.0.0_r1/fastboot/device/fastboot_device.cpp)
does not register the boot-image `boot` verb; unknown commands are rejected at
lines 234-237. That makes endpoint class relevant to the independent-execution
investigation. These are platform facts, not proof of Sony's installed code.

| N2 optional response | Classification and next research target |
| --- | --- |
| Explicit `yes` | Reported fastbootd endpoint. Investigate Sony's applicable recovery/fastbootd dispatcher and how an independent early-loader entry would be obtained. Standard fastbootd's absence of a boot verb is a concrete reason not to treat this endpoint as a ready RAM-boot route. No new mode transition is included. |
| Explicit `no` | Reported bootloader endpoint. Prioritize the actual Sony loader's registered download/boot handler and its locked-state/authentication decisions. This does not prove the handler exists or accepts an image. |
| Empty success or explicit unsupported response | Inconclusive; no inference of `no`, hardware failure or impossibility. An empty reply differs from standard AOSP fastbootd's implementation, but Sony changes remain possible. Continue authentic artifact/policy research instead of probing more variable names. |
| Other value, malformed output, I/O error or timeout | Stop and preserve the record. No endpoint classification or hardware-failure diagnosis follows automatically. |

The earlier screen makes a bootloader endpoint plausible; N2 can provide a
direct self-report or a bounded inconclusive result. Self-report is not
cryptographic attestation. It neither acquires the loader nor resolves image
acceptance. Do not collect another version, download-size or unlock variable.

## Fixed proposed commands and supervision

Use the unchanged private owner profile. `S` is its exact serial; `F` is the
absolute existing fastboot.exe path and SHA-256 already bound for N1. Revalidate
both host images and the trusted existing ADB listener/process/image. No adb.exe
launch, server lifecycle operation, driver installation or repair/reconnection
workaround is permitted.
Retain N1's host check that there are no remembered network-fastboot targets:
the native enumeration command must not contact an unrelated network endpoint.

Fresh prerequisites are the same physical Sony on BEAREAB-PC, responsive stock
Android, already authorized debugging, no update/pending restart/playback or
transfer, on-screen battery at least 50%, needed personal data backed up, and
the owner present with a usable Power button. Confirm these together before
entry; reuse no stale readiness assertion.

**Pre-entry identity guards, once each and in this order:**

```text
/system/bin/id -u
/system/bin/id -Z
/system/bin/getenforce
/system/bin/getprop ro.product.model
/system/bin/getprop ro.product.device
/system/bin/getprop ro.board.platform
/system/bin/getprop ro.soc.model
/system/bin/getprop ro.build.version.incremental
/system/bin/getprop ro.boot.slot_suffix
/system/bin/getprop ro.boot.verifiedbootstate
/system/bin/getprop ro.boot.flash.locked
```

All must match the existing profile. Preserve N1's no-lifecycle server checks,
continuous pre-entry watch, unique USB unit, atomic serial/transport selection
and code/plan/profile hashes. At the reviewed transition boundary send exactly
one **`reboot:bootloader`** service on that bound ADB transport. Its human-readable
equivalent is `adb -s S reboot bootloader`, but the ADB CLI must not be launched.
Lost acknowledgement is uncertain delivery, not permission to resend.

Allow at most 30 seconds for USB re-enumeration on the same physical port.
Require the owner's current FastBoot screen match; do not assume ADB transport
IDs bind fastboot. Then invoke these exact native argument arrays once:

```text
[F, "devices", "-l"]
[F, "-s", S, "getvar", "product"]
[F, "-s", S, "getvar", "is-userspace"]
```

Enumeration must contain one target with S; product must be exactly `icx1301`.
Only these are repeated fastboot observations: they are identity/transport
safeguards. Android's existing profile guards already check locked/green state
and slot, so `unlocked`, `secure`, `current-slot` and the unavailable version
are not queried again. No `getvar all`, OEM, unlock-ability, fetch, download,
boot, flash, erase, slot change, recovery/EDL or software reboot.

Each stdout/stderr stream remains capped at **4,096 bytes**, each operation at
**five seconds**. Whole-session deadline: **450 seconds**, not extended during
human pauses. Application-output ceiling: **262,144 bytes**; ADB-wire ceiling:
**2 MiB**. Native successes may print on stderr. Capture before interpretation,
including exit, timing, argument arrays, byte lengths and SHA-256. Host USB,
server epoch/image and native-file continuity must hold; any uncertainty stops.

Per-operation risks: the eleven stock-shell identity reads add short process,
logging and USB load; entry can persist reboot-control state and remove Android
availability; enumeration observes host interfaces; the two getvars issue
metadata requests but can encounter vendor bugs or hangs; the physical return
can fail to restore availability. Conditional post-return identities carry the
same bounded-read risks. No intended image/partition write is part of any step.

## Optional outcomes, return and stop rules

`is-userspace` is the last diagnostic. No retry, alternate name or substitute
command follows any outcome:

- One explicit named `yes`/`no` with successful bounded capture gives the
  corresponding reported class.
- One named **empty** value with exit 0 is a completed but inconclusive optional
  observation. It is not a hardware fault and does not require another query.
- A well-formed remote unknown/unsupported-variable or command response is
  inconclusive, even if the native client exits 0. Terminate communication;
  native exit alone is insufficient. No post-return device query in this branch.
- Malformed/contradictory/extra output, invalid identity, timeout, overflow,
  native I/O failure, unexpected permission requirement or USB loss terminates
  communication. Record the error without assigning a hardware cause. No
  automatic retry, privilege change or repair.

Use the N1-proven **physical** return: one owner Power-only hold of approximately
ten seconds, release, and wait up to two minutes. If normal Android is already
present, do not reset it. Do not interrupt an update/write-progress screen. No
menu selection, alternate key chord, repeated hold, software reboot or other
mode. If Android does not return, stop for review and do not improvise recovery.

For successful `yes`/`no` **or named empty exit-0** outcomes only, after the owner
confirms responsive stock Android, permit one fixed no-lifecycle rediscovery
(`host:version`, `host:devices-l`, `host:tport:usb`) followed by the same eleven
identity guards above. Bind any new ADB transport ID only in the private session
return record, requiring the same serial/physical port and unchanged identity;
never replace the original expected profile. Any failure stops. For unsupported
or erroneous optional outcomes, verify return through the owner/UI only and
issue no further device request, as in N1's stopped branch.

## Risks, evidence and authorization boundary

The entry can persist BCB/PMIC reboot reasons and normal startup may affect logs
or counters. Query bugs, USB loss and prolonged unavailability remain possible.
One observed intact-stock physical return does not guarantee the next return or
repair corrupted firmware. Same-board firmware restoration remains unproved.
This session is metadata-only in fastboot but includes a boot-mode transition;
it is not wholly volatile or part of the standing U1/H1 permission.

Use a new exclusive ignored capture directory. Pin the original profile,
reviewed code/plan, native binaries and host/port evidence; preserve raw streams,
partial/error records, owner observations and hashes. Keep identifiers and
photos private. Do not overwrite N1 or regenerate its raw manifest. The N2
registry and optional interpreter are offline only; no executable adapter or
approval record exists. Focused integration/failure tests and a new fixed live
digest are required before any later execution under the approved scope.

**Approval requested:** one supervised N2 session containing the fixed eleven
pre-entry identities, one serial-bound entry, enumeration, product guard, one
optional `is-userspace` query, the single physical return, and the conditional
post-return verification specified above. No other operation is implied.

## Next investigation of actual independent boot acceptance

The next substantive question is **whether the locked Sony execution component
registers a temporary `boot` handler, and what it authenticates before handoff**.
An endpoint flag, a download buffer or a trusted stock kernel cannot answer it.

The concrete offline target is the applicable Sony OS-loader executable or, if
N2 reports fastbootd, its actual recovery fastboot dispatcher together with the
early loader. Trace command registration to boot/download handlers, locked-state
checks, image-signature/AVB calls, kernel/ramdisk/DT/command-line coverage, and any
rollback/boot-control writes. Resolve delegated trust checks, not just strings.
Use the acquired RB1/QCM2290 LinuxLoader only as a disassembly/source comparison
model; its signed-image hashes and locked-boot diagnostic do not establish Sony
policy. A matched handler path is the acceptance evidence sought.

The missing input is still authentic Sony loader/selected boot evidence: the
encrypted official package and updater APK do not presently supply that image.
N2 may narrow which binary is needed but cannot manufacture it. No extra Android
metadata query is a substitute. Revisit artifact acquisition only against a
specific consumer/member or authenticated boot-policy relationship, not another
NWWM-wrapper study or a donor requirement.

Once a Sony-supported temporary interface, accepted image format/trust policy,
build-matched kernel/DT and failure/return coverage are established, the decisive
separately authorized experiment would be a minimal independent Linux initramfs
with an unmistakable local marker, no Android init/services and reviewed storage,
watchdog and power behavior. Observing that marker and independent userspace
would establish actual execution. It is **not proposed for execution now**:
authentic payload inputs and adequate recovery coverage are missing. Rejection
would narrow the particular handler/image hypothesis, not prove every execution
route impossible. No dummy image, unsigned-header probe or UpdateEngine call is
an innocuous substitute; each can alter device state.

## Offline validation completed

`tools/fastboot_n2_plan.py` contains only the fixed proposal and a pure saved-
output interpreter. It has no live backend or subprocess/socket entry point.
It classifies the original N1 version streams as unavailable without changing
the raw record or old validator. Seven new tests check the minimal registry,
digest sensitivity, explicit yes/no, legacy empty success, unsupported replies
with native exit 0 or 1, ambiguity, transport/permission errors and strict bounds;
real processes/sockets are blocked in these tests. The full suite ran **190
tests: 189 passed, one existing Windows symlink skip**. N1's implementation and
capture are unchanged. Source/provenance, preservation and document checks are
recorded privately with the proposed plan/profile digests; no N2 approval was
generated and no device operation occurred.
