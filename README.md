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
`v0.2.0` provides the SDL2 SDK. `fractal-v0.3.0` updates only the standalone
fractal application, using the same library. The SDK adds named public-screen
selection and the interactive example.
`v0.1.0` remains available as the initial window-fix preview. The inherited SDL header
version is **2.33.0**; upstream's Amiga port version was **0.7.0**. These are
separate version numbers. This is not an official SDL release or a claim of
complete SDL 2.33 compatibility.

The SDK ZIP and tar.gz contain `lib/libSDL2.a`, `lib/libSDL2_test.a`,
`include/SDL2/`, a small window example (source and executable), documentation,
the exact patch, licence, build metadata, and per-file SHA-256 checksums.
GitHub also provides the tagged source archive. `libSDL2_test.a` is SDL's
support library for tests, not evidence that the full SDL suite passed.

### SDL ZZFractal 0.3.0 executable

[Release notes and requirements](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/tag/fractal-v0.3.0).

- [Amiga LHA package](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/download/fractal-v0.3.0/SDLZZFractal-0.3-XX19c.lha) — recommended; includes executable, icons, instructions and licences.
- [ZIP package](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/download/fractal-v0.3.0/SDLZZFractal-0.3-XX19c.zip).
- [Standalone Amiga executable](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/download/fractal-v0.3.0/SDLZZFractal) — SDL2 and the ARM worker are embedded; no Mac or MCP is needed.
- [Instructions](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/download/fractal-v0.3.0/ReadMe.txt) and [SHA-256 checksums](https://github.com/SkiltonUSA/SDL2-AmigaOS3/releases/download/fractal-v0.3.0/SHA256SUMS.txt).

This is the same hardware-verified 0.3 demo published in [Amiga-MCP-Debugger](https://github.com/SkiltonUSA/Amiga-MCP-Debugger/releases/tag/fractal-v0.3.0), still marked as a prerelease for the tested XX19c / XACP 1.7 configuration. For the bare executable, set its executable protection bit and a 131072-byte Shell stack as described in the instructions.

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

**SDL ZZFractal 0.3** is available as a separate executable LHA/ZIP in the release.
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
`dist/SDLZZFractal-0.3-XX19c.zip` needs no Mac, MCP, network or separate ARM file.
This application-owned ARM worker does not make ordinary SDL calls run on ARM.
Its raw compute and end-to-end timings are deliberately reported separately.

## Fractal comparison: with and without SDL2

Historical comparison before the 0.3 kernel/scheduler work. Recorded default 320×240 Mandelbrot renders on the same A4000TX / TF4060 /
ZZ9000. These are whole-render wall times; lower is better.

| Application | SDL2 | ARM render | 68060 render |
| --- | --- | ---: | ---: |
| Original native ZZFractal | Without SDL2 | 7.523 seconds | 15.081 seconds |
| SDL ZZFractal 0.2 | With SDL2 | 7.575 seconds | 17.427 seconds |

Both versions matched the same reference frame (`fb32f6c6`, all 76,800
iteration counts). These were separate individual application runs, **not a
controlled benchmark of SDL2 overhead**. Drawing, instrumentation and scheduling
differ, so the time difference cannot be attributed to SDL2 alone.

SDL2 provided a reusable graphics/input interface and tested 16-/32-bit RTG
support; these pre-0.3 measurements show no rendering speed improvement. SDL calls
remain on the 68060, with explicit computation sent to a separate ARM worker.
In the SDL version, measured computation took about 2.894 seconds on ARM
versus 2.233 seconds on the 68060. ARM caches remain disabled, and scheduling
and compilation differ; shorter ARM wall time is not a raw CPU speed ratio.

Evidence: [native baseline](evidence/2026-10-08/sdl-fractal/native-baseline.json),
[SDL acceptance runs](evidence/2026-10-08/sdl-fractal/acceptance.json), and
[timing definitions and limitations](docs/SDL-ZZFractal.md#measurements).

## Kernel and scheduling performance: 0.2 versus 0.3

The SDL library is **unchanged**: both use the published SDL2 0.2.0 SDK.
These improvements are in the fractal kernel, scheduling and checked tile
handoff. Same A4000TX, default 320×240 Q14 view, 128 iterations; medians of
three runs per mode in each developer build. Lower is better.

| Measurement | Fractal 0.2 | Fractal 0.3 | Improvement |
| --- | ---: | ---: | ---: |
| ARM whole render | 7.609 s | 3.848 s | 1.98×; 49.4% less time |
| ARM compute estimate | 2.899 s | 1.472 s | 1.97×; 49.2% less time |
| 68060 whole render | 17.292 s | 4.328 s | 4.00×; 75.0% less time |
| 68060 compute | 2.235 s | 1.692 s | 1.32×; 24.3% less time |

All measured frames matched the independent oracle. The CPU path benefits from
the common exact-integer kernel and much shorter scheduling waits. ARM work
slices preserve row checkpoints; its MMU and caches remain off. These are
application measurements with bridge instrumentation, not a general CPU or SDL
benchmark. A zoomed view took 5.665 s on ARM and 9.695 s on the 68060 in 0.3
(single runs). Transfer, drawing and computation overlap; do not add them.

Evidence: [baseline repeats](evidence/2026-10-08/sdl-performance/baseline.json),
[0.3 repeats](evidence/2026-10-08/sdl-performance/final.json), and
[implementation and integrity investigation](docs/SDL-ZZFractal.md#03-performance-and-shared-memory-validation).

Host validation of the shipped compute sources: `python3 -m unittest discover -s tests -v`
(Clang required; this does not replace physical Amiga testing).

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
