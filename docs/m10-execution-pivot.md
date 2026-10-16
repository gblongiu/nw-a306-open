# M10 execution pivot: original A306 EDL evidence and diagnostic limits

2026-10-15. Offline continuation after successful KC1. **Ordinary legacy kexec
through the observed stock kernel is closed. No independent Sony Linux execution
or accepted image mechanism has been demonstrated.** No device command, USB
enumeration, ADB-server request, mode change, image upload or contact with Sony
occurred in this increment. Existing evidence and historical reports are intact.

## KC1 incorporation and preservation

The [KC1 result](m10-kc1-results.md) is authoritative: decoded configuration line
391 explicitly disables `CONFIG_KEXEC`. `KEXEC_FILE` is absent, not an observed
disabled entry. The roadmap now reflects the running-device finding and keeps
independent handoff, independent cold boot and restoration separate. Android
userspace privileges cannot add an omitted compiled kernel facility.

The frozen independent validator was rerun offline against the original capture.
It again validated all **284 stream files**, exact command scope, framing,
identity/transport continuity, approval binding, host receipts, gzip CRC/size
and configuration hashes. Its two historical output writes were redirected to
memory, and its result matched the saved validation JSON exactly. Real socket
and process constructors were blocked; no capture or prior validation was changed.

A pre-edit ledger hashes **8,361 existing files** across public source/docs/tests,
local instructions and preserved M10 work, excluding Python caches. It includes
the independent kernel-handoff analysis, PID 1, initramfs and QEMU evidence. Those artifacts were neither
rebuilt nor deployed. Prior roadmap and checkpoint bytes were separately saved.
Private records are under `build/m10/execution-pivot-20261015-01/`.

## New Sony-specific artifact: what the original report actually shows

The bounded acquisition target was the previously inaccessible original images
in MrWalkman's June 28, 2024 [A306 report, post 4237][P]. The normal browser
challenge completed automatically; no CAPTCHA was solved or bypassed. Both
image URLs were read from that post's DOM. Browser downloads and separate bounded
HTTPS reads returned identical bytes. Original images remain private, alongside
URL, length and SHA-256 receipts; no third-party image is added to public review.

| Original member / source | Direct visual observation | Evidentiary limit |
| --- | --- | --- |
| `1719615460079.png`, [image 12425579][I1] | Photograph of a Sony-branded player connected to an opened USB cable with exposed conductors. | No legible model/build, wiring diagram, electrical measurements, protocol output or return sequence. Model attribution comes from the author's A306 report. |
| `1719613638195.png`, [image 12425534][I2] | Windows Device Manager lists `Qualcomm HS-USB QDLoader 9008` under serial ports. | Driver-assigned label; no USB descriptors, Sahara packet, hardware identity, trust digest, attempted image or authentication status. It is not cryptographic attestation or the project's unit. |

| Preserved original | Bytes / dimensions | SHA-256 |
| --- | --- | --- |
| `1719615460079.png` | 214,677 / 400 × 300 | `638ad404f53174cd80323228fefa91a0c093e8e4b2bb2b7a3e677ff2eefd6980` |
| `1719613638195.png` | 3,103 / 305 × 46 | `36bbe11c2755ea9e663429729c0987f1afe7e9d6048906daaee665b1dfbe51d5` |

**New finding:** the original illustrated evidence supports externally reported
download-mode enumeration on an A306. It does **not** document a rejected
programmer. The author's signed-loader conclusion is an inference without a
visible transaction in these two images. Do not turn it into an observed Sony
signature rejection, an accepted programmer, or a recovery capability. This
resolves the outstanding image-access gap in the
[ABL acquisition report](m10-sony-abl-acquisition.md); that dated report remains
unchanged. The original thread still supplies no build-bound temporary `boot`
response. No executable Sony artifact was obtained.

The opened cable photograph supplies no reproducible or approved entry method.
The images show neither continued Android availability nor return from download
mode. A port label cannot establish storage access or owner-controlled execution.

## Tested implementation finding: diagnostic text is not authentication evidence

Selected B. Kerler EDL client source was acquired at immutable commit
`1cda1a616748d608667b2d13b73a28d3197ceb45`. This is a **generic host client**,
not Sony firmware and not identified as the tool used in the 2024 report.

In [`sahara.connect`, lines 116-159][S1], a received HELLO returns without a reply;
a silent read instead triggers an XML NOP and potentially a second legacy probe.
Thus this method is not receive-only. [`cmd_hello`, lines 104-114][S2] transmits
a response selecting a mode. [`upload_loader`, lines 633-748][S3] sends image
data on target request; its broad exception handler can suggest a signature
problem without a target authentication status. Explicit END_TRANSFER status
handling is a separate branch. [`sahara_defs.py:78-128`][S4] distinguishes modes
and transport, format, initialization and authentication errors.

