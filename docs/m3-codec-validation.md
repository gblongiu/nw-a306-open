# M3 Opus correctness and codec validation

Date: 2026-10-13, America/New_York. The implemented host correction and tests
are against official Rockbox revision `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`
(R in the [M0 register](feasibility.md#evidence-register)).

## Baseline preservation

All 11 project files and existing M2 Windows records/fixtures were copied and
verified in private
`build/m3-baseline-20261013/`: **35 files total**. Its
`snapshot-manifest.json` records paths, sizes and SHA-256 values; manifest SHA-256
`13c3a539308f2fcde1398bfa118f476cba6c85f9abd40051ae915a58af6fbafb`.
The destination is covered by the existing `build/` exclusion. Sources remained
unchanged during snapshotting, and existing originals were not replaced.

All 13 preserved M1 artifacts matched their custody ledger; all three pinned
source archives matched their recorded SHA-256 values. M2's 41 binary/module
hashes and its inspector baseline were verified. Private development uses
separate WSL source/build copies; `.local-references/`, M1 firmware and M2
results remain preserved. No upstream snapshot was patched in place.

## Root causes and upstream comparison

The current official upstream was resolved to
[`0d117dc62cf61f24870a25fd38bbe71fd03afcf8`](https://github.com/Rockbox/rockbox/tree/0d117dc62cf61f24870a25fd38bbe71fd03afcf8).
Its `lib/rbcodec/codecs/opus.c` is byte-identical to R: SHA-256
`3fcaeabd9aa1d44c132d8987d354e402331d8e4d83811793f7b5855c30edee16`.
Thus the observed problem is also present in that inspected upstream source;
this statement does not cover future revisions.

The defect is in Ogg/Opus integration, with separate harness/build problems:

| Finding | Exact pinned source | Correction |
| --- | --- | --- |
| Final audio packet omitted | `opus.c:454` excludes `op.e_o_s` from the packet loop | Decode the EOS packet and trim its output using the final page endpoint |
| Ordinary EOF reports codec error | `opus.c:359,434-435,528-532` initializes error and reaches `done` without a successful EOS transition | Return success only after a validated EOS packet or requested halt; missing/truncated termination remains an error |
| End trimming absent | `opus.c:505-510` inserts decoded frames after preskip without final-granule trimming | Keep preskip and final-page trimming separate; validate granule progression |
| Packet/page errors can be skipped | `opus.c:439,449,454`; the old header path seeks past comment pages | Consume the comment packet in sequence and reject page/packet holes instead of disguising them as completion |
| Time seeking guesses packet position and delays commands | `opus.c:409-430,481-497`; commands normally checked only between read batches | Check commands before audio packets; restart the existing decoder and decode/discard to the requested sample position |
| Codec error leaves exit status zero | `warble.c:890-891,974-981` | Propagate codec failure through cleanup to the process exit status |
| Signed-16 float output has half amplitude | `warble.c:229-241,471-498,597-598` uses sample-depth 16 as a fractional shift although the input is `int16_t` | Normalize the signed-16 path by 2^15; retain codec-declared fractional scaling for wider samples |
| Cross-link uses a native compiler | `warble.make:32` links target objects with `HOSTCC` | Link Warble with `CC`; keep `HOSTCC` native for build-time generators |

[RFC 7845](https://www.rfc-editor.org/rfc/rfc7845.html), sections 3 and 4.2-4.6,
defines packet organization, preskip, PCM position, EOS trimming, initial
granules and seek preroll. The patch decodes the final packet, discards preskip,
and limits emitted samples to the final page endpoint. It allows a nonzero
initial granule origin, rejects inconsistent subsequent progression, and does
not equate exhausted input with a valid EOS. Decode-from-start seeking retains
the full decoder history before the requested output position.

## Patch and boundaries

[`rockbox-opus-correctness.patch`](../tools/rockbox-opus-correctness.patch) changes
only `opus.c`, `warble.c` and the one Warble link command. It applies with GNU
patch `--batch --fuzz=0 -p1` to a private copy of R. It is derivative Rockbox
work under the applicable GPL terms, identified as GPL-2.0-or-later; upstream
source notices remain intact. No Sony payload or proprietary code is included.

The patch uses the existing libogg/libopus implementation and existing output
buffer; it does not add a decoder or allocate whole streams. The decoder's
maximum frame capacity accounts for channel count. Restart seeks reuse/reset
the decoder rather than allocating a new one on every header. This favors
correctness over fast seeking: work grows with the seek destination. A later
page-seek optimization must preserve the regression results.

Scope is the tested single logical Opus stream, mono/stereo mapping supported
by the existing decoder. Chained/multiplexed streams, broad fuzzing and every
possible cropped-stream layout are not validated. Byte-offset startup resume
is explicitly rejected, including an offset/elapsed combination; restoring
timestamp-aware startup resume needs a separate regression before full hosted
playback integration. Tested time-seek commands are a separate supported path.
Complete Ogg conformance and NW-A306 playback remain unverified. Existing unused legacy seek helpers remain; no
unrelated source refactoring was performed.

## Deterministic corpus and independent reference

[`codec_regression.py`](../tests/codec_regression.py) generates original integer
triangle-wave PCM and encodes with the existing Windows FFmpeg
`9.0.1-full_build-www.gyan.dev`. The independent reference is FFmpeg's decoded
float64 PCM. No private recording or firmware is used. Opus output is compared
to decoded reference audio, not required to equal the lossy encoder's input.
`opusdec`/`opusinfo` were not installed; FFmpeg provided the available reference.

| Fixtures | Coverage |
| --- | --- |
| 12 Opus streams | Mono/stereo; 1, 120, 647, 648, 649, 959, 960, 961, 48000, 48001, 123457 and 250137 input frames at 48 kHz; 2.5/20/60-ms packets |
| Positive-origin Opus | Valid multi-page stream with audio granules shifted by 9600; expected PCM length unchanged |
| WAV and FLAC | Stereo 48000-frame lossless control cases |
| 15 seek checks | Five initial seeks on each of the three longer streams: 0, 1, 100, 500 ms and the final available whole-millisecond position |
| Eight malformed inputs | Truncated final byte, missing EOS page, bad CRC, missing EOS flag, excessive/decreasing granule, page-sequence hole, first EOS granule below preskip |

Each run contains **38 checks**: 15 valid decodes, 15 seeks and eight malformed
cases. Assertions cover completion status, error diagnostics, exact post-trim
frame counts, WAV structure, finite samples and reference-signal metrics.
Lossless controls match exactly. Opus thresholds were set to peak error <=0.005,
RMS error <=0.001, and SNR >=40 dB where reference RMS exceeds 0.01. Measured
minimum nonzero SNR was approximately **61.29 dB**, maximum peak error 0.002148.
Timeouts bound each subprocess to 30 seconds; crashes are failures, including
when a malformed fixture is expected to return a controlled error.

Malformed checks require exit status 1 and a recognized codec or metadata error
diagnostic; a positive QEMU signal exit is not accepted. The decreasing-granule
and below-preskip fixtures are rejected by Warble's metadata parser before
codec execution, so those two cases do not exercise the codec's own guards.

Generation was repeated. All **48 fixture/reference file sizes and SHA-256
values** reproduced; canonical manifest SHA-256:
`a75e169d4ab565a2ad6a68ee315bb428388d868157d298a93640c96888cf62c9`.
An initial generator placed FFmpeg's bitexact muxer flag on the input side;
repetition exposed random Ogg serial numbers. Moving the flag to the output
side corrected reproducibility. Earlier trial artifacts were retained privately.

## Actual results

| Execution | Result |
| --- | --- |
| Unpatched M2 native executable | 4/38 checks pass, **34 fail**; all 28 valid Opus/seek checks fail; six malformed cases incorrectly exit zero |
| Patched native x86-64 Linux | **38/38 pass** |
| Patched AArch64 under QEMU user mode | **38/38 pass**; all 30 valid/seek PCM output hashes equal native outputs |
| Native AddressSanitizer | **38/38 pass**, no reported invalid memory access; leak detection disabled, so leaks are not assessed |
| Fresh isolated AArch64 build | **38/38 pass** on both the trial and final corpus; all 30 final PCM hashes equal native outputs |
| AArch64 AddressSanitizer attempt | Runtime crashes before decoding for every fixture, including WAV; an empty ASan probe also exits 139. Target memory instrumentation remains unverified |

Both native and AArch64 forced rebuilds reproduced **41/41 executable/codec
hashes** in their respective same-path environments. A first forced cross-build
with `HOSTCC` overridden produced ARM build generators and failed to run
`bmp2rb`. The one-line Warble link fix removes that workaround; the subsequent
forced cross-build preserves native generators and reproduces all hashes.
Cross-path builds have different hashes because paths are embedded in debug
information and codec lookup; no cross-machine bit-reproducibility claim is made.

Native ASan instruments application and codec compilation/linking explicitly;
Warble clears configure's ordinary `GCCOPTS`, so merely enabling a configure
sanitizer switch would not establish instrumentation. Existing inspector tests
remain **10/10 passing**; the inspector and its tests are unchanged.

## Reproduce

Generate on the Windows host with its recorded FFmpeg build:

```powershell
.\.venv\Scripts\python.exe tests/codec_regression.py generate --out build/m3/corpus-new
```

Prepare/build using the Linux commands in
[AArch64 bring-up](m3-aarch64-bringup.md#reproduction). Then, from Linux:

```sh
python3 tests/codec_regression.py run --corpus /path/to/corpus-new \
  --warble "$work/native-build/warble.ipodvideo" --out /path/to/new-native-results
python3 tests/codec_regression.py run --corpus /path/to/corpus-new \
  --warble "$work/arm64-build/warble.ipodvideo" --out /path/to/new-arm-results \
  --runner "$work/environment/usr/bin/qemu-aarch64-static -L $work/environment/usr/aarch64-linux-gnu"
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 python3 tests/codec_regression.py run \
  --corpus /path/to/corpus-new --warble "$work/asan-build/warble.ipodvideo" \
  --out /path/to/new-asan-results
```

Output directories must be fresh. The runner first verifies every corpus
size/hash, writes private per-case stderr/results, and exits nonzero for any
failure. The unpatched baseline is intentionally expected to fail. Build and
execution details, ABI limits and hosted-application evidence are separate in
the linked report.

## Completion checks

Final checks reverified the 35 baseline copies, all 13 M1 artifacts and their
originals, three source archives, 318 private M0 records and all 41 preserved M2
build outputs. All 11,133 files in the preserved extracted Rockbox tree matched
the pinned archive. Only the roadmap changed among the original public files.
The final three-file patch also applied to a fresh private source copy and
produced the same patched source bytes.

Inspector tests passed 10/10 on Windows and Linux. Public deliverables contain
source, patches, pinned package metadata and reports. Firmware, raw private
evidence, generated media and binaries remain excluded.
