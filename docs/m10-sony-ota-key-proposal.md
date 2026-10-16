# M10 SK1 proposal: independent OTA-material access test

2026-10-15. **Offline review package frozen; not authorized or executed.**
This proposal tests one concrete capability on the existing functioning player:
can the ordinary shell identity obtain the Sony OTA decryption material through
the exact ABI in the acquired updater, without invoking installation?
The [focused report](m10-firmware-acquisition.md) gives evidence and host tests.
It requires no donor and changes no bootloader/firmware by design.

## Scope and prerequisites

Require explicit subsequent owner approval covering **temporary helper-file writes
and retrieval of key/IV material through one HIDL business call into private host
evidence**, not merely an ordinary metadata read. Confirm the
same sole player is responsive in stock Android, already authorized for debugging
and idle without update/transfer. All original identity/profile values stay fixed.

The canonical wrapper is `tools/run_sony_ota_material_once.py`, with adapter
`tools/acquire_sony_ota_material.py` and tests
`tests/test_acquire_sony_ota_material.py`. Exclusive delivery, the fixed schedule,
cancellation and captured-result validation have offline synthetic coverage.
Approval must bind the code, helper bytes, profile, scope and fresh private output
destination. Scope approval does not silently approve changed inputs.

The current candidate DEX is **4,904 bytes**, SHA-256
`2c65d860fc848640e8f46015b4600fa0adeffd3e4df7619575c2c75874af7c5b`.
It supersedes the earlier 4,648-byte `bce8b6db00cf...` candidate, which remains
historical evidence. A fresh host rebuild reproduced the current bytes. It has
not been tested under ART or Sony SELinux.

Review version `SK1-offline-review-20261015-01` is bound by private
`execution-bundle.json`, `reviewed-plan.json` and `approval-proposal.json` under
`build/m10/sk1-preparation-20261015-01/`. The bundle identifies source, tests,
build evidence, runtime-source receipts, transitive host dependencies and this
exact proposal. The expected identity remains the unchanged private
`build/m10/authorizations/expected-nwa306-20261014-01.json`; serial and physical
USB evidence are not public. The proposed evidence destination is fresh and
ignored. The proposal has `approved: false`; physical execution and owner
approval remain false. No actual approval or readiness record is created.

`build/m10/sk1-preparation-20261015-01/run_sk1_once.py` is retired and refuses
all invocations. Its former bytes are preserved in the reconciliation evidence;
it is not an alternate runner. Freeze identifies review inputs and reproducible
builds, not physical safety. Changed inputs require a new review and freeze.

Server implementation and compiled policy are missing. Static review of those
artifacts is desirable before approval. If still unavailable, approval must
explicitly acknowledge unknown getter/lazy-start effects and the lack of a
verified repair path for unexpected disruption. This is not classified as proven
read-only simply because the method is named `getKey`.

## Exact intended sequence

Reuse trusted existing-server host checks, original physical USB identity, the
one-time current transport-ID binding, held tracker and per-command atomic
selection/inventory/features guards. Never start/reconnect/repair the server.

Run the existing eleven identity commands once, in order:

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

If all pass, require the following fixed metadata/creation commands to succeed:

```text
/system/bin/toybox ls -ldZ /data/local/tmp
/system/bin/toybox ls -lZ /system/bin/app_process64
/system/bin/toybox mkdir -m 700 /data/local/tmp/nwa306-sk1-20261015-01
```

Require an ordinary nonsymlink temporary parent and an ordinary executable
runtime candidate; metadata alone does not verify ELF architecture. These exact paths are proposed, not previously verified
on this Sony. No alias/substitute runtime is allowed. `mkdir` must create a fresh
directory exclusively; any pre-existing entry stops the experiment.

Transfer only the frozen DEX through the trusted bound transport to the newly
created directory as `classes.dex`. No APK installation or permission change is
included. Enforce exact length/hash, a 16 KiB transfer ceiling and five seconds;
then verify the exact on-device hash with:

```text
/system/bin/toybox sha256sum /data/local/tmp/nwa306-sk1-20261015-01/classes.dex
```

Only after exact agreement, invoke once:

```text
/system/bin/toybox env CLASSPATH=/data/local/tmp/nwa306-sk1-20261015-01/classes.dex /system/bin/toybox timeout -s KILL 8 /system/bin/app_process64 /system/bin SonyOtaKeyProbe --run-approved
```

This supplies a temporary environment only to the helper process. It checks its
own UID/domain, looks up the fixed descriptor/default instance and issues at most
one explicit **business** transaction, code 1/flags 0. Framework-generated
service discovery and interface validation are additional IPC, as detailed below.
There is no updater/UpdateEngine call, client-requested service enumeration,
raw partition read or alternate caller.
Missing runtime/API/timeout support is a stop, not a reason to substitute commands.

