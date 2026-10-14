# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate synthetic media and check an existing Rockbox Warble executable.

No device interfaces are used. Outputs belong in an ignored build directory.
Generation needs an existing FFmpeg; execution needs Python's standard library.
"""

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import wave


if not __debug__:
    raise RuntimeError("validation requires assertions; run Python without -O")


CASES = [(1, 1, 2.5), (1, 120, 2.5), (1, 647, 20), (2, 648, 20),
         (2, 649, 20), (1, 959, 20), (2, 960, 20), (2, 961, 20),
         (2, 48000, 20), (1, 48001, 20), (2, 123457, 20), (1, 250137, 60)]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pages(data):
    """Bounded traversal of our small generated Ogg fixtures."""
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("fixture exceeds 16 MiB")
    offset = 0
    while offset < len(data):
        if len(data) - offset < 27 or data[offset:offset + 4] != b"OggS":
            raise ValueError("truncated/invalid Ogg page")
        count = data[offset + 26]
        start = offset + 27 + count
        if start > len(data):
            raise ValueError("truncated lacing table")
        end = start + sum(data[offset + 27:start])
        if end > len(data):
            raise ValueError("truncated page body")
        yield offset, end
        offset = end


def update_crc(data, offset, end):
    data[offset + 22:offset + 26] = b"\0" * 4
    crc = 0
    for byte in data[offset:end]:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (0x04C11DB7 if crc & 0x80000000 else 0)) & 0xFFFFFFFF
    struct.pack_into("<I", data, offset + 22, crc)


def ffmpeg_run(executable, *args):
    subprocess.run([executable, "-nostdin", "-hide_banner", "-loglevel", "error",
                    *map(str, args)], check=True, timeout=60)


def generate(out, ffmpeg):
    out.mkdir(parents=True, exist_ok=False)
    valid = []
    for channels, frames, duration in CASES:
        stem = f"c{channels}-n{frames}-p{duration:g}"
        wav = out / (stem + ".wav")
        pcm = bytearray()
        for i in range(frames):
            for channel in range(channels):
                period = 240 if channel == 0 else 320
                sample = ((i % period) * 2 - period) * 16000 // period
                pcm.extend(struct.pack("<h", sample))
        with wave.open(str(wav), "wb") as stream:
            stream.setparams((channels, 2, 48000, 0, "NONE", "not compressed"))
            stream.writeframes(pcm)
        opus = out / (stem + ".opus")
        ffmpeg_run(ffmpeg, "-i", wav, "-map_metadata", "-1",
                   "-fflags", "+bitexact", "-flags:a", "+bitexact", "-c:a", "libopus", "-b:a", "64k",
                   "-vbr", "off", "-frame_duration", duration, opus)
        reference = out / (stem + ".f64")
        ffmpeg_run(ffmpeg, "-i", opus, "-f", "f64le", reference)
        assert reference.stat().st_size == frames * channels * 8
        valid.append({"input": opus.name, "reference": reference.name,
                      "frames": frames, "channels": channels})
        if frames == 48000:
            flac = out / (stem + ".flac")
            ffmpeg_run(ffmpeg, "-i", wav, "-map_metadata", "-1",
                       "-fflags", "+bitexact", "-flags:a", "+bitexact", "-c:a", "flac", flac)
            lossless_ref = out / (stem + "-pcm.f64")
            ffmpeg_run(ffmpeg, "-i", wav, "-f", "f64le", lossless_ref)
            for path in (wav, flac):
                valid.append({"input": path.name, "reference": lossless_ref.name,
                              "frames": frames, "channels": channels, "lossless": True})

    base = out / "c2-n48000-p20.opus"
    raw = base.read_bytes()
    offsets = list(pages(raw))
    # Valid nonzero initial granule position (RFC 7845 section 4.5).
    shifted = bytearray(raw)
    for offset, end in offsets[2:]:
        granule = struct.unpack_from("<q", shifted, offset + 6)[0]
        struct.pack_into("<q", shifted, offset + 6, granule + 9600)
        update_crc(shifted, offset, end)
    (out / "positive-origin.opus").write_bytes(shifted)
    ref = out / "positive-origin.f64"
    ffmpeg_run(ffmpeg, "-i", out / "positive-origin.opus", "-f", "f64le", ref)
    assert ref.stat().st_size == 48000 * 2 * 8
    valid.append({"input": "positive-origin.opus", "reference": ref.name,
                  "frames": 48000, "channels": 2})

    malformed = {}
    malformed["truncated-byte.opus"] = raw[:-1]
    malformed["missing-eos-page.opus"] = raw[:offsets[-1][0]]
    data = bytearray(raw)
    data[-1] ^= 1
    malformed["bad-crc.opus"] = data
    for name, field, value in (("missing-eos-flag.opus", "flag", 0),
                               ("excess-granule.opus", "granule", 100000),
                               ("decreasing-granule.opus", "granule", 1),
                               ("page-hole.opus", "sequence", 9)):
        data = bytearray(raw)
        offset, end = offsets[-1]
        if field == "flag":
            data[offset + 5] = value
        elif field == "sequence":
            struct.pack_into("<I", data, offset + 18, value)
        else:
            struct.pack_into("<q", data, offset + 6, value)
        update_crc(data, offset, end)
        malformed[name] = data
    short = bytearray((out / "c1-n1-p2.5.opus").read_bytes())
    offset, end = list(pages(short))[-1]
    struct.pack_into("<q", short, offset + 6, 0)
    update_crc(short, offset, end)
    malformed["granule-before-preskip.opus"] = short
    for name, data in malformed.items():
        (out / name).write_bytes(data)
    hashes = {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
              for p in sorted(out.iterdir())}
    manifest = {"valid": valid, "malformed": list(malformed), "files": hashes}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(valid)} valid and {len(malformed)} malformed fixtures")


def doubles(raw):
    values = array("d")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    return values


def measure(output, reference, channels, frames, lossless):
    raw = output.read_bytes()
    if (len(raw) < 46 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE" or
            raw[38:42] != b"data" or struct.unpack_from("<HHI", raw, 20) != (3, channels, 48000)):
        raise AssertionError("invalid/absent float WAV output")
    if len(raw) != 46 + frames * channels * 8:
        raise AssertionError(f"frame count {(len(raw)-46)//(channels*8)} != {frames}")
    if struct.unpack_from("<I", raw, 42)[0] != len(raw) - 46:
        raise AssertionError("incorrect WAV data size")
    got = doubles(raw[46:])
    assert len(reference) == len(got) and all(math.isfinite(x) for x in got)
    differences = [a - b for a, b in zip(got, reference)]
    rms_error = math.sqrt(sum(x*x for x in differences) / len(got))
    rms_signal = math.sqrt(sum(x*x for x in reference) / len(got))
    peak = max(abs(x) for x in differences)
    snr = 20 * math.log10(rms_signal / rms_error) if rms_error and rms_signal else None
    if lossless:
        assert peak == 0, "lossless PCM mismatch"
    else:
        assert peak <= 0.005 and rms_error <= 0.001, "decoded-reference error too large"
        if rms_signal > 0.01:
            assert snr is None or snr >= 40, "decoded-reference SNR below 40 dB"
    return {"frames": frames, "rms_error": rms_error, "peak_error": peak,
            "snr_db": snr, "sha256": sha(output)}


def run(corpus, warble, out, runner):
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    for name, entry in manifest["files"].items():
        path = corpus / name
        assert path.stat().st_size == entry["bytes"] and sha(path) == entry["sha256"], name
    out.mkdir(parents=True, exist_ok=False)
    results = []
    prefix = shlex.split(runner)

    def invoke(name, seek=None):
        label = name + (f"-seek{seek}" if seek is not None else "")
        output = out / (label + ".wav")
        args = prefix + [str(warble), "-f"]
        if seek is not None:
            args += ["-c", f"seek={seek}"]
        proc = subprocess.run(args + [str(corpus / name), str(output)],
                              capture_output=True, timeout=30)
        (out / (label + ".stderr")).write_bytes(proc.stderr)
        return proc, output

    for entry in manifest["valid"]:
        seeks = [None]
        if entry["input"].endswith(".opus") and entry["frames"] > 48000:
            seeks += [0, 1, 100, 500, (entry["frames"] - 1) // 48]
        reference = doubles((corpus / entry["reference"]).read_bytes())
        for seek in seeks:
            record = {"input": entry["input"], "seek_ms": seek}
            try:
                proc, output = invoke(entry["input"], seek)
                assert proc.returncode == 0, f"exit status {proc.returncode}"
                assert b"error:" not in proc.stderr.lower(), "codec reported error"
                begin = (seek or 0) * 48
                record.update(measure(output, reference[begin*entry["channels"]:],
                                      entry["channels"], entry["frames"]-begin,
                                      entry.get("lossless", False)))
                record["passed"] = True
            except (AssertionError, subprocess.TimeoutExpired) as exc:
                record.update(passed=False, error=str(exc))
            results.append(record)
    for name in manifest["malformed"]:
        record = {"input": name, "malformed": True}
        try:
            proc, _ = invoke(name)
            assert proc.returncode == 1, f"uncontrolled corrupt-stream exit {proc.returncode}"
            diagnostic = proc.stderr.lower()
            assert any(message in diagnostic for message in (
                b"error: codec error", b"error: metadata parsing failed")), "missing controlled rejection"
            assert b"AddressSanitizer" not in proc.stderr, "sanitizer error"
            record.update(passed=True, exit_status=proc.returncode)
        except (AssertionError, subprocess.TimeoutExpired) as exc:
            record.update(passed=False, error=str(exc))
        results.append(record)
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    failures = [r for r in results if not r["passed"]]
    print(json.dumps({"checks": len(results), "passed": len(results)-len(failures),
                      "failures": failures}, indent=2))
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    gen = modes.add_parser("generate")
    gen.add_argument("--out", type=Path, required=True)
    gen.add_argument("--ffmpeg", default="ffmpeg")
    check = modes.add_parser("run")
    check.add_argument("--corpus", type=Path, required=True)
    check.add_argument("--warble", type=Path, required=True)
    check.add_argument("--out", type=Path, required=True)
    check.add_argument("--runner", default="", help="explicit QEMU command prefix")
    args = parser.parse_args()
    if args.mode == "generate":
        generate(args.out.resolve(), args.ffmpeg)
        return 0
    return run(args.corpus.resolve(), args.warble.resolve(), args.out.resolve(), args.runner)


if __name__ == "__main__":
    sys.exit(main())
