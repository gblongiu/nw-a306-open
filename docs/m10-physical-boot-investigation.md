# M10 physical-boot investigation: first host increment

Current follow-up, 2026-10-15: [advanced acquisition analysis](m10-advanced-acquisition.md)
adds validated related-platform loader inspection, distinguishes signed
reference images from Sony acceptance, and defines a research-board eMMC/debug
investigation ladder. It supersedes any interpretation that absent ordinary
Android access exhausts acquisition. No new physical access or boot route is
claimed; historical evidence below is retained.

2026-10-14. Host engineering authorized by the resume request. No device
operation authorized or performed. Starting checkout was clean at `761df61`.
This records a source-defined acquisition boundary and an offline tested plan;
**M10 is not declared complete**. The selected Sony boot bundle and an accepted
execution/restoration route are still missing.

Evidence labels used here match the requested categories:

- **Physical**: demonstrated on physical NW-A306 hardware, including explicitly
  identified historical owner observations; no fresh physical results here.
- **Artifact**: verified from device-specific artifacts; shared Sony source is
  identified as such and does not establish the owner's selected build.
- **Virtual**: verified in the virtual prototype.
- **Platform**: established for the broader platform, not the Sony board.
- **Plausible**: plausible but unverified.
- **Blocked**: unknown or blocked.

## Critical path and preferred architecture

**Virtual:** existing ARM64 Rockbox playback, KMS and evdev work supplies useful
application integration. **Artifact:** the preserved NWWM update, Sony source,
historical properties and certification photographs supply research inputs.
None supplies an accepted custom boot or demonstrated original-board restore.

