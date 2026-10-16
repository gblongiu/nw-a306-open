# M10 KC1: running stock kernel disables legacy kexec

2026-10-15. **KC1 executed once, completed successfully and passed independent
offline capture validation.** The configuration acquired from the physical
NW-A306 explicitly contains `# CONFIG_KEXEC is not set`. Ordinary legacy
stock-kernel kexec is closed as an immediate execution strategy for this build.
M10's broader independent-Linux objective remains open.

## KC1 execution

The owner explicitly authorized the unchanged [KC1 procedure](m10-kernel-config-authorization.md)
and confirmed the same personally owned player was responsive in stock Android,
debugging already authorized and idle. All 24 frozen execution-bundle inputs,
the original private profile and plan digest were checked before execution.
The plan remained:
`c50ef90a2555c3cb809ad1018b702f67854f765a4134f9df60151dd4ede36d62`.
The proposal remains preserved as false; separate actual approval/readiness
records bind this authorization. The preparation document's pending status is
historical and was not edited after the code/plan freeze.

The prepared `run_kc1_once.py --run-approved` runner was invoked exactly once.
Host preflight verified the existing trusted ADB listener/process/image and
healthy original physical USB endpoint. KC1 resolved the current transport ID
once for the original serial, required matching USB selection and retained the
held tracker plus atomic serial/ID and before/after inventory/features guards.
All original profile values remained unchanged.

All eleven starting identities passed. The sole new acquisition command was:

```text
/system/bin/toybox head -c 262145 /proc/config.gz
```

It ran once, returned exit **0**, produced **33,525 stdout bytes** and no stderr,
and completed in approximately **0.084 seconds**. All eleven ending identities
and their transport guards passed. Host postflight also passed. No failure,
overflow, retry, substitute command or additional characterization occurred.

The guarded ADB session took approximately **1.917 seconds**, with 23 shell
observations, 119 connections and 57,154 total logged wire bytes. Host checks
are outside that session duration. The same original device identity and USB
endpoint were preserved; the transport ID was only session-local.

The player was responsive to all ending Android shell checks. No new screen,
touch, playback or comprehensive peripheral-health test was performed. No
claim about the player's state after the last observed response is made.

## Running kernel configuration

The captured header is `Linux/arm64 4.19.157 Kernel Configuration`.
The following are exact observations from the decoded configuration:

| Symbol | Observed text / absence | Decoded line |
| --- | --- | --- |
| `CONFIG_KEXEC` | `# CONFIG_KEXEC is not set` | 391 |
| `CONFIG_KEXEC_FILE` | No assignment or explicit unset entry present | — |
| `CONFIG_IKCONFIG` | `CONFIG_IKCONFIG=y` | 111 |
| `CONFIG_IKCONFIG_PROC` | `CONFIG_IKCONFIG_PROC=y` | 112 |

The configuration is **149,691 bytes** after bounded decompression. The missing
`KEXEC_FILE` symbol is not an observed disabled setting. Published Sony ARM64
source lacks its applicable implementation, but this capture alone does not
establish a runtime file-loader capability or prove a syscall's behavior.

Private physical evidence is under
`build/m10/device-kc1-20261015-01/`: `11-stdout.bin` is the exact gzip capture;
`running.config` is its validated decoded form; `manifest.json` and all raw
wire/decoded streams remain preserved. No private device identifiers or raw
configuration were added to public files.

| Artifact | SHA-256 |
| --- | --- |
| Raw gzip, 33,525 bytes | `11a92dae8ea8b3f9f624dd7c4a6b023cf8c887d2c4b69d74779158f454f16aae` |
| Decoded config, 149,691 bytes | `975ec08ad647c0991e637d93ba4a58384403611df79b1709701fe7e84cc65ade` |
| Original capture manifest | `c1fc28c074638703c458df6d33fae257527d9b744ae1b12352da33ab36b61cf1` |

## Validation and evidence strength

