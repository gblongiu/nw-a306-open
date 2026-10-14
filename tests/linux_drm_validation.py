# SPDX-License-Identifier: GPL-2.0-or-later
"""Check actual QEMU scanout against completed KMS presentations and PCM."""
import argparse
import json
from pathlib import Path
import re
import linux_vm_validation as vm


def ppm(path):
    data = path.read_bytes()
    header = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\s', data)
    assert header, 'unsupported QEMU screenshot header'
    w, h = map(int, header.groups())
    pixels = data[header.end():]
    assert (w, h) == (320, 480) and len(pixels) == w*h*3
    value = 2166136261
    for byte in pixels:
        value = ((value ^ byte) * 16777619) & 0xffffffff
    assert len(set(pixels)) > 8, 'blank or unexpectedly flat scanout'
    return f'{value:08x}'


def display(directory):
    vm.boot(directory)
    text = (directory / 'kms.log').read_text()
    assert 'READY driver=virtio_gpu mode=320x480 format=XRGB8888' in text
    frames = re.findall(r'PRESENT frame=(\d+) rgb_fnv1a32=([0-9a-f]{8}) fb=(\d+)', text)
    assert len(frames) > 10 and [int(x[0]) for x in frames] == list(range(1, len(frames)+1))
    assert len({x[2] for x in frames}) == 2, 'double buffering not exercised'
    assert all(frames[i][2] != frames[i+1][2] for i in range(len(frames)-1))
    hashes = {x[1] for x in frames}
    captures = [ppm(directory / f'scanout-{i}.ppm') for i in range(3)]
    assert len(set(captures)) > 1, 'scanout did not update'
    assert all(h in hashes for h in captures), 'scanout differs from rendered RGB frame'
    assert 'restore=0 drop_master=0' in text and 'M6_KMS_ERROR' not in (directory/'app.log').read_text()
    return {'case': directory.name, 'presentations': len(frames),
            'distinct_rendered_frames': len(hashes), 'scanout_rgb_fnv1a32': captures,
            'cleanup': 'CRTC restored and DRM master released'}


def validate(a):
    results = [display(d) for d in [a.wav, a.flac, a.opus, a.touch, a.repro]]
    assert len({json.loads((d/'result.json').read_text())['rockbox_sha256']
                for d in [a.wav,a.flac,a.opus,a.touch,a.repro]}) == 1
    results += [vm.track(a.corpus,a.wav,'signal.wav',44100,True),
                vm.track(a.corpus,a.flac,'signal.flac',44100,True),
                vm.track(a.corpus,a.opus,'signal.opus',48000,False)]
    text = (a.touch/'evdev.log').read_text()
    for x,y in [(160,240),(80,300),(140,300),(220,300)]:
        assert any('ROCKBOX button=' in s and not s.startswith('ROCKBOX button=0 ') and
                   f'xy={x},{y}' in s for s in text.splitlines()), (x,y)
    assert 'CLEANUP complete' in text
    states = [r for r in vm.events(a.touch/'trace.tsv') if r['event']=='state']
    paused = [r for r in states if int(r['status']) & 2]
    assert len(paused)>=2 and len({r['elapsed'] for r in paused}) == 1
    assert any(int(r['tick'])>int(paused[-1]['tick']) and r['status']=='1' and
               int(r['elapsed'])>int(paused[-1]['elapsed']) for r in states)
    results.append({'case':'KMS_touch_alignment_pause_resume_drag','passed':True})
    assert vm.sha(a.wav/'root.cpio.gz') == vm.sha(a.repro/'root.cpio.gz')
    results.append({'case':'KMS_repeated_boot_identical_initramfs','passed':True})
    with a.out.open('x') as f:
        json.dump(results,f,indent=2);f.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['corpus','wav','flac','opus','touch','repro','out']:
        p.add_argument('--'+n,type=Path,required=True)
    validate(p.parse_args())
