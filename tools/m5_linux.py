# SPDX-License-Identifier: GPL-2.0-or-later
"""Pinned generic ARM64 VM only; no host device passthrough or physical media.

Run in Linux/WSL. All writable paths must be in this project's ignored build/
or ~/.cache/nwa306-open/. Original source/evidence inputs remain read-only.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import m3_build

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'tests'))
from playback_validation import CONFIG, environment, link
LOCK = Path(__file__).with_name('m5-linux.lock.json')


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def private(p):
    p = p.resolve()
    for root in [PROJECT / '.local-references', PROJECT / 'firmware-images']:
        root = root.resolve()
        if p == root or root in p.parents:
            raise ValueError('protected evidence destination')
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+', p.as_posix()):
        raise ValueError('private build paths require simple Linux path characters')
    if not any(p != root and root in p.parents for root in
               [(PROJECT / 'build').resolve(), (Path.home() / '.cache/nwa306-open').resolve()]):
        raise ValueError('writable paths must be within ignored build/ or the private research cache')
    return p


def inputs(vm, download=False):
    cache = vm / 'inputs'
    cache.mkdir(parents=True, exist_ok=True)
    entries = json.loads(LOCK.read_text())
    for entry in entries:
        p = cache / entry['file']
        if not p.exists() and download:
            part = p.with_suffix(p.suffix + '.part')
            with urllib.request.urlopen(entry['url'], timeout=60) as r, part.open('xb') as f:
                shutil.copyfileobj(r, f)
            if part.stat().st_size != entry['bytes'] or sha(part) != entry['sha256']:
                raise ValueError('download verification failed: ' + p.name)
            part.rename(p)
        if p.stat().st_size != entry['bytes'] or sha(p) != entry['sha256']:
            raise ValueError('input verification failed: ' + p.name)
    return entries


def call(cmd, cwd, env, log):
    subprocess.run(list(map(str, cmd)), cwd=cwd, env=env, stdout=log,
                   stderr=subprocess.STDOUT, check=True)


def build(work, vm, source, sdl, previous_inputs):
    inputs(vm)
    m3_build.prepare(work, source, sdl, previous_inputs)
    env = environment(work)
    with (work / 'm5-build.log').open('wb') as log:
        for name in ['rockbox-playback-integration.patch', 'rockbox-hosted-decoder-error.patch']:
            with (PROJECT / 'tools' / name).open('rb') as f:
                subprocess.run(['patch', '--batch', '--fuzz=0', '-p1'],
                               cwd=work / 'rockbox-source', stdin=f, stdout=log, check=True)
        with tarfile.open(vm / 'inputs/alsa-lib-1.2.11.tar.bz2') as t:
            t.extractall(work, filter='data')
        alsa = work / 'alsa-build'
        alsa.mkdir()
        prefix = work / 'alsa-prefix'
        env['CC'] = str(work / 'tool-bin/aarch64-linux-gnu-gcc')
        call([work / 'alsa-lib-1.2.11/configure', '--host=aarch64-linux-gnu',
              '--prefix=' + str(prefix), '--disable-shared', '--enable-static',
              '--disable-python', '--disable-ucm', '--disable-topology'], alsa, env, log)
        call(['make', '-j4'], alsa, env, log)
        call(['make', 'install'], alsa, env, log)
        sdlbuild = work / 'sdl-ui-build'
        sdlbuild.mkdir()
        sdlprefix = work / 'sdl-ui-prefix'
        env.update(CFLAGS='-I' + str(prefix / 'include'), LDFLAGS='-L' + str(prefix / 'lib'),
                   PKG_CONFIG_LIBDIR=str(prefix / 'lib/pkgconfig'))
        options = ['--host=aarch64-linux-gnu', '--prefix=' + str(sdlprefix),
                   '--disable-shared', '--enable-static', '--disable-joystick', '--disable-haptic',
                   '--disable-sensor', '--enable-video', '--enable-audio', '--enable-alsa',
                   '--disable-alsa-shared']
        options += ['--disable-' + s for s in ['x11', 'wayland', 'kmsdrm', 'vulkan',
                    'opengl', 'opengles', 'pulseaudio', 'pipewire', 'jack', 'sndio', 'oss']]
        call([work / 'SDL2-2.30.0/configure', *options], sdlbuild, env, log)
        call(['make', '-j4'], sdlbuild, env, log)
        call(['make', 'install'], sdlbuild, env, log)
        shutil.copy2(prefix / 'lib/libasound.a', sdlprefix / 'lib/libasound.a')
    m3_build.build(work, 'hosted', None, None)
    link_vm(work)


def link_vm(work):
    link(work)
    directory = work / 'hosted-build'
    obj = directory / 'm5-input.o'
    make = directory / 'm5-adapter.make'
    make.write_text('include ' + str(directory / 'm4-adapter.make') + '\n' +
                    'export LDOPTS += -Wl,--wrap=SDL_InitSubSystem,--wrap=SDL_Quit,' +
                    '--wrap=button_read_device,--wrap=audio_take_decoder_error\n' +
                    f'{directory}/rockbox: {obj}\n{obj}: {PROJECT}/tests/linux_evdev_touch.c\n' +
                    '\t$(CC) $(CFLAGS) -c $< -o $@\n')
    # Changing linker wrapper flags is not a Make dependency. The M4 helper
    # may just have relinked without these wrappers; force this final link.
    if obj.exists():
        obj.touch()
    with (directory / 'm5-link.log').open('wb') as log:
        for target in ['all', 'install']:
            call(['make', '-f', 'Makefile', '-f', make, '-j4', target],
                 directory, environment(work), log)
    print(json.dumps({'vm_binary_sha256': sha(directory / 'rockbox')}, indent=2))


def rootfs(work, vm, corpus, out, playlist, touch, fault, memory_work=None):
    root = out / 'root'
    root.mkdir()
    for name in ['bin', 'sbin', 'proc', 'sys', 'dev', 'run', 'etc', 'lib/aarch64-linux-gnu',
                 'home/.config/rockbox.org']:
        (root / name).mkdir(parents=True, exist_ok=True)
    with tarfile.open(vm / 'inputs/alpine-minirootfs-3.21.8-aarch64.tar.gz') as t:
        for name in ['bin/busybox', 'lib/ld-musl-aarch64.so.1']:
            member = t.getmember('./' + name)
            if not member.isfile():
                raise ValueError('unexpected minirootfs member type')
            with t.extractfile(member) as src, (root / name).open('xb') as dst:
                shutil.copyfileobj(src, dst)
            (root / name).chmod(0o755)
    for name in ['sh', 'mount', 'mkdir', 'uname', 'cat', 'echo', 'sleep', 'kill',
                 'poweroff', 'base64', 'sha256sum', 'timeout', 'wc', 'insmod']:
        (root / 'bin' / name).symlink_to('busybox')
    for name in ['libc.so.6', 'libm.so.6', 'ld-linux-aarch64.so.1']:
        shutil.copy2(work / 'environment/usr/aarch64-linux-gnu/lib' / name,
                     root / 'lib/aarch64-linux-gnu' / name, follow_symlinks=True)
    (root / 'lib/ld-linux-aarch64.so.1').symlink_to('aarch64-linux-gnu/ld-linux-aarch64.so.1')
    # Configured Rockbox data paths are absolute; recreate only its private prefix.
    shutil.copytree(work / 'app-prefix', root / str(work / 'app-prefix').lstrip('/'))
    shutil.copy2(work / 'hosted-build/rockbox', root / 'rockbox')
    manifest = json.loads((corpus / 'manifest.json').read_text())
    for name, item in manifest['files'].items():
        p = corpus / name
        if p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
            raise ValueError('corpus changed: ' + name)
    shutil.copytree(corpus / 'library', root / 'music')
    (root / 'home/.config/rockbox.org/config.cfg').write_text(CONFIG + 'touchscreen mode: grid\n')
    # Direct hw PCM: no guessed mixer or Sony routing. Only the virtual ALSA card.
    (root / 'etc/asound.conf').write_text('pcm.!default { type hw card 0 device 0 }\n'
             'ctl.hw { @args [ CARD ] @args.CARD { type string } type hw card $CARD }\n')
    (root / 'etc/passwd').write_text('root:x:0:0:root:/home:/bin/sh\n')
    deptext = subprocess.check_output(['unsquashfs', '-cat', vm / 'inputs/modloop-virt',
                         'modules/6.12.110-0-virt/modules.dep'], text=True)
    deps = {line.split(':')[0]: line.split(':')[1].split() for line in deptext.splitlines()}
    selected = []
    def add(name):
        if name in selected:
            return
        for dependency in deps[name]:
            add(dependency)
        selected.append(name)
    for name in ['kernel/drivers/input/evdev.ko', 'kernel/drivers/input/misc/uinput.ko',
                 'kernel/sound/virtio/virtio_snd.ko']:
        add(name)
    if 'CONFIG_VIRTIO_CONSOLE=y' not in (vm / 'inputs/config-6.12.110-0-virt').read_text():
        raise ValueError('kernel lacks built-in virtual console')
    for name in selected:
        data = subprocess.check_output(['unsquashfs', '-cat', vm / 'inputs/modloop-virt',
                                        'modules/6.12.110-0-virt/' + name])
        p = root / 'modules' / Path(name).name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(data)
    module_load = '\n'.join('insmod /modules/' + Path(n).name + ' || fatal module' for n in selected)
    exports = ['output.s16', 'screen.bmp', 'trace.tsv', 'app.log', 'evdev.log', 'memory.log']
    memory_commands = ''
    if memory_work:
        memory = root / 'memory'
        memory.mkdir()
        compiler = work / 'tool-bin/aarch64-linux-gnu-gcc'
        for name, flags in [('shared', ['-fsanitize=address']),
                             ('static', ['-fsanitize=address', '-static-libasan', '-no-pie'])]:
            subprocess.run([compiler, '-O0', '-g', '-fno-omit-frame-pointer', *flags,
                            PROJECT / 'tests/asan_runtime_probe.c', '-o', memory / name],
                           env=environment(work), check=True)
        for name in ['libasan.so.8', 'libgcc_s.so.1', 'libstdc++.so.6']:
            shutil.copy2(work / 'environment/usr/aarch64-linux-gnu/lib' / name,
                         root / 'lib/aarch64-linux-gnu' / name, follow_symlinks=True)
        oldbuild = memory_work / 'arm64-static-asan-build'
        target = root / str(oldbuild).lstrip('/')
        target.mkdir(parents=True)
        shutil.copy2(oldbuild / 'warble.ipodvideo', target / 'warble.ipodvideo')
        (target / 'lib/rbcodec/codecs').mkdir(parents=True)
        for codec in ['wav', 'opus']:
            shutil.copy2(oldbuild / f'lib/rbcodec/codecs/{codec}.codec',
                         target / f'lib/rbcodec/codecs/{codec}.codec')
        memory_commands = f'''
export ASAN_OPTIONS=detect_leaks=0:halt_on_error=1
{{
for p in shared static; do
    timeout -k 1 8 /memory/$p; echo MEMORY_${{p}}_VALID=$?
    timeout -k 1 8 /memory/$p bad; echo MEMORY_${{p}}_OOB=$?
done
for p in signal.wav signal.opus; do
    SDL_AUDIODRIVER=dummy timeout -k 1 12 {oldbuild}/warble.ipodvideo -f /music/$p /run/asan-$p
    echo MEMORY_WARBLE_$p=$?
done
}} > /run/memory.log 2>&1
'''
        exports += ['asan-signal.wav', 'asan-signal.opus']
    export_commands = '\n'.join(f'if [ -f /run/{n} ]; then echo M5_BEGIN_{n}; '
            f'base64 /run/{n}; echo M5_END_{n}; fi' for n in exports)
    program = '/missing-rockbox' if fault else '/rockbox'
    init = f'''#!/bin/sh
export PATH=/bin:/sbin
mount -t devtmpfs devtmpfs /dev
mount -t proc proc /proc
mount -t sysfs sysfs /sys
fatal() {{ echo M5_FATAL_$1; poweroff -f; while :; do sleep 1; done; }}
{module_load}
printf 'M5_INIT kernel='; uname -r
cat /proc/asound/cards
export RBROOT=/home SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=alsa
export ALSA_CONFIG_PATH=/etc/asound.conf LD_LIBRARY_PATH=/lib/aarch64-linux-gnu
export SDL_AUDIO_ALSA_DEFAULT_DEVICE=default
{memory_commands}
export M4_PLAYLIST={shlex.quote(playlist)} M4_LIBRARY=/music
export M4_PCM=/run/output.s16 M4_TRACE=/run/trace.tsv M4_SCREEN=/run/screen.bmp
{'export M5_TEST_GUEST=generic-arm64-vm' if touch else ''}
# One foreground application; bounded failure, no automatic restart loop.
timeout -s TERM -k 2 50 {program} > /run/app.log 2>&1
status=$?
echo M5_APP_EXIT=$status
port=
for p in /sys/class/virtio-ports/*; do
    if [ "$(cat "$p/name")" = m5.evidence ]; then port=/dev/${{p##*/}}; fi
done
[ -n "$port" ] || fatal evidence_port
{{
{export_commands}
}} > "$port"
echo M5_SHUTDOWN
poweroff -f
while :; do sleep 1; done
'''
    (root / 'init').write_text(init)
    (root / 'init').chmod(0o755)
    # Stable archive order, ownership and timestamps. No special host files.
    for p in sorted(root.rglob('*')):
        os.utime(p, (0, 0), follow_symlinks=False)
    os.utime(root, (0, 0))
    names = b'\0'.join(str(p.relative_to(root)).encode() for p in sorted(root.rglob('*'))) + b'\0'
    archive = subprocess.run(['cpio', '--null', '-o', '--format=newc', '--reproducible',
                              '--owner=0:0'], cwd=root, input=names, capture_output=True, check=True)
    with (out / 'root.cpio.gz').open('xb') as f:
        with gzip.GzipFile(filename='', fileobj=f, mode='wb', mtime=0) as g:
            g.write(archive.stdout)
    return exports, selected


def prototype(work, vm, corpus, out, playlist, rate, touch=False, fault=False, memory_work=None):
    inputs(vm)
    out.mkdir(parents=True, exist_ok=False)
    qemu = vm / 'qemu'
    if not qemu.exists():
        qemu.mkdir()
        for e in json.loads(LOCK.read_text()):
            if e['file'].endswith('.deb'):
                subprocess.run(['dpkg-deb', '-x', vm / 'inputs' / e['file'], qemu], check=True)
    exports, modules = rootfs(work, vm, corpus, out, playlist, touch, fault, memory_work)
    env = os.environ | {'LD_LIBRARY_PATH': str(qemu / 'usr/lib/x86_64-linux-gnu'),
                       'QEMU_MODULE_DIR': str(qemu / 'usr/lib/x86_64-linux-gnu/qemu')}
    command = [str(qemu / 'usr/bin/qemu-system-aarch64'), '-machine', 'virt', '-cpu', 'cortex-a53',
               '-m', '512', '-smp', '2', '-accel', 'tcg', '-nodefaults', '-no-reboot',
               '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-nic', 'none',
               '-kernel', str(vm / 'inputs/vmlinuz-virt'), '-initrd', str(out / 'root.cpio.gz'),
               '-append', 'console=ttyAMA0 rdinit=/init panic=-1',
               '-audiodev', f'wav,id=capture,path={out}/virtio.wav,out.frequency={rate},'
                            'out.channels=2,out.format=s16',
               '-device', 'virtio-sound-pci,audiodev=capture']
    command += ['-device', 'virtio-serial-pci', '-chardev',
                f'file,id=evidence,path={out}/export.txt', '-device',
                'virtserialport,chardev=evidence,name=m5.evidence']
    with (out / 'console.log').open('xb') as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=100)
    data = (out / 'console.log').read_bytes().replace(b'\r', b'')
    if len(data) > 40 * 1024 * 1024:
        raise ValueError('unexpected serial output size')
    exported = (out / 'export.txt').read_bytes()
    if len(exported) > 40 * 1024 * 1024:
        raise ValueError('unexpected evidence output size')
    for name in exports:
        match = re.search(b'M5_BEGIN_' + name.encode() + rb'\n(.*?)M5_END_' + name.encode(), exported, re.S)
        if match:
            (out / name).write_bytes(base64.b64decode(b''.join(match[1].split()), validate=True))
    status = re.search(rb'M5_APP_EXIT=(\d+)', data)
    report = {'qemu_exit': result.returncode, 'app_exit': int(status[1]) if status else None,
              'clean_poweroff': b'M5_SHUTDOWN' in data and b'reboot: Power down' in data,
              'rockbox_sha256': sha(work / 'hosted-build/rockbox'),
              'initramfs_sha256': sha(out / 'root.cpio.gz'), 'modules': modules,
              'command': command, 'touch': touch, 'fault_injection': fault,
              'artifacts': {n: sha(out / n) for n in exports if (out / n).exists()}}
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['command', 'artifacts']}, indent=2))
    if result.returncode or not report['clean_poweroff'] or (not fault and report['app_exit']):
        raise RuntimeError('guest failed; inspect preserved console and result')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    acq = sub.add_parser('inputs')
    acq.add_argument('--vm-dir', required=True, type=Path)
    acq.add_argument('--download', action='store_true')
    b = sub.add_parser('build')
    for name in ['work', 'vm-dir', 'source', 'sdl-archive', 'previous-inputs']:
        b.add_argument('--' + name, required=True, type=Path)
    ln = sub.add_parser('link')
    ln.add_argument('--work', required=True, type=Path)
    vm = sub.add_parser('prototype')
    for name in ['work', 'vm-dir', 'corpus', 'out']:
        vm.add_argument('--' + name, required=True, type=Path)
    vm.add_argument('--playlist', required=True, choices=['wav.m3u', 'flac.m3u', 'opus.m3u',
                    'mixed.m3u', 'opus-controls.m3u', 'invalid.m3u', 'chain.m3u'])
    vm.add_argument('--rate', type=int, choices=[44100, 48000], default=44100)
    vm.add_argument('--touch', action='store_true')
    vm.add_argument('--fault', action='store_true')
    vm.add_argument('--memory-work', type=Path,
                    help='preserved M4 instrumented build; bounded guest probes')
    a = p.parse_args()
    if os.name != 'posix':
        p.error('Linux/WSL required')
    if a.command == 'inputs':
        inputs(private(a.vm_dir), a.download)
    elif a.command == 'build':
        build(private(a.work), private(a.vm_dir), a.source.resolve(),
              a.sdl_archive.resolve(), a.previous_inputs.resolve())
    elif a.command == 'link':
        link_vm(private(a.work))
    else:
        prototype(private(a.work), private(a.vm_dir), a.corpus.resolve(),
                  private(a.out), a.playlist, a.rate, a.touch, a.fault,
                  a.memory_work.resolve() if a.memory_work else None)


if __name__ == '__main__':
    main()
