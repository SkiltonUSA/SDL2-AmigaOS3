# Changelog

## 0.2.0 — 2026-10-08 (preview)

- Add the `SDL_AMIGA_PUBLIC_SCREEN` hint with an explicit screen lock across
  window creation. Empty/unset selects the default; unavailable named RTG
  screens fail without silently changing the display.
- Add a self-contained SDL ZZFractal source example and standalone executable
  packaging: zoom, pan, iteration limits, CPU/ARM selection, cancellation,
  native Workbench iconify/restore and temporary RTG test screens.
- Separate measured compute, transfer, colour mapping and SDL drawing costs.
  ARM timing reads and calibrates the existing global timer without changing
  it. The shared-memory allocation/cache contract remains unchanged.
- Keep SDL itself on the 68k; the application's bounded tile client and worker
  demonstrate explicit ARM offloading.

## 0.1.0 — 2026-10-08 (preview)

- Import SDL2 headers 2.33.0 and library source from bdgscotland's AmigaOS3
  port at `1eefa8f35c5ad4b63fa835e251e801a9315dff5c`.
- Remove the invalid Picasso96API-to-CyberGraphX library-base fallback.
- Use clipped, client-relative WritePixelArray updates through the window's
  layered RastPort; remove direct RTG bitmap writes and implicit RTG scaling.
- Package the 68030+ static libraries, headers, source patch, small window
  example, pinned build wrapper, checksums and A4000TX acceptance evidence.
- Disable upstream file-debug logging in the release build. Library remains
  `-O0`; ARM offloading is application-owned and not part of this SDL build.
- Rebuild archives from scratch to prevent duplicate C2P assembly members;
  both relinked diagnostics are byte-identical to the hardware-tested programs.
