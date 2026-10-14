# M5 Android-free generic ARM64 Linux prototype

2026-10-14. A real ARM64 Linux guest now boots directly into the Rockbox
application, plays local music through Linux ALSA/virtio sound, accepts synthetic
touch through Linux evdev, and powers down. There is no Android userspace.
This is a generic QEMU `virt` machine, **not NW-A306 boot or hardware validation**.
Sony integration requirements are in [the hardware plan](m5-hardware-evidence-plan.md).

## Baseline preservation

All 26 project files were copied
and size/SHA-256 verified in ignored `build/m5-baseline-20261014/`.
Snapshot manifest SHA-256:
`7319c4650c586df9b88c36bfb6bab48377a39b3d17ec9eab43f3fb2036671892`.
It also records 1,593 private M4 Windows files. All 13 M1 artifacts, three pinned
archives, 318 M0 records, 1,887 recorded M3 private files, the 48-file M3 corpus
and 32-file M4 corpus passed their existing size/hash checks. Original private
evidence remains at its original location; no original was replaced or deleted.

M2's 41 outputs and M3's native and ARM64 sets of 41 outputs each match their
recorded hash lists. M4's 42 application/codec outputs match its final manifest
and were also copied and reverified in private
`~/.cache/nwa306-open/m5-baseline-20261014/`; that manifest hashes to
`b69880f38781b37168f768ffa428c4a40a5d918cb38de55619e347f9c095cba7`.
The old patches, corpus, toolchain and source archives remain unchanged.
New compilation uses fresh `m5/` and `m5-repro/` working copies.

## Exact system and dependency provenance

| Component | Executed configuration / reason |
| --- | --- |
| Virtual machine | Privately unpacked Ubuntu QEMU system ARM `1:8.2.2+ds-0ubuntu1.18`, x86-64 host, TCG, `virt`, Cortex-A53, two CPUs, 512 MiB RAM; no network, disk, USB or physical-device passthrough |
| Kernel | Alpine 3.21.8 aarch64 `virt`, Linux `6.12.110-0-virt`; direct `-kernel`/`-initrd`, console `ttyAMA0`, `/init` PID 1 |
| Minimal root | BusyBox and musl loader selected from Alpine's 3.21.8 minirootfs; only required applet links, proc/sys/dev mounts, Rockbox assets/codecs, glibc libraries and synthetic music |
| Userspace ABI | AArch64/LP64 ELF, glibc 2.39 loader/libc/libm from the existing M3 cross sysroot; BusyBox separately uses musl. No Android linker or framework. |
| Rockbox | R `afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09`, existing normal `sdlapp`, 320x480, M3 Opus patch + M4 playback patch + M5 hosted decoder-error patch and test-only link wrappers |
| Linux sound | ALSA-lib 1.2.11 built statically; SDL 2.30.0 rebuilt with its existing ALSA backend. `hw` PCM on the generic virtio card; QEMU WAV output backend. No Sony mixer/control sequence. |
| Guest modules | `evdev`, `uinput`, `snd`, `snd-timer`, `snd-pcm`, `virtio_snd`; dependency order taken from the matching modloop's `modules.dep`. Virtio console is built into this kernel. |
| Input test | `tests/linux_evdev_touch.c`: synthetic ABS_X/Y + BTN_TOUCH → uinput → actual kernel evdev → SYN_REPORT batches → SDL mouse events → ordinary Rockbox touchscreen mapping |
| Display | Existing SDL software rendering with dummy video, captured BMP. No X/Wayland/Mesa added. No DRM modeset, virtual scanout, Sony panel or backlight claim. A board KMS backend remains an integration requirement. |
| Supervision | One foreground Rockbox process; BusyBox timeout TERM/KILL bound, captured exit status, evidence export, kernel poweroff. No restart loop, storage writer or unattended recovery attempt. |

The main suite and VM build SHA-256 is
`ef5a8fbcb6f63a41217a3a9bbca5e778467e7b4a16dab8aecb6e0fb3cb70652a`.
Fresh build under the separate `m5-repro` prefix:
`da71268894b823d128dc96c0b51ebd2dbf62cecca90ecf316728cceeb6f531d7`.
Absolute configured asset/debug paths differ between prefixes; those binaries
are not claimed byte-identical. Both boot and play independently checked WAV.
Two forced full builds **at the same prefix** reproduce all 42/42 hashes,
including the main-suite binary above.

Twenty new input files are pinned in `tools/m5-linux.lock.json`: three QEMU
packages, twelve required host runtime-library packages, the minirootfs,
matching kernel/config/modloop, and ALSA source. Packages are unpacked privately,
never installed and never run through package-maintainer scripts. The QEMU and
minirootfs hashes were checked against publisher metadata; kernel/config/modloop
and ALSA hashes pin the bytes acquired over official HTTPS, **without a claim
of independently verified publisher signatures**. The existing 15-package
toolchain lock and SDL source hash are retained.

