# M10: Sony host delivery evidence and the next acquisition gate

2026-10-15. Offline work only; no player, ADB-server or fastboot communication.
N1/N2, denied reads, H1 quarantine and previous reference analysis are unchanged.

**Result:** newly acquired, signed Sony PC updater code establishes an MTP
firmware-delivery interface. It does **not** establish Sony loader readback,
temporary-boot registration, locked-state rejection or authentication ordering.
No accepted independent execution path or original-board restoration was found.
This closes a concrete host-companion lead to the extent described below;
it does not establish that no other acquisition or execution method exists.

## Question, acceptance criteria and authentic acquisition

The selected new question was whether Sony's PC companion supplies a loader,
readback/repair mechanism or different delivery path that could expose authentic
NW-A306 boot policy without touching the working player. Acceptance required
an authentic preserved container, selective static inspection, instruction
evidence for any claimed interface, and explicit limits on negative findings.
The already analyzed Android updater and reference LinuxLoader were not rerun.

Sony lists Music Center for PC on the
[NW-A306 download page](https://www.sony.com/electronics/support/product/nw-a306/downloads).
The [version-specific download page](https://www.sony-asia.com/electronics/support/articles/00259254)
identifies version 2.7.3.1, 187,376,616 bytes and release 2026-03-31. Its download
link supplied the acquired installer at:
`https://info.update.sony.net/PP002/MusicCenterForPcSSL/contents/0016/musiccenter_setup_2.7.3.exe`.
The NW-A306 listing retains an older 2024 date; the version-specific page and
[release history](https://www.sony.com/electronics/support/articles/MC4PC020001)
date 2.7.3 to 2026. This discrepancy is recorded, not used to infer a loader build.

| Original or derived artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Original `musiccenter_setup_2.7.3.exe` | 187,376,616 | `0b641d6951218fbf42210ea3bcb23b0bcb9f8e26561c1adb970bee6d0d4cc051` |
| Embedded main MSI, installer offset `0x29cc72` | 184,294,912 | `81654a6c29453dc6042888233f8e1f0842cad949d4c302cc5e7ae7c02f8eb595` |
| Selected `WmFwUpdater.dll` | 588,040 | `7c31378ed74d11d3eb49c91994675a632f5e911908cf52fe9134912575bf47a6` |

Windows Authenticode verification returned valid for the original Sony installer
and all five selected DLLs. This verifies host-package signatures; it says
nothing about accepted OTA, AVB or Qualcomm trust roots on the player.

Private evidence is under `build/m10/sony-host-delivery-20261015-01/`:
HTTP receipt/headers/hash, signature results, container indexes, read-only MSI
File-table export, extraction scripts, selected members, disassembly, checks
and preservation ledgers. No Sony program, custom action or library was run.
Microsoft Windows Installer `OpenDatabase(..., 0)` and SELECT read the MSI table;
this was not installation or administrative extraction. Trusted 7-Zip 26.04
performed static archive extraction; its acquisition URLs and hashes are saved.

Important extraction correction: a naive contiguous carve at the embedded
`MSCF` magic failed 7-Zip header validation. The CAB is an MSI compound-storage
stream and must be reconstructed through its sector chain. The failed carve
and failure log remain private. Extracting the named `Data1.cab` stream through
7-Zip produced a valid 166,671,471-byte, 53-block MSZip archive. No conclusions
were drawn from the failed carve. The exact MSI size excludes trailing package
data and does not alter the original installer.

The 1,500-entry MSI File table was matched to the CAB index. Nine selected files
were extracted, with table size/hash checks: `WmFwUpdater.dll`, `Mtp.dll`,
`UwcBackend_Library.dll`, `UwcHelperApp.exe`, `WmHelper.dll`, `OmgBootChecker.dll`,
`device.sal`, `model.js`, `AutoUpdatePCClient.ini`. No member is named as an
ABL/aboot, fastboot, Firehose, boot image, vbmeta, payload.bin or UPG artifact.
This is a **name-inventory result**, not proof that opaque resources cannot
contain additional code. `device.sal` is opaque; it was not executed or decoded.
The additional backend/helper inspection was limited to strings and PE metadata.

## New Sony implementation evidence

Classification: **verified from authentic Sony host artifacts**. The product
listing makes this companion applicable to the A306, but the native module
also supports other products. These observations are neither an acquired Sony
loader nor demonstrated calls on this NW-A306.

`WmFwUpdater.dll` is **x86 PE32**, preferred base `0x10000000`, not AArch64.
Its `.text` is RVA `0x1000`, file offset `0x400`; `.rdata` is RVA `0x5c000`,
file offset `0x59e00`. File offsets, RVAs and virtual addresses were kept
distinct. Independent Capstone 5.0.6 disassembly is preserved privately.
Existing ARM64 xrefs only cover ADR/adjacent ADRP+ADD candidates; they cannot
analyze this module. ELF/MBN/GPT inspectors remain unchanged and are inapplicable
to the host DLL. No reference-firmware analysis was repeated.

| DLL locator (RVA unless stated otherwise) | Established observation / limit |
| --- | --- |
| `0x21707–0x2173e`; call `0x2175a → 0x24877` | Device-eligibility path looks for both advertised opcodes `0x9401` and `0x9402` before querying device information. Nearby diagnostic at file `0x63768` identifies `sony.net/WMFU`; no live extension support is claimed. |
| Method entry `0x24877`; diagnostic address at `0x24903`; operation constant at `0x24bcd` | `CWmFwPortableDevice::GetDevInfo` constructs operation `0x9401`. The operation-property setter and transfer diagnostics support an MTP information transaction, not partition readback or a boot-command list. |
| `0x27b07`, `0x27d18`; data `0x68d40`, `0x68ef0` | Storage-selection path references exported `default-capability.xml` and a firmware-update-supported storage XPath. A capability file is not an authenticated boot-policy declaration. |
| `0x29be8 → 0x2451a`; `0x29d60 → 0x23977` | MTP firmware-copy worker calls DeleteFile and CopyFile routines. These are active object operations; running the worker is outside this assignment. |
| `0x23e96 → 0x293fe`; `0x296c7–0x297b2` | CopyFile calls StreamCopy. The latter passes the same buffer from stream Read to Write in its copy loop, with no transform between those calls. This establishes that copy stage, not absence of transformation elsewhere in the application or on-device installer. Microsoft documents [Read](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nf-objidl-isequentialstream-read) and [Write](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nf-objidl-isequentialstream-write). |
| `0x2a48f → 0x28d4b`; diagnostic `0x28dad`; operation constant `0x28fd3` | Separate `StartFWUpdate` constructs opcode `0x9402`. Do not call it as an information probe: its intended operation starts installation. |

The host evidence supports ordinary firmware-file delivery and an explicit
update-start transaction. It supplies no demonstrated service that reads a
loader or executes a supplied Linux image in RAM. Absence of selected strings
or imports is not a complete negative call-graph proof. The PC module's vendor
opcode numbers must not be sent to fastboot or treated as bootloader commands.
Do not invoke either vendor transaction under existing characterization approval.

The narrow verifier `tools/inspect_sony_pc_updater.py` requires the exact DLL
hash, validates bounded PE32 mapping, then checks 17 selected instruction,
relative-call and data locators. It does not load code, send commands, solve a
whole-program CFG or claim a named diagnostic alone proves reachability. The
private disassembly supplies the surrounding code reviewed for the table.

Reproduce against the private artifact:

```powershell
python tools/inspect_sony_pc_updater.py build/m10/sony-host-delivery-20261015-01/selected/WmFwUpdater.dll
python -m unittest discover -s tests -p test_inspect_sony_pc_updater.py -v
```

## Other targeted source result

Four selectively read members of the preserved Sony 3.06 source archive were
examined for a software-visible loader-log acquisition path. Exact member
names/hashes are in `boot-log-source-members.json`; archive SHA-256 remains
`5bf646baad7d99a3c598cdc1050fdb1af9a944c9ee6dcbd7e60680c313cfc477`.

`kernel/msm-4.19/drivers/soc/qcom/boot_stats.c:19–24,74–100` describes timestamp
fields and printing them, not a retained loader binary or command log.
`minidump_log.c:42–63,359–370` registers the **kernel** log buffer for minidump;
`msm_minidump.c` and `memory_dump_v2.c` provide dump infrastructure, not an
established ordinary-shell loader reader. Source presence does not prove build
selection or access. No crash, minidump trigger, memory read or download-mode
experiment follows from this finding. These candidates do not currently justify
additional physical log acquisition.

## Boot-acceptance decision

| Remaining Sony hypothesis | Current evidence / distinguishing result |
| --- | --- |
| Temporary `boot` absent | Still possible. Need authentic dispatcher/build evidence or a separately justified dispatcher observation. No new Sony reply was obtained. |
| Registered but locked rejection | Still possible. Need Sony handler instructions or a transaction whose interpretation is justified independently of the RB1 model. |
| Registered with authenticated-image requirement | Still possible. Need Sony's verifier, trust inputs and image coverage/order; a signed PC DLL is irrelevant to this gate. |
| Owner-controlled accepted execution | Unproved. Need an implemented owner trust/temporary-execution mechanism and an applicable image. Existing locked/secure reports do not establish that one exists. |

No hypothesis becomes viable merely from this acquisition. The strongest
execution target remains a Sony-supported, authenticated or owner-controllable
temporary Linux handoff **if such a path exists**. The blocking capability is
access to Sony's actual dispatcher/verifier or equivalent direct evidence.
More informational getvars and repeated reference disassembly cannot supply it.
Do not submit a no-download, empty, malformed or arbitrary `boot` as a harmless
probe: Sony's dispatch, buffer state and pre-verification writes remain unknown.

## Proposed P1: unattempted loader-node metadata gate

**Requires new authorization; not executed or added to a live registry.**
This is the least disruptive remaining practical acquisition check on the one
working unit: establish actual exposed partition names and node modes/labels
before considering any raw read. B2/H1 stopped before their block-name listing;
no successful or denied block-directory observation is being repeated. H1 stays
quarantined. P1 does not retry or replace the denied proc/tree/audio content reads.

After the existing eleven identity observations, propose only:

```text
/system/bin/toybox ls -ldZ /dev/block/by-name
/system/bin/toybox ls -lZL /dev/block/by-name
```

First command: 4,096 bytes per stdout/stderr stream, five seconds; require exit
0, empty stderr and exactly the named ordinary directory, no final symlink.
Otherwise stop, even if a symlink is normal on another Android model.

Second command: 65,536 bytes per stream, five seconds, only after the first gate.
`-L` obtains target inode metadata: type, mode, owner/group, security label and
major/minor numbers under the existing names. It opens no partition content and
does not read GPT, `/proc/partitions`, a DT or filesystem payload. Require exit
0, empty stderr, bounded complete output and ordinary expected node metadata;
dangling links, unexpected objects, overflow or uncertainty terminate the session.
Do not substitute paths or follow up with `cat`, `dd`, `head`, an ioctl or root.

Then, only on success, repeat the same eleven ending identities. Exact identity
commands/values remain those in the frozen `characterization_plan.IDENTITY`
registry and private approved profile: uid, shell context, enforcing state and
eight Sony/build/slot/lock properties. Total: **24 observations**, 319,488 bytes
combined stdout/stderr ceiling, existing 2-MiB wire and five-minute session caps.
Before execution, implement and offline-test this fixed registry, bind its digest,
code hashes and the unchanged private identity profile to a new approval record.
Reuse the trusted no-lifecycle adapter and server/transport guards. Do not edit
N1/N2, renew bindings silently, start ADB or implement a generic command runner.

Prerequisites: fresh owner confirmation of the same connected, responsive stock
unit, previously authorized debugging, no update/playback/transfer; matching
trusted existing ADB server process/image, single USB device and approved profile.
Preserve exact binary streams, statuses, timing, manifests and hashes privately.
Any failure or identity/server change stops without retry or alternate access.

Expected decision: actual loader-like names plus potentially readable modes
would justify a **separate**, exact-artifact acquisition proposal. Names are not
assumed to be `abl_a`, and modes do not prove effective access: groups, SELinux,
symlink races and storage policy still matter. Restrictive nodes or no useful
entries would reject this ordinary-unprivileged acquisition hypothesis for the
observed state, not every software route. Even successful acquisition would not
prove boot acceptance. P1 intentionally makes no payload read or boot attempt.

Risk is qualitatively low: ordinary VFS metadata work, diagnostic accounting,
USB/charging effects, hangs/disconnects and private partition inventory exposure.
No boot-mode transition or intended persistent-state change is requested. No
special return procedure should be necessary because Android stays running;
if it stops responding, cease communication and report, without automatic reboot
or recovery action. Approval would cover only these metadata observations and
the stated guards, not collection of raw storage or another experiment.

The private, non-executable `p1-proposal-unapproved.json` binds these 24 commands,
limits and original profile hash. Its proposal digest is
`8130a847398b50a8da8960a1cd9bc3d8842fc67f03fcea5a2c143ddb12e5acbe`;
`approved:false` and `executable:false` are explicit. This is a scope digest,
not a claim that a live P1 implementation has been validated or authorized.

## Recovery and validation

This increment acquires **no original-board partition bytes or unique state**.
Before any first boot-image experiment, still require applicable original
boot/DT/AVB/loader inputs and layout, understood pre-authentication GPT/slot and
rollback effects, preservation of board-specific provisioning/calibration and
security-bound state, and an accepted surviving same-board repair path.
An OTA, reference rescue package or Power return from normal fastboot is not
that repair path. No secrets, RPMB or secure-storage service were accessed.

Actual validation: seven new unit tests passed; 17 authentic-DLL locator checks
passed. The inspector regression set ran **57 tests, zero failures/errors/skips**
with the already preserved optional Capstone dependency. An initial run without
that dependency passed with three expected disassembly skips; both logs remain.
No N1/N2 integration or physical operation was rerun. Prior-file preservation,
new-artifact hashes, table/index consistency and final Git results are recorded
in the private final-validation ledger. All 3,426 inventoried prior private files
and four preceding public work products matched; all 1,500 MSI/CAB names/sizes
matched and all nine selected member hashes verified. The source archive hash
also matched. Final Git status: the pre-existing tracked roadmap modification,
47 untracked files including these three additions, and nothing staged.

Public files added in this increment: this report,
`tools/inspect_sony_pc_updater.py`, `tests/test_inspect_sony_pc_updater.py`.
All other additions are private under the single directory above. Existing
uncommitted files, `.local-references/`, roadmap, N1/N2 and Git history were not
modified. M10 remains open; independent Sony execution remains unproved.
