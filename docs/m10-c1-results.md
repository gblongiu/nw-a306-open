# M10 C1: metadata denial and the next boot-interface observation

2026-10-15 correction: the later
[fastboot reconciliation](m10-fastboot-reconciliation.md) supersedes the M1
menu-discovery proposal below. Historical owner-device ADB-to-fastboot entry and
Power-button return were already observed. M1 was never executed or authorized;
its proposal is retained as history. C1's raw denial and validation are unchanged.

2026-10-15. C1 was explicitly authorized and attempted once after the owner's
fresh prerequisite confirmation. It stopped at the parent query as required.
M10 remains open; no independent Sony boot or same-board restoration is claimed.
Historical proposals and raw evidence remain unchanged.

## Physical result

Classification: **demonstrated on physical NW-A306 hardware** through the
previously approved private identity/transport binding and trusted existing ADB
server. The eleven initial identity observations passed. The next operation was:

```text
/system/bin/toybox ls -ldZ /mnt/icx_cache
```

Exit status was **1**, stdout **0 bytes**, stderr **38 bytes**:

```text
ls: /mnt/icx_cache: Permission denied
```

The adapter stopped with `inaccessible`: **12 attempted observations, 11 valid**.
It did **not** attempt the ZIP metadata query, ending identity queries, retries,
alternate paths or content acquisition. No server lifecycle action, update,
privilege change, reboot or setting change occurred. There were 61 bounded
server connections carrying 11,904 logged wire bytes, including identity and
transport guards. No further device requests followed the failure.

**Established:** the approved shell cannot complete this parent metadata query.
**Unknown:** the parent's type, label and permissions; the reason for denial
(DAC, SELinux or traversal); whether `NW_WM_FW.zip` exists or is readable.
The result closes this authorized access attempt, not every cache-acquisition
possibility. It does not justify an OTA content-acquisition proposal, permission
bypass or neighbouring-path search.

Raw capture is private in ignored `build/m10/device-c1-20261015-01/`. The raw
manifest remains partial and retains the adapter's conservative
`physical_evidence:false`; the separate `capture-validation.json` in ignored
`build/m10/c1-integration-20261015-01/` records the physical classification and
its basis without changing original evidence. Private identifiers are omitted
from this report.

## Implementation and validation

- `tools/characterization_c1.py`: fixed registry of the two exact metadata
  operations, surrounded by the existing eleven start/end identities; strict
  inode-output validation rejects symlinks, unexpected paths/types, ambiguous
  lines, malformed timestamps and an empty ZIP candidate. Metadata never proves
  content read access.
- `tools/adb_readonly.py`: C1 integration with existing admission, continuous
  transport watch and atomic serial/transport selection. Four source hashes,
  session-specific approval, unchanged profile and exact operations are pinned.
  C1 stream capture stops at the literal 4,096-byte limit; other stages retain
  their previous behavior. No new transport or lifecycle mechanism was added.
- `tests/test_characterization_c1.py`: nine fake-server tests cover exact order,
  plan/code/profile guards, identity/transport mismatch, failure preservation,
  strict bounds, malformed metadata and inert default invocation. Tests block
  real sockets and subprocesses.
- `docs/m10-c1-results.md`: this result and the proposed next experiment.

Acceptance criteria were fixed scope, guard checks before shell execution,
4,096 bytes per stdout/stderr, five seconds per operation, no target query after
parent failure, and byte-preserving private failure evidence. These were met;
successful metadata acquisition was not.

The full suite ran **164 tests: 163 passed, one existing Windows
symlink-permission skip**. All nine new tests passed. Offline capture validation
verified all **146 stream files** and their lengths/hashes, the 147-file capture,
approval/plan/profile binding, exact attempted command prefix, atomic transport
responses, timing and wire totals. **1,473 prior ledger-covered files** remain
preserved; the deliberately changed adapter's original bytes were saved before
editing. Existing standing grants are not silently rebound to the new code.
No earlier denied read or quarantined H1 operation was retried.

## Offline finding affecting boot-entry design

Classification: **established for AOSP Android 14, not demonstrated on Sony**.
In pinned `android-14.0.0_r1` source:

