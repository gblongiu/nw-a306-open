# M5 deployment paths and restoration evidence

2026-10-14. Host-only research. The [M1 evidence
register](recovery-provenance.md#source-register) and M0–M4 reports remain intact.

## New model-specific service evidence

Sony's NW-A306/YY1301B1 **US-model** service document, dated 2024-06-15,
states: “The service policy of this model is Product Exchange.” Page 2 lists
documentation and a USB cable as service parts; it supplies no board schematic,
programmer, restoration image or factory-flash procedure.
[Sony service document, hosted by Encompass](https://research.encompass.com/SON/rr/NWA306_B.pdf).
Sony identifies Encompass as its US parts partner in
[support article 00026306](https://www.sony.com/electronics/support/accessories-audio-video-accessories/articles/00026306).

The two-page PDF was downloaded privately and visually reviewed. SHA-256:
`a8a0381fbcff9539b16ba98b8615bf5d10b5e10a8544279db3ae09167a77359f`.
This is stronger evidence of the published US service policy than generic
“repair available” wording. It does **not** establish the current policy for
the owner's sales region, exclude an internal factory capability, or prove
that a replaced unit preserves the original board's unique state. An exchange
must not be counted as demonstrated in-place recovery.

The appropriate US inquiry channel is Sony Electronics
[Contact Support](https://us.esupport.sony.com/support/s/support-contact?ce=true&language=en_US),
selecting **MP3 Players & Voice Recorders**, then requesting service/platform
engineering escalation and a written case response. For another sales region,
use the regional links in the
[NW-A306 customer-support guide](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733570.html).
No form, chat or case was submitted. Encompass parts sales are not assumed to
provide platform-engineering authorization.
Sony's indexed contact-page contents exposed that product group; direct page
retrieval returned HTTP 502 in the research tool. The maintainer should confirm
current routing when approving contact; no live chat availability is asserted.

## Authentication: separate gates, specific missing artifacts

Historical D1 establishes stock `icx1301`, QCS2290, firmware 3.06.00 and
locked/green state. It supplies neither accepted custom-image policy nor the
selected boot-header version. Android version alone is insufficient to select
the actual header, DT placement, signing policy or rollback state. Obtain
matching authentic images and parse their headers and AVB descriptors offline;
do not manufacture a boot image from a generic Android version assumption.
[AOSP boot image headers](https://source.android.com/docs/core/architecture/bootloader/boot-image-header),
[AVB](https://source.android.com/docs/security/features/verifiedboot/avb).

Qualcomm's technical overview describes ROM-rooted authentication, signed ELF
firmware and hardware/OEM/software identity constraints, with possible debug,
device binding and rollback restrictions. It does not identify which format
generation or restrictions Sony selected for this NW-A306. An accepted Android
kernel image, an accepted peripheral firmware image and an authenticated service
programmer are separate questions; one does not authorize the others.
[Qualcomm, sections 1, 3–5](https://www.qualcomm.com/media/documents/files/secure-boot-and-image-authentication-technical-overview-v2-0.pdf).

Sony's current [Open Devices list](https://opendevices.sony.net/supported-devices-and-functionality)
describes Xperia platforms and supplies no NW-A306 entry. This bounds that
program's documented applicability; it is not a proof that Sony has no private
development facility. AOSP distinguishes supported unlocking from permission
to request it; a UI OEM switch cannot establish either on this model.
[AOSP locking/unlocking](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking).

Five Sony GPL archive members were read selectively and hash-recorded in private
`build/m5/sony-members.json`. Archive S is the pinned 3.06.00 archive identified
in [M2](m2-host-architecture.md). Exact additional constraints are:

| Source locator in S | Observation and implication |
| --- | --- |
| `kernel/msm-4.19/arch/arm64/configs/publishing/sony_dmp_android_defconfig:95–100` | Modules, modversions, mandatory module signatures and SHA-512 are selected. If the running kernel matches, independently compiled replacement modules need an accepted signing arrangement; source availability does not make them loadable. This is a published configuration, not a measured running configuration. |
| Same file, 51–54, 347–352 | Multiple Qualcomm architectures and both Himax and Sintronix touch families are enabled. It cannot select the physical A306 board or touchscreen. |
| `kernel/msm-4.19/arch/arm64/Kconfig:1009–1017` | Kexec is an optional system call dependent on `PM_SLEEP_SMP`. The published Sony config does not explicitly enable it; source support alone establishes no callable, privileged or authorized handoff. |
| `kernel/msm-4.19/drivers/firmware/qcom_scm.c:273–292` | `qcom_scm_pas_auth_and_reset` delegates peripheral authentication/reset to secure firmware. A userspace replacement cannot assume that supplying arbitrary DSP bytes is sufficient. Active Sony loader selection remains unknown. |
| `kernel/msm-4.19/drivers/md/dm-verity-avb.c:217–229` | This is an AVB-specific runtime verity error handler with boot parameters. It is not bootloader verification code or a custom-execution interface. Its failure handling can involve writes; it was inspected only as source. |

The archive inventory still has no `icx1301`-named member or XBL artifact.
Filename absence is not proof that no relevant unnamed board data exists; M2's
missing selected DT and external DLKM build-input findings still stand.
There was no new evidence resolving NWWM internals, so M5 did not repeat UPG
scanning, decryption attempts or historical-tool experiments.

## Ranked deployment decision tree

First obtain a **model/region/revision-specific written answer**. If Sony can
provide supported execution plus same-unit recovery, audit matching artifacts
offline before proposing a spare-device test. If only exchange is available,
establish exactly what is lost and keep the primary device untouched. If no
authorization is documented, continue host Linux engineering and artifact
acquisition; do not reinterpret a generic mechanism as permission or proof.

| Rank / candidate | Supporting evidence | Missing prerequisite / failure mode / recovery dependency | Exact next investigation and authorization |
| --- | --- | --- | --- |
| 1. Sony-supplied accepted development or temporary image | Qualcomm documents OEM-controlled debug facilities generically; no A306 implementation established | Sony's accepted container, handoff, revision restrictions and service coverage; RAM execution can still change storage or power hardware | Audit supplied documentation/images for accepted execution and recovery coverage. A hardware test needs separate approval and recovery proof. |
| 2. Retain authentic vendor kernel/firmware, replace minimal userspace through a supported path | Published Linux drivers and working generic ARM64 Rockbox | Exact AVB descriptors, ramdisk/rootfs placement, module signatures, compatible DT and accepted image chain; verity may reject a changed rootfs | Request matching boot/recovery/DTBO/vbmeta and build metadata. Audit provenance and authenticated ranges before proposing changes. |
| 3. Model-specific supported unlock or custom-key enrollment | AOSP documents these as implementation-dependent capabilities; Sony's published program is Xperia-specific | NW-A306 support, irreversible provisioning consequences, rollback policy and same-unit restoration | Ask Sony explicitly about this model and region. Do not execute Xperia instructions or infer support from the OEM switch. Separate device authorization required. |
| 4. Authorized privileged kexec on a matching spare | Optional ARM64 source interface exists | Running configuration, privilege, legal authorization, correct entry ABI, driver quiescence and safe power state; can hang without storage writes | Obtain configuration and Sony policy first. A reviewed spare plan is a later gate. Android-assisted experimental handoff would not itself satisfy independent power-on into Rockbox. |
| 5. Authenticated service/factory engineering route | Service channel exists; US manual documents exchange, not a programmer | Authentic signed tool/image, access rights, entry surviving GPT/both-slot failure and unique-state handling | Ask whether engineering can restore the same board rather than exchange it. Do not acquire/run generic programmers or attempt EDL. Original-board restoration and device operations require explicit review. |
| 6. Revised/mainline Linux or another matching development platform | Generic kernel/rootfs now boots and uses ALSA/evdev | Sony panel/audio/PMIC support still missing; a different kernel does not remove Sony authentication. Another board cannot validate Sony analog circuitry | Compare authentic board resources with existing driver support after acquisition. Keep generic adapter work offline; any purchase or hardware experiment needs its own scope. |

## Restoration coverage that must be answered

| Failure state | Evidence now | Required confirmation before an experiment |
| --- | --- | --- |
| Healthy Android; interrupted ordinary update | Authentic OTA distribution exists | Target variant, reinstall/rollback rules and documented update failure coverage |
| One unusable slot | Historical A/B names, no restoration test | Actual fallback policy and whether the other slot remains bootable with shared metadata |
| Both boot slots or recovery unusable | No matching recovery procedure | Same-board service entry independent of Android/recovery, authentic tool/image and validation procedure |
| GPT or shared AVB metadata damaged | No coverage established | Supported entry independent of partition discovery and complete matching reconstruction resources |
| Calibration/provisioning/security state lost | No preservation/restoration method established | Device-bound versus replaceable data, lawful backup/restore terms and consequences of exchange; another unit's data is not a substitute |

No row establishes a safe custom boot; the listed prerequisites remain missing.

## Final concise Sony inquiry (unsent)

M5's questions distinguish original-board restoration from the US product-exchange
policy, request failure-specific tool/image identifiers and unique-state treatment,
and ask about supported execution and board/build resources. The consolidated
[M6 questions](m6-recovery-engineering.md#sony-inquiry-unsent) retain this scope.
The historical inquiry was not sent.
