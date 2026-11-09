# Current research status

**Updated:** 2026-11-09. This page summarizes the existing project evidence; it is not a new device test.

## Objective

Run owner-controlled ARM64 Linux on the Sony NW-A306 (`icx1301`), with native Rockbox and a general-purpose Linux environment as separate user experiences. Android root would be an intermediate capability, not equivalent to independent boot.

## Demonstrated

- A generic ARM64 QEMU guest runs the prototype Linux environment with Rockbox, virtual input, display and audio paths. These results do not establish device driver compatibility.
- Sony NW-A300-series firmware update contents have been decrypted and reconstructed offline. Boot-chain and verified-boot components have been analyzed. No owner-accepted unsigned boot path is established.
- Read-only ADB observations of the retail NW-A306 report Android 14, firmware 3.06.00, Linux `4.19.157-perf+`, locked/green verified boot, enforcing SELinux and `uid=2000(shell)`.
- The supplied 3.06.00 kernel source and reconstructed binary contain the rtmutex proxy-lock rollback behavior discussed in CVE-2026-43499. The [source and binary audit](sony-rtmutex-20261104.md) records the matched instructions, tested state model and provenance limits.

## Not demonstrated

- Root (`uid=0`), a stable kernel read/write primitive, or arbitrary privileged execution on the NW-A306.
- A working GhostLock exploit for Sony. A separate ARM64 QEMU research harness has reproduced an invalid RT-mutex traversal, but its intended synthetic `waiter->task` and `waiter->lock` values did not reach the observed object. Its readback success criterion also needs correction before a positive verdict can be trusted.
- Byte-for-byte identity between the supplied reconstructed ELF and the kernel running on the retail unit. The [rtmutex audit](sony-rtmutex-20261104.md) records two different complete kernel builds, despite matching selected relevant functions.
- An owner-invokable ABL unlock/flash/boot command, independent EFI entry, or verified same-board unbrick route.
- Physical Linux boot, native Rockbox playback, or Sony-specific driver bring-up.

## Current decision

The rtmutex flaw is a specific vulnerability candidate, **not a working root chain**. Further exploit work must establish a causally demonstrated, controlled memory operation using Sony-relevant binaries and a verifier that rejects unchanged payload data. Repeated generic QEMU crashes do not meet that condition.

No crash-prone test or boot-critical write should run on the only working Walkman without a separate operation review and explicit authorization. The recovery route is not proven.

## Evidence handling

Firmware images, private device receipts, reconstructed binaries and bulk QEMU traces remain in ignored local storage. This source repository records bounded findings and reproducibility methods; links into local `build/` directories are not a public evidence download. Historical reports retain their original dates and should be read against this summary where their status has changed.
