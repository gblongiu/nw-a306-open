# NW-A306 final device authorization packet

2026-10-14. **Host adapter implemented and tested entirely offline. No device
interaction or live-server connection has occurred. Neither stage is authorized.**
Stage A and Stage B require separate explicit human approvals.

## Preconditions and approved execution mechanism

Use the human's physical Sony NW-A306, already connected by USB, normally booted
and responsive in stock Android with USB debugging already enabled/authorized.
Require one player and no other ADB transport. Human confirmation must establish
which physical unit/cable is present. No update, playback or file transfer should
be underway. Do not change settings, accept prompts, reconnect, or alter audio,
charging or radio state to satisfy these prerequisites; stop if uncertain.

An **already-running trusted local ADB server** at IPv4 `127.0.0.1:5037` is
required. `tools/adb_readonly.py` connects directly to it. It never launches an
ADB executable, subprocess or daemon and sends no lifecycle/reconnect service.
No installed ADB client hash is needed for execution. Server absence, refusal,
wrong protocol version or unavailable required services produces a private
failure manifest and stops without starting/restarting anything.

The supported server protocol is version 41 (`0029`) with `tport` selection and,
for Stage B, `shell_v2` and `track-devices`. Unsupported behavior is a stop, not
a fallback. The tested host layouts are little-endian Windows and WSL; other
endianness is refused. Plan construction/module import perform no communication.

Historical D1 comparison expectations, not current observations: model
`NW-A300Series`, device `icx1301`, platform `bengal`, SoC `QCS2290`, build `27`,
slot `_b`, verified state `green`, locked `1`. Historical source SHA-256:
`af61015a3302e62b6ceaa7e6660ae8d8dbf356ce462263b97d4037909bca8496`.
Require UID `2000`, context `u:r:shell:s0`, SELinux `Enforcing`. The human approves
these comparison values; changed reports stop and require review, not automatic
baseline replacement. Properties and server metadata are not cryptographic
attestation.

Host entry point `P` is
`C:\Users\dante\AppData\Local\Programs\Python\Python314\python.exe`;
script `C` is
`C:\Users\dante\PycharmProjects\nw-a306-open\tools\adb_readonly.py`.
Use argument arrays with no host shell. Private paths below are proposed new
paths, not existing approval files. No approval record has been generated.
Plan output is inert: `[P, C, "--stage", "A"]` or the corresponding `"B"`.
The approval JSON must have exactly `approved`, `stage`, `plan_sha256`,
`profile_sha256`, `output`; `approved` must be true, the plan/code digest must
match, and output must match the absolute new directory. A records null profile
hash; B records the SHA-256 of canonical expected-profile JSON. The record is
an accidental-execution guard, not proof of consent: it may be created only
following the human's explicit stage/session authorization. Its bound exclusive
output directory prevents reuse; no retry or changed directory is implicit.

Confirm sufficient host disk space. Keep all outputs under ignored `build/m10/`.
The OS/filesystem may stall or fail; partial manifests are best effort, not a
promise of durable recovery evidence.

## Stage A: discovery only, separate approval

Proposed exact host argument array:

`[P, C, "--stage", "A", "--run-approved", "--approval", "C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\authorizations\stage-a-20261014-01.json", "--out", "C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\device-stage-a-20261014-01"]`

Exact server request sequence, three connections:

1. `host:version`: verify length-framed response `0029`; no automatic repair of
   absent or incompatible server. Files `000-version.tx.bin` and `.rx.bin`.
2. `host:devices-l`: at most 16,384 response bytes; require exactly one online
   serial and canonical positive uint64 transport ID, with reported
   `device:icx1301`. Files `001-inventory.tx.bin` and `.rx.bin`.
3. `host:tport:usb`: require `OKAY` plus the same eight-byte native little-endian
   transport ID. This confirms the server-selected unique USB transport, including
   hosts that omit USB path text. No daemon/shell service follows this selection.
   Files `002-usb-selection.tx.bin` and `.rx.bin`.

