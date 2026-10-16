# Research roadmap

Research through M9 is complete. M10 engineering and guarded characterization
are in progress. KC1 confirms that the running stock kernel disables ordinary
legacy kexec; that immediate execution route is closed for the observed build.
The working system remains a generic ARM64 Linux prototype. Custom NW-A306
execution, hardware compatibility and original-board restoration remain
unverified. The target is independent Linux supporting native Rockbox and a
general-purpose handheld environment.

The milestone reports below retain dated findings, source locators, negative
results and test evidence. Future acceptance criteria describe requirements,
not demonstrated capabilities. The [hardware matrix](hardware-matrix.md)
tracks subsystem gaps.

## M0 - Evidence and feasibility foundation

The [feasibility assessment](feasibility.md) establishes the evidence register,
compares minimal Linux with bare metal and identifies boot, recovery, audio and
power dependencies. Minimal Linux with Rockbox as the primary interface is the
leading direction. A Rockbox Android application, launcher or modified Android
system does not meet the standalone objective. Feasibility remains unproven.

## M1 - Offline boot and recovery evidence

[Recovery provenance](recovery-provenance.md) identifies four Sony update
variants and inspects their manifests/headers. One complete UPG matches its
advertised size and MD5, with an independent SHA-256 record. Update availability
establishes neither a complete image set nor same-version reinstall, custom-image
acceptance or restoration from unbootable Android.

## M2 - Container analysis and host architecture

[Firmware analysis](m2-firmware-analysis.md) reconciles variant-size differences
and defines the observed NWWM header profile. Ten synthetic inspector tests
passed; the payload remains opaque. The older Android Walkman AES-CBC decoder
is a comparison lead, not a demonstrated A306 decoder.

[Host validation](m2-host-architecture.md) built native Rockbox Warble and 40
codecs, reproducing all 41 hashes in a clean same-environment rebuild. WAV/FLAC
PCM matched exactly. Opus failed an EOS/frame-count test, motivating M3. No
ARM execution or complete application playback was established in M2.

## M3 - Opus correctness and AArch64 execution

[Codec validation](m3-codec-validation.md) records the EOS/granule, seek,
harness-scaling/error-status and cross-link fixes. All 38 checks passed on
native Linux, AArch64/QEMU and native ASan; the unpatched baseline failed 34.
All 48 fixture/reference hashes reproduced, as did 41 native and 41 ARM64
build-output hashes.

[AArch64 bring-up](m3-aarch64-bringup.md) establishes actual ELF/runtime
requirements and SDL UI rendering, injected key events and normal shutdown.
[Board research](m3-board-dependencies.md) adds calibration ABI, battery-profile
and charging/thermal source contracts. Target hardware remained untested.

## M4 - End-to-end hosted playback

[Application validation](m4-playback-validation.md) exercises real playlists,
codec loading, PCM output and WPS controls. Ten scenarios passed, including
mixed transitions, timestamp resume, one-frame Opus and repeated playback.
WAV/FLAC PCM matched exactly; Opus delivered 108,001 frames at 48 kHz with
68.79 dB reference SNR.

The forced-resampling comparison failed and mixed-rate transitions included
silence. Native ASan passed; ARM64 instrumented Rockbox hung despite successful
negative-case probes. These remain limits, not passing memory-safety results.
[Integration requirements](m4-nwa306-integration.md) and
[boot/recovery analysis](m4-boot-recovery-next-steps.md) identify missing board
resources, firmware and restoration evidence.

## M5 - Generic Linux boot and input/audio integration

The [Linux prototype](m5-linux-prototype.md) boots an Android-free ARM64 guest
into Rockbox and delivers checked WAV/FLAC/Opus through kernel ALSA/virtio sound.
Synthetic uinput/evdev taps pause/resume playback; drag coordinates reach
Rockbox. Seven VM checks passed, including repeated boot and missing-application
shutdown. Two forced builds reproduced all 42 outputs and repeated initramfs
packaging was identical.

[Playback reliability](m5-playback-reliability.md) adds decoder-error delivery
to the hosted UI. The ten application scenarios, 38 ARM64 codec, 38 native ASan,
ten inspector and seven safety tests passed. Chained Opus remained unsupported;
ARM64 shared-ASan crashes and static-ASan hangs also occurred in a full guest.
[Hardware contracts](m5-hardware-evidence-plan.md) define required safety and
interface inputs. [Service research](m5-boot-recovery-paths.md) distinguishes
Sony's published US product-exchange policy from same-board restoration.

