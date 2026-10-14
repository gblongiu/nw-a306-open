# M3 AArch64 Linux execution and hosted Rockbox

Date: 2026-10-13. **Rockbox code now executes as AArch64 Linux binaries under
QEMU user mode.** Corrected Warble passes WAV, FLAC and Opus regression checks;
the SDL hosted Rockbox application also starts, renders its UI, handles injected
keys and exits through its normal shutdown path. This is generic Linux
userspace validation, with no NW-A306 hardware, kernel or boot validation.

## Validation levels

| Level | Demonstrated result / boundary |
| --- | --- |
| AArch64 compilation | ELF64 little-endian ARM AArch64 executable and shared codec objects inspected with `file`/`readelf` |
| AArch64 execution | Actual binaries run through explicit `qemu-aarch64-static -L <private sysroot>` |
| Rockbox codec execution | 38/38 checks pass, including real dynamically loaded WAV/FLAC/Opus decoders and seeking/error paths |
| Hosted Rockbox application | Existing `sdlapp` target built with codecs/plugins; startup, software-rendered UI, navigation events and clean shutdown tested |
| Generic Linux integration | Glibc loading, files, SDL software video/dummy audio, threads and application event loop exercised in user mode |
| Not demonstrated | Hosted application audio playback, plugin execution, ALSA/DRM integration, bootable rootfs/init, target kernel/modules, target ASan instrumentation |
| NW-A306 compatibility | **Unverified for every hardware subsystem and the Sony boot/recovery chain** |

The SDL application uses an existing Linux-hosted Rockbox target. Its generic C
paths are selected by
configure's `arch=none` for SDL; the compiler still produces actual AArch64
instructions. Warble configures `arch=arm64`. Neither choice proves Sony driver
integration.

## Toolchain, ABI and isolation

Existing Ubuntu 24.04 WSL2 x86-64, GNU Make 4.3, Perl 5.38.2 and Python 3.12
were retained. Ubuntu packages were **downloaded and unpacked privately**, not
installed. Only the AArch64 QEMU executable was selected from its package;
other emulator binaries, package scripts and binfmt registration were not used.

| Input | Recorded version |
| --- | --- |
| Rockbox | R `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09` plus the project patch |
| GCC cross compiler | 13.3.0, package `13.3.0-6ubuntu2~24.04.1cross1` |
| AArch64 binutils | `2.42-4ubuntu2.10` |
| Target glibc / headers | `2.39-0ubuntu8cross1` |
| Linux userspace headers | `6.8.0-25.25cross1`; not the target Sony kernel |
| Target GCC runtime / ASan packages | `14.2.0-4ubuntu2~24.04.1cross1`; exact entries in lock file |
| QEMU user mode | `1:8.2.2+ds-0ubuntu1.18` |
| SDL | 2.30.0, reused hash-verified M2 source archive |
| Additional host packaging tool | `zip 3.0-13ubuntu0.2`, needed by the real hosted build's voice-string/assets packaging |

[`m3-toolchain.lock.json`](../tools/m3-toolchain.lock.json) records all 15 package
versions, original filenames, lengths and SHA-256 values. Acquisition hashes
matched the configured Ubuntu package metadata; the build helper verifies the
locked hashes before unpacking. It never silently chooses newer versions if
the recorded packages disappear from a mirror.

Private directories are `~/.cache/nwa306-open/m3/` and the independent fresh
`m3-repro/` workspace. Windows corpus, logs and integrity records are under
ignored `build/m3/`; the pre-edit baseline is separately preserved. No system
package, Windows driver, host boot setting or device interface was changed.

The binaries use the AArch64 LP64 ABI and `/lib/ld-linux-aarch64.so.1`.
Dynamic dependencies include `libm.so.6`, `libc.so.6` and the loader; the actual
target loader resolves them inside the supplied sysroot. Warble's symbol-version
requirements include **GLIBC_2.38**. The tested rootfs therefore cannot simply
substitute an older libc or Android Bionic. Rebuilding against a deliberately
chosen older sysroot is a separate compatibility test. Codec modules must use
the same target/API/libc choices as their application.

SDL is statically linked. Codec-harness SDL has video/audio disabled. The hosted
build enables software video/audio while disabling X11, Wayland, KMSDRM,
OpenGL/Vulkan and physical ALSA/PulseAudio/PipeWire/JACK/sndio/OSS backends.
Runtime uses `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`; no physical
audio or display backend is accessed. This does not validate real PCM output.

## Builds, execution and reproducibility

The [codec report](m3-codec-validation.md) records the complete corpus and
before/after results. Native, AArch64 and native-ASan final runs each pass 38/38;
all 30 valid/seek AArch64 PCM files match native hashes. Independent preparation,
patch application, SDL compilation and AArch64 compilation in `m3-repro/` also
produced a runnable harness passing 38/38 trial and final checks.

| Original private workspace artifact | SHA-256 |
| --- | --- |
| Native `warble.ipodvideo` | `479d7eff82c895466e12a8b62030f17cab97c43709c30d20e6597b76b5f1665b` |
| AArch64 `warble.ipodvideo` | `1561f6460ccdac221b4765a7a45ad4804d7061fa818a1441ec4080d79ac814b2` |
| AArch64 `opus.codec` | `c73a3da89f6ee05c0c54e56c80b32eef98fc29aace3b88d6772918d635f3f595` |
| AArch64 `flac.codec` | `7266ba5952f5a265e14e95471e5ecd7cc7a5e249620241cbdc2dd2b79dfe335b` |
| AArch64 `wav.codec` | `1f71de9af839252082d14c2f673e58e3c3a38990efc828e1f1cb761f1d65d07b` |
| Fresh-workspace hosted `rockbox` without smoke hooks | `a08b4d8f23511d54784f2efbfab06dd4b93f94c0c43f549438996321fabad608` |
| Fresh-workspace hosted `rockbox.smoke` | `7d62f97fa127a2b326df7b95c532df04eeaeac399b20d8d22e5e63245af7b6a7` |

