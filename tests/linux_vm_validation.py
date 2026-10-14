# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate captured generic Linux VM evidence, never physical hardware."""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import wave


if not __debug__:
    raise RuntimeError("validation requires assertions; run Python without -O")


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def events(path):
    rows = []
    for line in path.read_text().splitlines():
        fields = line.split('\t')
        rows.append({'event': fields[0]} | dict(x.split('=', 1) for x in fields[1:] if '=' in x))
    return rows


def boot(directory, expected=0):
    report = json.loads((directory / 'result.json').read_text())
    assert report['qemu_exit'] == 0 and report['app_exit'] == expected and report['clean_poweroff']
    log = (directory / 'console.log').read_text()
    assert 'M5_INIT kernel=6.12.110-0-virt' in log and 'VirtIO SoundCard' in log
    for name, digest in report['artifacts'].items():
        assert sha(directory / name) == digest, name
    return report


def track(corpus, directory, name, rate, lossless):
    boot(directory)
    reference = (corpus / (name + ('.s16' if lossless else '.native.s16'))).read_bytes()
    callback = (directory / 'output.s16').read_bytes()
    assert len(callback) >= len(reference) and len(callback) % 4 == 0
    music = callback[:len(reference)]
    got, ref = array('h'), array('h')
    got.frombytes(music)
    ref.frombytes(reference)
    if sys.byteorder != 'little':
        got.byteswap()
        ref.byteswap()
    peak = max(abs(a-b) for a, b in zip(got, ref))
    rms = math.sqrt(sum((a-b)**2 for a, b in zip(got, ref)) / len(ref))
    signal = math.sqrt(sum(a*a for a in ref) / len(ref))
    snr = 20 * math.log10(signal/rms) if rms else None
    assert peak == 0 if lossless else peak <= 5 and snr >= 60
    assert not any(callback[len(reference):]), 'non-silent callback tail'
    with wave.open(str(directory / 'virtio.wav')) as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (2, 2, rate)
        delivered = f.readframes(f.getnframes())
    offset = delivered.find(music)
    assert offset >= 0 and offset % 4 == 0, 'complete PCM absent from Linux/virtio output'
    assert not any(delivered[:offset]) and not any(delivered[offset+len(music):])
    rows = events(directory / 'trace.tsv')
    assert any(r['event'] == 'codec_load' and r['status'] == '0' for r in rows)
    assert any(r['event'] == 'codec_complete' and r['value'] == '0' for r in rows)
    assert not any(r['event'] == 'watchdog' for r in rows)
    assert 'M5_UI_ERROR_CONSUMED' not in (directory / 'app.log').read_text()
    return {'case': name, 'music_frames': len(music)//4, 'rate': rate,
            'callback_frames': len(callback)//4, 'virtual_output_frames': len(delivered)//4,
            'virtual_output_start_frame': offset//4, 'peak_error_s16': peak, 'snr_db': snr,
            'pcm_sha256': sha(directory / 'output.s16'), 'wave_sha256': sha(directory / 'virtio.wav')}


def validate(args):
    corpus = args.corpus
    for name, item in json.loads((corpus / 'manifest.json').read_text())['files'].items():
        assert (corpus / name).stat().st_size == item['bytes'] and sha(corpus / name) == item['sha256']
    results = [track(corpus, args.wav, 'signal.wav', 44100, True),
               track(corpus, args.flac, 'signal.flac', 44100, True),
               track(corpus, args.opus, 'signal.opus', 48000, False)]
    reports = [boot(d) for d in [args.wav, args.flac, args.opus, args.touch, args.error, args.repro]]
    assert len({r['rockbox_sha256'] for r in reports}) == 1, 'mixed application builds'
    touch = (args.touch / 'evdev.log').read_text()
    assert 'CAPS x=0..319 y=0..479 BTN_TOUCH' in touch and 'CLEANUP complete' in touch
    for x, y in [(160, 240), (80, 300), (140, 300), (220, 300)]:
        assert any('ROCKBOX button=' in s and not s.startswith('ROCKBOX button=0 ') and
                   f'xy={x},{y}' in s for s in touch.splitlines()), (x, y)
    assert touch.count('SDL type=1025 ') == 3 and touch.count('SDL type=1026 ') == 3
    assert 'SDL type=1024 x=140 y=300 down=1' in touch
    assert 'SDL type=1024 x=220 y=300 down=1' in touch
    states = [r for r in events(args.touch / 'trace.tsv') if r['event'] == 'state']
    paused = [r for r in states if int(r['status']) & 2]
    assert len(paused) >= 2 and len({r['elapsed'] for r in paused}) == 1
    assert any(int(r['tick']) > int(paused[-1]['tick']) and r['status'] == '1' and
               int(r['elapsed']) > int(paused[-1]['elapsed']) for r in states)
    results.append({'case': 'kernel_touch_pause_resume_drag', 'paused_ms': int(paused[0]['elapsed']),
                    'gesture_scope': 'coordinates and release delivered; no multitouch claim'})
    errors = events(args.error / 'trace.tsv')
    assert sum(r['event'] == 'codec_complete' and r['value'] == '-1' for r in errors) == 1
    assert sum(r['event'] == 'codec_complete' and r['value'] == '0' for r in errors) == 1
    assert (args.error / 'app.log').read_text().count('M5_UI_ERROR_CONSUMED status=-1') == 1
    assert (args.error / 'output.s16').read_bytes().find((corpus / 'signal.wav.s16').read_bytes()) >= 0
    results.append({'case': 'decoder_error_ui_then_valid_track', 'passed': True})
    boot(args.fault, 127)
    assert not (args.fault / 'output.s16').exists(), 'failed app unexpectedly activated audio'
    results.append({'case': 'missing_application_safe_poweroff', 'passed': True})
    assert sha(args.wav / 'root.cpio.gz') == sha(args.repro / 'root.cpio.gz'), 'initramfs not reproducible'
    track(corpus, args.repro, 'signal.wav', 44100, True)
    results.append({'case': 'repeated_boot_and_identical_initramfs', 'passed': True,
                    'sha256': sha(args.repro / 'root.cpio.gz')})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as f:
        json.dump(results, f, indent=2)
        f.write('\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['corpus', 'wav', 'flac', 'opus', 'touch', 'error', 'fault', 'repro', 'out']:
        p.add_argument('--' + name, type=Path, required=True)
    validate(p.parse_args())
