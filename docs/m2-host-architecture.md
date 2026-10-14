# M2 minimal Linux / Rockbox architecture and host validation

Assessment: 2026-10-13. The preferred design
remains **Linux with Rockbox as the primary interface and no Android userspace**.
M2 built and exercised existing Rockbox codec/DSP components on the host;
it did not build an NW-A306 firmware, boot a target kernel or validate hardware.
The [firmware report](m2-firmware-analysis.md) records preservation and the
opaque update-container findings. M0's [evidence register](feasibility.md#evidence-register)
and [hardware matrix](hardware-matrix.md) retain their original scope.

## Minimum proposed stack

Provisionally retain the vendor Linux/Qualcomm support rather than replacing
the SoC platform in bare metal. A reviewed boot mechanism would hand off to an
ARM64 kernel, authentic board DT/overlays, necessary drivers and platform
firmware. A small initramfs/root filesystem would provide init/supervision,
device nodes, required firmware loading, filesystem mounts, audio initialization
and charging/thermal/watchdog/shutdown policy. Rockbox would own the UI and
library/playback, using Linux display, event input and ALSA interfaces.

Android framework, ART, APKs, Binder services, AudioFlinger, a compositor and
Sony effects are not planned dependencies. Removing them is conditional on
replacing any essential board/power/audio initialization they perform. ALSA
direct playback is preferred; a sound server or a desktop is not initially
required. A CPU-rendered DRM/KMS buffer is the display fallback if framebuffer
compatibility is absent; accelerated graphics are unnecessary for this design.
Neither display path has been demonstrated on NW-A306.

An initial root filesystem can avoid modifying Android's dynamic `super`
layout, but its placement and boot handoff are still design questions. This is
not a claim that a ramdisk or removable-card boot bypasses signature policy.
Keep internal user-data encryption and unique calibration/key storage intact.
Optional Bluetooth, Wi-Fi and Sony processing do not gate the first verified
wired-playback environment; battery, charging and thermal protection do.

## ABI and build audit

Sony's `build.config.aarch64:1-6` specifies `ARCH=arm64`,
`aarch64-linux-gnu-` and a separate `arm-linux-gnueabi-` compatibility toolchain.
The published defconfig enables `CONFIG_COMPAT` and forced SHA-512 module
signatures. These are source/build settings, not captured running-kernel or
installed userspace ABIs. No decrypted stock executable, loader, module or libc
has been identified in the candidate package. [A1; M0 S1]

Prefer **AArch64 little-endian Linux userspace with a single libc/toolchain** as
the next host cross-build candidate. Glibc is a conservative initial choice
given the successful native Linux build and existing hosted integration;
musl would require a separate API/loader audit, not just relinking. A 32-bit
ARM userspace remains an alternative if it materially reduces proven porting
cost, but needs a compatible kernel, matching float/calling ABI and complete
32-bit loader/libc/ALSA dependencies. `CONFIG_COMPAT` alone supplies none of
those userspace libraries. Kernel modules must match the ARM64 kernel ABI and
configuration regardless of application bitness.

Pinned Rockbox configure recognizes AArch64, and its source contains some
AArch64 codec/thread support. This does not constitute an NW-A306 target.
Existing Sony A10 paths and the experimental NW-A30 port describe different
hardware, mount layouts and startup environments. Their target IDs, key maps,
volume indices and board constants must not be reused as verified A306 values.
[M0 R1/R2/N1; A2]

Hosted codec/plugin modules are loadable executable objects, not architecture
neutral media. Build the application, codecs and plugins for the same ISA,
libc, compiler ABI, target ID and API revision. Rockbox loaders check codec
magic/target/API and plugin API size/version. At R, codec API is 50 and plugin
API 285. The M2 test executable and codecs are ELF64 little-endian **x86-64**;
`ldd` resolves libc/libm and the host loader, with no missing library. This
validates native LP64 loading of the exercised codecs, not ARM64 code generation,
32-bit support, arbitrary plugins or compatibility with Android/Bionic binaries.
One nonfatal `%ld`/`uint32_t` format warning in `libm4a/demux.c:488` remains a
portability audit item. [A2, A3]