Kernel/config/modules are from the same immutable
[Alpine 3.21.8 netboot directory](https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/aarch64/netboot-3.21.8/),
not the changing latest kernel package. The rootfs source is in the
[official release directory](https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/aarch64/).
ALSA source: [official 1.2.11 archive](https://www.alsa-project.org/files/pub/lib/alsa-lib-1.2.11.tar.bz2).
QEMU documents the Linux `CONFIG_SND_VIRTIO` requirement and
[virtio-sound interface](https://www.qemu.org/docs/master/system/devices/virtio/virtio-snd.html);
the actual pinned 8.2.2 binary's device options and successful guest enumeration
were also checked, rather than assuming current documentation proves support.

These components retain their respective licenses: Linux/QEMU/BusyBox GPL,
glibc and ALSA LGPL, musl MIT, SDL zlib, and Rockbox plus its derivative patches
the applicable Rockbox GPL terms. Input/source/license provenance is a development
record, not a ready-to-distribute compliance bundle. No firmware or generated
binaries are public project deliverables.

## Boot, output and control results

Private `build/m5/linux-results.json` contains seven passing checks. Exact final
VM runs are under `~/.cache/nwa306-open/m5-vm/`: `final-wav`, `flac-final`,
`opus-final`, `touch-final2`, `error-ui`, `fault`, `wav-repro`.
Each result records the QEMU command, application/initramfs hashes, module set,
exit status and exported artifact hashes. Console logs establish kernel startup,
PID 1, ALSA card enumeration and kernel poweroff.

| Check | Independently checked result |
| --- | --- |
| WAV | All 99,226 stereo frames at 44,100 Hz match the reference exactly in both application callback and virtual sound output. |
| FLAC | All 99,226 stereo frames at 44,100 Hz match exactly at both boundaries. |
| Opus | All 108,001 stereo frames at 48,000 Hz; peak reference error 5 s16 units, SNR 68.7867 dB. The virtual sound file contains the complete actual callback music bytes exactly. |
| Real kernel touch path | Two centre taps pause/resume; elapsed time remains 913 ms during observed pause. A drag delivers x=80→140→220, y=300 and release to Rockbox. Three presses/releases and cleanup verified. This is single-contact transport and representative UI control, not multitouch or Sony touch validation. |
| Decoder failure | Truncated Opus completes with -1, UI consumes that error once, then the valid WAV plays completely. Valid files produce no decoder-error notification. |
| Missing application | Injected absent executable returns 127; no application PCM capture is created; guest powers down cleanly. It does not test every possible hung kernel/service failure. |
| Repeated boot | Identical initramfs SHA-256 `4673162034b50959db00b62237f8559ea3458b6e7f90e8c4d2bb5f97978a8b9d`; both boots deliver the full exact WAV and shut down. |

The WAV backend receives Linux virtual-device output, independently of the
post-SDL-callback capture. Initial virtual-output silence is 2,048 frames for
WAV/FLAC and 8,192 frames in the recorded Opus run. Remaining output is silence;
callback and virtual-file totals include buffering/startup/shutdown silence and
can vary with scheduling. Musical frame counts, ordering and rates are verified;
the entire WAV-file duration is not represented as track duration or a hardware
latency measurement. Neutral DSP settings are the unchanged M4 configuration.
QEMU reports an unavailable input voice for its output-only WAV backend;
the output captures pass independently. No microphone or host audio device is
passed through.

Evidence leaves the guest through a named **virtual serial port**, never a
shared physical disk. Early UART-only export exceeded the bounded runtime and
was retained as a failed harness attempt. An initial input-hook attempt wrapped
`SDL_Init` although Rockbox uses `SDL_InitSubSystem`; its playback success was
not counted as input success. The corrected hook and an explicit final relink
are in the published script. Early WPS-only error observation was insufficient;
the final action-loop error delivery is covered by the final tests.

## Reproduction

Run in WSL/Linux, from this project. These commands use only ignored/private
paths. `--work` for `build` and `--out` for `prototype` must be fresh; existing
inputs are verified, never silently replaced. `inputs --download` is the only
step that downloads new dependencies. The original Rockbox archive is unchanged.

```sh
P=/path/to/nw-a306-open
B="$HOME/.cache/nwa306-open"
python3 "$P/tools/m5_linux.py" inputs --vm-dir "$B/m5-vm" --download
python3 "$P/tools/m5_linux.py" build --work "$B/m5-repro" --vm-dir "$B/m5-vm" \
  --source "$P/.local-references/upstream/rockbox/rockbox-afe91f1dfb1c9d90da928bb2bf8a0fbc6957ff09" \
  --sdl-archive "$B/m2/inputs/SDL2-2.30.0.tar.gz" --previous-inputs "$B/m4/inputs"
python3 "$P/tools/m5_linux.py" prototype --work "$B/m5-repro" --vm-dir "$B/m5-vm" \
  --corpus "$P/build/m4/corpus4" --out "$B/m5-vm/fresh-build-wav" --playlist wav.m3u
```

The recipe was executed successfully with the original local paths. Choose new
private suffixes on a
repeat run. Additional playlists/rates, `--touch`, `--fault`, and the bounded
`--memory-work` experiment are exposed by `--help`. `tests/linux_vm_validation.py`
accepts explicit corpus/run paths and checks hashes, Linux output, touch state,
error propagation, fault shutdown and initramfs reproducibility. M4's unchanged
`playback_validation.py` remains the ten-scenario application validator.

The tool needs existing Python 3.12, make/native GCC, cpio, dpkg-deb and
unsquashfs in WSL, plus the pinned private cross toolchain. No system package,
Windows driver or host boot setting was installed or changed. The root image
is approximately 25 MiB unpacked and 9.3 MiB compressed in the final playback configuration; memory-probe
variants add diagnostic binaries/libraries. No additional service framework is
required. This is a supervised host prototype, not an installer or a Sony boot image.
