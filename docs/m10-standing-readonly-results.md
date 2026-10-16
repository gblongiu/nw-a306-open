# M10 standing enforcement and physical U1/H1 results

2026-10-14. The owner approved fixed U1/H1 and minimal implementation. The
approved policy document remains unchanged at SHA-256
`4ebcc03041fcf1987eec2a0321848ce3937d86908372974595c0051cc629776a`;
its proposal-time status is historical. No APK acquisition or boot is approved.

## Implementation and actual checks

`tools/standing_readonly.py` defines exact U1/H1 registries, validates bounded
absolute APK-path lines and admits only a policy/version/profile/plan-bound
grant. Paths are data, never executed or automatically opened. Empty, malformed,
duplicate, control-character, traversal, excessive-count and oversized output
fails. Adapter stage selection reuses the existing watcher, guards, frames,
deadlines and private capture; there is no arbitrary operation selector.

An exclusive lease and append-only hash-linked journal prevent concurrent
sessions and block unfinished/corrupt attempts. Results bind capture-manifest
hashes; altered previous manifests block admission. At most two distinct plans
run per turn. A failure ends the turn and quarantines its operation across
turns, disabling any plan containing it. No retry, reset, stale-lock removal or
quarantine-clearing API exists. Trusted host operation and genuine human consent
remain prerequisites; approval files do not authenticate consent themselves.

Eleven new fake-transport tests cover exact scopes/caps/bookends, package-path
validation, both complete plans, all six H1 denial positions, missing/false/stale
grants, identity/transport failures, journal/lock/crash stops, limits, quarantine,
changed prior manifests and inert CLI. Real network/process constructors are
blocked in fixtures. Full discovery: **Windows 122 tests, 121 passed, one
symlink-permission skip; WSL Ubuntu 24.04, 122 passed**. Original replay/transport
modules and B2 registry were unchanged. Old source-bound approvals remain
historical, not reusable approvals for the edited adapter.

## Physical observations and evidence integrity

Before each session, host checks matched the existing loopback server's listener
owner, process creation, native path and pinned SHA-256. No executable/lifecycle/
reconnect operation was used. The latest owner confirmation was reused under
the continuous-connection rule, with no known intervening activity. Live guards
required the unchanged private binding before shell reads; registry/caps matched
the approved proposal. Each plan ran once.

| Plan digest | Physical result |
| --- | --- |
| U1 `1adfbe0dc554a1029681366d4191839bf6ecc139969586830d5c2e6c65ea61e7` | **Complete:** 23 valid observations, including ending identities; 118 connections, 23,566 wire bytes, about 2.03 s. |
| H1 `2b2be9eba24b83ca150e9a955621330667ddd14c11da640c3ffd54fd843a7177` | **Incomplete:** eleven identities valid, twelve observations attempted, sixteen unattempted; 61 connections, 11,910 wire bytes, about 0.91 s. |

**Demonstrated on physical NW-A306 hardware:** U1 returned one registered updater
APK location under `system_ext`, basename `automagic.apk`, for
`com.sony.walkman.systemupdater`. Exact path stays private. No APK bytes were
read. This establishes registration/path metadata, not content, signer or behavior.

H1's first inventory,
`/system/bin/toybox head -c 65537 /proc/asound/cards`, returned exit 1, empty
stdout and permission-denied stderr. DAC/SELinux/traversal cause is **unknown**.
No later PCM/input/graphics/power/partition-link observation or ending identity
check ran. `sound-cards` is quarantined; H1 is disabled under unchanged v1.
No retry, substitute read, escalation or further device action followed.

Independent offline validation passed raw/decoded hashes/counts, exact transmitted
services/close-stdin, host replies/binding, atomic selection, frame boundaries and
exits, stream agreement, successful payloads, deadlines/caps and journal/manifest
agreement. All 395 prior physical/provenance/authorization/preparation files were
rechecked unchanged. Private evidence: `build/m10/device-u1-20261014-01/`,
`device-h1-20261014-01/`, `authorizations/` and
`standing-implementation-20261014-01/`. No identifiers were published.

## Updater analysis and the next technical dependency

The lead is now one registered code location. Scoped local filename/text checks
did not locate `automagic.apk`; the four supplied audio APKs are not this
artifact. This does not establish absence inside every opaque archive. No new
decoder or proprietary binary was downloaded, executed or publicly imported.

Historical M2 F5 uses the same `com.sony.walkman.systemupdater.util` namespace
in `UpdateDataDecipher.java` and `UpdateProperties.java`; exact pinned revision,
locators and hashes remain in [M2's source register](m2-firmware-analysis.md#source-locators).
Reported A100/ZX500 framing/cipher behavior is a **plausible comparison**, not
A306 equivalence. Neither this namespace nor `automagic.apk` proves those classes
exist in the actual binary. No old decoder or rejected digest guess was rerun.

The genuine NWWM transport remains opaque. Static analysis of the actual updater
could test its framing/length/digest/cipher hypotheses and identify authenticated
ranges, version/variant checks, full/delta members and recovery/update-engine
handoff. Inspect bounded ZIP/DEX/native members; never execute the installer.
APK signing, UPG decryption, OTA signing and loader/DT/AVB acceptance are separate
boundaries. Vendor-only acceptance could yield useful authentic images without
supporting custom execution. A normal update API cannot establish independent
same-board restoration or same-version reinstall.

Highest-value next task: acquire and statically analyze **only the registered
updater APK**. A private proposal at
`standing-implementation-20261014-01/updater-acquisition-proposal.json` records
the exact path/commands, regular-file/16 MiB size gate, byte/deadline limits,
risks, recovery uncertainty and expected decisions. It is not executable:
separate acquisition approval and offline-tested implementation are required.
The standing adapter retains its 2 MiB metadata-session limit and permits no
content transfer. No new operation is requested to complete a checklist.

Vendor kernel/DT/firmware plus independent Linux init/Rockbox remains the preferred
integration candidate, conditional on accepted delivery. No custom boot or
original-board restoration is demonstrated. Loader policy, selected boot/DT/AVB,
firmware/calibration and power/thermal/watchdog ownership remain unresolved.
U1 retains standing approval for justified future use; H1's denial needs review
and no acknowledgment alone clears quarantine. M10 remains open.
