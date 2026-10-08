# SDL2 AmigaOS3 — window fixes preview

An **altered, experimental source distribution** of
[bdgscotland/libSDL2-amigaos3](https://github.com/bdgscotland/libSDL2-amigaos3),
pinned to `1eefa8f35c5ad4b63fa835e251e801a9315dff5c`, with local video fixes and named public-screen support,
verified using an A4000TX and ZZ9000.

This project packages the **68k static SDL2 library** and development headers.
SDL calls still execute on the 68k. There is no automatic ARM offloading,
or firmware changes in the SDL library. The SDK includes a separate example
with an application-owned ARM worker; ordinary SDL calls remain on the 68k.

## Versions and downloads

[Download releases](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases).
`v0.2.0` adds named public-screen selection and the interactive SDL ZZFractal example.
`v0.1.0` remains available as the initial window-fix preview. The inherited SDL header
version is **2.33.0**; upstream's Amiga port version was **0.7.0**. These are
separate version numbers. This is not an official SDL release or a claim of
complete SDL 2.33 compatibility.

The SDK ZIP and tar.gz contain `lib/libSDL2.a`, `lib/libSDL2_test.a`,
`include/SDL2/`, a small window example (source and executable), documentation,
the exact patch, licence, build metadata, and per-file SHA-256 checksums.
GitHub also provides the tagged source archive. `libSDL2_test.a` is SDL's
support library for tests, not evidence that the full SDL suite passed.

## What changed

- Removed the fallback that treated `Picasso96API.library` as a CyberGraphX
  library base. Those library vector tables are not interchangeable.
- Replaced direct RTG bitmap writes and implicit scaling with clipped
  `WritePixelArray` updates through the window's layered RastPort. This uses
  client-relative coordinates for `WA_GimmeZeroZero` windows and preserves
  individual dirty rectangles, at one source pixel per displayed pixel.
- The release build omits `SDL_OS3_DEBUG`, avoiding debug file I/O to the
  upstream developer's `WORK:` paths. The two-file source patch is unchanged
  from the tested build.

- `SDL_AMIGA_PUBLIC_SCREEN` selects an existing named RTG public screen.
  Unset/empty selects the default; an unavailable named screen fails explicitly.
  Window creation holds a public-screen lock and never changes the default
  public screen. This is an Amiga-specific hint, not a portable SDL API.

Read [the patch explanation](docs/CHANGES.md),
[hardware evidence and limits](docs/VALIDATION.md), and
[source provenance](docs/PROVENANCE.md).

## Interactive ARM example

**SDL ZZFractal 0.2** is available as a separate executable LHA/ZIP in the release.
It supports CPU/ARM rendering, click-to-zoom, pan, iteration limits, cancellation
and Workbench iconify/restore. Temporary RTG test screens leave Workbench
preferences untouched. It requires the tested ZZ9000 XX19c/XACP 1.7 setup;
close other ARM apps first. See [the app instructions](examples/zzfractal/ReadMe.txt)
and [architecture, timings and acceptance](docs/SDL-ZZFractal.md).

The self-contained source is under `examples/zzfractal/`. After building SDL:

```sh
python3 scripts/build_fractal.py --container-command '["podman"]'
python3 scripts/package_fractal.py
```

Clang with an ARM target and LLVM `ld.lld` are also required. The resulting
`dist/SDLZZFractal-0.2-XX19c.zip` needs no Mac, MCP, network or separate ARM file.
This application-owned ARM worker does not make ordinary SDL calls run on ARM.
Its raw compute and end-to-end timings are deliberately reported separately.

## Use the SDK

Target: AmigaOS 3.x, 68030 or newer, using the GCC/libnix `-noixemul` toolchain.
The corrected RTG path requires a compatible `cybergraphics.library` V40+.
Physical acceptance was on AmigaOS 3.2.3 with a TF4060/68060 and ZZ9000, with
`cybergraphics.library` 42.7 and `Picasso96API.library` 2.455.
AGA fallback remains in the inherited source but is untested in this release.

Extract the SDK on your development machine. For a cross compiler on PATH:

```sh
SDK=/path/to/SDL2-AmigaOS3-0.2.0
m68k-amigaos-gcc -std=c99 -O2 -m68030 -noixemul -D__AMIGAOS3__ \
  -I"$SDK/include/SDL2" "$SDK/examples/window.c" \
  "$SDK/lib/libSDL2.a" -lm -lamiga -o window-demo
```

Copy `window-demo` to the Amiga. From its Shell directory:

```text
Protect window-demo +e
Stack 131072
window-demo
```

The example displays four colour quadrants; Escape, Q or the close gadget
exits. It exits automatically after 15 seconds. The SDK example is a packaging
and link check; the earlier hardware acceptance used separate diagnostic
programs documented in `docs/VALIDATION.md`.

`libSDL2.a` is linked into your application at build time. **Do not copy it to
`LIBS:`**: it is not an Amiga shared `.library` and needs no startup service.
No ixemul.library is required by this build. Applications must still meet
AmigaOS and graphics backend requirements.

## Build and package

Run these commands from a clone of this source repository.
Python 3 and Docker or Podman are required. The wrapper pins the compiler image
by digest, uses `-O0 -m68030 -noixemul` for the library, and creates ZIP/tar.gz
SDKs plus `SHA256SUMS` in `dist/`:

```sh
python3 scripts/build_release.py
# Podman instead:
python3 scripts/build_release.py --container-command '["podman"]'
# A named remote Podman connection:
python3 scripts/build_release.py --container-command '["podman","--connection","YOUR_CONNECTION"]'
```

Use this wrapper for the documented build. The imported upstream `Makefile`
is retained for provenance; its generic Docker, emulator and example targets
refer to upstream tools/examples not included in this library-only snapshot.
The wrapper uses its `native-build` target. `docs/PROVENANCE.md` records the
image digest, source boundary and patch SHA-256.

## Current limits

Acceptance covers the window-surface API (`SDL_GetWindowSurface`,
`SDL_UpdateWindowSurface`, `SDL_UpdateWindowSurfaceRects`), basic input and
shutdown on one machine. Audio, fullscreen, resizing/scaling, SDL's texture
renderer and broad SDL compatibility remain unverified. The fractal example
adds bounded tests on temporary 16-bit and 32-bit-storage RTG screens; this
does not establish compatibility of every display API. The patch removes the former RTG fast/scaling paths; performance
and behavior can differ from upstream. The library is built at `-O0`, so this
is a correctness baseline, not a tuned general-purpose game SDK.

## Licence and attribution

The upstream zlib licence is preserved in [LICENSE](LICENSE). Original SDL,
Amiga port and third-party source notices remain in their files. Original SDL
is by Sam Lantinga and contributors; this AmigaOS3 base is from bdgscotland.
Local fixes and packaging are maintained here by SkiltonUSA. No upstream
endorsement is implied. New original documentation, example and build script
in this repository are also provided under the zlib licence.
