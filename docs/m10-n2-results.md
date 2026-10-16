# M10 N2: bootloader endpoint confirmed, stock Android return verified

2026-10-15. The owner authorized the fixed [N2 scope](m10-n2-authorization.md)
and supplied fresh readiness and FastBoot-screen confirmations. N2 completed
with **`is-userspace: no`**. Classify this as **reported bootloader fastboot**,
demonstrated on the physical NW-A306 through the guarded protocol observation.
After the approved physical-return instruction, the owner reported it was back
on; all eleven conditional Android identity checks passed. Independent Linux
execution and same-board firmware restoration remain unproved. M10 remains open.

## Exact physical result

The trusted existing ADB server, host binaries, unique USB unit, physical port,
original identity profile and frozen code/plan were checked. All eleven initial
Android identities passed. Exactly one bound `reboot:bootloader` request was
acknowledged; same-port USB re-enumeration met the 30-second limit. The owner
confirmed the same unit's FastBoot Mode/product screen before native queries.
No new screen photograph was acquired in N2.

| Native invocation, actual order | Actual result | stdout / stderr bytes | Exit |
| --- | --- | --- | --- |
| `fastboot devices -l` | One target matching the private approved serial | 33 / 0 | 0 |
| `fastboot -s S getvar product` | `product: icx1301` | 0 / 48 | 0 |
| `fastboot -s S getvar is-userspace` | `is-userspace: no` | 0 / 48 | 0 |

`S` denotes the private serial. The last complete stderr was exactly:

```text
is-userspace: no
Finished. Total time: 0.002s
```

Both lines ended in CRLF. Product stderr likewise ended with
`Finished. Total time: 0.002s`. There was no retry, extra diagnostic, software
reboot, image transfer, unlock, flash, erase or slot-change request.

The owner was instructed to use the approved single Power-only hold and then
reported return. Actual hold duration was not measured. Conditional rediscovery
and eleven identity guards completed at approximately **204.714 seconds** from
session start, within 450 seconds. They matched the same original unit, stock
build, slot `_b`, green boot state and locked state. Ephemeral transport IDs were
rebound only inside the private session; the original expected profile bytes
were preserved. These checks establish return to the expected Android identity,
not comprehensive peripheral health or recovery after firmware corruption.

