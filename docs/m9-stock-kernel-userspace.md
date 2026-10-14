# M9 stock-kernel independent-userspace contract

2026-10-14. Sony's shared source can execute a non-Android init. M9 establishes
more precise module, firmware, device-node and protection prerequisites, plus
a tested dependency specification. It establishes **no accepted replacement
initramfs/rootfs** and no Sony hardware runtime compatibility. Evidence classes
and actual artifact availability are in the [inventory](m9-boot-artifact-inventory.md).

## New source findings

S is the unchanged 20260716 Sony archive; `K` means `kernel/msm-4.19/`.
Thirteen members were read selectively, each below 1 MB; private
`build/m9/sony-members.json` preserves full locators, bytes and SHA-256.

| ID / exact source and SHA-256 | Consequence, with applicability limit |
| --- | --- |
| M9-S1: `K/kernel/module.c:271-280,1282-1346,2819-2846,3059-3078,3720-3730`; `fb25739d27905cbcec19c84bc9e827276b9909d1f8f3d2d0e3887018ccc2e083` | Module signature enforcement, version/CRC and vermagic checks are distinct. Source-matched compilation alone does not establish trusted signatures or ABI. Published defconfig selects modules/MODVERSIONS/mandatory signatures; final config and accepted modules remain U |
| M9-S2: `K/kernel/kmod.c:70-99,125-171`; `310e2df14091a748b039f9d19e1f43a6388f5c13c122ab5aee044cec1ec7e9bc` | Autoload calls `call_usermodehelper`. Combined with M8's `umh.c:383-401,535-561` and empty static-helper config, this can return success without executing modprobe. Independent init needs verified built-ins or explicit permitted module loading and actual readiness, not success of an autoload request |
| M9-S3: `K/drivers/base/devtmpfs.c:32-56,348-365`; `56beffcacf55997ada36e516a62cb024a3a3ef5d73f11f1d002ef914760c2d12`; `K/drivers/base/dd.c:42-50`; `17f2c706dd570da3905a7a111c425e2322117c52475e617ae3eeb9683ee26455` | Device-node filesystem mounting is conditional; deferred probe is an explicit not-ready state. Published defconfig has no explicit DEVTMPFS entry, which does not establish the final setting. Need authentic node/permissions and probe/resource contract, not Android ueventd by assumption |
| M9-S4: `K/drivers/soc/qcom/watchdog_v2.c:314-342,776-787,989-1011`; `8e0ed02aea2f0abfccb673d8d3754016b0e2f328c7946d9aa0778b388b3940fd`; published defconfig:377-394,656-659, SHA `8822ea40625c2b57c805519591f41f247dd02e41ed41b8091af17a5f73544b6c` | Userspace watchdog interface is conditional on selected DT; owner/timing cannot be inferred from a generic `/dev/watchdog`. Thermal userspace governor and writable trips are configured alongside kernel protection. Enabled source options do not prove complete Android-independent protection; selected governor, trips and service ownership remain U |
| M9-S5: `K/drivers/soc/qcom/subsys-pil-tz.c:679-710,1084-1110,1301`; `de72b940c8c17cac62d5436a94ac7fac3ba20939bd15227d7ed11b1f3ffedb5a` | This candidate PIL loader derives firmware identity/resources from DT and invokes secure authentication/reset. Active A306 loader and secure-firmware policy U. Its conditional branches are not permission to modify DT or bypass authentication |
| M9-S6: `K/drivers/of/fdt.c:988-1020,1171-1182,1191-1227,1335-1348`; `3edb6c06c374305cb03ec30c12f38d8d1ae29cc026cea2f7640a6449c6977ef4` | Reads `/chosen` bootargs and initrd addresses; CMDLINE_EXTEND concatenates configured and supplied input. FDT header/CRC checks are structural/integrity processing, **not cryptographic boot authorization**. Actual DT inputs/coverage remain U |

