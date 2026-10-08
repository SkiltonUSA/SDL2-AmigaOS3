/* SDL2 AmigaOS3 SDK example. Copyright (C) 2026 SkiltonUSA.
 * Provided under the zlib licence; see LICENSE. */
#include <stdio.h>
#include "SDL.h"

int main(int argc, char **argv)
{
    SDL_Window *window = NULL;
    SDL_Surface *surface;
    SDL_Event event;
    Uint32 started;
    int x, y, quit = 0, result = 20;
    (void)argc; (void)argv;
    if (SDL_Init(SDL_INIT_VIDEO) < 0) goto done;
    window = SDL_CreateWindow("SDL2 AmigaOS3 preview", 100, 100, 320, 240, 0);
    if (!window) goto done;
    surface = SDL_GetWindowSurface(window);
    if (!surface) goto done;
    for (y = 0; y < 2; ++y) {
        for (x = 0; x < 2; ++x) {
            SDL_Rect rect = {x * 160, y * 120, 160, 120};
            if (SDL_FillRect(surface, &rect, SDL_MapRGB(surface->format,
                x ? 0 : 255, y ? 0 : 255, x && y ? 255 : 0)) < 0) goto done;
        }
    }
    if (SDL_UpdateWindowSurface(window) < 0) goto done;
    started = SDL_GetTicks();
    while (!quit && SDL_GetTicks() - started < 15000) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT || (event.type == SDL_KEYDOWN &&
                (event.key.keysym.sym == SDLK_ESCAPE || event.key.keysym.sym == SDLK_q)))
                quit = 1;
        }
        SDL_Delay(20);
    }
    result = 0;
done:
    if (result) fprintf(stderr, "SDL: %s\n", SDL_GetError());
    if (window) SDL_DestroyWindow(window);
    SDL_Quit();
    return result;
}
