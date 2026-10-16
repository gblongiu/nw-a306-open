# M10 P1: session-local transport binding and execution

2026-10-15. The owner explicitly authorized the P1 binding correction and one
metadata session, then confirmed the same player meets the operating prerequisites.
The preceding [preflight block](m10-p1-results.md) remains historical evidence.
This correction supersedes only its requirement to reuse an old transport ID.
It does not authorize another metadata command, content acquisition or mode change.

## Reviewed binding correction

The original approved profile and N2 post-return captures remain unchanged.
N2's old ID is **not** substituted. P1 now obtains the current ID from one fresh
`host:devices-l` result after checking the trusted existing server's version.
Require exactly one online transport, the original approved serial, the expected
`icx1301` inventory attribute and a valid nonzero ID. Confirm the healthy physical
USB root and expected connection through host-only Windows inventory, and require
`host:tport:usb` to select that same current ID. An absent/ambiguous/non-USB target
or mismatched serial stops before any Android command.

The ID is copied into a **session-local** profile; all original identity values,
serial, online state and device count stay fixed. A held `host:track-devices`
connection invalidates the session on any subsequent notification or disconnect.
Every observation retains before/after inventory/features guards and atomic
serial selection with returned-ID verification on the same connection as shell.
No later mismatch can trigger discovery, rebinding, reconnect or retry.

Eleven unprivileged Android identity checks must match the original profile
before the first metadata command. The manifest records the original profile
separately from the provisional current binding, then marks the binding identity
verified only after all eleven checks and their transport guards succeed.
The same eleven ending checks run only if both metadata observations succeed.
Server/host continuity and private capture validation remain required. These
guards bound identity/connection risk; they are not cryptographic attestation.

The only implementation changes are P1's pure profile-copy validator, P1-specific
initial inventory/routing in the existing adapter, plan policy and tests.
No socket, lifecycle, generic transport, retry or command-registry behavior was
expanded. Other stages retain their binding semantics; old code-bound approvals
are not silently regenerated. Previous source bytes were saved privately.

## Unchanged fixed operations, bounds and stops

After the initial identities, execute exactly:

```text
/system/bin/toybox ls -ldZ /dev/block/by-name
/system/bin/toybox ls -lZL /dev/block/by-name
```

The first requires successful exit, empty stderr and one exact ordinary-directory
record without a final symlink or ambiguous metadata. Only then may the second
run. The second requires successful exit, empty stderr and complete valid block
inode metadata. Existing parsers and their rejection conditions are unchanged.
No discovered name is followed by another command.

There are at most 24 shell observations. Identity/directory streams each retain
4,096 bytes; node-inventory streams retain 65,536 bytes. Every operation retains
five seconds. Session bounds remain 319,488 combined output bytes, 2 MiB wire
bytes and five minutes. Raw binary protocol/streams, exit status, timing and
hashes are saved privately, including failures. A failure stops the sequence;
ending identities do not run after a failed metadata operation.

No partition contents, secrets, privileged operations, updater invocation,
permission changes, reboot or persistent-state writes are authorized. Android
stays running. Unexpected responsiveness or connection behavior stops further
communication; no automatic recovery operation is allowed.

## Approval and evidence record

The fresh execution approval binds the revised plan/code hashes, immutable
original profile hash and a new private output directory. The current ID is
resolved inside that one session; it is not preselected from historical evidence.
Original scope and per-operation bounds match the preserved P1 proposal exactly.
Integrated plan SHA-256:
`7dc4b66670ac825d8ed575ff006f7592ef6d1f79e5e2be053d332a278abccf6c`.
The reviewed plan, test logs, host checks, approval and preservation ledger are
under `build/m10/p1-current-binding-20261015-01/`; physical capture uses the new
ignored `build/m10/device-p1-20261015-01/` directory. No evidence or identifier
belongs in public Git tracking. Actual execution findings are recorded below
after capture validation; authorization alone is not an execution result.

## Actual physical result

**Demonstrated on the physical NW-A306:** P1 completed all 24 observations,
including both metadata commands and eleven ending identity checks. All exits
were zero, stderr empty, payloads valid and transport guards successful. The
current transport ID differed from the original profile, was resolved once in
this session and stayed bound throughout. No historical ID was substituted.
The owner-confirmed original device/identities and healthy physical USB connection
matched. Host/server process, image and USB guards passed before and after.