## M6 - DRM/KMS virtual scanout

[Display integration](m6-linux-display-integration.md) adds actual DRM dumb
buffers and page flips with independent QEMU captures. Playback, aligned touch,
normal cleanup and repeated boot passed; unsupported mode was rejected. Two
forced builds reproduced 42 outputs. The application, codec, inspector, safety
and seven VM regressions passed within their recorded limits.

The [artifact inventory](m6-board-artifact-inventory.md) compares an authentic
20230714 Sony source archive with the pinned newer release; neither supplied a
selected Sony board DT. Related QCM2290/RB1 sources remain platform references.
[Execution](m6-custom-boot-assessment.md) and
[recovery](m6-recovery-engineering.md) matrices separate image acceptance,
compatible handoff and surviving restoration paths.

## M7 - FCC evidence and hardware convergence

The [FCC review](m7-fcc-evidence.md) inventories 43 PDFs/594 pages and reviews
ten internal-photo exhibits. The certification sample shows SODAGREEN M/B 1.03,
QCS2290, PM4125, Samsung KLMBG2JETD storage, audio-family marking 3778, WCN3950
and LIS1650 battery. Owner-board equivalence and a proposed board date remain
unverified. Of 31 catalog digest matches, 29 retain a two-byte size-metadata
conflict; 12 documents have no catalog digest.

[Hardware convergence](m7-hardware-convergence.md) prioritizes eMMC/SDHCI and
separates Android boot slots, hardware boot areas and RPMB. The
[execution/recovery report](m7-boot-recovery.md) distinguishes Sony's radio
firmware authentication declaration from OS boot policy. Eight inventory tests,
ten inspector and seven safety tests passed. Preserved M6 captures revalidated;
these were not fresh runtime experiments.

## M8 - Boot/storage and startup dependencies

The [storage model](m8-boot-storage-architecture.md) separates eMMC regions,
EXT_CSD protection, GPT, A/B, super, AVB and RPMB. Eight synthetic EXT_CSD tests
passed. The [artifact/source audit](m8-board-firmware-artifacts.md) traces init,
firmware delivery and module signatures. Three NWWM stored-byte SHA-224
hypotheses failed; the body remained opaque.

[Execution paths](m8-execution-paths.md) prioritize selected stock-kernel and
independent-init evidence. The [recovery matrix](m8-recovery-assessment.md)
identifies surviving-stage and unique-state requirements. Thirty-three unit
tests passed; earlier outputs and captures revalidated. The historical
[M9 proposal](m8-next-milestone.md) records the resulting research questions.

## M9 - Selected artifacts and independent userspace

The [artifact inventory](m9-boot-artifact-inventory.md) finds no selected
boot/DT/AVB bundle; four fresh official manifests match M1 byte for byte. DTC
fuzz-corpus trees are excluded from Sony hardware claims.

The [userspace audit](m9-stock-kernel-userspace.md) traces successful-no-op
module autoload, ABI/signature checks, firmware/node readiness and thermal/
watchdog ownership. Its 13-role dependency contract rejects omitted roles,
cycles and ordering bypass and propagates failures. Forty-two unit tests passed,
including nine contract tests also passing in WSL. Preserved M6 results
revalidated without new guest boots.

The [authentication model](m9-authentication-boundaries.md) separates boot/DT/
init coverage, modules and peripheral trust. The
[recovery analysis](m9-recovery-readiness.md) requires independently surviving
entry, accepted reconstruction artifacts and unique-state continuity. No
alternate init/root or original-board restoration is verified.

## M10 - Artifact acquisition and execution acceptance (in progress)

The immediate priority is authentic firmware acquisition as a distinct objective:
original ABL/XBL/boot/DT/AVB bytes and actual layout, or firmware-processing code
that can establish a concrete acquisition capability. Acquisition, independent
execution and same-board restoration require separate evidence. Manufacturer
cooperation and additional hardware are not prerequisites for continued research.
The [M9 decision report](m9-next-decision.md) retains the historical service
questions and acquisition limits.