Forced same-directory rebuilds reproduce all 41 Warble/codec hashes on each
architecture. The fresh workspace changes embedded paths, so its binary hashes
differ; decoded results still pass. Reproducibility demonstrated here means
same-environment binary rebuild consistency plus a functioning fresh-workspace
recipe, not interchangeable binaries across arbitrary hosts/toolchains.

Two real integration obstacles were resolved: the initial Warble link used
native `HOSTCC`, and the hosted application's packaging required `zip`. A
forced-build workaround that set `HOSTCC` to AArch64 also rebuilt generators
for the wrong execution architecture. The project patch instead links Warble
using target `CC`, retaining native generators. Cross-binutils additionally
need their private host shared-library directory in `LD_LIBRARY_PATH`.

### Hosted application smoke

The uninstrumented SDL application first ran for ten seconds without a crash,
then was stopped by the test timeout; that alone was not counted as functional
UI proof. [`hosted_sdl_smoke.c`](../tests/hosted_sdl_smoke.c) adds test-only GNU
link wrappers around `SDL_WaitEvent` and `SDL_RenderPresent`. It captures actual
software-rendered pixels, injects down/right press/release events, and sends
`SDL_QUIT`. It does not replace Rockbox's application logic or force success.
Failure to render or complete shutdown returns a test error/timeout.

The independently prepared application produced **11 rendered frames**, accepted
four key events and exited **0** through the normal shutdown path. Its pre-quit
BMP SHA-256 was `a4680c95075a43a934d08f25598f8455945646aad346f63f5bc5bc22ce7d9f71`.
An earlier run's captured UI was visually checked: the database initialization
prompt was rendered after navigation. The screen includes a live clock, so
screen hashes/frame counts are observations, not deterministic UI baselines.
Audio was dummy-only; full application's codec playback and plugin behavior
were not exercised. User files/configuration are confined using Rockbox's
`RBROOT` and `--root` options, without changing the host's `HOME`.

### Memory-validation limit

Native AddressSanitizer passes the full corpus, with `detect_leaks=0`; this is
bounded memory-access evidence, not a proof of memory correctness for all input.
AArch64 ASan builds succeeded but crash before useful execution under this
QEMU/glibc/libasan combination. An empty instrumented main fails identically
with exit 139, isolating a tool/runtime problem from decoding. Its exact cause
is unresolved. A compatible ARM64 VM/runtime or a separately evaluated newer
QEMU is the next investigation; those tests must not be claimed complete here.

## Reproduction

Use existing Linux/WSL host tools and a **fresh private work directory**.
The pinned extracted Rockbox source and SDL tarball are read-only inputs.
`--inputs` can reuse the verified package cache; otherwise exact locked packages
are downloaded into the private workspace. No administrator installation occurs.

```sh
project=/path/to/nw-a306-open
work="$HOME/.cache/nwa306-open/m3-new"
python3 "$project/tools/m3_build.py" prepare --work "$work" \
  --source /path/to/pinned/rockbox-afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09 \
  --sdl-archive /path/to/SDL2-2.30.0.tar.gz
python3 "$project/tools/m3_build.py" build native --work "$work"
python3 "$project/tools/m3_build.py" build arm64 --work "$work"
python3 "$project/tools/m3_build.py" build native-asan --work "$work"
python3 "$project/tools/m3_build.py" build hosted --work "$work"
python3 "$project/tools/m3_build.py" smoke --work "$work"
```

The helper pins version/epoch, checks the patch input hashes, applies with zero
fuzz, isolates sysroot/wrappers/libraries and keeps build logs private. It was
exercised for fresh preparation, fresh ARM64/hosted builds and hosted smoke;
native/ARM64 build modes were also checked in the original workspace.
To repeat the measured rebuild comparison, record SHA-256 for Warble and all
`.codec` files, then run `make -B -j4` with `VERSION=afe91f1dfb`,
`SOURCE_DATE_EPOCH=0` and the private binutils library path. Do not override
`HOSTCC` with a target compiler. Compare against the recorded list.

Minimum remaining application work is full hosted playback/regression through
dummy or file PCM, robust resume/chaining/fast seek, and target-independent
tests for display/input/storage/audio-policy boundaries. A board-specific
Linux backend, init/safety policy and authorized boot/recovery still require
the [dependency investigation](m3-board-dependencies.md). Subsequent application
playback is recorded in the [M4 report](m4-playback-validation.md).

Sources: pinned R `tools/configure:3194-3220,4632-4635`, SDL target/architecture;
`firmware/export/config/sdlapp.h`, hosted platform/audio/storage;
`firmware/target/hosted/sdl/button-sdl.c:355-390`, event/shutdown loop;
`window-sdl.c:225-232`, actual window/renderer;
`firmware/target/hosted/filesystem-app.c:133-145,174-193`, RBROOT/config paths.
Package origins/hashes are in the lock file; SDL source/hash and original archive
provenance remain in the M2/M0 reports. Direct build, ELF, loader, test and image
observations above refer to private generated outputs, not target-device logs.