Capture duration: **2.126 seconds**; 124 connections, **38,188 wire bytes** and
**9,635 combined stdout/stderr bytes**. Independent offline validation checked
296 raw/decoded stream files, exact request bytes, host responses, same-connection
selection, shell-v2 frames, exits, payloads, hashes, deadlines and operation order.
No follow-up device command ran after this session. No root, partition content,
permission change, reboot, unlock, flash or updater operation occurred.

The directory is an ordinary `drwxr-xr-x`, owned `root:root`, label
`u:object_r:block_device:s0`. The second command resolved **85 block-node entries**
through `ls -L`. This is an inode inventory, **not 85 verified GPT partitions**:
it includes an entry named `mmcblk0`. It supplies major/minor numbers, not symlink
target path strings, partition capacities, LBAs, image formats or contents.
Displayed inode timestamps do not establish firmware build dates.

### Observed boot/recovery candidate metadata

Every node in this table was `brw-------` (`0600`), owned `root:root`.
Labels are shown without their common `u:object_r:` prefix and `:s0` suffix.
The role column is an investigation hypothesis based on names/labels, not
verified image contents or an established Sony execution path.

| Actual names | Resolved major:minor, in listed order | Label type | Candidate role / limit |
| --- | --- | --- | --- |
| `abl_a`, `abl_b` | `179:28`, `179:29` | `vendor_custom_ab_block_device` | First targets for authentic ABL/fastboot-policy acquisition; executable contents remain unread. |
| `xbl_a`, `xbl_b` | `179:1`, `179:2` | `vendor_xbl_block_device` | Earlier loader candidates; trust configuration and selected bytes unknown. |
| `xbl_config_a`, `xbl_config_b` | `179:3`, `179:4` | `vendor_custom_ab_block_device` | Early-loader configuration candidates. |
| `boot_a`, `boot_b` | `179:11`, `179:12` | `boot_block_device` | Kernel/ramdisk candidates; header version, DT placement and authentication coverage unknown. |
| `dtbo_a`, `dtbo_b` | `259:2`, `259:3` | `vendor_custom_ab_block_device` | Overlay candidates; selected board overlay unknown. |
| `vbmeta_a`, `vbmeta_b` | `259:30`, `259:31` | `vendor_custom_ab_block_device` | Top-level AVB candidates; descriptors/keys unread. |
| `vbmeta_system_a`, `vbmeta_system_b` | `179:14`, `179:15` | `vendor_custom_ab_block_device` | Additional AVB metadata candidates; chaining unproved. |
| `recovery_a`, `recovery_b` | `179:16`, `179:17` | `recovery_block_device` | Actual recovery-named nodes; no demonstrated recovery entry, image policy or repair capability. |
| `imagefv_a`, `imagefv_b` | `259:4`, `259:5` | `vendor_custom_ab_block_device` | Firmware-volume candidates, contents unknown. |
| `multiimgoem_a`, `multiimgoem_b` | `259:33`, `259:34` | `vendor_custom_ab_block_device` | OEM aggregate-image candidates; no assumed authentication role. |
| `multiimgqti` | `259:35` | `block_device` | Aggregate-image lead, not a readback interface. |
| `uefisecapp_a`, `uefisecapp_b` | `259:6`, `259:7` | `vendor_uefi_block_device` | UEFI/security-component candidates. |
| `toolsfv`, `cateloader`, `catefv`, `catecontentfv` | `259:26`, `259:28`, `259:37`, `259:38` | `block_device` | Additional authentic node names for future artifact matching; no diagnostic access or owner execution inferred. |
| `uefivarstore`, `devinfo`, `logfs`, `logdump` | `259:39`, `259:20`, `259:27`, `259:29` | `block_device` except `logdump`: `vendor_logdump_partition` | Persistent-state/log candidates; not authorized readers or safe write targets. |

The complete observed name inventory is:

```text
SN abl_a abl_b apdp bluetooth_a bluetooth_b boot_a boot_b
catecontentfv catefv cateloader ddr devcfg_a devcfg_b devinfo dip
dsp_a dsp_b dtbo_a dtbo_b featenabler_a featenabler_b frp fsc fsg
hyp_a hyp_b imagefv_a imagefv_b keymaster_a keymaster_b keystore limits
logdump logfs mdtp_a mdtp_b mdtpsecapp_a mdtpsecapp_b metadata misc mmcblk0
modem_a modem_b modemst1 modemst2 multiimgoem_a multiimgoem_b multiimgqti
nvp oem_a oem_b opt1 opt2 opt3 ota persist qupfw_a qupfw_b rawdump
recovery_a recovery_b rpm_a rpm_b secdata splash spunvm ssd storsec super
toolsfv tz_a tz_b uefisecapp_a uefisecapp_b uefivarstore userdata
vbmeta_a vbmeta_b vbmeta_system_a vbmeta_system_b xbl_a xbl_b
xbl_config_a xbl_config_b
```

