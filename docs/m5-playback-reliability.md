# M5 playback reliability and instrumentation

2026-10-14. The full [Linux prototype](m5-linux-prototype.md) adds ALSA output
and kernel input validation. This report records the focused playback increment
and unresolved issues; all M3/M4 fixes and original regression fixtures remain.

## Decoder failures reach the hosted UI

`tools/rockbox-hosted-decoder-error.patch` modifies three Rockbox files, after
the preserved M3/M4 patches:

- `apps/playback.c`: record a negative status at `audio_codec_complete`, before
  deferred track-transition handling can obscure it. Release/acquire atomic
  handoff; the codec/audio path does not draw or wait for the UI.
- `apps/playback.h`: expose a consume-once error query for the hosted target.
- `apps/action.c`: consume the error on the ordinary hosted UI action loop and
  display “Decoder failed (%d). Check this file.” through the existing splash
  renderer. Delivery does not depend on remaining inside the WPS.

The change is scoped to SDLAPP, with the UI caller also guarded by software
codec configuration. It does not change ordinary codec PCM, suppress negative
completion, or replace the existing next-track behavior. It retains buffered
partial audio from a damaged track; it is not a promise to discard every sample
already decoded before the failure. A single last-error mailbox can coalesce
several failures before a UI poll, and the new message is currently English.
Filename-specific queued errors, localization and metadata-rejection messages
remain further work. No unsupported claim of complete application error coverage.

Regression evidence: valid WAV/FLAC/Opus runs have normal completion and no error
notification. Truncated Opus produces exactly one -1 completion and one
`M5_UI_ERROR_CONSUMED status=-1` observation at the normal UI query, followed by
complete valid WAV PCM. Test-only wrappers observe the query without replacing
the splash or error source. The initial deferred-completion/WPS-only attempt
did not establish this behavior; the corrected final action-loop implementation
does. The final ten-scenario suite uses a single recorded application build.

## Retained guarantees and Linux output

| Validation | Actual result |
| --- | --- |
| M3 AArch64 codec suite | 38/38 pass, using the preserved M4 ARM64 Warble/codecs and unchanged M3 corpus. The new patch does not modify codec files. |
| Native ASan codec suite | 38/38 pass with the preserved native instrumented build; leak detection remains disabled as in M4, not asserted passing. |
| Firmware inspector | 10/10 pass; inspector and fixtures unchanged. |
| Final M5 application suite | 10/10 pass: WAV, FLAC, Opus, mixed playlist, pause/resume/seek/next/previous/stop, timestamp restart, one-frame file, five cycles, invalid files and explicit unsupported-chain fallback. |
| Actual Linux PCM boundary | WAV/FLAC exact full reference; Opus 108,001 frames at 48 kHz, peak error 5 s16, SNR 68.7867 dB. QEMU WAV contains the complete application PCM music region. |
| Safety decision tests | 7 tests pass; missing verification, required policy/readings, stale/future/nonfinite inputs and invalid clock remain not-ready. No physical muting/protection claim. |

Private final application results: `build/m5/final-app/suite-results/results.json`.
Maximum recorded progress errors are WAV 60.68 ms, FLAC 47.40 ms, Opus 17 ms,
within the retained 75 ms test limit. The restart still emits 60,001 remaining
Opus frames at 1,000 ms. Steady-state playback-buffer availability remains
4,154,264 bytes after the first cycle. That does not establish heap/FD leak
freedom or comprehensive underrun recovery.

ALSA rates are selected per native-rate test: 44.1 kHz WAV/FLAC, 48 kHz Opus.
The M4 forced-44.1-kHz Opus resampling failure remains preserved: approximately
20.39 dB SNR, two-frame delay and 99,227 active frames versus 99,226 reference.
M5 does not replace that result with its passing native-rate comparison.
Mixed-rate playback still has 204 silent 44.1-kHz frames at the recorded rate
transition; it is not claimed cross-rate gapless. QEMU backend rate conversion
for mixed/error tests is not a benchmark of Rockbox's resampler or Sony hardware.

## Chained Ogg Opus: precisely bounded remaining work

The existing valid two-link fixture still fails application metadata acceptance
and advances to the valid WAV. That is a tested unsupported-input outcome,
**not chained decoding support**. The final suite explicitly reports
`chain_support: false`.

Two layers must change together:

1. R `lib/rbcodec/metadata/ogg.c:138–141, 219–225` compares the initial and last
   page serials and rejects their mismatch. Removing that check alone would
   lose link identity and still give incorrect length/seeking semantics.
2. The preserved patched `lib/rbcodec/codecs/opus.c` finalizes at the first
   validated EOS. A subsequent link needs a new OpusHead/Tags parse, fresh
   decoder/channel state, its own pre-skip and granule origin, EOS trim and a
   cumulative timeline. Time seeking must identify the link and honor its
   decoder pre-roll; a serial change without a valid boundary is not a chain.

The two identical fixture links each represent 108,001 frames; the intended
concatenation is 216,002 frames. A reliable oracle should concatenate separately
decoded links before testing a whole-stream decoder. M4 recorded that FFmpeg's
whole-chain second-link output differed from isolated-link decoding; do not
silently promote that output to a conformance oracle. Different channel counts,
pre-skips/origins, short links and malformed boundaries need deliberate tests
before broad support. M5 leaves both parser and decoder unchanged rather than
make a partial fix that compromises the ordinary passing path. This lower
priority work remains behind authentic-board integration prerequisites.

## Bounded ARM64 memory investigation

The existing M4 shared/static ASan problem was reproduced **inside the booted
ARM64 guest**, eliminating QEMU user-mode syscall translation as a sufficient
explanation. It does not eliminate QEMU CPU emulation, runtime/toolchain mismatch
or application/interceptor interactions.

`m5_linux.py prototype --memory-work` compiles the unchanged independent probe
and copies only the preserved instrumented Warble executable and WAV/Opus
modules into the private guest. Minimal probes have eight-second bounds; each
Warble run has a twelve-second TERM/KILL bound. The host VM is also bounded.
Private evidence: `m5-vm/memory/memory.log`, console and exported diagnostic
outputs; no diagnostics were disabled to turn a failure into success.

| Full-system ARM64 guest experiment | Result |
| --- | --- |
| Shared ASan valid and intentional OOB | Both SIGSEGV/139 before the probe's “entered main” marker. |
| Static ASan valid | Enters main, exits 0. |
| Static ASan intentional OOB | Enters main; reports a genuine heap-buffer-overflow and exits 1. |
| Preserved static-ASan Warble WAV | Metadata/module loading succeeds; decoding does not complete within twelve seconds; timeout termination status 143. |
| Preserved static-ASan Warble Opus | Same bounded failure after module allocations; status 143. |

The shared runtime is GCC 14's package while the static runtime is supplied by
the GCC 13 toolchain, as already recorded in M4; layout/runtime differences are
not isolated by those two builds. The exact cause remains unresolved. A useful
next bounded experiment is the same static-ASan main with uninstrumented codec
modules, followed by a debugger trace of one hung decode if authorized tooling
is justified. Do not repeat a full timeout suite or claim ARM64 memory safety.
M4's passing UBSan/minimal probes remain historical results; this guest experiment
did not rerun UBSan or validate an instrumented full application.

Normal application/guest shutdown, repeated boot, playback controls and buffer
reuse pass. They establish the tested state transitions and output, not absence
of all leaks, races, out-of-bounds accesses or kernel/driver faults.
