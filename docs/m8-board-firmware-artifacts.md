# M8 board and firmware artifacts

2026-10-14. M8 narrowed the stock-kernel initialization and storage contracts;
it did not locate an authentic selected Sony DTB/DTBO or boot/restoration bundle.
Evidence classes S/H/P/I/U are defined in the [boot/storage report](m8-boot-storage-architecture.md).
Certification-sample markings remain distinct from the owner's configuration.

## Acquisitions and bounded search scope

New resources are private in ignored `build/m8/primary/`, acquired 2026-10-14.
Their bytes were hashed locally; neither proprietary images nor source copies
were added to public files. These are component/platform references, not new
selected Sony board artifacts.

| Resource / revision and locator | Bytes / SHA-256 / terms and applicability |
| --- | --- |
| [Samsung product brief](https://www.avnet.com/fsp/opasdata/d120001/medias/docus/190/SAM-KLM8G1GETF-B041-Datasheet.pdf), `samsung-product-brief.pdf`, p. 1; undated product-page print | 457,051; `eed68b4fd0e244ca3dfa6a60439b9a0a8123ca52af5638d0cc30db1aacf53016`; Samsung copyright, no redistribution license assumed. Two-page strict PDF parse and p. 1 visual review; exact B041 brief but sample suffix unconfirmed |
| [Qualcomm secure boot](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/secure-boot-and-image-authentication-version_final.pdf), `qualcomm-secure-boot.pdf`, 2019, sections 1, 3-5 | 699,258; `2de76bcd1d01604eba13386a6878ee562bc6bce018affad21f4d8ff035b5be6f`; Qualcomm copyright. Old v2-0 URL redirects here; 19-page strict parse and targeted pp. 4-6 visual review. Generic generation, not Sony boot policy |
| [Linux v6.12 PM4125 DTSI](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/refs/tags/v6.12/arch/arm64/boot/dts/qcom/pm4125.dtsi), `pm4125.dtsi` | 2,383; `50766f51ce5aa88fc69261d0bc29aec3f2c6765f09ab6cc70689050cb386466d`; GPL-2.0+ OR BSD-3-Clause; platform only |
| [Linux v6.12 MMC definitions](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/refs/tags/v6.12/include/linux/mmc/mmc.h), `mmc.h` | 17,216; `50a03b69f2a0c19c7c24d69d5a537fa76defdfc6a9cc7738a1c7d8751bdd5775`; GPL-2.0, file notices apply; register reference only |
| [Linux v6.12 SMD regulator driver](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/refs/tags/v6.12/drivers/regulator/qcom_smd-regulator.c), same basename | 57,439; `aedb5834f2dcf49ec57014d2d9e408a300b402402445439a494fa25d8c7a7951`; GPL-2.0-only; related platform, no Sony rail selection |
| [mmc-utils](https://kernel.googlesource.com/pub/scm/utils/mmc/mmc-utils/+/c6692d5f9bf1ab6fbf5694a0b61477621cc4d016/), pinned `c6692d5f9bf1ab6fbf5694a0b61477621cc4d016` | `mmc_cmds.c`: 98,044, `f45ce339439ec0a6afb87d28a021688337407f798cf2f763b6650a9e6d592a0e`; `mmc.h`: 10,274, `e510e21a1ab60e30ad34adf39c0d49c98833455e4ad47737518bb70d4cc494fe`; GPL v2 notices. Static reference only; no device utility built/run |

Gitiles TEXT downloads used ordinary HTTPS, not Git operations. The initial
upstream `qcom-rpm-regulator.c` request returned 404; the correctly named
`qcom_smd-regulator.c` was then acquired. This was a filename correction, not
evidence of missing regulator support. Private acquisition JSON preserves URLs,
redirects, date, sizes, failures and hashes. No software dependency was installed.

Public searches used `NW-A306 dtbo kernel`, `NW-A306 boot.img dtb`, `icx1301
device tree`, `SODAGREEN kernel Sony`, `SODAGREEN QCS2290` and `NW-A300 dtbo Sony
kernel`. They yielded no authenticated selected A306 bundle in the results
reviewed. Older A100 custom-kernel results describe different hardware and were
not adopted as A306 evidence. Sony's [20260716 release page](https://oss.sony.net/Products/Linux/Audio/NW-A300-NW-ZX700_%2820260716%29.html)
still exposes the shared source archive; its selected board bundle is not
provided on that page. The [Open Devices list](https://opendevices.sony.net/supported-devices-and-functionality)
lists Xperia models, no NW-A306 entry. Negative findings apply to these searches
and publications only, not every possible legitimate source. No inquiry was sent.

## Targeted Sony source audit

S is the unchanged 20260716 archive, SHA-256
`5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`.
It is the shared NW-A300/NW-ZX700 release, not a verified image build manifest.
M8 read **15 regular members**, each below 1 MB, selectively from the compressed
archive. All member bytes/hashes are in private `build/m8/sony-members.json`
and `sony-followup.json`. Prefix below: `kernel/msm-4.19/`.

| Locator / member SHA-256 | New result and applicability limit |
| --- | --- |
| `init/main.c:338-361,1037-1043,1117-1145,1194-1200`; `ec168e8ee08f5af1381d891bc918d2965126ec01de34e0e9d4712ea50742feef` | Parses `init=`/`rdinit=`, defaults early userspace to `/init`, otherwise mounts root and tries standard init paths. Kernel code does not require an Android executable. Accepted control of these inputs is unproven |
| `init/initramfs.c:614-675`; `f9f0abccd009cc27351d24ee2872314d94e033164245faa84f27c39ff90c487e` | Supports built-in initramfs and externally supplied initrd unpacking. This source neither identifies Sony's actual ramdisk nor grants permission to replace authenticated bytes |
| `drivers/base/firmware_loader/main.c:283-352,593-611`; `a2f482a4f6678becc20c48999176289577501e1cbbc4d0b83400e318e5daa591` | Direct lookup includes custom path, **`/mnt/vendor/persist`**, release-specific/update and normal `/lib/firmware` paths. Independent init must make required files available in time; persist is not proven to hold a particular calibration file |
| `drivers/base/firmware_loader/fallback.c:542-585,638-701`; `de60f22404577d0c21aaad6cb7635129fc81efbbeb79212f395490e185b9072a` | Fallback exposes sysfs loading/data and may emit `KOBJ_ADD`; userspace must respond or requests can time out. Caller flags, sysctls and security hooks matter |
| `kernel/umh.c:383-401,535-561`; `8528be6e5c1a370eb5607720a0e84b81d07ce74a0b1239da30fc5b1e7ae0645d` | Empty static helper makes `call_usermodehelper` a successful no-op. It does **not** prove firmware uevents are disabled or that Android's uevent consumer is unnecessary |
| `drivers/soc/qcom/peripheral-loader.c:1011-1045,1248-1251,1369-1373`; `4eb33dcd873f7b1089537ecdbf4eac3acc870c06a596756a87e7937875118be4` | Requests selected-name `.mdt`/`.bNN` files, then calls authentication/reset operations. Linux file delivery and secure peripheral acceptance are separate. Selected firmware names/resources still missing |
| `kernel/module_signing.c:48-87`; `7e4ae7e48afb0e5df0f9389761ce3eca027124d53eede058775fcaee963940c8` | PKCS#7 module verification against trusted kernel keys; no accepted signing key acquired. Published mandatory signatures still constrain independently built modules |
| `drivers/mmc/host/sdhci-msm.c:1813-1857,2273-2288,2350-2380,6155-6157`; `d02f3d460ad1d84fe9a7a4f22307aa53ff60385fbae178cb2e449c94c7562422` | Supplies, voltage/current arrays, width, clocks, speed modes and nonremovable policy come from DT. eMMC marking narrows controller research but supplies none of these Sony values |
| `arch/arm64/configs/publishing/sony_dmp_android_defconfig:34,67-68,95-100,272-275,412-415,491-498,548-559,571-573,656-657`; `8822ea40625c2b57c805519591f41f247dd02e41ed41b8091af17a5f73544b6c` | Initrd, direct/fallback firmware loader, several regulator/RPM families, MMC and peripheral loader support; module signature enforcement and static-helper policy. Published config cannot select active drivers or prove final `.config` |

Also read `init/do_mounts.c`, MMC core/header and two regulator sources; these
support the contract or bound the search, not additional selected-board claims.
`drivers/base/firmware_loader/Kconfig:67-95` also warns that custom fallback
without uevents has no timeout and needs explicit failure acknowledgement;
standard modern udev cannot be assumed to provide firmware fallback. A minimal
userspace needs the selected loading contract, not just a generic event daemon.
Archive filename search for PM4125/SODAGREEN/KLMBG/QCS2290, loader names,
`avbtool`, `fstab` and `init.rc` found no matching board/init/loader artifact;
only unrelated e2fsprogs `convfstab` and `gs_fpgaboot` names. No broad content
search of every archive member is claimed. Two initially requested paths were
misspelled (`subsystem-pil-tz.c`, `qcom-rpm-regulator.c`); later inventory finds
`subsys-pil-tz.c` and `qcom_rpm-regulator.c`. Their initial absence says nothing
about subsystem support. M7's 389 DTS/DTSI bounded scan and M6 older-release
comparison are retained without repeating them.

## Component convergence into selected-board requirements

Upstream PM4125 DTSI uses **`qcom,pm2250`** PMIC compatibles (13,88),
SPMI children, PON/power key, RTC, GPIO and disabled VBUS/Type-C nodes (18-92).
The v6.12 regulator driver has `qcom,rpm-pm2250-regulators` (1357) and sends
SMD RPM requests (42-79). Thus searching only a `pm4125` spelling would miss
relevant platform interfaces. These bindings do not establish Sony's PMIC
identity registers, enabled peripherals, charger/profile or rail constraints.
No reference-board voltages, addresses or pin settings were copied into a Sony DT.

| Subsystem / selected implementation contract | Established source basis | Still required for authentic A306 integration |
| --- | --- | --- |
| eMMC / SDHCI | H Samsung family; S shared MMC + SDHCI parser | Selected controller/pins/rails/speed, EXT_CSD/boot regions, GPT and logical metadata; authenticated restoration layout |
| PM4125 / power | H package; P PM2250-compatible SPMI/RPM objects; S multiple RPM frameworks | Selected driver chain, supplies/consumers, battery/JEITA/thermal/watchdog owners, shutdown/suspend policy |
| Kernel / DT / modules | S ARM64 source and published signed-module config | Authentic image/header/build ID, final config, selected DT/overlay order, memory map, ABI/symbols and trusted module policy |
| Firmware / init | S direct filesystem lookup, fallback events, PIL authentication | Manifest of file names/versions/hashes, mount timing, consumers, trusted environment dependencies and independent init responsibilities |
| Display / touch / keys | S [M4 I3-I4](m4-nwa306-integration.md#exact-new-source-locators); H display assembly only | Panel/DSI/backlight/rails/reset commands and controller identity, input/wake mappings. Generic KMS/evdev code cannot supply them |
| Audio / DSP / amp | H 3778 marking; S CXD3778GF family, Bengal DPCM, ACAL and PIL source | Selected topology/DAIs/mixer controls, genuine DSP/calibration, mute/gain/power sequence, jack policy. Persist path alone establishes no table contents |

A board profile should be accepted for implementation only when model/build,
DT compatibles/overlay IDs, kernel ABI, firmware dependencies and safety owners
agree with authentic supplied metadata. M8 adds a partial EXT_CSD reader; it
does not manufacture that profile, DT or a deployable Sony image.

## Bounded firmware hypothesis test

The original complete `0002` UPG remains **1,589,253,264 bytes**, SHA-256
`50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
M2 already reconciled the 4,256-byte published-size difference as distinct
0000/0002 distributions, not a repaired wrapper. [M2 evidence](m2-firmware-analysis.md).

M8 reran the unchanged header inspector and streamed one bounded pass computing
SHA-224 over (a) the entire stored file, (b) bytes 128 to EOF, and (c) the first
1,589,253,124 stored body bytes. **None equals the 56-character field**. This
falsifies these three simple stored-byte digest hypotheses only. It neither
proves encryption nor contradicts the older model's plaintext-digest lead.
No key, decryption, authentication bypass, payload execution or archive repair
was attempted. Private `container-followup.json` records the exact predicates.

No validated inner boundary, manifest, boot/recovery/vendor_boot, DTB/DTBO,
vbmeta, kernel, firmware or calibration member is identified. Compression,
signature ranges and internal region restrictions remain U. M2's full signature
scan was not repeated. The smallest useful container input is an applicable
published format specification or lawfully supplied decoded, provenance-bound
member manifest/sample; it need not disclose signing secrets. An authentic
selected boot/DT bundle supplied independently would bypass this container
research bottleneck without bypassing boot authorization.
