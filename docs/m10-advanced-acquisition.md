# M10: loader acquisition and hardware investigation

2026-10-15. This increment implements host inspection and evaluates new
acquisition avenues. No device command, boot transition, electrical probing,
disassembly, firmware execution or Git history operation occurred. Prior
physical failures and private evidence remain preserved. M10 remains open.

## Decision and measurable question

**Question:** can authentic related-platform artifacts establish a reproducible
loader-analysis workflow, and do the Sony photographs support an acquisition
route independent of ordinary Android permissions and NWWM decoding?

Acceptance criteria for this host increment: acquire a provenance-bound public
reference bundle; inspect selected images without running them; distinguish
hash consistency, embedded-key signature verification and actual device trust;
reject invalid recovery geometry despite valid CRCs; test corruption/bounds;
identify a source-bound physical target and the next experiment's limits.
These criteria do not include a Sony loader acquisition or independent boot.

**Result:** reference analysis is now reproducible. The strongest new route to
actual Sony loader bytes is targeted acquisition at the eMMC boundary, first
investigating in-system access on a separate research board. That bypasses the
Android file-permission and OTA-wrapper boundaries; it does not bypass secure
boot. Its electrical feasibility, read access and the presence of plaintext
loader images remain **plausible but unverified**. Passive boot-console research
is a complementary, potentially less invasive route to behavior, not an
equivalent binary acquisition.

## Concrete reference analysis