Smart-socket requests use four ASCII hex length bytes followed by the named
service; replies require `OKAY` or bounded `FAIL`. No device-shell command,
property, partition or user file is read in A. All wire bytes are private and
SHA-256 inventoried in `manifest.json`, with timestamps, lengths, exact requests
and outcome. Network limits: five seconds per connection, 20 seconds total,
65,536 transmitted plus received bytes (a received overrun sentinel is failure).

Serial/model/path disclosure and existing-server discovery/logging effects are
possible. USB may already affect charging. Offline/unauthorized/multiple/absent
or unexpected transport, missing identity, mismatched USB ID, malformed response,
connection loss, deadline, cancellation or limit violation stops immediately.
Do not handle prompts, reconnect or start a daemon.

A successful result supplies a **candidate** private serial/ID binding. The
human must match it to the physical player. A alone establishes neither actual
Android property identity nor custom boot or recovery. Stop after reporting A;
there is no transition into B under Stage A approval.

Stage A plan/code digest:
`b05e6748c9c84e2164c3dce29a4588e83e7fb0c6405e52ccdb1e30aaf62f7ae5`.

## Stage B: fixed read-only characterization, separate approval

After successful A and human unit matching, prepare a private expected profile
with `binding` (serial S, nonzero transport ID T, state device, count 1) and the
11 exact identity expectations in rows 00-10 below. Existing tests show its
schema; no genuine profile exists yet. Approve its canonical hash, the full
39-row schedule, plan/code hash and one output directory. A smaller selection
requires a revised reviewed plan; this runner does not silently omit rows.

Proposed exact host argument array:

`[P, C, "--stage", "B", "--run-approved", "--approval", "C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\authorizations\stage-b-20261014-01.json", "--profile", "C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\authorizations\expected-nwa306-20261014-01.json", "--out", "C:\Users\dante\PycharmProjects\nw-a306-open\build\m10\device-stage-b-20261014-01"]`

Exact protocol order:

1. `host:version` verifies `0029`.
2. Hold `host:track-devices` open. Require initial `S\tdevice\n`. Any later
   notification, EOF or error invalidates the session, even an identical update.
3. `host:tport:usb` returns T; no shell follows this selection.
4. For each row in order, before and after its shell operation query
   `host:devices-l` (same single S/T/online state), then
   `host-transport-id:T:features` (must include shell_v2).
5. For the row's actual shell, open a new connection and send
   `host:tport:serial:S`; require returned ID T **on that same connection**.
   Only then send `shell,v2,raw:` followed by the exact constant R in the table.
   Send shell-v2 close-stdin frame `04 00000000`; never send input, allocate a
   terminal or accept legacy/raw unframed output.
6. Require separate framed stdout (ID 1), stderr (ID 2), one-byte exit (ID 3),
   then clean EOF. Unknown channels, bad sizes, missing/duplicate exit or trailing
   data stop. Any stderr or nonzero exit stops; no command is retried.

Wire requests are generated only from the fixed registry and approved S/T;
returned strings/links never become new commands. There is no public arbitrary
service, shell-string, endpoint, retry or fallback CLI option.

Connection indices are deterministic: 000 version, 001 transport-watch, 002 USB;
for row i, indices 003+5i inventory-before, 004+5i features-before, 005+5i shell,
006+5i inventory-after, 007+5i features-after. Actual files are
`INDEX-LABEL.tx.bin` and `.rx.bin`, with labels `inventory`, `features`, or
`shell-NN`; all exact names/requests, byte counts, hashes and times are in the
manifest. Decoded row outputs use `NN-stdout.bin`/`NN-stderr.bin`. Each connection
is journaled, including failed selections and raw shell-v2 headers/status.

