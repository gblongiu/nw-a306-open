/* SPDX-License-Identifier: GPL-2.0-or-later
 * Test-only link wrappers for the ordinary hosted Rockbox application.
 * Playlist/control calls run on its main thread; PCM is captured only AFTER
 * the real SDL callback fills the output buffer. No codec is called directly.
 */
#include "config.h"
#include <SDL.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include "audio.h"
#include "metadata.h"
#include "playlist.h"
#include "settings.h"
#include "root_menu.h"
#include "action.h"
#include "codec_thread.h"
#include "kernel.h"

static FILE *pcm_file, *trace_file;
static atomic_ulong output_frames;
static atomic_uint rendered;
static long playback_start_tick, last_observed;
static atomic_bool started, quit_requested;
static bool seen_play;
static unsigned step;
static unsigned cycle = 1;
static void (*real_callback)(void *, Uint8 *, int);
static void *real_userdata;
static SDL_AudioSpec output_spec;

static void trace(const char *event, long value)
{
    if (trace_file) {
        fprintf(trace_file, "%s\ttick=%ld\tframes=%lu\tvalue=%ld\n", event,
                (long)current_tick, atomic_load(&output_frames), value);
        fflush(trace_file);
    }
}

static void finish(void)
{
    trace("process_exit", rendered);
    if (pcm_file)
        fclose(pcm_file);
    if (trace_file)
        fclose(trace_file);
}

__attribute__((constructor)) static void setup(void)
{
    const char *out = getenv("M4_PCM");
    const char *log = getenv("M4_TRACE");
    if (!out || !log)
        return;
    pcm_file = fopen(out, "wbx");
    trace_file = fopen(log, "wx");
    if (!pcm_file || !trace_file)
        _Exit(91);
    atexit(finish);
}

static void capture_callback(void *userdata, Uint8 *stream, int length)
{
    (void)userdata;
    real_callback(real_userdata, stream, length);
    if (length < 0 || length > 1024 * 1024 || output_spec.channels != 2 ||
        output_spec.format != AUDIO_S16LSB ||
        atomic_load(&output_frames) > 48000UL * 120)
        _Exit(92);
    if (fwrite(stream, 1, length, pcm_file) != (size_t)length)
        _Exit(93);
    atomic_fetch_add(&output_frames, length / 4);
}

SDL_AudioDeviceID __real_SDL_OpenAudioDevice(const char *, int,
                    const SDL_AudioSpec *, SDL_AudioSpec *, int);
SDL_AudioDeviceID __wrap_SDL_OpenAudioDevice(const char *device, int recording,
                    const SDL_AudioSpec *wanted, SDL_AudioSpec *obtained, int flags)
{
    if (!pcm_file || recording)
        return __real_SDL_OpenAudioDevice(device, recording, wanted, obtained, flags);
    SDL_AudioSpec spec = *wanted;
    real_callback = spec.callback;
    real_userdata = spec.userdata;
    spec.callback = capture_callback;
    spec.userdata = NULL;
    SDL_AudioDeviceID id = __real_SDL_OpenAudioDevice(device, recording, &spec, obtained, flags);
    if (id) {
        output_spec = *obtained;
        fprintf(trace_file, "output\tfreq=%d\tchannels=%u\tformat=%u\tsamples=%u\tframes=%lu\n",
                obtained->freq, obtained->channels, obtained->format, obtained->samples,
                atomic_load(&output_frames));
        fflush(trace_file);
    }
    return id;
}

struct codec_api;
bool __real_get_metadata_ex(struct mp3entry *, int, const char *, int);
bool __wrap_get_metadata_ex(struct mp3entry *id3, int fd, const char *path, int flags)
{
    bool ok = __real_get_metadata_ex(id3, fd, path, flags);
    if (trace_file) {
        fprintf(trace_file, "metadata\tpath=%s\tok=%d\n", path, ok);
        fflush(trace_file);
    }
    return ok;
}

int __real_codec_load_file(const char *, struct codec_api *);
int __wrap_codec_load_file(const char *name, struct codec_api *api)
{
    int status = __real_codec_load_file(name, api);
    if (trace_file) {
        fprintf(trace_file, "codec_load\tname=%s\tstatus=%d\n", name, status);
        fflush(trace_file);
    }
    return status;
}

void __real_audio_codec_complete(int);
void __wrap_audio_codec_complete(int status)
{
    trace("codec_complete", status);
    __real_audio_codec_complete(status);
}

