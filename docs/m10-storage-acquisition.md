# M10 storage acquisition: optical evidence to loader bytes

2026-10-15. Offline increment; no player communication, power application,
probing, teardown or boot-mode operation. No research board has been supplied
in the available evidence. The primary player is excluded from this proposal.
Existing evidence and uncommitted files are preserved. M10 remains open.

## Findings that change the acquisition procedure

1. **Verified from certification-sample artifacts:** U2's base marking is
   Samsung `KLMBG2JETD`; the full suffix remains unresolved. The board reads
   `SODAGREEN M/B REV:1.03`. Neither identifies the owner's production revision.
   No motherboard net or pad-to-ball connection is verified.
2. **Verified in the reference artifacts, not Sony:** six XBL/ABL a/b/r spans
   agree between `rawprogram0.xml` and the GPT entries in hardware region 0.
   The reference maps these loaders alongside GPT partitions, not exclusively
   into hardware boot1/boot2. Acquisition must inspect actual Sony layout and
   hardware configuration rather than assume that dumping boot regions finds
   every loader. The reference GPT remains an invalid installation template.
3. **Verified from Sony published source, not a running command trace:**
   switching hardware partitions uses `CMD6` and updates `PARTITION_CONFIG`.
   Reading storage is not necessarily a command sequence with no card-state
   changes. Reader initialization, switches and automatic repair/configuration
   must be reviewed before authorizing a capture.

The highest-value unresolved question is **whether a production research board
provides identifiable, electrically isolatable access to U2**. H0 resolves the
optical prerequisites only. eMMC remains the strongest investigated route to
loader *bytes* independent of Android and NWWM; it is not demonstrated viable.
Passive UART could provide behavior with less invasive connections after net
identification, but does not promise a loader dump or command console.

## Source-bound map and package documentation

Private `build/m10/storage-access-20261015-01/board-map.html` overlays unchanged
M7 photo files. `board-map.json` binds each region to a PDF page, image/PDF
SHA-256, approximate normalized rectangle, observation and separate confidence
in interface applicability. It contains **two views, eight regions, zero
assigned signal nets**. View A is the preserved Part 10 p. 1 rendering; view B
is Part 8 p. 2. There is no established cross-face registration. Original
photos and derived map/previews remain ignored, not public assets.

| Map ID / exact source | Observation and confidence | Interface claim / required proof |
| --- | --- | --- |
| A1, Part 10 p. 1, U2 | High for base marking; suffix unknown | Storage component target. Exact suffix, A1 index, dimensions and package must agree before using a ball map. No visible ball-to-pad connection. |
| A2, same, U1 | High for QCS2290 identification | Controller isolation/reset/high-impedance behavior unknown. SoC reset alone is not proof the bus is isolated. |
| A3, same, U4 | High for PM4125 marking | No U2 supply rail, regulator output or decoupling net identified. |
| A4, same, routing beside U1 | High for visible routing/vias | No complete CLK/CMD/DAT0 route follows through the multilayer PCB. No net names assigned. |
| A5, same, U2403 | High for package location | Function unknown; not an established debug device. |
| B1, Part 8 p. 2, staggered round pads beside connector | High for exposed pads; low/unverified as acquisition interface | Candidate net-survey area only. No eMMC/UART/JTAG/SWD/EDL assignment. |
| B2, same, revision text | High for certification-board revision | Production/donor equivalence unknown; record actual revision and component population. |
| B3, same, board-to-board connector | High for physical landmark | Connector pin functions unknown. Used for orientation, not a storage connector claim. |

Part 6 pp. 1-2 supplies full-board orientation and the assembled shield view;
Part 10 shows components with the shield removed. Do not interpret that as a
non-destructive access procedure. No new production photograph establishes a
revision difference or equivalence. The schematic remains unavailable; see
[M7 exact evidence and conflicts](m7-fcc-evidence.md).

