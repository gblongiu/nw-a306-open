# M9 authentication-boundary model

2026-10-14. **No Sony-specific alternate-execution acceptance mechanism was
established.** Historical locked/green state, official update metadata and
shared module/peripheral verification code are distinct evidence. Actual
boot-image/DT/AVB bytes and accepted init/root-selection policy remain missing.
The [artifact inventory](m9-boot-artifact-inventory.md) bounds those conclusions.

## Boundary inventory tied to available evidence

| Boundary / selecting component | Verified evidence and necessary acceptance condition | Actual Sony-specific gap |
| --- | --- | --- |
| Update distribution to installer | S: manifest version/variant/size/MD5 and eligibility; preserved UPG agrees with transport metadata | Installer authentication, NWWM signed/decrypted ranges and inner member identities U. Transport hash agreement is not a custom-image signature |
| ROM to early firmware | P: Qualcomm ROM-rooted trust architecture; historical stock boot occurred | Exact Sony stage identities, accepted OEM/hardware IDs, fuse state, image ranges, memory initialization and authorized service entry U |
| OS loader to kernel/ramdisk/DT | S: D1 locked/green and boot/DTBO/vbmeta names; P: generic AVB image descriptors can bind these resources | No selected image/header/descriptor graph, root key, rollback location or DT overlay selection. Unchanged kernel does not establish permission to modify its enclosing image or ramdisk |
| DT/boot parameters to kernel init | P: M9-S6 reads `/chosen` bootargs and initrd pointers; M8 init accepts standard init selection | These parsers do not authorize changes to input DT, command line, bootconfig or ramdisk. Actual authenticated coverage and supported mutable inputs U |
| Kernel to modules | P: S published mandatory module signatures, version/CRC/vermagic and PKCS#7 checks (M9-S1; M8 module_signing.c) | Need final config, complete selected module/ABI inventory and accepted key policy. Source availability or GPL rights alone do not make an independently built module loadable |
| Kernel to peripheral firmware | P: M9-S5 candidate PIL loader requests DT-selected firmware and invokes secure authentication/reset, conditionally configured | Need selected loader, firmware files, secure policy, resource/ABI constraints. A conditional shared-source no-auth branch does not establish the selected Sony setting or authorize altering it |
| Kernel to root filesystem | P: ordinary Linux mount/init support; generic AVB/verity can cover filesystem blocks and boot inputs | Selected root placement, dm-linear/verity graph, ramdisk/fstab and permitted alternate-root selection U. A filesystem containing Rockbox is not an accepted power-on route |
| Restoration tool to original board | S: US manual specifies product exchange; no accepted restore set/tool acquired | Surviving independent entry, credentials/accepted programmer, complete compatible images, rollback policy and unique-state preservation U |

