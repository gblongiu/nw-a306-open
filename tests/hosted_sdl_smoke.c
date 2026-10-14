/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Test-only SDL link wrappers: capture software rendering, inject keys, quit.
 * No hardware backend is used; build SDL with dummy video/audio only.
 */
#include <SDL.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static atomic_uint frames;
static atomic_uint image_crc;
static atomic_bool image_saved;
static atomic_bool quitting;

void __real_SDL_RenderPresent(SDL_Renderer *renderer);

void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{
    int width, height;
    if (SDL_GetRendererOutputSize(renderer, &width, &height) == 0 &&
        width > 0 && height > 0 && width <= 1280 && height <= 1920) {
        size_t size = (size_t)width * height * 4;
        unsigned char *pixels = malloc(size);
        if (pixels && SDL_RenderReadPixels(renderer, NULL, SDL_PIXELFORMAT_ARGB8888,
                                          pixels, width * 4) == 0) {
            uint32_t crc = 2166136261u;
            for (size_t i = 0; i < size; ++i)
                crc = (crc ^ pixels[i]) * 16777619u;
            const char *path = getenv("M3_FRAME_BMP");
            SDL_Surface *surface = SDL_CreateRGBSurfaceWithFormatFrom(
                pixels, width, height, 32, width * 4, SDL_PIXELFORMAT_ARGB8888);
            if (surface && path && !atomic_load(&quitting) && SDL_SaveBMP(surface, path) == 0) {
                atomic_store(&image_crc, crc);
                atomic_store(&image_saved, 1);
            }
            if (surface)
                SDL_FreeSurface(surface);
        }
        free(pixels);
    }
    atomic_fetch_add(&frames, 1);
    __real_SDL_RenderPresent(renderer);
}

int __wrap_SDL_WaitEvent(SDL_Event *event)
{
    static unsigned calls;
    ++calls;
    if (calls > 200) {
        fputs("M3 smoke: shutdown timed out\n", stderr);
        _Exit(3);
    }
    SDL_Delay(50);
    SDL_zero(*event);
    if (calls == 20 || calls == 21 || calls == 30 || calls == 31) {
        event->type = (calls & 1) ? SDL_KEYUP : SDL_KEYDOWN;
        event->key.keysym.sym = calls < 30 ? SDLK_DOWN : SDLK_RIGHT;
        return 1;
    }
    if (calls == 60) {
        if (!atomic_load(&image_saved) || atomic_load(&frames) < 2) {
            fputs("M3 smoke: rendering not established\n", stderr);
            _Exit(4);
        }
        fprintf(stderr, "M3 smoke: frames=%u image_fnv1a=%08x keys=4 quit=SDL_QUIT\n",
                atomic_load(&frames), atomic_load(&image_crc));
        atomic_store(&quitting, 1);
        event->type = SDL_QUIT;
        return 1;
    }
    if (!SDL_WaitEventTimeout(event, 10))
        SDL_zero(*event);
    return 1;
}
