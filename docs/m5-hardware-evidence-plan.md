# M5 authentic hardware inputs and Linux contracts

2026-10-14. The [generic Linux prototype](m5-linux-prototype.md) exercises Linux
ALSA and evdev, not Sony hardware. This plan turns the source-level
[M4 subsystem inventory](m4-nwa306-integration.md) into specific collection and
integration requirements. Its I1–I8 and M3 B1–B6 locators are retained by reference.
Actual GPIO, regulator, gain, mixer, calibration and thermal values remain missing.

## Missing inputs and implementable boundaries

| Subsystem | Authentic inputs required | Linux userspace contract / failure behavior |
| --- | --- | --- |
| Boot/kernel/modules | Matching stock boot/recovery, header/ramdisk and selected DT/overlays; final config, compiler/build IDs, `Module.symvers`, DLKM helper and signature acceptance information | Preserve accepted boot and firmware stages. Published module-signature enforcement adds a loadability gate; generic ARM64 binaries do not satisfy it. Reject identity/ABI mismatches before proposing device execution. |
| Board identity | Sales-region/revision mapping and actual selected DT compatible, chosen nodes, phandles and overlay order | Bind adapters to identified resources, never an assumed card/event number. `icx1301` and YY1301B1 alone do not select a DT. |
| Display/backlight (I3) | Selected SDE/DRM driver, connector/panel, exact DSI commands/timings/rails/reset sequence, scanout formats, rotation and backlight owner/range | Enumerate DRM resources/capabilities; select an actual supported mode/plane/format; use atomic modesetting only if supported. Quiesce scanout and release buffers on failure. Touch orientation must match scanout. No KMS or backlight operation tested in M5. |
| Touch/buttons (I4) | Bound controller, firmware, evdev capabilities, ABS/MT ranges, slot protocol, orientation and physical-key codes/wake policy | Batch updates through `SYN_REPORT`; on `SYN_DROPPED`, discard partial state and resynchronize capabilities/current slots before new gestures. Handle tracking IDs and release state on disconnect. M5 deliberately aborts on dropped events and supports only its synthetic single-contact ABS_X/Y protocol, not arbitrary MT hardware. |
| ALSA frontend/backend (I1) | Actual card/PCM identities, DAI/phandle bindings, supported rates/formats/channels/periods, route/control topology and owner | Negotiate `hw` parameters and verify returned values; handle partial writes, XRUN recovery and disconnect explicitly. M5 exercises SDL's existing ALSA backend on virtio, not a new Sony route. An unsupported rate must be rejected or handled by an explicitly tested converter. |
| DSP/firmware (I7, B1) | Selected PIL/remoteproc path, matching signed ADSP and other peripheral firmware, reserved memory/IPC resources, ACAL ABI and calibration provisioning | Firmware initialization and authentication must succeed before routing. Retain necessary licensed platform binaries independently of Android framework. Do not treat generic Q6 source or PAS calls as accepted firmware. |
| Sony codec/amp/jack (I2, B2/B6) | CXD3778GF revision/type, exact bus/bindings/rails, table hashes/ABI, jack IRQ/wake behavior, mute/gain limits and order | Remain muted until identity, firmware, calibration, route, gain and safety readiness are established. Apply only authentic reviewed controls; loss of readiness requests mute/quiescence. No mixer values or register writes implemented. |
| Music/root storage (I5/I6) | Actual controller, root placement, partition/filesystem/slot metadata, encryption owner and microSD/card-detect policy | Mount only explicitly identified filesystems under reviewed policy; local library reads must tolerate absent/removing media and I/O errors. VM music is immutable initramfs input copied into RAM, not a tested internal/microSD mount or encryption replacement. |
| Battery/charging (B3/B4) | Battery/thermistor profile, calibrated units, safe limits, charger/JEITA ownership and USB/current constraints | Kernel charging protection must stay active independently of Rockbox. Timestamp telemetry with one monotonic clock; absent, nonfinite, future or stale safety inputs revoke readiness. A status display cannot implement charger policy. |
| Thermal/watchdog (I8, B5) | Sensor/calibration/trips, policy ownership, watchdog binding, pet/bark times and suspend interaction | Keep kernel thermal protection. Pet only after critical-service health is verified, using the actual documented interface; never disable watchdogs to mask a failure. Missing owner/policy keeps audio muted. No watchdog opened or petted. |
| Suspend/shutdown (I2/I7) | Dependency order, wake IRQs, charging interaction, DSP stop/ack and PMIC reset/poweroff ownership | Mute, drain/quiesce, synchronize storage, release display/input and request the verified kernel poweroff path. VM clean poweroff and application-failure shutdown do not validate Sony shutdown, battery lifetime or suspend. |

