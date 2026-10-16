# M10 transport boundary validation

2026-10-14. Host-only transport validation and characterization preparation.
Starting Git status already contained modified `docs/roadmap.md` and untracked
characterization-plan/test/investigation files. That prior work was preserved.

## Implemented boundary and tests

`tools/characterization_transport.py` reuses the existing profile, payload and
private-output policy. It adds fixed approved-subset scheduling, pure proposed
argument construction, before/after transport guards, concurrent bounded binary
pipe draining, real monotonic deadlines, bounded client cleanup and exclusive
provenance logs. Only an injected simulation is admitted. There is no subprocess
launcher, socket connection, USB discovery, default executor or live fallback.

The 18 new tests use in-memory fake transports and two hardcoded local Python
children. No proposed ADB argument tuple is executed. Real pipe fixtures test
65,536 arbitrary bytes on each channel concurrently and killing/reaping a hung
child with a partial result. The simulation API is trusted test code, not a
sandbox for hostile plugins.

Coverage: unknown/reordered/duplicate commands, digest mismatch, hostile serials,
missing identity, wrong/ambiguous/offline/unauthorized transports, boolean counts,
non-USB state, absent shell-v2, replaced server epoch and root UID. Capture tests
cover binary fidelity, separate stdout/stderr, exit/permission/unsupported
categories, malformed pipes/disconnect, per-stream/total limits, exhausted
budget stopping before another dispatch, actual deadlines, missing exit,
cancellation/interruption, blocked readers and no retry. Logging tests cover
exclusive deterministic names, exact hashes/counts, provenance, traversal,
overwrite refusal and host-write failure.

The shared profile validator now requires canonical, positive uint64 transport
IDs. Zero can select the client's default-target branch, so `0`, leading zeros,
negative and overflowing IDs are refused before any dispatch. This tightens the
earlier replay admission rule without changing its fixed command-plan digest.

Categories are diagnostic: `inaccessible` uses a permission-denied message and
`unsupported` conventional exit 127; raw exit/stderr remains authoritative.
They cannot identify a particular DAC/SELinux cause. Successful capture with
invalid payload becomes `invalid_output`, retains bytes and stops the session.

Cleanup uses bounded process wait/reader joins. Client termination does not prove
cancellation of descendants, server work or remote commands. A blocked reader
produces incomplete cleanup and ends the session. Disk failure can prevent the
attempted partial manifest too; no durable storage guarantee is claimed.

## ADB source constraint and remaining live gate

Pinned Android `android-14.0.0_r1` sources were acquired by HTTPS, not by executing
ADB or Git. Originals/provenance are private under
`build/m10/transport-validation-20261014/primary/`.

| Primary source | Verified broader-platform behavior / SHA-256 |
| --- | --- |
| [client/commandline.cpp](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/client/commandline.cpp):691-786 | Explicit -T requests raw mode and fails when shell-v2 is unavailable; remote args are joined without escaping. Requires a constant audited remote string. `18af1ace283cf2056aee7d0c87dbeed9a0ba79374dc303e72939658a4f08099b` |
| [client/adb_client.cpp](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/client/adb_client.cpp):254-330,408-435 | Missing local server can be launched; version mismatch can kill/restart it. Targeted services/features support transport IDs. `49338f10503ea57859c83b8f9b3dc4bd9e71bca7fe7dd82b89418c3ae542cc53` |

These are not an exact source mapping of installed 36.0.2 or the Sony daemon.
Pure argument construction does not make the CLI safe to launch. A future live
adapter must prevent implicit lifecycle changes, bound admission/start/guards,
parse bounded inventory/features, classify actual USB transport, preserve
shell-v2 status/channels and verify the server epoch. Current tests validate
pipe/simulation behavior, not these unimplemented live properties or Sony access.

## Records and deliverables

Final test counts/commands, private artifacts and Git status are recorded after
verification in ignored `build/m10/transport-validation-20261014/validation.json`
and `work-products.json`. Original `build/m10/work-products.json` and its 14
files remain unchanged. The new Sony source audit reads four exact regular
members, 180,085 bytes; no broad extraction or local-reference writes.

Executed full unittest discovery: **Windows 84 tests: 83 passed, one symlink
creation skip; WSL Ubuntu 24.04: all 84 passed.** The 18 new transport tests pass
on both platforms. Commands: `python -m unittest discover -s tests -p 'test_*.py' -v`
and WSL Python discovery over the same test directory. No ADB/fastboot/EDL utility
was executed. `git diff --check` and explicit new-file whitespace checks passed.

The [authorization packet/runbook](m10-characterization-authorization.md) lists
every proposed command, full host argument contract, output index, bounds,
permissions, risks, stops and deployment decision. Ten extra metadata reads
cover Android/loader reports, storage, ALSA/input and display/power/regulator
directory metadata. They do not measure hardware operation or electrical state.

