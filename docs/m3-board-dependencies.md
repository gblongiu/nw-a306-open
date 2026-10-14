# M3 firmware, board dependencies and recovery investigation

Date: 2026-10-13. This extends the preserved M0-M2 evidence without device
access. No boot/recovery image, key, board DT or calibration was obtained from
the Walkman. The [AArch64 execution results](m3-aarch64-bringup.md) validate
generic software only; source availability remains distinct from target binding.

## Firmware-container follow-up

The preserved candidate still matches size 1,589,253,264, manifest MD5
`a785c3d360bca2c0fd81f4182c9bec8b` and SHA-256
`50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643`.
The unchanged inspector reproduces the M2 header report and passes all ten
synthetic regressions. No evidence justifies adding an inner-container parser.

Direct comparison of the preserved `0000` and `0002` prefixes gives a useful
additional length relationship:

| Quantity | `0000` | `0002` | Difference |
| --- | --- | --- | --- |
| Sony manifest total | 1,589,257,520 | 1,589,253,264 | 4,256 |
| Fixed visible header | 128 | 128 | 0 |
| Decimal field at 96-107 | 1,589,257,391 | 1,589,253,124 | 4,267 |
| Body length minus decimal | 1 | 12 | -11 |

Thus `4267 + (1-12) = 4256`. This reconciles the length-like field with the
distribution-size difference, but **does not prove padding semantics or explain
the underlying payload differences**. The visible header shape is shared;
the 56-character hex fields differ, and no literal model/region/version string
is established in the inspected 128 bytes. Only `0002` has a complete local
body. Whole-package equivalence and distribution selection remain unverified.