## Dependency matrix

“Source” identifies reviewed code, “binary required” identifies a runtime
payload dependency, and “missing/unverified” identifies an unresolved input or
target behavior. Every row remains unverified on custom NW-A306 hardware.
Source citations refer to M0 unless an `A` locator below is given.

| Dependency | Availability / evidence | Minimum integration and unresolved requirement |
| --- | --- | --- |
| Kernel/platform | Source: Linux 4.19.157, Qualcomm/ARM64 configuration, S1 | Authentic selected DT, reserved memory, clocks, regulators and boot handoff missing; no complete target kernel build demonstrated |
| Modules/build | Source: Qualcomm audio and Sony codec; missing external DLKM helper, S7 | Reproduce kernel/module configuration and symbols; resolve build helper and signing requirements before claiming a usable module |
| Board DT/DTBO | Missing verified NW-A306 tree/overlay; S9 and M1 inventory | Recover authentic trees or obtain board documentation; generic Bengal/QCM2290 descriptions cannot supply panel/audio/PMIC wiring |
| Init/libc/devices | Open Linux userspace components available in principle; target selection/build unverified | Small init, `/proc`, `/sys`, `/dev`, supervision and bounded shutdown; no new init system chosen or rootfs claimed built |
| Rockbox core/codecs/plugins | Source R; host codec application and 40 codec modules built, A3 | Add an independently reviewed target config/backends; cross-build and test application/codecs/plugins together. Only WAV/FLAC decode passed fully in M2 |
| Display/backlight | Source DRM/MSM/SDE/DSI and backlight config, S1/S9; Rockbox `/dev/fb0` backend, R2 | Determine panel and active driver; test fbdev availability or implement DRM/KMS software scanout, mode selection, stride/format/orientation and suspend/brightness |
| Buttons/touch | Source GPIO keyboard, evdev, Himax HX83102 and SINTRONIX options, S1/R2 | Establish actual controller, event codes, coordinates and wake behavior; touch firmware/calibration availability unverified |
| ALSA frontend/routing | Source Rockbox ALSA and Bengal machine driver, R2/S3 | Replace needed Android mixer/route setup with exact card/PCM/control configuration; no stock mixer profile recovered |
| Qualcomm DSP transport | Source Q6ASM/QDSP6 interfaces and PCM writes, S2/S7; binary firmware dependency in platform loaders, A4 | Obtain matching DSP binaries and calibration/routing inputs lawfully; identify active firmware loader, authentication policy and board binding. Open transport is not DSP firmware source |
| Sony wired codec | Source CXD3778GF I2C/ASoC controls and MI2S links, S3/S4/S6 | Verify selected ICX/STD route, GPIOs/regulator/clocks, jack and muted startup; kernel control access is not a measured headphone path |
| Gain/mute/calibration | Source sparse defaults, runtime table ports and multi-register volume writes, S5/S6 | Correct table data, units/dB limits and sequencing missing; do not treat the default index 120 as a safe audible setting |
| MD6000/RME | Source requests external firmware, S8; binary payload not supplied/verified here | Establish whether this shared NW-ZX700/NW-A300 component exists on A306 or is needed for the initial PCM path before adding it |
| Internal storage | Source MMC/UFS options and ext4/F2FS/VFAT; historical dynamic layout, S1/D1 | Establish physical storage, GPT and encryption implications; retain unique state and avoid mounting unknown partitions writable |
| Removable microSD | Source MSM SDHCI and hosted storage model, S1/R1 | Replace older `/mnt/media` and `/sys/block/mmcblk1` assumptions with actual board paths; implement detection, mount/unmount, removal and resume safely |
| Charging/battery | Source QPNP SMB5/SMBLITE/QG and related options, S1 | Board PMIC, battery profile, thermistor/current/voltage limits and USB policy missing/unverified; Rockbox monitoring alone is not charging policy |
| Thermal/watchdog | Source TSENS/CPU/devfreq, user-space governor, emergency poweroff and QCOM watchdog, S1/A1 | Identify trips, required userspace governor/service and watchdog owner; protect faults before extended operation |
| Suspend/shutdown | Source codec suspend/resume, reset/watchdog and platform power support, S1/S6 | Verify wake sources, DSP/rail/storage sequencing, charging interaction and reliable shutdown; no power or battery-life claim |
| Firmware/unique state | Binary requirements/calibration are incompletely inventoried; M1 L4, S5/S8/A4 | Obtain exact filenames, provenance, matching versions and permitted provisioning; preserve device-bound data. A GPL code archive is not a binary firmware inventory |
| Optional effects/connectivity | Sony processing implementations unavailable in reviewed sources; transport/control hooks only, S6/P4 | Defer; independently evaluate Rockbox DSP. Bluetooth/Wi-Fi need separate firmware/stack/integration/licensing evidence |