The published Sony config enables several architectures and both Himax and
Sintronix touchscreen families; neither is selected for the actual board by
that fact. The service document supplies no board diagram. See the exact new
source locators and regional service limits in [boot/recovery paths](m5-boot-recovery-paths.md).

## Tested safety-policy increment

`tools/linux_safety.py` is a pure decision function with **no device I/O or
unmute capability**. It requires positive verification of eight ownership/data
conditions plus every configured live reading. No Sony policy or default limit
is shipped: missing policy returns not-ready. Seven tests cover healthy synthetic
inputs, every missing verification condition, absent/stale/future telemetry,
malformed/reversed limits, nonfinite values and invalid clocks.
Battery voltage, battery temperature and SoC temperature policies are all
required; an otherwise plausible policy cannot silently omit a critical reading.

Its dimensionless fixture limits are test data, not battery or thermal settings.
This proves a fail-closed decision boundary, not actual muting or protection.
A future authenticated collector and hardware mute implementation must satisfy
the table above; logging “not-ready” alone would not safely silence an amplifier.
The generic VM explicitly uses a virtual sound card and has no Sony hardware gate
to bypass. Do not transfer that VM exception into a device configuration.

Protocol references: [Linux input event codes](https://docs.kernel.org/input/event-codes.html)
and [uinput](https://docs.kernel.org/input/uinput.html). These describe the generic
event interface; they do not identify the Sony touchscreen or its firmware.

## Proposed characterization requirements

First request supplied board/build/service artifacts and audit existing private
evidence; that can avoid device access. If still necessary, seek a separate
authorization for a normally booted, stable matching device, with the exact
transport, operations, privilege, paths and byte limits reviewed in advance.
Include discovery and transport selection in that reviewed operation plan.

Candidate bounded evidence classes for that review:

- Build/device/slot and supported-unlock **properties only**: whitelist
  `ro.product.device`, `ro.build.version.incremental`, `ro.boot.slot_suffix`,
  `ro.boot.verifiedbootstate`, `ro.boot.flash.locked`, `ro.oem_unlock_supported`.
  A returned property still cannot prove image acceptance or service recovery.
- Selected DT identity and board resource descriptions from supplied DTB/DTBO or
  explicitly approved `/proc/device-tree/compatible`, `/proc/device-tree/model`
  and `/sys/firmware/fdt`; keep the raw tree private because it may contain
  identifiers. No blanket device-tree dump or block partition read is proposed.
- Supplied kernel config/module metadata, or separately reviewed `/proc/config.gz`,
  `/proc/modules` and existing driver-binding descriptions. No module load,
  driver bind/reprobe, privileged escalation or automatic fallback collection.
- `/proc/asound/cards`, `/proc/asound/pcm` and previously identified evdev
  capability descriptions; no PCM opening, audio playback, mixer changes or
  physical input-event recording. Identify the touch protocol before designing
  its adapter. No generic event-number assumptions.
- Existing panel/backlight, power-supply, thermal and watchdog **ownership and
  schema descriptions** from supplied artifacts first. Review any proposed
  live attribute individually: reads may wake hardware or request measurements.
  No bus probes, status polling loop, watchdog open/pet or control writes.

Suggested collection ceilings for review are 64 KiB per text item and 2 MiB
total; a selected DT/config artifact needs its own explicit size exception.
Hash locally, retain raw results outside Git, redact identifiers in summaries,
and never acquire device-bound keys or substitute another unit's calibration.
Stop on unexpected permissions, a path not on the whitelist, unstable behavior,
unknown read side effects or a requested state change. Do not reboot to expose
missing evidence. These are proposed collection limits, not hardware limits.

Before any future custom execution, separately establish model-specific
authorization, restoration covering the intended failures, and reviewed power,
thermal, mute and watchdog behavior. A matching spare reduces exposure of the
primary device but does not waive those gates.
