# M10 N1: physical fastboot responses and Android return

2026-10-15. The owner explicitly authorized the existing N1 scope with
`version-bootloader` before `is-userspace`. Fresh physical supervision, battery,
backup and normal-idle prerequisites were confirmed. The experiment **stopped
at the empty bootloader-version value**, as required. It did not complete the
full diagnostic schedule. No independent Linux boot or firmware restoration is
claimed; M10 remains open.

Subsequent protocol reconciliation: **the version value is unavailable, not
evidence of a malfunction**. AOSP's pinned fastboot specification documents
legacy empty OKAY replies for unknown variables. N1 captured native-client
output and exit status, not raw USB status packets, so that behavior is a
compatible explanation, not a proven diagnosis of Sony's implementation or
loader age. An intentionally unset version also fits. The original N1 parser
stop, raw bytes and successful observations are preserved unchanged. See
[N2's minimal proposal and acceptance-investigation decision](m10-n2-authorization.md).

## What ran on the physical Sony

Classification: **demonstrated on physical NW-A306 hardware**, with exact private
serial binding, trusted existing ADB server, atomic transport selection, matching
physical USB port, owner supervision and photographs. This is fresh captured
evidence, distinct from the earlier historical owner report.

The eleven approved Android identity guards passed. Exactly one serial-bound
`reboot:bootloader` service was acknowledged, and the same unit re-enumerated on
the same USB port within the approved arrival window. Neither adb.exe nor an
ADB server lifecycle command ran.

The owner's photograph shows `FastBoot Mode`, product `icx1301`, variant
`QCS EMMC`, secure boot `yes`, state `locked`, and blank bootloader/baseband
version fields. The private serial matches the approved binding. These are
bootloader-screen reports, not direct chip identification, a dump of the trust
chain or proof of an implemented RAM-boot command.

All six attempted native invocations exited **0**. Raw stdout/stderr were saved
independently before interpretation. Serial and USB identifiers remain private.

| Invocation, in actual order | Captured response | stdout/stderr bytes | Result |
| --- | --- | --- | --- |
| `fastboot devices -l` | One target matching the approved serial | 33 / 0 | Valid enumeration |
| `fastboot -s S getvar product` | `product: icx1301` | 0 / 48 | Identity guard passed |
| `fastboot -s S getvar unlocked` | `unlocked: no` | 0 / 44 | Security guard passed |
| `fastboot -s S getvar secure` | `secure: yes` | 0 / 43 | Security guard passed |
| `fastboot -s S getvar current-slot` | `current-slot: b` | 0 / 47 | Slot guard passed |
| `fastboot -s S getvar version-bootloader` | Empty value | 0 / 52 | Output validation stopped the session |
| `fastboot -s S getvar is-userspace` | **Not attempted** | None | Excluded after the stop |

`S` denotes the private approved serial. Successful variable output was on
stderr, including native timing lines. The last complete stderr, with CRLF line
endings preserved privately, was:

```text
version-bootloader:
Finished. Total time: 0.001s
```

The first raw line contains one space after the colon before CRLF.

[`fastboot/README.md:121-130`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/README.md#121)
describes the empty-success compatibility case. The reference native client
also accepts an OKAY with an empty payload
([`fastboot_driver.cpp:495-497`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/fastboot_driver.cpp#495))
and prints a successful named empty value
([`fastboot.cpp:953-963`](https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/fastboot/fastboot.cpp#953)).
This is reference-source behavior; the installed host binary is hash-bound but
not established as an exact build of these sources. The observed empty value
should be recorded as unavailable regardless of why Sony returned it.

The actual stop string is `unexpected fastboot response line`: the conservative
validator rejects the empty named value. This was **not** a permission denial,
`unknown command`, transport failure or nonzero native exit. No parser change,
retry, substitute query or continuation was made after observing it.

## Return and preservation

Following the requested approved single Power-only return procedure, the owner
reported **"Back on"** and supplied photographs showing the Android home screen.
Classification: **physical screen evidence and owner-reported return**. The
photos establish Android UI availability; exact button-hold duration and
comprehensive responsiveness/peripheral health were not measured.

No `fastboot reboot`, other boot mode, menu selection, unlock, erase, partition
operation, image transfer or unrelated OEM command ran. In accordance with the
failure branch, **no post-return ADB/fastboot query ran**. Android return is not
being claimed from a new ADB identity check. The original expected profile was
not rewritten, and all previous denied operations remain untouched.

Raw private capture: ignored `build/m10/device-n1-20261015-01/`. It includes
pre-entry wire/identity records, the exact native argument arrays and separate
streams, approvals/plan, and the original owner photographs. Associated host
snapshots, source bindings, test logs, failure validation and the complete
private inventory are in ignored `build/m10/n1-integration-20261015-01/`.
Raw manifests retain their original conservative classification fields; separate
validation records explain the physical-evidence basis.

## Implementation and actual verification

- `tools/fastboot_n1.py`: fixed, separately supervised entry/query/return phases;
  no default execution, retries or software-return path. Query order matches the
  owner's sole requested change. Failed diagnostics prohibit return queries.
- `tests/test_fastboot_n1.py`: nineteen tests cover fixed order, stale approval,
  missing readiness, wrong transport/identity, host changes, entry failure,
  successful stderr, strict caps, unknown/empty output, stop behavior and
  session-local post-return transport rebinding. Two tests use known local
  Python children for actual pipe overflow and timeout/reaping; Android host
  tools never run in tests.
- `tools/adb_readonly.py`: the existing stream reader honors the plan's strict
  cap flag for N1 as it already did for C1. Other stage behavior is unchanged.
- `docs/m10-fastboot-reconciliation.md`: approved order and result link.
- `docs/m10-boot-feasibility.md`: fresh physical-result link.
- `docs/m10-n1-results.md`: this report.

The full suite ran **183 tests: 182 passed, one existing Windows symlink skip**.
All nineteen new N1 tests passed. Saved capture validation verified **156 stream
files**, lengths/SHA-256, plan/profile/approval binding, identity wire decoding,
one entry request, exact six native invocations, limits and omission of all
post-failure requests. The pre-entry wire capture contains 61 connections and
11,804 bytes. Native invocations took approximately 69-87 ms each, below five
seconds; every captured stream remained below 4,096 bytes. Earlier evidence and
pre-edit source/report bytes remain preserved. Nothing was staged or committed.

## What this establishes for independent Linux

Fastboot access, the reported locked/secure state and the intact-system physical
return now have fresh project evidence. A loader-version string was not exposed
by this exact query. An empty response does not identify the loader, prove the
command is absent, or exhaust other artifact-based identification.

The screen is consistent with a Qualcomm-style bootloader UI. Nevertheless,
`is-userspace` was not queried, so that protocol discriminator remains unknown;
do not promote visual similarity to traced loader architecture. There is no
accepted independent kernel, ramdisk, DT or boot-image experiment. Secure/locked
reports constrain the hypothesis but do not reveal every acceptance decision.

The strongest execution hypothesis remains a supported temporary path admitting
an independent payload under the actual Sony trust policy. Neither that path
nor unlocking is demonstrated. This intact-stock return is availability
evidence, not recovery after damaged images or unique-state loss.

The next narrowly useful interface observation is `is-userspace`, which was
never attempted. A future session requires review of this failure and a fixed
scope that does not require a nonempty version guard. It is not a continuation
or automatic retry of N1. Authentic loader/boot/AVB evidence, payload acceptance
and an accepted same-board repair mechanism remain separate unresolved gates.
