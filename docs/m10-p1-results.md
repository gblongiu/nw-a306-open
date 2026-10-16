# M10 P1 integration and preflight result

Later owner authorization permits one freshly resolved, session-local transport
ID for the original physical device. See [P1 correction and execution](m10-p1-execution.md).
The earlier preflight outcome below is retained unchanged as history.

2026-10-15. **P1 authorized, implemented and tested; not executed.**
No ADB-server request or player command was sent. There is no P1 permission
denial, partition inventory, raw acquisition or new physical boot observation.
N1/N2 and earlier successes/failures remain preserved.

## Actual preflight blocker

The [P1 proposal](m10-sony-host-evidence.md#proposed-p1-unattempted-loader-node-metadata-gate)
pins the original private profile and forbids silent binding renewal. Its scope
digest and profile-file hash still match the preserved proposal. However,
N2's successful post-return manifest records a different ephemeral ADB transport
ID for the **same serial and unchanged eleven-value identity policy**.

That is evidence of a prior transport change, not a new device mismatch or a
current live transport observation. The original P1 binding cannot be presumed
current. The fresh human confirmation of normal responsive Android and idle
conditions does not resolve which server transport ID is authorized for P1.
The documented uncertain-prerequisite stop therefore occurred **before server
communication**, without substituting the N2 binding or modifying the profile.

Host-only checks passed: BEAREAB-PC, the same unique existing loopback ADB
listener/PID/process-creation time, pinned native server path and SHA-256, and
the healthy physical USB root/location matching the saved N2 post-return host
snapshot. Windows host/PnP inventory and native process-image inspection were
used; neither adb.exe nor fastboot.exe was executed. The owner confirmed the
same idle stock device with previously authorized debugging. No ADB lifecycle,
connection repair, new discovery or partition operation was attempted.

Private receipts under `build/m10/p1-integration-20261015-01/` contain exact
host output, owner confirmation, code/plan/profile hashes and the preflight
failure record. There is deliberately no live `device-p1` capture or executable
approval file: **zero P1 sessions were attempted**. Do not mistake the fake-server
integration outputs for physical evidence.

## Fixed integration

`tools/characterization_p1.py` adds exactly these two observations between the
existing eleven starting and eleven ending identities:

```text
/system/bin/toybox ls -ldZ /dev/block/by-name
/system/bin/toybox ls -lZL /dev/block/by-name
```

First cap: 4,096 bytes per stream; second cap: 65,536. Every operation retains
a five-second deadline. The session retains 319,488 combined output bytes,
2 MiB wire bytes and five minutes. Successful exit and empty stderr are
mandatory. The second command is unreachable after a failed first validator.
Transport/identity guards run before and after every successful observation;
the same-connection serial selection must return the pinned transport ID.

The conservative parser accepts one exact ordinary-directory record, then a
complete Android toybox `total` header and uniquely named block-node records.
It validates mode, ownership, labels, device major/minor fields and timestamps.
Symlinks, unexpected object types, duplicate/unsafe names, ambiguous records,
missing labels, partial output and excessive streams stop the session. Modes
are recorded, not interpreted as proof of effective read access. No command
opens a partition for content or follows observations with additional commands.

Formatting was checked against the already preserved AOSP Android 14 toybox
`ls.c:247–261,360,380–395,473–519,605`, provenance in
`build/m10/c1-integration-20261015-01/toybox-source-provenance.json`.
It provides a platform formatting model, not proof of Sony access permissions.

The adapter change only adds P1 stage selection, validator routing, strict
stream caps and source hashes. No lifecycle, socket, retry, discovery or generic
command mechanism changed. P1 hashes both its module and C1's reused field
patterns. Integrated plan SHA-256:
`7e877056c82c88c493124089c1b1a5da7e81ef0d1e110749c6b52c5b571389aa`.
This executable-plan digest includes reviewed code hashes; it is distinct from
the earlier non-executable proposal digest and preserves its exact operations.

Changing the shared adapter changes code-bound plan digests. Historical captures
remain bound to their original code; the previous adapter bytes were preserved
before editing. Old approvals/grants must not be regenerated or reused silently.
N1/N2 source files, stored approvals and physical captures were not edited.

## Validation and preservation

- Ten P1 fake-transport tests passed. Real socket and process constructors were
  blocked. Checks cover exact sequence/caps/digests, inert CLI, atomic selection,
  stale bindings, failed first gates, malformed listings, denied/missing paths,
  warnings, oversized streams, evidence hashes and refusal before communication.
- Full repository suite: **231 tests run, 230 passed, zero failures/errors**.
  One Windows symlink-permission test skipped. The preserved Capstone dependency
  was supplied so instruction tests were exercised. This is offline regression,
  not another N1/N2 physical experiment.
- The host preflight matched the approved command registry and limits. Its sole
  failed check was the original versus last-verified transport-binding comparison.
- Prior evidence and uncommitted files are hashed in `preservation-before.json`.
  The intentional shared-adapter change is compared through its preserved
  `pre-change-adb_readonly.py` copy. Final preservation and checkpoint results are
  saved alongside the test logs: all **3,541 prior files** matched, with zero
  mismatches. No previous evidence was overwritten.

## Next acquisition decision and narrowly defined reconciliation

No Sony partition names were observed by P1. Do not promote `abl_a`, `boot_a`,
`dtbo`, `vbmeta`, `vendor_boot` or recovery names from the reference board into
Sony facts. Existing N1/N2 observations continue to prove bootloader fastboot,
locked/secure state and supervised stock return, not temporary-image acceptance.

The highest-value immediate action is to resolve **only** P1's binding policy,
then run the already authorized metadata scope once if all guards pass.
`binding-reconciliation-proposal.json` is private, `approved:false` and
`executable:false`. It proposes the already verified N2 post-return profile,
changing only `binding.transport_id`; serial and every identity value remain
identical. The original profile stays immutable. Its proposal digest is
`45a0587d571936089ab122cff6797b85e968925bae3a08eb28d51e41d9c7199f`.

This reconciliation needs explicit review because the approved document pins
the original profile and forbids silent renewal. It is **not** a request to
reauthorize the same metadata commands. Once approved, the existing adapter
must still verify the exact candidate transport; any mismatch stops without
another refresh, retry or alternate command. No new discovery or mode change
is proposed. A changed server/USB identity remains a separate hard stop.

If P1 later succeeds, actual names, node types, ownership and labels can select
an exact loader-acquisition candidate. Permission metadata alone cannot establish
SELinux access or authenticate an image. Reading original partition bytes would
still require a separate fixed acquisition proposal with verified target identity,
size bounds and integrity checks; P1 grants none of that access. A denied P1
must be preserved without a substitute path. The current result is a host
preflight block, not evidence against Android partition-directory accessibility.

There is no new evidence permitting a Linux boot image to be submitted. Sony
dispatcher/verifier behavior, pre-authentication GPT/slot/rollback effects and
same-board restoration remain unresolved. P1 stays in Android and does not
intend persistent-state changes. If unexpected loss of responsiveness occurs
during a future approved run, stop communication; do not improvise a reboot.
The successful N1/N2 Power return remains distinct from firmware restoration.

## Work products

This increment adds this report, the
[separate checkpoint inventory](m10-source-control-checkpoint.md),
`tools/characterization_p1.py` and `tests/test_characterization_p1.py`, and modifies
`tools/adb_readonly.py`. Private additions are confined to the P1 integration
directory. Existing roadmap changes and accumulated M10 work remain uncommitted.
No source-control history, staging, Pages or Sony contact operation occurred.
Final status: the pre-existing tracked roadmap modification and 51 untracked
files, including the four additions above; nothing staged. The shared adapter
was already untracked and its preceding bytes are preserved privately.