Host analysis should establish a new validated container/resource fact or a
precise access boundary that determines the next bounded acquisition. Validate
image bounds, build/region provenance, DT selection, authenticated coverage and
recovery dependencies before implementing target adapters. A synthetic all-ready
profile cannot substitute for an acquired artifact.

The [first M10 host increment](m10-physical-boot-investigation.md) establishes
the shared Sony source's live-tree versus raw-FDT access boundary and implements
a fixed characterization plan with offline replay/provenance tests. It has no
live transport and establishes no device access. Boot-path ranking, recovery
survival dependencies and the next separately authorized read-only request are
recorded there. M10 remains incomplete; selected images, accepted execution
and same-board restoration remain unresolved.

Subsequent physical [N2](m10-n2-results.md) establishes reported bootloader
fastboot and intact-stock return; [P1](m10-p1-execution.md) records successful
bounded partition-name/permission characterization. Neither establishes image
acceptance or a usable partition reader. [KC1](m10-kc1-results.md) successfully
captured the running configuration: `# CONFIG_KEXEC is not set` at decoded line
391. Additional Android privileges alone cannot provide an omitted kernel
facility. Do not repeat that investigation without materially new evidence.
The preserved minimal ARM64 initramfs and analysis tools remain available
for later bring-up; their QEMU result is not Sony execution or cold boot.

The [execution pivot](m10-execution-pivot.md) acquires the original public A306
EDL images and tests a pinned host client's diagnostic behavior offline. The
images support reported download-mode enumeration, but contain no programmer
transaction or authentication rejection. Sony temporary-boot registration,
locked-state policy and pre-authentication writes remain unknown. Prioritize
original Sony acceptance evidence or a demonstrably applicable reader over
further generic loader comparisons. A complete ABL dump is one evidence route,
not a universal requirement. Independent execution, independent cold boot and
same-board restoration remain separate, open milestones. The
[checkpoint inventory](m10-source-control-checkpoint.md) includes KC1 and the
current review boundary; no further device operation is authorized.

The [firmware acquisition increment](m10-firmware-acquisition.md) tests a standalone
client for the actual Sony OTA-material API, independently of installation. Host
ABI/client checks pass; real shell admission and usable provisioning remain
unverified. The [SK1 proposal](m10-sony-ota-key-proposal.md) defines the specific
experiment on the existing player, including temporary helper writes and a HIDL
call with unverified server effects and implicit framework interface validation.
The canonical wrapper and unapproved offline review package are complete;
physical execution remains unauthorized. The updater success-path finding is
recorded and closed; no ABL
reader, plaintext OTA or new Sony boot image was acquired. No donor is required.

## Later hardware gates

1. **Accepted execution and recovery.** Establish model/region/revision-specific
   image acceptance and original-board restoration covering the intended failure
   states, including unique provisioning/calibration. A matching spare reduces
   exposure but does not replace recovery proof.
2. **Controlled boot and protection.** Validate the accepted kernel/DT handoff
   and minimal userspace with charging, thermal, watchdog and shutdown ownership.
   Keep analog output muted and demonstrate the reviewed restoration path.
3. **Display, input and storage.** Verify panel/backlight lifecycle, input
   orientation/wake behavior, internal/microSD access, removal and I/O failures.
   Generic guest results do not satisfy these hardware criteria.
4. **Wired audio.** Validate matching firmware/calibration, DAI routing, jack
   behavior, bounded gain/mute sequencing and failure shutdown before listening.
   Measure rates, precision and resampling before any bit-perfect claim. Power-on
   must reach Rockbox independently of Android userspace.
5. **Reliability.** Exercise cold boots, suspend/wake, charging/playback, low
   battery, thermal faults, media hotplug and recovery under a reviewed plan.
   Measure drain and boot time. Optional connectivity/effects require their own
   dependency and licensing assessment.

Each physical operation requires explicit approval and its hardware-safety
prerequisites. These gates define dependencies, not a release schedule.

## Release requirements

An installable system requires verified hardware operation and dependable
installation/restoration, reproduced by another developer. Supply pinned inputs,
applicable GPL and other license compliance, maintenance documentation and
truthful compatibility limits. Publication of this research prototype does not
establish an installable firmware release.
