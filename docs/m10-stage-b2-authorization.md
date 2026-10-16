# M10 Stage B2 metadata authorization packet

2026-10-14. **Prepared and tested offline; execution is not authorized.**
The physical Stage B failure remains intact. This packet proposes a new fixed
scope, not a retry, continuation or silent skip of that failed session.

## Engineering question and acceptance criteria

Can the already identified, locked stock NW-A306 supply narrow bootloader,
updater and registered-hardware metadata that identifies the next authentic
boot/recovery artifact or Sony driver investigation without tree-content access?

B2 must use exactly 33 observations: eleven initial identity checks, eleven
metadata observations below, then the same eleven identity checks. Every
observation requires before/after transport guards, complete binary stdout and
stderr with valid exit status, and the existing deadlines and byte limits.
Only completion of all 33 can mark B2 complete. Any failure preserves a partial
session and stops; successful earlier observations remain individually bounded
evidence. Even full completion would not establish native boot or recovery.

Implementation is limited to a constant registry in
`tools/characterization_b2.py` and stage selection in `tools/adb_readonly.py`.
No transport, retry, socket, authentication or capture mechanism was added.
There is no runtime operation selector or supplied remote command.

## Preconditions, identity and execution entry

Before any execution, renew the owner's confirmation of the same physical
unit/cable, normal responsive stock Android, already enabled/authorized USB
debugging, and no update, playback or file transfer. Require a single USB player
and no other ADB transport. Do not change settings, accept prompts, reconnect
the device or start/restart ADB to meet these conditions.

Require the existing trusted server on BEAREAB-PC at IPv4 `127.0.0.1:5037`.
Recheck its listener owner, process image and file hash locally against the
private Stage B preflight. The previously verified image is
`C:\Users\dante\AppData\Local\Android\platform-tools\adb.exe`, SHA-256
`56656270da132f44e9cb4fb86a12ba965635c80423d43dcdd944d9fec4ab4622`.
Do not execute it. If server continuity, provenance, device identity or any
precondition is uncertain, stop. Do not refresh a stale binding automatically;
renewed discovery would need its own explicit scope. A smart socket does not
cryptographically authenticate its local server or prove an epoch across the
approval gap; process checks and the held tracker bound, not eliminate, that risk.

Reuse the existing private profile
`build/m10/authorizations/expected-nwa306-20261014-01.json` unchanged. Its serial
and nonzero transport ID are private. One online transport, the exact saved
binding and these physically observed initial/ending values are required:

| Indices at start / end | Exact remote command | Required output before terminal newline |
| --- | --- | --- |
| 00 / 22 | `/system/bin/id -u` | `2000` |
| 01 / 23 | `/system/bin/id -Z` | `u:r:shell:s0` |
| 02 / 24 | `/system/bin/getenforce` | `Enforcing` |
| 03 / 25 | `/system/bin/getprop ro.product.model` | `NW-A300Series` |
| 04 / 26 | `/system/bin/getprop ro.product.device` | `icx1301` |
| 05 / 27 | `/system/bin/getprop ro.board.platform` | `bengal` |
| 06 / 28 | `/system/bin/getprop ro.soc.model` | `QCS2290` |
| 07 / 29 | `/system/bin/getprop ro.build.version.incremental` | `27` |
| 08 / 30 | `/system/bin/getprop ro.boot.slot_suffix` | `_b` |
| 09 / 31 | `/system/bin/getprop ro.boot.verifiedbootstate` | `green` |
| 10 / 32 | `/system/bin/getprop ro.boot.flash.locked` | `1` |

Each identity stream has a 4,096-byte cap. These property values are runtime
reports, not fuse attestation. A changed value stops; never replace the baseline
automatically or modify the device to match it. R1 risk below applies to each.

Proposed future host invocation, **not executed**:

```powershell
& 'C:\Users\dante\AppData\Local\Programs\Python\Python314\python.exe' `
  'C:\Users\dante\PycharmProjects\nw-a306-open\tools\adb_readonly.py' `
  --stage B2 --run-approved `
  --approval 'C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\authorizations\stage-b2-20261014-01.json' `
  --profile 'C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\authorizations\expected-nwa306-20261014-01.json' `
  --out 'C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\device-stage-b2-20261014-01'