The candidate source path for wired sound is Rockbox PCM -> ALSA frontend ->
Qualcomm Q6ASM/DSP -> selected MI2S backend -> CXD3778GF controls/output.
This is an inference from S3/S4/S7, not a runtime trace. Source-declared rates
and S16/S24/S32 formats do not prove negotiated formats, routing, meaningful
precision, DSP bypass or bit-perfect output. ALSA's rate-near negotiation in
R2 is an additional reason to measure the eventual route explicitly.

## Actual host environment and isolation

Existing Ubuntu 24.04 WSL2 was used, x86-64 kernel
`6.6.87.2-microsoft-standard-WSL2`. It does not emulate QCS2290, the Sony board,
boot chain, display, audio electronics, PMIC or charging behavior. No generic
system VM was built: a native codec harness supplied a smaller, relevant test.

| Tool/input | Actual pinned or recorded version |
| --- | --- |
| Rockbox | R `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`, unchanged private source copy |
| GCC | `13.3.0-6ubuntu2~24.04.1` |
| Binutils | `2.42-4ubuntu2.8` |
| GNU Make | `4.3-4.1build2` |
| Perl | `5.38.2-3.2ubuntu0.6` |
| glibc / development headers | `2.39-0ubuntu8.9` |
| Python | Existing Windows 3.12.10; WSL package `3.12.3-0ubuntu2.1` |
| Fixture encoder/reference | Existing Windows FFmpeg `9.0.1-full_build-www.gyan.dev` |
| Added isolated dependency | SDL **2.30.0**, official source tarball; SHA-256 `36e2e41557e0fa4a1519315c0f5958a87ccb27e25c51776beb6f1239526447b0` |

SDL was required by the existing Warble harness's headers/thread/audio stubs;
its audio/video backends were disabled because tests write files. Source,
library, logs and an unchanged Rockbox build copy reside only under
`~/.cache/nwa306-open/m2/` in WSL. Windows fixtures/check records/scripts are
under ignored `build/m2-host/`. No system package, Windows driver or host boot
setting was changed. `.local-references/` remained read-only; 45 previously
reviewed Sony members were re-streamed from the archive and matched the M0
cache exactly, with two additional selectively read platform-loader members.

## Reproduction and build results

Use an isolated source/build copy, never configure inside `.local-references/`.
The following are the actual build choices, with `work` standing for the private
WSL directory above. The original R source copy was made with `cp -a` from the
pinned extracted snapshot. [A3, A5]

