# SPDX-License-Identifier: GPL-2.0-or-later
"""Generic ARM64 virtio DRM test only; no host device passthrough.

Reuses the pinned M5 environment and test controller. Writes only to private
build/cache paths. Run after tools/m5_linux.py build in a fresh private workdir.
DRM headers are selected, hash-checked members of the pinned Sony source archive.
"""
import argparse
import base64
import gzip
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tarfile
import time
import m5_linux as m5

HEADERS = {
    'drm.h': 'db00f6d1630faeb5b662d966258a4e0a8e5b47dad42bc1c5fe14647069726e19',
    'drm_mode.h': 'f7c1e510b96214166ceb68fcee72a6e85d1f5c2b21acbd8c01ff62cb6e1a2e24',
    'drm_fourcc.h': '5964ff18eaa2a4e0ae9e99b41adbefc9a53eb4af95f31b78a9b2eb72ab69c731',
}
# These are input hashes, not a claim that Sony's target kernel runs in this VM.


def link(work, archive):
    headers = work / 'drm-headers'
    headers.mkdir(exist_ok=True)
    with tarfile.open(archive) as t:
        for name, expected in HEADERS.items():
            member = t.getmember('kernel/msm-4.19/include/uapi/drm/' + name)
            if not member.isfile() or member.size > 100000:
                raise ValueError('unexpected UAPI member')
            data = t.extractfile(member).read()
            import hashlib
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('UAPI hash mismatch')
            p = headers / name
            if p.exists() and p.read_bytes() != data:
                raise ValueError('existing private header differs')
            if not p.exists():
                p.write_bytes(data)
    d = work / 'hosted-build'
    objs = [d / n for n in ['m6-playback.o', 'm5-input.o', 'm6-kms.o']]
    wrappers = ['root_menu', 'get_action', 'SDL_OpenAudioDevice', 'SDL_RenderPresent',
                'codec_load_file', 'audio_codec_complete', 'get_metadata_ex',
                'SDL_InitSubSystem', 'SDL_Quit', 'button_read_device', 'audio_take_decoder_error']
    make = d / 'm6-adapter.make'
    text = 'export LDOPTS += ' + ' '.join('-Wl,--wrap=' + n for n in wrappers) + '\n'
    text += f'{d}/rockbox: ' + ' '.join(map(str, objs)) + '\n'
    for obj, source, flags in zip(objs,
            ['hosted_playback.c', 'linux_evdev_touch.c', 'linux_drm_scanout.c'],
            ['-D__wrap_SDL_RenderPresent=m4_present', '', '-I' + str(headers)]):
        text += f'{obj}: {m5.PROJECT}/tests/{source}\n\t$(CC) $(CFLAGS) {flags} -c $< -o $@\n'
    make.write_text(text)
    if objs[-1].exists():
        objs[-1].touch()  # wrapper flags are not tracked by upstream Make
    with (d / 'm6-link.log').open('wb') as log:
        for target in ['all', 'install']:
            m5.call(['make', '-f', 'Makefile', '-f', make, '-j4', target],
                    d, m5.environment(work), log)
    print('M6 application SHA256', m5.sha(d / 'rockbox'))


def pack(root, destination):
    for p in [*sorted(root.rglob('*')), root]:
        os.utime(p, (0, 0), follow_symlinks=False)
    names = b'\0'.join(str(p.relative_to(root)).encode() for p in sorted(root.rglob('*'))) + b'\0'
    result = subprocess.run(['cpio', '--null', '-o', '--format=newc', '--reproducible',
                             '--owner=0:0'], cwd=root, input=names, capture_output=True, check=True)
    with destination.open('wb') as f:
        with gzip.GzipFile(filename='', fileobj=f, mode='wb', mtime=0) as g:
            g.write(result.stdout)


