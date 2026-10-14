# M1: recovery provenance and safe development path

Research date: 2026-10-13, America/New_York. This assessment covers public
documentation, existing references and static host artifact inspection.
[M2 firmware analysis](m2-firmware-analysis.md) subsequently preserved the 13
acquisitions, reconciled package sizes and tested the NWWM header profile.
Neither investigation established a stock image inventory, custom-boot path
or recovery from unbootable Android.

## Decision and evidence boundaries

Continue toward an Android-free Rockbox system through **minimal Linux and
host-only software validation**, with a separately authorized matched spare
as the eventual hardware development target. Recovery and boot authorization
remain parallel research requirements.

M1 establishes an available Sony firmware distribution path and investigates
recovery and custom-boot alternatives. It establishes neither restoration from
unbootable Android nor custom-code acceptance. The daily-use device is excluded
from experiments; any later hardware work needs a separately reviewed plan.

References D1/D2, S, R and N retain their meanings and pinned revisions in the
[M0 evidence register](feasibility.md#evidence-register). New references below
use H for direct host observations, L for additional local source locators and
P for primary public documentation. Documentation of a procedure is distinguished
from testing that procedure. Generic platform information is not target support.

## 1. Firmware and recovery artifact inventory

### Sony-hosted update manifests

Four public HTTPS manifest endpoints returned HTTP 200. Each contains a
67-byte text envelope followed by parseable XML. `Distribution` attributes give
the UPG URL, size, `MAC` and version; `Rules/Rule` entries select firmware
`>=1.00` and `<3.06`. The distribution version is `3.06`, while filenames and
support notices identify 3.06.00 (H1/H2, P1/P2).

| Variant identifier | Manifest | Advertised UPG bytes | Advertised `MAC` |
| --- | --- | ---: | --- |
| `0000` | [Sony manifest](https://info.update.sony.net/PA001/NW-A300Series_0000/info/info.xml) | 1,589,257,520 | `cf98cda7f2227a222fc23de27260e625` |
| `0001` | [Sony manifest](https://info.update.sony.net/PA001/NW-A300Series_0001/info/info.xml) | 1,595,425,312 | `4ab0b4dcdbcbe05a2b9ce532c4a4cab9` |
| `0002` | [Sony manifest](https://info.update.sony.net/PA001/NW-A300Series_0002/info/info.xml) | 1,589,253,264 | `a785c3d360bca2c0fd81f4182c9bec8b` |
| `0003` | [Sony manifest](https://info.update.sony.net/PA001/NW-A300Series_0003/info/info.xml) | 931,068,112 | `2172be1ded03f006cdbad31026846f62` |

The manifest URI is HTTP. For acquisition, only the scheme was changed to HTTPS
on the same Sony host/path; normal TLS verification remained enabled. Bounded
requests for bytes 0-4095 of all four UPGs returned HTTP 206 with total lengths
matching the manifests. These are successful remote-header checks, not full
downloads of all variants (H2).

The `0000` and `0002` totals respectively match Sony's Canada and UK notices
(P1/P2); the 4,256-byte difference is accounted for by distinct advertised
packages. This does not establish binary equivalence or a complete region map.
D1's product suffix `icx1301_002` has not been proven to select distribution
`0002`. The inspected candidate must not be installed on that assumption.
The `0000`, `0002` and `0003` manifests' English descriptions list NW-A306;
`0001` has no English description in the captured manifest (H1).

### Complete candidate acquisition

The host acquired
[`NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG`](https://info.update.sony.net/PA001/NW-A300Series_0002/contents/0012/NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG)
over HTTPS with HTTP 200. This variant was selected for static research because
its advertised size matches the UK notice, not because its match to the primary
unit has been established (H3, P1).

- Complete size: **1,589,253,264 bytes**, matching the manifest and response.
- MD5: `a785c3d360bca2c0fd81f4182c9bec8b`, matching the manifest's `MAC` field.
- SHA-256: `50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
- A second read of the completed disk file reproduced both hashes; its first
  4,096 bytes exactly match the earlier range response. Download completion was
  2026-10-14 00:38:23 UTC, October 13 project-local time.

`MAC` is Sony's field name. Empirical equality to MD5 is an integrity comparison,
not verification of a keyed MAC or digital signature. The local SHA-256 fixes
the inspected bytes; neither checksum proves signed boot acceptance, factory
image completeness, compatibility or successful restoration. Other variants'
full-file digests were not recomputed because their full payloads were not
downloaded. The candidate remains private and was never executed or installed.

### What is and is not available

| Artifact class | M1 result | Engineering significance |
| --- | --- | --- |
| Version 3.06.00 update distributions | Live manifests/four UPG headers verified; complete `0002` candidate downloaded and size/MD5/SHA-256 checked (H1-H3). | Public update availability is established; factory-image completeness is not. |
| Sony GPL source | Existing 20260716 release retained unchanged; exact hashes and source findings remain in M0 (S). | Kernel/driver research input, not an installable recovery image or signing authority. |
| Separate stock boot, DTBO, recovery and vbmeta images | Not established as independently usable images by this review. M0 found no such image members in the GPL archive. | Image formats, keys, rollback metadata and restoration dependencies remain unresolved. |
| Full factory/service image set, target-files build archive or authorized service programmer | Not located in the reviewed Sony support/help pages, manifests, local inventory and targeted official-domain searches. | Bounded negative finding; service-only or otherwise unlocated artifacts may exist. |
| Complete primary-device preservation image | None acquired; no device access was authorized. | D1's partition names are not a backup, full GPT or restoration procedure. |
| Rockbox sources | Existing R and N snapshots retained; no new source import or build. | Host-development references, not proof of custom-boot acceptance. |

Older `0000` distribution URLs for 1.01.04 and 2.03.01 returned HTTP 404 to
bounded HEAD checks. This records those retrieval outcomes only; it is not an
exhaustive historical-package inventory or a reason to attempt a downgrade.

## 2. Provenance, integrity and package-format limits

Captured raw manifest SHA-256 values include the envelope and exact body bytes:

| Manifest variant | Captured bytes | SHA-256 |
| --- | ---: | --- |
| `0000` | 55,730 | `78512827cbc169547091baa271d6019ec0701c7ab906d2c9e14c6be64e7b153b` |
| `0001` | 4,991 | `df720c1e603a30c03dbc795b9ff4405de154cd4c026329979526951646fdd39f` |
| `0002` | 55,730 | `94ed7dc95dfc1d60d46fc34e5ea1716afe3a558a68ed697c0ac10e92e91cfb77` |
| `0003` | 55,729 | `fe0504ae7f7e9cad40500da24602f4d95f2f0cb139a9fa216806e6112120ee34` |

Retrieval began at 2026-10-14 00:26:36 UTC, which is October 13 in the project's
timezone. XML `LastUpdate` fields are June 17, 2026; Sony's public release date
is July 16, 2026. Metadata generation time, public release time and retrieval
time are separate observations, not interchangeable dates (H1, P1/P2).

The envelope labels are `ENC0001` and `HAS0002`, with a `digest` field. Their
algorithm mapping was not established. Simple MD5 calculations over the XML
body did not reproduce the envelope digest; that failed hypothesis establishes
neither tampering nor a verified authentication scheme. The XML is directly
readable after the envelope; its label alone does not prove encryption (H1).

All four inspected UPG prefixes begin with ASCII `NWWM`; none begins with a ZIP
local-file header. Python's `zipfile.is_zipfile()` returns false for the complete
`0002` file. In that prefix, bytes 96-107 contain a decimal value
equal to the advertised total minus 140. This is a structural observation,
not a validated length-field specification or proof of the payload boundary.
Internal image names, full-versus-incremental update semantics, encryption,
signatures, trust anchors and partition write coverage remain unestablished
until a validated parser or applicable updater implementation is identified (H2/H3).

The pinned Rockbox `upgtools` format documentation and parser describe older
MD5-prefixed DES/AES containers (L2). They do not establish support for this
`NWWM` envelope. No older updater, repacker or script was run on the candidate.
Changing a URL/filename/header or recomputing a checksum cannot be treated as
signing authorization; no repacking or signature bypass was attempted.

Private host acquisitions and request/integrity records are held outside the
repository in `%TEMP%/nwa306-m1-20261013/`: raw manifests, four 4,096-byte prefixes,
the complete candidate UPG, `manifest-provenance.json`, `header-provenance.json`,
`package-provenance.json` and `static-inspection.json`. Public documentation
contains source locators and hashes, not proprietary payload bytes or private
device evidence. These temporary files need human retention if the research
must survive host cleanup; `.local-references/` was not modified.

## 3. Updater behavior, image acceptance and recovery

### Official updater versus restoration

Sony documents Wi-Fi updates through Android Settings and Music Center updates
requiring the Walkman's File Transfer UI. Both depend on usable Android; neither
notice documents reflashing when Android and recovery cannot boot (P1/P2).
The current manifest selection rules exclude firmware already at 3.06, the
version in D1. Same-version reinstallation is therefore not established by
this update metadata. Service reinstall capability remains a separate question.

Sony states that previous system software cannot be restored after updating.
That statement and the manifest's version-selection rules do not reveal
bootloader rollback indices, their persistent storage or the scope of service
exceptions. AOSP describes per-partition rollback protection in tamper-evident
storage, and distinguishes full and incremental OTAs (P7). Those mechanisms
must not be inferred solely from Sony's UPG filename, package size or A/B layout.

A/B provides conditional fallback to a bootable slot in the generic Android
design. It depends on slot metadata, successful-boot marking, compatible verified
images and rollback policy; the other slot may be invalid. It does not preserve
every shared partition, GPT, firmware component or security state. D1 establishes
an A/B baseline, not demonstrated fallback after arbitrary modification (P7, D1).

### Custom-boot authorization

D1 reports locked/green boot, an unknown loader version and an empty
unlock-support property. D2's failed unlock-ability query and enabled OEM switch
do not establish either an unlock route or its absolute absence. No new device
query was issued. Sony's reviewed unlock guidance is Xperia-specific; applying
it to this Walkman would be unsupported (D1/D2, P8).

| Candidate mechanism | Evidence reviewed | Unresolved requirements |
| --- | --- | --- |
| Sony-authorized development image or signing/service authorization | Generic authenticated-boot framework and Sony support channel (M0 P2, P4/P8 here). | Written NW-A306 policy, accepted image/signing identity, availability and reversal/recovery scope. No such developer route established. |
| Temporary boot through bootloader fastboot | AOSP separates RAM download/boot from flashing, but explicitly allows signature checks before boot (P9). | Actual loader/version/mode, command support, accepted format/signature and persistent effects. RAM residence alone provides no safety guarantee. |
| User-enrolled AVB root of trust | AOSP explicitly makes user-settable trust optional (P10). | NW-A306 implementation, enrollment/reversal, key policy and rollback/recovery behavior. Pixel examples are not Walkman evidence. |
| Stock-kernel kexec handoff | Sony source defines ARM64 KEXEC, but the published defconfig has no KEXEC entry; loading requires capability and security checks (L1). | Actual running configuration, legitimate privilege, permitted policy, memory/hardware handoff and recovery. No root or exploitation path is assumed. |
| Older Sony/Rockbox installer | NW-A30 README describes stock-init application replacement and its own older updater (L3). | Different MediaTek platform; neither replacement-kernel acceptance nor restoration is established for NW-A306. Application substitution does not meet the Android-free objective. |

Kexec is not a bypass demonstrated here. Its source requires `CAP_SYS_BOOT`,
non-disabled loading and security-hook approval, and warns that it does not
itself sync/unmount filesystems. Published Sony configuration also forces
module signature checking. These are source findings, not measured installed
configuration. Even a successful stock-Android-mediated handoff would not by
itself provide direct power-on into the final independent system (L1).

### Interfaces independent of Android

Historical fastboot accessibility is maintainer-reported, but its exact mode
and reachability under failed-boot conditions were not established (D2).
Bootloader fastboot and recovery userspace `fastbootd` are distinct. AOSP
`fastbootd` loads recovery's kernel and libraries; it is not ROM recovery.
Generic `fetch` documentation is restricted to debuggable, unlocked devices
and `vendor_boot`, not a general locked-device whole-storage backup (P11).

Linaro's Qualcomm documentation places EDL/Sahara in PBL/ROM, followed by an
OEM-signed RAM programmer providing Firehose storage operations. It requires
a proper device-specific programmer, command descriptions and firmware (P12).
This makes EDL an independent-interface **candidate**, not a verified NW-A306
recovery path. Entry, availability, accepted signer/programmer, storage support,
additional authorization and covered failures remain unknown. QDL also documents
multi-image programmer dependencies and signed digest-table programming on
applicable targets; accepted programmer transport need not imply unrestricted
storage access (P13). No programmer was acquired or run and EDL was not entered.

## 4. Failure-mode and restoration coverage matrix

No row below establishes a tested firmware restoration on this unit. “Documented”
means Sony describes the limited stock operation; “candidate” requires further
evidence and separate authorization. No procedure in this table is an instruction
to operate the primary device.

| Failure/state | Documented or plausible response | Coverage established | Missing evidence / limitation |
| --- | --- | --- | --- |
| Android works; older software eligible for update | Official Wi-Fi/Music Center update (P1/P2, H1). | Documented supported update route; not executed here. | Selected variant, exact write/authentication semantics and interrupted-update recovery. Current D1 version is excluded by manifest selection rules. |
| UI frozen, firmware otherwise intact | Sony force-restart hint (P3). | Documented restart without Android UI interaction; no damaged-image repair demonstrated. | Whether a particular freeze clears; no device test. Restart cannot be assumed to reconstruct firmware. |
| Settings accessible; user configuration/data problem | Sony factory reset (P3). | Documented reset deleting user content/settings. | No documented reconstruction of corrupt GPT, verified images or loaders. Data loss is expected; not performed. |
| Reboot loop with usable standby/reboot UI | Sony Safe-mode troubleshooting (P5). | Article relies on Android UI and later system updates. | Does not establish recovery when the kernel/recovery cannot boot. |
| Forgotten screen lock; Android inaccessible to owner | Sony paid repair/reformatting (P4). | Official service option for this particular failure is documented. | Does not prove bootloader, GPT, calibration or post-modification restoration coverage. No service contacted. |
| One slot fails; other slot remains valid | Generic A/B fallback (P7). | Conditional platform mechanism; target failure recovery untested. | Slot health/metadata, shared dependencies and rollback compatibility. No slot switching authorized. |
| Boot/system corrupt; intact signed recovery or loader | Recovery reinstall or bootloader restore candidate (D1/D2, P11). | Partition names and historical fastboot report only. | Entry independent of Android, accepted package/commands and same-version reinstall. No target sideload/flash support verified. |
| Both slots unusable or GPT/early loader damaged | Authenticated service/EDL candidate (P4/P12). | Generic ROM-stage mechanism and service channel only. | Matching authorized programmer/image set, layout, independent entry and restoration demonstration. No verified DIY coverage. |
| Calibration/provisioning lost, encryption keys or rollback state changed | Authorized same-device preservation/service candidate (L4, P7/P14/P15). | No complete preservation or restoration demonstrated. | Data locations, device binding, protected counters/fuses and authorized repair semantics. Ordinary partition copies may be insufficient. |
| Storage/electrical damage or unusable charging/power path | Service or specialist hardware diagnosis candidate (P4/P16). | No repair guarantee established. | Board/storage access, power isolation, component failure and whether service replaces the board. Firmware availability alone does not repair hardware. |

## 5. Independent preservation and recovery alternatives

Ranked by immediate usefulness and exposure to the primary device, not by a
claimed probability of success. “Host only” leaves the device untouched;
future hardware approaches carry unquantified failure risks.

| Rank / approach | Feasibility and useful progress | Prerequisites and failure risks |
| --- | --- | --- |
| 1. Host simulation and generic Linux virtual machine | Existing Rockbox simulator and QEMU `virt` provide documented host-development environments (L5, P17). | Pinned host environment and tests. Simulated success cannot establish NW-A306 secure boot, Sony audio, storage, charging or power. |
| 2. Official Sony service/documentation inquiry | Official NW-A306 support and paid-reformatting references justify asking about supported restoration (P4). | Human-sent inquiry or explicit permission to contact support. Require written answers on actual failure coverage, artifacts, rollback and unique-data preservation; no guarantee assumed. |
| 3. Matched spare as eventual test target | Contains experimental risk away from the daily-use unit; engineering risk-containment recommendation. | Match model, variant, hardware revision and starting firmware; budget for loss. Separate approval and recovery prerequisites still apply. The spare's own calibration/identity must be preserved. |
| 4. Authenticated factory/service recovery | Potentially strongest restoration route if model-specific documentation and tooling become available (P12; applicability unverified). | Authentic matching images/programmer, permitted use and demonstrated restoration on a spare. Signed service transport may impose further packet/image policy (P13). |
| 5. Accepted temporary boot with stock storage retained | Could reduce installation writes after loader acceptance is established (P9). | Device-specific authorization, image format and independent recovery. RAM payloads can still write storage, change power hardware or hang; temporary boot is not risk-free. |
| 6. Verified whole-storage preservation | Potential same-device restoration input and layout evidence, not a recovery mechanism by itself (P7/P14/P15). | Complete consistent acquisition, readable storage areas/configuration, protected-state accounting and a proven restoration route. A dump may not restore keys/counters/fuses. No acquisition authorized. |
| 7. External storage/debug-assisted recovery | Contingent specialist fallback; generic debug/storage mechanisms exist (P14/P16). | Schematics, identified storage, accessible signals/voltages, authorization and specialist equipment. Physical access does not establish enabled debug, signed-image acceptance or repairable security state; invasive damage is possible. |

Whole-device preservation must account for both GPT copies, slot/boot-control
metadata, dynamic-partition metadata, all required firmware and calibration,
storage-specific boot areas/configuration and protected security state. Linux
documents eMMC boot areas separate from ordinary user storage; OP-TEE documents
device-bound keys, authenticated RPMB access and write counters as a concrete
example of state that is not an ordinary rewindable disk image (P14/P15).
**Neither eMMC nor OP-TEE is established as the NW-A306 implementation.**
Applicable storage technology and security design must be identified first.

Sony's source includes an NVP node-creation module, but this code does not
establish where persistent calibration/provisioning is stored or how to restore
it (L4). M0's runtime audio tables likewise do not identify their persistent
origin (S5/S6). A Music Center content backup restores songs/playlists on the PC;
it is not a system, calibration or security-state preservation image (P6).
Never transplant another unit's purported full dump as a substitute for
preserving a device's own unique state.

## 6. Blockers and concrete evidence needed

| Blocker and current evidence | Alternatives investigated | Next safe investigation / acceptance evidence |
| --- | --- | --- |
| UPG contents and authentication unparsed (H2, L2). | Official metadata/direct downloads; comparison with older Rockbox parser. | Identify applicable Sony updater/parser documentation or a lawfully obtained static implementation; establish envelope/authentication and full image manifest before extraction/repack claims. No updater execution. |
| Distribution selection for the primary unit unproven (D1, H1). | Compare four official variants and regional notice sizes. | Obtain an authoritative product/variant selection rule from existing documentation or supplied evidence; compare signed model/build metadata once parseable. No cross-region trial. |
| No restoration demonstrated with Android unavailable (P1-P5). | Factory reset, Safe mode, service restoration, signed recovery/EDL, whole-storage and hardware approaches. | Sony service documentation specifying entry, image set, supported failed states, rollback and unique-data handling; later separately approved spare validation. |
| No custom-image acceptance established (D1/D2, P8-P11). | OEM-authorized signing, temporary boot, optional user trust, kexec, older Sony installers. | Applicable loader documentation or authentic loader-image static analysis; legitimate acceptance policy and reversal. Do not retry unsupported commands or rely on an exploit. |
| Persistent state coverage unknown (L4, S5/S6, P7/P14-P16). | Same-device backup, service provisioning, external access. | Map actual storage areas and unique-data ownership using authentic artifacts/schematics; state what cannot be backed up/restored. Security-version compatibility must be demonstrated, not inferred from a dump hash. |
| Driver/build inputs still incomplete (M0 S1-S9). | Minimal vendor Linux, later upstream migration, simulator/virtual host lane. | Host-only dependency/ABI audit on approval; identify DT and firmware/calibration provenance without claiming hardware support. |

## 7. Protecting the primary device

The daily-use NW-A306 is not a development target in this plan. Keep artifact
analysis on the host, with no USB/device discovery, update application launch,
reboot, root, unlock, slot/partition change, boot test, EDL entry or hardware work.
Do not copy UPG files onto it: stock-updater detection or user prompts are
unnecessary exposure. This restriction also applies to apparently reversible
experiments. No absolute zero-risk claim is made.

Any future hardware proposal must identify a separate test unit, authentic
matching artifacts, independent entry and verified recovery for the proposed
failure states, protected-data dependencies, charging/thermal protections and
an explicit stop/restore procedure. Obtain separate human authorization before
device operations, including on a spare. A spare alone does not waive the
recovery prerequisite or make its firmware/security state replaceable.

## 8. Recommended next work

M1 recommended a **host-only build and validation sequence**: pinned-source
build and ABI/dependency audit, existing Rockbox UI simulator, then a generic
Linux virtual machine with file storage and a virtual PCM endpoint. These can
validate software loading, navigation, decoding and controlled software PCM
behavior while real boot, audio and power remain unverified. QEMU's `virt` is
explicitly a fictional board with its own hardware description, not a NW-A306
emulator (L5, P17). No such builds or implementation began in M1.

Continue the recovery track with static analysis of the acquired Sony metadata
and candidate package and a human-sent service inquiry. Ask Sony specifically
whether it can restore this model/region from nonbooting Android, damaged
recovery or GPT; which authenticated images/interfaces are required; whether
same-version reinstall is supported; how rollback and unique calibration/keys
are preserved; and whether any authorized development-image route exists.
Documentation, a matched spare and, if a supported hardware route emerges,
schematics and specialist equipment could help resolve the evidence gaps.
Hardware execution still requires verified acceptance and recovery.

## Completion checks

- The four manifests parsed after their observed text envelopes. Distribution
  sizes match all four HTTP range totals; the complete candidate passed the
  independent disk size/hash/prefix checks described above. Envelope digest
  authentication and package signatures remain unverified.
- Additional Sony source members were selectively streamed read-only; no full
  extraction, external source import or utility execution occurred. Existing
  M0 archive revisions, citations and research findings were preserved.

## Source register

Public documentation accessed during the October 13 project-local research
session. Dynamic endpoints may change; raw acquired manifest hashes above
identify this inspection's exact inputs. M0 references and revisions are unchanged.

| Ref | Exact primary source / locator and scope |
| --- | --- |
| H1 | Four linked Sony manifests above, saved as `NW-A300Series_0000_info.xml` through `0003_info.xml`. Envelope bytes 0-66; XML `InformationFile` attributes, `ApplyConditions/ApplyCondition/Rules/Rule`, `Distributions/Distribution` attributes and English `Descriptions/Description`. Request status, timestamp, URL and hashes in private `manifest-provenance.json`. Direct host observations. |
| H2 | UPG URLs in each H1 `Distribution/@URI`, HTTPS transport. Prefix range 0-4095, HTTP 206 `Content-Range`, length, ETag, prefix SHA-256 and local basename in private `header-provenance.json`. Exact `NWWM` bytes at 0-3; `0002` decimal sequence at 96-107. Direct host observations, no decoded image manifest. |
| H3 | Complete linked `0002` UPG, exact size/MD5/SHA-256 above. Request/final URL, status, bytes and UTC acquisition times in private `package-provenance.json`; independent disk hashes, prefix comparison and `zipfile.is_zipfile()` result in `static-inspection.json`. Local host inspection only; no cryptographic signature or hardware validation. |
| L1 | Existing Sony S archive: `kernel/msm-4.19/arch/arm64/Kconfig`, lines 1009-1017 (`KEXEC`); `kernel/msm-4.19/kernel/kexec.c`, lines 192-208 (`kexec_load_check()`); `kernel/msm-4.19/arch/arm64/configs/publishing/sony_dmp_android_defconfig`, lines 98-100 (forced module signing), no `KEXEC` symbol found. Selected members streamed read-only; not installed-kernel evidence. |
| L2 | Existing R revision `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`: `utils/nwztools/upgtools/upg.h`, lines 26-43, older container description; `upg.c`, lines 151-187, MD5-prefix checking and DES/AES header decryption. Format comparison only; no tool execution. |
| L3 | Existing N revision `c476628bafe71b5a236b627bc4ac4fbd9a649d1b`: `README.md`, lines 146-172 (stock-init application replacement), 364-372 (older install/uninstall mechanism), with platform identity at 6-10. Author's NW-A30 claims, not NW-A306 tests. |
| L4 | Existing S archive: `vendor/sony/products/drivers/nvp/driver/icx_nvp_node/icx_nvp_node.c`, lines 16, 94-140 (`icx_nvp_node_probe()`, device-node creation). The archive inventory lists the node module but not its referenced `../include/icx_nvp.h`. No persistent calibration layout or recovery semantics established. |
| L5 | Existing R revision above: `docs/UISIMULATOR`, lines 18-39 (host simulator and `simdisk`), 49-58 (simulated controls). Source documentation, not a simulator build performed in M1. |
| P1 | [Sony UK 3.06.00 notice](https://www.sony.co.uk/electronics/support/digital-music-players-nw-nwz-a-series/nw-a306/software/00292251), File Info, Before You Upgrade, Download and Install. Documented supported update behavior and 0002-sized release. |
| P2 | [Sony Canada 3.06.00 notice](https://www.sony.ca/en/electronics/support/software/00292253), File Info and Download and Install. 0000-sized NW-A306 release; model-specific notice, not factory restoration proof. |
| P3 | Sony NW-A306 Help Guide: [Restarting the player](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html), Hint; [Formatting the player](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733530.html), main procedure/Note. Documented stock troubleshooting/reset, not reflash validation. |
| P4 | Sony NW-A306 Help Guide: [Initial setup](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733584.html), Note on forgotten screen locks and fee/reformatting; [Customer support website](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733570.html), regional support links. Establishes a service inquiry route and limited repair description. |
| P5 | [Sony repeated-restart article](https://www.sony.com/electronics/support/digital-music-players-nw-nwz-zx-series/articles/00343114), steps 1-5. Page identifies Article ID 00343325 and modification date 2026-01-20. Android UI/Safe-mode/Google Play troubleshooting, not ROM recovery. |
| P6 | [Sony Music Center restore documentation](https://www.sony.com/electronics/support/digital-music-players-nw-nwz-a-series/nw-a1000/articles/MC4PC020085), version 2.2.0 or later, step 5 and following notes. PC songs/playlists restore; page routing names another model, so used only for application backup scope. |
| P7 | AOSP [A/B updates](https://source.android.com/docs/core/ota/ab), Slots/Update engine/Bootloader interactions; [Implement A/B updates](https://source.android.com/docs/core/ota/ab/ab_implement), Generate OTA packages; [Use Verified Boot](https://source.android.com/docs/security/features/verifiedboot/verified-boot), Rollback protection. Generic architecture, not a captured Sony updater/rollback implementation. |
| P8 | [Sony unlock guidance](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader), What is this?/Preparations/Unlock your device; [AOSP locking and unlocking](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking), unlock transition and lock properties. Xperia/generic scope, not Walkman authorization. |
| P9 | [AOSP fastboot protocol](https://android.googlesource.com/platform/system/core/+/main/fastboot/README.md), Command Reference (`download`, `boot`), Client Variables (`secure`, `is-userspace`). Protocol can require signatures before boot as well as installation. |
| P10 | [AOSP Device state](https://source.android.com/docs/security/features/verifiedboot/device-state), User-settable root of trust. Optional feature, not established on NW-A306. |
| P11 | [AOSP fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd), Unify fastboot and recovery, Fastboot commands, Fastbootd changes. Recovery dependency and constrained fetch behavior; no target mode test. |
| P12 | [Linaro/96Boards Qualcomm USB flashing documentation](https://www.96boards.org/documentation/consumer/guides/qdl.md.html), Qualcomm USB flashing tool/Flashing the device. PBL/Sahara, signed device-specific programmer and Firehose prerequisites. Development-board/platform evidence only. |
| P13 | [QDL README at revision `ced9263`](https://raw.githubusercontent.com/linux-msm/qdl/ced9263/README.md), EDL mode, Flash device, Validated Image Programming, Multi-programmer targets. Additional policy/image dependencies on applicable targets; no claim VIP applies to NW-A306. Tool not installed or executed. |
| P14 | [Linux MMC device partitions](https://cdn.kernel.org/doc/html/latest/driver-api/mmc/mmc-dev-parts.html), MMC Boot Partitions. Storage-specific preservation consideration; actual target storage medium unverified. |
| P15 | [OP-TEE secure storage](https://optee.readthedocs.io/en/latest/architecture/secure_storage.html), Key Manager, Device access, Security considerations, Encryption. Concrete generic device-binding/RPMB example, not a claim Sony uses OP-TEE. |
| P16 | [Qualcomm Mobile and IoT security](https://www.qualcomm.com/government/mobile-iot), Secure boot storage, Secure storage and key provisioning, Secure debug. ROM/e-fuse/OTP and debug authorization concepts; actual device fuse/debug configuration unknown. |
| P17 | [QEMU Arm System emulator](https://www.qemu.org/docs/master/system/target-arm.html), Choosing a board model; [QEMU virt](https://www.qemu.org/docs/master/system/arm/virt.html), introduction, Linux guest kernel configuration and hardware information. Generic virtual environment, not NW-A306 emulation. |