Limits: 198 connections maximum, five seconds per connection, five-minute total
network deadline, at most 2 MiB of **all transmitted and received wire bytes**.
Host replies/FAIL text are capped at 16,384 bytes; shell decoded stream caps are
in the table, with at most 4,096 frames per command. An overrun prefix is never
accepted as complete. Tracker cleanup has a 0.3-second join allowance. Closing
our sockets is the only cancellation action; it cannot guarantee remote process
termination. Filesystem I/O cannot be given an absolute time guarantee.

Stage B plan/code digest:
`9a2a9b54b78a681021ab516ac340466b941c0f472240010353063f8bcae6418e`.

## Proven limitations and approval scope

The local smart-socket protocol does not authenticate the server process or
expose a durable epoch across separate A/B sessions. Trust in the pre-existing
local server is a prerequisite. Confirm no known restart/reconnect since A;
B revalidates S/T and all identity reports instead of claiming durable continuity.
The held tracker detects changes during B; guards on separate sockets are not
atomic with that tracker. A read already dispatched when a change is detected
may still run. Its session is rejected, evidence is marked incomplete as
appropriate, and no retry or restoration action follows. Serial selection plus
returned ID on the command connection prevents an ID reused for another serial
from selecting that unit. It cannot defeat spoofed identities from a malicious
local server or device.

No physical compatibility/accessibility has been proven. Unsupported services
on the actual server produce a stop with exact private evidence, not permission
for another implementation, privilege change or boot mode. These limits do not
prevent a separately approved discovery attempt. They do prevent claims of
attestation, recoverability or zero operational risk.

## Ordered B operations

All rows require ordinary shell UID 2000 with existing DAC/SELinux permission;
none requests elevation. Five-second capture deadline per operation; cleanup
allowance is specified below. Column NN determines
exclusive `NN-stdout.bin` and `NN-stderr.bin`, raw binary byte counts and
SHA-256 in `manifest.json`, with exact arguments, timestamps, exit, guards and
completion. Removing a row changes the schedule/digest and output indices;
approve the final exported indices, not an altered copy of this table.

Every row is a read request, **not a guarantee of zero state effects**. R1:
process/diagnostic/log/accounting effects; R2: kernel metadata locks and private
names/paths/identifiers; R3: package/Binder-service work/logging; R4: directory,
inode and symlink metadata activity. USB connection can affect charging.
No returned link is opened. All permissions and availability remain unverified.

