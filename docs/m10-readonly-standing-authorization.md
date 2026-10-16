# M10 proposed standing authorization for read-only characterization, v1

2026-10-14. **Proposal only; not approved or active.** The human authorized its
preparation after the one-shot B2 attempt. No operation described here has been
executed under standing permission. This proposal needs one explicit approval;
it does not ask to reauthorize B2 or retry either failed read.

## Authority and limits

Once approved, the agent may generate session-specific approvals and execute
either fixed plan U1 or H1 below without asking for that same plan again, while
all identity, host, device-state and failure conditions remain satisfied.
No background polling, unattended recurring runs or unrelated milestone work.
At most two sessions per human-initiated engineering turn, each only when its
result answers an identified current engineering question; no repetition simply
to reconfirm unchanged evidence. This is a conservative workload bound, not a
measured device-safe rate. Any session failure ends device interaction for that
turn, even if another plan remains. No retries or alternate reads follow.

In a later human-initiated engineering turn, a different approved plan may run
without renewed operation approval. A failed operation remains quarantined;
any fixed plan containing it is disabled until a separate explicit approval
addresses that failure and a revised procedure. Reporting a failure or human
acknowledgment alone does not clear quarantine.

This policy covers unprivileged metadata only. It does not authorize settings,
service, security or persistent-state changes; root/su/escalation; raw device,
partition, GPT, EXT_CSD, RPMB, FDT or tree-content reads; firmware/calibration,
APK or application-private file acquisition; input-event/PCM/mixer/watchdog or
sensor/regulator attribute opens; reboot, fastboot/recovery/EDL, experimental
boot, unlock, flash, erase or partition changes. No Sony contact, network/cloud
execution, Git history changes, public raw evidence or private identifier upload.

Ordinary diagnostic execution can still produce process/log/accounting and USB
charging effects. Binder queries can access package storage internally. A hang
could affect availability. There is no demonstrated original-board recovery;
no reboot or mode transition is a fallback. Socket closure does not guarantee
remote cancellation. These residual risks are part of the proposed approval.

## Device, host and freshness requirements