This host assignment supplies the validated simulated interface and review
packet. No physical compatibility, accepted independent boot or restoration is
established; M10 remains incomplete. Next human review concerns the operation
scope. Actual execution additionally requires private identity binding and a
reviewed no-lifecycle live adapter. Passing tests grants neither permission.

## Final no-lifecycle adapter, 2026-10-14

`tools/adb_readonly.py` now implements the missing direct smart-socket adapter.
It contains no subprocess or lifecycle operation. Default CLI/module import and
plan construction are inert. Explicit `--run-approved`, a matching stage/plan/
profile/output approval record and a new ignored output directory are required
before its sole connector can reach IPv4 `127.0.0.1:5037`. Consent still comes
from the human, not from the existence of a JSON file.

It verifies protocol version 41; discovery uses `host:devices-l` and atomic USB
selection. Characterization holds `host:track-devices`, checks inventory/features
before and after each read, then selects the approved serial and verifies its
returned nonzero uint64 ID on the **same connection** as each fixed shell-v2
command. It closes stdin, separates binary stdout/stderr, requires a one-byte
exit plus clean EOF, rejects unknown frames and never retries uncertain sends
or commands. It directly journals every transmitted/received byte within session
bounds, including selections, errors and framing; decoded streams have separate
hashes. Failed records remain incomplete.

The [final two-stage authorization packet](m10-characterization-authorization.md)
supersedes the earlier CLI reference proposal. No ADB executable is invoked.
Its exact request sequence, output names, host arguments, permission/risk
matrix and stop conditions reflect the implemented adapter. No approval file or
genuine device profile has been created. The next step is Stage A discovery,
only after explicit approval; no further host milestone is proposed.

New integration tests use only injected fake sockets with actual socket and
process constructors blocked. An additional connector test mocks the socket
constructor and verifies its one fixed endpoint and single attempt. Tests cover
fragmentation/partial sends, version/status/length/FAIL rejection, absent server,
serial/USB/ID ambiguity, shell-v2 negotiation, binary fidelity, separate exit/
stderr, missing/invalid/duplicate/trailing exit, interrupted payload, deadlines,
cancellation, stream/session budgets, tracker update/EOF, forbidden services,
exclusive paths, disk-write failure and exact log hashes. They do not connect to
any real server, physical Android device or virtual Android device.

Results: **102 tests on each platform: Windows 101 pass plus the existing
symlink-permission skip; WSL Ubuntu 24.04 all 102 pass.** All 18 new adapter
tests pass on both. Existing local Python pipe fixtures still run as controlled
host fixtures; no ADB, fastboot, EDL or other device utility is executed.

The protocol does not authenticate the local server or supply a durable epoch
across A/B approval gaps. Trust in the existing local server and human matching
are prerequisites. The live tracker is a session-lifetime signal, not OS-process
attestation. Separate guards cannot make change detection atomic with dispatch;
a read already sent when change is detected may run. Serial/ID atomic selection
prevents selecting a different serial through reused IDs, while tracker/guard
failure rejects the session without retry. Socket closure cannot guarantee
remote cancellation. These are explicit limitations, not pending implementation
work or reasons to assume unsafe compatibility.

Protocol source register (Android `android-14.0.0_r1`, platform evidence only):

| Primary source and exact locator | Established contract |
| --- | --- |
| [OVERVIEW.TXT:83-126](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/OVERVIEW.TXT) and [SERVICES.TXT:7-29](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/SERVICES.TXT) | Smart-socket hex length/status, version, inventory and tracking. |
| [adb.cpp:1240-1299,1327-1337,1390-1394](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/adb.cpp) and [client/adb_client.cpp:80-137](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/client/adb_client.cpp) | Serial/USB tport selection returns native uint64 ID, enabling verification before the daemon service. |
| [transport.cpp:601-695,1431-1455](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/transport.cpp) | Tracker framing and inventory fields/terminal transport ID. |
| [shell_protocol.h:44-103](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/shell_protocol.h), [shell_service_protocol.cpp:27-64](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/shell_service_protocol.cpp), [daemon/shell_service.cpp:774-790](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/daemon/shell_service.cpp) | Channel IDs, native 32-bit lengths and one-byte exit; supported hosts/target wire layout are little-endian. |
| [adb.h:70](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-14.0.0_r1/adb.h) | Server protocol version 41, independent of SDK release. |

Exact source bytes/SHA-256, bounded HTTPS origins, simulated A/B transcripts,
plan/code digests, tests, preservation checks and final Git status are recorded
privately under `build/m10/no-lifecycle-20261014/`. Earlier private inventories
and evidence remain in place. This work establishes no Sony runtime access,
accepted Linux boot, hardware function or original-board recovery.