| NN / ID | Exact remote R / interface | Output type / per-stream maximum | Native deployment question / interpretation | Risk |
| --- | --- | --- | --- | --- |
| 00 uid | `/system/bin/id -u` | ASCII / 4,096 B | Require 2000 or stop before further requests | R1 |
| 01 context | `/system/bin/id -Z` | ASCII / 4,096 B | Require u:r:shell:s0; no privilege workaround | R1 |
| 02 selinux | `/system/bin/getenforce` | ASCII / 4,096 B | Require Enforcing; no policy changes | R1 |
| 03 ro.product.model | `/system/bin/getprop ro.product.model` | Property / 4,096 B | Match approved NW-A300Series expectation | R1 |
| 04 ro.product.device | `/system/bin/getprop ro.product.device` | Property / 4,096 B | Require icx1301 | R1 |
| 05 ro.board.platform | `/system/bin/getprop ro.board.platform` | Property / 4,096 B | Compare bengal; mismatch invalidates source applicability | R1 |
| 06 ro.soc.model | `/system/bin/getprop ro.soc.model` | Property / 4,096 B | Compare QCS2290; not ROM/fuse attestation | R1 |
| 07 ro.build.version.incremental | `/system/bin/getprop ro.build.version.incremental` | Property / 4,096 B | Compare approved build 27; change requires review | R1 |
| 08 ro.boot.slot_suffix | `/system/bin/getprop ro.boot.slot_suffix` | Property / 4,096 B | Compare approved _b; neither switch nor fallback test | R1 |
| 09 ro.boot.verifiedbootstate | `/system/bin/getprop ro.boot.verifiedbootstate` | Property / 4,096 B | Require green report; not authenticated-coverage proof | R1 |
| 10 ro.boot.flash.locked | `/system/bin/getprop ro.boot.flash.locked` | Property / 4,096 B | Require 1; no unlock request | R1 |
| 11 kernel | `/system/bin/uname -r` | Release text / 4,096 B | Bind vendor-kernel research; not final config/ABI proof | R1 |
| 12 tree-link | `/system/bin/readlink /proc/device-tree` | Path / 4,096 B | Require /sys/firmware/devicetree/base before tree reads | R4 |
| 13 compatible | `/system/bin/toybox head -c 4097 /proc/device-tree/compatible` | NUL string list / 4,096 B accepted | Selected board-family evidence can weaken reference-board assumptions | R2 |
| 14 model | `/system/bin/toybox head -c 4097 /proc/device-tree/model` | One NUL string / 4,096 B accepted | Board-model cross-check; not DT/overlay provenance | R2 |
| 15 updater-candidates | `/system/bin/pm list packages --user 0 -s systemupdat` | Filtered package names / 16,384 B | Consumer-acquisition lead for NWWM; empty excludes only this filter/user | R3 |
| 16 unlock-report | `/system/bin/getprop ro.oem_unlock_supported` | Empty/0/1 / 4,096 B | Owner-policy lead; 1 cannot prove unlocking or RAM boot | R1 |
| 17 android-release | `/system/bin/getprop ro.build.version.release` | Property / 4,096 B | Compare Android 14; does not select boot-image format | R1 |
| 18 bootloader-report | `/system/bin/getprop ro.bootloader` | Property / 4,096 B | Loader-version lead; empty/generic leaves identity unknown | R1 |
| 19 partitions | `/system/bin/toybox head -c 65537 /proc/partitions` | Names/counts / 65,536 B accepted | Current storage topology; no GPT/extents or reconstruction coverage | R2 |
| 20 block-names | `/system/bin/toybox ls -l /dev/block/by-name` | Directory/link metadata / 65,536 B | Check boot/recovery/DTBO/vbmeta naming; no target opens | R4 |
| 21 sound-cards | `/system/bin/toybox head -c 65537 /proc/asound/cards` | Card/driver descriptions / 65,536 B accepted | Select Sony driver investigation; no routing/playback proof | R2 |
| 22 sound-pcm | `/system/bin/toybox head -c 65537 /proc/asound/pcm` | PCM descriptions / 65,536 B accepted | Identify registered endpoints; no PCM/mixer/firmware opens | R2 |
| 23 input-devices | `/system/bin/toybox head -c 65537 /proc/bus/input/devices` | IDs/names/capabilities / 65,536 B accepted | Identify key/touch drivers; no events/range/wake tests. May expose Uniq/private paths | R2 |
| 24 graphics-names | `/system/bin/toybox ls -l /sys/class/graphics` | Directory/link metadata / 16,384 B | Framebuffer topology; not panel/timing/backlight initialization | R4 |
| 25 power-names | `/system/bin/toybox ls -l /sys/class/power_supply` | Directory/link metadata / 16,384 B | Supply names/topology; no battery/thermal/charging values | R4 |
| 26 regulator-names | `/system/bin/toybox ls -l /sys/class/regulator` | Directory/link metadata / 16,384 B | Instances/topology; no voltage/enable/constraint polling | R4 |
| 27 raw-fdt-mode | `/system/bin/toybox ls -ld /sys/firmware/fdt` | Permission metadata / 4,096 B | Export presence/mode only; missing export stops, no content read | R4 |
| 28-38 end:* | Repeat exact rows 00-10 in the same order | Same types/caps; separate indexed files | Require unchanged identity before marking the session complete | R1 |

## Stop rules, privacy and recovery

