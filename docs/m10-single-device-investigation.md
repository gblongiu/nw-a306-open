# M10: acquisition on the functioning NW-A306

2026-10-15. Current constraint: one functioning owner device; no donor or exposed
board. H0/electrical acquisition is **not a prerequisite** for continuing M10.
Earlier hardware proposals remain historical conditional options. This increment
uses existing artifacts and public source only; no device communication or boot
transition occurred. Existing failures, private materials and uncommitted work
are preserved. M10 remains open.

## Selected actionable acquisition hypothesis

**Question:** did the stock updater leave an already decoded OTA at its exact
staging path, potentially accessible without root, service invocation or updates?

The authentic acquired Sony APK supplies a concrete target:
`/mnt/icx_cache/NW_WM_FW.zip`. The selected nonstreaming implementation constructs
that file, decodes into it, requests `File.setReadable(true, false)`, constructs
the payload specification and calls UpdateEngine. The permission-call result is
ignored. This is a request for readability beyond the owner, **not evidence
that permissions changed successfully or that shell can traverse/read it**.
DAC, ancestors, SELinux, current existence and file identity remain unknown.

This is targeted file-lifetime/access research, not repeated NWWM decoding or a
proposal to run the updater. A readable leftover could yield stock boot/DT/AVB
and possibly loader artifacts if included in that OTA. No inner inventory is
assumed. A complete early-loader image is not the only useful outcome.

### New artifact evidence and locators

Classification: **verified from device-specific artifacts**, not physical file
existence or an observed installation. Code offsets below are absolute offsets
in `classes.dex` of the previously acquired APK, SHA-256
`1d23a544bfa3f4cdbf9d8ef0514dbaaad985c6fa7ef70fdb52f786b4f2485b68`.

| Exact method / DEX offset | Established behavior |
| --- | --- |
| `UpdateManager.lambda$applyAbNonStreamingUpdate$12`, code item `0x063154`; path load `0x063168` | Constructs the exact staging file and passes it as decoder output. |
| Same method, `0x06319c`, `0x0631a4`, `0x0631a6` | Constants are true/false for `File.setReadable(ZZ)Z`; next instruction at `0x0631ac` does not collect its return. |
| Same method, `0x0631b0`, `0x0631c6` | Passes this file to `PayloadSpecs.forNonStreaming`, then delegates installation to UpdateEngine. |
| `UpdateManager.onPayloadApplicationComplete`, `0x0637fc`; path `0x06387a`, deletion `0x06388c` | Completion values 0/52 reach a branch that deletes the staging ZIP when install type is 0. Other paths and broader lifecycle can differ; retention is not guaranteed. |
| `PrepareStreamingService.downloadPreStreamingFiles`, `0x064c2c`; `0x064cd6`, `0x064d06` | Uses the same internal ZIP path and deletes an existing internal file during preparation. The streaming monitor also requests broader readability at `0x064e00`/`0x064f38`. |

The ignored private script `verify_cache_lead.py` checks the selected path string,
constant-register values, actual DEX method/prototype tables, invocation bytes,
unchecked return and matching cleanup path/call directly against original DEX
bytes. It is a bounded targeted check, not a general DEX verifier or full
control-flow proof. Existing SDK disassembly supplies the surrounding lifetime
trace; no APK program or extracted library executes. Seven in-memory mutation/
bounds controls are rejected; original bytes remain unchanged.

Normal successful update cleanup weakens the expectation of a leftover. That
does not make a low-impact exact-path metadata observation pointless: a positive
result could unlock authentic images without electrical access; a negative result
closes this current-residue hypothesis. Do not create residue by invoking an
update, debug branch, decoder, secure-storage service or permission change.

## Why ordinary fastboot readback is not the replacement assumption

Fresh pinned AOSP Android 14 source inspection establishes **platform behavior**:

- [`commands.cpp:724-743,871-876`](https://github.com/aosp-mirror/platform_system_core/blob/android-14.0.0_r1/fastboot/device/commands.cpp): fastbootd fetch checks build enablement and locked state before opening a partition; its allowlist is vendor_boot and its A/B forms.
- [`Android.bp:138-149`](https://github.com/aosp-mirror/platform_system_core/blob/android-14.0.0_r1/fastboot/Android.bp): `FB_ENABLE_FETCH` is enabled for debuggable builds.
- [`variables.cpp:376-380,505-513`](https://github.com/aosp-mirror/platform_system_core/blob/android-14.0.0_r1/fastboot/device/variables.cpp): userspace identification returns yes; maximum-fetch-size is unavailable when fetch is disabled.

The physical Sony reports a locked `user` build. **If it retains this AOSP
implementation**, fastbootd fetch is not an ordinary stock acquisition path.
Actual Sony native code remains unacquired, so this is not proof of its exact
implementation or early-loader command policy. No fetch experiment is proposed.

The preserved reference LinuxLoader contains a locked-device boot rejection
diagnostic at PE file offset `0x3eb28`. That is **reference-artifact string
evidence only**, not a traced Sony handler or proof about every reference path.
Neither a large download limit nor a host fastboot help listing proves RAM boot.
The host's `fastboot boot` is an active payload-transfer/execution operation,
not a safe query of supported commands.

Public first-person NW-A306 recovery/menu reports provide **unverified leads**,
including an Android 14 claim in the [A306 recovery thread](https://www.reddit.com/r/walkman/comments/170vq2v/nwa306_android_recovery_mode/).
Conflicting key sequences, build omissions and reports of getting stuck prevent
promoting them to a tested entry/exit procedure. Factory reset anecdotes establish
neither firmware reinstall nor unsigned acceptance. Xperia instructions remain
inapplicable without Sony-model evidence.

## C1 proposal: exact metadata, normal Android only

**Pending new authorization; not executed.** Two new remote commands, in order:

```text
/system/bin/toybox ls -ldZ /mnt/icx_cache
/system/bin/toybox ls -ldZ /mnt/icx_cache/NW_WM_FW.zip
```

The first observes only the parent object's metadata. Admit the second only if
the first succeeds and identifies a directory without a symlink or ambiguous
output. The second observes only the exact artifact's inode metadata: type,
mode, owner/group, label and size. No directory enumeration, content read,
final-object dereference, alternate path, glob, update invocation or secret retrieval.
Normal ancestor traversal still occurs; the parent check rejects a final symlink.
A mode suggesting readability is a candidate, not an access test or ZIP proof.

Each stdout/stderr stream: **4,096 bytes**, **5 seconds** per operation. Success
requires exit 0 and empty stderr. The fixed proposal surrounds these commands
with the existing eleven identity observations at each end: **24 observations**,
196,608-byte combined output ceiling, 2-MiB wire ceiling and five-minute session
ceiling. Private proposal JSON contains the exact identities, commands, current
profile digest, source hashes and plan digest. It remains `approved:false`.

Require fresh owner confirmation of normal responsive stock Android, authorized
USB debugging and no update/playback/transfer; revalidate the existing trusted
ADB listener/process/image hash, single physical USB unit, unchanged private
serial/transport binding, shell UID/context/enforcement and locked/green build
profile. Use only the reviewed no-lifecycle server mechanism: no adb executable
launch, server start/restart, settings changes or device reconnection to repair
a precondition. Bind output privately and preserve raw bytes, hashes, exit
status and guard results. A changed binding or uncertain prerequisite stops.

**Failure policy:** denial, absence, nonzero exit, stderr, timeout, overflow,
symlink, unexpected type/identity or ambiguous output preserves partial evidence
and stops the session. No retry or substitute. Target absence is useful negative
evidence, not permission to search neighbouring files. If the parent fails,
do not attempt the target. If the target fails, do not run ending queries.

**Risks:** short diagnostic process/load/logging/accounting work, VFS/label reads,
USB charging and possible hang/disconnect. No intentional persistent software
change, partition access or boot transition. This does not need a firmware
restoration operation to undo an intended change, but it also establishes no
recovery capability. Ordinary forced restart documentation is only an availability
fallback, not proof of restoration or permission to reboot during this probe.

Eight cases using the existing offline replay verify fixed-order success,
parent denial/symlink, target absence/symlink, output overflow, identity change
and stale digest. These are synthetic semantics checks, not live ADB integration.
No C1 live stage or standing-policy extension was added. Before execution, its
fixed scope needs reviewed integration with existing admission/transport guards
and host tests; new code hashes must be recorded. The current standing U1/H1
policy does not authorize C1 and H1 remains quarantined.

## Decisions after that observation

**Positive regular-file metadata:** prepare a separate bounded acquisition of
this exact existing file, beginning with read-access/format validation. Do not
acquire it under C1. Bind the captured package to its internal version, partition
manifest, signatures and unchanged provenance before extracting authorized
members. OTA contents may be incremental, omit early loaders, or fail to match
the installed slot. They are not automatically a restoration image.

**Absent/denied residue:** close this exact hypothesis and advance to controlled
boot-interface observation on the same player. No donor requirement returns.
The next candidate would first establish manual menu entry and return-to-stock
under a separate approved transition procedure, before any host payload command.
It is not executable under this packet. A later fixed metadata sequence could
query `getvar:version`, `getvar:product`, `getvar:is-userspace`, and
`getvar:max-download-size`, bound to the physically controlled unit and a reviewed
host tool. Any failed query stops; no `getvar:all`, OEM command, fetch, download,
unlock, slot change or boot payload is implied. Actual entry/exit and fastboot
identity binding must be defined before that proposal is approved.

## Execution milestone and preservation

A complete loader dump is **not mandatory for the next interface observation**.
An independently verified implemented boot interface plus a known accepted test
image/ABI and bounded return path could justify a later experiment without every
loader binary. Today those conditions are not established. Metadata does not
prove the loader accepts changed kernel, ramdisk, DT or boot parameters; locked/
green and the reference rejection diagnostic make unauthenticated RAM boot an
unproven hypothesis. Actual authentication remains a separate gate.

Authentic OTA/boot evidence can narrow image structure, verification graph and
recovery coverage even if it lacks the OS-loader executable. Independent Linux
still needs an accepted entry and appropriate original-board hardware support.
No root, signing-secret retrieval or Android-assisted launcher is proposed.

Before consequential boot/write experiments, establish surviving accepted repair
entry, applicable original images/layout, rollback compatibility and preservation
of the owner's calibration/provisioning and security-bound state. A/B, official
OTA availability, cached plaintext or a factory-reset menu proves none alone.
The cached OTA cannot recreate RPMB counters/keys, ROM/SoC-bound state or omitted
device-specific regions. Reading images and executing independent images remain
separate engineering objectives.

Final verification: the original targeted DEX check passed; seven corruption/
bounds controls were rejected; eight synthetic replay cases passed. **18 source,
scope, document and preservation checks passed, zero failed**, with **1,456
prior ledger-covered files unchanged**. The prior full unit-suite result is
154 passes and one Windows symlink-permission skip; no full rerun is claimed.
No transport source, standing authorization, earlier report or Pages file changed.
Private sources, scripts, results and the complete increment inventory are under
ignored `build/m10/single-device-20261015-01/`.