```

The execution approval file and live output directory do not exist. The draft
`build/m10/b2-preparation-20261014-01/approval-pending.json` has `approved:false`
and was tested to refuse before connecting or creating the output. After human
authorization and successful preflight only, create a new execution approval
with the draft's exact stage, plan/profile digests and output, and `approved:true`.
Never reuse or edit Stage A/B approval/evidence files. A CLI invocation without
`--run-approved` only prints a plan; import/plan construction makes no connection.

## Exact metadata scope, order and risks

Caps apply independently to stdout and stderr; successful stderr must be empty.
For `head`, one extra sentinel byte is requested to reject oversized output.
The sentinel is never accepted as complete data; the utility can internally read
more than it emits. Directory listings are output-bounded rather than a promise
that the remote process internally visits only that many bytes.

Risks shared by all rows: diagnostic process/load/log/accounting effects, USB
charging effects, hangs/disconnects and incomplete evidence. No intentional
persistent Android configuration, firmware or filesystem writes are requested.

- **R1:** property/identity utility; no intended state mutation. Empty/generic
  reports may leave capability unknown; they are not unlock or boot permission.
- **R2:** package-manager Binder query can enumerate installed metadata, read
  storage and update accounting/logs internally. Filter bounds returned names,
  not internal enumeration. It does not launch the updater or inspect APK bytes.
- **R3:** registered proc metadata, with memory-backed callbacks audited in the
  original packet. No block, PCM or input-event target is opened. Input records
  can include private `Uniq` identifiers; raw output must remain private.
- **R4:** directory/inode/symlink metadata, including possible VFS work. No
  target block device, sysfs attribute, regulator or sensor is opened. Access
  remains unverified; a listing cannot establish functioning hardware.

| Index / ID | Exact remote command | Cap per stream | Why necessary / expected evidence and decision | Risk |
| --- | --- | --- | --- | --- |
| 11 bootloader-report | `/system/bin/getprop ro.bootloader` | 4,096 B | Loader-version lead for applicable local image/document matching. Blank/generic leaves identity unknown; a version string alone establishes no command support. | R1 |
| 12 unlock-report | `/system/bin/getprop ro.oem_unlock_supported` | 4,096 B | Empty/0/1 policy hint. 0/empty weakens this lead; 1 warrants implemented-policy research, never an unlock attempt or assumption of RAM boot. | R1 |
| 13 android-release | `/system/bin/getprop ro.build.version.release` | 4,096 B | Bind updater/platform reference applicability. Android release cannot determine Sony boot-header version or partition types. | R1 |
| 14 updater-candidates | `/system/bin/pm list packages --user 0 -s systemupdat` | 16,384 B | Narrow system/user-0 names containing `systemupdat`; a candidate identifies the next separately reviewed consumer-path acquisition. Empty excludes only this filter/user, not every updater. | R2 |
| 15 partitions | `/system/bin/toybox head -c 65537 /proc/partitions` | 65,536 B | Registered names and cached block counts select storage/layout research. No GPT/extents, partition contents, unique state or restoration coverage. | R3 |
| 16 sound-cards | `/system/bin/toybox head -c 65537 /proc/asound/cards` | 65,536 B | Registered Sony card/driver identities select machine-driver investigation. No playback, route, firmware or gain proof. | R3 |
| 17 sound-pcm | `/system/bin/toybox head -c 65537 /proc/asound/pcm` | 65,536 B | Registered playback/capture endpoints narrow independent ALSA startup dependencies. No PCM open, mixer access or functional test. | R3 |
| 18 input-devices | `/system/bin/toybox head -c 65537 /proc/bus/input/devices` | 65,536 B | Registered button/touch IDs, handlers and capabilities select driver/mapping work. No event sampling, wake or coordinate-range testing. | R3 |
| 19 graphics-names | `/system/bin/toybox ls -l /sys/class/graphics` | 16,384 B | Framebuffer names/links narrow stock display-stack ownership. Does not identify panel timing, DSI initialization or KMS capability. | R4 |
| 20 power-names | `/system/bin/toybox ls -l /sys/class/power_supply` | 16,384 B | Supply names/topology select charger/fuel-gauge ownership research. No battery values, thermal limits or charging-control tests. | R4 |
| 21 block-names | `/system/bin/toybox ls -l /dev/block/by-name` | 65,536 B | Current boot/recovery/DTBO/vbmeta naming and link targets narrow authentic artifact and recovery-dependency requests. No target opens. Last because device-node directory access is uncertain; no silent fallback. | R4 |

Boot/updater reports precede every peripheral inventory. `/proc/partitions`
provides an early storage observation; uncertain device-node link access is
deferred until after proc and class inventories. All unattempted accesses remain
**unknown**, including proc/class reads; this ordering is engineering judgment,
not a demonstrated Sony permission model. The Binder query stays early despite
its access uncertainty because the applicable updater consumer is the highest
value missing artifact lead.

Excluded entirely: `compatible` and `model` tree-content reads (including alias
workarounds); already observed kernel/tree-link; raw-FDT permission listing
(low acceptance value after the tree denial); regulator-instance listing
(does not establish consumer constraints or safety limits). Also excluded:
arbitrary package queries/paths, APK/firmware/calibration acquisition, cmdline,
bootconfig, raw FDT, raw partitions/GPT/EXT_CSD/ioctls, root/su/escalation,
settings/setprop/service changes, event/PCM/mixer/watchdog opens, mode transitions,
reboot, unlocking, flashing, erasing and partition/security-policy changes.

## Server services, bounds and failure handling

Unchanged reviewed adapter behavior:

1. `host:version`, require protocol 41 (`0029`). Hold `host:track-devices` and
   require exactly the saved serial in `device` state. `host:tport:usb` must
   return the saved nonzero transport ID; close without a daemon service.
2. Before and after every observation, `host:devices-l` must match the private
   single-device binding; `host-transport-id:T:features` must include `shell_v2`.
3. For each remote command R above, select `host:tport:serial:S`, require its
   returned transport ID T on that same connection, then `shell,v2,raw:R`.
   Send only shell-v2 close-stdin, no input, no PTY or fallback shell protocol.
4. Require separated stdout/stderr and one final one-byte exit packet, then EOF.

Full completion uses 168 connections and 33 shell services. Five-second
connection deadlines cover each guard/selection/shell connection; this is not
a five-second bound for all five connections of an observation combined.
The whole session has a 300-second deadline and 2 MiB combined transmitted and
received wire budget. Host replies are capped at 16,384 B; shell-frame count
at 4,096. Existing bounded tracker cleanup is unchanged. Host log I/O is not
guaranteed interruptible; closing a socket cannot prove remote cancellation.

Stop on any identity/transport/watch/server/protocol change, ambiguity, prompt,
denial, missing/unsupported path or command, nonzero exit, stderr, invalid payload,
timeout, disconnect, cancellation, byte limit or host I/O failure. Preserve raw
partial bytes and failure status. No retry, skip, alias workaround, escalation,
server restart or recovery/mode fallback follows. A different scope requires
another reviewed packet and explicit authorization. A watcher can detect change
after a read was dispatched; rejection does not undo that read.

Keep all raw binary frames, decoded streams, manifests, times, hashes, serials,
transport IDs and potentially private input identifiers under ignored
`build/m10/`. Publish only sanitized conclusions. Each operation's completion
flag requires its own successful guards; full completion additionally requires
the ending identity checks. No target network service or cloud component is used.

## Offline validation, digests and retained history

Canonical plan SHA-256 for this exact B2 implementation:
`2de22535e3536b27f95311b545f2da5e92f193cfa1ad8a313316c24f5288f427`.
The plan pins the operation definitions and SHA-256 of `adb_readonly.py`,
`characterization_b2.py`, `characterization_plan.py` and
`characterization_transport.py`. Any code/plan/profile/output change invalidates
the corresponding approval guard. The pending draft remains unapproved.

The adapter edit necessarily changes newly constructed A/B plan digests as well.
Their old authorization files and physical captures are historical evidence,
not reusable approvals for the edited code. Original adapter bytes and original
A/B plans were saved before editing under the private preparation directory.
The original offline replay/transport modules were not edited. No historical
capture, validation, manifest, hash, approval or private profile was rewritten.

Nine new fake-transport tests check the exact 33-operation registry, bookends,
caps/order, all excluded services/objects, stale/cross-stage/false approvals,
profile binding, schedule mutation, inert CLI, initial/ending identity failures,
atomic transport selection, and denial at each of eleven metadata positions.
The successful fragmented fixture records 168 connections with matching raw and
decoded hashes. Real socket/process constructors are blocked during fixtures.
Windows full discovery: **111 tests, 110 passed, one symlink-permission skip**.
WSL Ubuntu 24.04: **111 passed**. The pending real-profile draft was separately
rejected before connection; the proposed live output directory was not created.
None of these offline results establishes Sony access to a proposed B2 path.

Private plans, test logs, full fake capture, before/after preservation ledger,
pending approval and boot-evidence audit are under
`build/m10/b2-preparation-20261014-01/`.

## Feasibility decisions and authorization boundary

The [boot investigation follow-up](m10-physical-boot-investigation.md#b2-preparation-and-offline-boot-access-reassessment)
ties each acquisition lead to accepted-payload and original-board recovery
questions. An updater name could unlock analysis of the preserved opaque NWWM
package through later lawful consumer acquisition. A loader report could select
applicable implementation evidence. Partition names could change our model of
boot/recovery dependencies. Peripheral registrations could narrow stock-kernel
reuse requirements. None directly authorizes changed images or demonstrates a
restore procedure. A positive unlock property is not a viable boot method.

**Required decision:** explicitly authorize only this fixed Stage B2 sequence
for the previously confirmed physical unit and unchanged private profile,
subject to renewed preconditions, the exact digest, limits and stop rules above.
Preparation is complete; stop here. Authorization would cover these metadata
reads only, with no later acquisition, boot, write or recovery experiment.
