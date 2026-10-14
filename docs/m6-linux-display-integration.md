# M6 Linux DRM scanout integration

2026-10-14. **Actual AArch64 Rockbox frames now reach a Linux DRM/KMS virtual
display**, alongside normal WAV/FLAC/Opus playback through ALSA. Independent
QEMU screen captures verify nonblank, changing scanout. This closes M5's generic
display gap; it does not validate the Sony panel, backlight or boot chain.

## Implementation and dependency choice

The pinned SDL 2.30.0 KMSDRM implementation was reviewed before adding an
adapter. `src/video/kmsdrm/SDL_kmsdrmvideo.c`, `KMSDRM_CreateWindow():1431-1530`,
forces OpenGL for a non-Vulkan window, initializes GBM and loads EGL. Using that
backend would add a graphics stack to the existing software renderer. The
[SDL master hint](https://wiki.libsdl.org/SDL2/SDL_HINT_KMSDRM_REQUIRE_DRM_MASTER)
also confirms that rendering needs DRM master access. M6 instead adds a small
**test-only** dumb-buffer adapter at `SDL_RenderPresent`, without changing
Rockbox playback or adding Mesa, libdrm, X11, Wayland or Android.

`tests/linux_drm_scanout.c` requires the explicit generic-guest guard, QEMU's
`linux,dummy-virt` model and `virtio_gpu` driver before modesetting. It opens
only the guest card, bounds resource/connector/mode arrays, selects an advertised
320x480 mode and compatible CRTC, and verifies dumb-buffer pitch/size. Two
XRGB8888 buffers are accepted by ADDFB2; software-rendered ARGB pixels are copied
with the kernel-returned pitch, damage is notified, and page flips alternate
buffers with a two-second event deadline. The current renderer size must match
the selected mode. On normal exit the original CRTC is restored, buffers are
released, DRM master is dropped and the descriptor is closed.

This deliberately uses legacy KMS, one virtual connector, no scaling and no
rotation. Unsupported modes/topologies fail, rather than synthesize timings.
It is not a general hotplug/atomic compositor or an installable Sony backend.
The [DRM userspace interface](https://docs.kernel.org/gpu/drm-uapi.html) defines
the generic master/modesetting boundary; successful virtual ioctls do not prove
that Sony's vendor driver supports the same path.

Three existing UAPI headers are selectively read from pinned Sony archive S
into the private build, avoiding another dependency. Their original notices
remain intact; they are not vendored publicly. Member prefix is
`kernel/msm-4.19/include/uapi/drm/`:

| Header | Bytes | SHA-256 |
| --- | --- | --- |
| `drm.h` | 31,352 | `db00f6d1630faeb5b662d966258a4e0a8e5b47dad42bc1c5fe14647069726e19` |
| `drm_mode.h` | 24,750 | `f7c1e510b96214166ceb68fcee72a6e85d1f5c2b21acbd8c01ff62cb6e1a2e24` |
| `drm_fourcc.h` | 25,541 | `5964ff18eaa2a4e0ae9e99b41adbefc9a53eb4af95f31b78a9b2eb72ab69c731` |

Raw UAPI sparse `__user` annotations are neutralized for userspace compilation;
structures are not rewritten. Compatibility of the used ioctls is demonstrated
against the actual 6.12 guest, not inferred from the headers' availability.
The C adapter carries GPL-2.0-or-later; existing patches and other components
retain their applicable licenses. No firmware or proprietary data is embedded.

## Exact executed system and evidence

The [M5 pinned environment](m5-linux-prototype.md#exact-system-and-dependency-provenance)
is reused unchanged: QEMU system ARM 8.2.2 Ubuntu package, TCG `virt`/A53, two
CPUs/512 MiB, Alpine ARM64 Linux 6.12.110, BusyBox initramfs, glibc 2.39,
ALSA 1.2.11 and SDL 2.30.0. No disk, network, USB or physical passthrough exists.
M6 adds `virtio-gpu-pci,xres=320,yres=480` and the matching virtio-gpu module
dependency closure (19 total guest modules including the existing six).
The module list and full command are retained in each private `result.json`.

Rockbox is pinned R `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`, normal
`sdlapp` 320x480, with the unchanged M3/M4/M5 patches and test wrappers.
Fresh private work prefix: `~/.cache/nwa306-open/m6/`.
**Final executable SHA-256:**
`c88b2320ef864e719986ec9f217cd0200ab7f1a2f767577e1bfb4491ed0c7933`.
Two forced same-prefix full builds reproduce all **42/42** application/codec
hashes. Different configured prefixes are not claimed byte-identical.
An earlier integration build (`77381a84…`) is preserved separately; all final
display/VM/application results use the final hash above.

SDL still uses its dummy software-rendering surface, but that surface is now
presented through actual kernel DRM buffers/page flips. QMP `screendump` reads
the virtual display independently, rather than returning the SDL BMP. Each run
has three 320x480 RGB PPM captures whose FNV-1a32 checksums match completed
renderer presentations. This is a frame-comparison check, not a cryptographic
integrity proof. SHA-256 records identify the retained capture files. The
captured WAV screen was visually reviewed: title, metadata, progress and controls
are upright with the expected colors and layout.

Private final evidence: `~/.cache/nwa306-open/m6-final-vm/`,
`build/m6/final-display-results.json`, `final-linux-results.json`,
`final-app/`, `rebuild-1.json` and `rebuild-2.json`. Generated images, PCM,
initramfs and binaries remain ignored. Normal callback tails and virtual-audio
startup silence vary with scheduling; complete music samples/order are checked
independently, not equated with total wall-clock capture length.

| Final experiment | Actual result |
| --- | --- |
| WAV / FLAC / Opus scanout | Each 22 completed alternating-buffer presentations, 21 distinct RGB frames; three changing QMP captures match presentation checksums; clean CRTC/master release and guest poweroff |
| ALSA output with scanout active | WAV and FLAC each 99,226 music frames at 44.1 kHz, exact reference PCM; Opus 108,001 at 48 kHz, peak error 5 s16 and SNR 68.7867 dB. QEMU WAV contains the entire emitted music region |
| Touch with scanout | 354 presentations/56 distinct frames; 160,240 tap pauses/resumes, 80→140→220 at y=300 drag coordinates reach ordinary Rockbox mapping; clean input cleanup |
| Repeated WAV boot | Same final application and identical initramfs SHA-256 `795556a2cf0aa1fe42b6ff7cfb4f4df38318057a927cb0aaf265d6e307746121`; correct output and clean shutdown again |
| Unsupported 640x480-only output | Explicit “no advertised 320x480 mode” failure, application status 102, no READY or scanout capture; supervisor powers guest off. No fabricated scaling/timing |
| Existing seven VM assertions | All pass, using DRM for music/touch/repeat and the existing dummy-video path for decoder-error and missing-application fault cases. Truncated Opus reaches UI error once then valid WAV; missing executable returns 127 without PCM |

The 320x480 renderer and synthetic 0..319/0..479 touch ranges align without
transformation. Sony's 1280x720 product panel needs its authentic orientation,
mode and touch ranges plus an appropriate UI build; this test does not select
them. Loading the generic backlight module as a DRM dependency does not exercise
any backlight device or prove brightness control.

## Reproduction

Use Linux/WSL and private paths. Prepare a **fresh** work directory with the
existing M5 build procedure and verified R/SDL/toolchain inputs first; do not
reuse/modify the preserved M5 worktree. Existing synthetic corpus hashes and
`tools/m5-linux.lock.json` must verify. Then, from the project directory:

```sh
python3 tools/m6_display.py link --work ~/.cache/nwa306-open/m6 \
  --sony-archive .local-references/sony-gpl-source/3.06.00-20260716/gpl_source.tgz
python3 tools/m6_display.py run --work ~/.cache/nwa306-open/m6 \
  --vm-dir ~/.cache/nwa306-open/m5-vm --corpus build/m4/corpus4 \
  --out ~/.cache/nwa306-open/m6-check/wav --playlist wav.m3u
```

Repeat the run with new output directories for `flac.m3u`, `opus.m3u --rate
48000`, `opus-controls.m3u --rate 48000 --touch`, and a second `wav.m3u`.
`--unsupported-mode` exercises the 640x480 rejection separately. The run command
sets only generic virtual devices and a private QMP socket; it never selects a
host card or physical device. It preserves exit status, UART, PCM, DRM log,
independent screenshots and hashes. Existing output directories are refused.

```sh
python3 tests/linux_drm_validation.py --corpus build/m4/corpus4 \
  --wav ~/.cache/nwa306-open/m6-check/wav \
  --flac ~/.cache/nwa306-open/m6-check/flac \
  --opus ~/.cache/nwa306-open/m6-check/opus \
  --touch ~/.cache/nwa306-open/m6-check/touch \
  --repro ~/.cache/nwa306-open/m6-check/repro --out build/m6-check-results.json
```

The M4/M5 application, codec, safety and inspector commands remain unchanged.
Final-suite details and limits are below. Full-build reproducibility uses the
same environment (`VERSION=afe91f1dfb`, `SOURCE_DATE_EPOCH=0`) and two forced
`make -B -f Makefile -f <work>/hosted-build/m6-adapter.make -j4 all` invocations,
comparing `rockbox` and every `.codec` SHA-256. Existing upstream warnings are
retained in the logs; there is no claim of a warning-free full build.

## Remaining display/power contracts

Before a Sony backend can replace the guest restriction, authentic board data
must establish the primary DRM node, capabilities, mode/format/stride, rotation,
panel sequencing and backlight owner. Begin dark; enable brightness only after
accepted frame presentation and safety readiness. Loss of readiness, scanout
completion or critical-service health must request dark/quiescent state; restore
display resources and follow verified shutdown ownership. Bounds and ordering
must be tested with synthetic contracts before real I/O. M6 implements no guessed
backlight, regulator, DSI or thermal writes. Current guest tests cover startup,
updates, unsupported mode and normal cleanup, not device loss/hotplug, suspend,
physical blanking or failed-ioctl cleanup completeness.

The existing pure fail-closed safety decision remains the tested policy boundary;
it is not a hardware mute/backlight implementation. Kernel charging/thermal
protection must remain independent of Rockbox. Source availability and generic
scanout do not validate the CXD3778GF, Sony display or battery electronics.

## Retained regressions and limits

Final application suite: 10/10 scenarios pass on the final build. Preserved
codec builds/corpus pass 38/38 AArch64 checks and 38/38 native ASan checks;
10/10 firmware-inspector and 7/7 safety tests pass. These suites/assertions were
not weakened. The seven VM checks above also pass on the final application.
M2's 41 original outputs verify; earlier pinned archives and M0-M5 evidence
remain unchanged as recorded in the [integrity inventory](m6-board-artifact-inventory.md#baseline-integrity).

Valid chained Opus remains unsupported and explicitly rejected/fallback-tested.
Native-rate success does not repair M4's approximately 20.39-dB forced-resampling
failure or establish cross-rate gapless playback. Native ASan uses the preserved
`detect_leaks=0` configuration; ARM64 shared-ASan pre-main crashes and static-ASan
Warble timeouts remain unresolved, not silently disabled or presented as passes.
No new claim of complete ARM64 memory safety, resource-leak freedom, physical
audio fidelity, Sony panel compatibility or safe device deployment is made.
