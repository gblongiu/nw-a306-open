# M9 original-board recovery readiness

2026-10-14. No new model-specific restoration facility was acquired or verified.
The [M8 failure-state assessment](m8-recovery-assessment.md) and original US
service evidence remain intact. M9 adds route-specific failure dependencies and
narrows why a working stock kernel or a transport update is insufficient.
No recovery procedure was validated in M9.

## Source-specific restoration acceptance matrix

| Failure | Evidence actually available | Independently surviving restoration prerequisites / objective acceptance |
| --- | --- | --- |
| Android fails, recovery intact | Historical D1 recovery names; fresh Sony manifests require firmware `<3.06`, not proof of same-version recovery reinstall | Applicable reachable recovery independent of failed Android; accepted matching package/version policy and repaired partition list; original board preserved, stock verified boot and hardware/safety functionality restored |
| Both boot slots fail | Historical A/B names and slot `_b` only; no fallback-control bytes or test | Accepted surviving loader/recovery independent of both failed kernels/ramdisks and shared metadata; genuine boot/DT/AVB set plus actual slot policy. Confirm intended slot/fallback behavior after restoration |
| Recovery or AVB failure | vbmeta/recovery names, no authentic descriptor graph or lower-loader repair facility | Entry not dependent on damaged recovery or trust metadata; accepted image chain and rollback-compatible repair rights. Restore authentic verification and independently reachable recovery |
| GPT / partition / super metadata failure | eMMC certification-sample evidence; no GPT, super map or reconstruction set | Partition-independent authorized service entry, genuine layout/images, region/protection handling and excluded unique state. Validate correct maps, images and stock boot on the original storage/board |
| Early loader failure | Qualcomm ROM trust architecture generic; no applicable Sony ROM service entry/programmer | Accessible authenticated original-board service execution, matching memory/board/security policy and accepted early stages. Restore genuine chain without replacing motherboard or protected identity |
| Unique calibration / provisioning lost | Shared ACAL/table consumers and persist lookup, no selected data classification or regeneration process | Applicable lawful preservation/regeneration service and device-bound-state treatment, including counters/keys where used. Restore Sony-defined calibration/safety and identity-bound operation; another unit's bytes cannot establish this |

Sony's [2024-06-15 US manual](https://research.encompass.com/SON/rr/NWA306_B.pdf),
p. 2, specifies **product exchange**, not original-board recovery. Its preserved
SHA-256 is `a8a0381fbcff9539b16ba98b8615bf5d10b5e10a8544279db3ae09167a77359f`.
It neither documents another region's policy nor excludes an internal factory
facility. All lower-stage restoration possibilities in this matrix remain U.

Official update, factory reset, recovery reinstall, bootloader restoration,
authenticated service repair and product/board replacement are different
capabilities. The fresh manifest recheck supplies update metadata only. eMMC
hardware boot areas and configuration, user partitions and RPMB remain separate
preservation scopes. No accepted programmer, complete restore image, transferable
protected state or no-risk RAM execution is inferred.

## Execution route to failure coverage

This table identifies possible consequences to cover before a later experiment;
it does not prescribe writes or claim all effects would occur.

| Proposed route | Failure states that must be addressed | Required independent survivor and missing proof |
| --- | --- | --- |
| Stock kernel + independent init/root | Failure to mount/map files, firmware wait, absent modules, thermal/watchdog ownership or mute/shutdown failure; persistent image edits could affect boot/recovery/AVB | Supported accepted userspace selection, preserved stock chain and applicable recovery outside altered resources. M9 module no-op and custom firmware fallback findings make explicit readiness/failure handling essential |
| Supported temporary/engineering image | Kernel/DT/resource errors can mismanage power or storage; software can alter persistent state even if delivered to RAM | Documented side effects and accepted handoff plus same-board restoration covering possible writes and power failure. Volatile image location is not proof of reversibility |
| Official unlock / owner-key enrollment | Security-state transition, erasure, relock/rollback or protected-state consequences depend on implementation | Applicable transition/reversal policy and accepted complete restoration with unique-state treatment; none established for A306 |
| Service/factory execution | GPT/early-image/provisioning impact depends on authenticated tool scope | Documented accepted service entry and reconstruction scope, original-board outcome and calibration preservation. Generic Qualcomm programmers/EDL are insufficient |
| Kernel handoff or upstream kernel | Driver quiescence, wrong DT, firmware/power ownership, crashes; writes depend on image behavior | Accepted execution and recoverable initial chain plus board-safe resources. A surviving Android-assisted first kernel would not itself fulfill independent startup |

The minimum-userspace verifier tests dependency refusal and desired shutdown
ordering only. It cannot establish that a mute, storage synchronization,
watchdog handoff or poweroff adapter works. Source-level explicit module loading
also requires accepted modules, privilege and actual completion; it is not
a restoration mechanism.

## Readiness decision and minimum proof set

No future physical procedure is justified by the current evidence. To evaluate
one, require all of: model/build-bound accepted artifacts; documented supported
execution and persistent effects; selected hardware/safety configuration;
surviving-entry graph independent of intended failures; genuine complete
restoration resources for that scope; unique-state preservation/regeneration
terms; and objective original-board stock/security/hardware acceptance criteria.
A matching spare may support later authorized validation but supplies none of
these proofs by itself.

The smallest useful recovery acquisition remains an applicable same-board
capability statement identifying supported failure classes, accepted tool/image
IDs, access rights, rollback restrictions and provisioning treatment. Public or
already lawfully supplied material may be audited on the host. The
[previous Sony inquiry](m5-boot-recovery-paths.md#final-concise-sony-inquiry-unsent)
records the outstanding service questions and remains unsent. Any physical
characterization or restoration requires an explicit operation plan and approval.