```sh
work="$HOME/.cache/nwa306-open/m2"
project=/path/to/nw-a306-open
# Fresh isolated workspace; preserve and verify any pre-existing inputs first.
mkdir -p "$work/inputs" "$work/sdl-build" "$work/warble-build"
cp -a "$project/.local-references/upstream/rockbox/rockbox-afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09" "$work/rockbox-source"
curl -fL --max-time 120 -o "$work/inputs/SDL2-2.30.0.tar.gz" https://www.libsdl.org/release/SDL2-2.30.0.tar.gz
echo "36e2e41557e0fa4a1519315c0f5958a87ccb27e25c51776beb6f1239526447b0  $work/inputs/SDL2-2.30.0.tar.gz" | sha256sum -c -
tar -xzf "$work/inputs/SDL2-2.30.0.tar.gz" -C "$work"
cd "$work/sdl-build"
../SDL2-2.30.0/configure --prefix="$work/sdl-prefix" \
  --disable-shared --enable-static --disable-video --disable-audio \
  --disable-render --disable-joystick --disable-haptic --disable-sensor
make -j4
make install
export PATH="$work/sdl-prefix/bin:/usr/bin:/bin"
export VERSION=afe91f1dfb SOURCE_DATE_EPOCH=0
cd "$work/warble-build"
../rockbox-source/tools/configure --target=ipodvideo --ram=64 --type=w --no-ccache
make -j4
sha256sum warble.ipodvideo lib/rbcodec/codecs/*.codec > ../build-first.sha256
make clean
make -j4
sha256sum -c ../build-first.sha256
```

`ipodvideo` chooses an existing codec-harness configuration, not an iPod firmware
build or an A306 target. `VERSION` prevents the upstream version script from
querying Git; epoch zero is a chosen deterministic timestamp, not a commit date.
Both builds succeeded, with **all 41 hashes identical**: Warble and 40 codec
modules. This is a clean rebuild in the same source/build paths and environment,
not a demonstrated cross-machine or cross-toolchain reproducible firmware.
The hash-list record SHA-256 is
`c03544f6c9e3a0cc2ac26d13b386699fab85e05f65289417e4e4b915cffa898d`.

| Output | SHA-256, both builds |
| --- | --- |
| `warble.ipodvideo` | `686f77482263461937851427f2c806c2f4298db24707a7d3d138dc9654b3665d` |
| `flac.codec` | `9a1461bc9794e7ae7ffac3ff12f9b62709b2a108c89234d42ea2fadaa45aa095` |
| `opus.codec` | `715a688aa78122e415716214e8927e73e9d6de59a5b2c854ffc6fb8b510daa69` |
| `wav.codec` | `f99596a4da3c1abf0c480eb5ec51d7347f4b970be3d7e4ca1a46f49a437ab5bb` |

No target kernel/modules, ARM userspace, complete Rockbox UI or plugin execution
was validated. No test used an audio device. These limits apply even though
additional decoder modules compiled successfully.

## Deterministic codec / DSP smoke tests

The fixture is one second of 48-kHz stereo signed-16 PCM. For frame `i` from
0 through 47999, left is `(i*257)%60001-30000`, right is
`30000-(i*509)%60001`. A second fixture is 48000 stereo frames of zero.
Generate using Python's `wave` module with two channels, two-byte samples,
48000-Hz rate, and little-endian `struct.pack('<hh', left, right)`; no private
recording is involved. The exact original WAV hashes are below.

```powershell
ffmpeg -nostdin -hide_banner -loglevel error -y -fflags +bitexact -i signal.wav -map_metadata -1 -flags:a +bitexact -c:a flac -compression_level 5 signal.flac
ffmpeg -nostdin -hide_banner -loglevel error -y -fflags +bitexact -i silence.wav -map_metadata -1 -flags:a +bitexact -c:a libopus -b:a 64k -vbr off silence.opus
ffmpeg -nostdin -hide_banner -loglevel error -y -i silence.opus -f s16le opus-reference.pcm
```

Invoke Warble from its build directory, with input/output paths to those fixtures:

```sh
./warble.ipodvideo -f signal.wav wav-float.wav
./warble.ipodvideo -f signal.flac flac-float.wav
./warble.ipodvideo -f silence.opus opus-float.wav
./warble.ipodvideo signal.flac flac-dsp.wav
```

`-f` bypasses the DSP and writes float64 WAV, allowing exact codec comparisons.
For these harness outputs, verify RIFF/fmt/data fields, float format 3, stereo
48000 Hz and the 46-byte harness header. Unpack little-endian doubles from
offset 46; `round(sample*32768)` must equal every generated signed-16 sample,
with exactly 48000 frames. Inspect stderr as well as exit status: Warble prints
a codec-run error without changing its final zero exit status. [A3]

