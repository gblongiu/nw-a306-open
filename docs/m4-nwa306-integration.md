# M4 NW-A306 Linux integration requirements

Date: 2026-10-14. [Application playback](m4-playback-validation.md) now works on
generic AArch64 Linux. Every custom NW-A306 subsystem and boot path remains
unverified. This report adds exact Linux interfaces and missing resource inputs
to the [M3 inventory](m3-board-dependencies.md), without inventing board values.

Eighteen selected members of the pinned Sony GPL archive S were streamed
read-only, bounded to 700,000 bytes per member, with size/SHA-256 records retained
privately. This archive covers multiple Sony products. A driver name, enabled
symbol or related Qualcomm compatible does not identify the active A306 driver.
Historical D1 identifies `icx1301`, Android firmware 3.06.00, Qualcomm QCS2290
and locked/green boot state; those observations do not select a complete DT.

## Subsystem contracts and readiness

| Subsystem / precise source interface | Required resources and firmware | Missing A306 inputs / readiness |
| --- | --- | --- |
| Kernel and boot | Published ARM64 4.19.157 configuration, external audio DLKM, module symbols/signatures, authentic boot header/ramdisk/DT/overlays | Source partial; missing selected DT, external build helper and accepted boot handoff. No target kernel/modules built or booted (M2 A1/S7) |
| Root filesystem/storage | Linux block/filesystem interfaces; `sdhci-msm.c` uses `qcom,bus-width`, `qcom,clk-rates`; `ufs-qcom.c` uses PHY and `qcom,vccq-parent` resources | Neither source family proves installed storage type. Need exact controllers, card detect, rails, GPT/slot mapping and encryption ownership; rootfs placement remains a design choice (I5/I6) |
| Audio frontend/backend | Bengal DPCM frontends `msm-pcm-dsp.*`, routing platform `msm-pcm-routing`, secondary ICX/quaternary STD MI2S links; `asoc-platform/cpu/codec` phandles bind names | Source partial. Need actual card, PCM frontend, backend/control names, channel/rate/clock settings and selected DAIs; no ALSA device number or mixer value inferred (I1) |
| DSP initialization | Q6ASM/ACAL from M2/M3; generic Q6v5 lifecycle uses named wdog/fatal/ready/handover/stop-ack IRQs and SMEM stop state | Matching ADSP firmware, authenticated loader, reserved memory, clocks, resets, IPC and calibration remain unavailable. Generic remoteproc/PIL sources do not establish the selected vendor path (I7, M2 A4, M3 B1) |
| Sony codec/amp | I2C compatible `sony,cxd3778gf`, codec controls, GPIO/regulator resources, runtime table ports and control suspend/shutdown | Exact bus/address, selected TYPE_A/Z path, rails, GPIO polarity, tables and gain mapping missing. Original calibration and table transactions must be preserved; no guessed defaults used (I2, M3 B2/B6) |
| Headphones/muting | CXD interrupt handlers call `cxd3778gf_handle_hp_det_event`; separate mute paths/workqueues and shutdown order exist | Need actual jack detection path, IRQ/wake policy and independently safe mute/route/gain sequence. The Bengal dummy always-inserted jack code is under `#if 0`; it must not be used as a working headphone detector (I1/I2) |
| Display/DRM | Vendor DSI panel parser requires timing and panel data, reset GPIO and selected PWM/WLED/DCS/external backlight type; DRM APIs offer connector/CRTC/plane/framebuffer modesetting | Authentic panel command sequences, timing, lane/clock/rail configuration, active SDE/KMS driver and scanout format/orientation missing. Generic `msm_drv.c` is a comparison, not proof of the selected techpack path (I3) |
| Touch/buttons | Himax platform reads panel/display coordinates and IRQ/reset/3v3/CS GPIOs; GPIO keys require `linux,code`, optional input type, wake action and debounce | Actual controller/binding, firmware, dimensions, orientation, keys and wake sources missing. HX source presence is not proof of installed hardware. SDL/WPS actions validate app behavior only (I4) |
| Battery/charging | QG battery profile and SMB5 charging policy from M3 B3/B4; Linux power-supply class supplies status/voltage/current/temperature properties | Matching battery/thermistor/profile, charge/current/voltage limits and policy owner missing. A status reader cannot replace JEITA/charging policy |
| Thermal/watchdog | TSENS calls its selected calibration operation; watchdog exposes userspace-pet attributes only when `qcom,userspace-watchdog` is selected, with DT pet/bark times | Need selected sensor/calibration/trips, userspace governor ownership and watchdog configuration. Do not assume `/dev/watchdog` is the sole watchdog contract or disable a watchdog to keep Rockbox running (I8) |
| Suspend/shutdown/failure | CXD control flushes mute/resume work and mutes before shutdown; Q6v5 stop has bounded completion; power/reset source exists | Need actual dependency order, wake IRQs, charging interaction, storage sync and PMIC reset/poweroff ownership. No suspend, battery lifetime or safe failure recovery measured (I2/I7/I8) |
| AVB/authorization/restoration | Historical locked/green A/B state and opaque NWWM update candidate | No matching factory image set, custom-image acceptance mechanism or restoration from unbootable Android demonstrated. See [next investigations](m4-boot-recovery-next-steps.md) |