def run(work, vm, corpus, out, playlist, rate, touch, unsupported_mode=False):
    m5.inputs(vm)
    out.mkdir(parents=True, exist_ok=False)
    exports, modules = m5.rootfs(work, vm, corpus, out, playlist, touch, False)
    root = out / 'root'
    deptext = subprocess.check_output(['unsquashfs', '-cat', vm / 'inputs/modloop-virt',
                        'modules/6.12.110-0-virt/modules.dep'], text=True)
    deps = {line.split(':')[0]: line.split(':')[1].split() for line in deptext.splitlines()}
    extra = []
    def add(n):
        if n in modules or n in extra:
            return
        for dep in deps[n]:
            add(dep)
        extra.append(n)
    add('kernel/drivers/gpu/drm/virtio/virtio-gpu.ko')
    for n in extra:
        data = subprocess.check_output(['unsquashfs', '-cat', vm / 'inputs/modloop-virt',
                                        'modules/6.12.110-0-virt/' + n])
        (root / 'modules' / Path(n).name).write_bytes(data)
    init = (root / 'init').read_text()
    init = init.replace('printf \'M5_INIT', '\n'.join('insmod /modules/' + Path(n).name +
              ' || fatal drm_module' for n in extra) + "\nprintf 'M5_INIT")
    init = init.replace('export RBROOT=', 'export M6_DRM_GUEST=generic-arm64-vm\nexport RBROOT=')
    init = init.replace('} > "$port"', 'if [ -f /run/kms.log ]; then echo M5_BEGIN_kms.log; '
              'base64 /run/kms.log; echo M5_END_kms.log; fi\n} > "$port"')
    (root / 'init').write_text(init)
    pack(root, out / 'root.cpio.gz')
    qemu = vm / 'qemu'
    env = os.environ | {'LD_LIBRARY_PATH': str(qemu / 'usr/lib/x86_64-linux-gnu'),
                       'QEMU_MODULE_DIR': str(qemu / 'usr/lib/x86_64-linux-gnu/qemu')}
    qmp = out / 'qmp.sock'
    if len(str(qmp)) > 100:
        raise ValueError('QMP socket path too long')
    command = [str(qemu / 'usr/bin/qemu-system-aarch64'), '-machine', 'virt', '-cpu', 'cortex-a53',
        '-m', '512', '-smp', '2', '-accel', 'tcg', '-nodefaults', '-no-reboot',
        '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-nic', 'none',
        '-qmp', f'unix:{qmp},server=on,wait=off',
        '-device', 'virtio-gpu-pci,xres=' + ('640' if unsupported_mode else '320') + ',yres=480',
        '-kernel', str(vm / 'inputs/vmlinuz-virt'), '-initrd', str(out / 'root.cpio.gz'),
        '-append', 'console=ttyAMA0 rdinit=/init panic=-1',
        '-audiodev', f'wav,id=capture,path={out}/virtio.wav,out.frequency={rate},out.channels=2,out.format=s16',
        '-device', 'virtio-sound-pci,audiodev=capture', '-device', 'virtio-serial-pci',
        '-chardev', f'file,id=evidence,path={out}/export.txt', '-device',
        'virtserialport,chardev=evidence,name=m5.evidence']
    captures = []
    with (out / 'console.log').open('xb') as log:
        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 100
        try:
            while process.poll() is None and time.monotonic() < deadline:
                if b'M6_KMS_READY' in (out / 'console.log').read_bytes():
                    break
                time.sleep(.05)
            if process.poll() is None and qmp.exists() and b'M6_KMS_READY' in (out/'console.log').read_bytes():
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect(str(qmp))
                    stream = s.makefile('rwb', buffering=0)
                    json.loads(stream.readline())
                    def request(name, args=None):
                        stream.write((json.dumps({'execute': name, 'arguments': args or {}}) + '\n').encode())
                        while True:
                            r = json.loads(stream.readline())
                            if 'error' in r:
                                raise RuntimeError(r)
                            if 'return' in r:
                                return r
                    request('qmp_capabilities')
                    for i in range(3):
                        time.sleep(.35)
                        p = out / f'scanout-{i}.ppm'
                        request('screendump', {'filename': str(p)})
                        captures.append(p.name)
            process.wait(timeout=max(1, deadline-time.monotonic()))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    data = (out / 'console.log').read_bytes().replace(b'\r', b'')
    exported = (out / 'export.txt').read_bytes()
    if len(exported) > 40 * 1024 * 1024:
        raise ValueError('evidence output bounds')
    for name in exports + ['kms.log']:
        match = re.search(b'M5_BEGIN_' + name.encode() + rb'\n(.*?)M5_END_' + name.encode(), exported, re.S)
        if match:
            (out / name).write_bytes(base64.b64decode(b''.join(match[1].split()), validate=True))
    status = re.search(rb'M5_APP_EXIT=(\d+)', data)
    report = {'qemu_exit': process.returncode, 'app_exit': int(status[1]) if status else None,
        'clean_poweroff': b'M5_SHUTDOWN' in data and b'reboot: Power down' in data,
        'rockbox_sha256': m5.sha(work / 'hosted-build/rockbox'),
        'initramfs_sha256': m5.sha(out / 'root.cpio.gz'), 'modules': modules + extra,
        'command': command, 'touch': touch, 'captures': captures,
        'artifacts': {n: m5.sha(out / n) for n in exports + ['kms.log'] + captures if (out / n).exists()}}
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['command', 'artifacts']}, indent=2))
    if unsupported_mode:
        if process.returncode or not report['clean_poweroff'] or report['app_exit'] != 102 or captures or \
                'no advertised 320x480 mode' not in (out/'app.log').read_text():
            raise RuntimeError('unsupported mode was not safely rejected')
    elif process.returncode or report['app_exit'] or not report['clean_poweroff'] or not captures:
        raise RuntimeError('DRM guest failed; evidence retained')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    b = sub.add_parser('link')
    b.add_argument('--work', type=Path, required=True)
    b.add_argument('--sony-archive', type=Path, required=True)
    r = sub.add_parser('run')
    for n in ['work', 'vm-dir', 'corpus', 'out']:
        r.add_argument('--' + n, type=Path, required=True)
    r.add_argument('--playlist', choices=['wav.m3u', 'flac.m3u', 'opus.m3u', 'opus-controls.m3u'], required=True)
    r.add_argument('--rate', choices=[44100, 48000], type=int, default=44100)
    r.add_argument('--touch', action='store_true')
    r.add_argument('--unsupported-mode', action='store_true', help='test rejection with a 640x480 virtual output')
    a = p.parse_args()
    if a.command == 'link':
        link(m5.private(a.work), a.sony_archive.resolve())
    else:
        run(m5.private(a.work), m5.private(a.vm_dir), a.corpus.resolve(), m5.private(a.out),
            a.playlist, a.rate, a.touch, a.unsupported_mode)