| Test | Actual result / limitation |
| --- | --- |
| WAV decode | Pass: all 96000 channel samples match exactly, 48000 frames, no codec error |
| FLAC decode | Pass: same exact PCM and byte-identical float WAV as WAV decoding |
| FLAC through Rockbox DSP | Smoke pass: stereo signed-16 44100-Hz output, 44101 frames, no codec error. Resampling occurred; endpoint count/quality and physical output are not validated |
| Opus decode | **Fail:** 47688 zero frames rather than 48000; stderr `error: codec error`, despite process exit 0 |
| Independent FFmpeg Opus decode | 48000 zero frames, 192000 signed-16 PCM bytes; confirms a complete reference decode of this fixture |
| Post-rebuild repeat | Same decode-output hashes and Opus failure reproduced |

| Fixture / result | SHA-256 |
| --- | --- |
| `signal.wav` | `682c57516b8ca6ada87295b094556f3d738c1d7cf51c0407ee5debd38aea1c51` |
| `silence.wav` | `ede1f6dd33abfce7bb3a45ba79b0ab5f8baae692709dd32214a41da9af55ab13` |
| `signal.flac` | `4f614309c0dcace52f4888d16c718a7fe136a99575cdbc10c592962c7c719563` |
| `silence.opus` | `02b85e429b193cdf90b5c8b17699a119094f3a782f16f01fdd3f7531fbb75043` |
| WAV and FLAC float output | `0a3d3c17dbf0d125b9f7750ccd24b3329fb9aecab3e651b1417ead61f3e44a6f` |
| FLAC DSP output | `bf15886a414bea86d9ca8f304289044f932c40110b67fe48507a31e195ef9164` |
| Incomplete Opus float output | `cea356e52f391ce58193f4de4695496e64761b02147105d83922cdf4bfa9a922` |
| FFmpeg Opus reference PCM | `ea0787f65f73b0013d03b359490e3125211b28ad5c1502ffb1544c0ded4192f5` |

The synthetic Opus stream has 51 audio packets, preskip 312, and pages at
0/47/127/8204 with granules 0/0/48000/48312; its last page carries EOS.
Pinned `opus.c:454` excludes packets marked `e_o_s` from its decode loop.
Decoding only the first 50 960-frame packets, then subtracting preskip, gives
the observed `48000-312=47688` frames. The EOF path at 434-435 reaches `done`
with the initial `CODEC_ERROR` from 359. These source paths explain this
fixture's omission/error; they do not establish the behavior of every Opus
stream or every target. A regression and reviewed EOS/granule trimming fix
are concrete offline implementation work; M3 records the subsequent correction.
No upstream source was changed in M2. [A6]

## Forward engineering priorities and prerequisites

| Unresolved requirement | Next concrete investigation | Prerequisite / boundary |
| --- | --- | --- |
| Codec correctness | Add a regression for Opus EOS/preskip/end trimming; test nonzero, short, chained and seek cases before a narrowly reviewed fix | Pinned source copies and generated fixtures; no hardware needed |
| Target ABI/userspace | Isolated pinned AArch64 toolchain/libc cross-build of hosted codec harness, then generic user-mode/VM tests and plugin audit | Select toolchain/libc and record licenses/hashes; generic execution does not validate the board |
| Package contents | Confirm NWWM cipher/key/digest and selectively inspect authenticated plaintext OTA/image metadata | Lawfully supplied matching format evidence and material |
| Board/kernel completeness | Recover exact DT/overlays, module configuration and missing build-helper requirements; produce a reproducible target kernel/module build | Authentic matching images/docs and suitable isolated cross-toolchain; no install |
| Audio initialization | Trace required ALSA controls, Q6 firmware and tables; design muted startup and synthetic control-policy tests | Matching routing/calibration evidence and licenses; hardware output remains separately gated |
| Display/input/storage | Define backend interfaces and host tests for formats/events/hotplug after obtaining board evidence | Actual panel/input/mount information; avoid inventing A306 constants |
| Power safety | Identify all Android-owned charging, thermal and watchdog responsibilities and necessary replacement policy | Correct board DT, battery/thermal data and service/source evidence; no extended hardware operation until reviewed |
| Custom boot authorization | Obtain model-specific supported acceptance/signing/unlock or custom-key documentation; evaluate temporary boot and privileged kexec only conditionally | Sony/service or authoritative matching evidence; OEM switch and generic Xperia/i.MX guides insufficient |
| Recovery/unique state | Seek authentic full images, exact restore scope, same-version/rollback policy and unique-data preservation | Sony service cooperation may be needed; EDL requires matching authorized programmer/tools if applicable, and a matching spare for separately approved validation |