**Conditional package reference, not wiring instructions:** the Samsung-authored
[B041 datasheet](https://www.ftcelectronics.com/datasheets-e4/klmbg2jetd-b041.pdf),
Rev. 1.0, PDF pp. 4-6, describes KLMBG2JETD-B041 as 32 GB eMMC 5.1 in a
153-ball, 11.5 x 13 x 0.8 mm package, 0.5 mm pitch. Table 2 gives DAT0=A3,
CMD=M5, CLK=M6, RST_n=K5, strobe=H5, VDDI=C2 and VSS including J5. It specifies
VCC 2.7-3.6 V and VCCQ 1.70-1.95 V or 2.7-3.6 V. VDDI is an internal regulator
node, not a proposed supply input; RFU balls are not usable connections. The
figure is ball-side down: photo orientation alone cannot transfer ball positions
to PCB pads. These facts describe a candidate suffix, not selected Sony rails.

This marked-confidential document was obtained from a public third-party mirror
and is preserved privately, SHA-256
`f9d8f6f855ee15df6748a388a5287ac8306ab06d250673ace45067d52d9058ca`.
It is not an authenticated manufacturer download or permission to redistribute.
The [Samsung-authored product brief](https://www.avnet.com/fsp/opasdata/d120001/medias/docus/190/SAM-KLM8G1GETF-B041-Datasheet.pdf)
already preserved in M8 corroborates identity/dimensions; the [programmer
manufacturer's listing](https://www.elnec.com/en/device/Samsung/KLMBG2JETD-B041%20%5BFBGA153%5D/)
independently lists the B041/FBGA153 variant. Its generic part-number voltage
table warns of inaccuracies and is not adopted as an electrical specification.
The [TI-hosted Samsung Rev. 1.1 attachment](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/Samsung-eMMC_2D00_2611204514.pdf)
was readable through the research service but direct acquisition returned 403;
no local bytes or equivalence hash is claimed. Revision/page counts differ.
Micron's ISP/design/partition notes were located, but their links require
sign-in/NDA; their unseen contents are not evidence. No account or agreement
was created. No source document or pin-map figure is copied into public Git.

## Storage acquisition requirements

| Object | What an approved capture might preserve | What it cannot establish |
| --- | --- | --- |
| User-area GPT and partition extents | Actual primary/backup headers, arrays, fixed/dynamic metadata and complete authorized partition bytes | Sony early-loader names/offsets before capture; successful reconstruction or image acceptance |
| Hardware boot1/boot2, GP areas | Separate original regions if present, selectable and accessible | Android A/B equivalence, actual ROM boot source, or all executable stages |
| CID/CSD/EXT_CSD | Identity, capacities, selected area, configuration/protection observations | Immutable SoC trust, signing authority or every protection state |
| RPMB / secure-storage / provisioning | Preserve in place; only separately scoped metadata if justified later | Plain sector cloning, replay of counters/authenticated writes, retrieval of keys or a decoded Sony secure-storage database |
| ROM, SoC-bound state and eMMC internal controller | None through an ordinary logical eMMC sector dump | ROM code, OTP/fuses, SoC-bound keys, raw NAND/FTL state or internal controller firmware |

User/boot-region read access is a hypothesis until the exact chip and response
are established. File encryption or stored-container encryption may remain;
physical access does not imply plaintext. Card protection and host security are
different boundaries. Host read-only behavior also does not prove all internal
managed-storage state stays unchanged.

**Published Sony source:** archive
`.local-references/sony-gpl-source/3.06.00-20260716/gpl_source.tgz`, member
`kernel/msm-4.19/drivers/mmc/core/block.c`, SHA-256
`94e3142a0735713aa7d768213c7fc4d3be0ca5eefe307c01ce9150072b71038a`,
`mmc_blk_part_switch:885-921` clears only the access mask, retains the other
configuration bits and issues `mmc_switch` for `EXT_CSD_PART_CONFIG`.
`include/linux/mmc/mmc.h` defines `MMC_SWITCH` as 6. Previously preserved
`mmc.c:2087-2146` enables reset-lost ERASE_GRP_DEF and restores user-area access
during initialization. This demonstrates potential command side effects in
published code; it does not select a future reader's behavior or authorize it.
Linux `force_ro` is not a substitute for reviewing the acquisition command trace.
Any future approval must distinguish sector reads from explicitly permitted
runtime switches. A partition-access switch must preserve bits outside the
`0x07` access mask; an indiscriminate full-byte write can change boot selection
or acknowledgment settings. No such switch is authorized by this document.

**Electrical topology:** an eMMC read requires the chip to be powered. An
unpowered whole board cannot simply be read through clips. Supplying U2 while
the SoC is off can back-power the SoC/PMIC through shared rails or I/O clamps.
Powering the board normally can produce dual-host CLK/CMD/DAT contention and
background writes. Holding a reset line is insufficient without verified
high-impedance behavior. An ISP plan needs a demonstrated power/IO isolation
boundary; socketed chip-off removes controller contention but introduces major
rework risk. Neither is an approved connection here.

Minimum future net set is verified GND, VCC, VCCQ, CMD, CLK and DAT0; reset and
other host-connected signals must also have known handling. A low-speed,
single-data-line reader may reduce wiring, but it still needs eMMC protocol,
correct pull-ups/levels, initialization, reliable busy/error handling and
explicit hardware-area support. A generic SD adapter or 3.3-V interface is not
qualified. No current/voltage setpoint, reset polarity or ground-pad assignment
is selected from the photographs.

An acquisition should start with approved identity/configuration, actual
addressing/sector size and bounded layout reads. Then bind explicit hardware
area, LBA span and byte count to each file; do not trim partition padding or
substitute firmware-member size for partition size. Retain raw bytes plus
reader version/settings and command/error logs. Two separately scheduled reads
of each approved span, made while the Sony host is isolated, must agree in size
and SHA-256, with chunk hashes locating disagreements. A mismatch stops analysis;
it does not trigger retries, majority voting or a repaired image. Agreement
establishes repeatability of that span, not completeness or authenticity.
Failure of the first scheduled read stops before the second is attempted.
Existing EXT_CSD/GPT/ELF inspectors can check supplied captures. No full userdata
dump, RPMB transaction, configuration write or guessed sector read is proposed.

The RB1 analysis checked six XBL/ABL spans and image fit using the existing
ELF/MBN and GPT inspectors plus bounded XML parsing. Six altered label/offset/size/region/layout
controls were rejected. For example, the reference XBL allocation exceeds its
ELF member by 502,272 bytes: a deployable member is not a byte-for-byte backup of
the entire partition. No reference offset is proposed for Sony acquisition.

## H0: exact optical characterization proposal

**Prerequisite:** a separately supplied genuine NW-A306 board, already exposed,
USB and battery disconnected by its supplier/qualified handler, supported on
an ESD-safe fixture. Availability, power isolation, provenance and permission
must be confirmed before starting. Do not substitute the working player,
A307/ZX707/A100 board or an unidentified board. Prefer an original, non-corroded
board with known stock history and intact storage. Occluded components are
acceptable negative evidence. This scope does not authorize opening an intact
donor, disconnecting soldered battery leads or removing shields.

**Question:** does a retail board expose the B1 region without rework, and can
its revision and storage package be identified for a later isolation/net study?

**Handling:** ESD bench, appropriate grounded handling/fixture, no contact with
component leads, pads or connector contacts. Support board edges without flexing
or crushing parts. Use diffuse visible light and a second oblique light angle
for markings; avoid glare and heat. No cleaning, scraping, adhesives, shield
movement or flex manipulation to expose hidden parts.

**Orientation:** photograph with USB-C/microSD end north. Call the storage/shield
face A and connector/revision face B, documenting these definitions. Photograph
the flip around the board's long axis with north unchanged. Record at least
three shared physical landmarks (mounting holes, edge notch, USB end), plus a
scale in the board plane. Do not infer mirrored net locations before registering
same-board landmarks. Retain original camera orientation/metadata and record
any derived rotation separately.

**Fixed shot list, original files, at most 20 photos of at most 25 MiB each
(500 MiB total):**

1. Face A full overview with scale and private board label.
2. Face B full overview with the same north direction and scale.
3. Edge/landmark view documenting the flip and asymmetric outline.
4. Revision text, perpendicular, including surrounding silkscreen.
5. B1 pad cluster with connector and nearby mounting holes in frame.
6. B1 close-up from a second lighting angle.
7. U2 package and orientation index if already exposed; otherwise its occlusion.
8. U2 marking at second lighting angle if exposed; otherwise shield boundaries.
9. Accessible U2 perimeter/passives and vias, without moving anything.
10. U1/U4 area and any existing repair/corrosion affecting an access plan.

Use macro imaging or nominal 10-30x optical microscopy for close-ups where
available. Acceptance is actual resolution: the smallest relevant marking glyph
should be at least 20 native pixels high where legible, with focused pad edges.
Allow up to ten exposure/focus alternatives within the total cap, never AI
enhancement or inferred text. Failure to read a suffix is recorded as unresolved.

Store originals privately with UTC time, shot ID, face/orientation, lighting,
source/board provenance and SHA-256. Serial/QR data remain private. Compare
mechanical outline, mounting holes, connector placement, pad pattern, revision,
package markings and component population against FCC Parts 6/8/10. Report
matches, differences and occlusions separately; resemblance is not continuity.

**Stop before handling** if authorization, identity or power isolation is
uncertain, exposed battery damage exists, or a qualified ESD-safe setup is absent.
Stop if a requested view requires force, electrical contact, disassembly,
shield removal or rework. No improvised substitute. **Risk:** low relative to
probing/rework, but ESD and mechanical damage are possible. No intended software
state change; no storage is read. **Expected value:** a revision-bound accessible
feature map and package candidate, or explicit negative evidence that changes
the electrical-access design. H0 does not establish a recovery capability.

## Progression after H0, each separately authorized

| Potential experiment | Required proof / equipment and limits | Observation and rejection; state, damage and controls |
| --- | --- | --- |
| E1: unpowered net/rail identification | H0 map, exact suffix/index and reliable package data; qualified low-energy measurement plan, meter specifications, microscope and insulated microprobes. Test voltage/current must be below documented limits for every connected component; numeric limits are not known yet, so no test is ready. Continuity mode injects current. | Establish ground/supply/signal correspondence to known endpoints, not just a beep to a plane. No flash writes intended; injection/shorts/ESD can damage parts. No probing until limits and endpoints are justified. Failure to find safe endpoints rejects that setup, not all ISP. |
| E2: passive activity / UART hypothesis | E1 ground/Vref and safe pad identities; high-impedance scope/qualified level-compatible capture, no transmitter. Any powered run needs its own stock boot and shutdown plan; stock can write state. | Capture voltage/timing before decoding. Correlated CLK/CMD/DAT activity may support storage-net identity; repeated asynchronous serial could support UART. Silence does not prove absence. Probe loading, shorts and wrong ground can damage or disrupt boot. No driving/resetting unknown pads. |
| E3: isolated eMMC identity and layout capture | Verified rails/nets, actual controller-isolation boundary and qualification on a spare equivalent chip; current-limited independent supplies, eMMC-capable reader and audited initialization. Measured board levels must match part limits before numeric setpoints are approved. | CID/CSD/EXT_CSD and bounded GPT regions, with predefined reads and logs. Reject unexpected identity, errors, back-powering or active Sony-host drive. No persistent write intended, but reviewed runtime CMD6/state changes may be necessary and need explicit scope. No auto-detect write/repair, high-speed training assumptions, voltage injection into VDDI or automatic retries. |
| E4: original loader-span acquisition | E3 actual geometry and identified candidate partitions/regions; fixed span/size plan and separately scheduled duplicate reads | Require agreement and original-byte preservation; run existing inspectors without executing code. Stop on mismatch/denial. Could preserve original authorized regions, not ROM/RPMB keys or all unique state. No boot/flash follows automatically. |
| Chip-off / direct BGA socket fallback | ISP demonstrably lacks a safe accessible isolation path; exact socket/pin orientation, rework profile and expendable research board, qualified BGA facility | Eliminates shared-host wiring but can irreversibly destroy package/PCB. Requires separate destructive-risk approval and prior preservation where possible. Readout still needs audited reader commands; no assumption it reconstructs the primary board. |

No electrical procedure is presently ready for execution: package suffix,
board rails, net map, isolation and instrument limits are missing. H0 can reduce
some of these unknowns without pretending to resolve the rest.

## Alternatives, execution and recovery

| Route | Priority / actual missing discriminator | Qualitative difficulty, risk and rejection |
| --- | --- | --- |
| Supplied build-bound Sony images or independently available decoded stock bundle | Lowest physical risk; none currently verified available. Inspect immediately if provenance-bound artifacts are supplied. | Low handling cost, variable availability. Reject wrong build/board or altered bytes as evidence of the running loader; do not conclude all acquisition impossible. |
| Passive UART | After H0/E1, potentially cheapest behavioral evidence | Moderate net-identification work; lower risk than active storage driving, still powered-probe risk. No enabled UART established; log-only access may never yield binaries. |
| Early-loader/recovery metadata | Separate approved entry/return needed; actual Sony handler/build is the discriminator | Low extra equipment, unresolved availability/state risk. Userspace fastbootd is not early-loader execution. An absent handler rejects that command route, not physical acquisition. |
| Authenticated diagnostic/Sahara programmer | Need actual Sony trust/initialization match and command rights | High applicability uncertainty. No known accepted Sony programmer. RB1 image and 9008 visibility are insufficient; mismatched trust/DDR rejects that image. No upload proposed. |
| Build-specific software or debug research | Authentic Sony loader or a concrete reachable source-matched interface | High analysis effort, no applicable weakness established. JTAG requires identified nets and permissive debug policy; public precedent is not proof. Offline analysis continues when actual code arrives. |

Independent Linux still requires control at the **OS-image acceptance stage**,
not merely storage access. In the reference this is a LinuxLoader-bearing ABL;
the actual Sony component/name and policy are unknown. After acquisition, trace
its handler registration, lock checks, trusted-key selection, verified ranges,
DT/ramdisk selection, rollback/slot writes, and the verification-to-handoff path.
Then distinguish a supported temporary load from a supported trust transition
or a concrete security flaw. A signed vendor kernel with modified init is not
automatically accepted. No custom image or exploit is proposed today.

Before a primary-device boot experiment, restoration must cover exact original
GPT/boot-region configuration and applicable early loaders, both boot/AVB sets,
dynamic metadata, version/rollback rules and calibration/provisioning, plus an
accepted repair entry surviving the intended failure. Keep RPMB and SoC-bound
state intact; raw copies cannot rewind authenticated counters or recreate keys.
An acquisition from a donor preserves that donor, not the primary board's unique
state. A/B and reference rescue packages do not satisfy same-board recovery.
Even temporary execution can change counters, storage or power/watchdog state.

This increment produced the private annotated map and reproducible storage-span
analysis, acquired a conditional package reference, and prepared H0. It did not
repeat signature verification or change transport infrastructure. Final checks
and complete new private file inventory are in this increment's ignored ledger.
**26 focused offline checks passed, zero failed**, including six rejected
reference-manifest mutations, source locators, map/source integrity and document
checks. **1,430 prior ledger-covered files matched**, including prior private
evidence and six public files from the preceding increment. Browser rendering
loaded both 3024 x 4032 originals, passed overlay-toggle verification and was
visually reviewed. The unchanged full unit suite's prior result remains 154
passes and one Windows symlink-permission skip; it was not rerun or represented
as a new result. No Sony loader bytes or new physical evidence were acquired.
The next resource is a genuine separately exposed NW-A306 research board with
documented provenance/power isolation, followed by explicit H0 approval. An
assembled donor needs a separate teardown plan before it meets that condition.
