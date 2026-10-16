# M10 KC1: bounded running-kernel configuration capture

2026-10-15. **Prepared and tested offline; not authorized or executed.**
This proposes one new unprivileged content read, surrounded by the existing
identity checks. It authorizes no kexec, privilege change, kernel setting,
boot-mode transition, partition operation or retry. M10 remains open.

## Why this read

The independent kernel-handoff investigation resolved Sony's published
`arch/arm64/configs/publishing/sony_dmp_android_defconfig` using Sony's native
Kconfig parser: `CONFIG_KEXEC=n`; explicitly enabling it succeeds in a positive
control. The applicable ARM64 source does not supply `KEXEC_FILE` support.
These are published-source findings, not the running player's configuration.

The same defconfig selects `IKCONFIG` and `IKCONFIG_PROC` at lines 18–19.
Sony `kernel/msm-4.19/kernel/configs.c:77–84` creates `/proc/config.gz` with
ordinary read permissions. Android 14 reference
[`private/shell.te:17–18`](https://android.googlesource.com/platform/system/sepolicy/+/refs/tags/android-14.0.0_r1/private/shell.te#17)
allows shell to read the corresponding label; `private/genfs_contexts:9`
assigns it to this path. Sony's actual selected configuration and policy may
differ. A denial establishes neither absence of kexec nor a broken device.

The report, selected source, native parser and generated configurations,
QEMU-only PID 1 source/binary/initramfs, logs, input package archives and
hashes are preserved under
`build/m10/kernel-config-preparation-20261015-01/`.
The private preservation manifest records 3,440 verified copied files, 11,894,320 bytes,
and the original inventory hash. Unpacked dependency files and Python caches
were excluded. Preserved scripts/logs retain their historical temporary paths;
the new implementation and checks use the preserved files, not temporary input.
All this storage is ignored by the existing `build/` rule. It is not a public
source import or a Sony firmware build.

## Exact proposed device sequence

Once each, in this order, require all eleven starting identity responses to
match the unchanged original private profile:

```text
/system/bin/id -u
/system/bin/id -Z
/system/bin/getenforce
/system/bin/getprop ro.product.model
/system/bin/getprop ro.product.device
/system/bin/getprop ro.board.platform
/system/bin/getprop ro.soc.model
/system/bin/getprop ro.build.version.incremental
/system/bin/getprop ro.boot.slot_suffix
/system/bin/getprop ro.boot.verifiedbootstate
/system/bin/getprop ro.boot.flash.locked
```

Then perform **exactly one** new read:

```text
/system/bin/toybox head -c 262145 /proc/config.gz
```

Only if capture and validation succeed, repeat the same eleven identity checks
in the same order. A successful session therefore has **23 shell commands**,
of which one reads configuration bytes. No `ls`, `cat`, `uname`, capability
probe, alternative path, helper upload or privilege attempt is included.
Any failure stops immediately; no ending checks run after a failed operation.

Use the existing trusted loopback ADB server at `127.0.0.1:5037`; do not launch
adb.exe or start/stop/reconnect the server. Reuse the established host-only checks
of listener owner, process creation, executable path/hash, physical USB root,
healthy state and connection location. A changed server or ambiguous device is
a stop, not permission to repair transport.

KC1 explicitly adopts P1's reviewed binding rule: resolve one initial current
transport ID for exactly the original serial and `icx1301`, confirm USB selection,
and keep all original identity values immutable. Track the connection throughout.
Every shell operation retains before/after inventory/features checks and serial
selection with returned-ID verification on the same connection as the shell
request. No later rediscovery or rebinding. The transport ID is session-local;
the original profile is preserved. These are continuity controls, not attestation.

Send through `shell,v2,raw` without a PTY and close stdin. Keep binary stdout,
stderr and exit status separate. Every request is fixed by the plan; no shell
command construction from captured data.

## Bounds, validation and interpretation

- Accept at most **262,144 compressed bytes**. The requested 262,145th byte is
  an overflow sentinel, never accepted as configuration. The inherited adapter
  stops on overflow and preserves at most the cap plus one decoded byte; an
  oversized frame declaration is rejected before consuming its payload.
- Five-second deadline for the read connection; 180-second session deadline;
  2 MiB combined wire budget; 4,096 shell frames per operation. Identity streams
  retain their 4 KiB bounds. No timeout retries.
- Host-side zlib decoding permits one gzip member and at most **2 MiB expanded
  data**, with one bounded overflow byte. Require end-of-stream and valid CRC32
  and ISIZE; reject truncation, concatenated members and any trailing bytes.
  No unbounded decompression or flush operation.
- Require ASCII, newline-terminated generated ARM64 configuration text, valid
  configuration assignments and unique symbols. Inspect `CONFIG_KEXEC`,
  `CONFIG_KEXEC_FILE`, `CONFIG_IKCONFIG` and `CONFIG_IKCONFIG_PROC`. Missing
  symbols are `not_present`, never silently interpreted as disabled. Unsupported
  formatting is inconclusive and preserved for offline review, not retried.
- Preserve raw wire/decoded files and SHA-256/count metadata, even on failure.
  Only after all ending guards succeed does the manifest promote `11-stdout.bin`
  as the configuration artifact with its parsed result and expanded hash.
  The adapter always leaves `physical_evidence:false` pending independent review.

An identity-bound, validated `CONFIG_KEXEC=n` ends investment in ordinary
stock-kernel legacy kexec and prioritizes Sony's actual bootloader acceptance
and other credible execution paths. `CONFIG_KEXEC=y` establishes only a build
setting: assess legitimate privilege/policy, memory/DT, CPU shutdown, watchdog,
display, charging and recovery prerequisites before proposing a handoff.
An unexpected `KEXEC_FILE=y` must be reconciled with the published source;
it does not prove a callable mechanism. No configuration setting alone proves
accepted kernel images or independent Linux execution.

## Offline implementation and checks

`tools/acquire_kernel_config.py` is a small subclass of the existing capture
session, with a fixed registry, bounded validator and explicit approval gate.
Existing ADB, standing-authorization and P1 modules are unchanged. Its default
CLI only prints the plan; unapproved arguments never connect. The exact approved
output directory is created exclusively, so the same approval cannot be reused
after a capture attempt. Approval binds stage, full plan/code hashes, immutable
profile and output path. Approval JSON does not establish human consent.

`tests/test_acquire_kernel_config.py` exercises real framing logic against fake
sockets, with real socket and process constructors blocked. The 17 tests cover
successful capture and hashes; enabled/disabled/unknown settings; missing files
and permission denial; truncated/CRC/ISIZE failures; malformed configuration;
trailing/multiple gzip members; exact compressed and expanded limits; sentinel,
split-frame and oversized-header overflow; initial/ending identity changes;
one-time ID binding and subsequent mismatch; tracker loss; partial data;
deadlines and session bytes; false/stale approvals, reuse and inert CLI; and a
tracker-loss race during final watcher shutdown that must block promotion.

Windows full discovery: **253 tests, 249 passed, four skipped** (one host symlink
restriction, three optional Capstone tests). All 17 KC1 tests passed on Windows
and WSL. All three preserved Sony Kconfig cases were checked with the new
validator; a saved synthetic session verifies exact commands and raw/decoded
hashes. Final logs are `full-tests-windows-final.txt` and
`kc1-tests-wsl-final.txt` in the preparation directory.
No physical configuration bytes or runtime capability were acquired.

## Approval record and execution procedure

Private preparation directory:
`build/m10/kernel-config-preparation-20261015-01/`.
`reviewed-plan.json` contains the complete fixed plan and code hashes.
`approval-proposal.json` has `approved:false`, stage `KC1`, canonical plan and
original-profile SHA-256 values, and the exact fresh destination
`build/m10/device-kc1-20261015-01`. `owner-readiness-proposal.json` is also false.
`execution-bundle.json` binds the wrapper, host guard, dependencies, original
profile/host evidence, proposal and offline validation records.

1. Obtain direct human authorization for this exact KC1 sequence, including
   current-ID binding and the 22 identity checks. Confirm the same player is
   present, responsive in stock Android, already authorized for debugging and
   idle without an update or transfer. Do not reuse old readiness assertions.
2. Only after that response, create fresh `approval.json` matching the proposal
   except `approved:true`, and `owner-readiness.json` containing the actual
   authorization text and current UTC timestamp. Preserve the false proposals.
   The wrapper requires readiness no older than 15 minutes. No approved records
   or live-attempt reservation exist at this preparation checkpoint.
3. Recheck the frozen bundle and ensure the output and attempt reservation are
   absent. On Windows, invoke the prepared wrapper **once**:

   ```powershell
   python build/m10/kernel-config-preparation-20261015-01/run_kc1_once.py --run-approved
   ```

   This is a future execution instruction, not a command run during preparation.
   Default invocation is inert. The wrapper reserves the attempt before host
   preflight; even preflight failure requires review and does not permit retry.
   It uses the existing host checks, then the guarded capture, then host-only
   continuity checks. No further device request follows capture failure.
4. Independently validate wire framing, emitted services, record hashes, exact
   scope, original/session identity binding and host continuity. Reparse the
   captured file offline and reconcile the manifest before reporting a physical
   finding. Do not treat the adapter's result alone as attestation.

Risk classification: **low, bounded read-only characterization**, with private
build information captured. Any denial, unexpected identity, transport loss,
overflow, invalid gzip/text or uncertain host continuity ends the experiment.
Preserve all partial evidence; no fallback read, mode change or automatic repair.
No bootloader/firmware recovery claim is made or required for this read.

Authorization remains pending because the user's assignment explicitly requires
separate permission for the device read, and `AGENTS.md` requires explicit
approval for device-facing commands. The ultimate execution objective remains
independent Linux for Rockbox and a general-purpose handheld environment.
