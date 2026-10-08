# Verification scope

The historical results below describe SDK 0.1.0. SDK 0.2.0 adds the
[interactive SDL ZZFractal acceptance](SDL-ZZFractal.md).

## Physical A4000TX acceptance — 2026-10-08

Hardware: TF4060/68060, ZZ9000; AmigaOS 3.2.3;
`cybergraphics.library` 42.7 and `Picasso96API.library` 2.455.
The Workbench screen was 1920x800, **8-bit**, while the SDL surface was
320x240 ARGB8888 with pitch 1280. Palette and RTG conversion are included.

The earlier hardware diagnostic used the exact library hash recorded in
[PROVENANCE.md](PROVENANCE.md) and exercised:

- Colour quadrants, mouse click, A key and window close gadget.
- An external ZZ9000 Core1 Mandelbrot worker, using XX19c/XACP 1.7,
  producing 150 tiles with reference hash `fb32f6c6` in 7279 ms end-to-end.
- Q/normal exit, Escape during incomplete ARM rendering, repeat launch and
  automatic exit. ARM teardown returned the worker before freeing its memory.

The ARM computation ran in the separate application worker, **not inside
SDL**. Rendering, conversion, input and OS calls ran on the 68k.

| Final run | Updates | Elapsed | Mean per update |
| --- | ---: | ---: | ---: |
| Baseline full 320x240 surface | 30 | 1,517,496 us | 50.583 ms |
| Baseline 32x16 rectangle | 30 | 20,754 us | 0.692 ms |
| ARM image, full 320x240 surface | 30 | 1,531,321 us | 51.044 ms |
| ARM image, 32x16 rectangle | 30 | 20,749 us | 0.692 ms |

These loops redraw an already populated pixel buffer and include event
polling. They are not game FPS or isolated ARM throughput. Logs, acceptance
metadata and final screenshots are in [evidence/2026-10-08](../evidence/2026-10-08/).

The acceptance JSON also records 30 passing fractal/debugger project tests and
an MCP smoke check covering 138 tools. Those are integration regressions of
the debugger project, **not 30 SDL compatibility tests**.

## Distribution checks

The standalone SDK is rebuilt from this repository with the pinned compiler,
and its included example is linked using the staged SDK headers and static
library. See `evidence/distribution-verification.json` for results and hashes.
The SDK example itself is a compile/link check, not an additional physical
acceptance run. The clean archive has a different hash from the earlier archive because
repeated upstream builds appended three duplicate C2P assembly members.
All 149 rebuilt object files are identical. Relinking **both original hardware
diagnostics** against the clean SDK produces byte-for-byte identical
executables to the ones physically tested. See
[archive comparison](../evidence/archive-comparison.json) and
[probe relink hashes](../evidence/probe-relink-verification.json).
This establishes identity of the tested programs, not broader API coverage.
The wrapper removes old objects and archives before each build to prevent
stale/duplicate members from accumulating.

## Still unverified

Audio/AHI/Paula, fullscreen, AGA, arbitrary scaling/resizing, extensive window
occlusion/movement, SDL's texture renderer, 32-bit screen performance, other
RTG cards and the upstream SDL suite remain untested. No OpenRCT2 execution
or general ARM acceleration is claimed. The probes made no persistent AmigaOS
configuration or firmware changes and were stopped after acceptance.

## 0.2.0 interactive application acceptance

See [SDL ZZFractal](SDL-ZZFractal.md#acceptance-record) and the
[record](../evidence/2026-10-08/sdl-fractal/acceptance.json) for the new
14-render suite, native 16-/32-bit colour checks and timing limitations.
