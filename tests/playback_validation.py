# SPDX-License-Identifier: GPL-2.0-or-later
"""Synthetic library and end-to-end hosted Rockbox tests; no device interfaces."""
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import wave
from codec_regression import pages, update_crc

# codec_regression rejects optimized Python so these assertions stay active.
PROJECT = Path(__file__).resolve().parents[1]
CONFIG = """volume: 0
repeat: off
shuffle: off
crossfade: off
replaygain type: off
replaygain noclip: off
crossfeed: off
eq enabled: off
dithering enabled: off
bass: 0
treble: 0
beep: off
talk menu: off
talk file: off
talk dir: off
volume fade: off
"""

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def generate(out, ffmpeg):
    out.mkdir(parents=True, exist_ok=False)
    library = out / 'library'
    library.mkdir()
    records = []
    def ff(*args):
        subprocess.run([ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error',
                        *map(str, args)], check=True, timeout=60)
    for name, rate, frames in [('signal', 44100, 99226), ('opus-source', 48000, 108001),
                                ('long', 44100, 352801)]:
        pcm = bytearray()
        for i in range(frames):
            amplitude = 4000 + ((i // (rate // 4)) % 8) * 300
            for period in [rate // 200, rate // 150]:
                pcm.extend(struct.pack('<h', ((i % period) * 2 - period) * amplitude // period))
        with wave.open(str(library / (name + '.wav')), 'wb') as stream:
            stream.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
            stream.writeframes(pcm)
    ff('-i', library/'signal.wav', '-fflags', '+bitexact', '-flags:a', '+bitexact',
       '-metadata', 'title=M4 FLAC', '-c:a', 'flac', library/'signal.flac')
    ff('-i', library/'opus-source.wav', '-fflags', '+bitexact', '-flags:a', '+bitexact',
       '-metadata', 'title=M4 Opus', '-c:a', 'libopus', '-b:a', '96k', '-vbr', 'off', library/'signal.opus')
    ff('-i', library/'long.wav', '-fflags', '+bitexact', '-flags:a', '+bitexact',
       '-metadata', 'title=M4 long Opus', '-c:a', 'libopus', '-b:a', '96k', '-vbr', 'off', library/'long.opus')
    with wave.open(str(library/'short.wav'), 'wb') as stream:
        stream.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        stream.writeframes(struct.pack('<hh', 4000, -3000))
    ff('-i', library/'short.wav', '-fflags', '+bitexact', '-flags:a', '+bitexact',
       '-c:a', 'libopus', '-b:a', '96k', '-vbr', 'off', library/'short.opus')
    first = (library/'signal.opus').read_bytes()
    second = bytearray(first)
    for begin, end in pages(second):
        serial = struct.unpack_from('<I', second, begin+14)[0]
        struct.pack_into('<I', second, begin+14, (serial+1) & 0xffffffff)
        update_crc(second, begin, end)
    (library/'chained.opus').write_bytes(first+second)
    for name in ['signal.wav', 'signal.flac', 'signal.opus', 'long.wav', 'long.opus', 'short.opus', 'chained.opus']:
        ref = out / (name + '.s16')
        ff('-i', library/name, '-ar', '44100', '-ac', '2', '-f', 's16le', ref)
        if name.endswith('.opus'):
            ff('-i', library/name, '-ac', '2', '-f', 's16le', out/(name+'.native.s16'))
        records.append({'name': name, 'reference': ref.name, 'reference_frames': ref.stat().st_size//4})
    for name, entries in [('wav.m3u',['signal.wav']),('flac.m3u',['signal.flac']),
                          ('opus.m3u',['signal.opus']),('mixed.m3u',['signal.wav','signal.flac','signal.opus']),
                          ('controls.m3u',['long.wav','signal.flac','signal.opus']),
                          ('opus-controls.m3u',['long.opus','signal.wav','signal.flac']),
                          ('short.m3u',['short.opus']),('chain.m3u',['chained.opus','signal.wav'])]:
        (library/name).write_text('\n'.join(entries)+'\n')
    (library/'empty.wav').write_bytes(b'')
    (library/'invalid.opus').write_bytes(b'not an Ogg Opus file\n')
    (library/'truncated.opus').write_bytes((library/'signal.opus').read_bytes()[:-30])
    (library/'invalid.m3u').write_text('empty.wav\ninvalid.opus\ntruncated.opus\nsignal.wav\n')
    files = {p.relative_to(out).as_posix(): {'bytes':p.stat().st_size,'sha256':sha(p)}
             for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'manifest.json').write_text(json.dumps({'tracks':records,'files':files},indent=2)+'\n')
    print(json.dumps({'files':len(files),'manifest_sha256':sha(out/'manifest.json')},indent=2))

def environment(work):
    env = os.environ.copy()
    env.update(VERSION='afe91f1dfb', SOURCE_DATE_EPOCH='0')
    env['PATH'] = f'{work}/tool-bin:{work}/environment/usr/bin:/usr/bin:/bin'
    env['LD_LIBRARY_PATH'] = str(work/'environment/usr/lib/x86_64-linux-gnu')
    return env

def link(work, asan=False):
    directory = work/('hosted-asan-build' if asan else 'hosted-build')
    adapter = directory/'m4-playback.o'
    wrappers = ['root_menu','get_action','SDL_OpenAudioDevice','SDL_RenderPresent',
                'codec_load_file','audio_codec_complete','get_metadata_ex']
    makefile = directory/'m4-adapter.make'
    makefile.write_text('export LDOPTS += '+
                       ' '.join('-Wl,--wrap='+name for name in wrappers)+'\n'+
                       f'{directory}/rockbox: {adapter}\n'+
                       f'{adapter}: {PROJECT}/tests/hosted_playback.c\n'+
                       '\t$(CC) $(CFLAGS) -c $< -o $@\n')
    with (directory/'m4-link.log').open('wb') as log:
        options = ['CC='+str(work/'tool-bin/aarch64-linux-gnu-gcc')+
                   ' -fsanitize=address -static-libasan -no-pie -fno-omit-frame-pointer',
                   'GLOBAL_LDOPTS=-Wl,--no-warn-rwx-segments'] if asan else []
        subprocess.run(['make','-f','Makefile','-f',str(makefile),'-j4','all',*options],
                       cwd=directory,env=environment(work),stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run(['make','-f','Makefile','-f',str(makefile),'install',*options],
                       cwd=directory,env=environment(work),stdout=log,stderr=subprocess.STDOUT,check=True)
    print(json.dumps({'binary':str(directory/'rockbox'),'sha256':sha(directory/'rockbox')},indent=2))

def run(work, corpus, out, playlist, controls, elapsed, offset, cycles, asan=False, restart=None):
    manifest = json.loads((corpus/'manifest.json').read_text())
    for name, item in manifest['files'].items():
        p = corpus/name
        assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256']
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(corpus/'library', out/'library')
    if restart:
        shutil.copytree(restart/'home',out/'home')
    config = out/'home/.config/rockbox.org'
    config.mkdir(parents=True,exist_ok=True)
    (config/'config.cfg').write_text(CONFIG)
    env = environment(work)
    env.update(RBROOT=str(out/'home'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',
               M4_PLAYLIST=playlist,M4_LIBRARY=str(out/'library'),M4_PCM=str(out/'output.s16'),M4_TRACE=str(out/'trace.tsv'),
               M4_SCREEN=str(out/'screen.bmp'), M4_ELAPSED=str(elapsed), M4_OFFSET=str(offset), M4_CYCLES=str(cycles))
    if controls:
        env['M4_CONTROLS']='1'
    directory = work/('hosted-asan-build' if asan else 'hosted-build')
    if asan:
        env['ASAN_OPTIONS']='detect_leaks=0:halt_on_error=1'
    command=[str(work/'environment/usr/bin/qemu-aarch64-static'),'-L',str(work/'environment/usr/aarch64-linux-gnu'),
             str(directory/'rockbox')]
    try:
        proc=subprocess.run(command,cwd=directory,env=env,capture_output=True,timeout=50)
    except subprocess.TimeoutExpired as exc:
        (out/'stdout.log').write_bytes(exc.stdout or b'')
        (out/'stderr.log').write_bytes(exc.stderr or b'')
        (out/'run.json').write_text(json.dumps({'timeout_seconds':50,'binary_sha256':sha(directory/'rockbox')},indent=2)+'\n')
        raise
    (out/'stdout.log').write_bytes(proc.stdout)
    (out/'stderr.log').write_bytes(proc.stderr)
    trace=(out/'trace.tsv').read_text()
    result={'exit_status':proc.returncode,'binary_sha256':sha(directory/'rockbox'),
            'pcm_bytes':(out/'output.s16').stat().st_size,'pcm_sha256':sha(out/'output.s16'),
            'playlist':playlist,'watchdog':'watchdog' in trace}
    (out/'run.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if proc.returncode or result['watchdog'] or 'process_exit' not in trace or b'ERROR: AddressSanitizer' in proc.stderr:
        raise RuntimeError('application playback run did not complete normally')

def analyze(corpus, output, track, out):
    """Check one uninterrupted track; callback padding is separate from music."""
    captured=(output/'output.s16').read_bytes()
    trace=(output/'trace.tsv').read_text()
    native_opus=track.endswith('.opus') and 'output\tfreq=48000\tchannels=2\tformat=32784' in trace
    rate=48000 if native_opus else 44100
    ref=(corpus/(track+('.native.s16' if native_opus else '.s16'))).read_bytes()
    run_result=json.loads((output/'run.json').read_text())
    assert run_result['exit_status']==0 and not run_result['watchdog']
    assert f'output\tfreq={rate}\tchannels=2\tformat=32784' in trace
    assert 'codec_complete' in trace and 'value=-1' not in trace
    assert len(captured)%4==0
    result={'track':track,'rate':rate,'reference_frames':len(ref)//4,'callback_frames':len(captured)//4}
    if track.endswith(('.wav','.flac')):
        assert captured.startswith(ref), 'lossless PCM differs, is reordered or missing'
        assert not any(captured[len(ref):]), 'non-silent padding after lossless track'
        result.update(exact_reference=True, music_frames=len(ref)//4)
    else:
        a=array('h'); a.frombytes(captured)
        b=array('h'); b.frombytes(ref)
        if os.sys.byteorder!='little':
            a.byteswap(); b.byteswap()
        # The existing Rockbox Hermite resampler has about two output frames of
        # latency relative to FFmpeg's independent FIR reference. Bound alignment
        # to +/- four frames; never allow a broad search to conceal dropped audio.
        begin=0 if native_opus else 64
        end=len(b) if native_opus else len(b)-64
        assert end>begin
        scores=[]
        for lag in ([0] if native_opus else range(-4,5)):
            error=sum((a[i+lag*2]-b[i])**2 for i in range(begin,end))/(end-begin)
            scores.append((error,lag))
        mse,lag=min(scores)
        rms=math.sqrt(mse)
        signal=math.sqrt(sum(v*v for v in b[begin:end])/(end-begin))
        peak=max(abs(a[i+lag*2]-b[i]) for i in range(begin,end))
        snr=20*math.log10(signal/rms)
        active_end=max(i//2+1 for i,v in enumerate(a) if v)
        result.update(alignment_frames=lag,rms_error_s16=rms,peak_error_s16=peak,
                      snr_db=snr,music_frames=active_end,exact_reference=False)
        out.write_text(json.dumps(result,indent=2)+'\n')
        assert abs(active_end-len(b)//2)<=(0 if native_opus else 4), 'music endpoint differs'
        assert snr>=(40 if native_opus else 30) and peak<=32768*(.005 if native_opus else .05), 'PCM/reference mismatch'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def memory_probe(work, out):
    out.mkdir(parents=True,exist_ok=False)
    env=environment(work)
    compiler=work/'tool-bin/aarch64-linux-gnu-gcc'
    runner=[str(work/'environment/usr/bin/qemu-aarch64-static'),'-L',str(work/'environment/usr/aarch64-linux-gnu')]
    cases=[('shared-pie',['-fsanitize=address']),
           ('shared-nopie',['-fsanitize=address','-no-pie']),
           ('static-nopie',['-fsanitize=address','-static-libasan','-no-pie']),
           ('ubsan',['-fsanitize=undefined'])]
    records=[]
    for name, flags in cases:
        binary=out/name
        subprocess.run([str(compiler),'-O0','-g','-fno-omit-frame-pointer',*flags,
                        str(PROJECT/'tests/asan_runtime_probe.c'),'-o',str(binary)],env=env,check=True)
        for bad in [False,True]:
            runtime=env.copy()
            runtime.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:verbosity=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            label=name+('-negative' if bad else '-valid')
            args=['overflow' if name=='ubsan' else 'oob'] if bad else []
            try:
                proc=subprocess.run(runner+[str(binary),*args],env=runtime,capture_output=True,timeout=15)
                (out/(label+'.stdout')).write_bytes(proc.stdout)
                (out/(label+'.stderr')).write_bytes(proc.stderr)
                records.append({'case':label,'exit_status':proc.returncode,
                                'entered_main':b'probe entered main' in proc.stdout,
                                'asan_overflow':b'ERROR: AddressSanitizer: heap-buffer-overflow' in proc.stderr,
                                'ubsan_overflow':b'signed integer overflow' in proc.stderr})
            except subprocess.TimeoutExpired:
                records.append({'case':label,'timeout':True})
    (out/'results.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records,indent=2))

def suite_check(corpus, runs, out):
    out.mkdir(parents=True,exist_ok=False)
    def read(case):
        directory=runs/('review-'+case)
        result=json.loads((directory/'run.json').read_text())
        assert result['exit_status']==0 and not result['watchdog'], case
        events=[]
        for line in (directory/'trace.tsv').read_text().splitlines():
            fields=line.split('\t')
            events.append({'event':fields[0],**dict(f.split('=',1) for f in fields[1:] if '=' in f)})
        assert any(e['event']=='process_exit' for e in events),case
        return directory,events,(directory/'output.s16').read_bytes()
    results=[]
    for case,track in [('wav','signal.wav'),('flac','signal.flac'),('opus','signal.opus')]:
        directory,events,data=read(case)
        analyze(corpus,directory,track,out/(case+'.json'))
        rate=48000 if case=='opus' else 44100
        errors=[abs(int(e['elapsed'])-int(e['frames'])*1000/rate) for e in events
                if e['event']=='state' and int(e['status'])==1]
        assert errors and max(errors)<=75, (case,'progress drift',errors)
        results.append({'case':case,'passed':True,'max_progress_error_ms':max(errors)})
    directory,events,data=read('mixed')
    ref=(corpus/'signal.wav.s16').read_bytes()
    assert data.startswith(ref+ref)
    rates=[e for e in events if e['event']=='output']
    assert [int(e['freq']) for e in rates]==[44100,48000]
    boundary=int(rates[1]['frames'])*4
    assert not any(data[2*len(ref):boundary])
    opus=(runs/'review-opus/output.s16').read_bytes()[:108001*4]
    assert data[boundary:boundary+len(opus)]==opus
    assert not any(data[boundary+len(opus):])
    results.append({'case':'mixed','passed':True,'rate_switch_silence_frames':boundary//4-2*99226})
    directory,events,data=read('controls')
    names=[e['event'] for e in events]
    for name in ['pause_command','resume_command','seek_command','next_command','previous_command','stop_command']:
        assert name in names,name
    pause=next(e for e in events if e['event']=='pause_command')
    resume=next(e for e in events if e['event']=='resume_command')
    paused=[e for e in events if e['event']=='state' and int(e['status'])&2 and
            int(pause['tick'])<=int(e['tick'])<=int(resume['tick'])]
    assert len(paused)>=2 and len({e['elapsed'] for e in paused})==1,'pause progress not stable'
    assert not any(data[(int(resume['frames'])-1024)*4:int(resume['frames'])*4]),'pause output not silent'
    seek=next(e for e in events if e['event']=='seek_command')
    nxt=next(e for e in events if e['event']=='next_command')
    assert any(e['event']=='state' and int(seek['tick'])<=int(e['tick'])<int(nxt['tick']) and
               2500<=int(e['elapsed'])<3000 for e in events),'active seek not observed'
    prev=next(e for e in events if e['event']=='previous_command')
    assert any(e['event']=='state' and int(nxt['tick'])<int(e['tick'])<int(prev['tick']) and
               e['path'].endswith('signal.wav') for e in events),'next track not observed'
    assert any(e['event']=='state' and int(e['tick'])>int(prev['tick']) and
               e['path'].endswith('long.opus') for e in events),'previous track not observed'
    results.append({'case':'controls','passed':True,'paused_elapsed_ms':int(paused[0]['elapsed'])})
    directory,events,data=read('restart')
    ref=(corpus/'signal.opus.native.s16').read_bytes()[48000*4:]
    got=array('h'); got.frombytes(data[:len(ref)])
    expected=array('h'); expected.frombytes(ref)
    assert len(got)==len(expected) and max(abs(a-b) for a,b in zip(got,expected))<=5
    assert not any(data[len(ref):])
    results.append({'case':'restart_timestamp_resume','passed':True,'music_frames':len(ref)//4})
    directory,events,data=read('short')
    ref=(corpus/'short.opus.native.s16').read_bytes()
    got=struct.unpack('<hh',data[:4]); expected=struct.unpack('<hh',ref)
    assert max(abs(a-b) for a,b in zip(got,expected))<=5 and not any(data[4:])
    results.append({'case':'one_frame_opus','passed':True})
    directory,events,data=read('cycles')
    ref=(corpus/'signal.wav.s16').read_bytes()
    cursor=0
    for _ in range(5):
        pos=data.find(ref,cursor)
        assert pos>=cursor and not any(data[cursor:pos]),'cycle PCM incomplete or reordered'
        cursor=pos+len(ref)
    assert not any(data[cursor:])
    available=[int(e['value']) for e in events if e['event']=='buffer_available_stopped']
    assert len(set(available[1:]))==1,'steady-state playback buffer loss'
    results.append({'case':'five_cycles','passed':True,'buffer_available':available})
    for case in ['invalid','chain']:
        directory,events,data=read(case)
        rejected=[e for e in events if e['event']=='metadata' and e['ok']=='0']
        assert len(rejected)>=(2 if case=='invalid' else 1)
        if case=='invalid':
            assert any(e['event']=='codec_complete' and e['value']=='-1' for e in events)
        else:
            ref=(corpus/'signal.wav.s16').read_bytes()
            assert data.startswith(ref) and not any(data[len(ref):])
        results.append({'case':case,'passed':True,'metadata_rejections':len(rejected),
                        'chain_support':False} if case=='chain' else {'case':case,'passed':True})
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    gen=sub.add_parser('generate')
    gen.add_argument('--out',required=True,type=Path)
    gen.add_argument('--ffmpeg',default='ffmpeg')
    ln=sub.add_parser('link')
    ln.add_argument('--work',required=True,type=Path)
    ln.add_argument('--asan',action='store_true')
    rn=sub.add_parser('run')
    rn.add_argument('--work',required=True,type=Path)
    rn.add_argument('--corpus',required=True,type=Path)
    rn.add_argument('--out',required=True,type=Path)
    rn.add_argument('--playlist',required=True)
    rn.add_argument('--controls',action='store_true')
    rn.add_argument('--elapsed',type=int,default=0)
    rn.add_argument('--offset',type=int,default=0)
    rn.add_argument('--cycles',type=int,default=1)
    rn.add_argument('--asan',action='store_true')
    rn.add_argument('--restart-from',type=Path)
    an=sub.add_parser('analyze')
    an.add_argument('--corpus',required=True,type=Path)
    an.add_argument('--output',required=True,type=Path)
    an.add_argument('--track',required=True)
    an.add_argument('--out',required=True,type=Path)
    mem=sub.add_parser('memory-probe')
    mem.add_argument('--work',required=True,type=Path)
    mem.add_argument('--out',required=True,type=Path)
    suite=sub.add_parser('suite-check')
    suite.add_argument('--corpus',required=True,type=Path)
    suite.add_argument('--runs',required=True,type=Path)
    suite.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.command=='generate':
        generate(args.out.resolve(),args.ffmpeg)
    elif args.command=='link':
        link(args.work.resolve(),args.asan)
    elif args.command=='analyze':
        analyze(args.corpus.resolve(),args.output.resolve(),args.track,args.out.resolve())
    elif args.command=='memory-probe':
        memory_probe(args.work.resolve(),args.out.resolve())
    elif args.command=='suite-check':
        suite_check(args.corpus.resolve(),args.runs.resolve(),args.out.resolve())
    else:
        run(args.work.resolve(),args.corpus.resolve(),args.out.resolve(),args.playlist,
            args.controls,args.elapsed,args.offset,args.cycles,args.asan,
            args.restart_from.resolve() if args.restart_from else None)

if __name__=='__main__':
    main()
