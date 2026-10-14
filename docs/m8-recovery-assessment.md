# M8 original-board restoration assessment

2026-10-14. No original-board restore interface is verified. The applicable
published US service evidence remains Sony's 2024-06-15 two-page manual,
**product exchange on p. 2**, SHA-256
`a8a0381fbcff9539b16ba98b8615bf5d10b5e10a8544279db3ae09167a77359f`.
[Sony-authored manual, Encompass mirror](https://research.encompass.com/SON/rr/NWA306_B.pdf).
It does not exclude an internal capability or establish another region's policy.
No inquiry was sent and no physical recovery experiment occurred.

## New storage implications

The [M8 model](m8-boot-storage-architecture.md) separates user area, hardware boot
regions, boot-selection/protection configuration and RPMB. A restoration scope
must enumerate each **actually used** object; a user-area partition collection
alone cannot demonstrate full reconstruction. Which hardware boot region Sony
uses, if any, remains unresolved. The new EXT_CSD reader cannot determine that
from synthetic inputs and cannot acquire a real capture.

`PARTITION_CONFIG` access and boot enable differ. A/B slot recovery does not
restore eMMC boot configuration. Power-on versus permanent boot protection,
boot-configuration protection and reliable-write semantics have different
consequences. Linux software `force_ro` is another boundary, not an authentication
policy. RPMB transactions use authentication and counters; the actual Sony
contents/uses are U. Restoring old bytes is not proof of acceptable replay,
rollback or device-bound trust state. No key or protected provisioning was sought.

## Failure-state dependency matrix

S/H/P/I/U classifications follow the boot/storage report. **All proposed Sony
interfaces below are U** unless stated otherwise. An earliest possible survivor
is a dependency hypothesis, not an available restoration facility.

| Failure state | Earliest candidate survivor and dependencies | Images / authorization / unique-state requirements | Actual documented capability and original-board outcome / success criterion |
| --- | --- | --- | --- |
| Android unusable, recovery intact | I: independently reachable recovery kernel/userspace; needs its loader, DT, storage and power support | Matching accepted reinstall package, variant/version rules, repaired partition list; preserve required provisioned/calibrated areas | S: normal update and formatting instructions, no applicable unbootable reinstall proof. U: original-board restore. Success would require authentic Android boot, accepted security state and functional hardware/data preservation checks |
| Both Android boot slots unusable | I: recovery or lower loader independent of the failed images; separate recovery names alone prove no independence | Genuine boot/DT/AVB set, selected slot/fallback metadata and supported access; no borrowing another unit's protected state | S: historical A/B names only. U: surviving entry and restore. Success needs both intended slots/policy validated and repeated stock startup without a shared-metadata dependency failure |
| Recovery or AVB metadata damaged | I: authorized lower loader/service entry not dependent on recovery userspace or damaged trust metadata | Accepted recovery/kernel/DT/vbmeta chain and rollback-compatible versions, exact authenticated repair rights | U: loader entry/repair facility. Fastbootd may require recovery and does not establish survival. Success needs complete authentic verification chain and recovery entry after stock restoration |
| GPT or dynamic metadata corrupted | I: partition-independent authorized service execution; GPT and super damage are different scopes | Authentic layout and image manifest, accepted tools, eMMC region/protection handling, known exclusions and preserved unique data | U: partition-independent entry/programmer. OTA existence is insufficient. Success requires valid matching map/metadata, all necessary images and unchanged provisioning on the same storage/board |
| Early authenticated loader failure | P: immutable ROM remains conceptually distinct; U: accessible Sony-approved service route and PMIC/memory prerequisites | Sony-accepted programmer/stages matching board/security identity, authentication credentials/access rights and rollback rules | No applicable ROM/service entry or programmer documented. Generic Qualcomm EDL and another board's loader do not establish acceptance. Success would need authentic restored chain and unchanged original motherboard/storage/security binding |
| Device-specific provisioning/calibration corruption | I: preservation or documented authorized regeneration service, only where supported | Exact replaceable versus device-bound classification; lawful preservation rights; firmware/calibration versions and protected-state continuity | U: backup/regeneration process and RPMB ownership. Exchange does not satisfy original-board restoration. Success includes Sony-defined calibration/safety checks and preserved/regenerated authentic identity-bound state, not only Android boot |

No row has demonstrated failure coverage. A matching spare can help future
validation but supplies neither accepted images nor a restoration method. A
replacement motherboard or product exchange fails the original-board criterion.
No generic programmer, pad marking, tool download or protocol presence was
promoted into evidence of a usable NW-A306 recovery interface.

## Restoration evidence contract

Before proposing a low-risk physical experiment, assemble a coherent proof set:

1. **Applicability:** model/region/build, board/storage revision and security
   policy match; artifact origin, version, hashes and permitted use recorded.
2. **Survival graph:** exact entry stage and every prerequisite it needs;
   explicitly exclude failure states that destroy a prerequisite. Include power,
   memory setup, partition discovery and authentication dependencies.
3. **Accepted reconstruction set:** complete image/layout/tool manifest for the
   covered scope, accepted signer/credentials, rollback compatibility and
   partition/configuration exclusions. A transport MD5 or opaque NWWM file is
   insufficient to inventory these dependencies.
4. **Original state:** define unique calibration/provisioning and protected
   counters/keys, what survives, what may legitimately be regenerated, and
   what cannot be copied between units. Do not publish their contents.
5. **Objective outcome:** original board and storage retained; authentic stock
   boot/security and recovery restored; storage/audio/display/input/charging/
   thermal/shutdown checks appropriate to the repaired scope; no silent loss
   of unique state. Criteria must come from applicable documentation and a
   separately approved validation plan, not guessed electrical thresholds.
6. **Experiment scope:** separately explicit contact/device authorization and
   evidence adequate for that exact operation. An apparently temporary boot
   can still alter counters, storage or power state; lack of a write command
   does not establish harmlessness.

This is a review contract, not a flashing procedure or an automated permission
grant. No test claims to prove physical recovery from these document requirements.
Host work can validate supplied image/header/descriptor/layout consistency and
dependency closure, but cannot verify device acceptance or same-board outcomes.

## Smallest useful next restoration evidence

Seek an applicable **original-board restoration capability statement** with
tool/artifact identifiers, supported failure states and provisioning treatment,
through a public service publication or lawfully supplied documentation. Pair
it with the selected image/layout bundle. If future contact is separately
authorized, the [existing concise Sony inquiry](m5-boot-recovery-paths.md#final-concise-sony-inquiry-unsent)
records these questions; it remains unsent.

Factory reset only resets permitted user state; routine update assumes working
prerequisites; authenticated service repair may be a different facility; exchange
changes the unit. None can substitute for evidence covering the intended failure.
Current evidence does not justify a hardware experiment, but host artifact and
kernel/userspace analysis can continue.
