# M10 physical boot feasibility decision

Latest offline result, 2026-10-15: [temporary-boot source and RB1 disassembly](m10-boot-execution-analysis.md)
establish two distinct reference models. Historical standard user builds omit
the boot command; their enabled non-user path can change GPT/rollback state before
overall verification succeeds. RB1 registers boot but rejects a locked device
before image parsing, slot clearing and authentication on its normal handler path.
Sony's corresponding dispatcher/gate remains unidentified. No new device operation
or payload test occurred; N1/N2 are preserved. The next evidence target is Sony's
actual command table and early acceptance branch, with recovery for state writes
required before any image experiment.

Latest physical result, 2026-10-15: [N2 completed](m10-n2-results.md) with
`is-userspace: no`, reporting **bootloader fastboot**. After the approved physical
return, all eleven stock-Android identity checks passed. N1's unavailable version
and original stop remain preserved. The next target is Sony's temporary-boot
registration, locked-state/authentication path and possible boot-control writes;
no additional informational getvars or image experiment is proposed. Custom-image
acceptance and same-board firmware restoration remain unresolved. Earlier dated
recommendations below are retained as history, superseded by this result.

Current physical follow-up, 2026-10-15: [N1 results](m10-n1-results.md) now provide
guarded command/output evidence of Sony fastboot product/security/slot state and
an empty bootloader-version response. The owner documented return to Android.
Endpoint classification and independent-image acceptance remain unresolved.

Protocol follow-up: the empty version is unavailable, compatible with legacy
empty-success behavior, not a loader-malfunction finding. The
[proposed N2](m10-n2-authorization.md) contains just one new optional variable,
`is-userspace`, plus required identity/transport checks. It is not authorized or
executed. Its outcome selects the acceptance-policy investigation, not a boot
payload; N1's original evidence and stop record remain intact.

## Current correction: historical owner-device fastboot evidence

2026-10-15. [Fastboot reconciliation and proposed N1](m10-fastboot-reconciliation.md)
supersedes the access assumptions and next-action recommendation below. The
original M0 brief already recorded working fastboot and return to Android;
matching host input-history entries have now been located. Original fastboot
command/output transcripts were not located within the documented search scope.
The owner's detailed historical observations establish reported physical entry,
`icx1301`, locked/secure state, slot b, one unsupported unlock-ability query, a
software-return failure and a Power-button return. These are historical
owner-attested results, not newly captured or independently transcript-verified
results. Preserve that distinction without reverting them to generic public leads.

The strongest actionable next observation is the existing endpoint's
`is-userspace` and `version-bootloader` responses, after identity/state guards.
Repeating manual menu discovery is unnecessary. Temporary independent boot
remains the preferred conditional execution hypothesis; implemented RAM boot,
accepted changed images, unlocking and dependable return/repair remain unknown.
Loader acquisition would help policy analysis but is not required for this next
metadata observation. The older checkpoint below is retained as history.

## Earlier checkpoint, before reconciliation

2026-10-14; host-only research continued into 2026-10-15 UTC. No new device
operation. Earlier evidence, denied reads, H1 quarantine and uncommitted work
remain intact. This assessment adds reboot-policy source evidence, not another
firmware-wrapper investigation or a deployment milestone.

## Decision and the six engineering answers

1. **Strongest conditional candidate:** early-loader-supported temporary boot,
   initially retaining the build-matched Sony kernel and supplying independent
   init/userspace. This is the preferred investigation target, **not a viable
   boot method established for the NW-A306**. There is currently no route with
   demonstrated custom-payload acceptance and same-board recovery.
2. **Direct support:** the physical unit boots Sony's Linux kernel; preserved
   physical observations report QCS2290, locked/green and `4.19.157-perf+`.
   Published shared Sony kernel source supports non-Android init and reboot-mode
   requests. Neither observation proves a loader accepts changed boot inputs.
   Generic ARM64 Rockbox remains virtual evidence only.
