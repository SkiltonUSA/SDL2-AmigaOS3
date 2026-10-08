# Local changes relative to the pinned upstream

Base: `bdgscotland/libSDL2-amigaos3` at
`1eefa8f35c5ad4b63fa835e251e801a9315dff5c`.
The exact delta is [window-safety.patch](../patches/window-safety.patch).
The first repository commit imports the unmodified library source; the next
applies this patch and adds distribution documentation/build tooling.

## Correct library base

`src/video/amigaos3/SDL_os3video.c` previously opened
`Picasso96API.library` if opening `cybergraphics.library` failed, assigning
both to `CyberGfxBase`. A library base selects a specific function-vector
layout. These two APIs cannot be used interchangeably.

The patch removes that fallback. The RTG path uses `cybergraphics.library`
V40+ only; the existing no-CyberGraphX/AGA selection remains. Systems with
only Picasso96API and no compatible CyberGraphX interface will not acquire
RTG support through that invalid fallback. The tested machine has both
libraries installed.

## Layer-aware window drawing

`src/video/amigaos3/SDL_os3framebuffer.c` previously wrote pixels relative to
a locked bitmap's base without accounting for the window's position or
occlusion. Its alternate scaling path compared the window's outer dimensions
with the client surface and addressed the destination bitmap directly.

The replacement intersects each requested rectangle with the SDL surface
bounds and calls `WritePixelArray` using the window's layered RastPort. The
layer system can clip drawing for the window. Source and destination use the
clipped client-relative coordinates; `WA_GimmeZeroZero` already supplies that
origin, so adding border offsets would displace the image. The final patch
corrects the extra border offset caught in an earlier local test.

There is no implicit RTG scaling in this path: one source pixel maps to one
displayed pixel. The former direct VRAM fast path and its profiling branch
are removed from the update function. This favors the verified windowed
behavior and may cost performance on other modes. Arbitrary resizing,
occlusion/movement stress tests and other RTG cards are still pending.
The existing unused copy helper and scaling allocation code remain untouched
to keep the patch identical to the hardware-tested source.

## Build configuration

The distribution wrapper preserves upstream's `-O0 -m68030 -noixemul` library
configuration but removes `-DSDL_OS3_DEBUG`. This avoids file logging to the
upstream developer's `WORK:` paths and excludes that I/O from measurements.
No SDL API header version, ARM behavior, firmware or operating-system setup
is changed. The example is separately built at `-O2`.

## Reapply or inspect

The source in this repository is already patched; do not apply it again.
In a separate clean upstream checkout:

```sh
git checkout 1eefa8f35c5ad4b63fa835e251e801a9315dff5c
git apply --check /path/to/window-safety.patch
git apply /path/to/window-safety.patch
```