The minimum system remains vendor-compatible ARM64 Linux, authentic DT/modules
and necessary firmware/data, a small supervised userspace, and Rockbox as its
primary interface. Android framework, AudioFlinger and Sony effects are not
planned requirements. Essential initialization they currently own still needs
an identified replacement. Optional connectivity/effects do not gate wired
playback; power and thermal protection do.

## Concrete host-testable boundaries

These are interface requirements, not placeholder hardware implementations.
Only the SDL PCM/application boundary has been implemented and exercised in M4.

| Boundary | Contract / future mock test | Real Linux prerequisites |
| --- | --- | --- |
| PCM output | Explicit rate, channels, sample format, ordered frames, accepted/drained state and errors. M4 capture already distinguishes music, padding, pause and rate changes | ALSA hw/sw parameter negotiation, actual frontend/backend routing, drain/underrun behavior; capture on SDL proves no ALSA routing |
| Audio policy | Begin muted; require validated profile, DSP readiness, route and bounded gain before enabling output. Jack removal, data mismatch or service failure returns to muted state | Authentic control names/units, data integrity/provenance and codec sequencing. Mock transitions can validate refusal paths without any hardware write |
| Display | Mode/format/stride/orientation explicitly negotiated; map CPU buffer, present completion, blank/backlight lifecycle and loss of device | Active DRM primary node, connector/CRTC/plane and property capabilities; use dumb-buffer/software scanout where supported. Do not assume `/dev/fb0` |
| Input | Timestamped key/touch events, press/release and coordinate mapping; unplug/reconnect and wake state explicit | Bound evdev device identity/capabilities and calibration; scripted WPS actions currently bypass this boundary |
| Storage | Mount identity, read-only validation, media present/removed state and file-operation errors; no assumptions about `mmcblk` numbering | Authentic block mapping and mount/encryption rules. Generic files now exercise libraries/playlists, not microSD hotplug or power loss |
| Safety supervisor | Timestamped battery/thermal/service health, stale-data deadlines, muted fallback and orderly stop/shutdown request | Board-approved thresholds, kernel/user policy ownership, required watchdog service and shutdown mechanism. No invented limits or automatic service restarts yet |