No `vendor_boot`, `init_boot` or standalone `dtb` entry appeared in this listing.
That does not prove those image structures/resources are absent elsewhere or
establish a particular Android boot-image ABI. No additional path was queried.

All nodes were `0600` root:root except `frp` (`0600` system:system) and `rawdump`
(`0660` root:system). None was world-readable. The approved shell reported uid
2000 and enforcing SELinux. For the loader candidates, ordinary DAC modes grant
no read permission to that shell; a direct read is not a useful next probe.
Effective access, extra capabilities/ACLs and SELinux authorization were not
tested, and no permission bypass is proposed. The two non-root-group exceptions
do not establish shell access or a route to ABL.

## Acquisition and execution consequence

The new evidence removes guessed partition names from the investigation.
`/dev/block/by-name/abl_b` is now a concrete first acquisition candidate aligned
with the repeatedly observed Android `_b` slot; `abl_a` is its comparison
candidate. Actual early-loader slot selection is still unverified. `boot`,
`recovery`, `dtbo` and AVB candidates now have device-specific names and inode
identities. None of their original bytes has been acquired.

**No demonstrated unprivileged loader-acquisition mechanism is available.**
P1 establishes the exact target and an ordinary-shell permission obstacle;
it does not justify an expected-denial raw read, more directory probes or
generic fastboot commands. The next useful acquisition requires one of:

- An authentic, build-applicable decoded Sony firmware payload containing ABL,
  from which original image bytes can be extracted offline. The preserved UPG
  remains opaque and its inner ABL coverage unproved; no repeated wrapper work
  or decoder/service invocation was performed in P1.
- A separately reviewed Sony-compatible readback/export capability that can
  lawfully read the observed ABL node without writing device state. Such a
  capability is not established. If obtaining it requires privilege escalation,
  mode transitions or other consequential operations, those need their own
  concrete risk assessment and explicit authorization.

For either route, the first real transfer proposal must bind the exact artifact,
reader authority, current device/build/slot, independently established length,
byte/time ceilings and private original-byte/hash provenance. Node metadata does
not provide the partition length. A newly acquired ABL would then be examined
with the existing ELF/MBN/PE tools for the actual Sony dispatcher, locked-state
branch, verifier and ordering of persistent effects. No raw acquisition is
automatically authorized by this result, and no currently available reader is
presented as working.

Temporary `boot` registration, locked-state rejection, accepted signatures/image
coverage and pre-authentication writes remain **unknown for Sony**. This result
materially improves artifact targeting; it does not establish independent Linux
acceptance. No additional informational fastboot cycle is recommended merely
to repeat known locked-state findings.

For same-board preservation, actual names such as `devinfo`, `uefivarstore`,
`persist`, `nvp`, `SN`, key/provisioning and modem-state candidates must not be
overwritten by a generic image. Their names do not reveal their contents.
P1 preserves none of those bytes, GPT boundaries, eMMC hardware boot regions,
RPMB or SoC-bound state. A/B and recovery-named nodes still do not provide a
tested restoration mechanism or rollback compatibility. Independent-boot
experiments remain gated on actual acceptance and recovery evidence.

## Checks and changed work products

Fifteen P1 offline tests passed. Full suite: **236 run, 235 passed, zero
failures/errors**, one Windows symlink-permission skip. Capture validation
passed all protocol/identity/integrity/deadline checks described above. The
original profile, N2 capture and earlier preflight/failure records remain
unchanged; final preservation hashes and exact work-product inventory are private.

Public changes in this increment: `tools/characterization_p1.py`,
`tools/adb_readonly.py`, `tests/test_characterization_p1.py`, the small historical
cross-reference in `docs/m10-p1-results.md`, and this new execution report.
All new raw evidence, approval records and host scripts remain ignored under
`build/m10/`. No Git staging/history, Pages, firmware or Sony-contact operation
occurred. M10 remains open.