M8's exact init/initramfs/firmware source locators are retained in its
[artifact audit](m8-board-firmware-artifacts.md#targeted-sony-source-audit).
The published config explicitly marks only MSM_RDBG and two DVB entries `m`;
that is not the complete selected module set or the external audio DLKM list.
Missing final config, generated audio configuration, module symbols and signed
binaries prevent a complete built-in/dynamic classification.

Audio dependencies remain substantive: shared `audio_calibration.c:574-602`
registers `msm_audio_cal` and ioctl/compat handlers (SHA
`653757cc8d51aa53139fb7cadc9327c91a049614eb5db9c81760c2e604a8d389`).
`cxd3778gf_table.c:136-195,274-328,414-442` provides proc table delivery and
integrity checks (SHA `6e480a57a2c08382f3ef2a1bbd0e9d94fae161962837f976d18ea4559b2c1db7`).
These are source interfaces, not measured A306 nodes, genuine calibration or
cryptographic acceptance. No table, mixer value or write operation is implemented.

The subsequent planning review identified another acquisition constraint in
the same M9-S6 member. `drivers/of/fdt.c:1427-1452` exports the initial tree as
`/sys/firmware/fdt` with mode `S_IRUSR` and can withhold the file after a CRC
mismatch. Lines 1232-1241 remove an RNG seed and update the CRC. Normal-shell
readability therefore cannot be assumed, and an exported in-memory tree need
not match the original storage bytes or preserve DTBO packaging. These source
lines and the member SHA-256 above were rechecked during publication review;
actual runtime permissions and selected configuration remain unobserved.

## Minimum service and initialization specification

[`m9-userspace-contract.json`](../tools/m9-userspace-contract.json) describes
**13 evidence/readiness roles**, not thirteen actual Sony daemons. `requires`
edges are conservative engineering precedence derived from the sources and
the safety objective; they are not a measured kernel probe timeline. `basis`
distinguishes source-supported interfaces from requirements. M9-A denotes the
[acceptance conditions](m9-authentication-boundaries.md); M9-U denotes the
still-unselected board contract below.

| Role / prerequisite | Minimum independent responsibility and unresolved input |
| --- | --- |
| `handoff` | Accepted kernel/DT/init/root selection, documented side effects and restoration contract. All unestablished on A306 |
| `board` | Selected build/DT/ABI, resource map and firmware/service/safety ownership. Shared GPL source and FCC packages cannot populate this profile |
| `early_protection` | Verify mute ownership and functioning baseline charging/thermal protection before potentially blocking initialization. Establish watchdog supervision in bootstrap wherever actual policy requires it |
| `bootstrap` | Independent init/supervisor, process reaping, proc/sys/dev interfaces and permissions; root-critical drivers and any firmware already accessible from accepted early userspace or built-ins |
| `storage` | Authentic root/mount mapping, module/firmware stores, persist/calibration ownership, read/write policy and media failure handling. No guessed block numbers or GPT offsets |
| `firmware_delivery` | Selected files available before dependent loads; direct `/lib/firmware`/persist lookup or required sysfs/event consumer. Custom fallback may wait indefinitely, so failure acknowledgement matters |
| `modules` | Explicit accepted ABI-matched module set or positively verified built-in coverage. Handle dependencies and load errors; no reliance on successful no-op autoload |
| `peripherals` | Confirm regulator/clock/power/IPC resources, selected loader and firmware authentication/initialization, and completion of deferred probes |
| `display_input` | Authentic DRM/panel/backlight and input bindings, device permissions, orientation, wake/loss policy. M6 virtual results do not select these |
| `audio_muted` | Actual muted state, DSP/calibration/DAI/route readiness and reviewed gain/mute contract. File presence or table checksum alone cannot establish audio safety |
| `protection` | Full selected charging/thermal policy and live health/ownership, including any userspace responsibilities. Preserve early protections during initialization/failure |
| `watchdog` | Established owner, actual documented interface/timing, live critical-service supervision. This readiness gate does not mean supervision can be delayed until the end of initialization |
| `rockbox` | Start primary UI only after every prerequisite; remain muted until the separate reviewed live safety/audio policy permits output. No Android/Google framework is planned |

This model resolves one important ordering hazard: provide firmware delivery
before explicitly loading modules that may synchronously request it. Root-
critical drivers/firmware cannot themselves live only on the unavailable root
filesystem. The bootstrap role therefore requires them earlier, through the
authentic accepted early filesystem or built-ins. If the actual selected set
creates a storage/firmware cycle, that is a concrete blocker to resolve, not
permission to force this model's order onto hardware.

An independent init need not recreate all Android. It must replace the
essential owners: device-node/permissions handling; required module and firmware
delivery; mounts/logical-device setup; hardware service/safety supervision;
audio calibration/routing; and shutdown. AOSP first-stage init normally maps
dynamic `super` before mounting its logical filesystems; keeping a separately
accepted RAM root could avoid that root dependency, but accepted RAM-root
selection and memory budget are U. It cannot remove the firmware/persist and
safety dependencies. [AOSP dynamic partition implementation](https://source.android.com/docs/core/ota/dynamic_partitions/implement).

No selected Sony init/fstab/property-service files were acquired. Therefore no
specific Android property, daemon name, SELinux label or complete replacement
service list is asserted. D1's historical SELinux enforcing state and the
published security options require an applicable permissions/security-policy
contract; disabling policy is not an established execution route.

## Tested host verifier and failure contract

[`userspace_contract.py`](../tools/userspace_contract.py) validates the fixed
role set, unique IDs/dependencies, source-locator fields, acyclic graph and
critical precedence. All roles must be ancestors of Rockbox startup. It reads
bounded regular UTF-8 JSON files (maximum 64 KiB), rejects symlinks/nonregular
files, duplicate JSON keys, unsupported schemas and malformed states, and
performs no subprocess, device I/O, service control or firmware writing.

Input states are `ready`, `missing`, `failed`, asserted externally or synthetic;
omitted states are missing. They are **not evidence authenticated by the tool**.
Failures propagate through dependencies. A fully ready synthetic model still
returns `deployment_authorized: false`. No real Sony profile or all-ready state
file is shipped. Existing `linux_safety.py` remains the separate live-telemetry
decision function; M9 neither weakens it nor implements an unmute adapter.

On lost readiness the output lists desired actions: verified mute request,
application stop, peripheral quiescence, display/input release, owned-storage
synchronization and reviewed kernel poweroff. Charging/thermal/watchdog owners
must remain active until actual shutdown or documented handoff. This is a
review contract, not executed recovery: failed mute or poweroff stays unverified.

```powershell
python -m unittest discover -s tests -p test_userspace_contract.py -v
python tools/userspace_contract.py tools/m9-userspace-contract.json
```

Nine deterministic tests pass on Windows and WSL. They cover all 13 missing/
failed role cases, independent branch behavior, cycles/unknown/duplicate roles,
firmware/safety-order bypass, schema/evidence/state errors, bounded malformed
JSON and unchanged inputs, and CLI outcomes. The second command intentionally
returns **1** with all roles blocked; invalid input returns 2, synthetic model
readiness 0. No result proves actual image acceptance, muting or protection.