On complete successful result validation only, remove exactly the two artifacts
created by this session, with no recursion or wildcard:

```text
/system/bin/toybox rm /data/local/tmp/nwa306-sk1-20261015-01/classes.dex
/system/bin/toybox rmdir /data/local/tmp/nwa306-sk1-20261015-01
```

Then repeat all eleven identities and perform host-only continuity checks.
Maximum scope: **29 shell observations, one bounded DEX transfer, one service
lookup and at most one business transaction**. No request follows any failure;
if that leaves the helper file/directory behind, preserve the failure and review
cleanup separately. Do not continue just to collect ending identities.
The single lookup is a client invocation; internal framework/service-manager IPC
and lazy-start activity are not claimed to be a single wire transaction.

## Framework lookup traffic and evidence boundary

Pinned **AOSP `android-14.0.0_r1` source**, preserved with exact hashes in
`build/m10/sk1-preparation-20261015-01/aosp-android14/`, establishes this path:

| Source locator | Framework behavior |
| --- | --- |
| `HwBinder.java:77-81`; `HwBinder.cpp:322` | The two-argument lookup uses `retry=false` and enters `getRawServiceInternal`. |
| `ServiceManagement.cpp:874,907,914-916` | Looks up transport/service through the service manager, then validates a returned interface with `canCastInterface`. |
| `HidlTransportUtils.cpp:27-39` | Validation of this non-base descriptor calls the returned service's `interfaceChain`. Avoiding the generated Java `asInterface` wrapper does not remove this native validation traffic. |
| `service.cpp:246-286` | An admitted lookup of an absent service can request lazy activation through `ctl.interface_start`, even when the client lookup does not retry. |

These are generic Android source facts, not observed Sony runtime behavior.
Runtime receipt files pin the original upstream URLs, byte counts and SHA-256
values. The genuine Sony proxy still defines the business ABI separately in the
[acquisition report](m10-firmware-acquisition.md). The Java host stub returns a
synthetic binder directly and does not model discovery IPC, `interfaceChain`,
lazy activation or Sony SELinux admission. No exact total wire-transaction count
or Sony-side-effect bound is established. Sony's service implementation and live
compiled policy remain unavailable.

## Bounds, evidence and risks

Five seconds for other shell operations, twelve seconds for the helper connection,
180 seconds overall, 2 MiB combined wire, 512 KiB combined decoded streams and
4,096 shell frames per observation. Non-helper streams retain 4 KiB limits;
helper stdout and stderr are each capped at 64 bytes. Successful helper stdout
must be **exactly 64 bytes**: `SK1` plus a
zero byte, little-endian status/key-length/IV-length, then 32/16-byte vectors.
Require exit zero, empty stderr and expected status/geometry/nonzero key.
Anything else remains failed private evidence. These output limits do not prove
a bound on native Binder reply allocation inside the Android process.

Stop on denial, unknown status, malformed/extra output, partial transfer, wrong
identity/hash, timeout, disconnect, tracker loss or uncertain host continuity.
No retry, escalation, root/domain change, security-policy change, reset, mode
transition or alternative service method is allowed. Do not publish captured
vectors, raw logs or identifiers. Record each service/frame, exit, length/hash,
timing, code/profile/approval binding and before/after host evidence privately.

Lookup may activate a lazy service; caller/SELinux checks and server behavior are
unverified. The getter might perform provisioning, counter or persistent-state
work that is absent from the client proxy. A blocking RPC can outlive its client;
killing the helper does not guarantee cancellation of server work. Unexpected
allocation or service failure may affect availability on the only working player.
The temporary files intentionally write userdata, even though no boot partition
write is intended. No claim of invisibility or zero incidental storage activity.

Android stays in its current boot mode. On failure, stop communication and obtain
the owner's local responsiveness observation; no automatic reboot/service restart
or improvised recovery. Normal response/ending identities would establish stock
shell continuity only. No tested restoration procedure covers unforeseen damage.

## What would count as new access

First establish an identity-bound reply independently from raw capture. Then,
entirely offline, test that single captured pair against the preserved official
UPG candidate: bounded AES-CBC decoding, complete valid PKCS padding, full SHA-224
match and ZIP validity, followed by payload signatures/manifest/extent analysis.
Do not invoke the Android decoder or install anything. A successful host decode
would establish OTA-material access and plaintext distribution acquisition; it
would not prove ABL inclusion, equality with installed images, unsigned boot
acceptance or a restoration writer. Distribution applicability remains a separate
question. Failure identifies an access/compatibility
boundary without authorizing another device experiment.
