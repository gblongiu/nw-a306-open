# M10: reconciled fastboot evidence and proposed N1

Subsequent execution: [N1 physical results](m10-n1-results.md). The authorized
reordered run stopped at an empty bootloader-version response, without querying
is-userspace. The owner supplied photographs of fastboot and Android return.
The original draft/reconciliation below remains historical evidence.

2026-10-15. Offline reconciliation only; no player communication, executable
invocation, reboot or bootloader request occurred. N1 is **proposed, not
authorized or executed**. It replaces the unexecuted M1 menu-discovery proposal.

Later 2026-10-15 execution instruction: the owner explicitly authorized N1 with
the sole diagnostic-order change **version-bootloader before is-userspace**.
The table below reflects that approved order. Execution remains conditional on
offline integration tests, unchanged identity/host prerequisites and fresh
physical readiness confirmation immediately before entry. The earlier draft,
original report and its digest are preserved privately; no other scope expands.

## Evidence located and its limits

The original M0 human brief, lines 75-80, already states locked/secure boot,
working ADB/fastboot, `flashing get_unlock_ability` returning `unknown command`,
and successful return to Android. The unchanged M0 source register,
`docs/feasibility.md:52`, labels this D2 and explicitly notes the missing query
transcript. The newer M10 assessment failed to carry that evidence forward.

The original M0 attachment was located, copied privately byte-for-byte and
hashed. The preserved **input history**, Windows PowerShell PSReadLine
`ConsoleHost_history.txt`, supplies these exact locators; serials remain private:

| History lines | Preserved command evidence |
| --- | --- |
| 40459-40465 | Targeted ADB state query, host fastboot version, targeted ADB bootloader reboot and fastboot enumeration. |
| 40772-40780 | Targeted product, unlocked, current-slot, secure and unlock-ability queries. |
| 40784-40792 | A `getvar all` capture into a variable, filtering including `is-userspace` and `version-bootloader`, followed by reboot. No saved output filename appears. |
| 40797-40804 | Fastboot enumeration, another filtered `getvar all`, another reboot. |
| 40808-40825 | ADB/fastboot and Windows USB checks. |

History proves which input strings were recorded, not successful execution,
reply values, chronology by timestamp or return status. It contains no command
outputs. The original project chat also preserves the M0 brief-reading command;
that output is the brief, **not a captured fastboot session**.

A bounded local search decoded 1,211 text files, including UTF-16 evidence, and
indexed twelve original research ZIPs for bootloader/transcript members. No
original fastboot reply transcript was found there. The device-evidence folder
is empty; D1 is Android property/partition-name evidence, not fastboot output.
One oversized updater-disassembly text was excluded. Source trees were excluded
as non-session material. This is not a claim that no transcript exists anywhere
in external chats or other archives. Search scope, hashes, exact private history
excerpts and original brief are in ignored
`build/m10/fastboot-reconciliation-20261015-01/`.

## Corrected physical findings

Classification throughout this table: **historical physical NW-A306 observations
attested by the owner; original command/output transcripts unavailable in the
reviewed evidence**. Matching input history is corroboration, not independent
verification of the outcomes. No historical date, client version or exact
firmware build is inferred from the current build.

| Owner-reported observation | Engineering consequence and limit |
| --- | --- |
| Targeted `adb reboot bootloader` entered fastboot; enumeration identified the same unit. | Physical fastboot access is observed, not merely a generic Qualcomm or public-report hypothesis. The exact early-loader versus fastbootd implementation remains unclassified. |
| Product `icx1301`, unlocked `no`, secure `yes`, slot `b`. | Historical endpoint identity and reported security/slot state. Not a trust-chain dump or proof of every handler's authentication. |
| `flashing get_unlock_ability`: remote `unknown command`. | That exact command was unsupported in the observed endpoint. It is not proof that every unlock, OEM or engineering interface is absent; no alternatives are authorized for probing. |
| `fastboot reboot`: `Write to device failed (no link)`. | Reliable software return is not established. Do not classify this as a Sony remote policy rejection or retry reboot as routine cleanup. |
| Approximately ten-second Power hold returned Android, subsequently seen by ADB. | One historical same-unit availability return succeeded. Not a guaranteed exit from every mode or repair after corrupted firmware, and not a measured exact timing contract. |

The current user report adds the specific responses and return mechanism beyond
the shorter original D2 brief. Existing fresh locked/green Android observations
are consistent but do not retrospectively verify the fastboot responses.

## Source analysis that changes the next experiment

Bounded pinned `android-14.0.0_r1` sources were acquired without execution.
They establish **broader-platform behavior, not the installed Sony code or an
exact match to the historical Windows fastboot binary**:

- [`fastboot/README.md:121-130,171-195`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/README.md):
  getvar reads configuration; unknown variables can produce FAIL or legacy empty
  success. Under this protocol, `secure=yes` declares signature requirements for
  installing or booting images. This strengthens the expected authentication
  barrier but does not prove Sony checks every field or every RAM-boot handler.
- [`fastboot_driver.cpp:100-103,434-450`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/fastboot_driver.cpp):
  GetVar sends `getvar:<key>`. The write-failure diagnostic is emitted when the
  transport does not report the full command write, before response processing.
  A partial delivery or later device action cannot be excluded. The historical
  binary/USB trace is missing, so cable, driver, endpoint, timing and Sony policy
  cannot be distinguished from that message alone.
- [`fastboot.cpp:2367-2409`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/fastboot.cpp):
  the selected getvar branch displays a variable; it is separate from boot,
  download and reboot handling. Fixed getvar argument arrays contain none of
  those actions. This is source review, not a test of the installed executable.
- [AOSP fastbootd documentation](https://source.android.com/docs/core/architecture/bootloader/fastbootd#fastboot_commands):
  explicit `is-userspace=yes` identifies fastbootd; `no` reports bootloader
  fastboot. Unknown, empty or malformed output leaves classification unresolved.
  It must not be interpreted as `no`.

The already preserved AOSP init/BCB analysis in
[C1 results](m10-c1-results.md#offline-finding-affecting-boot-entry-design) remains
valid: bootloader-target reboot can write `bootonce-bootloader` to misc and fsync;
shared Sony kernel source also records reboot reasons. The successful historical
entry does not show whether this Sony wrote or cleared BCB/PMIC state. Repeating
entry is a consequential availability transition, not wholly volatile metadata.

## N1: exact proposed scope

Question: **what implementation does the already observed fastboot endpoint
report, and what loader version can anchor artifact research?** Prior known
variables are repeated only as identity/security guards. No `getvar all`, unlock
query retry, OEM query, partition access, payload, download, boot or flash.

Let `S` be the exact serial from the unchanged approved private owner binding;
never use a default device. Let `F` be the absolute existing `fastboot.exe` path
and SHA-256 recorded in private `host-tool-proposal-binding.json`. Both host ADB
and fastboot files were hashed without executing them; the historical fastboot
binary's identity remains unknown. Native commands below mean argument arrays
under bounded capture, not a PowerShell pipeline, string-built shell or PATH
lookup.

Prerequisites: fresh owner confirmation of responsive stock Android and no
update, pending restart, playback or transfer; usable Power button; adequate
battery (at least 50% on-screen, a conservative experiment threshold); owner
backups of needed personal data. Require the same host, trusted existing ADB
server/process/image, exact private identity, one physically controlled Sony,
stable USB connection and already working Windows driver. Any uncertainty stops
before entry; no server repair, driver installation or reconnection workaround.

Before entry, run the existing eleven fixed identity guards, each once:

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

They must exactly match the approved profile. Use existing no-lifecycle server
checks, continuous watch and same-connection serial/transport binding; no new
shell command or permissive baseline substitution. At the intentional transition
boundary only, dispatch **one** bound ADB service `reboot:bootloader` on the
selected transport. Its familiar CLI equivalent is `adb -s S reboot bootloader`;
do **not** launch that ADB CLI, whose lifecycle behavior is unsuitable here.
This new service requires focused offline integration before any future live
run; the current metadata adapter does not admit it. No generic transport rewrite
is needed or proposed.
Once dispatched, loss of the ADB link or acknowledgement leaves delivery/action
uncertain and never permits a repeat. The expected mode-change disconnect is
recorded at this explicit boundary; it does not relax pre-entry identity guards.

Allow at most 30 seconds for the expected USB transition. Observe Windows USB
arrival on the same physical port without issuing repair commands. Then invoke
`[F, "devices", "-l"]` once. Require exactly one fastboot entry with `S`, the
physically observed player's mode screen and matching physical USB port. ADB
transport IDs do not bind fastboot. A serial/product reply is not cryptographic
attestation; physical control and absence of another target are essential.

Run these six exact argument arrays in order, admitting the next only after
success and valid output:

| Array | Expected evidence / necessity |
| --- | --- |
| `[F, "-s", S, "getvar", "product"]` | Must report `icx1301`: identity guard. |
| `[F, "-s", S, "getvar", "unlocked"]` | Must report `no`: unchanged security guard. |
| `[F, "-s", S, "getvar", "secure"]` | Must report `yes`: unchanged security guard. |
| `[F, "-s", S, "getvar", "current-slot"]` | Must report `b`, consistent with Android `_b`: slot guard. |
| `[F, "-s", S, "getvar", "version-bootloader"]` | Nonempty bounded printable version: artifact/source matching lead; not a loader dump. |
| `[F, "-s", S, "getvar", "is-userspace"]` | Explicit `yes` or `no`: distinguishes endpoint class; the principal new observation. |

Native stdout and stderr are each capped at **4,096 bytes**, each invocation has
a **five-second deadline**, and the entire session has a **450-second deadline**.
Enumeration has the same limits. Capture both streams independently: fastboot
normally prints successful variables on stderr, so C1's empty-stderr rule does
not apply. Require exit zero, exactly one expected named value, and only reviewed
status/timing formatting; ambiguous INFO or extra values stop. Preserve all raw
bytes before interpretation. A metadata query can stall or expose a vendor bug;
no intentional partition writes or image transfer is involved.

Any nonzero exit, FAIL, timeout, empty/unknown variable, overflow, ambiguous
device, changed guard or transport loss stops **all further diagnostic queries**.
Do not retry, replace a variable, run a broad enumeration or use another driver.
Record the failing operation and partial evidence. A native-process termination
does not prove cancellation of a remote operation or complete durable logging.

## Return and failure handling are part of the proposed approval

Do **not** send `fastboot reboot`, `continue`, `reboot-bootloader`, recovery/EDL
entry or any menu action. For normal completion, or after a failure once the
player has left Android, the owner performs **one Power-only hold of roughly
ten seconds**, releases it, and waits up to two minutes without other keys.
This deliberately uses the same-unit historical availability return; it is
not a guaranteed repair path. If Android is already normal, do not reset it.
Do not interrupt any automatic update/write-progress screen: leave it alone
and stop for review. No repeated hold loop or alternative button combination.

After a failed diagnostic, record only the owner's observed return/UI response
and stop; no additional ADB/fastboot query is allowed in that failed session.
After all six queries succeed and the owner confirms normal responsive Android,
perform one fixed no-lifecycle rediscovery (`host:version`, `host:devices-l`,
`host:tport:usb`), then the same eleven identity guards once. The returned ADB
transport ID may legitimately differ across this approved transition: keep the
original profile unchanged, require the same serial and physical unit, and bind
the new ID only in this session's separate post-return record before the guards.
An absent device, changed identity/server or failed post-return guard stops.

Protect the evidence in a new exclusive ignored directory: command arrays,
UTC/monotonic times, deadlines, raw per-stream bytes, exit statuses, hashes,
host-tool/source/plan digests, pre/post binding records and private screen photos.
The draft registry is `approved:false`. Approval must bind this scope and the
reviewed implementation after synthetic admission/capture/failure tests. No
live runner has been implemented or executed in this reconciliation.

Risks: persistent reboot-control/reason changes, interruption of availability,
USB failure, or a boot loop whose cause/clearing is unknown. The Power hold and
Sony's [frozen-player restart guidance](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html)
support a bounded fallback, not its guaranteed success. No factory reset,
accepted reflash or original-board reconstruction has been demonstrated. This
proposal is **metadata-only while in fastboot, but not a read-only overall
session**, because it enters and exits a boot mode. Approving N1 means accepting
that specific unresolved availability risk; it does not authorize firmware or
boot-chain modification.

## How the result changes independent-Linux research

`is-userspace=no` makes the observed endpoint a reported early-loader interface
worth matching to authentic command-policy artifacts. `yes` redirects research
to recovery fastbootd and leaves independent early entry unresolved. An unknown
response stops the session and leaves classification open. A version string
narrows source/image searches but does not establish a binary match.

None of these outcomes proves RAM boot, unlock support, signature bypass,
accepted kernel/ramdisk/DT changes or survival after corrupting firmware.
`secure=yes`, interpreted under the protocol contract, weighs against assuming
an unsigned `fastboot boot` path. Authentic acceptance policy remains the next
execution gate; a complete loader dump is useful but not mandatory for N1.
Recovery still requires board-matched original images/layout, applicable
AVB/rollback state, preserved provisioning/calibration and an accepted surviving
repair mechanism. A successful Power-button return from intact stock firmware
establishes none of that repair coverage.

The authorization decision requested is **N1 only: one bound ADB bootloader
transition, the fixed identity/enumeration/six-getvar schedule, one physical
return attempt and conditional successful-session post-return verification**.
M1 is superseded. No new authorization or execution is inferred from this report.

Offline validation: **18 checks passed, zero failed** for preserved source/input
locators, source/tool hashes, draft scope, document links and preservation of
**1,647 prior inventoried files**, with intentional report edits covered by
byte-for-byte pre-edit copies. `git diff --check` passed. No live integration or
new firmware test is claimed; the full unit suite was not rerun for these
documentation changes. This increment changes only this report,
`docs/m10-boot-feasibility.md` and `docs/m10-c1-results.md`, plus ignored private
research/validation records. Existing code, evidence, denials and Git history
remain intact; M10 is not complete.