Six offline tests execute only selected AST methods with fake transport and
synthetic inputs. They confirm HELLO/no-write behavior, both silence probes,
command-mode response, an exception producing the signature guess without an
image-data request, and a separate explicit authentication-status branch. Real
socket/process constructors were blocked; upstream modules and device libraries
were not imported. These tests validate host control flow, not Sony responses.
The first harness run caught incorrect expected probe lengths; the corrected
six-test run passes and both logs are preserved.

For future evidence, retain the actual packet/status and image hash rather than
diagnostic wording alone. Neither this client method nor its fallback probes
belongs in a proposed receive-only observation. Memory-debug support, identity
commands and read rights on Sony remain unobserved.

## Execution decision and one next task

The bounded investigation acquired original evidence and eliminated an apparent
authentication observation. It did not supply a plaintext OTA, accepted reader,
Sony dispatcher or owner-key transition. The failed embedded-material experiment
and unrelated Sony Mobile programmer remain closed; neither was repeated.
The [existing source/RB1 comparison](m10-boot-execution-analysis.md) is reused,
without another reference-loader analysis or a claim that its policy is Sony's.

The immediate blocker is **no original Sony protocol or implementation evidence
between download-mode enumeration and authenticated execution/read access**.
Knowing that a Windows port appeared cannot select a programmer or explain
temporary-boot acceptance. A full ABL binary is useful, but an original,
build-bound command transaction or an authenticated applicable artifact could
answer a narrower question without it.

**Single highest-value next task:** develop a separately reviewable, no-image
Sahara identity-characterization proposal for a matched research unit, beginning
with evidence of reproducible entry and supervised stock return. Its purpose is
to acquire actual protocol/version and, only if explicitly supported and approved,
hardware/OEM/root-key identity needed to screen reader candidates. Do not begin
with programmer uploads or an unbounded automatic client. The present evidence
does not make that proposal executable on the working player.

The narrowest first observation would be a bounded initial inbound HELLO capture
with zero outbound protocol data, stopping on silence, unexpected mode or
disconnect. It would establish a protocol offer, **not** storage access or boot
acceptance. Command-mode identity requests are a separate reviewed extension;
the client's mode-selection and fallback behavior must not be silently inherited.
Entry/exit, same-unit USB binding, timeout and availability consequences must be
resolved before requesting physical authorization. No such operation is performed
or authorized here. An already-existing original trace can substitute for a new
physical observation if its provenance and scope are adequate.

Temporary `boot` registration, locked rejection, supplied-image coverage and
pre-authentication persistent writes remain unknown on Sony. Firmware decoding
or an accepted reader would still need to expose those branches; mode discovery
alone does not answer them. No bypass or unsupported owner execution is asserted.

Before a recoverable first Linux image trial, the remaining requirements are:

- Sony-specific acceptance and failure ordering for the chosen execution entry.
- Applicable kernel, selected DT/reservations, initramfs and authenticated image
  relationship; a verifiable new-kernel/PID 1 output channel.
- Same-board restoration surviving the trial's failure states, with actual
  layout/images, rollback compatibility and preservation of provisioning,
  calibration and RPMB/SoC-bound state. Normal fastboot Power return is insufficient.
- Reviewed storage/DMA, watchdog, charging, thermal and shutdown ownership for
  the first bounded run. The generic QEMU payload supplies no Sony safety contract.

## Review boundary and checks

Public changes this increment: `docs/roadmap.md`, this report and
`docs/m10-source-control-checkpoint.md`. No production source, existing test,
authorization or physical result was edited. KC1's existing implementation,
tests and two reports are now included in the exact checkpoint inventory.
All new scripts, third-party source, screenshots, receipts and validation logs
remain ignored/private. Their complete ledger and the final preservation result
accompany the checkpoint. No Git history or remote action occurred.

Current host checks: **17 KC1 tests passed**, **six new private client controls
passed**, and the unchanged full suite's result is recorded in the checkpoint.
KC1 revalidation agrees with its original result. Final disclosure, whitespace,
exclusion and preservation checks are recorded there. No new Sony execution,
hardware health or recovery test is claimed. This bounded assignment ends for
human review; M10 and the independent-Linux objective remain open.

[P]: https://www.head-fi.org/threads/new-sony-walkman-nw-a300-series-android-12.966467/post-18202281
[I1]: https://cdn.head-fi.org/a/12425579.png
[I2]: https://cdn.head-fi.org/a/12425534.png
[S1]: https://github.com/bkerler/edl/blob/1cda1a616748d608667b2d13b73a28d3197ceb45/edlclient/Library/sahara.py#L116-L159
[S2]: https://github.com/bkerler/edl/blob/1cda1a616748d608667b2d13b73a28d3197ceb45/edlclient/Library/sahara.py#L104-L114
[S3]: https://github.com/bkerler/edl/blob/1cda1a616748d608667b2d13b73a28d3197ceb45/edlclient/Library/sahara.py#L633-L748
[S4]: https://github.com/bkerler/edl/blob/1cda1a616748d608667b2d13b73a28d3197ceb45/edlclient/Library/sahara_defs.py#L78-L128
