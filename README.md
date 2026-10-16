# NW-A306 Open

**One device. Two futures.** NW-A306 Open is an independent, open-source effort to put owner-controlled Linux on the Sony NW-A306 (`icx1301`). The shared foundation is a standalone ARM64 Linux system, with two envisioned experiences:

- **Rockbox in your pocket.** A dedicated, local-first digital audio player with physical controls, music-library navigation and no Android dependency.
- **Linux in your pocket.** A compact, general-purpose ARM64 handheld for compatible applications, terminal tools and experiments beyond music.

[Explore the interactive proposal](https://gblongiu.github.io/nw-a306-open/) · [Research roadmap](docs/roadmap.md)

**Current status:** Rockbox runs in a generic Android-free ARM64 Linux guest with tested audio, input and DRM/KMS output. Neither proposed experience has booted independently on the physical NW-A306. There is no Walkman installer, verified custom-boot procedure or demonstrated original-board restoration path. Sony boot acceptance, genuine board resources and safe hardware bring-up remain unresolved.

## Implementation

The prototype uses QEMU's generic `virt` machine, an Alpine Linux kernel,
a small BusyBox initramfs and an AArch64 glibc build of Rockbox's SDL application.
SDL supplies the existing ALSA audio backend. Test adapters connect synthetic
uinput/evdev events to Rockbox and copy software-rendered frames to virtio DRM
buffers for KMS page flips. The guest has no Android userspace, network, disk,
USB or physical-device passthrough.

Three patches against Rockbox revision
`afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09` address Opus end trimming/seeking,
hosted playback integration and decoder-error delivery to the UI. Build helpers
pin dependency versions and verify input hashes. Host tools inspect an observed
Sony UPG header profile, supplied EXT_CSD files and evidence metadata; separate
pure functions evaluate safety prerequisites and userspace dependency order.
These tools do not acquire data from a Walkman or deploy firmware.

## Verified capabilities

The recorded M3-M6 experiments establish the following within the pinned host
and virtual environment. Later research rechecked preserved evidence; it did
not repeat every runtime experiment.

| Capability | Recorded result |
| --- | --- |
| Codec regression | 38 checks pass on native Linux, AArch64/QEMU and native AddressSanitizer; leak detection disabled |
| Hosted application | Ten playback scenarios cover WAV/FLAC/Opus, controls, timestamp resume, short files, repeated playback and error handling |
| Linux audio | WAV/FLAC music samples match the reference exactly; Opus delivers 108,001 frames at 48 kHz with 68.79 dB reference SNR |
| Linux input | Synthetic taps and drag events traverse uinput/evdev into Rockbox; taps pause and resume playback |
| DRM/KMS | Changing 320x480 virtual scanout matches independent QEMU captures; unsupported mode is rejected |
| Rebuild consistency | Two forced builds reproduce all 42 application/codec hashes at the same configured prefix |

Exact commands, hashes, results and limits are in the
[codec report](docs/m3-codec-validation.md),
[application report](docs/m4-playback-validation.md),
[Linux prototype](docs/m5-linux-prototype.md) and
[display integration report](docs/m6-linux-display-integration.md).
These are software and virtual-device results, not physical audio measurements.

## Hardware barriers and unsupported behavior

Historical stock-device diagnostics identify QCS2290/`bengal`, Android 14,
firmware 3.06.00/build 27, locked/green boot state and A/B partition names.
FCC photos identify a SODAGREEN 1.03 certification board and component families;
equivalence to the owner's board is unverified. The
[evidence register](docs/feasibility.md#evidence-register) and
[hardware matrix](docs/hardware-matrix.md) distinguish these observations from
shared source, related-platform references and hypotheses.

A selected Sony boot/DT/AVB bundle, accepted independent-init path, matching
modules, firmware/calibration and dependable original-board restoration remain
missing. Sony audio, display, buttons/touch, storage, charging, thermal,
watchdog, suspend and shutdown behavior are unvalidated in a custom system.
An OEM-unlock setting or accessible fastboot interface does not establish
custom-image acceptance. Open kernel drivers do not supply proprietary DSP
firmware or Sony processing algorithms.

Chained Opus playback is unsupported. Forced Opus resampling failed the recorded
reference comparison; cross-rate gapless playback and ARM64 sanitizer operation
remain unresolved. There are no verified bit-perfect output, battery-life,
Bluetooth, Wi-Fi or Sony-effect compatibility results.

Hardware work requires an explicit operation plan, authentic matching inputs,
reviewed power/audio protection and a verified recovery path covering the
proposed failures. A generic Qualcomm or Xperia procedure is insufficient.

## Build and test

The file inspectors and unit tests use Python's standard library. Use Python
3.12 or later and run from the repository root:

```sh
python -m unittest discover -s tests -v
python tools/inspect_upg.py --help
python tools/inspect_extcsd.py --help
python tools/userspace_contract.py tools/m9-userspace-contract.json
```

The last command intentionally exits **1** because no readiness states were
supplied. It evaluates a dependency model and establishes no device readiness.

Full builds require x86-64 Linux (tested in Ubuntu 24.04 under WSL2), native GCC,
make, Perl, patch, tar, apt download metadata and dpkg-deb. VM packaging also
needs cpio and unsquashfs. The helpers unpack the pinned AArch64 toolchain and
QEMU packages privately. Python 3.12 and the tool versions in the reports are
the recorded build environment. Media generation requires FFmpeg with libopus
and FLAC; exact fixture hashes were obtained with the recorded FFmpeg 9.0.1
build and may differ with another encoder version.

Supply the pinned Rockbox source and SDL 2.30.0 archive; the source archives,
package cache and generated fixtures are excluded from this repository. Start
with [AArch64 reproduction](docs/m3-aarch64-bringup.md#reproduction), then the
[Linux build recipe](docs/m5-linux-prototype.md#reproduction) and
[DRM recipe](docs/m6-linux-display-integration.md#reproduction).
Use fresh private build directories. The recipes build a generic host prototype,
not a Sony firmware image. Package availability and hash verification are
prerequisites; helpers do not substitute newer dependencies silently.
Use simple absolute Linux paths without spaces or shell metacharacters; the
build helpers embed paths in generated Makefiles and compiler options.

## Repository structure

| Path | Contents |
| --- | --- |
| `docs/` | Feasibility, subsystem requirements, source provenance and historical test reports |
| `tools/` | File inspectors, dependency/policy models, pinned build inputs and Rockbox patches |
| `tests/` | Synthetic unit tests, media generators, regression validators and guest adapters |
| `LICENSE` | Complete GNU GPL v2 text; original project contributions use GPL-2.0-or-later |
| `COPYING` | Preserved GPL terms from the pinned Rockbox source |

Private references, firmware, raw evidence, build outputs, local instructions
and implementation planning are excluded by `.gitignore`.

## Technical documentation

- [Roadmap and research results](docs/roadmap.md)
- [Firmware container analysis](docs/m2-firmware-analysis.md)
- [Hardware integration contracts](docs/m7-hardware-convergence.md)
- [Boot/storage architecture](docs/m8-boot-storage-architecture.md)
- [Selected-artifact inventory](docs/m9-boot-artifact-inventory.md)
- [Independent-userspace contract](docs/m9-stock-kernel-userspace.md)
- [Authentication boundaries](docs/m9-authentication-boundaries.md)
- [Recovery requirements](docs/m9-recovery-readiness.md)

## Licensing and contributions

Original NW-A306 Open code, tests, tools, configuration and documentation are
licensed under GNU GPL version 2 or, at your option, any later version
(`GPL-2.0-or-later`). See [LICENSE](LICENSE) and
[licensing and attribution](docs/licensing.md). Rockbox-derived changes retain
their existing GPL-2.0-or-later terms. Third-party components and quoted material
retain their own notices and terms; proprietary Sony artifacts are excluded.

Contributions should address a documented engineering gap, include relevant
regressions and distinguish source findings from runtime verification. Preserve
third-party notices and provenance. Firmware, proprietary Sony code, private
recordings, device identifiers and raw diagnostic evidence do not belong in
contributions.
