# M0 feasibility assessment

Assessment date: 2026-10-13. Scope: offline source review and preserved evidence.
Findings describe the pinned sources below, not every firmware release or the
current contents of a device. M0 contains no build or hardware test results.

## Decision

**Custom firmware feasibility remains unproven. Investigate minimal Linux with
Rockbox as the primary interface first.** Linux
offers existing Rockbox backends and the published Qualcomm/Sony driver stack;
bare metal would require replacing much of that stack. Both remain blocked by
an authorized custom-boot path and verified recovery. This is an engineering
recommendation, not a statement that either architecture can run on this device.

## Evidence register

References beginning `S` identify exact members of Sony's archive; `R` and `N`
identify paths relative to the pinned Rockbox snapshots. `D` references are
private, preserved observations or prior analysis; only sanitized conclusions
are published here. They are not independently reproducible from this public
repository. Line numbers are one-based in the reviewed files. `P` denotes
primary public documentation, accessed on the assessment date.

### Provenance

- **S:** [Sony NW-A300/NW-ZX700 source release, 20260716](https://oss.sony.net/Products/Linux/Audio/NW-A300-NW-ZX700_%2820260716%29.html),
  `gpl_source.tgz`, locally in `.local-references/sony-gpl-source/3.06.00-20260716/`.
  Recomputed MD5 `7ce834790870b0918cd183f7be4d81fb` matches the recorded Sony
  value; SHA-256 `5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`
  matches `SOURCE-VERIFICATION.txt`. The release covers two product families;
  inclusion alone does not identify the NW-A306's active board configuration.
- **R:** [Official Rockbox snapshot](https://github.com/Rockbox/rockbox/tree/afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09),
  revision `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09` under
  `.local-references/upstream/rockbox/`. ZIP SHA-256
  `9f1339f4658e710fafd0b88d120664971b23033878834442bab8fe2999b73df8` rechecked.
- **N:** [Experimental NW-A30 snapshot](https://github.com/unlimish/rockbox-nwa30/tree/c476628bafe71b5a236b627bc4ac4fbd9a649d1b),
  revision `c476628bafe71b5a236b627bc4ac4fbd9a649d1b` under
  `.local-references/upstream/rockbox-nwa30/`. ZIP SHA-256
  `a1d06d1b7ab10c1784c3c0ad5c440dc2b1ce5a7b0c0e814b075fd957809ddd6e` rechecked.
- **D provenance:** `.local-references/vcapblock/consolidation-manifest.json`
  records 318 files and their original locations, sizes, and SHA-256 values.
  All 318 size/hash checks passed in M0. This checks preservation, not truth of
  every interpretation. The separate `device-evidence/` and
  `firmware-analysis/` directories contained no files in the initial inventory.

### Source locators

| Ref | Exact locator and scope |
| --- | --- |
| D1 | `vcapblock/diagnostics/vCapBlock-root-preflight.txt`, UTF-16LE decoded lines 1-18: model, device, software, SoC, boot state and layout properties; lines 23-34: boot-related partition names. Private historical device evidence. |
| D2 | Maintainer's M0 brief: OEM unlocking enabled, ADB/fastboot accessible, unlock-ability query returned `unknown command`, normal Android restored. No transcript for that fastboot query was located in the reviewed evidence. |
| D3 | User-supplied Windows WALKMAN Properties screenshot, General tab: Sony, `NW-A300Series`, firmware field `1.0`, battery field 97%. Serial number excluded. Host-visible fields only. |
| D4 | `vcapblock/evidence/recovered/run-20261013-034536-594878239/sony-relevant-logcat.txt`, lines 170-189: timer stop, SafeVolume activation, confirmation request, warning launch, focus request and Poweramp pause. Private runtime evidence. |
| D5 | `vcapblock/source-projects/vCapBlock-device-v0.5.1/docs/SONY_READ_ONLY.md`, lines 12-24: prior DEX method traces and limitations of literal-only inspection; `docs/DEVICE_BASELINE.md`, lines 9-17: earlier trials without a genuine warning. Prior analysis, not a fresh method-level disassembly. |
| S1 | `kernel/msm-4.19/Makefile`, lines 2-5: source kernel 4.19.157. `arch/arm64/configs/publishing/sony_dmp_android_defconfig`, lines 51, 69, 95, 341-352, 373-394, 429-442, 491-498, 620-624: Qualcomm, compatibility, modules, input, power, display, sound, storage and Android configuration. Paths after the first are relative to `kernel/msm-4.19/`. |
| S2 | `vendor/qcom/opensource/audio-kernel/config/bengalautoconf.h`, lines 15, 25, 41, 45: QDSP6 interfaces, Bengal and CXD3778GF enabled in this source configuration. |
| S3 | `vendor/qcom/opensource/audio-kernel/asoc/bengal.c`, lines 5765-5794: secondary MI2S linked to CXD3778GF ICX playback; 5855-5884: quaternary MI2S linked to STD playback; 7108-7125: card name, audio routing and component nodes required from device tree. |
| S4 | `vendor/qcom/opensource/audio-kernel/asoc/codecs/cxd3778gf/cxd3778gf.c`, lines 559-589: GPL declaration and `sony,cxd3778gf` I2C binding; 627-697: rate list and Sound/Music/Playback DAI formats; 827 onward: ALSA controls, including volume at 913 onward and mute at 949 onward. |
| S5 | Same codec directory, `cxd3778gf_table.c`, lines 78-84, 132-142, 187, 309-333: sparse volume/tone initializers, `ovt`/`tct`/DSD table ports, mode 0600 and runtime table loading. `cxd3778gf_volume.c`, lines 127-173: volume index drives table-based register writes. |
| S6 | Same codec directory, `cxd3778gf_platform.c`, lines 103-116: TYPE_Z/TYPE_A selected by card name; 119-227: device-tree GPIOs and `vl14` regulator. `cxd3778gf_control.c`, lines 223-244: initial mute with master-volume index 120; 668-726: early suspend/resume; `cxd3778gf_dnc.c`, lines 28-51: optional external processing interface. |
| S7 | `vendor/qcom/opensource/audio-kernel/asoc/msm-pcm-q6-v2.c`, lines 395-415, 718, 879: Q6ASM stream open, client allocation and writes. Same codec directory as S4, `Android.mk`, lines 20-45: external audio-module build depends on `device/qcom/common/dlkm/AndroidKernelModule.mk`. |
| S8 | `kernel/msm-4.19/drivers/misc/lifmd6000/lifmd6000.c`, `rme_spi_read_fw()`, lines 651-675: requests external RME firmware. `kernel/msm-4.19/sound/soc/fsl/lif-md6000-rme.c`, `md6000_setup_params()`, lines 168-343: format/rate control. Presence does not establish use on NW-A306; shared release includes NW-ZX700. |
| S9 | `kernel/msm-4.19/techpack/display/config/bengaldisp.conf`, lines 4-8: DRM/MSM/SDE/DSI configuration. `kernel/msm-4.19/arch/arm64/boot/dts/qcom/Makefile`, lines 2-9: generic boards, no NW-A306 target there. |
| R1 | `firmware/export/config.h`, lines 91-93: native/hosted platforms. `firmware/export/config/sonynwzlinux.h`, lines 5-7, 83-92, 106-116: hosted Linux, ALSA, charging monitoring and host storage. `tools/configure`, lines 3604-3623: existing Sony A10 hosted target; 4684-4692: AArch64 detection, not QCS2290 support. |
| R2 | `firmware/target/hosted/pcm-alsa.c`, lines 78-86, 159-190, 531-551: PCM format selection, rate negotiation and ALSA open; `lcd-linuxfb.c`, lines 66-127: `/dev/fb0`, framebuffer ioctls and mapping; `button-devinput.c`, lines 65, 188-267: Linux event input. Latter paths share the same directory. |
| R3 | `lib/rbcodec/codecs/SOURCES`, lines 1-6: Opus and FLAC codec sources. `docs/COPYING`, GPL version 2; `docs/LICENSES` and individual source headers: additional component licenses. |
| N1 | `README.md`, lines 6-10, 23-56: MT8127/Linux 3.10/glibc architecture and author-reported functionality/limits; `firmware/export/config/sonynwa30.h`, line 87: includes hosted Sony configuration. These are NW-A30 claims, not tests by this project. |
| P1 | [AOSP locking/unlocking](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking), sections “Unlocking the bootloader” and “Locking/unlocking critical sections”; [Verified Boot flow](https://source.android.com/docs/security/features/verifiedboot/boot-flow), “Flow for A/B devices” and “Communicate Verified Boot state to Android”. Generic policy, not proof of Sony implementation. |
| P2 | [Qualcomm secure-boot overview](https://www.qualcomm.com/news/onq/2017/01/secure-boot-and-image-authentication-mobile-tech), “Secure Boot and Image Authentication”: ROM-rooted authenticated chain. [QCS2290 product description](https://www.qualcomm.com/internet-of-things/products/q2-series/qcs2290), CPU and DSP features. Platform evidence only. |
| P3 | [Sony firmware 3.06.00 notice](https://service.sony.com.cn/download/firm/00003034.html), version/release date, “Before updating” and update methods: Wi-Fi or Music Center for PC; prior-version restoration unsupported. Regional update instructions, not a factory recovery package for this unit. [Sony Open Devices unlock page](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader), “What is this?”: Xperia scope, no Walkman authorization established. |
| P4 | [Sony NW-A306 announcement](https://www.sony.co.uk/presscentre/sony-unveils-a-new-walkman-with-enhanced-sound-quality-and-longer-battery-life), “Faithful sound reproduction”: S-Master HX. [NW-A306 sound adjustments](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733581.html): Sony effect features and output-specific restrictions. Product documentation, not driver validation. |
| P5 | [Linux ASoC overview](https://docs.kernel.org/sound/soc/overview.html): codec/platform/machine separation. [Linux v6.12 `qcm2290.dtsi`](https://raw.githubusercontent.com/torvalds/linux/v6.12/arch/arm64/boot/dts/qcom/qcm2290.dtsi), CPU/PSCI, SDHC and `remoteproc_adsp` nodes: related platform support, not NW-A306 board support. |
| P6 | Local Bootlin `documentation/bootlin/embedded-linux-slides.pdf` (551 pages), pages 65 “Linux vs. bare-metal toolchain”, 68 “ABI”, 88 “Bootloader role”, 229 “Root filesystem in memory: initramfs”, 315 “Device Tree design principles”. SHA-256 recorded in adjacent `source-manifest.json`: `91eca04a0c5504e399206e31575d63e5d0a8dc21c2fdc8474bcb42e73dcd612a`. [Public edition location](https://bootlin.com/doc/training/embedded-linux/embedded-linux-slides.pdf) may change; page locators refer to the preserved copy. |

## Boot chain and recovery

D1 reports `green`, locked vbmeta, flash locked, A/B updates, a slot suffix and
dynamic partitions. It lists paired boot, recovery, DTBO, vbmeta and
vbmeta_system partitions plus `super`; it does not supply a complete GPT,
partition sizes, boot headers, rollback indices or binary images. Kernel
4.19.157 is a **source finding** (S1), not a measured running-kernel version.

The working model is Qualcomm ROM -> authenticated platform loaders -> Android
bootloader/AVB slot selection -> boot image/kernel and ramdisk -> Android
userspace (P1/P2). The names, versions, signing policy, execution state, handoff
addresses and exact sequence of this unit's earlier loaders are **unverified**;
do not present generic XBL/ABL arrangements as a captured NW-A306 chain.

OEM unlocking enabled (D2) is permission-related UI state, not an unlocked
loader. `unknown command` for one query establishes only that query's failure;
it proves neither that every unlock mechanism is absent nor that another one
works. D1's empty `ro.oem_unlock_supported` is also inconclusive. Sony's Xperia
procedure (P3) is not a supported Walkman procedure. No verified NW-A306 unlock,
root, custom-key enrollment or unsigned temporary-boot procedure was established.

The complete Sony archive member inventory contains 85,019 entries. No member
name contains `icx1301`, `BoardConfig`, `mixer_paths`, an `abl/` or `xbl/`
component, or a Bengal-named `.dts`/`.dtsi`; no `boot*.img`, `recovery*.img` or
`vbmeta*.img` was found. S9's Qualcomm DT Makefile lists other boards. These are
bounded filename/inventory findings, not proof that no relevant information is
embedded under another name or obtainable elsewhere. The referenced QCOM DLKM
build helper (S7) is absent from this inventory. Thus the release is not a
demonstrated complete, independently reproducible firmware build environment.

Sony provides a 3.06.00 update route (P3), but no matching full factory image set
or dependable restoration from an unbootable modified system was verified in
M0. Update availability, Android factory reset, a successful exit from fastboot,
and A/B fallback do not establish that recovery. Slot fallback also depends on
boot-success metadata and rollback policy (P1). EDL access and an authorized,
matching programmer remain unknown and are not a recovery plan.

Before any experimental custom boot, require all of the following:

1. Exact regional/hardware identity, partition map, image format, DTB/DTBO
   selection, AVB chain and rollback constraints documented from authorized
   evidence; no borrowed layout or cross-region assumption.
2. Authentic, hashed stock images and required firmware/calibration material,
   with provenance and permitted use; a documented restoration procedure that
   remains reachable if Android fails to start.
3. Recovery demonstrated under a separately approved plan, preferably on a
   spare matching device, with the failure states it actually covers recorded.
4. A device-specific, authorized custom-image acceptance mechanism, exact scope
   of any destructive transition and a reviewed bounded experiment. A claimed
   temporary boot is not presumed supported or safe.
5. Explicit approval of the exact device operation.

## Firmware architectures and Rockbox integration

| Consideration | Minimal Linux with Rockbox | Fully native bare-metal Rockbox |
| --- | --- | --- |
| Intended environment | Linux kernel plus small root filesystem/init; Rockbox starts as primary UI. No Android framework, ART, Google services, launcher or Sony Android application stack. | Rockbox runtime and target drivers directly manage the application processor, while any unavoidable platform firmware must be identified. |
| Reuse supported by source | Hosted Rockbox ALSA, event-input and host-filesystem code (R1/R2); Sony/Qualcomm kernel and audio modules (S1-S9). | Rockbox native platform exists (R1), but no QCS2290/NW-A306 target was found in the reviewed configuration/target inventory. |
| Required new work | Board DT and kernel configuration, module/firmware loading, display and input adaptation, mixer/codec initialization, battery/power policy and reliable init/shutdown. | CPU entry/exception/timer/interrupt support plus MMU/cache/DMA, clocks/resets, pinctrl, PMIC/regulators, storage, USB, display/touch, audio/DSP IPC, battery/charging/thermal and suspend drivers or equivalent firmware services. Scope inferred from the Linux stack, not an implementation estimate. |
| Boot dependency | Custom kernel/ramdisk must be accepted by the existing boot chain. | Bare-metal payload also needs an accepted boot container and known processor/memory handoff. It bypasses none of the signing restrictions. |
| Maintenance | Smaller initial driver gap; vendor 4.19 divergence and missing build inputs are liabilities. Long-term upstreaming needs a separate board/driver audit. | Larger new platform surface and validation burden; no demonstrated SoC target to reuse. Avoid promises of lower power or faster boot. |
| M0 verdict | Best evidence-supported research direction; still blocked and untested. | No credible near-term implementation path established; retain as a comparison, not the first port. |

Suggested Linux shape, conditional on the gates: accepted boot container ->
kernel with correct board DT and required modules/firmware -> minimal initramfs
or small root filesystem -> init and essential safety services -> Rockbox.
Preserving required Qualcomm firmware does not require preserving Android
userspace; it does mean an entirely open firmware stack has not been established.
Init must retain charging, thermal protection, shutdown and crash handling;
removing Android cannot simply remove their policy responsibilities (S1, P6).

R1/R2 provide backend source code; reuse on NW-A306 remains unverified. Linux
framebuffer code assumes `/dev/fb0`, whereas Sony's display configuration is
DRM/SDE/DSI (S9); framebuffer compatibility or a DRM backend needs evidence.
Map actual input events and storage mounts rather than inheriting older Sony
paths. Choose and validate ABI/toolchain/libc deliberately: S1 enables 32-bit
compatibility in an ARM64 configuration, and R1 detects AArch64, but neither
proves a new Rockbox target builds or loads its codecs/plugins. A 32-bit Linux
userspace is a candidate, not a settled requirement (P6). FLAC/Opus source is
present (R3); throughput and playback remain untested here.

N1 describes an unofficial hosted port on **MediaTek MT8127, Linux 3.10 and
hard-float glibc**, with limitations including Bluetooth and real shutdown.
It is useful for studying integration problems and Sony control concepts.
Its loader, register assumptions, PCM device numbers, permissions, calibration,
volume mapping and display/input setup must not be transferred to QCS2290.
Sharing a codec-family name is not board compatibility.

Mainline Linux v6.12 contains QCM2290 SoC descriptions (P5), including clocks,
storage and ADSP-related infrastructure. This is a related-platform lead, not
a verified QCS2290 Walkman port or proof of complete audio support. Prefer an
offline vendor-kernel dependency audit before choosing a newer kernel; an
upstream migration may reduce long-term divergence but expands initial work.

## Sony audio: available code and unresolved dependencies

**Open driver evidence.** S2 enables the Bengal/CXD3778GF components. S3 wires
secondary MI2S playback to the ICX codec DAI and quaternary MI2S to the STD DAI.
S4 exposes I2C control and ALSA controls for volume, routing-related state and
muting; S6 manages power/reset/jack-detection GPIOs and a regulator. Together
with Sony's S-Master HX product statement (P4), these are credible leads to the
digital-amplifier integration. They do not identify this board's selected DT,
active PCM endpoint or complete physical signal path. ASoC separates machine,
platform and codec responsibilities (P5); codec source alone is insufficient.

**Digital path and formats.** The reviewed source suggests CPU-decoded PCM ->
ALSA/Q6ASM frontend -> Qualcomm DSP/routing -> MI2S backend -> Sony codec/amp.
Q6ASM use is explicit in S7; runtime topology and required DSP binaries or
calibration are unverified. S4 lists 44.1/48 kHz families through 352.8/384 kHz
among other entries, S16/S24/S32 PCM containers, and DSD formats on ICX/DAC DAIs.
This is a driver declaration, not an end-to-end supported-rate matrix, effective
DAC precision or proof of native DSD on the NW-A306. R2 negotiates ALSA rates
with `set_rate_near`; its 32-bit container does not prove 32-bit resolution or
bit-perfect output. Mixer choices, DSP processing, resampling, clocks and the
physical output all require later measurement.

**Calibration and safe initialization.** S5 has sparse volume initializers,
zero-initialized tone/DSD tables and privileged runtime table-loading ports.
Volume is an index that drives several register values, not an established dB
scale. Correct device-specific tables, their loader and redistribution rights
were not established. S6 initializes mute but a master-volume index of 120;
never treat source defaults or guessed mixer values as a safe bring-up sequence.
Before output testing, derive a bounded mute/power/route/volume sequence and
verify calibration under a separate approved plan. TYPE_A/TYPE_Z selection is
card-name dependent in S6; it must be reconciled with the actual NW-A306 DT.

**Additional firmware.** S8's MD6000/RME code requests an external firmware
payload. The publication serves NW-ZX700 too, so whether this block lies on
the NW-A306 playback path is unknown. Record and resolve it as a possible
dependency; do not assert that all audio needs this block or that its payload
is freely redistributable. The same caution applies to ADSP and wireless
firmware, which have not been matched to this device.

**Sony processing and Android services.** A GPL codec control or a “sound
effect” mixer control is not an implementation or license for DSEE Ultimate,
ClearAudio+, Vinyl Processor, DC Phase Linearizer or other Sony processing.
P4 documents stock features; D5 records prior APK/HIDL analysis, including
`SafeVolume$SafeVolumeActive.entry()`, `requestSafeVolumeConfirm()` and
`VolumeCtrlAlertActivity`. Those analysis notes are not newly validated
disassemblies. S6's DNC interface also permits a separately registered module;
an interface does not establish availability of its algorithm. No complete
open-source implementation of Sony's advertised effects was established by
this selective review. Plain Rockbox playback and any independent Rockbox DSP
features should be evaluated separately from Sony feature parity.

**Observed interruption and conflicting evidence.** D4 records the timer
stopping, `INACTIVE -> ACTIVE`, confirmation, Sony warning launch, Sony's audio
focus request and Poweramp's `AUDIOFOCUS_LOSS` pause in sequence. It supplies the
genuine-warning evidence absent from D5's earlier short trials. The earlier
absence is not a contradiction of the later event, and neither proves a
successful suppression mechanism. This establishes an Android service/UI
interaction, not a codec defect or a hardware timer that must exist under
Rockbox. An independent system still needs deliberate hearing-safety behavior;
M0 does not specify a volume-limit bypass.

**Output and power.** Wired headphones are the first proposed output target;
the correct frontend, backend routes, jack handling, tables, gain and mute
sequencing are unresolved. Bluetooth additionally needs a verified controller
transport/firmware, host stack, pairing, audio profile, encoder and Rockbox
output integration. ALSA or S-Master HX availability does not provide those.
Networking is optional and equally unvalidated. S6 contains audio suspend/resume
logic, but idle drain, wake behavior, charging interaction, thermal behavior,
pop suppression and battery life have not been measured without Android.

## Conflicts, limits and completion checks

- D3's Windows firmware `1.0` and 97% battery are host fields. D1 and Sony's
  3.06.00 notice support the Android baseline; the host field's semantics and
  battery accuracy remain unknown. The screenshot does not prove custom power
  management. No device serial, private recording, APK or raw log is reproduced.
- General platform drivers and enabled defconfig symbols are source availability,
  not verified subsystem binding. Display, touch variants and MD6000 especially
  need a board-specific match; see the [hardware matrix](hardware-matrix.md).
- Review enumerated the archive and selectively read 45 source/build files into
  private temporary review copies outside the project. No full extraction or
  source import was performed. Prior gzip/TAR and ZIP CRC validation was supplied
  by the maintainer; M0 rechecked archive hashes, not a fresh full CRC test.
- All 318 vCapBlock manifest entries passed size and SHA-256 checks. Relevant
  source locators and Markdown links were checked offline; 11 cited Rockbox and
  NW-A30 files match their pinned ZIP members byte-for-byte. These are evidence
  and documentation checks, not build or hardware tests.

The resulting next research question was whether an authentic matching image
set could be obtained, what the update package contains, and which restoration
route survives an unbootable Android system. The
[M1 inventory](recovery-provenance.md) records that follow-up.