The public [Qualcomm Linux flash recipe](https://github.com/qualcomm-linux/qcom-deb-images/blob/main/debos-recipes/qualcomm-linux-debian-flash.yaml)
selects the RB1 23.12 rescue archive for `qcm2290` (preserved recipe lines
412–419). Its published SHA-256 matches the downloaded 23,218,788-byte ZIP:
`c75b6c63eb24c8ca36dad08ba4d4e93f3f4cd7dce60cf1b6dfb5790dc181cc3d`.
The archive, license, provenance, selected members and analysis stay ignored
under `build/m10/advanced-boot-20261014-01/`. No archive program was executed.
This is an authentic public **reference-board artifact**, not Sony firmware or
an accepted Sony programmer. QCM2290/RB1 compatibility is not QCS2290/Sony
DDR, OEM, security-policy or storage compatibility.

| Selected reference member | Actual offline result | What it establishes |
| --- | --- | --- |
| `abl.elf` | ELF32/ARM container; 3 program headers; MBN v6 envelope | Container width is not necessarily code width. Its load region contains a checksum-valid PI firmware volume and LZMA GUID-defined section. The nested `LinuxLoader` PE image is **AArch64**, machine `0xaa64`. |
| `xbl.elf` | ELF64/AArch64 container; 17 program headers; MBN v6 | Real early-image envelope and segment geometry for this reference release. No Sony stage identity is inferred. |
| `prog_firehose_ddr.elf` | ELF64/AArch64 container; 17 program headers; MBN v6 | A public related-platform programmer exists. Its presence, signatures and name establish neither Sony acceptance nor Sony initialization compatibility. |
| `gpt_main0.bin`, `gpt_backup0.bin` | Header and array CRCs match; geometry fails | These are installation templates. Last usable LBA and alternate-header fields include placeholders; `rootfs` ends before it starts. `patch0.xml:6–17` supplies disk-size-dependent patches. They are not captured recovery layouts. |

All **37 segment hashes match**. Each image contains 120 bytes of OEM metadata,
a 104-byte OEM signature allocation and a 6,144-byte certificate allocation.
A separate private check with trusted `cryptography` verifies all three
ECDSA-P384/SHA-384 image signatures against their embedded leaf keys and nine
certificate signatures, including the embedded roots' self-signatures. This
does **not** authenticate those roots against Sony fuses or any external trust
anchor, validate Sony policy, or show the player would execute these images.
Three in-memory signature-corruption controls are rejected while segment
hashes continue to match. Original artifact bytes are unchanged.

The first signature check failed because the allocated signature includes
zero padding beyond the DER object. Its result is preserved separately; the
corrected checker validates the DER length and padding before verification.
The private FV walker likewise explicitly skips FFS PAD/RAW files; its initial
PAD interpretation failure was a parser limitation, not malformed firmware.

Format references are ELF gABI, [coreboot's MBN header definitions](https://github.com/coreboot/coreboot/blob/812d0e2f626dfea7e7deb960a8dc08ff0e026bc1/util/qualcomm/mbn_tools.py)
(`Boot_Hdr`, preserved lines 509 onward), and pinned TianoCore
`edk2-stable202402` PI headers and [LZMA GUID definition](https://github.com/tianocore/edk2/blob/edk2-stable202402/MdeModulePkg/Include/Guid/LzmaDecompress.h).
No reference firmware implementation is copied into the public tools.

Material revision conflict: Linaro's [2024 U-Boot article](https://www.linaro.org/blog/initial-u-boot-release-for-qualcomm-platforms/)
describes newer RB1/RB2 work using v7 envelopes and developer boards without
enforced secure boot. This acquired 23.12 bundle has v6. Neither observation
selects Sony's version. Dummy signing is a development facility, not evidence
of bypassing a production root of trust. Replacing XBL/hypervisor components
also has firmware-handoff consequences even on a compatible development board.

Bounded strings from the extracted reference PE identify fastboot, recovery,
AVB and rollback-related diagnostics; offsets and input hash are private.
Strings are locators, not command-handler or lock-policy proof. Attempts to
retrieve the indicated RB1 ABL source branch returned HTTP 429; those failures
are recorded. No source-level handler comparison or Sony vulnerability is
claimed. [BootStomp](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/redini)
and [Wade's bootloader research](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/qpss22-christopher-wade.pdf)
provide analysis precedents, not a demonstrated vulnerability in this model.

## Sony boot architecture: known boundary versus missing implementation

**Demonstrated on the physical NW-A306:** locked/green verified boot,
QCS2290 report, stock Android boot and kernel `4.19.157-perf+`. These do not
identify the fuse state, root digest, loader generation or every verification
operation. **Verified from device-specific artifacts:** the updater delegates
installation to UpdateEngine. Historical names include boot, recovery, dtbo
and vbmeta A/B pairs; complete geometry, early-loader names and use of
vendor_boot/init_boot remain unknown. Sony published source restricts one
software EDL reset branch to orange state; it does not establish ROM entry or
programmer acceptance. See [prior source locators](m10-boot-feasibility.md).

**Broader platform:** ROM authenticates subsequent executable stages under
configured hardware policy; later loaders establish OS/AVB trust and handoff.
The reference bundle concretely supplies XBL and a LinuxLoader-bearing ABL.
Mapping these names, trust keys, rollback storage, fastboot implementation,
selected DT/ramdisk coverage and Sony-specific configuration onto this Sony
is still **unknown**. Storage boot regions, user-area GPT, RPMB and SoC-bound
state must be investigated separately. Shared PMIC/IMEM restart code does not
prove safe return from a foreign kernel or a service mode.

## Evidence-bound physical interface map

These locations refer to the **FCC certification sample**, SODAGREEN M/B
REV:1.03. They are not the owner's board revision or an electrical pinout.
The preserved originals and hashes are in [M7 evidence](m7-fcc-evidence.md).
The later user screenshot contains these same views; it adds no new net or
electrical observation.

| Target / original photograph | Confirmed visual evidence | Unknowns and next discriminating observation |
| --- | --- | --- |
| U2, Part 10 p. 1, beside U1 | Samsung base marking `KLMBG2JETD`; eMMC family identified in M7/M8 | Exact suffix/ball map, bus nets, rails, access protections and boot-region configuration. Read actual research-board marking before selecting datasheet or reader. No assumed BGA pinout or voltage. |
| Staggered round gold pads beside the board-to-board connector, Part 8 p. 2 | An exposed pad cluster near revision text and mounting holes | No UART/JTAG/SWD/eMMC/EDL identification. Optical revision match first; later separately approved continuity/voltage/activity measurements would distinguish nets. |
| U1 and U2 area, Part 6 overview versus Part 10 p. 1 | Shield present in assembly view, removed in component view | Test-pad accessibility on a retail assembly and need for shield rework are unknown. Photograph exposure is not evidence of safe shield removal. |
| Battery/jack area, Part 9 p. 2 | `+`, `-`, `T` labels and connectors | Battery/power area, not established debug pins. Do not attach a serial adapter or infer a logic supply. |
| U2403, Part 10 p. 2 | Package and nearby traces visible | Function and usable interface unknown. The photo cannot establish a debug ASIC or follow all multilayer nets. |

## Investigation ladder

Order means expected information value and prerequisites, not probability of
success. Cost categories are relative engineering estimates, not quotations.
Every physical step below requires new, specific approval.

| Approach / capability | Work possible now; tools and prerequisites | Decisive experiment, persistence and risk | Effect on deployment |
| --- | --- | --- | --- |
| 1. Supplied authentic Sony dump or decoded bundle | Inspect offline with the new tools; bind board/build/provenance. Public reference workflow completed; no applicable Sony dump found. Low host cost. | Validate loader envelopes, firmware volumes, selected boot/DT/AVB and geometry. Reject mismatched, patched or incomplete provenance. No player access. | Fastest analysis if a lawful original artifact becomes available; acquisition alone grants no execution. |
| 2. Research-board optical map, then passive boot UART | FCC location map completed. Need separate exposed board, ESD bench, microscope/camera. Later need high-impedance scope/logic capture and measured logic levels. Low-to-moderate lab cost plus unit. | H0 below. Later capture only after verified ground/Vref; sense TX without driving unknown pads. No intended storage writes, but opening/probing/normal boot have mechanical, electrical and availability risks. Reject UART lead if no observable serial activity under the approved conditions; silence does not reject storage acquisition. | Could identify stages/builds, selected boot sources, errors and modes; no guarantee of a console, commands or loader bytes. |
| 3. Targeted eMMC ISP acquisition | Reuse existing EXT_CSD tool plus new GPT/ELF tools. Need exact part data, verified CMD/CLK/DAT0/GND/VCC/VCCQ mapping, controller isolation, compatible reader and reviewed command trace. Moderate-to-high difficulty. | First read-only identity/configuration and bounded primary/backup GPT regions; then explicitly scoped loader regions. No automatic reader configuration writes, guessed rails or bus contention. Risk of electrical damage/back-powering; no intended persistent write does not mean harmless. Reject ISP setup if safe isolation or verified mapping is unavailable. | Can expose authentic loaders without Android permission or NWWM decoding; stored images may still have additional protection. Does not defeat signature policy. |
| 4. Build-bound bootloader/recovery interface observation | Prepare only after defining actual entry/exit and owner binding. Need approved mode transition, capture and tested stock return. Lower equipment cost, unresolved availability risk. | Distinguish early fastboot from userspace fastbootd, then fixed metadata-only commands. No downloads, boot, unlock, erase or flash. If loader lacks a relevant handler, eliminate that handler-based route on that build. | Directly narrows command implementation and acceptance prerequisites; metadata is not accepted custom execution. |
| 5. ROM/service-mode programmer investigation | Reference signed envelope available for comparison, never a Sony upload candidate. Need Sony ROM/OEM/security identity, applicable accepted programmer and verified DDR/storage initialization. | Separately reviewed bounded handshake/identity observation only after entry/return risk resolved; no fuzzing or loader upload in an initial inventory. Reject mismatched trust/initialization; USB 9008 or Sahara visibility alone is insufficient. Service entry may strand availability. | Could provide read/repair access if the exact acceptance and rights are established. No demonstrated Sony restoration today. |
| 6. Static Sony loader/security analysis | Reference unpacking and integrity workflow ready. Need actual Sony code/build; use disassembler, call graph and host parser harnesses. Analyze command checks, authenticated byte ranges, validation-to-use paths and reset/write effects. High analysis difficulty. | Test a concrete code hypothesis with offline corruption/coverage oracles before any device experiment. A known issue on a different chip/build is not applicability. No Sony vulnerability identified in this increment. | Could reveal a supported policy or build-specific execution flaw; a volatile foothold still needs an eventual persistent Android-free boot route. |
| 7. JTAG/SWD or authorized debug | Need exact SoC package/debug nets, Vref/reset mapping and debug authorization state. No confirmed header in photographs. High setup difficulty. | After separate electrical approval, determine whether the correctly identified interface responds and whether authentication permits useful access. Reject exposed-debug route if it requires unavailable OEM authorization; do not infer this from silence alone. | Potential memory/behavior evidence, conditional on actual debug policy; no current capability. |
| 8. Chip-off on sacrificial board | Need qualified BGA rework, exact socket/reader, preservation plan and a unit that may be lost. High cost/risk. | Capture storage only after ISP is unsuitable and rework is approved. Physical removal can destroy chip/board; readout may omit RPMB/SoC-bound state. | Alternative to bus isolation for acquisition. A raw copy is not a demonstrated restore or signature bypass. |
| 9. Equivalent-board lab and fault injection | Reference-board boot tools can be validated separately. Fault work needs actual Sony stage timing, power/reset map, passive traces, trigger, scope/glitch equipment and expendable unit. Highest research cost; no purchase made. | Equivalent-board results establish only lab technique. Sony fault experiments require a concrete target/check and controlled sacrificial setup after preservation. Brownouts/glitches can corrupt storage, protection or power hardware. | A research avenue if a specific acceptance weakness is testable, not a promised bypass. Not appropriate on the working unit now. |

## Independent execution candidates

No candidate is currently verified viable. The strongest next **execution
hypothesis to discriminate** is whether the actual early loader contains an
owner-authorized or otherwise accepted volatile boot path. The reference
LinuxLoader makes static investigation concrete, but supplies no Sony policy.
Preferred initial payload strategy remains an authentic vendor kernel/DT and
independent init/Rockbox if an accepted controllable input exists.

| Candidate | Established / unresolved | Reject or advance; persistent state and recovery |
| --- | --- | --- |
| Early-loader accepted RAM payload | Sony locked/green is physical; actual command/authentication policy unknown | Acquire Sony handler/trust evidence. Absent handler or unauthenticatable changed input eliminates that branch. RAM delivery can avoid installation, but boot counters, rollback, watchdog and payload writes must be assessed; a known stock return and failure repair are required. |
| Supported owner trust transition/enrollment | No model/build-specific supported unlock established | Actual handler/policy could establish support or prohibit it. Requires persistent security changes and possible erasure; approved original-state preservation and accepted restoration needed before testing. |
| Bootloader/parser/debug/security weakness | General research precedent only | Authentic Sony binary and concrete reachable check are missing. Static evidence could justify a bounded sacrificial experiment or rule out an individual flaw. Volatile execution is possible in principle; durable boot and recovery are separate problems. |
| Accepted stock image selecting independent init/root | Stock boots; shared Linux supports init selection | Need selected authenticated graph and owner-controllable input. Reject if all usable selectors are authenticated with no permitted override. A rootfs write is persistent; stock accepted images and repair required. |
| Sony updater/recovery delivering modified images | Real updater delegates to authenticated native install; no changed-image acceptance | Must satisfy installer and bootloader independently. NWWM decoding alone cannot do so. Persistent writes; complete accepted reconstruction and surviving repair entry required. Secondary priority unless new trust evidence changes this. |
| Service programmer or direct storage writes | eMMC acquisition is a plausible evidence route; Sony programmer acceptance unknown | Reading/copying bytes does not authorize a changed next stage. Need accepted programmer rights plus boot trust transition or specific weakness. Writes threaten shared early state; exact-board recovery prerequisite remains. |
| Android-assisted kernel handoff | Platform precedent, no project hardware demonstration | Can aid lab testing only if selected config/privilege allows it; it does not itself meet independent power-on. No new privilege experiment proposed. |

## Next concrete physical proposal: H0, optical only

**Target:** the Part 8 p. 2 pad cluster and U2 area on a separately supplied,
already exposed NW-A306 research board. Keep the working player intact.
Procurement, enclosure opening, battery desoldering and shield removal are not
covered by this proposal; an assembled donor first needs its own reviewed
mechanical procedure. No purchase or teardown has occurred.

**Hypothesis:** a retail research board exposes a corresponding candidate pad
cluster without RF-shield rework, and its storage marking/revision can be read.
This is the first safely testable prerequisite for ISP/UART planning, not a
claim that those pads provide either interface.

**Exact scope:** confirm with the supplier/technician that USB and battery are
disconnected; use an ESD-safe fixture without flexing the board; take one
overview of each face with orientation and scale, then focused images of board
revision, pad cluster, U2 marking if already visible, and shield boundaries.
At most 20 original photographs, each at most 25 MiB. Store originals privately
with acquisition time, board label and SHA-256; make a separate location map.
No powered measurements, continuity tests, soldering, heat, scraping, electrical
connections or storage commands. No device secret or provisioning read.

**Equipment:** separately supplied exposed board, ESD bench/fixture, microscope
or macro camera, scale and evidence workstation. **Risk:** low compared with
electrical/rework experiments, but ESD, handling and pre-existing battery
damage remain possible. No intended persistent software change. Confirmed
power isolation and a handler competent in battery/ESD safety are prerequisites.
Stop if isolation is uncertain, the board requires force/rework to expose a
target, battery damage is visible, or identity/revision cannot be documented.
An occluded marking is recorded as occluded, not uncovered by improvisation.

**Expected evidence:** original photographs establishing pad accessibility,
retail revision and readable storage suffix, or a recorded negative result.
If pads differ or require rework, revise the access strategy before electrical
work. If they match, prepare a separately approved passive voltage/activity
survey; never connect a 3.3-V UART adapter to unknown pads. ISP requires a later
verified net/rail/isolation map. This H0 proposal awaits explicit approval and
does not extend the standing ADB allowlist.

## Same-board preservation and verification

The working device's recovery gate remains unsatisfied. Before consequential
experiments, establish surviving entry, accepted repair execution, exact layout
and boot-region configuration, both applicable image/AVB sets, version/rollback
constraints and preservation of calibration/provisioning. User-area/boot-region
dumps do not replay authenticated RPMB or recreate SoC-bound keys/fuses. A second
board reduces exposure; it cannot restore the original board's unique state.
Destruction of storage, unrecoverable provisioning, protection changes or loss
of every accepted repair entry can defeat same-board restoration. No such
failure was caused or experimentally tested here.

New public tools: `inspect_qcom_elf.py` (32 MiB, 128 program headers, MBN v6 only,
explicit unsupported layouts, no signature-trust claim) and
`inspect_gpt_capture.py` (8 MiB, bounded entries, explicit capture offsets,
CRCs plus geometry, no restore claim). Both read ordinary files only and never
open a player or apply patches. Synthetic tests include modified code/header,
signature/hash separation, truncation/oversize/unsupported formats, CRC-valid
bad geometry, overlap and capture-origin errors. Private reference checks,
test output and prior-evidence preservation results accompany the artifacts.

Actual final verification: **155 tests ran: 154 passed and one existing
Windows symlink-permission test skipped**. This includes 23 new parser tests.
**25 reference/provenance/preservation checks passed, zero failed**; 1,374
prior private ledger-covered files matched their recorded sizes and hashes.
The three ELF CLIs returned 0; the two GPT CLIs returned the expected 1 for
invalid template geometry. A private validation helper initially assumed a
fixed PE-header offset; that failed check is preserved and the helper now reads
the DOS header's actual PE offset (3,672). This was a check defect, not a changed
image or an architecture conflict. Public document links/whitespace and
`git diff --check` passed. No physical firmware behavior was tested.

Reproduction entry points, against supplied ordinary files only:

```text
python -m unittest discover -s tests -v
python tools/inspect_qcom_elf.py supplied-loader.elf
python tools/inspect_gpt_capture.py supplied-primary-gpt.bin --header-offset 512 --array-offset 1024
```

Offsets in the example are the inspected reference primary fragment's offsets;
they are not assumed Sony capture geometry. A 0 exit from the ELF inspector
means the supported structural checks did not fail; inspect the explicit
unsupported-layout and signature-verification fields before interpreting it.
Neither command establishes signer trust or restoration capability.

The next required resource is an authentic Sony loader bundle or the separately
approved research-board access above. Additional wrapper analysis, generic ADB
infrastructure and virtual playback work do not answer that dependency. This
increment narrows acquisition and prepares actual loader analysis; it does not
establish an unlock, accepted Linux payload or same-board recovery.