The most credible *payload strategy* is initially to retain an authentic,
accepted vendor kernel, selected DT and required firmware while replacing
Android userspace with a small independent init and Rockbox. Sony's shared
kernel supports ordinary Linux init selection; see
[M8 exact source locators](m8-board-firmware-artifacts.md#targeted-sony-source-audit).
**Plausible:** this reduces simultaneous board-port changes. **Blocked:** we do
not control an accepted ramdisk/root/init input. Retaining a trusted kernel
does not make a changed boot image trusted. Proprietary DSP firmware or tables
would remain an unresolved constraint on the fully open-source destination.

Keep the M10 acquisition-first order, with these concrete dependencies:

1. Identify the applicable updater consumer and running board's resource
   identity. This can unlock existing firmware evidence and avoid guessed DTs.
2. Recover authentic boot/DT/AVB and recovery members; determine actual
   authenticated coverage and complete versus incremental restoration inputs.
3. Resolve accepted execution and independently surviving same-board recovery
   together. Neither another prototype boot nor a backup checksum satisfies this.
4. Establish selected protection/firmware/module ownership; then implement the
   smallest independent init. Only then propose a bounded physical boot.

The source access audit below advances step 1 now. Display/audio adapter changes
are premature while panel data, selected routing and power limits are absent.
No historical milestone report is rewritten by this reassessment.

## Ranked boot-access candidates

Ranking is investigation priority, not demonstrated availability. **No candidate
currently qualifies for a device boot experiment.** A stock-kernel payload and
an upstream-kernel payload both need one of these accepted delivery paths.

| Rank / actual candidate | Supporting evidence | Missing proof and rejection condition |
| --- | --- | --- |
| 1. Owner-authorized bootloader policy plus a temporary RAM boot | **Physical, historical:** D1 reports locked/green icx1301, not an unlocked unit. **Plausible:** an owner/engineering policy would be the cleanest reusable delivery interface if implemented. | **Blocked:** actual loader identity, implemented unlock policy, data erasure/rollback consequences, RAM-load command and accepted image rules. An OEM switch/property or generic Qualcomm command proves none. Reject RAM-boot branch if the applicable loader has no accepted nonpersistent load; reject any unlock experiment until unique state and its recovery consequences are covered. |
| 2. Existing accepted stock environment selecting independent init/root without unlock | **Artifact:** Sony shared `init/main.c` supports `init=`/`rdinit=` and normal init paths; M8 documents exact lines/hashes. Could retain the vendor kernel's board support. | **Blocked:** a supported owner-controllable input outside authenticated coverage, selected root/verity policy and handoff. Reject this branch if every selectable init/root input is authenticated with no accepted owner-controlled selection. Source support alone is insufficient. |
| 3. Recovery/updater-authorized alternative image | **Artifact:** genuine Sony transport package and manifests exist; historical partition names include recovery. | **Blocked:** applicable consumer, signatures, allowed image/partition set, version policy and independent recovery entry. A stock OTA is an acquisition/restoration lead, not authorization for a custom image. Reject custom execution through this route if it accepts only unchanged vendor-authorized images without a supported owner/engineering policy. |
| 4. Privileged Linux kexec handoff | **Platform:** Linux has such mechanisms. It could test a kernel while Android initially boots, if the selected kernel and privilege policy permit. | **Blocked:** selected config, syscall/lockdown/signature policy, lawful privilege route and peripheral shutdown. It cannot alone meet power-on directly into Rockbox. Reject if selected kernel or acceptance policy denies the handoff; do not pursue privilege changes during characterization. |
| 5. ROM/service download with an accepted exact-board programmer | **Platform:** Qualcomm ROM authentication/service mechanisms exist. **Blocked:** Sony entry, programmer acceptance, DDR/eMMC setup and command rights. | Require exact-board provenance, OEM/security binding, accepted programmer, actual read/write scope and reconstruction inputs. A 9008 USB ID/Sahara response is not that proof. Reject a supplied programmer if identity/authentication or board initialization does not match; do not substitute another QCS2290 board's loader. |
| 6. Exploit, debug pads or direct storage modification as execution access | **Plausible** only in general; no applicable exploit/debug-unlock evidence or reviewed board connection exists. | Direct writes do not defeat secure boot. No evidence-supported experiment is presently available. Defer unless a concrete applicable mechanism appears and recovery covers its failures. |

**Platform:** Qualcomm's [secure-boot explanation](https://www.qualcomm.com/news/onq/2017/01/secure-boot-and-image-authentication-mobile-tech)
describes chained image authentication. It does not select the Sony loader
generation, fuse policy or authenticated ranges. Do not assign another board's
stage names to this unit. [M9 authentication boundaries](m9-authentication-boundaries.md)
separate early execution, OS/DT/init coverage, modules and peripheral firmware.
Only actual loader/image evidence can resolve those boundaries for this board.

A newly reviewed [third-party NW-A306 EDL failure report](https://www.reddit.com/r/walkman/comments/1ua113b/nwa306_hard_bricked_in_edl_9008_mode_after_a/)
contains an author's claimed enumeration/handshake and a request for a missing
programmer. The author subsequently describes a freeze and forced restart
during an update transfer, qualifying the initial interrupted-flash account.
**Plausible, unverified anecdote:** no independently inspected unit, accepted
programmer, artifact set or successful restoration is supplied. It cannot be
promoted to Physical evidence here. No identifiers are reproduced or contact made.

## Recovery survival dependencies

**Blocked:** none of the following is a demonstrated original-board restore.
The dependency graph is: surviving entry -> accepted repair execution ->
accessible storage/configuration -> complete applicable reconstruction bytes ->
permitted rollback/version state -> preserved device-unique state -> restored
stock boot and essential hardware. Every edge must survive the proposed failure.

| Failure | Candidate earliest survivor / requirements | Present recovery limit |
| --- | --- | --- |
| Android userspace/root damage | Independently bootable intact recovery or surviving accepted loader; complete matching OS/verity inputs | Recovery names known historically; independence, entry and actual repair coverage unknown |
| Both kernel/ramdisk slots or AVB/recovery damage | Earlier accepted loader/service entry not dependent on damaged images; accepted matching images/keys/version state | No applicable accepted loader repair operation or verified coverage |
| GPT/super/slot metadata damage | Entry/storage mapping independent of damaged layout; exact GPT/extents/slot reconstruction and accepted content | Partition names are insufficient; no exact reconstruction set |
| Early-loader/storage boot-region damage | Surviving ROM or external storage access; accepted exact-board initialization and all required early images/configuration | No accepted programmer, board wiring or complete early image set |
| Unique calibration/provisioning/RPMB damage | Prior preservation plus a permitted restoration path for the specific state | User-area copies cannot replay authenticated RPMB or invent device-bound provisioning; some losses may be irrecoverable |

[M8 storage distinctions](m8-boot-storage-architecture.md) remain essential:
user area, hardware boot1/boot2, EXT_CSD, RPMB, GPT/A-B/super and AVB/rollback are
different state. Existing public-file backups preserve engineering work, not
the player's essential original state. Sony's exchange-oriented service notice
does not establish restoration of the same board; see
[M9 recovery](m9-recovery-readiness.md).

A temporary image could hang, write storage, misconfigure power or break the
return path. Resetting into stock is a hypothesis until entry and state survival
are verified. No ranked candidate yet has a credible demonstrated rollback.

## New bounded source evidence

Four exact regular members were selectively read from the unchanged Sony
20260716 GPL archive, SHA-256
`5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`.
Total selected bytes: **63,530**; no bulk extraction or local-reference writes.
Private copies/ledger: ignored `build/m10/sony/` and `build/m10/source-audit.json`.
Prefix below is `kernel/msm-4.19/`. These are **Artifact** source facts with
**Blocked** runtime selection/SELinux availability.

| Exact member / SHA-256 | Finding and consequence |
| --- | --- |
| `drivers/of/kobj.c:31-36,63-83,115-143`; `eaa187d86c6817c2bfb7c55fb8e51075011191303961e9cf926e521142dcb9de` | Property reads copy existing property memory with offsets/counts. Ordinary properties use `0444`; names beginning `security-` use `0400` and report size zero. This callback does not poll a peripheral. Restrict the first request to root `compatible`/`model`; do not recursively read arbitrary properties. |
| `drivers/of/base.c:222-243`; `9bbf4acc4be36e343102d7b4b83a9d34ed7d76863cf90f1859caefa4b7fbdd7d` | Creates the devicetree kset and `/proc/device-tree` alias to `/sys/firmware/devicetree/base`. An unexpected alias is a review stop, never a newly authorized path. |
| `drivers/of/Kconfig:51-58`; `bca29b337b0e6436a7055b789b8e6218b25894de92d118c452eaac00ac8c2084` | OF_KOBJ defaults to SYSFS; final selected config remains unavailable. Existence cannot be inferred solely from the published defconfig. |
| `Documentation/ABI/testing/sysfs-firmware-ofw:14-28,30-51`; `4a7f4acb18d64c3bfb7dbf69d8aa647a63b66e97dfac9305456187a0db3c39f3` | `/proc/device-tree` is the stable ABI; properties contain exact binary values. Live property bytes are not original DTB/DTBO packaging or authentication coverage. |

The prior source check `drivers/of/fdt.c:1427-1452` exports raw FDT with
`S_IRUSR`, and can withhold it after a CRC mismatch; SHA-256
`3edb6c06c374305cb03ec30c12f38d8d1ae29cc026cea2f7640a6449c6977ef4`.
Thus a denied raw export does not rule out readable ordinary live properties.
Both availability and access require a separately authorized normal-shell test.

The preserved `sony-apks.zip` directory contains exactly four APK members named
for the previously studied audio applications and `SHA256.csv`; no separately
named updater member. This directory check does not inspect embedded consumers
or prove a global absence. No APK was executed or newly extracted.
The historical A100/ZX500 decoder remains an inapplicable comparison until an
A306 consumer is identified. No rejected UPG digest guesses were rerun.

Pinned **Platform** semantics were acquired by HTTPS into ignored
`build/m10/primary/` (Android `android-14.0.0_r1`, not a Sony binary match):

- [Toybox head](https://android.googlesource.com/platform/external/toybox/+/refs/tags/android-14.0.0_r1/toys/posix/head.c),
  lines 9,35-59, SHA-256 `67d0fea684ef4c841226577c4f76cf1054e548013e7c1b1b408ae1c1e2688242`:
  `-c` copies bytes, not lines. It may read a buffer beyond the emitted limit;
  only the reviewed memory-backed properties qualify for these first reads.
- [Package-manager query](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/pm/PackageManagerShellCommand.java),
  `runListPackages`, lines 943-1064, SHA-256
  `7c554cc6e5b39a979c3aa6f63a20a139d85a94114f285d7fd1923b98f046ae13`:
  `--user 0`, `-s` and substring filtering select returned names. The service
  still internally enumerates installed package metadata; no updater is launched.
  An empty result cannot exclude an updater with another name or user.
- [ADB manual](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/docs/user/adb.1.md),
  shell section, SHA-256 `50ffa5202a19e7a9b0facb25d70ef88d88eb9e07aeed4a4e40e690d0f0957002`:
  `-n` disables stdin, `-T` disables PTY, `-x` disables status/channel separation.
  A future transport must require shell-v2 and refuse fallback. Replay does not
  test its wire behavior or actual Sony utilities.

## Implemented question and acceptance results

Question: can a fixed first-pass plan preserve binary board identity evidence,
refuse collection after identity/access failures, and leave bounded private
records without adding a device execution endpoint?

`tools/characterization_plan.py` prints the immutable plan by default. The only
other mode replays explicitly synthetic responses for that exact plan digest.
There is **no live backend**, executable dispatch, USB discovery or network path.
It provides an admission/logging core for later reviewed collection, not a ready
live collector. No input/output value can add a remote operation.

Acceptance results from the 18 new tests:

- Exact normal locked Sony-shell profile, one bound synthetic transport, command
  order and unchanged transport required. Identity is checked before evidence
  and again at the end; failures terminate without subsequent requests.
- Independent per-stream caps, cap-plus-one sentinel, modeled command/session
  deadlines and required exit status. Denial, malformed values and stderr stop.
  These tests do not demonstrate cancellation of a real blocked process.
- NUL/CR/LF/arbitrary bytes survive logging unchanged; invalid DT string
  properties are retained privately but rejected as complete evidence.
- New exclusive output directories under ignored `build/m10`; traversal and
  symlink/junction paths rejected. Logs record exact operations, exit/completion,
  UTC/monotonic times, plan/tool/profile/fixture hashes and per-stream hashes.
  Host I/O/interruption handling attempts a partial manifest; a full/unavailable
  disk can also prevent that final write. No durable-log guarantee is inferred.
- Replays are always labeled nonphysical. CLI summaries omit identity/raw data.
  Direct Python API/JSON replay inputs are trusted as *synthetic inputs only*;
  they cannot attest a real transport or create physical evidence.

Run `python tools/characterization_plan.py` to review the plan without device
access. Optional `--fixture`, `--expected`, `--out` accept bounded local JSON
only; tests define the synthetic schema. No real device profile is shipped.

## Proposed physical characterization, requiring separate authorization

This is an operation-level proposal, not authorization or a runnable live
collector. The exact ordered plan is 11 identity requests, seven evidence
requests, then the same 11 identity requests. Each timeout is five seconds;
each stream cap is 4,096 bytes except the package query, 16,384. Session ceiling
is five minutes and 2 MiB. No retries or fallback reads.

| Phase / exact remote command | Question / expected observation / risk |
| --- | --- |
| `/system/bin/id -u`; separately `/system/bin/id -Z`; separately `/system/bin/getenforce` | Expect shell UID 2000, `u:r:shell:s0`, Enforcing. Stop otherwise. Diagnostic process/log effects; no privilege change. |
| `/system/bin/getprop ro.product.model` | Compare approved current model, not an assumed historic value. |
| `/system/bin/getprop ro.product.device` | Expect approved icx1301 identity. |
| `/system/bin/getprop ro.board.platform` | Compare bengal report. |
| `/system/bin/getprop ro.soc.model` | Compare QCS2290 report. |
| `/system/bin/getprop ro.build.version.incremental` | Compare privately approved current build. Changed build requires review. |
| `/system/bin/getprop ro.boot.slot_suffix` | Compare current approved slot; no slot mutation. |
| `/system/bin/getprop ro.boot.verifiedbootstate` | Compare green report, not ROM-fuse attestation. |
| `/system/bin/getprop ro.boot.flash.locked` | Compare locked report; no unlock request. |
| `/system/bin/uname -r` | Bind kernel release; string alone does not prove final config. |
| `/system/bin/readlink /proc/device-tree` | Expect exact reviewed alias; stop on absence/unexpected path. |
| `/system/bin/toybox head -c 4097 /proc/device-tree/compatible` | At most 4,096 accepted bytes; NUL-delimited board-family strings or a precise denial/absence. |
| `/system/bin/toybox head -c 4097 /proc/device-tree/model` | Single NUL-terminated model or denial/absence. Neither property supplies complete board resources. |
| `/system/bin/pm list packages --user 0 -s systemupdat` | Narrow updater-name candidates only. Binder/service and storage/accounting effects possible. A result becomes a later path-review item; no APK is opened. |
| `/system/bin/getprop ro.oem_unlock_supported` | Empty/0/1 report. Does not demonstrate implemented unlock or RAM boot. |
| `/system/bin/toybox ls -ld /sys/firmware/fdt` | Permission metadata only; missing export is a stop result. No raw FDT read. |
| Repeat first 11 requests in the same order | Detect changed identity/build/slot/security before marking the run complete. |

Plan SHA-256 (canonical JSON excluding its displayed digest):
`d41c8a9bb5462218a24fbde1930f74214a3f7d83fa26a844d3a327c529052bd8`.

Before requesting an executable session, privately bind the physical unit to
one existing authorized transport and approve its current expected profile.
The host ADB executable was located and hashed, **not executed**:
`C:\Users\dante\AppData\Local\Android\platform-tools\adb.exe`, SHA-256
`56656270da132f44e9cb4fb86a12ba965635c80423d43dcdd944d9fec4ab4622`;
local SDK metadata reports 36.0.2, not an independently authenticated binary.
A future host argument array would use that pinned executable, an explicit
reviewed transport, and `shell -n -T` with one constant remote string. Its
shell-v2 behavior, binary capture, real timeouts and no-server-start behavior
still need host-only transport testing before execution approval is requested.
No device discovery or authorization prompts are implicitly approved.

Persistent state: no intentional settings, files, services or boot-policy writes.
Android may log requests, package/file access may update accounting, and a USB
connection can change charging state. Unexpected load/hang/disconnect requires
stopping; killing a host client does not guarantee remote cancellation.
**Recovery remains unverified**, so no recovery/mode transition is proposed as
a fallback. The result would select the next bounded tree/package artifact
request or document denial; it would not authorize a boot experiment.

## Native board-support dependencies after acquisition

| Priority | Reusable support and evidence | Selected Sony requirement still unresolved |
| --- | --- | --- |
| Kernel/DT first | **Artifact:** shared vendor 4.19 source; **Platform:** upstream QCM2290/RB1 analogues | Authentic boot header/kernel/config, DT/overlay ordering, memory/reserved memory, ABI, module keys and firmware. Upstream analogues cannot supply Sony addresses or rails. |
| Display | **Virtual:** KMS integration; **Artifact:** vendor DSI source and sample assembly | Panel identity, DSI init/timings/reset/rails, backlight range and orientation. No panel selected. |
| Buttons/touch | **Virtual:** evdev integration; **Platform:** standard input/GPIO-key abstractions | Actual key/IRQ/wake mappings, selected touch controller/firmware and coordinates. Source driver presence is not selection. |
| Audio | **Artifact:** sample 3778-family marking; published CXD3778GF/DPCM/MI2S/ACAL/PIL sources | Selected DAIs/routes, DSP authentication, genuine firmware/calibration/tables, mute/gain/jack sequencing. Proprietary processing is separate from open drivers. No physical playback established. |
| Internal/microSD | **Artifact:** sample Samsung eMMC/socket; vendor SDHCI-MSM; **Platform:** upstream MMC/filesystems | Selected controller/pins/supplies/speed/card detect, exact layout and encryption/unique-state ownership. Initial root selection cannot depend on guessed mmc numbering. |
| Battery/power/thermal | **Artifact:** PM4125/LIS1650 sample; vendor QG/SMB5/TSENS/watchdog; **Platform:** upstream PM2250-compatible/SMD resources | Genuine cell profile, thermistor/JEITA/trips/current limits, watchdog owner, wake/charging and shutdown. Establish protections before display or audio enablement. |
| Standalone startup/shutdown | **Virtual:** Rockbox/Linux runtime; **Artifact:** ordinary init and firmware/module contracts | Replace necessary Android initialization, device-node creation, firmware delivery and safety ownership; ordered mute/quiesce/sync/poweroff. No Android runtime dependency may be hidden in a claimed standalone result. |

Exact prior member/function hashes remain in [M7 hardware convergence](m7-hardware-convergence.md),
[M8 artifact contracts](m8-board-firmware-artifacts.md) and
[M9 userspace ownership](m9-stock-kernel-userspace.md).

## Verification and next dependency

Windows Python unit discovery: **66 tests, 65 passed, one symlink-creation skip**.
WSL Ubuntu 24.04 Python discovery: **66 passed**, including that symlink test.
Commands: `python -m unittest discover -s tests -p 'test_*.py' -v` and the same
discovery under WSL Python. No ARM64 rebuild, new VM result or device test is
claimed. The plan CLI was inspected; `--live` is rejected.

This increment makes the next evidence collection smaller and testable, and
resolves a specific raw-FDT versus live-property access assumption. It does not
bring an image closer to bootloader acceptance or prove any recovery method.
Next engineering step: host-test a pinned shell-v2 transport without a device,
bind the private identity/approval scope, then request the exact normal-Android
characterization above. A lawfully supplied applicable updater or selected
boot/DT/AVB artifact would allow host analysis to proceed independently sooner.

## Transport-validation follow-up, 2026-10-14

The [host transport increment](m10-transport-validation.md) adds real bounded
pipe capture and simulation guards. It preserves the earlier replay and digest.
Local Python fixtures test binary streams and client timeout/cancellation;
no ADB executable or device interface is used.

The [operation review packet](m10-characterization-authorization.md) expands the
proposal with source-audited storage/ALSA/input inventories and limited display,
power-supply and regulator directory metadata. These can select the next board,
driver or consumer investigation, not reconstruct authenticated images, measure
functional peripherals or establish safe charge limits and recovery.

A new platform-source constraint is explicit: ordinary ADB CLI reads may start
or restart its server. A no-lifecycle live adapter and private device binding
remain execution gates. No physical operation or future milestone is authorized
by this increment; the earlier physical-boot blockers remain unresolved.

## Final host adapter, 2026-10-14

The [validated direct-server adapter](m10-transport-validation.md#final-no-lifecycle-adapter-2026-10-14)
resolves the CLI lifecycle blocker without executing ADB. The
[final Stage A/B packet](m10-characterization-authorization.md) is ready for
separate device approvals. All validation uses fake sockets; no real server or
Walkman has been contacted. Stage A discovery is the next step after approval.

The observations can bind running identity/tree/driver metadata and narrow
bootloader, updater and recovery-dependency investigations. They cannot supply
authenticated images, accepted independent-init delivery, functional hardware,
safe charging/shutdown ownership or demonstrated restoration. These physical
deployment blockers remain. Read-only discovery is not a recovery mechanism,
and M10 or any future physical milestone is not declared complete.

## Owner-authorized physical characterization, 2026-10-14

The owner confirmed the USB-connected unit, previously authorized debugging,
normal responsive stock Android, and no concurrent update/playback/transfer.
Stage A used the reviewed no-lifecycle adapter and exactly `host:version`,
`host:devices-l`, and `host:tport:usb`. It found one online `icx1301` candidate;
the USB-selected transport matched the inventory. Existing-server process image
and executable hash were checked locally without executing ADB or starting its
server. Private identifiers and raw captures remain under ignored `build/m10/`.
Following the owner's confirmation and further explicit authorization, the
reviewed full Stage B sequence was attempted once.

**Demonstrated on physical NW-A306 hardware:** the first eleven identity reads
matched the approved profile: shell UID 2000, `u:r:shell:s0`, SELinux Enforcing,
model `NW-A300Series`, device `icx1301`, platform `bengal`, SoC `QCS2290`, build
incremental `27`, slot `_b`, verified-boot report `green`, and flash-locked report
`1`. These are stock runtime observations, not independent fuse attestation or
proof of an unlock/alternative-boot interface. The next two observations returned
kernel release `4.19.157-perf+` and the `/proc/device-tree` symlink target
`/sys/firmware/devicetree/base`.

Observation 13 (zero-based),
`/system/bin/toybox head -c 4097 /proc/device-tree/compatible`, returned exit 1,
empty stdout, and permission-denied stderr. The adapter stopped immediately
under the reviewed stop rule. There was no retry, alternative path, privilege
escalation, reboot, settings change or firmware operation. DAC versus SELinux
versus directory-traversal cause is **unknown**. The source-level ordinary OF
property mode does not establish shell access on this running Sony system.
Neither `compatible` nor `model` was acquired; the remaining updater, storage,
audio, input, display, power and FDT-metadata observations were not attempted.

The Stage B session is **incomplete**: 13 successful observations, 14 attempted,
25 unattempted, 71 connections and 13,984 wire bytes. Successful observations
passed their individual before/after binding guards. The final eleven identity
rechecks were not reached, so no full-session consistency claim is made. Local
validation checked all recorded wire/decoded hashes and counts, decoded shell
frames independently, compared streams and exit status, and checked the exact
approved operation prefix. These checks passed, including classification of the
denial; they do not turn a failed read into complete evidence.

Private provenance: `build/m10/device-stage-a-20261014-01/` and
`build/m10/device-stage-b-20261014-01/` contain manifests, binary captures,
validation results and work-product inventories; the three Stage B profile,
approval and preflight files are under `build/m10/authorizations/`. These files
must remain untracked. No live-adapter or operation-registry code was changed
to bypass the denial. Earlier host-only reports above describe their respective
increments; this section records the subsequent physical observations.

This narrows the running-kernel target and establishes an actual access barrier
to the proposed board-identification read. It does not establish accepted native
boot delivery, selected DT/overlay contents, hardware function, protection
settings or same-board restoration. M10 remains incomplete. The next useful
experiment is a separately reviewed fixed subset of the already proposed
independent updater/storage/peripheral metadata reads, with the same identity
guards and stop conditions, excluding the denied tree-property reads. The
current adapter executes the full sequence only; do not silently skip its
failure or rerun it. Prepare and validate any revised plan before requesting
the specific revised device operation approval required by the packet. An
applicable original boot/DT/AVB artifact or updater consumer remains the
parallel host-analysis dependency; writes still require demonstrated recovery.

## B2 preparation and offline boot-access reassessment

2026-10-14. The human authorized preparation and offline testing only; **B2 has
not run**. The [fixed B2 packet](m10-stage-b2-authorization.md) selects eleven
previously unattempted metadata operations between the same eleven initial and
ending identity checks. It excludes both tree-content reads and low-value
raw-FDT/regulator listings, and moves uncertain device-node link metadata last.
The adapter change only selects and enforces that fixed scope. It does not
weaken the prior denial rule or introduce transport infrastructure.

The next decisive work remains accepted-payload and original-board recovery
analysis, with updater/loader/partition metadata as acquisition leads. Another
virtual boot or speculative Sony image build would not resolve those gates.

### Rechecked local evidence and exact limits

The one-off offline audit reused the existing read-only UPG inspector and
preserved source-member ledgers; no network, device requests, archive-wide
extraction, key guessing or rejected container hypotheses were attempted.
Private audit: `build/m10/b2-preparation-20261014-01/boot-evidence-audit.json`.

| Evidence class / exact artifact | Result and engineering consequence |
| --- | --- |
| **Verified from device-specific artifacts:** preserved complete `NW-A300Series_0002_V3_06_00_NW_WM_FW.UPG`, 1,589,253,264 B | Fresh read-only SHA-256 `50513039b47bb96952508f00e6c149312feb5ae3e3f920ba2fdd8f089d6fc643` and MD5 `a785c3d360bca2c0fd81f4182c9bec8b` match preservation/transport metadata. Inspector still identifies only the 128-byte NWWM outer profile, opaque body and unverified authentication. No selected images or recovery completeness are established. |
| **Verified from device-specific artifacts:** preserved `NW-A300Series_0002_info.xml`, XML after the 67-byte envelope | SHA-256 `94ed7dc95dfc1d60d46fc34e5ea1716afe3a558a68ed697c0ac10e92e91cfb77` matches M9. `Rules/Rule` requires firmware `>=1.00` and `<3.06`. This does not establish same-version reinstall, owner-region applicability or any custom signer/rollback policy. An update distribution is not a factory restore set. |
| **Verified shared Sony source; broader support, not selected runtime:** `kernel/msm-4.19/arch/arm64/configs/publishing/sony_dmp_android_defconfig:34,67-68,98-100,307-308,656-657` | Rechecked SHA-256 `8822ea40625c2b57c805519591f41f247dd02e41ed41b8091af17a5f73544b6c`. Published initrd and CMDLINE_EXTEND support leaves a source-level independent-init possibility; mandatory module signatures and empty static helper remain integration constraints. Published config is not the physical final `.config` or permission to edit boot inputs. |
| **Verified shared Sony source; broader support, not selected runtime:** `kernel/msm-4.19/init/main.c:338-361,1117-1145,1194-1200`; `drivers/of/fdt.c:988-1020,1171-1227` | Source bytes match M8/M9 ledgers. Kernel accepts ordinary init selection and consumes loader-supplied chosen bootargs/initrd addresses. Neither function authenticates or makes those inputs owner-controllable. The actual running release `4.19.157-perf+` narrows the family but does not establish binary/config equivalence to these sources. |
| **Verified shared Sony source; active policy unknown:** `kernel/msm-4.19/drivers/md/dm-verity-avb.c:104-107,127-128,131-152,177-200,224-229` | Rechecked SHA-256 `0d4f48b3ce9c57fbe5827542a806ce459a521c9e9037dda93c1c6e614fd8fe80`. `dm_verity_avb_error_handler()` gates on `invalidate_on_error=yes`, resolves a configured vbmeta device and calls a writer that changes header/footer magic and submits a block write. It is an optional error response, not a loader authentication implementation. Build selection, parameters and occurrence on this unit are **unknown**. No triggering experiment is proposed. |

The last source fact gives a concrete additional failure dependency: a system
initially delivered to RAM could still cause persistent storage effects through
its selected kernel/error policy. Before a boot experiment, establish the actual
verity/error/slot/rollback behavior and restoration coverage. Do not disable or
trigger that policy to investigate it. This finding does not change the reviewed
memory-backed proc metadata reads into raw filesystem or block reads.

### Conditional execution routes after the physical observations

**Demonstrated on physical hardware:** normal stock execution, shell identity,
reported locked/green state, kernel release and the tree alias; ordinary root
tree-property access was denied. **Unknown:** an accepted custom boot interface,
owner key policy, selected boot/DT/AVB graph and surviving same-board restoration.
No independent Linux boot route is currently demonstrated or deployment-ready.

The smallest plausible payload remains the accepted vendor kernel/DT/firmware
with independent Linux init and Rockbox, because it preserves the most existing
board support. This is an integration preference, not a discovered delivery
method. An unchanged kernel does not exempt a changed containing image, ramdisk,
DT, command line or root from authentication. Upstream Linux still needs the
same acceptance/recovery gates plus a larger Sony board port.

| Candidate delivery route / classification | What B2 could change | Required evidence to continue; condition to reject the branch |
| --- | --- | --- |
| Supported owner unlock/key enrollment or engineering temporary boot: **plausible but unverified** | Loader report could identify applicable implementation; unlock report is only a lead. No property value proves the interface. | Model-specific accepted entry, command/image/DT contract, persistent/security effects and recovery. Reject generic Xperia/QCS2290 instructions; reject temporary-boot branch if the applicable loader has no accepted RAM-load interface. |
| Existing accepted stock kernel selecting independent init/root: **source capability established; accepted selection unknown** | Partition and loader reports could select authentic artifact requests. Peripheral names narrow required stock-driver ownership. | Genuine boot/ramdisk/DT/AVB/fstab and an owner-controllable input accepted by that trust chain. Reject this route if every relevant input is authenticated with no supported independent selection. |
| Vendor updater/recovery consuming an alternative payload: **applicable consumer/authentication unknown** | A filtered updater candidate could identify the next lawful consumer acquisition and resolve NWWM framing/member/authentication evidence. Partition links could clarify names, not independent recovery entry. | Applicable consumer and complete decoded manifest; signer/coverage, version/variant policy and actual allowed payload set. If only vendor-signed immutable images are accepted, retain artifact/stock-recovery value but reject this as custom execution without a separate supported trust transition. Decryption alone supplies no signing authority. |
| Authenticated ROM/service execution: **broader Qualcomm capability; Sony acceptance blocked** | Partition names might narrow restoration scope. B2 supplies no service entry or programmer acceptance proof. | Exact-board accepted programmer/tool, hardware/security binding, rights and complete original-state reconstruction. No loader/programmer exists in the acquired set. EDL enumeration alone cannot support a boot or restoration claim. |
| kexec handoff: **broader source capability; selected config/privilege unknown** | No selected B2 read establishes this capability. Do not add privileged/config probing to this scope. | Final config, accepted privilege/handoff policy, device quiescence and recovery. Android-assisted launch alone fails independent power-on; deprioritize absent a concrete accepted contract. |

No applicable exploit, debug unlock or direct-storage trust bypass is established
by local artifacts. Those remain unsupported hypotheses, not proposed routes.
The existing ranked boot candidates and recovery-survival graph above remain
valid with these refined physical/access observations.

The next acquisition priority is the applicable updater consumer or a provenance-
bound boot/recovery/DT/AVB bundle. Then reconstruct authenticated coverage and
supported mutable inputs, determine an accepted execution interface and its
persistent effects, and establish restoration independent of the proposed
failure. Selected firmware/calibration and battery/thermal/watchdog/shutdown
ownership must be resolved before implementing a physical independent init.
B2 does not remove those requirements; its packet is the next specific
authorization decision, not a request to install or boot anything.

## Owner-authorized Stage B2 result and next investigation

2026-10-14. The human explicitly authorized the unchanged 33-observation B2
plan and confirmed the same normal, responsive, debugging-authorized stock
player with no update/playback/transfer. Before execution, the saved plan/code,
private profile and 187 earlier evidence/authorization files were revalidated.
The existing server's listener owner, process creation, native image path and
SHA-256 matched. An initial host-only label comparison used historical CIM
`adb.exe` versus Get-Process `adb`; the distinction was resolved using matching
process/path/hash evidence, preserving both assessments. No server or device
request was sent during those host checks. The session-specific approval was
generated only after preflight, without editing previous approvals or code.

The exact approved B2 adapter was executed **once** and stopped as required.

| Classification: demonstrated on physical NW-A306 hardware | Observation / precise limit |
| --- | --- |
| Initial eleven identity checks | All matched the approved locked/green shell/build/slot profile. These are runtime reports, not fuse attestation. |
| `/system/bin/getprop ro.bootloader` | `unknown` plus newline. No useful loader version or supported interface is identified. This does not prove there is no loader. |
| `/system/bin/getprop ro.oem_unlock_supported` | Empty value (one newline), exit zero. Does not establish implemented unlock support or impossibility; no setting or unlock request was made. |
| `/system/bin/getprop ro.build.version.release` | `14` plus newline. Matches the platform reference generation, not boot-image packaging or binary equivalence. |
| `/system/bin/pm list packages --user 0 -s systemupdat` | One result: `com.sony.walkman.systemupdater`. This establishes its registration in the scoped system/user-0 query, not its path, content, activity or exact installer implementation. |
| `/system/bin/toybox head -c 65537 /proc/partitions` | Exit 1, empty stdout, `Permission denied` stderr. DAC/SELinux/traversal cause remains unknown. No partition contents or topology were acquired. |

Result: **B2 incomplete**, 15 valid observations, 16 attempted, 17 unattempted,
81 connections and 16,048 wire bytes. The six audio/input/display/power/partition-
link inventories and eleven ending identity checks were not reached. Successful
records passed their individual before/after guards; full-session ending
consistency cannot be claimed. There was no retry, alternative path, privilege
escalation, mode transition, reboot or intentional persistent-state change.
No further device communication followed the denial.

Independent local validation passed all raw/decoded hash and byte-count checks,
compared the exact approved service prefix including transmitted close-stdin,
decoded each atomic selection and shell-v2 frame sequence, compared stream bytes
and exit statuses, validated each successful payload, and rechecked all 187
earlier files unchanged. The running acquisition code still matches the approved
plan digest. Private evidence: `build/m10/device-stage-b2-20261014-01/`;
host provenance, original/resolved preflight assessments and validation script:
`build/m10/stage-b2-preflight-20261014-01/`; exclusive execution approval:
`build/m10/authorizations/stage-b2-20261014-01.json`. Identifiers remain private.

### What this changes about independent boot and recovery

The updater is now a **device-specific artifact acquisition lead**, replacing a
generic search for an unidentified installer. Existing local reference filenames
and scoped textual searches of prior firmware/research/vCapBlock material did
not locate that consumer. The preserved four audio-named APKs are not a supplied
systemupdater artifact. This is a bounded local negative result, not evidence
that the consumer is unavailable or absent inside every archive. No new APK was
opened, acquired, executed or published.

The next highest-value operation is the exact unprivileged package-path metadata
query proposed as U1 in the [standing policy](m10-readonly-standing-authorization.md),
then separately bounded acquisition of the applicable code if lawful access and
exact paths permit. The preserved AOSP package-manager source supports the query
semantics; it is not a Sony access guarantee. Neither U1 nor any other new device
operation was executed. Consumer analysis should determine NWWM framing,
authenticated/decrypted ranges, decoded full-versus-delta member inventory,
version/variant/signature checks and the actual installation/recovery handoff.
Do not infer those from a Java package name or reuse an older A100 decoder.

The unknown loader and empty unlock report add **no positive accepted-execution
evidence**. Bootloader owner-policy, engineering RAM boot and accepted independent
init/root selection remain unverified. Updater analysis outranks another generic
kernel build because it could expose authentic boot/recovery/DT/AVB bytes and
their actual coverage. Even a decoded update or embedded public key would not
establish custom payload acceptance, the board's trusted key or an independent
surviving restore path. A vendor-only signature policy would retain artifact/
stock-update value while ruling out that updater as a custom-execution route
without a supported trust transition.

The partition denial adds a second real access barrier; it does not establish
the cause or rule out independently permitted class/link metadata. Neither
denied read may be retried or reached through an alias. The untouched inventories
remain unknown and secondary to the updater lead. No boot candidate now passes
the acceptance/board-support/original-board-recovery gates; M10 remains open.

The proposed standing policy is **inactive pending one explicit approval**. It
would remove repeated requests for fixed U1/H1 sessions under unchanged identity,
host, freshness, limits and evidence conditions, and quarantine failures. It
does not expand authorization to acquisition bytes, writes or boot experiments.

## Standing policy activation and U1/H1 physical results

The human approved fixed U1/H1 policy v1 and its minimal enforcement implementation.
The [implementation and physical-results report](m10-standing-readonly-results.md)
records 122-test offline validation, source-bound plans and private provenance.
The exact approved policy document and all prior physical evidence remain intact.

**Demonstrated on physical NW-A306 hardware:** U1 completed all 23 observations
and identified one registered `automagic.apk` location under `system_ext` for
`com.sony.walkman.systemupdater`; the exact path is private. Ending identity
checks passed. No APK content was read. H1 passed eleven initial identity checks
then stopped on a permission denial at `/proc/asound/cards`; its other five
inventories and ending checks were not attempted. The failed operation is
quarantined and H1 is disabled under the unchanged standing policy. No further
device action followed that failure.

The highest-value next input is the exact updater APK for bounded static consumer
analysis. The same namespace in historical M2 decoder research is a comparison
lead only. APK/OTA/boot authentication and recovery remain separate unknowns;
there is still no demonstrated independent Linux delivery or original-board
restore. A private one-artifact acquisition proposal records commands, bounds,
risks and expected decisions. Acquisition bytes need separate approval and
offline implementation validation; metadata permission does not cover them.

## Acquired updater: actual decoder and installer handoff

The owner separately authorized one bounded read-only acquisition of the exact
U1 APK. The [updater analysis](m10-updater-analysis.md) records first-attempt
success, 1,337,774 preserved bytes, raw-frame/hash/ZIP/v3-signature verification,
132-test offline checks and private provenance. No updater code, service or
extracted library was executed; H1 and denied reads stayed untouched.

**Verified from the device-specific APK:** the active NWWM decoder uses a
128-byte header, AES/CBC/PKCS5Padding and SHA-224 over plaintext. Its key/IV come
from `vendor.sony.securestorage@1.0::ISstorage/default`, not an established
offline constant. The decoded ZIP is expected to contain stored `payload.bin`
and `payload_properties.txt`; the client calls Android UpdateEngine with the
file/offset/size/properties. No key was retrieved and no UPG was decrypted.

This identifies the real format consumer and two external dependencies. It
does not establish native payload-signature policy, accepted custom boot inputs
or recovery. Prioritize build-matched native UpdateEngine verification/public-key
configuration and the HAL implementation, or an applicable decoded stock OTA,
before another generic image build. APK signing, decryption, payload signing
and boot/DT/AVB acceptance remain distinct. All additional device artifact or
property reads require their own authorized scope; M10 remains open.

## Native firmware trust boundaries and boot-entry priority

The subsequent [firmware trust investigation](m10-firmware-trust-boundaries.md)
pins Android 14 native verifier/writer source and compares the relevant QPR
policy functions. This is platform evidence, not a build-matched Sony binary.
The Android API clears caller-supplied keys; official-build metadata checks
prevent treating the missing-key fallback as an unsigned-install method. OTA
submission can mutate slot/update state before rejection and is not a read-only
verification test. The four official UPG URLs remain available, but no decoded
selected boot/DT/AVB set or same-board restoration facility was acquired.

Prioritize actual loader acceptance and a surviving restoration entry over
further NWWM wrapper work or secure-storage provisioning research. Authentic
selected boot/DT/AVB/loader artifacts are the primary missing input; installed
native UpdateEngine/public OTA certificates can resolve the narrower Sony OTA
policy gap under a future bounded acquisition approval. No device command ran
in this increment, no secret was collected, and no custom boot route is ready.

## Physical feasibility: selected loader is the next evidence blocker

The subsequent [boot feasibility assessment](m10-boot-feasibility.md) traces the
published reset-driver selection, the orange-state gate on one software EDL
entry, and IMEM/PMIC reset-state effects. These are shared-source facts, not
running-image verification or an original-board recovery method. No new device
operation ran. Early-loader temporary boot with the stock kernel remains a
conditional investigation target; no accepted custom payload is established.

Defer the previously suggested native UpdateEngine/OTA-certificate acquisition:
it cannot settle early-loader acceptance or surviving recovery. Prioritize an
authentic running-build OS-loader image and trace its actual command/authentication
handlers. Its Sony partition name, an authorized read-capable interface and
same-board restoration remain unresolved. No blind mode transition or generic
programmer is proposed, and M10 remains open.
