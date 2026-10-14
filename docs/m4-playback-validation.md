# M4 end-to-end AArch64 playback and reliability

Date: 2026-10-14, America/New_York. M4 demonstrates actual
hosted Rockbox playback of WAV, FLAC and Opus, with PCM captured at SDL output.
This is Linux userspace
execution, not a bootable NW-A306 operating system or physical audio validation.

## Preserved baseline and executed build

All 19 project files were copied, size/SHA-256 verified
and retained in ignored `build/m4-baseline-20261013/`. Its recoverable
`snapshot-manifest.json` SHA-256 is
`b43023fb94f5aceffc2e52ed2c79dd029673f7fd6ecd669a65b4b570acaa7084`.
The manifest also records hashes for 1,887 private M3 files. All 13 M1 artifacts,
three pinned archives, 318 M0 records, M2's 41 outputs, M3's corpus, patch and
toolchain lock were verified. Original archives and `.local-references/` remain
unchanged; all source modifications use an isolated WSL copy.

The executed application is Rockbox R
`afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`, existing `sdlapp` target, normal
application type, 320x480, plus the M3 patch, M4 patch and test-only link wrappers.
Application SHA-256 used for the ten-scenario suite:
`1567dc4866d51414ac4ab479e06d09c1577952e92a71b0e1010b291ebb4ef801`.
The final full-rebuild application SHA-256 is
`b3d921ba711dc16cf629f050ac0d45439d360be6fdcca155ca682f6943eb3f71`.
An incremental/full comparison differs only in GNU build-ID notes across the
application and 41 codecs; executable/data bytes outside those notes match.
Two successive forced full builds reproduce all **42/42 hashes**. A repeat
Opus application run on the rebuilt set reproduces the validated music PCM.
It is ELF64 little-endian AArch64/LP64, executed with the M3 pinned QEMU
8.2.2 Ubuntu package and glibc 2.39 sysroot. GCC 13.3, SDL 2.30.0 and all 15
locked packages are reused without new downloads or system-wide installations.
See [M3 ABI/toolchain evidence](m3-aarch64-bringup.md#toolchain-abi-and-isolation).

Private workspace: `~/.cache/nwa306-open/m4/`; Windows inputs/results:
`build/m4/`. Package metadata, binary and codec lookup paths are confined to
these workspaces. `RBROOT` confines configuration. The hosted application's
`--root` option does not pivot its native filesystem, so M4 uses explicit private
library paths and relative playlist entries rather than assuming a sandbox.

## Actual application path and capture

[`hosted_playback.c`](../tests/hosted_playback.c) uses GNU link wrappers.
After normal initialization, it selects a real M3U using `playlist_create()` and
`playlist_start()`, then enters the real `root_menu()` and While Playing Screen.
There are no direct codec calls and no replacement playback engine. The ordinary
buffering/codec threads load `.codec` modules, decode, run Rockbox DSP, fill
pcmbuf/mixer buffers and invoke the real SDL PCM callback.

The `SDL_OpenAudioDevice` wrapper substitutes only a callback trampoline: it
first calls Rockbox's original callback, then records the resulting bytes.
SDL's dummy backend remains clocked and receives the same buffer. Capture is
bounded to 120 seconds and validated as stereo signed-16 little-endian PCM.
This is captured application output, not Warble output or an assertion based
on a silent sink. Callback padding and post-playback silence are separated
from music frames in comparisons.

Controls enter the normal WPS action handlers for pause/resume, next/previous
and stop. Active seek calls the ordinary `audio_pre_ff_rewind()` /
`audio_ff_rewind(2500)` APIs on the main application thread. The test is not a
physical keyboard/evdev test. It observes metadata, codec completion, output
format, progress, buffer availability and actual rendered screens. Shutdown
uses SDL_QUIT and the normal Rockbox shutdown path, not a forced successful exit.

## Corrections justified by playback evidence

[`rockbox-playback-integration.patch`](../tools/rockbox-playback-integration.patch)
applies after the unchanged M3 correction and changes three files:

- `opus.c`: report decoded-frame progress instead of each page's endpoint;
  retain initial granule origin when reporting time. When startup includes
  elapsed time and a byte offset, elapsed time is authoritative: decode/discard
  from zero using the existing exact seek path. Clear the stale offset before
  rereading headers. Offset-only resume remains rejected; no approximate byte
  seek was added.
- `metadata/ogg.c`: subtract Opus pre-skip from ordinary stream duration and
  retain a nonempty sub-millisecond stream with a one-millisecond UI duration.
  A first attempt rejected M3's one-frame case; regression testing caught it
  and the final patch restores all 38 checks. This retains the pinned parser's
  existing single-stream/fixed-header assumptions. Cropped positive-origin
  metadata duration and very long 64-bit granules still require further work.
- `config/sdlapp.h`: advertise 44.1 and 48 kHz through the existing SDL rate
  interface. Auto rate selection now avoids forced Opus resampling. This is a
  generic SDL-target change tested on dummy SDL, not a Sony rate capability.

The patch and Rockbox-dependent test adapter are GPL-2.0-or-later. Original
test materials do not override Rockbox or other component licensing.

## Deterministic library and PCM results

[`playback_validation.py`](../tests/playback_validation.py) generates original
integer waveforms using the existing Windows FFmpeg 9.0.1 build, plus a one-frame
Opus fixture, eight-second control tracks, a two-link chained file, empty/invalid
files and a truncated Opus stream. FFmpeg independently decodes the references.
All **32 media/reference/playlist files** and the manifest reproduced exactly.
Canonical manifest SHA-256:
`5752a7aa3c693c6a5c0c8b427ee3a142bc030f84aeaf14542a1d1b0ac46f42b1`.
FFmpeg warns about non-monotonic DTS at concatenated links while writing raw
PCM; the chain has distinct serials and complete CRC-correct links. Its native
reference has twice the individual frame count, but second-link PCM differs
from decoding that link alone. It is not used as a chaining-conformance oracle;
Rockbox's observed metadata rejection is the result of this test.

| Final single-track run | Music delivered | Independent comparison |
| --- | --- | --- |
| `signal.wav` | 99,226 stereo frames, 44,100 Hz | Every music sample byte-identical; subsequent callback bytes are zero |
| `signal.flac` | 99,226 stereo frames, 44,100 Hz | Same exact lossless result |
| `signal.opus` | 108,001 stereo frames, 48,000 Hz | Zero alignment shift; RMS error 1.0461 signed-16 units, peak 5, SNR 68.7867 dB |

Music duration is approximately 2.25002 seconds. Opus decoded PCM is compared
with decoded reference, not with its lossy encoder input. Native-rate Opus
requires exact frame count, SNR >=40 dB and peak <=0.005 full scale; no arbitrary
alignment search is permitted. Lossless paths require exact samples. Neutral
configuration disables ReplayGain, EQ, crossfeed, dithering, tone, shuffle,
repeat, crossfade, voice/beeps and volume fades; volume is 0 dB. Actual PCM
confirms unity gain on the lossless paths.

An earlier 44.1-kHz-only build exercised the existing Hermite resampler. Against
FFmpeg's different resampler it produced 99,227 active frames, about two frames
of latency and only 20.39 dB SNR on this discontinuous waveform, failing the
30-dB comparison threshold. That failure is preserved; M4 does not claim to
have fixed or validated resampler quality. The native-rate path separates this
issue from the correctly decoded Opus signal.

## Functional and reliability results

The final `suite-check` passes **ten scenarios**, all with normal exit 0 and no
watchdog termination. A successful process exit alone never counts as successful
decoding of every playlist entry.

| Scenario | Evidence / limitation |
| --- | --- |
| Startup, library, codecs and UI | Real playlist files opened, WAV/FLAC/Opus modules loaded, WPS rendered; Opus title and progress visually checked |
| Progress and metadata | Single-track maximum progress discrepancies versus delivered frames: WAV 17.65 ms, FLAC 47.36 ms, Opus 18.34 ms; all below the 75-ms callback/chunk allowance |
| Pause/resume | WPS actions reach paused state; progress remains 213 ms across paused observations and final paused output window is silent; playback resumes |
| Active seek | Main-thread seek to 2500 ms observed in the running long-Opus track; M3's exact codec seek regressions remain passing |
| Next / previous / stop | Next reaches WAV, previous returns to long Opus, stop drains/stops and exits normally |
| Mixed playlist / completion | WAV and FLAC appear consecutively and exactly; following Opus PCM equals the single-track capture. Rate switch adds 204 silent 44.1-kHz frames (~4.63 ms), so cross-rate gapless output is not claimed |
| Restart with timestamp resume | New application process reuses copied prior configuration, requests elapsed 1000 ms with an observed nonzero offset, and delivers the remaining 60,001 Opus frames within peak error 5 |
| One-frame Opus | One music frame reaches output; padding remains silent; millisecond display necessarily rounds |
| Five playback cycles | All five complete lossless signals delivered. Available playback buffer settles from 4,187,064 to 4,154,264 bytes and stays stable for cycles 2-5; normal shutdown follows |
| Invalid / chained files | Empty and invalid files fail metadata; truncated Opus returns codec status -1 and next WAV plays. Valid chained Opus fails the pinned metadata serial check and is skipped; link-transition playback is **unsupported** |

Error visibility is incomplete: `audio_codec_complete(-1)` reaches the engine,
but pinned `audio_on_codec_complete()` largely handles it like ordinary track
completion. The trace distinguishes the error; M4 does not claim a reliable
user-facing error report. Partial PCM from a truncated track can precede its
error. Chaining and explicit application error reporting are concrete M5 work.
No unexpected holes occur within the validated uninterrupted music. Callback
silence, pause and rate-switch padding are accounted for; stressed real-time
underrun recovery, exhaustive state testing and long-run leak freedom are unproven.

## Memory/runtime investigation

The independent [`asan_runtime_probe.c`](../tests/asan_runtime_probe.c) is
unrelated to Rockbox. Shared libasan crashes before main for both PIE and
non-PIE. Static libasan/non-PIE enters main, succeeds for valid input and reports
the deliberate heap overflow with exit 1. UBSan likewise reports its separate
signed-overflow negative case. The isolated GCC-13 static archive and the
locked GCC-14 shared runtime are different inputs; linkage/runtime version and
initialization/layout remain candidate causes. Neither PIE alone nor an
assumption that all ARM64 ASan is impossible explains these observations.

Native ASan with the M4 patch passes **38/38**. ARM64 uninstrumented M4 passes
**38/38**. An ARM64 static-ASan application builds but times out before reaching
the playlist hook. The static-ASan harness initially fails module loading due
to an unexported runtime symbol; exporting executable symbols resolves loading,
but decoding then hangs after allocations. Eight per-case records were retained
and the repeated hanging suite stopped. These are **failed instrumentation
approaches**, not decoder regression successes or proof of an invalid access.
The exact hang is unresolved; audit static runtime interaction with Rockbox's
libc/allocator and hosted thread scheduling before another large instrumented run.

Only instrumented builds omit `-z defs` so modules can bind ASan symbols from
their executable, consistent with the [ASan shared-library guidance](https://clang.llvm.org/docs/AddressSanitizer.html#usage).
Memory diagnostics remain enabled; no suppression was added. Leak detection is
disabled for these access checks, so leaks are not assessed by ASan. SDL itself
was not instrumented. Stable playback-buffer observations and clean shutdowns
are bounded resource evidence, not heap/FD leak proof or ARM64 memory-safety proof.

## Reproduction and source locators

Use fresh private directories. First run M3's hash-checked `prepare`, apply the
M4 patch with `patch --batch --fuzz=0 -p1` inside its isolated source copy, then:

```sh
python3 tools/m3_build.py build hosted --work "$work"
python3 tests/playback_validation.py link --work "$work"
python3 tests/playback_validation.py run --work "$work" --corpus "$corpus" \
  --out "$runs/review-opus" --playlist opus.m3u
python3 tests/playback_validation.py analyze --corpus "$corpus" \
  --output "$runs/review-opus" --track signal.opus --out "$runs/opus-analysis.json"
python3 tests/playback_validation.py memory-probe --work "$work" --out "$work/probes"
```

Generate with `python tests/playback_validation.py generate --out <fresh-path>`
on the recorded Windows FFmpeg environment. For `suite-check`, use fresh
`review-wav/flac/opus/mixed/invalid/chain/short` runs with matching M3U names;
`review-controls` uses `opus-controls.m3u --controls`; `review-cycles` uses
`wav.m3u --cycles 5`; `review-restart` uses `opus.m3u --restart-from <prior-run>
--elapsed 1000 --offset 16384`. Then run `suite-check --corpus ... --runs ...
--out <fresh-path>`. Output directories refuse replacement.

The failed ARM64 ASan build is reproducible by configuring a separate hosted or
Warble build, using `CC="<target-gcc> -fsanitize=address -static-libasan -no-pie
-fno-omit-frame-pointer"`, and for instrumentation only
`GLOBAL_LDOPTS="-Wl,--no-warn-rwx-segments -Wl,--export-dynamic"`. Keep HOSTCC
native. Install hosted assets into a separate private prefix. `link --asan` and
`run --asan` select `hosted-asan-build`; failures/timeouts must remain failures.

Pinned R locators: `apps/main.c:166-249` initialization/root entry;
`apps/root_menu.c:859-866,941-981` start/WPS selection;
`apps/gui/wps.c:799-815,869-873,938-962,1048-1052` controls;
`apps/codec_thread.c:509-547` ordinary codec run/completion;
`apps/playback.c:2918-2973` completion handling;
`firmware/target/hosted/sdl/pcm-sdl.c:103-163,294-352` SDL format/callback;
`lib/rbcodec/metadata/ogg.c:133-227` single-stream/duration assumptions;
`lib/rbcodec/dsp/resample.c:39-93` fixed-point Hermite state;
`apps/settings_list.c:1624` actual `volume fade` key. Earlier trial outputs and
failed approaches remain privately retained, not overwritten or published.

Final integrity checks verified the 19 baseline copies, 1,887 recorded M3
private files, 13 M1 artifacts and originals, three archives, 318 M0 records
and 11,133 pinned extracted Rockbox files. Patch context remains verbatim;
generated evidence and build outputs remain private.