M9-S identifiers and member hashes are in the [userspace source table](m9-stock-kernel-userspace.md#new-source-findings).
Qualcomm's generic [2019 overview](https://www.qualcomm.com/media/documents/files/secure-boot-and-image-authentication-technical-overview-v2-0.pdf)
does not select Sony's loader generation or trust metadata. The M7 radio letter
establishes radio firmware policy, not OS unlock, AVB or service authorization.

## Pinned AVB structure reference, not parsed Sony AVB

M9 acquired four files from AOSP **android-14.0.0_r1** through bounded HTTPS
Gitiles TEXT reads. This version is a platform reference, not a claimed match
to Sony's AVB implementation. Private originals are in `build/m9/primary/`;
full URL/date/hash records are in `platform-provenance.json`. The libavb headers
carry permissive MIT-style notices; no upstream code was imported into the
public implementation.

| Reference / SHA-256 | Precisely inspected structure and applicability |
| --- | --- |
| [README](https://android.googlesource.com/platform/external/avb/+/refs/tags/android-14.0.0_r1/README.md), 55,387 bytes; `8177735a7d08d229e7d8995820a322d4079bb783803c2d3f7983b7d6d51e2894` | Lines 46-145: signed descriptors, chained partitions, rollback and A/B; 650-668: platform root-of-trust handling; 850-920: platform rollback storage/update policy. No Sony rollback state or RPMB placement inferred |
| [avb_vbmeta_image.h](https://android.googlesource.com/platform/external/avb/+/refs/tags/android-14.0.0_r1/libavb/avb_vbmeta_image.h), 11,913 bytes; `0979deac8902cbcbd0ec1d2f94af6692ab954fe698b1bd2e8b193b7eec3a3607` | Lines 64-102,124-190 define fixed header, authentication/auxiliary block sizes, descriptor/public-key offsets, algorithm and rollback fields. No actual Sony values recovered |
| [avb_hash_descriptor.h](https://android.googlesource.com/platform/external/avb/+/refs/tags/android-14.0.0_r1/libavb/avb_hash_descriptor.h), 3,127 bytes; `61811399ac8e4ca0392a87039de9edfcaab72d165a346337e87b5fb5c3a4d602` | `AvbHashDescriptor`, `image_size`, algorithm, partition/salt/digest lengths and flags. A boot descriptor can cover kernel plus initramfs; need actual descriptor to establish Sony's covered range |
| [avb_kernel_cmdline_descriptor.h](https://android.googlesource.com/platform/external/avb/+/refs/tags/android-14.0.0_r1/libavb/avb_kernel_cmdline_descriptor.h), 2,949 bytes; `e4fd1da0db2f64c88265992225183981a73788de316f8dfdc53b270b9c865ce5` | `AvbKernelCmdlineDescriptor` carries flags/length and following command-line bytes. Parameters may originate in authenticated metadata; kernel support for reading them does not make them owner-mutable |

A matching boot/DT/AVB bundle must first yield bounded image regions and the
descriptor dependency graph, then applicable root-of-trust and rollback policy.
Offline signature checking against an embedded key alone would not prove that
the physical Sony trusts that key. No generic AVB parser was added merely to
parse synthetic images while the actual selected bytes remain unavailable.

## Decision table: supported facts, invalid implications and candidates

| Claim or candidate | Classification / acceptance condition | Smallest decisive evidence |
| --- | --- | --- |
| Sony kernel can execute non-Android init | P source capability established; actual selected execution U | Authentic ramdisk/root/DT/cmdline inputs plus supported policy accepting independent init selection |
| Accepted stock kernel plus modified ramdisk is automatically accepted | **Invalid implication**: generic hash descriptors can cover both. Actual Sony coverage U, not a demonstrated rejection test | Matching boot/vbmeta descriptor graph and applicable permitted-selection mechanism |
| `early_init_dt_verify` authenticates a Sony board tree | **Contradicted by inspected implementation**: header check and CRC, not a key/signature decision | Selected tree plus proof of its enclosing trust/selection chain; do not repurpose this function as authorization evidence |
| Successful module autoload proves a driver loaded | **Contradicted as a general inference for published settings**: empty static helper can succeed without modprobe | Final built-in/module list, accepted explicit loading path and independently observed readiness under future authorization |
| Fresh update metadata supplies a selected boot bundle | **Contradicted by inspected manifest scope**: one outer distribution and version rules, no inner images/DT/AVB graph | Applicable decoded-member manifest or independently supplied selected images |
| Sony-supported engineering/development execution | Supported concept, A306 implementation U | Applicable documentation identifying accepted entry, images, restrictions and restoration |
| Official unlock / owner-key enrollment | Generic capability, A306 support U; historical OEM switch/fastboot report insufficient | Model-specific implemented trust-transition policy, effects, accepted images and reversal/restoration |
| Documented temporary alternate-kernel boot | A306 entry/signatures/side effects U | Actual applicable loader documentation and accepted image/DT handoff; fastbootd cannot stand in for an independent early entry |
| Authenticated service execution | Could support restoration, not necessarily custom execution; A306 facility U | Same-board capability statement, accepted tool/image set and rights explicitly covering intended operation |
| Authorized kernel handoff/kexec | Optional ARM64 source, not explicitly enabled in published defconfig; final config/privilege/policy U | Actual final config and authorized handoff contract; Android-assisted launch alone misses independent power-on objective |
| Upstream kernel with Sony bindings | Related platform source exists; A/B/C gates still U | Authentic selected resources, supported drivers/firmware, accepted image policy and original-board restoration |

The preferred research candidate remains **accepted stock kernel plus independent
init**, because shared source and generic Rockbox already establish useful
interfaces. It remains a conditional contract, not an executable deployment
approach. If actual authenticated inputs are immutable without supported owner
selection, acceptance research must move to a documented engineering/unlock/
service mechanism rather than modifying verification. Nothing in this result
establishes impossibility of the long-term objective.
