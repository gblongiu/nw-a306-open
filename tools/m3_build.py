# SPDX-License-Identifier: GPL-2.0-or-later
"""Build native/ARM64 Rockbox in an isolated Linux workspace.

Prepare a fresh work directory, then build native/ARM64 Warble or SDL Rockbox.
Requires existing Python, GCC, make, Perl, apt download metadata and dpkg-deb.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess


PROJECT = Path(__file__).resolve().parent.parent
OPUS_SHA = "3fcaeabd9aa1d44c132d8987d354e402331d8e4d83811793f7b5855c30edee16"
WARBLE_SHA = "a710266fb3e47efce3064a78a1d3540a888d7f1794d37e9a15eb8ec22749fc47"
WARBLE_MAKE_SHA = "b3368831f0e1a0f267b876458960e262fcd9fa0fdfb93f834101057692c6f52a"
SDL_SHA = "36e2e41557e0fa4a1519315c0f5958a87ccb27e25c51776beb6f1239526447b0"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def call(args, cwd, env=None, log=None):
    if log:
        with (cwd / log).open("wb") as stream:
            subprocess.run(list(map(str, args)), cwd=cwd, env=env, stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
    else:
        subprocess.run(list(map(str, args)), cwd=cwd, env=env, check=True)


def prepare(work, source, sdl_archive, inputs):
    if work.exists():
        raise ValueError("prepare requires a fresh directory; existing evidence is never replaced")
    if sha(source / "lib/rbcodec/codecs/opus.c") != OPUS_SHA or sha(
            source / "lib/rbcodec/test/warble.c") != WARBLE_SHA or sha(
            source / "lib/rbcodec/test/warble.make") != WARBLE_MAKE_SHA:
        raise ValueError("source differs from the pinned patch inputs")
    if sha(sdl_archive) != SDL_SHA:
        raise ValueError("SDL archive hash mismatch")
    work.mkdir(parents=True)
    cache = work / "inputs"
    cache.mkdir()
    environment = work / "environment"
    environment.mkdir()
    lock = json.loads((PROJECT / "tools/m3-toolchain.lock.json").read_text())
    for entry in lock:
        path = cache / entry["file"]
        existing = inputs / entry["file"] if inputs else None
        if existing and existing.exists():
            shutil.copy2(existing, path)
        else:
            call(["apt-get", "download", entry["package"] + "=" + entry["version"]], cache)
        if path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
            raise ValueError("package verification failed: " + entry["package"])
        if entry["package"] == "qemu-user-static":
            producer = subprocess.Popen(["dpkg-deb", "--fsys-tarfile", str(path)], stdout=subprocess.PIPE)
            try:
                subprocess.run(["tar", "-xf", "-", "-C", str(environment),
                                "./usr/bin/qemu-aarch64-static"], stdin=producer.stdout, check=True)
            finally:
                producer.stdout.close()
            if producer.wait() != 0:
                raise ValueError("QEMU archive read failed")
        else:
            call(["dpkg-deb", "-x", path, environment], work)
    shutil.copytree(source, work / "rockbox-source")
    with (PROJECT / "tools/rockbox-opus-correctness.patch").open("rb") as patch:
        subprocess.run(["patch", "--batch", "--fuzz=0", "-p1"],
                       cwd=work / "rockbox-source", stdin=patch, check=True)
    # This hash-verified SDL source is unpacked only to build the host dependency.
    call(["tar", "-xzf", sdl_archive, "-C", work], work)
    wrappers = work / "tool-bin"
    wrappers.mkdir()
    for name in ("gcc", "cpp"):
        args = [str(environment / f"usr/bin/aarch64-linux-gnu-{name}-13"),
                "--sysroot=" + str(environment)]
        if name == "gcc":
            args += ["-Wl,-rpath-link," + str(environment / "usr/aarch64-linux-gnu/lib")]
        wrapper = wrappers / ("aarch64-linux-gnu-" + name)
        wrapper.write_text("#!/bin/sh\nexec " + shlex.join(args) + ' "$@"\n')
        wrapper.chmod(0o755)
    for name in ("ld", "as", "objcopy", "objdump", "readelf", "strip", "nm",
                 "gcc-ar", "gcc-nm", "gcc-ranlib"):
        suffix = "-13" if name.startswith("gcc-") else ""
        (wrappers / ("aarch64-linux-gnu-" + name)).symlink_to(
            environment / ("usr/bin/aarch64-linux-gnu-" + name + suffix))
    (work / "package-manifest.json").write_text(json.dumps(lock, indent=2) + "\n")


def build(work, mode, native_sdl=None, sdl_source=None):
    env = os.environ.copy()
    env.update(VERSION="afe91f1dfb", SOURCE_DATE_EPOCH="0")
    env["PATH"] = f"{work}/tool-bin:{work}/environment/usr/bin:/usr/bin:/bin"
    env["LD_LIBRARY_PATH"] = str(work / "environment/usr/lib/x86_64-linux-gnu")
    cross = mode.startswith("arm64") or mode == "hosted"
    hosted = mode == "hosted"
    sanitizer = mode.endswith("asan")
    compiler = str(work / "tool-bin/aarch64-linux-gnu-gcc") if cross else "/usr/bin/gcc"
    if cross:
        env["CROSS_COMPILE"] = str(work / "tool-bin/aarch64-linux-gnu-")
    else:
        env.pop("CROSS_COMPILE", None)
    env["CC"] = compiler
    prefix = work / ("sdl-ui-prefix" if hosted else "sdl-prefix" if cross else "sdl-native-prefix")
    if native_sdl and not cross:
        prefix = native_sdl
    if not (prefix / "bin/sdl2-config").exists():
        directory = work / ("sdl-ui-build" if hosted else "sdl-build" if cross else "sdl-native-build")
        directory.mkdir(exist_ok=True)
        options = ["--prefix=" + str(prefix), "--disable-shared", "--enable-static",
                   "--disable-joystick", "--disable-haptic", "--disable-sensor"]
        if cross:
            options += ["--host=aarch64-linux-gnu"]
        if hosted:
            options += ["--enable-video", "--enable-audio", "--disable-x11", "--disable-wayland",
                        "--disable-kmsdrm", "--disable-vulkan", "--disable-opengl", "--disable-opengles",
                        "--disable-alsa", "--disable-pulseaudio", "--disable-pipewire",
                        "--disable-jack", "--disable-sndio", "--disable-oss"]
        else:
            options += ["--disable-video", "--disable-audio", "--disable-render"]
        call([(sdl_source or work / "SDL2-2.30.0") / "configure", *options], directory, env, "configure.log")
        call(["make", "-j4"], directory, env, "build.log")
        call(["make", "install"], directory, env, "install.log")
    env["PATH"] = str(prefix / "bin") + ":" + env["PATH"]
    names = {"native": "native-build", "arm64": "arm64-build", "native-asan": "asan-build",
             "arm64-asan": "arm64-asan-build", "hosted": "hosted-build"}
    directory = work / names[mode]
    directory.mkdir(exist_ok=True)
    options = ["--no-ccache"]
    if hosted:
        (work / "app-prefix").mkdir(exist_ok=True)
        options += ["--target=sdlapp", "--type=n", "--lcdwidth=320", "--lcdheight=480",
                    "--prefix=" + str(work / "app-prefix")]
    else:
        options += ["--target=ipodvideo", "--ram=64", "--type=w"]
    call([work / "rockbox-source/tools/configure", *options], directory, env, "configure.log")
    args = ["make", "-j4"]
    if sanitizer:
        env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        compiler += " -fsanitize=address -fno-omit-frame-pointer"
        args += ["CC=" + compiler]
    # The patch links Warble with CC; HOSTCC must remain native for generators.
    call(args, directory, env, "build.log")
    if hosted:
        call(["make", "install"], directory, env, "install.log")
    binary = directory / ("rockbox" if hosted else "warble.ipodvideo")
    print(json.dumps({"binary": str(binary), "sha256": sha(binary)}, indent=2))


def smoke(work):
    directory = work / "hosted-build"
    out = work / "hosted-smoke"
    out.mkdir(exist_ok=False)
    binary = directory / "rockbox"
    stock = out / "rockbox.stock"
    shutil.copy2(binary, stock)
    env = os.environ.copy()
    env.update(VERSION="afe91f1dfb", SOURCE_DATE_EPOCH="0")
    env["PATH"] = f"{work}/environment/usr/bin:{work}/tool-bin:/usr/bin:/bin"
    env["LD_LIBRARY_PATH"] = str(work / "environment/usr/lib/x86_64-linux-gnu")
    adapter = out / "sdl-smoke.o"
    call([work / "tool-bin/aarch64-linux-gnu-gcc", "-std=c11",
          "-I" + str(work / "sdl-ui-prefix/include/SDL2"), "-c",
          PROJECT / "tests/hosted_sdl_smoke.c", "-o", adapter], directory, env)
    makefile = directory / "Makefile"
    original = makefile.read_bytes()
    try:
        with makefile.open("a") as stream:
            stream.write("\nexport LDOPTS += " + str(adapter) +
                         " -Wl,--wrap=SDL_WaitEvent,--wrap=SDL_RenderPresent\n")
        os.utime(directory / "firmware/libfirmware.a", None)
        call(["make", "-j4"], directory, env, "smoke-link.log")
        shutil.copy2(binary, out / "rockbox.smoke")
    finally:
        makefile.write_bytes(original)
        shutil.copy2(stock, binary)
    for name in ("home", "files"):
        (out / name).mkdir()
    env.update(RBROOT=str(out / "home"), SDL_VIDEODRIVER="dummy",
               SDL_AUDIODRIVER="dummy", M3_FRAME_BMP=str(out / "frame.bmp"))
    proc = subprocess.run([str(work / "environment/usr/bin/qemu-aarch64-static"),
                           "-L", str(work / "environment/usr/aarch64-linux-gnu"),
                           str(out / "rockbox.smoke"), "--root", str(out / "files")],
                          cwd=directory, env=env, capture_output=True, timeout=20)
    (out / "stdout.log").write_bytes(proc.stdout)
    (out / "stderr.log").write_bytes(proc.stderr)
    if proc.returncode != 0 or b"M3 smoke: frames=" not in proc.stderr or not (out / "frame.bmp").is_file():
        raise RuntimeError("hosted smoke failed; inspect its private logs")
    print(proc.stderr.decode())
    print(json.dumps({"stock_sha256": sha(stock), "smoke_sha256": sha(out / "rockbox.smoke"),
                      "frame_sha256": sha(out / "frame.bmp"), "exit_status": proc.returncode}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--source", required=True, type=Path)
    prep.add_argument("--sdl-archive", required=True, type=Path)
    prep.add_argument("--inputs", type=Path, help="optional existing verified .deb cache")
    prep.add_argument("--work", required=True, type=Path)
    compile_parser = sub.add_parser("build")
    compile_parser.add_argument("mode", choices=["native", "arm64", "native-asan", "arm64-asan", "hosted"])
    compile_parser.add_argument("--work", required=True, type=Path)
    compile_parser.add_argument("--native-sdl", type=Path)
    compile_parser.add_argument("--sdl-source", type=Path)
    smoke_parser = sub.add_parser("smoke")
    smoke_parser.add_argument("--work", required=True, type=Path)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("run this build tool inside Linux/WSL")
    work = args.work.resolve()
    for protected in (PROJECT / ".local-references", PROJECT / "firmware-images"):
        if work == protected or protected in work.parents:
            parser.error("work must be outside protected evidence directories")
    if args.command == "prepare":
        source = args.source.resolve()
        if work == source or source in work.parents:
            parser.error("work must be outside the source input")
        prepare(work, source, args.sdl_archive.resolve(), args.inputs.resolve() if args.inputs else None)
    else:
        if not (work / "package-manifest.json").is_file():
            parser.error("prepare the isolated environment first")
        if args.command == "smoke":
            smoke(work)
        else:
            build(work, args.mode, args.native_sdl.resolve() if args.native_sdl else None,
                  args.sdl_source.resolve() if args.sdl_source else None)


if __name__ == "__main__":
    main()
