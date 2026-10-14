# M7 execution and original-board recovery

2026-10-14. No NW-A306 custom execution or same-board restoration is demonstrated.
The new FCC material supplies target-specific radio-authentication policy,
certification-sample identity and storage/provisioning constraints; it does not
supply a bootloader, accepted alternate image or service programmer.

## New evidence relevant to execution

Sony's `14_Non_SDR_5G_WiFi.pdf`, p. 1, dated 2022-09-14, states that the
YY1301B1 radio's regulatory domain cannot be changed by third-party software
and official firmware is subject to manufacturer authentication. The signed
second page was also reviewed. This is evidence of **radio regulatory policy**,
not a specification of Android AVB keys, bootloader unlock support or service
authentication. The separate KDB594280 software-security declaration remains
metadata-only. [Exhibit 6141975](https://fccid.io/AK8YY1301B1/Letter/YY1301B1-Template-Cover-Letter-KDB-442812-Non-SDR-For-5G-WiFi-6141975).

The RF report (`07_RF_BT3_Test.pdf`, p. 8) names Qualcomm Radio Control Toolkit
4.0.00185.0 for continuous transmit tests. A certification test facility is not
an independently bootable Linux entry, a restoration service or permission to
operate a retail unit. No toolkit was acquired/run. The photos expose packages
and pads but no verified debug/EDL entry, secure-boot fuse state or accepted
signature policy. An exposed pad is not a recovery interface.

Historical D1 locked/green state and partition names remain the only preserved
target boot observations. Existing NWWM bytes and ten inspector tests still
verify the outer header only. M7 did not repeat exhaustive opaque-payload scans
or historical decryption experiments: new component markings supply neither
keys nor a validated container specification. Images/DT/AVB/rollback metadata
remain unavailable. [M2 firmware limits](m2-firmware-analysis.md).

## Execution alternatives and decision evidence

The [M6 ranked matrix](m6-custom-boot-assessment.md#ranked-decision-matrix)
retains its full privilege, signature, write and recovery requirements. M7's
target-specific update is below. No candidate has a verified A306 entry point.

| Candidate / priority | Entry, authentication and kernel/DT requirements | Independence, persistent effects and proof still missing |
| --- | --- | --- |
| 1. Sony-supported development / accepted temporary image | Need model/revision-specific supported entry, accepted signer/container, kernel/DT/ramdisk and peripheral firmware. FCC radio authentication does not document this facility | Could be independent of Android if a boot-time entry is supplied. RAM execution still runs power/storage code; write/counter side effects unknown. Need supplied accepted image and documented same-board failure coverage |
| 2. Accepted stock kernel + independent userspace | Need actual boot-header/AVB signed ranges, ramdisk/root selection, final config and signed modules/firmware. Photos identify likely eMMC/PMIC/codec, not permitted init changes | Meets objective only if power-on reaches Linux/Rockbox without Android userspace. Modified ramdisk/rootfs may violate the chain despite unchanged kernel. Need matching authentic images/descriptors and essential-init ownership before proposing layout |
| 3. Model-specific unlock / owner-key enrollment | Need actual A306 implementation and authorized trust transition; OEM switch and published Xperia facilities are insufficient | May change persistent security state and erase data; relock/rollback consequences unknown. Need applicable policy and restoration/provisioning coverage. FCC radio restrictions neither prove nor disprove a supported kernel unlock |
| 4. Supported retail temporary boot | Need loader implementation distinct from recovery-dependent fastbootd, accepted signatures, exact image/DT/memory handoff | Potentially Android-independent; no supported entry or no-write guarantee established. Need authentic loader documentation/supplied static evidence, not generic protocol expectations |
| 5. Authenticated service/factory development | Need Sony-accepted loader/tool/image manifest and access rights tied to board/security state; restoring stock may not permit custom payloads | May survive higher-stage failure only if documented surviving entry exists. Writes/provisioning effects unknown. US exchange manual provides no such tool or procedure |
| 6. Authorized kernel handoff | Need working initial kernel, approved privilege, actual KEXEC config, accepted DT/entry ABI and peripheral quiescence | Android-assisted handoff is a research bridge, not the independent finished product. Published Sony config does not explicitly enable KEXEC. No root/module injection or handoff experiment performed |
| Parallel: upstream Linux with authentic Sony board support | QCS2290/PM4125 evidence helps compare drivers; Sony-specific DT/panel/audio/safety and accepted boot chain still missing | Another kernel or removable boot medium does not remove signature requirements. No RB1 addresses/rails or image recipe adopted; a different physical board cannot establish Sony hardware compatibility |

Generic distinctions remain [AOSP locking/unlocking](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking),
[AVB boot flow](https://source.android.com/docs/security/features/verifiedboot/boot-flow)
and [bootloader fastboot versus fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd).
They define questions to resolve; they establish no Sony implementation. No
interface was queried to classify the maintainer's previously reported fastboot.

## Original-board failure coverage

The newly inspected US service manual is byte-identical to M5's preserved copy
and states **product exchange on p. 2**. It documents no original-board restore.
Factory reset, update, recovery reinstall, authenticated service restore, board
replacement and low-level recovery remain distinct. The letter's firmware
authentication statement does not turn an OTA into a factory reconstruction set.

| Failure | Earliest candidate surviving interface | Required accepted artifacts/authentication and unique-state proof | Current status / host-only next route |
| --- | --- | --- | --- |
| Android fails; recovery intact | Stock recovery, only if independently reachable and accepted reinstall supported | Matching accepted package, documented entry/version rules and restored partition list; preservation of calibration/provisioning | No applicable reinstall procedure. Locate model-specific service/image documentation or owner-supplied permitted artifacts; factory formatting is not image restoration |
| Both boot slots fail | Independently intact recovery/loader, if Sony's actual placement allows it | Genuine boot/DT/AVB set and slot/fallback policy, accepted access and unique-state handling | A/B names prove no surviving fallback. Offline image/header/descriptor inventory is prerequisite; no slot experiments |
| Recovery/AVB damaged | Bootloader/service facility independent of recovery, if enabled | Accepted recovery/vbmeta chain, rollback rules and authorized repair mechanism | Fastbootd may share damaged recovery. Need applicable interface/service documentation; no bootloader versus fastbootd assumption |
| GPT/dynamic metadata corrupt | Partition-independent early service entry, if supported | Authentic eMMC layout/programming manifest, accepted programmer, protected-area exclusions and provisioned-state verification | F3 strengthens the eMMC branch, not recovery. Acquire same-board restoration documentation and storage manifest; do not use another unit's GPT |
| Early loader fails | ROM-level/authenticated service entry, if reachable | Sony-accepted matching programmer/stages, board/OEM/security identity, credentials and rollback-compatible resources | No verified entry/programmer. QCS2290 or visible pads cannot justify EDL or bypass attempts |
| Calibration/provisioning lost | Documented Sony preservation/regeneration service, if available | Per-device versus replaceable-data classification, legal backup/restore rights, bound security/RPMB handling and post-restore checks | No such process established. Determine coverage from public/supplied technical materials; do not substitute another unit's keys/calibration |

The [MMC source audit](m7-hardware-convergence.md#new-bounded-source-investigation)
makes a recovery gap more specific: eMMC user-area Android boot slots, hardware
boot areas, EXT_CSD configuration/protection and RPMB are different objects.
Neither an OTA nor a hypothetical user-area dump establishes complete restoration
of all of them. Their actual A306 use remains unmeasured. Preserving bytes cannot
by itself reset replay-protected counters, reconstruct device-bound secrets or
prove accepted rollback. No keys, device reads or low-level tools were acquired.

## Dependency-ordered M8 prerequisites

1. **Selected board/build bundle:** lawfully supplied authentic selected DTB/DTBO,
   boot/recovery/vbmeta, final config/module symbols/signatures, firmware manifest
   and permitted calibration interfaces. Use SODAGREEN/1.03 and component markings
   as search keys, not as equivalent runtime identity. Audit hash/header/phandle/
   memory/ABI conflicts offline before any image construction.
2. **Execution policy:** model/region/revision-specific evidence of accepted
   development or temporary boot, or a supported stock-kernel/rootfs handoff.
   Need exact entry, signature, persistent-state and rollback behavior. Public
   regulatory policy is insufficient; seek publicly released engineering material
   or lawfully supplied owner artifacts.
3. **Original-board recovery proof:** a genuine accepted restoration set and
   procedure covering intended failures, original-board outcome, unique-state
   handling and verification. A written exchange policy cannot satisfy this.
   Supplied service material can be audited on the host without device access.
4. **Safety/interface profile:** authentic panel/touch/audio/battery/thermal/
   watchdog configuration and initialization ownership, reconciled with the
   identified PMIC/cell/codec/storage candidates. Only then implement the selected
   Linux adapter contracts and meaningful synthetic fault tests.

No physical experiment is justified by the present evidence. If supplied
artifacts cannot answer a narrow board-identity question, the smallest later
proposal is a separately reviewed, bounded normally booted characterization
scope based on the existing M5 whitelist, with individual read side effects
and recovery risk reviewed first. It cannot replace missing restoration proof
or validate custom acceptance. Actual boot/restoration would require further
explicit approval and all applicable hardware gates; a spare alone supplies
no recovery or acceptance proof.

## Validation and preservation

All 44 M6 project files were copied and verified in ignored
`build/m7-baseline-20261014/`; manifest SHA-256
`692d50a532d665243000e3771db40d1c87a88805f18b3922a818530307df1bc5`.
It records 2,104 public/private/reference integrity entries, reusing earlier
verified snapshots rather than duplicating the large private trees. M0 records,
all 13 M1 artifacts, source archives/patches, M2/M3/M4 outputs and M5 original/
snapshot files were checked. M6's 42 output hashes and preserved display/PCM/
input/failure captures revalidate successfully. No fresh QEMU playback or codec
benchmark was needed for documentation and the independent inventory tool.

M7 commands/results:

- `python -m unittest discover -s tests -p test_evidence_inventory.py`: 8 pass.
- `python -m unittest discover -s tests -p test_inspect_upg.py`: 10 pass.
- `python -m unittest discover -s tests -p test_linux_safety.py`: 7 pass.
- `tools/evidence_inventory.py --root <FCC-reference-root>`: 43 local records
  agree with acquisition sizes/hashes; 31 catalog digest matches, two full
  metadata matches, 29 size conflicts, 12 without catalog digests.
- Private `build/m7/pdf_audit.py` with bundled Python: all 43/594 PDF pages
  pass independent pypdf/PDFium traversal; visual review described in FCC report.
- Private `build/m7/verify_wsl.py` under Ubuntu-24.04: rechecks 42,518 M5 originals
  and snapshot copies, 41 M2 + 41 native/41 ARM64 M3 + 42 M4 outputs, 20 M5
  inputs and 42 M6 outputs; reruns existing validation of **preserved** DRM/PCM
  captures and all seven VM cases into new M7 result files. No earlier result
  file is overwritten and no device interface is used.

The 10 application / 38 ARM64 codec / 38 native ASan M6 results are retained
historical passes; they were not repeated in M7. Existing chained
Opus, resampling/gapless and ARM64 sanitizer limitations remain unchanged.