AOSP [defines `is-userspace`](https://source.android.com/docs/core/architecture/bootloader/fastbootd#fastboot_commands)
as the endpoint discriminator. Sony's explicit `no` supports the bootloader
classification; it is not binary identification or cryptographic attestation.
Preserve [N1's unavailable version and original stop](m10-n1-results.md): no
version query was repeated and no loader malfunction is inferred.

## Next acceptance investigation: the actual Sony temporary-boot path

**Decision:** prioritize Sony's early-loader command dispatcher and temporary
image authentication path. Further informational getvars and recovery fastbootd
characterization are not the next investigation. Enumeration and an endpoint
flag do not prove that `boot` is registered or accepts a changed payload.

The concrete targets are the actual command registration/build flags, any
locked-state gate before parsing, authenticated coverage of supplied kernel,
ramdisk/DT/command line, delegated trust checks, and boot-control writes before
handoff. Loader bytes are useful for this investigation; a full dump of every
loader stage is not an intrinsic prerequisite if equivalent authentic policy
evidence can be obtained. Such Sony evidence is still missing.

Focused offline comparison now supplies a more precise reason to inspect that
path before proposing a payload experiment:

- **Historical Qualcomm source, not Sony:** commit
  `7cbbe2bcdf354c1a65712b040b2c0763f26f08f1` of the preserved Code Aurora ABL
  tree conditionally registers `boot` under `ENABLE_BOOT_CMD`.
  [`FastbootCmds.c:1879–1962,2428–2430`](https://gitlab.com/Codeaurora/abl_tianocore_edk2/-/blob/7cbbe2bcdf354c1a65712b040b2c0763f26f08f1/QcomModulePkg/Library/FastbootLib/FastbootCmds.c#L1879)
  validates image size/header, then calls `ClearUnbootable()` before
  `LoadImageAndAuth()`. No direct `IsUnlocked()` gate occurs in this historical
  handler. This does not establish acceptance on Sony or the acquired RB1 build.
- **Historical storage implementation:**
  [`PartitionTableUpdate.c:174–334,1267–1285`](https://gitlab.com/Codeaurora/abl_tianocore_edk2/-/blob/7cbbe2bcdf354c1a65712b040b2c0763f26f08f1/QcomModulePkg/Library/BootLib/PartitionTableUpdate.c#L1267)
  clears the active boot entry's unbootable bit. If attributes differ, the update
  path recalculates checksums and writes primary and backup GPT blocks; unchanged
  entries skip writing. Thus an authentication failure can follow a persistent
  change in this implementation. This is not a finding that N2 changed GPT.
- **Historical authentication implementation:**
  [`VerifiedBoot.c:284–375,562–664`](https://gitlab.com/Codeaurora/abl_tianocore_edk2/-/blob/7cbbe2bcdf354c1a65712b040b2c0763f26f08f1/QcomModulePkg/Library/avb/VerifiedBoot.c#L284)
  selects verification behavior using device unlock state. Its preloaded-image
  branch excludes `boot` from the requested partition list before AVB verification.
  Merely finding an authentication call does not prove which supplied bytes it
  covers; the actual Sony path and delegated operations must be traced.
- **Separate acquired RB1 binary:** the previously verified LinuxLoader contains
  a locked-device temporary-boot rejection diagnostic at file offset `0x3eb28`.
  A bounded check confirmed the original binary hash and locator. A string is
  not a traced branch, and the historical source lacks that diagnostic/gate.
  Do not treat the two as build-matched or transplant either policy to Sony.

Four selected source files were preserved privately and verified against the
immutable historical commit. The closer RB1 release source URL still returned
HTTP 429; no source/build match is claimed. No firmware code was executed.

The next substantive action is to obtain authentic Sony early-loader/boot-policy
evidence and trace these specific branches, using the acquired reference binary
only as a comparison. The current encrypted Sony update package and updater APK
do not expose that handler. No authorized ordinary read has yet supplied it.
Do not infer infeasibility from this missing input, or reopen wrapper analysis
without a new artifact-specific hypothesis.

There is **no justified image experiment ready for execution**. Before one can
be proposed, establish Sony command support/locked-state policy, an applicable
image/DT/authentication relationship and recovery covering possible boot-state
writes. Even a stock signed image may fail a separate locked-state command gate;
changing only a ramdisk is not demonstrated to escape authentication. A header
or empty-image probe is not established to be harmless. No further physical
operation is authorized by this result.

## Implementation, preservation and checks

- `tools/fastboot_n2.py`: fixed live N2 phases reusing frozen N1 transport/capture;
  fresh owner prerequisites, hash admission, same-unit current transport binding,
  exact three native commands, optional-response interpretation and conditional
  return verification. Default invocation prints a plan without communicating.
- `tests/test_fastboot_n2.py`: seventeen integration tests cover approval/identity,
  host/readiness failures, exact schedule, yes/no/empty/unsupported responses,
  captured-response integrity, deadlines and return guards using injected fakes.
- `docs/m10-n2-authorization.md`: execution-integration/status annotations; no
  change to approved commands, bounds or return conditions.
- `docs/m10-boot-feasibility.md`: current N2 outcome/decision above dated history.
- `docs/m10-n2-results.md`: this report.

The full suite ran **207 tests: 206 passed, one existing Windows symlink skip**.
All seventeen new integration tests passed. Saved-capture checks verified
**292 stream files**, sizes/hashes, decoded identity bytes, exact native scope,
one entry request, host/plan/profile binding and conditional return. The pre/post
wire captures contain 62/59 connections and **23,354 total bytes**; native
invocations took approximately 67–72 ms each. All limits passed. **1,901 prior
files** remained hash-preserved, with original bytes retained for intentionally
edited documentation. Twelve saved-source/locator/order checks passed. These
source checks do not compile firmware or prove Sony runtime behavior.

Raw evidence and manifests remain in ignored `build/m10/device-n2-20261015-01/`;
integration, host snapshots, consent/readiness, validation and preservation
records are in ignored `build/m10/n2-integration-20261015-01/`. New source research
and its provenance are in ignored `build/m10/n2-boot-policy-20261015-01/`.
Private serials, transport IDs and raw inventories are excluded from this report.
Earlier N1 and denied-operation records remain unchanged. No Git history changed.