3. **What eliminates this candidate:** an applicable loader with no accepted RAM
   load/boot interface, or mandatory authentication of all changed inputs without
   an available owner-controlled acceptance mechanism. A signed stock kernel
   does not authorize changing its enclosing ramdisk, DT or command line. Such
   a result would eliminate this route, not prove every conceivable route
   impossible.
4. **Single most valuable missing artifact:** an authentic, running-build
   **OS-loader executable image** with provenance. Its actual Sony partition/file
   name is unknown; do not assume `abl`, `aboot` or `xbl`. Static analysis should
   first locate registered download/boot/unlock handlers and their authentication
   decisions. Delegation to another trusted component would identify the next
   precise dependency; one image alone cannot prove physical acceptance.
5. **Same-board restoration:** needs a reachable accepted repair entry surviving
   the intended failure; authentic layout and reconstruction bytes; rollback-
   compatible versions; accepted repair tools/rights; and preservation or lawful
   regeneration of unique state. No such complete mechanism is demonstrated.
6. **Next action:** acquire that authentic loader through an already lawful
   image/bundle or a separately reviewed, demonstrated read-capable interface,
   then trace its command table and trust decisions offline. No available
   authorized operation currently supplies it. Do not substitute a generic
   programmer, speculative mode transition or unsigned-payload test.

The concrete blocker is **missing selected loader policy and an independently
surviving restoration entry**, not missing Rockbox code or a decoding framework.
No physical boot experiment or mode-transition experiment is recommended on the
present evidence. Ordinary stock restart documentation is not firmware recovery.

## New technical evidence: restart policy in Sony's shared publication

