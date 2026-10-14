# M6 custom Linux execution assessment

2026-10-14. **No NW-A306 custom-boot mechanism is verified.** The generic ARM64
Linux/Rockbox system now has DRM scanout as well as ALSA/input. Those interfaces
do not grant execution on Sony hardware. This assessment ranks evidence requests
and future investigations. It contains no executable device procedure.

## Established constraints and narrowed uncertainty

Historical D1 reports locked/green state and A/B partition names. The maintainer's
OEM switch and working fastboot report neither identify bootloader versus
userspace fastboot nor demonstrate an accepted alternate image. Sony's
[Open Devices page](https://opendevices.sony.net/supported-devices-and-functionality)
still describes Xperia devices; no A306 entry was found. This is a limit of that
published program, not proof that private engineering support cannot exist.

The [earlier-release comparison](m6-board-artifact-inventory.md) supplies no
new selected Sony ARM64 tree. Both published configurations force module
signatures and enable multiple platforms; stock-kernel reuse therefore needs
the correct built-in/module set and accepted signatures, not merely a compiler.
The original [M5 SCM/PAS source findings](m5-boot-recovery-paths.md#authentication-separate-gates-specific-missing-artifacts)
also keep peripheral-firmware acceptance separate from kernel acceptance.

Three independent inputs are required: **permission/accepted execution**, a
**compatible kernel/DT/firmware handoff**, and **recovery for the possible
failures**. Recovery tooling can reinstall stock yet reject custom code.
Possession of an OTA, signed stock kernel or matching spare proves none of the
three by itself. The NWWM body remains opaque; it supplies no verified boot-image
header, DT inventory, AVB descriptor, rollback value or signing credential.

[AOSP lock state](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking)
distinguishes support from unlock permission and describes a destructive unlock
transition generically. [AVB boot flow](https://source.android.com/docs/security/features/verifiedboot/boot-flow)
requires an accepted trust chain. Neither document selects Sony policy.
[Fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd)
may share recovery's kernel and userspace, so a reachable fastboot-like interface
cannot be assumed to survive recovery failure. No command or mode query was run.

## Ranked decision matrix

Rank orders the next information to obtain, not measured probability of success.
All candidates remain unverified for A306.

| Rank / mechanism | Authorization, image and hardware prerequisites | Android / writes / failure and recovery | Evidence that would advance a decision |
| --- | --- | --- | --- |
| 1. Sony-authorized development image or temporary alternate kernel | Written model/region/revision approval; accepted signer/container, handoff ABI, real DT/overlays, firmware and safety ownership | Prefer independent power-on path. Temporary execution may avoid an intentional image write but still run storage/power drivers; actual counters/state side effects unknown. Need same-board recovery if execution hangs or corrupts state | Sony identifies supported interface, artifact/tool IDs, constraints and failed-state coverage. Audit a supplied accepted image/header/tree offline before a separately reviewed spare experiment |
| 2. Accepted stock kernel with independent minimal userspace | A supported way to select/change initramfs/rootfs within the authenticated chain; correct DT/firmware, built-in drivers or signed modules, compatible userspace UAPI | Can meet the objective only if boot selection works without Android. A new rootfs or ramdisk can invalidate authentication even when kernel bytes are unchanged. Placement/writes and restore requirements depend on supplied descriptors | Matching authentic boot/recovery/vbmeta/DTBO and final config/module/signature metadata. Map signed ranges, ramdisk ownership, command-line policy and essential Android-owned initialization; source config alone cannot resolve them |
| 3. Official model-specific unlock or owner-key enrollment | Explicit A306 support and legal authorization, supported key model, critical-partition/rollback policy, compatible signed/accepted image set | Independent boot potentially possible. Unlock/key transitions may erase data/change persistent protected state. Relocking an incompatible chain can prevent boot; same-unit provisioning/restoration must be established first | Sony's exact supported model/region list and documented consequences. An OEM UI switch or generic Xperia instructions is insufficient; no probing is proposed under M6 |
| 4. Documented temporary boot through retail loader | Accepted image/signature policy and enabled implementation; header/ramdisk/DT placement and memory handoff | Does not necessarily require Android if a boot-time entry exists; none established. “RAM-only” describes intended placement, not proof of no writes or safe peripherals. Need entry and restoration independent of the attempted kernel | Device-specific loader documentation or an authentic supplied loader's permitted offline interface analysis, plus a signed image and recovery coverage. Generic fastboot protocol support is only a hypothesis |
| 5. Authenticated service/factory engineering route | Genuine Sony-authorized tool/programmer, credentials/session policy, board/security identity, image manifest and permission to execute a development payload | May survive Android/recovery loss if its entry stage remains intact. Restoration normally writes storage; actual access/signature policy may permit stock restoration only. Must preserve unique state | Written original-board restoration capability for each failure row in the recovery report, exact supported tool/image IDs and access terms. Do not substitute a generic QCS2290 programmer or infer acceptance from matching SoC |
| 6. Authorized kexec / privileged transition | Working initial OS, approved privilege, actual running KEXEC configuration, entry ABI/DT, driver/DSP quiescence and safety continuity | Requires a functioning initial kernel; Android-assisted handoff is a research bridge, not independent power-on. RAM handoff can hang or misinitialize peripherals; state effects/restore still need review | Published Sony config has no explicit KEXEC enable; actual config/privilege unavailable. Obtain supplied final config and policy first. No root, module injection or approximate driver shutdown implementation |
| Parallel: upstream Linux / reference hardware | Pinned upstream QCM2290/RB1 data offers driver comparisons; Sony DT/panel/codec/PMIC/firmware and accepted handoff still required | Changing Linux version or boot medium does not change Sony authentication. Another development board can validate interfaces but cannot validate this Walkman's audio/power or recovery | Compare authentic Sony board inputs with upstream bindings when acquired. Procurement or any physical experiment needs its own authorization; do not adopt RB1 GPIOs, modem firmware or image recipe |

The retained minimum is a vendor-compatible kernel/DT with necessary licensed
firmware, minimal supervised userspace and Rockbox. Upstream migration remains
an alternative after a resource-by-resource comparison. The newly pinned RB1
tree explicitly identifies another board and HDMI bridge; it is not a shortcut
to Sony panel support or a ready boot recipe. Booting from microSD still requires
an authorized loader path and does not bypass the root of trust.

## Smallest decisive next investigations

1. Resolve the [service-capability questions](m6-recovery-engineering.md#sony-inquiry-unsent) from applicable documentation or a separately approved inquiry.
   The first answer should distinguish same-board restore from exchange and
   accepted development execution from stock-only service flashing. No message
   has been sent.
2. Acquire the located public regulatory photo exhibits through an accessible
   channel and verify their bytes/applicability. Use them to request the named
   schematic revision and selected board artifacts, not to infer undocumented
   electrical settings. M7 records the subsequent photo review.
3. If supplied boot/DT/config material remains unavailable, propose one bounded
   normally booted characterization session using the existing
   [M5 whitelist](m5-hardware-evidence-plan.md#proposed-characterization-requirements).
   Transport, privilege, individual read side effects and byte limits need
   separate device approval. DT identity/config cannot prove custom acceptance.
4. Only after matching artifacts, authorization and recovery coverage exist,
   review a matching spare's exact operation. Preserve calibration/provisioning
   under a documented method first. A spare is a validation resource, not an
   exemption from recovery gates or permission to experiment.

The archive search found no selected board tree, and the exhibits remained
inaccessible in M6. M7 records their subsequent acquisition and photo review.
