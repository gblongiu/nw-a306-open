# M6 board artifacts and acquisition results

2026-10-14. Host-only investigation. The selected NW-A306 DT/DTBO, matching
boot images and calibration remain unavailable. M6 adds an authentic earlier
Sony release comparison, a specific regulatory-document acquisition lead and
pinned upstream platform evidence. None establishes custom hardware operation.
The original [evidence register](feasibility.md#evidence-register),
[M3 board findings](m3-board-dependencies.md) and
[M4 driver locators I1-I8](m4-nwa306-integration.md#exact-new-source-locators)
are preserved.

## Identity and applicability

Historical D1 establishes `icx1301`, QCS2290/`bengal`, Android 14/3.06.00 and
locked/green state. Independently, Sony's [NW-A306 Help Guide](https://helpguide.sony.net/dmp/1301/v1/en/index.html)
explicitly names regulatory model **YY1301B1**. This associates those product
names; it does not establish a PCB revision, selected DT compatible or a
one-to-one mapping of all regional configurations.

Sony's [Japanese specifications](https://www.sony.jp/walkman/products/NW-A300_series/spec.html)
identify NW-A306 as 32 GB, with a 3.6-inch 1280x720 touch display and
microSD/SDHC/SDXC support. Capacity does not identify eMMC versus UFS; display
resolution does not supply DSI timings or orientation. The same page's wired
output rating is regional, not a universal safe gain limit. No board revision,
storage chip or touchscreen vendor was newly verified.

## Acquired sources, exact provenance

All downloads and selected source members are private under ignored `build/m6/`.
No source archive was imported into public deliverables or executed.

| Resource | Version / size / SHA-256 | Applicability / license |
| --- | --- | --- |
| [Sony source release](https://oss.sony.net/Products/Linux/Audio/NW-A300-NW-ZX700.html), [archive](https://prodgpl.blob.core.windows.net/download/Audio/20230714/NW-A300_NW-ZX700/gpl_source.tgz) | 20230714; 306,268,454 bytes; `67987eced744eb826b72d1602ccde62e07aa3e39bff0bb995f53bd2aac0b22f3` | Authentic shared NW-A300/NW-ZX700 publication; component licenses apply, not a universal archive license. Publisher MD5 `c3f8166bb08b65aa237e1a11634b2b97` matches. Not assumed to be the owner's build or the initial launch archive. |
| [Linux v6.12 QCM2290 DTSI](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/refs/tags/v6.12/arch/arm64/boot/dts/qcom/qcm2290.dtsi) | 58,506 decoded bytes; `27d959a0f11b876d6bda7b5ad7bc9d373873d46daf0f0074426e42b24fdcd6bc` | Related platform only; SPDX GPL-2.0+ OR BSD-3-Clause. Retrieved through Gitiles TEXT. |
| [Linux v6.12 Robotics RB1 DTS](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/refs/tags/v6.12/arch/arm64/boot/dts/qcom/qrb2210-rb1.dts) | 12,353 decoded bytes; `09f33c630b1b000bb458f7be42b0eeb31b3e0c8740c46bbb709d561a481e784a` | Explicitly `qcom,qrb2210-rb1`, `qcom,qrb2210`, `qcom,qcm2290` (13-14); **not Sony/QCS2290 board data**. Same dual license. |

The earlier Sony archive has 111,972 members and 453 paths under
`arch/arm64/boot/dts/`. Comparing those paths with pinned 20260716 archive S
finds **no additional ARM64 DTS/DTSI path**. Searches for `icx1301`, `qcs2290`,
`BoardConfig`, `dlkm` and `vendor/qcom/proprietary/devicetree` names find none;
five `icx` paths belong to NVP node code. These are bounded filename results,
not proof that unnamed data cannot exist. No bulk extraction was performed.

Two members were read selectively:

- `kernel/msm-4.19/Makefile:1-3` identifies 4.19.157; SHA-256
  `e6a4c5690c2edb4f6ce573714b7b28d95fa36cf4225f03e7412195b296884803`.
- `kernel/msm-4.19/arch/arm64/configs/publishing/sony_dmp_android_defconfig`,
  SHA-256 `ab2107eab3a7a3818a103707fae446cee4814419efc63011143a89b9cfb643eb`:
  51-54 enable multiple platforms; 98-100 force signed SHA-512 modules;
  296-300 and 491-498 enable both UFS and MMC families; 347-352 include
  Himax and Sintronix. Thus neither release selects the physical board for us.
  Firmware-loader fallback is configured at 272-275; userspace initialization
  still needs an audit of the actual loading mechanism and required files.

The comparison makes another undirected download of the same family source
less useful than acquiring the selected board artifacts. Original S and its
M0-M5 member hashes remain unchanged.

## Regulatory artifact lead and retrieval limits

The [AK8YY1301B1 exhibit index](https://fccid.io/AK8YY1301B1) lists ten internal
photo parts with attachment IDs **6141961, 6141963, 6141938, 6141939, 6141940,
6141941, 6141946, 6141947, 6141958, 6141960**, respectively. The manual is
6142006, nameplate 6141977, confidentiality letter 6141972. The filing dates
are in 2022; photos became public in March 2023. The index describes a headset,
in conflict with Sony's player identity. Do not use that label or a certification
sample as proof of the owner's board revision.

The index also names inaccessible schematic **YY1301B_Schematic diagram and
Block _r103_20220314a_bom**, block diagram **YY1301B_Block diagram**, and an
operation description. These are precise document requests, not inspected
schematics. The listed WCN3950 document is not proof of an installed chip.

Bounded requests to the FCC attachment interface
`https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=6141961` and the
[mirror PDF](https://fcc.report/FCC-ID/AK8YY1301B1/6141961.pdf) returned HTTP 403.
No photo PDF bytes, local size/hash, component marking or PCB revision was
verified. Mirror-published hashes are not local verification. Acquisition can
resume with a public exhibit downloaded through an ordinary accessible channel,
then size/hash recording and page review, without opening any Walkman. A
schematic request requires separately authorized contact and permitted-use terms.

## Related platform evidence and what it cannot supply

The [Qualcomm QCS2290/QCM2290 brief](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/qcs-qcm2290-soc-product-brief_87-28731-1.pdf),
87-28731-1 Rev. C / 0524C, pp. 1-2, describes A53, Adreno 702, DSI and DSP/RPM
facilities and distinguishes QCM's modem. Web text was accessible; direct
download returned 403, so no local PDF hash is claimed. It supports comparing
SoC interfaces, not transferring RB1's modem, rails or reserved-memory layout.

Pinned v6.12 DTSI locators: SDHCI 886-1002; TSENS 845-853; DPU/DSI
1582-1777; ADSP PAS remoteproc 1838-1870; watchdog 1969-1974. RB1 explicitly
uses an LT9611UXC HDMI bridge (226), `qcom/qcm2290/adsp.mbn` (328-330) and
board-specific storage supplies/pins (512-535). Sony has a different panel and
audio endpoint. Those firmware names, clocks, GPIOs and memory addresses are
**not** A306 settings. The files were not compiled into a Sony DT or boot image.

## Dependency matrix and acquisition order

“Source” below means verified shared-source content, not verified A306 binding.

| Dependency | Classification / what exists | Exact missing input and realistic next investigation |
| --- | --- | --- |
| Product / regional PCB identity | NW-A306/YY1301B1 verified by Sony; historical D1 platform identity | Selected compatible, PCB/BOM revision and region mapping. Review acquired regulatory photos/nameplate, then request the r103 schematic's applicability; photographs alone cannot establish DT selection. |
| Boot/kernel/DT/overlays | Shared Sony 4.19.157 source; selected DTB/DTBO and boot header missing | Authentic matching boot/recovery/DTBO/vbmeta, overlay order, chosen nodes, ramdisk and reserved memory. Request supplied artifacts first; separately authorized bounded characterization only if unavailable. |
| Modules / ABI / signatures | Configured MODVERSIONS and mandatory signatures (M5); DLKM helper absent | Final config, compiler/build ID, Module.symvers, selected modules and trusted signing process. Audit owner/Sony-supplied metadata offline before attempting a compatible build. |
| Display / backlight | SDE/DSI parser source I3; product resolution verified; upstream platform analogue | Selected panel compatible, commands, timing, lanes, rails/reset/polarity, scanout formats, orientation and brightness owner/range. Seek authentic DT and panel BOM; generic KMS tests supply no values. |
| Touch / physical keys | Multiple configured families; GPIO/input source I4 | Controller/firmware, bus/IRQ, ABS/MT ranges/protocol, rotation, key codes and wake bindings. Photos can narrow chip candidates; approved capabilities/tree evidence must select the driver. |
| DSP / firmware / calibration | Shared Q6ASM, ACAL, loader/authentication source B1/I7 | Matching signed ADSP files, reserved memory/IPC/clock/reset, ACAL layout/version and provisioning rights. Request firmware manifest and interface data; RB1 ADSP is not a replacement. |
| CXD3778GF / amp / jack | Sony codec/table/mute/jack source B2/B6/I2 | Actual codec/type, bus/rails/GPIO/IRQ, genuine tables, safe gain/mute/route sequence and jack wake policy. Obtain board audio bindings and calibration interface, keep output disabled until established. |
| ALSA routing | Bengal DPCM/MI2S source I1 | Exact frontend/backend/control topology and parameters. Request existing route profiles and PCM identities; no guessed card number or mixer writes. |
| Internal / microSD storage | Product capacity/card families verified; both controller source families present | Installed controller, rails/card detect, GPT/dynamic/slot metadata, encryption and rootfs placement. Supplied board/GPT metadata first; no device block reads or reference-board pin transfer. |
| Battery / charging / regulators | QG/SMB5/profile source B3/B4 | Battery/thermistor profile, PMIC identity, regulator constraints, JEITA/current/voltage limits and policy owner. Seek board DT/BOM/profile; no generic safe thresholds inferred. |
| Thermal / watchdog / suspend / shutdown | TSENS/QFPROM/watchdog and mute/stop source B5/I2/I7/I8 | Selected calibration/trips, pet/bark owner/times, wake dependencies, charger interaction and PMIC poweroff. Request policy/DT and audit required services before any custom execution. |
| Boot authorization / restoration | Historical locked/green; official update; US exchange policy | Accepted custom chain and same-board recovery covering intended failures. See the separate [boot assessment](m6-custom-boot-assessment.md) and [recovery matrix](m6-recovery-engineering.md). |

Only public-document/source facts and historical observations are target-specific
evidence here. New generic DRM/ALSA results are reported separately. No private
calibration, identifiers, proprietary firmware or source copies enter public
deliverables. Publication must respect each component's license and Sony's
artifact-use terms; GPL source access does not license proprietary services/data.

## Baseline integrity

All 37 project files and 1,113 M5 private Windows files were
copied and verified in ignored `build/m6-baseline-20261014/`. Manifest SHA-256:
`8a6613da0dbc15865e4c698c3e6ead704261188bb4dbae7b3e383143801fe95a`.
The pre-edit WSL snapshot manifest records 42,518 M5 private files, with copies
of all 42 built outputs and VM inputs/results, and verifies all 20 locked M5
inputs. All 42,518 originals were subsequently rechecked against that pre-edit
manifest and copied/verified, with 900 symlinks preserved, completing the full
private-tree snapshot without changing an original. Manifest SHA-256:
`014dd046c0205ea843c575981faac567f2ec18ce9e41d38e98f230fbc05dd11e`.
M0's 318 records, 13 M1 artifacts, 1,887 M3 and 1,593 M4 private Windows records
and three original archives passed verification. Snapshot copies and originals
were checked independently; all pre-M6 private evidence remains unchanged.