The unchanged tested host implementation accepted exactly one complete gzip
member, valid CRC/ISIZE, no trailing data and valid bounded ARM64 configuration
syntax. An independent offline validator then checked:

- All **284 raw and decoded stream files** against manifest lengths and hashes.
- Exact transmitted services, their order, closed stdin, shell-v2 frame
  boundaries, zero exits, empty stderr and equality with saved decoded output.
- Exactly one configuration read, eleven identities before and after, all
  inventory/features/atomic binding responses, tracker continuity and USB ID.
- Original profile immutability, code/plan/approval binding, session/read limits
  and successful before/after host receipts.
- A separate bounded gzip reader, explicit trailer CRC32 and size arithmetic,
  decoded SHA-256, exact symbol lines and agreement with the capture inspector.

All checks passed. Real socket and process constructors were blocked during
offline validation. The original acquisition manifest remains unmodified,
including its conservative `physical_evidence:false`; the separate validation
record establishes the reviewed physical-session finding. These are controlled
observations of the owner's stock device, not cryptographic hardware attestation.

Execution/validation metadata, the actual owner authorization, runner exit/output,
before/after preservation checks and work-product inventories are under
`build/m10/kernel-config-execution-20261015-01/`. Actual approval/readiness,
attempt reservation, host receipts and runner summary are alongside the frozen
preparation bundle in `build/m10/kernel-config-preparation-20261015-01/`.

## Linux execution implications

**Confirmed observation:** the running player's exported configuration explicitly
disables `CONFIG_KEXEC`. This corroborates the published configuration result;
it does not establish that every configuration setting or kernel byte matches
the published source.

**Engineering conclusion:** ordinary legacy `kexec_load` is unavailable through
this compiled stock kernel. In the applicable Sony source,
`kernel/msm-4.19/kernel/Makefile:72–74` and
`arch/arm64/kernel/Makefile:57` gate the kexec implementation, while
`kernel/sys_ni.c:148–150` supplies the unimplemented fallback. Gaining Android
userspace privileges alone cannot create an omitted compiled kernel facility.
No syscall probe or privileged operation was needed or performed to make this
configuration-based conclusion.

Close this ordinary stock-kernel handoff hypothesis unless new evidence changes
the installed-kernel premise. The separately preserved minimal ARM64 initramfs,
PID 1 source/binary and QEMU validation remain useful future bring-up artifacts;
they were not rebuilt or deployed here. Independent Linux execution and cold
boot on the Sony remain unproved.

## Next engineering priority

The strongest next task is **obtain authentic Sony build-specific temporary-boot
acceptance evidence and trace the actual `boot` path**: command registration,
locked-state gate, authenticated coverage of kernel/initramfs/DT/command line,
delegated checks and any persistent changes before rejection or handoff.
An applicable authentic ABL artifact or equivalent authoritative Sony policy
evidence can supply this; a complete loader dump is not universally required.

[M10's existing comparison](m10-boot-execution-analysis.md) already shows why
generic Qualcomm behavior cannot answer that question. Actual Sony policy and
artifact acquisition remain blockers. Do not reopen failed NWWM guesses,
repeat generic loader analysis, or infer owner-image acceptance from N2's
bootloader-fastboot classification. No additional physical experiment is
recommended or authorized by KC1's completion.

## Final state

The only public project file added in this execution turn is this report.
No existing source, test, authorization-proposal document or roadmap content
was modified. Private additions are fully enumerated and hashed in the execution
directory's `work-products.json`; the preserved baseline and final Git status
are recorded there. All pre-existing Git changes were retained, with this report
as the sole additional untracked public file. Nothing was staged or committed;
no Git history or remote operation occurred.

No regression rerun was needed: all frozen implementation/test inputs matched
the validated preparation bundle (17 KC1 tests on Windows and WSL; full Windows
suite 249 passes and four environment skips). This turn performed the live
guarded capture and independent offline validation described above.
`git diff --check` passed. No boot, reboot, root, kernel load, partition access,
upload, settings change or contact with Sony occurred. KC1 is complete; further
device work requires a separate scope and authorization.