Five specific members were selectively read from the unchanged Sony shared
3.06 source archive; no bulk extraction. Archive SHA-256 remains the previously
preserved `5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`;
archive size/mtime were unchanged across the read. Originals, member hashes and
locators are private under ignored `build/m10/boot-feasibility-20261014-01/`.
The public origin is the [Sony NW-A300/NW-ZX700 source release](https://oss.sony.net/Products/Linux/Audio/NW-A300-NW-ZX700_%2820260716%29.html).

Classification: **verified in shared Sony source / broader platform, not verified
in the running Sony image**. A published defconfig is stronger applicability
evidence than another board's procedure, but does not establish the final config,
selected DT or installed code. Prefix `K` below is `kernel/msm-4.19/`.

| Exact source | Established behavior and limit |
| --- | --- |
| `K/arch/arm64/configs/publishing/sony_dmp_android_defconfig:377`; `K/drivers/power/reset/Makefile:17` | Published `CONFIG_POWER_RESET_QCOM=y` selects **msm-poweroff.o**, not the separately configured qcom-pon driver. This narrows the appropriate source to inspect. Final running selection remains unknown. |
| `K/drivers/power/reset/msm-poweroff.c:150–164,552–556`; member SHA-256 `72eef6585e789c3135430efa06c353da323b6b5ee7d8b0cf78fae7e5719b6fdc` | Captures `androidboot.verifiedbootstate=` during kernel command-line setup. Its local `is_unlocked()` recognizes exactly `orange`; the `edl` restart branch invokes emergency download only in that case, otherwise writes the ordinary restart reason. This is a **kernel software gate**, not a ROM fuse reading, bootloader unlock implementation or proof about every possible EDL entry. Physical Android's green property is not a byte-for-byte capture of this kernel variable. |
| Same member, `msm_restart_prepare:488–563`, probe `631–677` | Bootloader/recovery requests write distinct IMEM reboot reasons and call PMIC restart-reason storage; warm/hard reset selection depends on runtime/DT policy. The driver binds through `qcom,pshold` and an IMEM restart-reason node. This supplies no implementation of the next loader's commands. |
| `K/drivers/input/misc/qpnp-power-on.c:456–485`; SHA-256 `dbc1227f02c4dbb723e2ef6dcfade78d3b331b5d6331ac4c748e461cf1f69dd4` | Restart reasons can be written to PMIC spare registers when selected `qcom,store-hard-reset-reason` policy enables it. These are register writes, not demonstrated flash erasure or permanent fuse changes. Retention/clearing on this board remains unknown. |
| `msm-poweroff.c:186–235,304–320,488–517,595–611`; published defconfig `579–581,673` | Download handling depends on mapped IMEM and secure calls; emergency download can disable the PMIC watchdog. Panic handling and reset mode can affect subsequent availability. Published options select Qualcomm watchdog, forced watchdog bite on panic and a five-second panic timeout; selected DT supplies watchdog timing. None proves emergency entry/programmer acceptance or safe automatic return on this unit. |

The `download_mode` default is zero. Probe requests SDI disabling when it remains
zero (`msm-poweroff.c:65,672–674`). Comments describe no runtime API for re-enabling
that SDI path; they do **not** establish a permanent fuse change or a power-cycle
restoration contract. Secure-call success and hardware behavior were not tested.

Consequences: do not treat a generic Android `reboot edl` recipe as an available
Sony restoration facility. Likewise, delivering a kernel to RAM does not remove
its ability to write storage/AVB state or program PMIC/watchdog/reset hardware.
An eventual first image needs reviewed storage permissions, charging/thermal
ownership, watchdog behavior and a failure exit. Prior
[dm-verity side effects](m9-authentication-boundaries.md) still apply.

## Boot-entry candidates: facts, hypotheses and rejection conditions

**Physical** means preserved owner-device observations; **shared source** is not
running-board verification; **reported** means an unreplicated public claim;
**unknown** means no acceptance evidence. No new physical result was obtained.

| Route | Model-specific basis / remaining hypothesis | Authentication and decisive evidence; rejection | Persistent effects / recovery prerequisite |
| --- | --- | --- | --- |
| Early-loader RAM boot | Physical locked/green. Public reports describe A306 fastboot/menu access, but no build-bound accepted custom boot. RAM command support is unknown. | Need authentic loader handler/policy, image/DT ABI and trusted-key rules. Reject if no usable temporary interface or no way to authenticate changed inputs. A getvar response alone would not prove payload acceptance. | Delivery need not install an image; execution/reset can still alter state. Need assessed return to stock and repair covering possible writes/power failure. |
| Supported unlock or owner-key enrollment, then installed Linux | OEM-support property was empty in Stage B2. Xperia documentation does not establish Walkman support; reported A306 unlock-command absence weakens this lead. | Need model/build-specific implemented trust transition, enrollment and image rules. Reject supported-unlock route if those handlers/policy are absent or prohibit it. An Android OEM toggle is insufficient. | Persistent security transition, possibly erasure/provisioning consequences. Need accepted restoration, unique-state treatment and documented reversal before any request to unlock. |
| Stock kernel selecting independent init/root | Physical stock kernel boots; shared Linux init code supports alternate init. Owner-controllable authenticated input is unknown. | Need selected boot/DT/AVB graph and a permitted input. Reject if all selectable inputs are authenticated and no owner-controlled selection is accepted. | Can be volatile only if supported volatile input is proved; installed edits are persistent. Need original accepted images and recovery independent of changed inputs. |
| Official updater or recovery delivering changed images | Artifact updater delegates to native installer. Historical recovery partition names are not recovery execution. | OTA authentication and loader AVB are separate gates. Need accepted changed payload plus accepted boot chain. Reject repacking/client-debug-path inference; recovery menu/factory reset does not grant unsigned execution. | Writes and slot/shared-state changes. Need applicable reinstall/repair acceptance and a surviving entry beyond damaged Android/boot/AVB. |
| Kernel handoff/kexec | Generic ARM64 precedent; no selected final config/privileged execution path. | Need enabled supported handoff and independent power-on mechanism. Android-assisted handoff alone fails the goal. | Handoff may be volatile; privilege/startup changes may persist. Need driver quiescence and recovery outside the altered environment. |
| ROM/service programmer or direct storage | Qualcomm platform precedent; no applicable Sony programmer, command rights or restore demonstration. New shared source restricts one software EDL path. | Need accepted Sony-bound programmer, security/DDR/storage match and actual rights. Reject another board's programmer or protocol visibility as proof. Direct writes do not defeat authentication. | Entry can strand availability; writes can damage early loaders/layout/provisioning. Need partition-independent accepted restore, complete original resources and unique-state protection. |

A [2023 A306-thread report, post 3,618](https://www.head-fi.org/threads/new-sony-walkman-nw-a300-series-android-12.966467/page-242)
states that `fastboot oem unlock` is unavailable and proposes, rather than reports
success with, an EDL cable/dump. Public search indexed the original post; full
page retrieval failed. No complete command/response record, running 3.06 match,
accepted RAM payload or restoration result was acquired. Recovery anecdotes
also conflict. They remain **reported/unverified leads**, not physical project
evidence. Older A100/i.MX instructions and ZX707 reports cannot establish A306
command support. No new selected image bundle was found in the bounded searches
for `icx1301` boot/vbmeta/loader images and A306 bootloader documentation.

Sony's model-specific [restart guide](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html)
documents forced restart with the power button after a freeze. It does not
promise exit from EDL/bootloader, repair of corrupted images, or recovery from
bad PMIC/watchdog configuration. The guide was acquired with original bytes,
URL/time and SHA-256; no restart was performed.

## Artifact acquisition decision and recovery blocker

The complete official encrypted UPG is preserved, not a decoded reconstruction
set. Selected DTB/DTBO, boot/recovery and vbmeta bytes remain absent; use of
vendor_boot/init_boot and actual loader names remain unknown. No format guess,
new regional download or synthetic parser resolves this. See the preserved
[artifact inventory](m9-boot-artifact-inventory.md).

**Defer native UpdateEngine/public OTA-certificate acquisition.** It would answer
which keys the running installer uses, not which payload the early loader accepts,
whether RAM boot exists, or how the original board can be repaired. Even a weak
OTA gate would leave boot authentication and recovery unresolved. Those are useful
secondary artifacts if a specific candidate later depends on OTA delivery; they
are not the best acquisition now. No new fixed acquisition plan is proposed for
them in this increment, and neither standard AOSP path is claimed as a verified
Sony file. This updates the previous report's secondary-acquisition suggestion.

There is no currently authorized operation that can provide the selected loader:
raw partition acquisition, privilege escalation and service-mode transitions
are outside scope; no demonstrated unprivileged read-capable interface or
plaintext public restore bundle has been identified. Reading UpdateEngine,
certificates or more ordinary Android properties cannot substitute for it.
A lawful supplied loader/decoded bundle can immediately be inspected offline.
Otherwise a genuinely new physical investigation requires its own concrete
operation and availability/recovery review; no permission bypass is proposed.

Restoration must cover the experiment's actual failure scope. Both boot slots
can share lower loaders/trust/partition metadata; a working inactive slot does
not repair GPT/super or loader corruption. Authentic OTA contents may omit early
loaders and unique regions. Old bytes may be rejected by rollback/counter policy.
RPMB/provisioning/calibration are not transferable from another unit and must
not be overwritten by a generic dump. Permanent storage protection, lost
unregenerable state or accepted-loader corruption without a surviving repair
entry could make same-board restoration unavailable. These are failure cases
to resolve, not claims that an operation was tried or such damage occurred.
The [same-board recovery assessment](m9-recovery-readiness.md) remains unsatisfied.

This increment changes this assessment and appends its decision to the physical-
boot investigation. Private additions are confined to the ignored research
directory: five source members, provenance, public research/restart reference,
source-locator/preservation checks and a work-product ledger. No production code,
transport or authorization framework changed. No physical operation, executable
firmware test, secret acquisition or Git history change occurred. M10 stays open.

Actual checks: **16 source/provenance checks passed, zero failed**, including
five member hashes, preserved published defconfig, driver-selection and policy
locators. **1,363 prior private ledger-covered files matched**, zero mismatches.
These checks did not compile or execute firmware and do not verify physical
behavior. Changed-document whitespace/local-link checks and `git diff --check`
passed. Final read-only Git status retains the prior dirty tree plus the new
assessment; nothing was staged or committed.