The Linux [DPCM documentation](https://docs.kernel.org/sound/soc/dpcm.html)
explains frontend/backend routing; it does not supply a Sony mixer profile.
[DRM userspace documentation](https://docs.kernel.org/gpu/drm-uapi.html) defines
interfaces whose actual driver capabilities must be queried later under an
approved plan. The [power-supply class](https://docs.kernel.org/power/power_supply_class.html)
defines reporting conventions, not this board's charging policy. These generic
documents guide contracts without establishing NW-A306 compatibility.

## Exact new source locators

All Sony paths below are archive members of unchanged S, SHA-256
`5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`.
`K` means `kernel/msm-4.19/`; `A` means
`vendor/qcom/opensource/audio-kernel/`. Line numbers refer to those member bytes.

| Ref | Source and exact observations |
| --- | --- |
| I1 | `A/asoc/bengal.c:4529-4545` disabled dummy jack; `5705-5790` MI2S/Sony links; `6180-6264` name/phandle binding; `6433-6490` DT-dependent card population. SHA-256 `46518c71bbc6bb7224f23e674de3607f71ec576e2ee2e0585d28b598c0f0b219` |
| I2 | `A/asoc/codecs/cxd3778gf/cxd3778gf.c:564-585` I2C binding, SHA `5b2eba83a2e96af76f75c3a23827cd93e41da0591508d4d6ccc52b3e2cd0019b`; `cxd3778gf_interrupt.c:42-84,122-152,197-216` jack IRQ/wake callbacks, SHA `c2dff81143874478c26d3f4bc5986b3c69a9da092012b10af94c5d631fcf0c04`; `cxd3778gf_control.c:459-585,594-726` shutdown/suspend work and mute, SHA `8b1473c89109603537620252f710940c1f3b03040134c668d3c25d907379636d` |
| I3 | `K/techpack/display/msm/dsi/dsi_panel.c:1081-1140,2408-2411,2532-2558,3576` panel timing/reset/backlight/name, SHA `e85110a37d366ebc4cb66ae46d8b63074a1bf9103ed1c3bb44a8fd9cfbf9827e`; `K/drivers/gpu/drm/msm/msm_drv.c:1043-1044,1386-1388` generic modeset/atomic/compatible comparison, SHA `508364d20f3ee76f062aa0cd36acf1127d7c5421baa77aa61948a39e7d3c7290` |
| I4 | `K/drivers/input/touchscreen/hxchipset/himax_platform.c:133-194` coordinates/GPIO inputs, SHA `fb020867883613697e2b0adcca144334c21d096d1887b6c5464112ddb2109407`; `K/drivers/input/keyboard/gpio_keys.c:788-819` required codes/wake/debounce, SHA `0806f1c1b22a87f7c02170982b9d7430ba73e1b40e82239ad69febed749714e7` |
| I5 | `K/drivers/mmc/host/sdhci-msm.c:2273-2283,6155-6157` bus/clock/compatible inputs, SHA `d02f3d460ad1d84fe9a7a4f22307aa53ff60385fbae178cb2e449c94c7562422` |
| I6 | `K/drivers/scsi/ufs/ufs-qcom.c:847-898,2228-2241,2969` PHY/rail/compatible, SHA `327f5f452962f68ae9598b771cf312a48b6cd9d68c89eb248f925fe577a5ea3c` |
| I7 | `K/drivers/remoteproc/qcom_q6v5.c:145-165,191-284` stop/IRQ/SMEM resources, SHA `9dba28bc6f809876d983e595594615c77e52e054a987a61584c71d25fe615ac0`; `K/drivers/soc/qcom/pil-q6v5.c:673-734` additional compatible-dependent implementation, SHA `58c0ccd705cd2e8629dfbdd094e6396b8abdc6db0ce4a6ac142d5aa2c0cf6c4c`. Neither is established as A306's active loader |
| I8 | `K/drivers/soc/qcom/watchdog_v2.c:81-84,314-342,780-787,989-1011` conditional userspace pet and DT timing, SHA `8e0ed02aea2f0abfccb673d8d3754016b0e2f328c7946d9aa0778b388b3940fd`; `K/drivers/thermal/qcom/tsens.c:67-76,171-175` selected calibration, SHA `89acf82750bbc13d579d4e54ba3c7f79dd0b5280913742b5a89041abc60a1d1f` |

M0-M3 evidence registers and revisions are preserved. No Sony source, firmware,
calibration, raw diagnostic log or device identifier is imported into public
deliverables. Shared NW-ZX700 features, MD6000 presence and older MediaTek
NW-A30 constants remain unverified for A306. Source review advances the missing
input checklist; it does not demonstrate board binding or safe operation.
