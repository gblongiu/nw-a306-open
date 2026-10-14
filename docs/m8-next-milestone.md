# M8 completion and focused M9 proposal

2026-10-14. Historical M8 results and M9 proposal. The minimal Linux/Rockbox
objective remains intact; no deployable Sony image was produced. Subsequent
[M9 results](m9-next-decision.md) are recorded separately.

## Completed engineering increment

- The [boot/storage model](m8-boot-storage-architecture.md) separates actual Sony
  observations from component capabilities and unknown loader selection. It
  explicitly models eMMC regions/configuration, A/B, GPT, super, AVB and RPMB.
- The [source/artifact audit](m8-board-firmware-artifacts.md) adds locally hashed
  Samsung/Qualcomm references and pinned PM4125/MMC/regulator sources. Targeted
  Sony init, firmware and module inspection identifies exact non-Android startup
  and file/event/authentication contracts. No selected Sony DT or image was found.
- A bounded EXT_CSD revision-8 file reader and eight synthetic tests turn the
  storage distinction into usable host tooling. No capture or command to obtain
  device data is included. Three NWWM stored-byte SHA-224 hypotheses were rejected;
  the original package hash still matches and its body remains opaque.
- The [execution matrix](m8-execution-paths.md) prioritizes selected stock-kernel
  artifact/acceptance research; the [recovery matrix](m8-recovery-assessment.md)
  separates six failure states and their surviving-stage/unique-state dependencies.

No new owner-hardware observation or accepted execution/restoration capability
was established. These results narrow interfaces and evidence requirements;
they do not solve the deployment gates.

## Proposed M9: selected-image and initialization contract

The most important missing input is an **authentic selected NW-A306 build bundle**:
boot/recovery/DTBO/vbmeta as actually applicable, any vendor-boot image only if
present, final config/build identity, module/firmware inventory and original
init/fstab metadata. Start with a small provenance-bound boot/DT/AVB sample and
manifest. Require build/region applicability before treating it as the owner's
configuration. This acquisition has more immediate research value than another
generic QEMU demonstration or an undirected shared-source download.

Legitimate routes, in order: publicly released Sony build/development/service
artifacts; a permitted existing owner-supplied artifact set with acquisition
provenance; separately authorized Sony service/platform inquiry if public
sources cannot supply it. Do not acquire protected secrets, borrow calibration
from another unit, interact with a device or infer permission from this proposal.

Proposed host-only M9 tasks:

1. Validate origin/hashes/model/build, then inspect image bounds, versioned
   headers, AVB descriptor graph, ramdisk/rootfs coverage, DT/overlay selection
   and dependencies. No image creation/signing/writing. If files remain opaque,
   request the smallest documented manifest/member sample rather than inventing
   structure or weakening authentication.
2. Audit selected init/fstab/firmware services against S's direct lookup, uevent,
   PIL, module and safety contracts. Produce the actual independent supervisor
   dependency order, identifying proprietary-only pieces and replaceable Linux
   interfaces. Implement fault tests only for authentic interfaces or explicitly
   synthetic contracts.
3. Compare selected PMIC/SDHCI/display/audio bindings with the pinned vendor and
   upstream sources. Reject inconsistent ABI/phandle/firmware/build inputs;
   preserve actual board values privately where necessary. Do not import RB1
   constants or generate a Sony DT from package markings.
4. Pair the artifact graph with an applicable accepted-execution policy and
   original-board restoration statement. Determine which candidate can progress
   to a separately reviewed experiment; finding compatible files alone is
   insufficient.

If acquisition remains blocked, finite host work can still trace the published
PIL/sysfs firmware consumer and module ABI contracts, or test an artifact parser
against an independently documented format. Avoid another all-unknown board
profile or a synthetic model presented as the selected Sony configuration.

The decisive next result would be a provenance-bound bundle identifying actual
kernel/DT/init and authenticated ranges, or an applicable written statement
establishing or excluding supported independent userspace selection. A documented
same-board recovery set is a separate requirement. Contact, normally booted
characterization, spare-device work and any custom execution each need their
own explicit scope and safety review. The Sony inquiry stays unsent.

## Validation and preservation

All **49** project files were copied and verified in ignored
`build/m8-baseline-20261014/`. Manifest SHA-256:
`6761bbfd109d4fc53ad80a40a5becbad09e1d8af7a1dda08c9506c419f338ef6`.
It also hashes all 142 existing M7 private files and reuses 2,060 M7 integrity
records, avoiding duplicate large snapshots. M0's 318 records, all 13 M1
artifacts, pinned original archives and preserved M3/M4 Windows evidence pass.

Windows unittest discovery: **33 pass** (8 new EXT_CSD, 8 evidence inventory,
10 UPG and 7 safety tests). The eight new tests also pass under WSL Python.
Private `build/m8/verify_wsl.py` redirects previous read-only verification outputs
into M8: 42,518 M5 original/snapshot file records, 41 M2 + 41 native/41 ARM64 M3
outputs, 42 M4 outputs, 20 locked M5 inputs and all 42 M6 reproducible outputs
pass. All 15 locked M3 toolchain packages retained in M6 inputs also match.
Preserved M6 DRM/PCM/input/error/shutdown captures revalidate; this is
**not a fresh VM or codec run**. Historical 38 codec/10 application/native ASan
results and their documented limitations are retained, not restated as M8 runs.

FCC classifications remain **43 PDFs / 594 structurally validated pages**, 31
catalog digest matches (29 with a two-byte size metadata conflict), 12 without
catalog digests, zero historical structural failures. M8 verifies preserved
hashes and inventory rather than repeating traversal of all pages. A size
metadata conflict is not a failed checksum. No FCC/reference originals changed.

Detailed checks and preservation records remain private under `build/m8/`.