The [M2 source comparison](m2-firmware-analysis.md#historical-formats-and-decoding-limits)
still supplies only a historical Android Walkman AES-CBC/OTA lead. Entropy,
16-byte alignment and length arithmetic do not authenticate that interpretation.
No key recovery, decryption, signature patching, payload execution or unrestricted
extraction was attempted. A targeted Sony-domain search and the existing archive
member inventory supplied no applicable NWWM specification or factory-image set.
That is a bounded negative result, not proof that Sony has no such material.
Boot/recovery/vendor/DTBO/vbmeta and filesystem inventories remain **unknown**.

## New source findings with engineering consequences

Eight selected Sony archive members were streamed read-only, with individual
sizes/SHA-256 recorded privately. These observations refine required interfaces;
none establishes that the driver binds to this board.

1. **Qualcomm calibration is a separate userspace contract.**
   `audio_calibration.c:389-517` validates calibration type/buffer sizes and
   dispatches allocate/prepare/set/get/post callbacks. Lines 520-566 translate
   compatibility ioctls; 582-602 register `msm_audio_cal`. A native AArch64
   initializer must use the appropriate UAPI/structure layout, not an assumed
   32-bit Android helper. The dispatcher does not supply device calibration
   values or prove that every route needs every calibration type. [B1]
2. **Sony table installation is a transaction, not a volume scalar.**
   `write_table()` stages `table_size+8` bytes, checks data, copies the complete
   table and applies a change. `check_data()` uses an additive sum and packed
   byte XOR in the trailing two native unsigned integers; all-zero data fails.
   This is an integrity convention, not a firmware signature or proof that
   guessed tables are safe. Host tests can eventually validate format/transaction
   sequencing using synthetic values, without issuing a device write. [B2]
3. **Battery profile is a concrete missing DT input.**
   `qg_load_battery_profile()` requires `qcom,battery-data`, selects by battery
   resistance/age settings, and reads battery type, maximum voltage and charge
   current. Missing battery-data returns `-ENXIO`. A gauge driver/config symbol
   cannot substitute for the correct battery profile. [B3]
4. **Charging behavior depends on selected policy properties.**
   SMB5 parsing includes step charging, software JEITA, watchdog timing,
   thermal-mitigation arrays and charger temperature limits. Removing Android
   while inheriting unknown DT defaults is not a validated charging policy. [B4]
5. **Thermal zone selection can depend on provisioned hardware data.**
   The QFPROM thermal source reads named nvmem cells and compares them with DT
   values before enabling/disabling listed zones. This is a specific reason to
   preserve board data and audit the selected thermal path; it does not establish
   that this driver is active on NW-A306. No fuse/nvmem read was attempted. [B5]

## Focused dependency inventory

“Verified” below means verified historical observation or source fact, never
verified custom-device operation. “Partially supported” means some source/input
exists. “Unavailable” means a required matching artifact was not established in
the bounded reviewed material. “Device-specific validation” remains required
for all proposed hardware integrations.

| Dependency | Classification and evidence | Offline work possible / exact missing input |
| --- | --- | --- |
| Board identity and DT/overlays | Historical identity verified (D1); matching DT unavailable | Derive an explicit DT property checklist from drivers; need authentic selected tree/overlays, revision, GPIO/rail/clock/memory bindings |
| Kernel / boot image | Partially supported: source 4.19.157, ARM64 config; boot headers/images unavailable | Resolve DLKM/build inputs and compiler configuration, then host-build kernel/modules; need authentic boot-image layout and accepted handoff |
| Qualcomm DSP / firmware | Partially supported: Q6ASM, loader/authentication source; matching binaries/data unavailable | Audit UAPI, routing and firmware loader requirements; use mock control transactions. Need actual firmware/calibration versions and permitted provisioning |
| Sony CXD3778GF | Partially supported: I2C/ASoC, GPIO/regulator/table interfaces (B2/B6) | Test table integrity/transaction and muted policy logic with synthetic data; actual tables, gain mapping and board-safe sequence still missing |
| Display/backlight | Partially supported: DRM/SDE/DSI source; device-specific validation | SDL software UI now executes; cannot prove fbdev, DRM scanout, panel timing/orientation or rail sequence |
| Buttons/touch | Partially supported: evdev and configured controllers; device-specific validation | Test normalized input/action mapping generically; need exact controller, codes, calibration, firmware and wake behavior |
| Audio routing | Partially supported: Bengal MI2S/CXD links; device-specific validation | Define ALSA/control interface and mocks after obtaining matching routes; no physical PCM/gain/output claim |
| Storage/microSD | Partially supported: kernel MMC/UFS/filesystems; historical partition names verified | Test file libraries/hotplug policies on generic filesystems; need actual controller, GPT, encryption, card detect and suspend behavior |
| Battery/gauge | Partially supported: QG profile parser (B3); profile unavailable | Mock power-supply values/error states; identify authentic battery/profile data before selecting operating limits |
| Charging/thermal/shutdown | Partially supported: SMB5/QFPROM/reset/watchdog source (B4/B5, M0 S1) | Audit all required policy owners and fault paths; need selected DT properties, sensors/trips, watchdog ownership and shutdown/charging behavior |
| Verified Boot / custom authorization | Locked/green historical evidence verified; authorized custom path unavailable | Seek model-specific signed-image/loader documentation; no supported unlock, temporary boot, custom-key or kexec route demonstrated |
| Stock restoration | Official Android-dependent update/reset documented; unbootable-device restoration unavailable | Obtain written service failure coverage, authentic image set/entry/tool policy, rollback and unique-data handling; later separately approved spare validation |

The smallest architecture remains ARM64 Linux, minimal supervised userspace and
Rockbox, retaining only necessary board firmware/control components. The source
findings argue for an explicit small audio/power initialization layer, not for
recreating Sony's full Android environment. No hardware stub or guessed board
constant was introduced. The older MediaTek NW-A30 remains a historical reference;
its boot paths, PCM numbers, tables and mounts supply no NW-A306 requirements.

## Historical service questions

M3 identified questions about restoration failure coverage, matching artifacts,
rollback and unique-state treatment, supported custom execution, board/build
resources and NWWM provisioning rights. The consolidated
[service questions](m6-recovery-engineering.md#sony-inquiry-unsent) retain those
requirements. No inquiry was sent.

## Alternatives and proposed M4 priorities

Continue full hosted playback and input/storage/audio-policy tests without a
device; optimize seek/resume only against the regression corpus. Investigate a
compatible ARM64 memory-instrumentation environment. Use authentic public/source
documentation to close DT/module/calibration and safety-policy gaps. A generic
development board can support software interfaces, but cannot prove Sony board
binding or boot acceptance.

If official information is insufficient, next paths are lawful static analysis
of matching supplied boot/DT artifacts, collaboration through a separately
authorized inquiry, and a matching spare for a future reviewed plan. Temporary
boot still needs image acceptance; kexec needs verified privilege/configuration;
service/EDL needs matching authenticated tooling if applicable. None is presently
verified. Host execution does not establish a safe device experiment.

Hardware experiments require separate approval, accepted execution and verified
recovery covering the proposed failure states.

## Exact new source locators

All members below are in unchanged Sony S (`gpl_source.tgz`, SHA-256 recorded in
M0). Hashes identify the streamed member bytes; references after the prefix are
relative to the listed directory. Private extracted review text is not published.

| Ref | Member, lines and SHA-256 |
| --- | --- |
| B1 | `vendor/qcom/opensource/audio-kernel/dsp/audio_calibration.c:389-517,520-566,582-602`; `653757cc8d51aa53139fb7cadc9327c91a049614eb5db9c81760c2e604a8d389`. Its `include/dsp/audio_calibration.h` was also read, SHA-256 `d645edb1f0f9f812b054e02b7955542dc83b8f1071d5758e714de14847d4b726`. |
| B2 | Same audio-kernel prefix, `asoc/codecs/cxd3778gf/cxd3778gf_table.c:28-31,138-141,246-340,414-442`; `6e480a57a2c08382f3ef2a1bbd0e9d94fae161962837f976d18ea4559b2c1db7`. |
| B3 | `kernel/msm-4.19/drivers/power/supply/qcom/qpnp-qg.c:3027-3100`; `ac654c14935e526bbbb499fd5b395e01aa8694b1be036045e51f4167dfadac59`. |
| B4 | Same power directory, `qpnp-smb5.c:513-571`; `dbdeb951a112738de094c247a5e00f4aa28793b0ddf3fd6e0503297eb6249183`. |
| B5 | `kernel/msm-4.19/drivers/thermal/qcom/qti_thermal_qfprom.c:18-45,107-140`; `53c1d3744e515b549b5563377291c50627ab98ed88a879202d0789307d17cd2f`. |
| B6 | Audio-kernel `asoc/codecs/cxd3778gf/cxd3778gf_platform.c:119-182,227`; `e4e13a84e6d96e0027a04157e72b45a94d52dd721baae865890954d3bf82208e`. Existing M0 S3/S4/S6 establish routing/control context, not board binding. |

The eighth selected member was the existing RME loader, rechecked unchanged:
`kernel/msm-4.19/drivers/misc/lifmd6000/lifmd6000.c:651-675`, SHA-256
`5971ea6972e961159be0490775e891f4e39acee9681029b95a0bc1cd578253a5`.
Its applicability to NW-A306 remains unknown; no loader operation was run.
Official recovery/update references remain in the preserved
[M1 source register](recovery-provenance.md#source-register). Searches during M3
did not supply an additional applicable factory-restore or NWWM specification;
unrelated Xperia/computer/older-player results were not adopted as evidence.
