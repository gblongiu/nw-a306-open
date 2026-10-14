# M7 target hardware contracts

2026-10-14. The [FCC review F1-F12](m7-fcc-evidence.md#visual-observations-and-confidence)
converts several generic hardware leads into identified certification-sample
components. It does not identify the owner's selected tree or validate runtime
compatibility. Original [M3 B1-B6](m3-board-dependencies.md#exact-new-source-locators)
and [M4 I1-I8](m4-nwa306-integration.md#exact-new-source-locators) remain the
precise Sony source references; actual GPIO, rail and routing values remain missing.

## Convergence matrix

| Subsystem | New target evidence / status | Linux dependency and implementation-ready requirement | Missing authentic input / acquisition route |
| --- | --- | --- | --- |
| Board/configuration | F1: SODAGREEN M/B 1.03 on sample; owner revision unresolved | Select configuration by authentic DT compatible, overlay order, board/revision/region and build hashes. Reject identity conflicts before enabling peripherals; a silkscreen label alone cannot select DT | Supplied selected DTB/DTBO, final config/chosen/reserved-memory and revision map. Public schematic remains withheld; future approved supplied-artifact or characterization route only |
| CPU/kernel/modules | F2: QCS2290 corroborates D1; published Sony 4.19.157 source/config only | AArch64 Linux remains preferred. Match compiler/config/module symbols and accepted module signatures; retain needed firmware and critical protections | Boot headers/ramdisk, final config, Module.symvers, external DLKM build input and signing acceptance. No target kernel/modules built or loaded |
| Internal storage | F3: Samsung KLMBG2JETD, manufacturer family maps to 32 GB eMMC; controller configuration still unresolved | Prioritize MMC/SDHCI-MSM path (I5) over UFS for this sample. Identify user area, hardware boot regions and RPMB separately; bind mounts by verified partition identity, never guessed mmc numbering | Authentic SDHC DT, pinmux/rails/bus width, matching GPT/dynamic metadata, boot-region configuration and encryption ownership. Photos do not establish HS400 operation or partition contents |
| microSD | F9: actual socket and connector assembly | Separate removable-card ownership from root/unique-state storage; handle absence/removal and I/O failure. Card-detect/power/suspend policy must be explicit | Selected controller, detect polarity, rails and filesystems. Existing RAM-library tests are not hotplug validation |
| PMIC/battery/charging | F4 PM4125; F8 LIS1650 label/protection PCB | Audit PMIC/SPMI/regulator and QG/SMB5 dependencies (B3/B4). Require validated battery-profile identity, thermistor units and policy owner; keep kernel protection independent of Rockbox | Authentic PMIC tree, cell profile/JEITA/thermal/current limits and battery-ID mapping. Printed 4.2 V is a cross-check, not a complete safe charging configuration |
| Display/backlight | F10: physical assembly/flex; resolution remains Sony product specification | Use capability/mode/format negotiation and present-completion lifecycle; begin dark, enable reviewed backlight only after display and safety readiness; fail dark/quiescent | Actual panel/controller, DSI commands/timings/rails/reset, orientation and backlight owner/range. M6 virtio KMS remains generic validation only |
| Touch/buttons | Physical keys and POWER-ON marking visible; touch controller not resolved | Derive ABS/MT protocol, ranges, orientation and key codes from authentic bindings/capabilities. Apply one documented affine/axis mapping to display and input; release contacts on disconnect/lost synchronization | Selected controller/firmware/IRQ/reset, touch ranges/slot protocol and wake bindings. Neither configured Himax nor Sintronix is selected by source presence |
| Sony audio/amp/jack | F6: U2504 marked 3778, strong CXD3778GF-family correlation; F9 jack | I1/I2 and B1/B2/B6 define DPCM/MI2S/ACAL/table/mute interfaces. Require authenticated DSP readiness, accepted calibration/table ABI, real routes and bounded gain before unmute | Selected TYPE_A/Z, phandles/bus/GPIO/rails, genuine tables/calibration, control topology and jack IRQ/wake. Visible oscillators do not establish clock routing or safe gains |
| DSP/peripheral firmware | QCS platform and shared loader source; matching binaries still missing | Preserve loader/authentication, reserved memory, IPC/clock/reset and stop acknowledgements (I7). Firmware acceptance is independent of Android kernel image acceptance | Authentic signed firmware manifest and permitted provisioning, ADSP/calibration versions and initialization owner. No RB1 firmware names or addresses transferred |
| Wireless | F7 WCN3950 family + F11 antenna; certification-specific regulatory constraints | Optional for initial wired system; leave disabled until authentic firmware/calibration/regulatory ownership established. Shared rail dependencies still require audit | Actual bus/ICNSS/firmware/NV board data and coexistence policy. FCC radio test toolkit is not firmware-loading or boot permission |
| RAM | F5 Micron package; exact part/density unresolved | Use accepted loader/DT memory map, reserved regions and kernel resources; do not program memory-controller training from a guessed FBGA code | Legible part/BOM and matching boot/DT memory definition. Generic VM RAM size is not target RAM evidence |
| Thermal/watchdog/suspend/shutdown | No selected sensors/trips/owners newly resolved | Preserve TSENS/calibration and watchdog ownership (B5/I8); safety service outlives UI. Order mute, DSP/audio quiescence, storage synchronization, display/input release and verified poweroff | Authentic trips/calibration, pet/bark ownership/timing, wake/charger interaction and PMIC shutdown. No physical safety interface operated |

## New bounded source investigation

SODAGREEN, LIS1650, US454261, PM4125 and WCN3950 are newly justified search terms.
Pinned Sony archive S was streamed read-only: **389 ARM64 DTS/DTSI members plus
six selected kernel/config/audio members, 3,154,636 bytes total**, each hashed.
No filename contains those five names and none appears in the selected content.
Per-member bound was 500,000 bytes, aggregate bound 30 MiB; no full extraction,
archive mutation or duplicate release download occurred. This narrows the search
to absent selected board/build artifacts; it is not an exhaustive all-source
string search or proof that unnamed equivalents cannot exist.

Two selected MMC members add a concrete recovery requirement:

| Sony S member | Exact observation / SHA-256 |
| --- | --- |
| `kernel/msm-4.19/drivers/mmc/core/mmc.c:496-507,544-549,617-622` | Conditional creation of hardware boot areas from EXT_CSD, boot protection and RPMB. SHA-256 `836724a3aabb623ed8274b4810e520c780373abcc80fd1acd10544454632ad84` |
| `kernel/msm-4.19/drivers/mmc/core/block.c:220-226,2666-2685` | Boot protection state and separate handling of RPMB areas. SHA-256 `94e3142a0735713aa7d768213c7fc4d3be0ca5eefe307c01ce9150072b71038a` |

Thus Android `boot_a`/`boot_b` names must not be confused with eMMC hardware
boot regions. A user-area/GPT copy cannot automatically establish preservation
of boot configuration or replay-protected provisioning. Actual enabled regions,
sizes and contents are unknown; no EXT_CSD or device read was performed.

Pinned upstream v6.12 QCM2290/RB1 resources from M6 remain platform analogues.
PM4125's visible presence strengthens comparison of PMIC support, but does not
permit reuse of RB1 regulator consumers, sensor assignments or charger settings.
Public searches for the new codename and A306 DTBO/build resources supplied no
selected Sony tree, programmer or restoration set. The Samsung old part URL
redirects to a family page and its Avnet brief direct download failed; these
bounded results are recorded, not retried indefinitely. No new source release
was downloaded merely to repeat M6's family inventory.

## Data requirements before adapter implementation

The minimal stack remains an accepted vendor-compatible kernel/DT, necessary
licensed platform firmware/data, a small safety/init supervisor and Rockbox.
Android framework is not a planned dependency; essential initialization it owns
must still be identified and replaced. The next implementation should consume
an authentic board profile with explicit evidence hashes, not default guessed
values. Preconditions are:

1. Board/build/overlay identity and compatible kernel/module/firmware set agree.
2. Kernel power, charging, thermal and watchdog ownership are established before
   application display or audio enablement. Unknown ownership keeps readiness false.
3. Display mode/orientation and input mapping share the same verified coordinate
   contract; no assumption that the existing 320x480 guest maps to Sony's panel.
4. Audio route/calibration identity, DSP readiness, jack state and bounded gain
   are verified while muted. On loss of readiness, mute/quiesce independently
   of UI success. A logged failure alone is not hardware protection.
5. Storage mounts exclude unidentified unique/provisioned areas; shutdown uses
   the authentic dependency order and poweroff interface.

The existing seven fail-closed safety tests pass on synthetic data. Implementing
these contracts requires the authentic board inputs listed above.