Bind only the owner-confirmed physical NW-A306 and unchanged private profile
`build/m10/authorizations/expected-nwa306-20261014-01.json`. Initial and ending
identity commands and exact newline-terminated values are identical to the
[B2 packet](m10-stage-b2-authorization.md#preconditions-identity-and-execution-entry):
UID 2000; `u:r:shell:s0`; Enforcing; NW-A300Series; icx1301; bengal; QCS2290;
build 27; slot `_b`; green; locked 1. The private serial/transport ID must match.
Never print them or adopt a changed profile automatically. Properties are not
cryptographic attestation. A transport ID is not a durable device identity.

At each session, host-only checks must establish the already trusted existing
BEAREAB-PC loopback server's listener owner, process creation, native image path
and pinned image SHA-256, using the B2 provenance record. Windows process-name
labels with/without `.exe` are representations; actual path/hash and process
continuity must agree. No ADB executable, daemon lifecycle request, restart,
reconnect or automatic discovery refresh. If the server or saved binding changed
or its continuity is uncertain, stop; obtain a separately reviewed discovery
scope. Do not turn a fresh serial/ID into the old approved binding.

Require normal responsive stock Android, previously authorized debugging, the
same confirmed physical connection, one online USB transport, and no known update,
playback, file transfer, prompt, hang or disconnect. The latest human confirmation
may be reused while that continuous connection and state are still known; do
not demand the same confirmation again merely because another approved plan is
selected. If time, intervening activity or uncertainty makes that state unknown,
request only the missing factual confirmation. Silence/time is not confirmation;
ADB identity alone cannot establish absence of playback or updates. Never issue
extra probes or change device state to satisfy these prerequisites.

## Fixed plan U1: locate the observed updater consumer

Question: where does the package manager register the physically observed
`com.sony.walkman.systemupdater` package's code? This is the next acquisition lead
for the preserved opaque NWWM firmware and its installer/authentication contract.

Run the eleven B2 identity checks, then exactly:

```text
/system/bin/pm path --user 0 com.sony.walkman.systemupdater
```

Then repeat the eleven identity checks: **23 observations**, 118 connections
under the unchanged transport pattern. Each identity stream cap is 4,096 B;
the package-path stdout and stderr caps are each 16,384 B. Require exit zero,
empty stderr and one or more bounded `package:` absolute-path lines. Only
registered base/split APK path metadata is accepted; no output is interpreted
as a command, executable or permission to open/pull a file. An empty result,
invalid path syntax or nonzero exit stops. Private paths stay private.

Risk: Binder query and internal package metadata/storage/log/accounting work;
no updater launch, APK transfer or APK byte read is requested. Returned paths
can identify code for a subsequent separately reviewed acquisition. They do not
establish installer algorithms, signing keys, custom acceptance or recovery.

Offline source basis: preserved AOSP `android-14.0.0_r1`
`PackageManagerShellCommand.java:726-757`, SHA-256
`7c554cc6e5b39a979c3aa6f63a20a139d85a94114f285d7fd1923b98f046ae13`:
`runPath()` accepts `--user`, calls `getPackageInfo`, and prints `sourceDir` and
`splitSourceDirs`. **Broader platform evidence, not a Sony binary match or Sony
access test.** The package's registration is physical B2 evidence; its path and
content remain unknown.

## Fixed plan H1: untouched hardware inventories

Question: which registered stock drivers, endpoints and boot-partition names
can anchor the independent-init and recovery-dependency investigation?

Run the eleven B2 identity checks, these six operations in this exact order,
then repeat the eleven identity checks: **28 observations**, 143 connections.

| Exact remote command | Cap per stream | Expected evidence / risk and limitation |
| --- | --- | --- |
| `/system/bin/toybox head -c 65537 /proc/asound/cards` | 65,536 B | Registered audio cards/driver names; cached proc metadata, no PCM open or playback proof |
| `/system/bin/toybox head -c 65537 /proc/asound/pcm` | 65,536 B | Registered audio endpoints; no mixer, route or firmware operation |
| `/system/bin/toybox head -c 65537 /proc/bus/input/devices` | 65,536 B | Registered key/touch identities and capabilities; no event sampling. Private Uniq/path values must be retained privately |
| `/system/bin/toybox ls -l /sys/class/graphics` | 16,384 B | Display-class links; VFS metadata, no attribute read or panel initialization proof |
| `/system/bin/toybox ls -l /sys/class/power_supply` | 16,384 B | Supply identities/links; no charge values, limits or control |
| `/system/bin/toybox ls -l /dev/block/by-name` | 65,536 B | Partition-name/link metadata only; no target opens, GPT, authentication or restoration proof |

The sentinel byte rejects oversized `head` output. Utilities may read internally
beyond emitted bytes. Listing caps bound output, not the number of internally
visited entries. All six paths remain untested on this player; access must not
be inferred from source modes or a successful unrelated read. Device-node links
are last because accessibility is uncertain. Failure stops rather than dropping
a row. Source callback/risk registers are retained in the B2/original packets.

## Immutable exclusions and failure handling

`/proc/device-tree/compatible` was denied in Stage B; `/proc/partitions` was
denied in B2. Both remain quarantined. Tree-property aliases, alternate entry
points and renamed commands are also excluded. U1/H1 do not include either
read. The untested tree model, raw-FDT metadata and regulator-instance listings
remain excluded; no broad traversal or ad hoc `getprop`, `ls`, `cat`, `head`,
package filter, package name or path substitution is allowed.

Preserve the existing direct-server invariants: loopback protocol 41; held
`host:track-devices`; saved USB selection; inventory/features guards before and
after each operation; atomic serial selection and returned transport ID on the
same connection as `shell,v2,raw`; closed stdin/no PTY; separate binary channels;
final one-byte exit and EOF. No fallback or reconnect. Any watcher change/loss,
identity/binding mismatch, prompt, denial, nonzero exit, stderr, unsupported or
invalid data, missing exit, timeout, interruption, byte limit or host I/O error
stops the session and ends device interaction for that turn. An already-dispatched
read might finish before change detection; rejection cannot undo it.

Each connection deadline remains five seconds; the full session deadline is
300 seconds, with a combined 2 MiB transmitted/received wire cap, 16,384 B host
reply cap and 4,096 shell-frame cap. These are separate from per-stream caps.
The guards/commands together are not promised to finish in five seconds.
Host log I/O and remote cancellation retain their documented limitations.

## Session admission, implementation and evidence

Approval of this document would authorize exactly U1/H1 under these conditions,
not arbitrary future read-only commands. It would also authorize minimal
repository-local registry wiring and offline tests needed to enforce those
plans; the current adapter does not yet expose U1/H1. No new transport framework
is required. No plan may run until its implementation passes offline checks for
exact commands/order/caps, exclusion enforcement, profile/output approval
guards, identity/watch failures, denial stops and binary integrity. Demonstrate
the new package-path output validator against malformed and oversized fixtures.

After that conformity check, pin each complete plan and code digest privately
to this approved policy's version/hash. The agent may generate a new approval
record for a conforming U1/H1 session autonomously; no second discretionary
operation approval is needed. Record the exact policy, plan, code, profile and
output hashes, engineering question, freshness basis and host preflight.
Changes beyond the exact scope or weakening a guard invalidate admission and
require a revised concrete proposal; an offline test pass never expands consent.

Use a new exclusive ignored `build/m10/` session directory. Preserve raw request/
response frames, decoded binary streams, exit/status, times, byte counts and
hashes; validate exact service/order and independent frame/stream agreement.
Mark partial sessions incomplete and quarantine their failure; require final
identity checks for whole-session completion. Rehash prior evidence for
preservation. Publish sanitized conclusions only. Code and evidence remain
unstaged/uncommitted and private materials stay untracked.

This is a documented proposal, not an active machine-enforced standing policy.
The private `read-only-policy-v1-20261014-01` preparation contains the two exact
proposed schedules and their hashes; those are scope artifacts, not executable
live-plan approvals. Implementation/source digests will be pinned after the
authorized minimal wiring, rather than pretending an unimplemented entry point
has passed live-adapter tests.

## Single approval decision

Approve standing policy v1 for the same privately bound player, including U1's
one exact new package-path query and H1's six untouched metadata reads, identity
bookends, limits, implementation/admission checks and failure quarantine. This
replaces per-session permission requests only within that fixed scope and may
be revoked at any time. B2 is already authorized and attempted; its reads are
not being submitted for reauthorization. All boot, security-state, acquisition
outside metadata and potentially persistent operations retain separate approval.
