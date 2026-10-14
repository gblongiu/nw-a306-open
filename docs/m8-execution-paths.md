# M8 independent execution assessment

2026-10-14. **No accepted independent NW-A306 Linux execution mechanism is
established.** M8 nevertheless narrows a useful candidate: the published Sony
kernel can start a non-Android init and load firmware from files/events. That
is a source property, not permission to select a replacement ramdisk/rootfs.
The [board audit](m8-board-firmware-artifacts.md) supplies exact locators/hashes.

## Three independent gates

**A, accepted execution:** authentic model/build-specific loader policy must
accept the intended kernel, DT, command line and userspace container, with
documented rollback and persistent-state effects. Historical locked/green state
does not tell us which bytes may be replaced. **B, compatibility:** selected
kernel/DT/modules/firmware and initialization/safety policy must actually match
the Sony board. **C, original-board restoration:** an applicable accepted set
and surviving entry must cover the intended failure states and unique state.
None of these gates is satisfied by passing another. No candidate passes all
three today. The [recovery assessment](m8-recovery-assessment.md) defines C.

## Stock-kernel alternative: the new concrete constraints

Sony S's `init/main.c` can execute `/init`, `rdinit=` or `init=`; it contains no
requirement that this executable be Android init. `init/initramfs.c` can unpack
built-in and externally supplied early userspace. Thus a source-level Android
requirement at the kernel-to-init boundary is **not supported**. Selection of
an alternative init is still U: no authentic boot header, enclosing AVB
descriptor graph, accepted command-line policy or selected rootfs was obtained.
Editing only a ramdisk could invalidate the chain even with an unchanged kernel.
[AOSP boot headers](https://source.android.com/docs/core/architecture/bootloader/boot-image-header)
describe possible layouts; Android 14 alone cannot choose Sony's actual one.

The minimal candidate is an accepted vendor kernel/DT/firmware set plus an
independent supervisor that mounts required filesystems, supplies selected
modules/firmware/calibration interfaces, starts safety owners and then Rockbox.
Keep Rockbox the primary interface; making it bare PID 1 before those owners
exist would leave process reaping, failures and power lifecycle unaddressed.
This is an implementation dependency proposal, not an image recipe.

Direct firmware delivery can avoid Android services **where** the correct file
is available at probe time. In S the search includes `/mnt/vendor/persist` and
`/lib/firmware`; fallback may require an event consumer. Empty static helper
does not suppress that path. The selected manifest must identify which loads
are direct, event-driven, secure PIL or proprietary-service mediated. Mandatory
module signatures, ACAL ABI/tables, secure peripheral authentication and safety
owners remain required. M8 did not establish that Sony's complete drivers work
without proprietary userspace. Generic M6 ALSA/KMS/evdev evidence remains valid
at application/interface level only.

## Ranked research decision matrix

Rank means value of the **next evidence acquisition**, not estimated deployment
success. Authentic selected images are first because they can resolve several
candidates simultaneously. Each row still requires A/B/C and separate approval
for any future device operation. No bypass or exploit is proposed.

| Rank / candidate | Actual support and Android-free fit | Missing acceptance, compatibility and restoration prerequisites / complexity | Smallest next proof; continue or redirect criterion |
| --- | --- | --- | --- |
| 1. Accepted stock kernel + independent userspace | Authentic S init/firmware interfaces and historical stock Linux boot; fits objective if selected at power-on | A: signed ramdisk/root/cmdline ranges and supported selection. B: final config/DT/modules/files/service owners. C: genuine stock restore and preserved unique state. Integration smaller than replacing all vendor drivers, still substantial | Obtain matching boot/recovery/DT/AVB and init/fstab/firmware manifest. Continue if an accepted independent selection is documented; if every selection input is protected with no supported replacement, redirect acceptance research rather than patch verification |
| 2. Sony-supported development / engineering image | Manufacturer controls official firmware; no applicable development entry established | Need documented A306 entry/signer/build/DT/resources and original-board failure coverage. Could start independently; supplied support could reduce integration uncertainty | Public or lawfully supplied model-specific development documentation/image. Continue only if acceptance and exact rights are established; absence in Open Devices bounds that program alone |
| 3. Authenticated factory/service execution | Sony service publication exists, but US manual specifies exchange | Stock restoration is distinct from permission to run custom userspace. Need accepted tool/image/credentials, independent surviving entry and provisioning preservation; high dependency on unavailable resources | Applicable same-board service capability statement plus artifact/tool identifiers. Continue recovery branch if only stock restore is supported; custom execution needs separate proof |
| 4. Official unlock / owner-key enrollment | Generic AOSP capability; no A306 implementation identified | Need implemented authorized trust transition, erasure/relock/rollback effects, key model, matching images and recovery. Could support independent Linux; persistent security effects U | Applicable Sony policy or authentic loader documentation. Reject Xperia instructions as A306 evidence; keep candidate unresolved until model-specific proof |
| 5. Documented temporary alternate-kernel boot | Protocol family known generically; maintainer's historical fastboot report does not classify implementation | Need independently reachable loader, accepted RAM image/DT/ABI and side-effect guarantees. No-write intent does not make bad power initialization safe or guarantee no counters change | Applicable implementation documentation or supplied authentic loader evidence. Continue only with accepted entry and recovery coverage; fastbootd alone cannot establish it |
| 6. Upstream Linux + authentic Sony board support | v6.12 related SoC, PMIC, SDHCI/display/PAS interfaces available | Still needs A and C; B additionally needs authentic Sony bindings, panel/audio/calibration and driver gaps. Highest hardware porting burden among independent kernel options | Selected DT/firmware/resource graph compared with upstream bindings. Continue supported subsystem adapters; do not transplant RB1 pins, firmware or rails |
| 7. Authorized kernel handoff / kexec | Optional ARM64 source; published config does not explicitly enable KEXEC | Requires accepted initial kernel, privilege/policy, actual config, DT/entry ABI and peripheral quiescence. Android-assisted handoff alone misses power-on independence; recovery still needed | Authentic final config and supported handoff policy. Deprioritize if unavailable or Android-dependent; it could be a future authorized bridge, not the final system |

Generic reference boundaries: [locking/unlocking](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking),
[bootloader versus fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd),
[verified boot flow](https://source.android.com/docs/security/features/verifiedboot/boot-flow).
Sony's [supported-device publication](https://opendevices.sony.net/supported-devices-and-functionality)
still supplies no NW-A306 entry. These sources establish no usable Sony command.

## Decision after M8

Retain the minimal Linux/Rockbox architecture. Prioritize the stock-kernel
**artifact and acceptance audit**, with Sony-supported engineering execution
as an independent acquisition track. The new source findings make the former
more technically specific but do not establish installation permission or
runtime compatibility. Upstream interface comparison remains worthwhile for
maintenance and missing-driver analysis once selected board data arrives.

Missing boot/recovery documentation limits physical testing. The next required
input is the authentic selected-image/descriptor/DT bundle and its model/build
binding, followed by an accepted selection/restoration policy. See the
[historical M9 proposal](m8-next-milestone.md) and [M9 results](m9-next-decision.md).