void __real_SDL_RenderPresent(SDL_Renderer *);
void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{
    ++rendered;
    const char *path = getenv("M4_SCREEN");
    if (path && started && !quit_requested && (rendered % 5 == 0)) {
        int w, h;
        if (!SDL_GetRendererOutputSize(renderer, &w, &h) &&
            w > 0 && h > 0 && w <= 1280 && h <= 1920) {
            SDL_Surface *surface = SDL_CreateRGBSurfaceWithFormat(0, w, h, 32, SDL_PIXELFORMAT_ARGB8888);
            if (surface) {
                if (!SDL_RenderReadPixels(renderer, NULL, surface->format->format,
                                          surface->pixels, surface->pitch))
                    SDL_SaveBMP(surface, path);
                SDL_FreeSurface(surface);
            }
        }
    }
    __real_SDL_RenderPresent(renderer);
}

void __real_root_menu(void);
void __wrap_root_menu(void)
{
    const char *name = getenv("M4_PLAYLIST");
    if (!name) {
        __real_root_menu();
        return;
    }
    playback_start_tick = current_tick;
    started = true;
    const char *library = getenv("M4_LIBRARY");
    if (!library || playlist_create(library, name) < 0 || playlist_amount() < 1)
        _Exit(94);
    trace("playlist_loaded", playlist_amount());
    const char *elapsed = getenv("M4_ELAPSED");
    const char *offset = getenv("M4_OFFSET");
    playlist_start(0, elapsed ? strtoul(elapsed, NULL, 10) : 0,
                      offset ? strtoul(offset, NULL, 10) : 0);
    /* Completion may precede the first UI poll for a one-frame file. This
     * marks an attempt only; the validator separately requires codec/PCM evidence. */
    seen_play = true;
    global_settings.start_in_screen = GO_TO_WPS + 2;
    sleep(HZ / 5);
    __real_root_menu();
}

static void observe(void)
{
    int status = audio_status();
    struct mp3entry *id3 = audio_current_track();
    fprintf(trace_file, "state\ttick=%ld\tframes=%lu\tstatus=%d\telapsed=%lu\toffset=%lu\tlength=%lu\trate=%lu\tcodec=%d\tpath=%s\ttitle=%s\n",
            (long)current_tick, atomic_load(&output_frames), status,
            id3 ? id3->elapsed : 0, id3 ? id3->offset : 0, id3 ? id3->length : 0,
            id3 ? id3->frequency : 0, codec_loaded(),
            id3 ? id3->path : "", id3 && id3->title ? id3->title : "");
    fflush(trace_file);
}

int __real_get_action(int, int);
int __wrap_get_action(int context, int timeout)
{
    if (!started || !trace_file)
        return __real_get_action(context, timeout);
    int action = __real_get_action(context, timeout < 0 ? HZ / 20 : MIN(timeout, HZ / 20));
    long age = current_tick - playback_start_tick;
    int status = audio_status();
    if (status & AUDIO_STATUS_PLAY)
        seen_play = true;
    if (current_tick - last_observed >= HZ / 5) {
        observe();
        last_observed = current_tick;
    }
    bool controls = getenv("M4_CONTROLS") != NULL;
    if (controls && (context & 0xff) == CONTEXT_WPS) {
        if (step == 0 && age >= HZ / 2) {
            ++step; trace("pause_command", status); return ACTION_WPS_PLAY;
        }
        if (step == 1 && age >= HZ) {
            ++step; trace("resume_command", status); return ACTION_WPS_PLAY;
        }
        if (step == 2 && age >= HZ * 3 / 2) {
            ++step; trace("seek_command", 2500);
            audio_pre_ff_rewind(); audio_ff_rewind(2500);
        }
        if (step == 3 && age >= HZ * 2) {
            ++step; trace("next_command", status); return ACTION_WPS_SKIPNEXT;
        }
        if (step == 4 && age >= HZ * 5 / 2) {
            ++step; trace("previous_command", status); return ACTION_WPS_SKIPPREV;
        }
        if (step == 5 && age >= HZ * 7 / 2) {
            ++step; trace("stop_command", status); return ACTION_WPS_STOP;
        }
    }
    if (seen_play && !(status & AUDIO_STATUS_PLAY) && age > HZ) {
        const char *cycles = getenv("M4_CYCLES");
        unsigned target = cycles ? strtoul(cycles, NULL, 10) : 1;
        if (target < 1 || target > 5)
            _Exit(95);
        trace("buffer_available_stopped", audio_buffer_available());
        if (cycle < target) {
            trace("cycle_restart", ++cycle);
            seen_play = false;
            if (playlist_create(getenv("M4_LIBRARY"), getenv("M4_PLAYLIST")) < 0)
                _Exit(96);
            playlist_start(0, 0, 0);
            sleep(HZ / 5);
            return ACTION_NONE;
        }
    }
    if (!quit_requested && ((seen_play && !(status & AUDIO_STATUS_PLAY) && age > HZ) || age > HZ * 35)) {
        quit_requested = true;
        trace(age > HZ * 35 ? "watchdog" : "playback_stopped", status);
        SDL_Event event;
        SDL_zero(event);
        event.type = SDL_QUIT;
        SDL_PushEvent(&event);
    }
    return action;
}