- [`init/reboot.cpp:1057-1071`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/init/reboot.cpp#1057)
  calls `write_reboot_bootloader` for a bootloader-target reboot.
- [`bootloader_message.cpp:225-235`](https://android.googlesource.com/platform/bootable/recovery/+/refs/tags/android-14.0.0_r1/bootloader_message/bootloader_message.cpp#225)
  reads the existing control message, refuses an already pending command, sets
  `bootonce-bootloader` and writes the message back.
- The same file, lines 161-172 and 114-140, resolves the misc device, opens it
  for writing, writes and calls `fsync`. Sony's actual mapping and implementation
  remain unknown. This is not a claim that our player received such a write.

Original source bytes, hashes, retrieval URLs and bounds are private. No source
or extracted program executed. This finding removes the assumption that an
ordinary ADB bootloader request is necessarily a volatile observation. Prefer
investigating the reported manual entry from stock Restart, without deliberately
requesting the AOSP bootloader-control-message path. Manual entry still has
unverified persistent effects and availability risk.

First-person [NW-A306 reports](https://www.reddit.com/r/walkman/comments/170vq2v/nwa306_android_recovery_mode/)
describe Restart followed by Volume Down reaching a menu; one explicitly claims
Android 14. Other reports conflict about keys and timing. Classification:
**plausible but unverified** on our build, including menu controls and exit.
Only the entry lead is relevant; recovery selection and factory reset are
excluded. Sony's [model-specific restart guide](https://helpguide.sony.net/dmp/1301/v1/en/contents/TP1000733532.html)
documents Power for two seconds, then Restart, and Power for ten seconds for a
frozen player. It does not document boot-menu exit or firmware restoration.

## Proposed M1: one manual menu observation and return

**Not authorized or executed.** Scope is the owner's sole functioning NW-A306.
No donor, exposed board, disassembly or loader dump is required. This is a
boot-mode experiment, not an extension of the standing read-only policy.

Prerequisites: fresh physical identification of the same unit; responsive stock
Android; no update, playback or transfer; no known pending update/restart;
owner-confirmed personal-data backup; on-screen battery at least 50% (an
engineering precaution, not a Sony-specified threshold). The owner operates the
buttons locally and has a camera and timer. Keep the existing cable connection
unchanged; no host command is issued and automatic device tooling is inactive.
If any prerequisite is uncertain, do not begin.

Exact proposed actions, for separate approval:

1. With the screen on, hold Power for two seconds and tap stock **Restart**.
   Immediately hold **Volume Down**, releasing at the first Sony logo or menu,
   or at 30 seconds, whichever comes first. This is one bounded attempt at the
   reported sequence, not a verified Sony procedure. No substitute key chord.
2. Observe for at most two minutes. If Android starts normally, record that the
   attempt did not expose a menu and stop; it does not rule out all interfaces.
   If a menu appears, photograph its initial screen privately without navigating.
   Capture exact menu title, visible version/security labels, options, selected
   option and on-screen control instructions; avoid publishing identifiers.
3. Select **Start** only if that exact option is visible, explicitly represents
   normal OS boot, and the screen unambiguously explains navigation/selection.
   Follow only those displayed controls. If any condition is absent, do not
   navigate or select another option. No Recovery, restart-bootloader, factory
   reset, update, unlock or slot option is permitted.
4. If normal boot cannot be selected or the unit becomes unresponsive, record
   the screen and stop the investigation. The proposed approval also includes
   **one Power-only ten-second forced-restart attempt**, then release and wait
   two minutes without other keys. This is an availability fallback based on
   Sony's frozen-player guidance; its effect in an unknown loader mode is
   unverified. If stock Android does not return, stop without repeated resets,
   recovery/EDL entry, host commands or improvised repair.
   Do not force restart an update or write-progress screen; leave it undisturbed
   and stop for review.
5. Record whether stock Android returned and is responsive to normal on-screen
   interaction. That establishes only this transition's observed return, not
   restored firmware or complete hardware operation.

**Exact host command list: empty.** No USB fastboot query, download, RAM boot,
image readback, write or payload transfer is covered. Stop on any unexpected
warning, automatic update, security-state prompt, abnormal heat, ambiguous
control or identity concern. If a menu is unexpected, capture only its initial
screen and use only the bounded fallback above.

Risks are temporary or prolonged unavailability, accidental menu selection and
unknown vendor mode handling. Ordinary shutdown/startup can update logs,
counters or boot reasons; no wholly volatile-state guarantee is made. There is
no intended firmware modification, but no demonstrated same-board firmware
restoration route exists. Approval must explicitly accept that unresolved
availability risk, including the conditional forced-restart fallback. The
procedure is not a recovery guarantee.

## Engineering decision

The next useful hardware observation is the authentic menu and its return path,
not another cache permission attempt or speculative loader payload. A menu with
bootloader identity would make a later fixed, separately approved USB metadata
probe worthwhile. A recovery-only screen or normal Android return would reject
this attempt's assumed entry, not establish global infeasibility. Menu access
alone proves neither USB fastboot support, implemented RAM boot, command
authorization nor acceptance of modified kernel/ramdisk/DT/AVB data.

The strongest remaining initial execution hypothesis is an implemented temporary
boot path whose Sony authentication policy admits an independent payload. It is
**unresolved**, not presently viable or ready for a payload experiment. Full
loader acquisition is not mandatory for M1. Authentic command behavior,
accepted image format/trust policy and a justified return path remain necessary
before independent Linux execution can be tested.

Preservation still needs board-matched original layout/images, applicable
rollback/AVB relationships, device-specific calibration/provisioning and an
accepted surviving repair interface. Existing OTA/reference packages do not
establish these or reconstruct RPMB/SoC-bound state. This session narrowed the
ordinary OTA-residue access route and the boot-entry risk model; it did not
obtain loader bytes, establish restoration or demonstrate independent boot.