Immediately stop on identity/transport/protocol/server change, ambiguity, prompt,
unexpected alias, failed/missing exit, stderr, timeout, disconnect, interruption,
malformed required value, byte limit or host I/O failure. Preserve bounded partial
bytes as incomplete; never accept truncation as complete evidence. Record
inaccessible/unsupported/invalid outcomes. No retry, alternative path or silent
skip follows a failed optional operation; a revised subset needs new approval.

Use binary pipes or reviewed shell-v2 frames, no terminal/text pipeline/clipboard
or CR/LF conversion. `head -c` may read a buffer beyond its emitted sentinel;
the reviewed OF/proc callbacks are memory/metadata readers. Permission denial
never authorizes escalation. Keep all raw captures, guard serials, paths, input
Uniq values and hashes private; publish sanitized technical conclusions only.

Excluded: root/su, setprop/settings, service changes, remount/debugfs, raw block
opens/GPT/EXT_CSD/ioctls, media/app-private data/secrets, firmware/calibration
extraction, cmdline/bootconfig, arbitrary DT traversal, raw FDT, sensor/regulator
attributes, event/PCM/mixer/watchdog opens, reboot/recovery/fastboot/EDL, unlock,
boot, flash, erase and partition changes. No Sony contact or automatic upload.
Returned package names/links only justify a later separate path review.

**Same-board recovery is unverified.** There is no mode-transition/restoration
fallback if Android hangs. Stop requests and record the failure; closing client
sockets cannot guarantee remote cancellation. Do not reboot to make a read work.
Successful characterization is not recoverability or accepted execution proof.

## Source basis and engineering decisions

The [prior source register](m10-physical-boot-investigation.md#new-bounded-source-evidence)
pins OF/property memory callbacks, raw-FDT permissions, Toybox bytes and package
filtering. New selective audit of shared Sony archive SHA-256
`5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`:

| Member under kernel/msm-4.19/ | Verified source fact / SHA-256 |
| --- | --- |
| `block/genhd.c:1007-1048,1390` | Registered names/cached sector counts, no raw block open. `f1eac174efc7aa595224b18cfeb333cfd78be699bb36991c9fb50b1b77bf48a8` |
| `sound/core/init.c:852-875` | Registered card IDs/driver/names under mutex, no PCM open. `2c5854f5022c968b474e5b1f7b215765b984f2a8c11f78bcb5f950c88d44875c` |
| `sound/core/pcm.c:1236-1255` | Registered PCM/substream metadata under mutex. `6736df13d8157410933b83bac01f3d2b56f8b8cd0f039df638f36e56ce680f44` |
| `drivers/input/input.c:1149-1190` | Registered IDs/names/paths/Uniq/handlers/capability bitmaps, no event reads. `2b56479815d1554370b56f4dd9c30ecdd9f7d6b5dea2699178c88cd6b4200a00` |

These are verified shared Sony artifact/source facts; runtime selection/access
is unknown. Class-directory reads are restricted to link metadata because
attribute reads can invoke driver operations.

After approved captures, choose exact next DT properties, updater-file path,
kernel/module/firmware matching and peripheral-source audit. Empty/negative
reports narrow observations without globally rejecting independent boot.
Partition names can identify recovery dependencies, never prove their survival
or repair capability. Original DTB/DTBO/AVB authentication, accepted boot delivery,
firmware/calibration, charging/JEITA/thermal/watchdog ownership, hardware function
and same-board restoration remain unresolved even if every read succeeds.

**Separate approval questions:**

- Do you authorize Stage A discovery only, under the stated existing-server,
  USB, output and stop conditions? It will stop after reporting the candidate
  binding for your physical-unit confirmation.
- After reviewing Stage A, do you authorize Stage B's exact 39 observations for
  that privately confirmed unit and approved profile? Stage A approval alone
  does not authorize B; its private binding must exist before execution.

Per the human's explicit assignment boundary, neither stage will run during
this host-validation assignment. Native boot, writes and recovery experiments
remain outside both approvals.