Retain minimal Linux provisionally. A mainline kernel is an alternative only
after identifying the missing Sony board/audio/power support; it is not a
shortcut supplied by generic QCM2290 source. Temporary boot still depends on
image acceptance; kexec depends on verified privilege/kernel support; EDL on
authenticated matching tooling. None is established. A matched spare or an
external development board/additional hardware could reduce primary-device
risk and support early interface work, but cannot prove this Walkman's boot or
audio compatibility. Codec, ABI, parser and policy work can proceed on the host.

Original project contributions use [GPL-2.0-or-later](licensing.md).
Derivative Rockbox work must meet its applicable GPL obligations; Linux,
SDL (zlib license), codec libraries and other components retain their respective
licenses. Proprietary firmware/calibration rights remain unresolved; source
availability does not confer binary redistribution rights. Keep such inputs
private until provenance and permitted provisioning are established. [M0 R3; A5]

Firmware/bootloader changes require an explicitly approved operation plan and
verified recovery. M3's [codec report](m3-codec-validation.md) records the
subsequent host corrections.

## Additional source locators

R/S/D identifiers refer to the preserved M0 register, not new archive revisions.

| Ref | Exact source / observation |
| --- | --- |
| A1 | S `kernel/msm-4.19/build.config.aarch64:1-13`; published `sony_dmp_android_defconfig:69,98-100,272-276,340-354,377-401,491-498,571-579,628-644`. Archive streamed read-only, contents of 45 M0 cached members rechecked identical. |
| A2 | R `tools/configure:4684-4699`, AArch64 detection; `firmware/asm/thread.h:44-53`, hosted/AArch64 stack consideration; `firmware/target/hosted/lc-unix.c:29-54`, `dlopen`/header lookup; `lib/rbcodec/codecs/codecs.h:73-82,248-272`; `apps/plugin.h:183,1075-1084`; `apps/plugin.c:972-983`, module API checks. |
| A3 | R `lib/rbcodec/test/warble.make:9-34`, build/dependencies; `warble.c:143-213`, output/header; `819-898`, metadata, dlopen and codec errors; `935-985`, write/play selection. Actual isolated configure/build/clean/rebuild, ELF/ldd inspections and generated-fixture results above. |
| A4 | S `kernel/msm-4.19/drivers/remoteproc/qcom_adsp_pil.c:78-84,111,337-347`, MDT load, SCM authentication and generic firmware names; SHA-256 `8d1382a880ce1c3de29c24f48086a6c0838c5fbcfb3ae47dc0273cf53b8c4ef4`. `drivers/soc/qcom/peripheral-loader.c:1033-1034,1223-1249`, firmware requests; SHA-256 `4eb33dcd873f7b1089537ecdbf4eac3acc870c06a596756a87e7937875118be4`. Source examples, not established active A306 loaders or firmware filenames. |
| A5 | [Official SDL 2.30.0 source](https://www.libsdl.org/release/SDL2-2.30.0.tar.gz), hash/version above; `LICENSE.txt`, zlib terms. R `tools/version.sh:42-62`, VERSION and epoch override; `tools/root.make:227-240`, private build cleanup. |
| A6 | R `lib/rbcodec/codecs/opus.c:359,434-435,454,462,505-514,528-532`, initial error, EOF, EOS exclusion, preskip and return. Direct parse of generated Ogg pages/packets, Warble stderr/output and independent FFmpeg reference decode. |
